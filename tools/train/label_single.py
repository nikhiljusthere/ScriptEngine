#!/usr/bin/env python3
"""Single-pass labeling: ONE call per window to the ninfer 35B, with the
labeling procedure (plan/EXTRACTION_PROCEDURE.md) as the system prompt.

THE method (owner 2026-10-07, plan/WINDOW_METHOD.md): by default each window also gets the
review-derived hints (label_hints.hints) and, when a review flag fires on the gated answer,
ONE repair turn (big_flags.check). --baseline turns both off for re-measurement only.

Owner 2026-10-06: skip draft_v2's multi-pass pipeline (samples, family and
sentence passes, 3-vote verifier) -- its output still needed manual fixing
on ~30% of windows. Instead the model reads the window plus the procedure
Claude uses to write the gold, and answers once. The procedure is a fixed
prefix of every request, so ninfer's prefix cache reads it once per lane.

After the answer, only MECHANICAL checks run (no model): the quote must be
verbatim in the window, the verb in the 12, the object shape right; ends
that are unnamed/class words, species/item/technique pages, or a place
outside arrived/departed/escaped are dropped; group ends split; self-rows
and symmetric duplicates removed (verify_save.end_errors' checks, the same
gates every saved pool window passed). The wording heuristics (bare modal,
"defeated" without a defeat lexeme) are OFF: the procedure decides those.

    scriptengine/.venv/bin/python tools/train/label_single.py \
        --in series/marvel/training/labels/big_in.jsonl --in series/mcu/... \
        --out series/universal/training/big/labels.jsonl [--workers 8] [--no-thinking]

Resumable: ids already in --out are skipped. A status line is written to
--out + ".status" every 25 windows (done/total, windows/min, ETA, failures).
"""
import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CODE = Path(__file__).resolve().parents[2]
# SCRIPTENGINE_ROOT: run this file from a worktree against the main checkout's
# data AND its gate modules (so the gate stays identical to the live run)
ROOT = Path(os.environ.get("SCRIPTENGINE_ROOT", CODE))
sys.path.insert(0, str(CODE / "tools" / "train"))
sys.path.insert(0, str(ROOT / "tools" / "train"))
import draft_v2  # noqa: E402
import verify_row_wiki as vrw  # noqa: E402
from verify_save import PLACE_LIKE, SPECIES_LIKE  # noqa: E402

draft_v2.MODAL = re.compile(r"(?!x)x")  # the procedure decides modals
draft_v2.DEFEAT = re.compile(r"")       # ... and what counts as a defeat
THINK = re.compile(r"^.*?</think>\s*", re.S)


def window_of(row):
    user = row["messages"][1]["content"]
    return user, user.split("Passage:\n", 1)[1]


def series_of(row):
    m = re.match(r"Series:\s*(\S+)", row["messages"][1]["content"])
    return m.group(1) if m else row.get("series")


def parse(text):
    body = THINK.sub("", text or "").strip()
    body = re.sub(r"^```[a-z]*\n?|\n?```$", "", body).strip()
    s, e = body.find("{"), body.rfind("}")
    if s < 0 or e <= s:
        return None
    try:
        d = json.loads(body[s:e + 1])
    except ValueError:
        return None
    ev = d.get("events") if isinstance(d, dict) else None
    return [x for x in ev if isinstance(x, dict)] if isinstance(ev, list) else None


def parse_v2(text):
    """v2 answer: {"events": [...], "facts": [...], "tags": [...]}.

    Returns (events, facts, tags, ok). `ok` is False when the JSON itself is unusable, which the
    caller treats exactly like a v1 parse failure: never write a failure row, just retry.
    """
    body = THINK.sub("", text or "").strip()
    body = re.sub(r"^```[a-z]*\n?|\n?```$", "", body).strip()
    s, e = body.find("{"), body.rfind("}")
    if s < 0 or e <= s:
        return None, None, None, False
    try:
        d = json.loads(body[s:e + 1])
    except ValueError:
        return None, None, None, False
    if not isinstance(d, dict):
        return None, None, None, False
    ev = d.get("events")
    ev = [x for x in ev if isinstance(x, dict)] if isinstance(ev, list) else None
    if ev is None:
        return None, None, None, False
    fa = d.get("facts")
    fa = [x for x in fa if isinstance(x, dict)] if isinstance(fa, list) else []
    tg = d.get("tags")
    tg = [x for x in tg if isinstance(x, dict)] if isinstance(tg, list) else []
    return ev, fa, tg, True


def tag_gate_keep(rows, window):
    """Tag rows are NOT fact rows: validate them with SECTION C's own rules."""
    import fact_gate
    kept, dropped = [], []
    for r in rows or []:
        probs = []
        if not isinstance(r, dict):
            dropped.append({**r, "why": "not an object"} if isinstance(r, dict) else {"row": str(r), "why": "not an object"})
            continue
        tg, q = r.get("tag"), r.get("quote") or ""
        if tg not in fact_gate.TAGS:
            probs.append(f"tag '{tg}' not in the allowed set")
        if len(q) < 3:
            probs.append("tag row needs the exact text it excuses")
        elif window and q not in window:
            probs.append("tag quote is not verbatim in the window")
        if probs:
            dropped.append({**r, "why": "; ".join(probs)})
        else:
            kept.append({"tag": tg, "quote": q})
    return kept, dropped


def fact_gate_keep(rows, window, wiki=None):
    """The fact layer's gate. Returns (kept, dropped); dropped carry a `why`.

    Applies the fact layer's own rules from tools/train/fact_gate.py. Where the fact layer
    deliberately differs from the event gate (a place, item, organisation or role IS a legal fact
    object; see v2 §B.1/B.8) it uses fact_gate's rules rather than the event gate's end checks.
    """
    import fact_gate
    kept, dropped = [], []
    for r in rows or []:
        probs = list(fact_gate.validate(r))
        q = r.get("quote") or ""
        if len(q) < 12:
            probs.append(f"quote shorter than 12 chars ({q[:30]!r})")
        elif window and q not in window:
            probs.append("quote is not verbatim in the window")
        if q and len(q) > 400:
            probs.append(f"quote is {len(q)} chars; the store truncates at 400")
        rel = r.get("relation")
        for end, is_obj in ((r.get("subject"), False), (r.get("object"), True)):
            if not end:
                continue
            why = fact_gate._end_ok(end, rel, is_obj, "fact", wiki)
            if why:
                probs.append(why)
        if probs:
            dropped.append({**r, "why": "; ".join(probs)})
        else:
            kept.append({k: r.get(k) for k in
                         ("quote", "subject", "relation", "object", "modality", "certainty",
                          "asserted_by", "canon")})
    return kept, dropped


# ninfer serve profiles differ: the 35B (--preserve-thinking off) accepts
# chat_template_kwargs.enable_thinking, while the 27B is launched with --preserve-thinking and
# REJECTS the option outright with HTTP 400 "chat_template_option_not_supported". Sending it anyway
# turns every request into an instant error, so we detect it once and then omit it.
THINK_KW = {"supported": True}


def ask(url, model, doc, user, thinking, max_tokens, timeout=1800, history=()):
    body = {"model": model, "temperature": 0.6 if thinking else 0.0, "top_p": 0.95,
            "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": doc}, {"role": "user", "content": user}, *history]}
    if THINK_KW["supported"]:
        body["chat_template_kwargs"] = {"enable_thinking": bool(thinking)}
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    try:
        m = json.loads(urllib.request.urlopen(req, timeout=timeout).read())["choices"][0]["message"]
    except urllib.error.HTTPError as e:
        detail = (e.read() or b"").decode("utf-8", "replace")
        if "chat_template_option_not_supported" in detail:
            THINK_KW["supported"] = False
            body.pop("chat_template_kwargs", None)
            req = urllib.request.Request(url, json.dumps(body).encode(),
                                         {"Content-Type": "application/json"})
            m = json.loads(urllib.request.urlopen(req, timeout=timeout).read())["choices"][0]["message"]
        else:
            raise
    return m.get("content") or ""


def gate(rows, window, wiki):
    """The mechanical end/shape checks; returns (kept, dropped)."""
    kept, dropped = draft_v2.check_rows(rows, window, wiki, vrw.BAD_END | SPECIES_LIKE)
    out = []
    for r in kept:
        why = None
        for end in (r["subject"], r["object"]):
            if not end:
                continue
            bare = re.sub(r"(?i)^(the|a|an)\s+", "", end.strip())
            exact = [p for p in wiki.resolve(bare) if p.lower() == bare.lower()]
            lab = wiki.label.get(exact[0]) if exact else None
            if lab in SPECIES_LIKE:
                why = f"end {end!r} is a {lab} page"
            elif (lab and end == r["object"] and r["verb"] not in ("arrived", "departed", "escaped")
                  and PLACE_LIKE.search(lab)):
                why = f"place {end!r} as the object of {r['verb']}"
        if why:
            dropped.append({**r, "why": why})
        else:
            out.append(r)
    return out, dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inputs", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--doc", default=str(ROOT / "plan/EXTRACTION_PROCEDURE.md"))
    ap.add_argument("--url", default="http://127.0.0.1:18081/v1/chat/completions")
    ap.add_argument("--model", default="qwen3.6-35b-a3b-ninfer")
    # the 35B on :18081 serves windowing/labeling (owner 2026-10-07).
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--no-thinking", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=16384)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--shuffle", action="store_true")
    ap.add_argument("--ids", default=None, help="only these ids (a JSONL with an id field)")
    # plan/WINDOW_METHOD.md: hints + repair are the method; --baseline exists only to re-measure
    ap.add_argument("--hints", action="store_true", default=True,
                    help="(default) append the review-derived reminders whose triggers occur in the window")
    ap.add_argument("--repair", action="store_true", default=True,
                    help="(default) one follow-up turn listing the review flags that fire on the answer")
    ap.add_argument("--baseline", action="store_true",
                    help="MEASUREMENT ONLY: turn hints and repair off (the retired plain single pass)")
    # ---- schema v2 (owner 2026-10-07, plan/EXTRACTION_PROCEDURE_V2.md) ----
    ap.add_argument("--schema", choices=("v1", "v2"), default="v1",
                    help="v2 = the event layer plus the fact layer plus tag rows (default: v1)")
    ap.add_argument("--v2-doc", default=None,
                    help="the v2 procedure doc (default plan/EXTRACTION_PROCEDURE_V2.md)")
    ap.add_argument("--coverage-repair", action="store_true", default=True,
                    help="(v2, default) one follow-up turn listing sentences no row covers")
    ap.add_argument("--no-coverage-repair", dest="coverage_repair", action="store_false")
    ap.add_argument("--add-only", default=None, metavar="GOLD.jsonl",
                    help="v2 add-only: events come from this file's final rows (id -> events), and the "
                         "model is asked ONLY for facts and tags. Used to add facts to Claude's "
                         "reviewed event rows without re-deriving them.")
    ap.add_argument("--provenance", default=None, help="a label written into each output row")
    a = ap.parse_args()
    if a.schema == "v2":
        a.doc = a.v2_doc or str(CODE / "plan/EXTRACTION_PROCEDURE_V2.md")
        # 2026-10-07 (owner): the 35B serves windowing/labeling by default on :18081;
        # explicit --url/--model always win (there is no forced remap anymore).
    doc = Path(a.doc).read_text(encoding="utf-8")
    rows = [json.loads(l) for p in a.inputs for l in open(p)]
    if a.ids:
        keep = {json.loads(l)["id"] for l in open(a.ids)}
        rows = [r for r in rows if r["id"] in keep]
    gold_events = {}
    if a.add_only:
        # the reviewed event rows are FIXED; the model only adds facts/tags
        for line in open(a.add_only):
            g = json.loads(line)
            gold_events[g["id"]] = g.get("events") or []
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(l)["id"] for l in open(out)} if out.exists() else set()
    rows = [r for r in rows if r["id"] not in done]
    if a.shuffle:
        # page-interleaved order: any prefix of the run is a fair sample of
        # all selected pages, so the run can stop once the target mix exists
        import random
        random.Random(20261007).shuffle(rows)
    if a.limit:
        rows = rows[:a.limit]
    wikis = {s: vrw.Wiki(str(ROOT / "series" / s / "facts.db")) for s in {series_of(r) for r in rows}}
    total, lock = len(rows) + len(done), threading.Lock()
    stats = {"done": len(done), "fail": 0, "rows": 0, "dropped": 0, "t0": time.time(), "new": 0}

    if a.baseline:
        a.hints = a.repair = False
    if a.hints or a.repair:
        import label_hints
    if a.repair:
        import big_flags

    def job(r):
        user, window = window_of(r)
        if a.hints:
            user = user + label_hints.hints(window, r.get("section") or "")
        if a.schema == "v2":
            return job_v2(r, user, window)
        events, raw, tries, down = None, "", 0, 0
        while events is None and tries < 3:
            try:
                raw = ask(a.url, a.model, doc, user, not a.no_thinking, a.max_tokens)
                tries += 1
                events = parse(raw)
            except urllib.error.URLError as e:
                # server down / restarting: wait, never record a failure row
                # (2026-10-07: a dead server turned 13,896 windows into
                # instant "connection refused" rows that a resume would skip)
                down += 1
                if down > 20:
                    return None
                time.sleep(30)
            except Exception as e:  # noqa: BLE001
                tries += 1
                raw = f"ERROR {e!r}"
        ok = events is not None
        kept, dropped = gate(events or [], window, wikis[series_of(r)])
        note, first = None, None
        if ok and a.repair:
            # one follow-up turn only when a review flag fires on the gated rows
            note = label_hints.repair_note(kept, window, big_flags.check)
            if note:
                answer = json.dumps({"events": events}, ensure_ascii=False)
                try:
                    raw2 = ask(a.url, a.model, doc, user, not a.no_thinking, a.max_tokens,
                               history=({"role": "assistant", "content": answer}, {"role": "user", "content": note}))
                    ev2 = parse(raw2)
                except Exception:  # noqa: BLE001 - keep the first answer
                    ev2 = None
                if ev2 is not None:
                    first = [(e["subject"], e["verb"], e["object"]) for e in kept]
                    kept, dropped = gate(ev2, window, wikis[series_of(r)])
                    raw = raw2
        return {"id": r["id"], "series": series_of(r), "page": r.get("page"), "section": r.get("section"),
                "kind": r.get("kind"), "ok": ok, "tries": tries, "events": kept, "dropped": dropped,
                "hinted": bool(a.hints), "repair_note": note, "first_rows": first,
                "answer": THINK.sub("", raw).strip()[-4000:], "think_chars": len(raw) - len(THINK.sub("", raw))}

    def job_v2(r, user, window):
        """The v2 pass: events + facts + tags, then at most TWO repair turns.

        Turn 1 = the model's own answer.
        Turn 2 = the event-layer review flags (label_hints.repair_note over big_flags.check, the same
                repair the v1 method uses) plus the fact-layer flags from fact_gate.check.
        Turn 3 = the coverage worklist: the sentences no row covers (fact_coverage.report). This is
                the turn that closes the 62.9% gap the step-2 baseline measured.

        In --add-only mode the event rows are FIXED by --add-only: they are not asked for, not
        re-derived and not repaired, and they are copied into the output byte-identically.
        """
        import fact_coverage
        import fact_gate
        wiki = wikis[series_of(r)]
        add_only = a.add_only is not None
        fixed_events = gold_events.get(r["id"]) if add_only else None
        if add_only and fixed_events is None:
            return None  # no reviewed rows for this id: not an add-only window
        if add_only:
            # tell the model the events are settled, so it spends its budget on facts
            user = user + (
                "\n\nThe EVENT rows for this window are already decided and are correct; do not "
                "write them. Write ONLY the `facts` and `tags` arrays. Answer with the full shape "
                "anyway, repeating the given events unchanged:\n"
                + json.dumps({"events": fixed_events}, ensure_ascii=False))
        events = facts = tags = None
        raw, tries, down, ok = "", 0, 0, False
        history = ()
        while events is None and tries < 3:
            try:
                raw = ask(a.url, a.model, doc, user, not a.no_thinking, a.max_tokens, history=history)
                tries += 1
                events, facts, tags, ok = parse_v2(raw)
            except urllib.error.URLError:
                down += 1
                if down > 20:
                    return None
                time.sleep(30)
            except Exception as e:  # noqa: BLE001
                tries += 1
                raw = f"ERROR {e!r}"
        if not ok:
            return None  # never write a failure row; a resume retries it
        if add_only:
            events = fixed_events
        else:
            kept_ev, dropped_ev = gate(events, window, wiki)
            if a.repair:
                note = label_hints.repair_note(kept_ev, window, big_flags.check)
                fflags, _ = fact_gate.check(facts, window, wiki, tags=tags)
                fflags = [f for f in fflags if not f.startswith("quote is not verbatim")][:8]
                if note or fflags:
                    bits = []
                    if note:
                        bits.append(note.split("\n\n")[1] if "\n\n" in note else note)
                    if fflags:
                        bits.append("Fact-layer checks that fired on your fact rows (each is a "
                                    "warning, not proof):\n" + "\n".join(f"- {f}" for f in fflags))
                    ask2 = ("Review these points about your answer, then answer with the COMPLETE "
                            "corrected JSON in the same shape:\n\n" + "\n\n".join(bits))
                    answer = json.dumps({"events": events, "facts": facts, "tags": tags},
                                        ensure_ascii=False)
                    try:
                        raw2 = ask(a.url, a.model, doc, user, not a.no_thinking, a.max_tokens,
                                   history=({"role": "assistant", "content": answer},
                                            {"role": "user", "content": ask2}))
                        e2, f2, t2, ok2 = parse_v2(raw2)
                    except Exception:  # noqa: BLE001 - keep the first answer
                        e2, f2, t2, ok2 = None, None, None, False
                    if ok2:
                        if not add_only:
                            events = e2
                        facts, tags = f2, t2
                        raw = raw2
        kept_ev = events if add_only else gate(events or [], window, wiki)[0]
        dropped_ev = [] if add_only else gate(events or [], window, wiki)[1]
        kept_fa, dropped_fa = fact_gate_keep(facts, window, wiki)
        kept_tg, dropped_tg = tag_gate_keep(tags, window)
        # ---- coverage repair turn (v2 SECTION C) ----
        cov_note = None
        if a.coverage_repair and not add_only:
            rep = fact_coverage.report(window, kept_ev, kept_fa, kept_tg)
            if rep["uncovered"]:
                missed = "\n".join(f"- {s}" for s in rep["uncovered"][:10])
                cov_note = (f"These sentences in the passage are covered by NO event row, NO fact row "
                            f"and NO tag row ({len(rep['uncovered'])} in total). Each one states "
                            f"something, so either write the rows it needs, or -- if it is genuinely "
                            f"not a fact -- give it a tag row with one of the allowed tags "
                            f"(dialogue, list_header, production, citation, apposition, attire, "
                            f"capability, deictic, below_floor). Remember: plans, orders, claims, "
                            f"dreams and hypotheticals are facts here (modality + asserted_by), not "
                            f"things to drop.\n{missed}\n\nAnswer with the COMPLETE corrected JSON "
                            f"in the same shape.")
                answer = json.dumps({"events": events, "facts": facts, "tags": tags}, ensure_ascii=False)
                try:
                    raw3 = ask(a.url, a.model, doc, user, not a.no_thinking, a.max_tokens,
                               history=({"role": "assistant", "content": answer},
                                        {"role": "user", "content": cov_note}))
                    e3, f3, t3, ok3 = parse_v2(raw3)
                except Exception:  # noqa: BLE001 - keep the previous answer
                    e3, f3, t3, ok3 = None, None, None, False
                if ok3:
                    events = e3 if not add_only else fixed_events
                    facts, tags = f3, t3
                    raw = raw3
                    kept_ev = gate(events or [], window, wiki)[0] if not add_only else kept_ev
                    dropped_ev = gate(events or [], window, wiki)[1] if not add_only else []
                    kept_fa, dropped_fa = fact_gate_keep(facts, window, wiki)
                    kept_tg, dropped_tg = tag_gate_keep(tags, window)
        cov = fact_coverage.report(window, kept_ev, kept_fa, kept_tg)
        out = {"id": r["id"], "series": series_of(r), "page": r.get("page"), "section": r.get("section"),
               "kind": r.get("kind"), "ok": True, "schema": "v2", "tries": tries,
               "events": kept_ev, "facts": kept_fa, "tags": kept_tg,
               "dropped": dropped_ev, "dropped_facts": dropped_fa, "dropped_tags": dropped_tg,
               "hinted": bool(a.hints), "coverage": {"narrative": cov["narrative"],
                                                     "covered": cov["covered"],
                                                     "uncovered": len(cov["uncovered"]),
                                                     "rate": round(cov["rate"], 4)},
               "uncovered_sentences": cov["uncovered"][:5],
               "other_verb": round(fact_gate.other_share(kept_fa), 4),
               "repair_note": cov_note, "answer": THINK.sub("", raw).strip()[-4000:],
               "think_chars": len(raw) - len(THINK.sub("", raw))}
        if a.provenance:
            out["provenance"] = a.provenance
        return out

    def status():
        el = time.time() - stats["t0"]
        rate = stats["new"] / el * 60 if el else 0
        left = total - stats["done"]
        eta = left / rate if rate else 0
        Path(str(out) + ".status").write_text(
            f"{time.strftime('%F %T')} done {stats['done']}/{total} | {rate:.1f} windows/min | "
            f"ETA {eta/60:.1f} h | parse-fail {stats['fail']} | rows {stats['rows']} | gate-dropped {stats['dropped']}\n")

    with ThreadPoolExecutor(a.workers) as pool, open(out, "a") as f:
        for res in pool.map(job, rows):
            if res is None:  # left for a later resume
                continue
            with lock:
                f.write(json.dumps(res, ensure_ascii=False) + "\n"); f.flush()
                stats["done"] += 1; stats["new"] += 1
                stats["fail"] += 0 if res["ok"] else 1
                stats["rows"] += len(res["events"]); stats["dropped"] += len(res["dropped"])
                if stats["new"] % 25 == 0:
                    status()
    status()
    print(Path(str(out) + ".status").read_text().strip())


if __name__ == "__main__":
    main()

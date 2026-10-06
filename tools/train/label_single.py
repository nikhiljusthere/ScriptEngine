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


def ask(url, model, doc, user, thinking, max_tokens, timeout=1800, history=()):
    body = {"model": model, "temperature": 0.6 if thinking else 0.0, "top_p": 0.95,
            "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": doc}, {"role": "user", "content": user}, *history],
            "chat_template_kwargs": {"enable_thinking": bool(thinking)}}
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    m = json.loads(urllib.request.urlopen(req, timeout=timeout).read())["choices"][0]["message"]
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
    a = ap.parse_args()
    doc = Path(a.doc).read_text(encoding="utf-8")
    rows = [json.loads(l) for p in a.inputs for l in open(p)]
    if a.ids:
        keep = {json.loads(l)["id"] for l in open(a.ids)}
        rows = [r for r in rows if r["id"] in keep]
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

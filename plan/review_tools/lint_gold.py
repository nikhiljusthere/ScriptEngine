#!/usr/bin/env python3
"""Gold-set lint (stage 8a, 2026-11-03): lint_v2's checks over the gold v2 audit, READ-ONLY.

`BV2_SET=gold lint.sh` already runs lint_v2 on the gold set, but it silently fills windows with no gold audit
record from the 35B labels and prints "missing 0", so an unfinished review looks complete. This adapter:
  - says how many windows have no gold audit record (they are linted on their 35B label rows, marked UNREVIEWED);
  - adds the two filtered classes lint_work computes for its reading list (name_short_and_full with person-like
    pairs only -> `name_short_and_full_person`; fought+defeat quoted in one sentence -> `E_A145_same_sentence`);
  - re-gates with progress on stderr (`--regate`), with lint_v2.regate's exact logic;
  - writes nothing but the `--json` file it is given (no audit, label or fix file is touched).

    lint_gold.sh [--regate] [--show CHECK] [--json OUT]
"""
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

os.environ["BV2_SET"] = "gold"  # big_review_v2 reads it at import: gold paths, gold order, gold passages
sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/review_tools")
import lint_v2  # noqa: E402
import lint_work  # noqa: E402

bv = lint_v2.bv
assert bv.GOLD and "gold_v2" in str(bv.AUDIT2), bv.AUDIT2


def gold_records():
    """(ids, records, reviewed): latest gold audit record per id, 35B label rows for ids with none."""
    ids, a2 = bv.order(), bv.audit2()
    labels = {r["id"]: r for r in bv.jl(bv.V2)}
    return ids, {**labels, **a2}, set(a2)


def advisory(rec, text):
    """X_* classes (2026-11-03, gold only, advisory: they wait on open rulings of RESUME_HANDOFF_2026-10-28's last
    update, so no reading list carries them). An end the window never writes (A112/A130: renames go only to a form in
    the window text; "page-title subjects/ends not in the window text are dropped"): X_end_absent = not one word
    (>= 3 letters) of it is in the window; X_end_partial = its words are there but not the whole string (a full name
    built from parts, "Maki" + "Zenin" -> "Maki Zenin"). X_tag_quote_pipe: a tag quote with a pipe (open ruling:
    infobox tags pipe-free)."""
    out, tl = defaultdict(list), text.lower()

    def end(x, row):
        if not x or x.lower() in tl:
            return
        words = [w for w in re.findall(r"[^\W\d_]{3,}", x.lower())]
        out["X_end_absent" if not any(w in tl for w in words) else "X_end_partial"].append((x,) + row)
    for e in rec.get("events", []):
        for x in (e["subject"], e["object"]):
            end(x, ("E", e["verb"]))
    for f in rec.get("facts", []):
        for x in (f.get("subject"), f.get("asserted_by")):
            end(x, ("F", f.get("relation")))
    for t in rec.get("tags", []):
        if "|" in (t.get("quote") or ""):
            out["X_tag_quote_pipe"].append((t.get("tag"), t["quote"][:60]))
    return out


def overlap_lint(ids, recs):
    """{b: {class: rows}} for overlapping gold windows (recon_lib: >= 2 shared sentences > 60 chars). The big set had
    recon.sh; the gold set never had an overlap pass. R_overlap_inconsistent = the shared sentences carry different
    rows (recon_lib.pair_diff); R_overlap_cross_split = the two windows sit in different splits (train vs dev/test:
    shared text across the split line)."""
    sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/review_tools/recon")
    import recon_lib
    _, sents = recon_lib.load()
    splits = {json.loads(l)["id"]: json.loads(l).get("splits") for l in open(bv.GOLD_IN)}
    out = defaultdict(lambda: defaultdict(list))
    for (a, b), n in sorted(recon_lib.overlap_pairs(sents).items()):
        d = recon_lib.pair_diff(a, b, ids, sents, recs)
        if d:
            # (layer, rows only in this window, rows only in the partner) on the shared sentences
            out[a]["R_overlap_inconsistent"].append((f"b{b}", n, [(layer, len(p), len(q)) for layer, p, q in d]))
            out[b]["R_overlap_inconsistent"].append((f"b{a}", n, [(layer, len(q), len(p)) for layer, p, q in d]))
        sa, sb = splits[ids[a - 1]], splits[ids[b - 1]]
        if sa != sb:
            for x, y, s in ((a, b, sb), (b, a, sa)):
                out[x]["R_overlap_cross_split"].append((f"b{y}", n, "+".join(s or [])))
    return out


def window_lint(b, wid, rec, text):
    out = lint_v2.checks(b, wid, rec, text)
    filt = lint_work.window_classes(b, rec, text)
    out["name_short_and_full_person"] = filt.get("name_short_and_full", [])
    out["E_A145_same_sentence"] = filt.get("E_A145_same_sentence", [])
    out.update(advisory(rec, text))
    return {k: v for k, v in out.items() if v}


def regate(ids, recs, pas, total, hits, only=None):
    """lint_v2.regate with progress; `only` = set of b-numbers to re-gate (None = all)."""
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("label_single", Path(bv.__file__).resolve().parent / "label_single.py")
    ls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ls)
    import verify_row_wiki as vrw
    wikis, t0 = {}, time.time()
    for b, wid in enumerate(ids, 1):
        if only is not None and b not in only:
            continue
        if b % 200 == 0:
            print(f"regate b{b}/{len(ids)} {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
        rec = recs.get(wid)
        w = pas[wid]
        series = rec.get("series") or "marvel"
        if series not in wikis:
            t1 = time.time()
            wikis[series] = vrw.Wiki(str(bv.ROOT / "series" / series / "facts.db"))
            print(f"wiki {series} loaded {time.time() - t1:.0f}s", file=sys.stderr, flush=True)
        wiki = wikis[series]
        evs = [{k: e.get(k) for k in ("quote", "subject", "verb", "object")} for e in rec.get("events", [])]
        kept, dropped = ls.gate(evs, w, wiki)
        if dropped or len(kept) != len(evs):
            total["REGATE_events"] += max(len(dropped), 1)
            hits["REGATE_events"].append((b, [(d.get("subject"), d.get("verb"), d.get("object"), d.get("why")) for d in dropped]
                                          or [f"kept {len(kept)}/{len(evs)}"]))
        fk, fd = ls.fact_gate_keep([dict(f) for f in rec.get("facts", [])], w, wiki)
        if fd:
            total["REGATE_facts"] += len(fd)
            hits["REGATE_facts"].append((b, [(d.get("subject"), d.get("relation"), d.get("object"), d.get("why")) for d in fd]))
        key = lambda f: (f.get("subject"), f.get("relation"), f.get("object"), f.get("modality"), f.get("asserted_by"))
        old, new = Counter(map(key, rec.get("facts", []))), Counter(map(key, fk))
        if not fd and old != new:
            total["REGATE_facts_changed"] += 1
            hits["REGATE_facts_changed"].append((b, [("-",) + k for k in old - new] + [("+",) + k for k in new - old]))
        tk, td = ls.tag_gate_keep([dict(t) for t in rec.get("tags", [])], w)
        if td:
            total["REGATE_tags"] += len(td)
            hits["REGATE_tags"].append((b, [(d.get("tag"), d.get("why")) for d in td]))
    print(f"regate done {time.time() - t0:.0f}s", file=sys.stderr, flush=True)


def main():
    a = sys.argv[1:]
    show = a[a.index("--show") + 1] if "--show" in a else None
    ids, recs, reviewed = gold_records()
    pas = bv.br.passages()
    unrev = [b for b, i in enumerate(ids, 1) if i not in reviewed]
    total, hits = Counter(), defaultdict(list)
    for b, wid in enumerate(ids, 1):
        for k, rows in window_lint(b, wid, recs[wid], pas[wid]).items():
            total[k] += len(rows)
            hits[k].append((b, rows))
    for b, cl in sorted(overlap_lint(ids, recs).items()):
        for k, rows in cl.items():
            total[k] += len(rows)
            hits[k].append((b, rows))
    if "--regate" in a:
        regate(ids, recs, pas, total, hits)
    print(f"gold windows {len(ids)} | with gold audit record {len(ids) - len(unrev)} | UNREVIEWED (35B label rows "
          f"linted) {len(unrev)} {['b%d' % b for b in unrev]}")
    for k in sorted(total):
        print(f"{k:32s} rows {total[k]:6d}  windows {len(hits[k]):5d}  e.g. b{[h[0] for h in hits[k][:8]]}")
    if show:
        for b, rows in hits.get(show, []):
            print(f"b{b}", rows)
    if "--json" in a:
        json.dump({"_meta": {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "audit": str(bv.AUDIT2),
                             "unreviewed": unrev, "regate": "--regate" in a},
                   **{k: v for k, v in hits.items()}}, open(a[a.index("--json") + 1], "w"), default=list,
                  ensure_ascii=False)


if __name__ == "__main__":
    main()

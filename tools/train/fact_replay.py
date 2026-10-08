#!/usr/bin/env python3
"""Replay the fact gate over an already-written labels_v2 file (no GPU).

Answers the question the council could not: what does the fact layer actually keep, and how
many written sentences are unroutable (an event rule refuses them AND no fact/tag can carry
them)?  Used to measure the effect of a gate or catalog change on output that already exists.

  scriptengine/.venv/bin/python tools/train/fact_replay.py FILE.jsonl [FILE2.jsonl ...]

Reports per file: facts proposed, kept, dropped (with the top drop reasons), other_verb share,
tag counts, and the coverage sentence funnel.  SCRIPTENGINE_ROOT must point at the checkout
holding series/*/facts.db.
"""
import collections
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("SCRIPTENGINE_ROOT", str(Path(__file__).resolve().parents[2]))
import fact_coverage  # noqa: E402
import fact_gate  # noqa: E402
import verify_row_wiki as vrw  # noqa: E402

# fact_gate inserts the DATA checkout's tools/train on sys.path, which would shadow this
# worktree's label_single; load ours by path so the worktree's gate helpers are the ones used.
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("worktree_label_single", __file__.replace("fact_replay.py", "label_single.py"))
ls = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ls)

ROOT = Path(os.environ["SCRIPTENGINE_ROOT"])


def series_of(row):
    """labels_v2 rows carry `series`; input rows carry it in the user turn."""
    return row.get("series") or ls.series_of(row)


def passages():
    """The window text per id, from the selection inputs (labels_v2 rows carry no text)."""
    out = {}
    for s in ("marvel", "mcu"):
        p = ROOT / "series" / s / "training/labels/big_in.jsonl"
        for line in open(p):
            r = json.loads(line)
            out[r["id"]] = r["messages"][1]["content"].split("Passage:\n", 1)[1]
    return out


def old_gate_comparison(rows, wikis, pas):
    """How many ALREADY-STORED fact rows would the pre-council gate have refused?

    The stored rows were gated at write time, so a plain replay cannot see the drop rate; this
    re-applies the old two rules (article refusal for person ends, inverted sentence-boundary
    flag) to the same rows and reports what the 2026-10-08 gate fix recovered.
    """
    import re as _re
    art = _re.compile(r"^(?:a|an|the|his|her|their|its)\s+", _re.I)
    art_old = bound_old = 0
    examples = []
    for r in rows:
        w = wikis[series_of(r)]
        window = pas.get(r["id"], "")
        for f in r.get("facts") or []:
            if not fact_gate.validate(f) and (not window or (f.get("quote") or "") in window):
                q = f.get("quote") or ""
                sents = fact_gate.sentences(window)
                if q and sents and not any(fact_gate.norm(s) in fact_gate.norm(q) for s in sents) and q in window:
                    bound_old += 1
                o = f.get("object") or ""
                if art.match(o) and fact_gate.NON_PERSON_OBJECT.get(f.get("relation")) not in (
                        "place", "item", "thing", "title", "name"):
                    art_old += 1
                    if len(examples) < 8:
                        examples.append((f.get("subject"), f.get("relation"), o, q[:50]))
    return art_old, bound_old, examples


def main():
    pas = passages()
    for path in sys.argv[1:]:
        rows = [json.loads(l) for l in open(path)]
        wikis = {s: vrw.Wiki(str(ROOT / "series" / s / "facts.db")) for s in {series_of(r) for r in rows}}
        kept = dropped = 0
        reasons = collections.Counter()
        ov = 0
        tags = collections.Counter()
        ev = fa = 0
        uncovered = narrative = 0
        for r in rows:
            w = wikis[series_of(r)]
            window = pas.get(r["id"], "")
            ev += len(r.get("events") or [])
            k, d = ls.fact_gate_keep(r.get("facts") or [], window, w)
            kept += len(k)
            dropped += len(d)
            ov += fact_gate.other_share(k) * len(k)
            fa += len(r.get("facts") or [])
            tk, td = ls.tag_gate_keep(r.get("tags") or [], window)
            tags.update(t["tag"] for t in tk)
            rep = fact_coverage.report(window, r.get("events") or [], k, tk)
            narrative += rep["narrative"]
            uncovered += len(rep["uncovered"])
            for x in d:
                reasons[x.get("why", "?")[:60]] += 1
        print(f"== {path}")
        print(f"windows {len(rows)} | event rows {ev} | facts proposed {fa} kept {kept} dropped {dropped} "
              f"({dropped / max(1, fa):.1%}) | other_verb {ov / max(1, kept):.1%}")
        print(f"tags {dict(tags)}")
        print(f"coverage {narrative - uncovered}/{narrative} narrative sentences covered "
              f"({1 - uncovered / max(1, narrative):.1%})")
        print("top drop reasons:")
        for why, n in reasons.most_common(8):
            print(f"   {n:5d}  {why}")
        art_old, bound_old, ex = old_gate_comparison(rows, wikis, pas)
        print(f"stored fact rows the OLD article rule would have refused (join/member_of on a "
              f"named group with its article): {art_old}")
        for e in ex:
            print("   e.g.", e)
        print(f"stored fact rows on which the inverted sentence-boundary rule would have fired on "
              f"the repair turn: {bound_old}")


if __name__ == "__main__":
    main()
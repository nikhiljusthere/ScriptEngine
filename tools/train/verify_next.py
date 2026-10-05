#!/usr/bin/env python3
"""Show the next window to verify by hand (plan/VERIFY_POOLS_BRIEF.md): its
id, page, section, the passage with numbered sentences, and the frozen
drafter's rows. Bookkeeping only -- the verdicts are the verifier's.

    scriptengine/.venv/bin/python tools/train/verify_next.py --series opm [--pool pool|test] [--id ID]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("--pool", default="pool")
    ap.add_argument("--id", default=None)
    a = ap.parse_args()
    from scriptengine.ingest.windows import sentence_spans
    lab = ROOT / "series" / a.series / "training" / "labels"
    src = lab / ("pool_in.jsonl" if a.pool == "pool" else "test_in.jsonl")
    drafts_path = lab / ("draft_frozen.jsonl" if a.pool == "pool" else "draft_frozen_test.jsonl")
    out = lab / f"{a.pool}_verified.jsonl"
    done = {json.loads(l)["id"] for l in open(out)} if out.exists() else set()
    drafts = {json.loads(l)["id"]: json.loads(l) for l in open(drafts_path)} if drafts_path.exists() else {}
    order = [json.loads(l) for l in open(src)]
    todo = [r for r in order if r["id"] not in done and (a.id is None or r["id"] == a.id)]
    todo = [r for r in todo if r["id"] in drafts] or todo
    if not todo:
        print(f"ALL VERIFIED: {len(done)}/{len(order)} windows of {a.series}/{a.pool}")
        return 0
    r = todo[0]
    if r["id"] not in drafts:
        print(f"WAIT: window {r['id']} has no draft yet (the drafter is still running)")
        return 3
    text = r["messages"][1]["content"].split("Passage:\n", 1)[1]
    print(f"PROGRESS {len(done)}/{len(order)} | NEXT id={r['id']} | series={a.series} | page={r['page']!r} | section={r['section']!r}")
    print("PASSAGE (numbered sentences):")
    for n, (_s, _e, sent) in enumerate(sentence_spans(text), 1):
        print(f"  [{n}] {sent}")
    print("DRAFT ROWS (frozen 35B drafter):")
    rows = drafts[r["id"]].get("events") or []
    for i, e in enumerate(rows):
        print(f"  {i}: {json.dumps({k: e.get(k) for k in ('quote', 'subject', 'verb', 'object')}, ensure_ascii=False)}")
    if not rows:
        print("  (none -- the drafter found no event; re-read every sentence for misses)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

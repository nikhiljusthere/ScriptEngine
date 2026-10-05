#!/usr/bin/env python3
"""Claude's review queue for the pool verification (plan/VERIFY_POOLS_BRIEF.md:
"Claude reviews EVERY saved window"). Prints each saved window after the
review cursor -- the passage (trimmed) and its final rows -- and with --mark
advances the cursor to the end of what was printed. Read-only otherwise.

    scriptengine/.venv/bin/python tools/train/audit_next.py --series csm [--pool pool] [--max 25]
    scriptengine/.venv/bin/python tools/train/audit_next.py --series csm --mark N
    scriptengine/.venv/bin/python tools/train/audit_next.py --status
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIKIS = ["opm", "csm", "marvel", "mcu", "berserk", "bleach", "db", "onepiece", "hxh"]


def paths(series, pool):
    lab = ROOT / "series" / series / "training" / "labels"
    return (lab / ("pool_in.jsonl" if pool == "pool" else "test_in.jsonl"),
            lab / f"{pool}_verified.jsonl", lab / f"{pool}_review_cursor.txt")


def cursor(c):
    try:
        return int(c.read_text().strip())
    except (OSError, ValueError):
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series")
    ap.add_argument("--pool", default="pool")
    ap.add_argument("--max", type=int, default=25)
    ap.add_argument("--mark", type=int, default=None, help="set the reviewed-through count")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--chars", type=int, default=700)
    a = ap.parse_args()
    if a.status:
        for s in WIKIS:
            for pool in ("pool", "test"):
                _src, ver, cur = paths(s, pool)
                n = sum(1 for _ in open(ver)) if ver.exists() else 0
                if n:
                    print(f"{s}/{pool}: saved {n}, reviewed {cursor(cur)}, waiting {n - cursor(cur)}")
        return 0
    src, ver, cur = paths(a.series, a.pool)
    if a.mark is not None:
        cur.write_text(str(a.mark))
        print(f"{a.series}/{a.pool}: reviewed through {a.mark}")
        return 0
    text = {json.loads(l)["id"]: json.loads(l)["messages"][1]["content"].split("Passage:\n", 1)[1]
            for l in open(src)}
    recs = [json.loads(l) for l in open(ver)] if ver.exists() else []
    start = cursor(cur)
    for i, r in enumerate(recs[start:start + a.max], start + 1):
        t = text[r["id"]].replace("\n", " ")
        rows = [(e.get("subject"), e.get("verb"), e.get("object"), (e.get("quote") or "")[:40])
                for e in r.get("final") or []]
        if not rows and len(t) < 220:
            print(f"== w{i} EMPTY: {t[:200]}")
            continue
        print(f"===== w{i} {r.get('page')} / {r.get('section')}")
        print(t[:a.chars])
        print(" FINAL", rows)
    print(f"[printed w{start + 1}..w{min(len(recs), start + a.max)} of {len(recs)}; "
          f"mark with --mark {min(len(recs), start + a.max)}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Refresh a per-line evaluation file from the live gold audit (latest record per window id, the compose rule),
re-projecting the target through the engine resolver. Written for the 2026-11-14 owner-approved correction of 11
JJK dev windows (gold_audit_v2.jsonl 4,201 -> 4,213 lines): the held-out targets must score both systems on the
corrected rows. Windows whose layers are unchanged are copied as they are.

    python tools/train/perline_refresh_gold.py --in s2data/holdout.jsonl --gold GOLD_AUDIT --db STORE_COPY --out holdout_fixed.jsonl
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from perline_build import build  # noqa: E402
from perline_candidates import Resolver  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--gold", required=True)
ap.add_argument("--db", help="one store COPY (single-series file)"); ap.add_argument("--out", required=True)
# the per-line TRAIN file spans seven series (2026-11-14 train-window audit, 181 windows changed): one resolver per
# series, built from the same store copies perline_build used, or the re-projected candidate lists drift
ap.add_argument("--stores", help="dir of store COPIES named <series>.db"); ap.add_argument("--jjk-db")
ap.add_argument("--identity", action="store_true", help="also rebuild every UNCHANGED window and count byte-equal "
                "rows: proves the stores and code reproduce the old file before trusting the changed ones")
a = ap.parse_args()
latest = {}
for l in open(a.gold):
    r = json.loads(l); latest[r["id"]] = r
_R = {}
def resolver(series):
    if a.db: db = a.db
    elif series == "jjk" and a.jjk_db: db = a.jjk_db
    else: db = f"{a.stores}/{series}.db"
    if db not in _R: _R[db] = Resolver(db)
    return _R[db]
changed, same, differ = [], 0, []
with open(a.out, "w") as f:
    for l in open(a.inp):
        r = json.loads(l); g = latest.get(r["id"])
        if g and any(g[k] != r[k] for k in ("events", "facts", "tags")):
            new = build(dict(r, events=g["events"], facts=g["facts"], tags=g["tags"]), resolver(r["series"]))
            new["split"] = r["split"]; r = new; changed.append((g.get("b"), r["id"], r["split"]))
        elif a.identity:
            re_ = build(r, resolver(r["series"])); re_["split"] = r["split"]
            if re_ == r: same += 1
            else: differ.append((r["series"], r["id"]))
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(json.dumps({"changed": len(changed), "identity_same": same, "identity_differ": len(differ),
                  "differ": differ[:20], "windows": changed}))

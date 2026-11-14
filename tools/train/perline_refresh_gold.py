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
ap.add_argument("--db", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
latest = {}
for l in open(a.gold):
    r = json.loads(l); latest[r["id"]] = r
R = Resolver(a.db); changed = []
with open(a.out, "w") as f:
    for l in open(a.inp):
        r = json.loads(l); g = latest.get(r["id"])
        if g and any(g[k] != r[k] for k in ("events", "facts", "tags")):
            new = build(dict(r, events=g["events"], facts=g["facts"], tags=g["tags"]), R)
            new["split"] = r["split"]; r = new; changed.append((g.get("b"), r["id"], r["split"]))
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(json.dumps({"changed": len(changed), "windows": changed}))

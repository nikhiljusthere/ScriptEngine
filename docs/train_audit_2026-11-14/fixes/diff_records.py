#!/usr/bin/env python3
"""What a fix batch changed: compare each window's last record with the one before it in an audit file.
    python3 fixes/diff_records.py AUDIT.jsonl N      (N = number of records the batch appended)
"""
import json, sys
lines = [l.strip("\x00\n ") for l in open(sys.argv[1])]; lines = [json.loads(l) for l in lines if l]
n = int(sys.argv[2]); old = {}
for r in lines[:-n]:
    if not r.get("void"): old[r["id"]] = r
tot = [0, 0, 0, 0, 0]
key = {"events": lambda e: (e["subject"], e["verb"], e.get("object"), e["quote"]),
       "facts": lambda f: (f["subject"], f["relation"], f.get("object"), f.get("modality") or "actual", f.get("certainty") or "stated", f.get("asserted_by") or "", f.get("canon") or "", f["quote"]),
       "tags": lambda t: (t["tag"], t["quote"])}
for r in lines[-n:]:
    o = old[r["id"]]; out = []
    for k in ("events", "facts", "tags"):
        a = {key[k](x) for x in o[k]}; b = {key[k](x) for x in r[k]}
        for x in sorted(a - b, key=str): out.append(f"   - {k[:-1]} {'|'.join(str(y) for y in x)}")
        for x in sorted(b - a, key=str): out.append(f"   + {k[:-1]} {'|'.join(str(y) for y in x)}")
        tot[0] += len(a - b); tot[1] += len(b - a)
    if "-v" in sys.argv: print(r["id"], r.get("why", "")[:80]); print("\n".join(out))
    tot[2] += 1
print(f"{tot[2]} windows: {tot[0]} rows removed, {tot[1]} rows added")

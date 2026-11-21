#!/usr/bin/env python3
"""Strict check that a blind output file is the reading of ITS input: same ids in the same order, and for each
window the same sentence numbers. Then a per-window sanity test against the gold: a window labelled from the
wrong passage shows up as near-zero class agreement.

    python check_ids.py INPUT.jsonl BLIND.jsonl [GOLD.jsonl]
"""
import json, sys
inp = [json.loads(l) for l in open(sys.argv[1])]
out = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
ids_in, ids_out = [r["id"] for r in inp], [r["id"] for r in out]
foreign = [i for i in ids_out if i not in set(ids_in)]
missing = [i for i in ids_in if i not in set(ids_out)]
dup = len(ids_out) - len(set(ids_out))
badn = sum(1 for r in out if r["id"] in set(ids_in) and sorted(int(l["n"]) for l in r["lines"]) != sorted(int(k) for k in next(x for x in inp if x["id"] == r["id"])["sentences"]))
print(f"input {len(ids_in)} output {len(ids_out)} | foreign ids {len(foreign)} | missing {len(missing)} | duplicates {dup} | order ok {ids_out == ids_in} | wrong sentence numbers {badn}")
if len(sys.argv) > 3:
    gold = {json.loads(l)["id"]: json.loads(l) for l in open(sys.argv[3])}
    sus = []
    for r in out:
        g = gold.get(r["id"])
        if not g: continue
        gl = {l["n"]: l["class"] for l in g["target"]["lines"]}
        n = len(r["lines"]); agree = sum(gl.get(int(l["n"])) == l["class"] for l in r["lines"])
        cand = len(g["candidates"]); over = any(p > cand for l in r["lines"] for p in l.get("people", []))
        if over or (n >= 4 and agree / n < 0.4): sus.append((r["id"], f"{agree}/{n}", g["page"][:40]))
    print(f"windows whose labels look like another passage's: {len(sus)}", sus[:6])

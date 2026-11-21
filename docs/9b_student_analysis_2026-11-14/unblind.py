#!/usr/bin/env python3
"""Unblind an adjudication: verdicts file lines are `<row number> <V|W|X> [group]`.

    python unblind.py --sheet sheet.txt --key key.json --verdicts verdicts.txt
"""
import argparse, collections, json, re

ap = argparse.ArgumentParser()
ap.add_argument("--sheet", required=True); ap.add_argument("--key", required=True); ap.add_argument("--verdicts", required=True)
a = ap.parse_args()
key = json.load(open(a.key))
V = {}
for l in open(a.verdicts):
    p = l.split()
    if p:
        V[f"R{int(p[0]):03d}"] = (p[1], p[2] if len(p) > 2 else None)
assert set(V) == set(key), "every row needs a verdict"
agreed = sum(int(x) for x in re.findall(r"agreed rows: (\d+)", open(a.sheet).read()))
grp = collections.defaultdict(list)
for c, (v, g) in V.items():
    if g:
        grp[(key[c]["win"], g)].append(c)
cross = {c for cs in grp.values() if {key[c]["src"] for c in cs} == {"S", "G"} for c in cs}
n = lambda src, v, inc=None: sum(1 for c, (vv, _) in V.items() if key[c]["src"] == src and vv == v and (inc is None or (c in cross) == inc))
S, G = agreed + sum(n("S", v) for v in "VWX"), agreed + sum(n("G", v) for v in "VWX")
print(f"agreed {agreed}; student rows {S}; gold rows {G}; scored P {agreed / S:.3f} R {agreed / G:.3f}")
for src, name, tot in (("S", "student-only", S), ("G", "gold-only", G)):
    print(f"{name}: V {n(src, 'V')}  W {n(src, 'W')}  X {n(src, 'X')}  -> wrong rows {n(src, 'X')}/{tot} = {n(src, 'X') / tot:.1%}")
print(f"same statement, two encodings: {len(cross)}/{len(V)} disagreement rows = {len(cross) / len(V):.0%}")
print(f"real student misses (gold-only V, no student encoding of the statement): {n('G', 'V', False)} (+{n('G', 'W', False)} defensible) of {G}")
print(f"valid statements the gold lacks (student-only V, no gold encoding): {n('S', 'V', False)} (+{n('S', 'W', False)} defensible)")

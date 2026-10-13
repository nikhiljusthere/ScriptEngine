"""recon_check.py C [C...] | all  -> remaining diffs for those components' overlap pairs
(re-derived from the latest audit; also re-checks every overlap pair inside the component)."""
import json, sys
from recon_lib import RECON, bv, load, overlap_pairs, pair_diff

comps = [json.loads(l) for l in open(RECON / "components.jsonl")]
want = None if sys.argv[1:] == ["all"] else {int(x) for x in sys.argv[1:]}
ids, sents = load()
a2 = bv.audit2()
allp = overlap_pairs(sents) if want is None else None
left = 0
for c in comps:
    if want is not None and c["c"] not in want:
        continue
    ws = c["windows"]
    ps = [(a, b) for i, a in enumerate(ws) for b in ws[i + 1:]]
    for a, b in ps:
        nb = {bv.big_flags.norm(y) for y in sents[b] if len(y) > 60}
        if sum(1 for x in sents[a] if len(x) > 60 and bv.big_flags.norm(x) in nb) < 2:
            continue
        d = pair_diff(a, b, ids, sents, a2)
        if d:
            left += 1
            print(f"C{c['c']} b{a}~b{b} DIFF")
            for n, x, y in d:
                print(f"  {n}: only b{a}: {x}\n  {n}: only b{b}: {y}")
if want is None:
    bad = sum(1 for (a, b) in allp if pair_diff(a, b, ids, sents, a2))
    print(f"ALL: {len(allp)} overlap pairs, {bad} inconsistent")
print(f"{left} inconsistent pairs in the checked components")

"""Build recon/components.jsonl: conflicting overlap pairs grouped into connected components
(a window in two conflicting pairs puts both pairs in one component, so no window is edited by
two sessions), split between the two sessions by window count. Run once."""
import json
from recon_lib import RECON, bv, load, overlap_pairs, pair_diff

ids, sents = load()
a2 = bv.audit2()
pairs = overlap_pairs(sents)
bad = [(a, b) for (a, b) in sorted(pairs) if pair_diff(a, b, ids, sents, a2)]
par = {}
def f(x):
    par.setdefault(x, x)
    while par[x] != x:
        par[x] = par[par[x]]; x = par[x]
    return x
for a, b in bad:
    par[f(a)] = f(b)
comp = {}
for a, b in bad:
    comp.setdefault(f(a), []).append([a, b])
comps = sorted(({"windows": sorted({w for p in ps for w in p}), "pairs": ps} for ps in comp.values()),
               key=lambda c: c["windows"][0])
load_ = {"app": 0, "term": 0}
for i, c in enumerate(comps, 1):
    c["c"] = i
for c in sorted(comps, key=lambda c: -len(c["windows"])):
    who = min(load_, key=load_.get)
    c["owner"] = who
    load_[who] += len(c["windows"])
RECON.mkdir(exist_ok=True)
with open(RECON / "components.jsonl", "w") as fh:
    for c in comps:
        fh.write(json.dumps(c) + "\n")
sizes = sorted((len(c["windows"]) for c in comps), reverse=True)
print(f"{len(pairs)} overlap pairs, {len(bad)} conflicting, {len(comps)} components; "
      f"largest {sizes[:8]}; windows per owner {load_}; "
      f"components per owner app={sum(c['owner']=='app' for c in comps)} term={sum(c['owner']=='term' for c in comps)}")

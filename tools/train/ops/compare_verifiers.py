"""Per-window Q6 verifier vs row-by-row Q6+wiki verifier, on the same adjudicated windows."""
import json, sys
sys.path.insert(0, "tools"); sys.path.insert(0, "tools/train")
from eval_extraction import match
from gold_tools import key
D = "series/jjk/training/gold/"
cand = {json.loads(l)["id"]: json.loads(l)["events"] for l in open(D + "cand_q6_pilot400.jsonl")}
gold = {json.loads(l)["id"]: json.loads(json.loads(l)["messages"][2]["content"])["events"] for l in open(D + "gold_pilot_all.jsonl")}
win = {json.loads(l)["id"]: {x["n"]: x["ok"] for x in json.loads(l)["verdicts"]} for l in open(D + "verify_q6_pilot400.jsonl") if json.loads(l)["ok"]}
row = {json.loads(l)["id"]: {x["n"]: x["ok"] for x in json.loads(l)["rows"]} for l in open(D + "verifyrow_1000.jsonl") if json.loads(l)["ok"]}
common = [i for i in win if i in row]
res = {"per-window": [0, 0, 0, 0], "row+wiki": [0, 0, 0, 0], "both say yes": [0, 0, 0, 0]}
for i in common:
    g = gold[i]; gk = {key(e) for e in g}; gt = [(e["subject"], e["verb"], e["object"]) for e in g]
    for n, c in enumerate(cand[i]):
        t = (c.get("subject"), (c.get("verb") or "").lower(), c.get("object"))
        if key(c) in gk: truth = 1
        elif not any(match(t, x) for x in gt): truth = 0
        else: continue
        # fought/met are symmetric: a kept pair counts when the verifier kept EITHER twin
        twins = [m for m, d in enumerate(cand[i]) if m != n and t[1] in ("fought", "met")
                 and (d.get("verb") or "").lower() == t[1] and match((d.get("subject"), t[1], d.get("object")), (t[2], t[1], t[0]))]
        def got(vs): return int(bool(vs.get(n)) or (truth == 1 and any(vs.get(m) for m in twins)))
        for name, v in (("per-window", got(win[i])), ("row+wiki", got(row[i])),
                        ("both say yes", int(got(win[i]) and got(row[i])))):
            r = res[name]; r[0 if truth else 2] += 1; r[1 if truth else 3] += v
print(f"windows compared: {len(common)}")
for name, (P, kp, N, kn) in res.items():
    print(f"{name:13s} correct rows passed {kp}/{P} = {kp/max(P,1):.3f}   wrong rows passed {kn}/{N} = {kn/max(N,1):.3f}   balanced-acc {(kp/max(P,1) + 1 - kn/max(N,1))/2:.3f}")

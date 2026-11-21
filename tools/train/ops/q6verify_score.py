"""Q6 verifier vs the adjudicated pilot gold, measured like the OpenJEV test:
correct rows = kept in gold; wrong rows = rejected and not a redundant duplicate."""
import json, sys
sys.path.insert(0, "tools"); sys.path.insert(0, "tools/train")
from eval_extraction import match
from gold_tools import key
D = "series/jjk/training/gold/"
cand = {json.loads(l)["id"]: json.loads(l)["events"] for l in open(D + "cand_q6_pilot400.jsonl")}
gold = {json.loads(l)["id"]: json.loads(json.loads(l)["messages"][2]["content"])["events"] for l in open(D + "gold_pilot_all.jsonl")}
P = N = kp = kn = 0; wins = 0
for l in open(D + "verify_q6_pilot400.jsonl"):
    v = json.loads(l)
    if not v["ok"]: continue
    wins += 1; g = gold[v["id"]]; gk = {key(e) for e in g}; gt = [(e["subject"], e["verb"], e["object"]) for e in g]
    ver = {x["n"]: x["ok"] for x in v["verdicts"]}
    for n, c in enumerate(cand[v["id"]]):
        t = (c.get("subject"), (c.get("verb") or "").lower(), c.get("object"))
        if key(c) in gk: P += 1; kp += ver.get(n, 0)
        elif not any(match(t, x) for x in gt): N += 1; kn += ver.get(n, 0)
print(f"windows {wins}  correct rows {P} passed {kp/P:.3f}  wrong rows {N} passed {kn/N:.3f}  balanced-acc {(kp/P + 1 - kn/N)/2:.3f}")

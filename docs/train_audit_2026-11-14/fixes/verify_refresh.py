#!/usr/bin/env python3
"""Independent check of the per-line training file after the training session refreshes it from the gold:
every window's events, facts and tags must equal the latest gold record, and the per-line target must have
been rebuilt for windows whose events or names changed.

    python3 fixes/verify_refresh.py [TRAIN.jsonl] [OLD_COPY.jsonl]
"""
import collections, json, sys
G = "/home/goblin/ScriptEngine/series/universal/training/big/gold_v2/"
TRAIN = sys.argv[1] if len(sys.argv) > 1 else "/home/goblin/student_runs_local/jjk_side/s2data/train.jsonl"
OLD = sys.argv[2] if len(sys.argv) > 2 else None
hist = {}
for l in open(G + "gold_audit_v2.jsonl"):
    l = l.strip("\x00\n ")
    if l:
        r = json.loads(l)
        if r.get("void"): hist.pop(r["id"], None)
        else: hist[r["id"]] = r
changed = {r["id"]: r for r in json.load(open("fixes/changed_windows.json"))}
ev = lambda rows: sorted((e["subject"], e["verb"], e.get("object") or "", e["quote"]) for e in rows)
fa = lambda rows: sorted((f["subject"], f["relation"], f.get("object") or "", f.get("modality") or "actual", f["quote"]) for f in rows)
tg = lambda rows: sorted((t["tag"], t["quote"]) for t in rows)
rows = [json.loads(l) for l in open(TRAIN)]
old = {json.loads(l)["id"]: json.loads(l) for l in open(OLD)} if OLD else {}
C = collections.Counter(); bad = []
for r in rows:
    g = hist[r["id"]]; C["windows"] += 1
    same = ev(r["events"]) == ev(g["events"]) and fa(r["facts"]) == fa(g["facts"]) and tg(r["tags"]) == tg(g["tags"])
    C["rows equal the gold"] += same
    if r["id"] in changed:
        C["changed windows present"] += 1; C["changed windows equal the gold"] += same
        if not same: bad.append(r["id"])
        if old:
            o = old[r["id"]]
            C["changed windows: per-line target differs from before"] += o["target"] != r["target"]
            C["changed windows: prompt differs from before"] += o["messages"] != r["messages"]
    elif old:
        C["unchanged windows whose target moved"] += old[r["id"]]["target"] != r["target"]
    # the target must agree with the messages' assistant turn
    a = [m for m in r["messages"] if m["role"] == "assistant"]
    if a:
        try: C["assistant turn equals target"] += json.loads(a[-1]["content"]) == r["target"]
        except Exception: C["assistant turn not JSON"] += 1
for k, v in C.items(): print(f"{v:6d}  {k}")
print("changed windows NOT equal to the gold:", bad[:10])

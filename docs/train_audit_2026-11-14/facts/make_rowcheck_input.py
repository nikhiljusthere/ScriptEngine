#!/usr/bin/env python3
"""A random sample of training windows for a row-by-row check of EVERY gold row (events, facts, tags), to
measure what the other passes leave behind. Sample is drawn per series in proportion, fixed seed.

    python3 facts/make_rowcheck_input.py [N=70] [SEED=11]   -> facts/RC_input.jsonl
"""
import collections, json, random, sys
N = int(sys.argv[1]) if len(sys.argv) > 1 else 70; SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 11
G = "/home/goblin/ScriptEngine/series/universal/training/big/gold_v2/"
bnum = {json.loads(l)["id"]: i for i, l in enumerate(open(G + "gold_in.jsonl"), 1)}
hist = {}
for l in open(G + "gold_audit_v2.jsonl"):
    l = l.strip("\x00\n ")
    if l:
        r = json.loads(l)
        if r.get("void"):
            if hist.get(r["id"]): hist[r["id"]].pop()
        else: hist.setdefault(r["id"], []).append(r)
inp = {json.loads(l)["id"]: json.loads(l) for l in open("blind/train_all_input.jsonl")}
tr = [json.loads(l) for l in open("/home/goblin/student_runs_local/jjk_side/s2data/train.jsonl")]
by = collections.defaultdict(list)
for r in tr: by[r["series"]].append(r)
rng = random.Random(SEED); pick = []
for s, rows in sorted(by.items()):
    k = max(1, round(N * len(rows) / len(tr)))
    # leave out the giant list windows: they would eat the sample
    rows = [r for r in rows if len(inp[r["id"]]["sentences"]) <= 20]
    pick += rng.sample(rows, k)
out = []
for r in pick:
    i = r["id"]; a = hist[i][-1]; w = inp[i]
    out.append({"b": bnum[i], "id": i, "series": r["series"], "page": r["page"], "section": w["section"],
                "page_text_before": w["page_text_before"], "sentences": w["sentences"], "page_text_after": w["page_text_after"],
                "gold_events": [[e["subject"], e["verb"], e["object"], e["quote"]] for e in a["events"]],
                "gold_facts": [[f["subject"], f["relation"], f["object"], f.get("modality") or "actual", f.get("certainty") or "stated", f.get("asserted_by"), f["quote"]] for f in a["facts"]],
                "gold_tags": [[t["tag"], t["quote"]] for t in a["tags"]],
                "reviewer_notes": [h.get("why") for h in hist[i]]})
with open("facts/RC_input.jsonl", "w") as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
n = lambda k: sum(len(r[k]) for r in out)
print(len(out), "windows;", collections.Counter(r["series"] for r in out), "rows:", n("gold_events"), "events", n("gold_facts"), "facts", n("gold_tags"), "tags")

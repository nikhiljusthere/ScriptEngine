#!/usr/bin/env python3
"""Pilot input for Addendum 7 (draft): training windows with a sentence left unrecorded because the doer or
participant was not named in the passage, each with a wide slice of its page before and after, its current
gold rows and tags, and the reviewer's notes.

    python3 ctx/make_ctx_input.py [N=60] [SEED=7]   -> ctx/P1_input.jsonl
"""
import collections, json, random, sqlite3, sys
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60; SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 7
BEFORE, AFTER = 1600, 900
G = "/home/goblin/ScriptEngine/series/universal/training/big/gold_v2/"; ROOT = "/home/goblin/ScriptEngine/series"
MUST = [1100, 737, 66, 29, 195, 357, 281, 97, 1408, 1048, 1337, 3065, 1448, 1058, 1046, 1330, 1254]
bnum = {json.loads(l)["id"]: i for i, l in enumerate(open(G + "gold_in.jsonl"), 1)}
hist = {}
for l in open(G + "gold_audit_v2.jsonl"):
    l = l.strip("\x00\n ")
    if l:
        r = json.loads(l)
        if r.get("void"):
            if hist.get(r["id"]): hist[r["id"]].pop()
        else: hist.setdefault(r["id"], []).append(r)
tr = {json.loads(l)["id"]: json.loads(l) for l in open("/home/goblin/student_runs_local/jjk_side/s3data/train.jsonl")}
sents = {json.loads(l)["id"]: json.loads(l)["sentences"] for l in open("blind/train_all_input.jsonl")}
byb = {bnum[i]: i for i in tr}
pool = collections.defaultdict(list)
for i, r in tr.items():
    if any(t["tag"] in ("no_doer", "crowd_end") for t in hist[i][-1]["tags"]): pool[r["series"]].append(i)
rng = random.Random(SEED); pick = [byb[b] for b in MUST if b in byb]
left = N - len(pick); tot = sum(len(v) for v in pool.values())
for s in sorted(pool):
    cand = [i for i in pool[s] if i not in pick and len(sents[i]) <= 20]
    pick += rng.sample(cand, min(len(cand), max(1, round(left * len(pool[s]) / tot))))
norm = lambda s: " ".join(s.split()); dbs, pages = {}, {}; out = []; noctx = 0
for i in pick:
    r = tr[i]; s = r["series"]; a = hist[i][-1]
    if s not in dbs: dbs[s] = sqlite3.connect(f"file:{ROOT}/{s}/facts.db?mode=ro", uri=True)
    if (s, r["page"]) not in pages:
        pages[(s, r["page"])] = norm(" ".join(x[0] for x in dbs[s].execute(
            "select s.text from sections s join documents d on d.id = s.document_id where d.title = ? order by s.ordinal", (r["page"],))))
    page, p = pages[(s, r["page"])], norm(r["passage"]); k = page.find(p[:60])
    before, after = (page[max(0, k - BEFORE):k], page[k + len(p):k + len(p) + AFTER]) if k >= 0 else ("", "")
    noctx += k < 0
    out.append({"b": bnum[i], "id": i, "series": s, "page": r["page"], "section": r.get("section", ""),
                "candidates_of_the_page": r["candidates"], "page_text_before": before, "sentences": sents[i], "page_text_after": after,
                "gold_events": [[e["subject"], e["verb"], e["object"], e["quote"]] for e in a["events"]],
                "gold_facts": [[f["subject"], f["relation"], f["object"], f.get("modality") or "actual", f.get("certainty") or "stated", f.get("asserted_by"), f["quote"]] for f in a["facts"]],
                "gold_tags": [[t["tag"], t["quote"]] for t in a["tags"]],
                "reviewer_notes": [h.get("why") for h in hist[i]]})
out.sort(key=lambda r: r["b"])
with open("ctx/P1_input.jsonl", "w") as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(out), "windows;", dict(collections.Counter(r["series"] for r in out)), "| no page context found:", noctx,
      "| no_doer tags:", sum(t[0] == "no_doer" for r in out for t in r["gold_tags"]), "crowd_end tags:", sum(t[0] == "crowd_end" for r in out for t in r["gold_tags"]))

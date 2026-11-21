#!/usr/bin/env python3
"""Third-look input for one chunk: for each window where the blind reading and the gold differ on an event
or on a person, everything an adjudicator needs: the window, the page text around it, the gold rows with
their quotes, the reviewer's notes, the blind reader's lines with names, and the differences.

    python make_adj_input.py NN      -> adj/chunk_NN_adj_input.jsonl
"""
import json, sys
n = sys.argv[1]
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
inp = {json.loads(l)["id"]: json.loads(l) for l in open(f"blind/chunks/chunk_{n}_input.jsonl")}
blind = {json.loads(l)["id"]: json.loads(l) for l in open(f"blind/chunks/chunk_{n}_blind.jsonl")}
work = [json.loads(l) for l in open(f"blind/chunks/chunk_{n}_work.jsonl")]
out = []
for w in work:
    i = w["id"]; a = hist[i][-1]; c = inp[i]["candidates"]; nm = lambda k: c[str(k)] if k else None
    out.append({"b": bnum[i], "id": i, "series": w["series"], "page": w["page"], "section": inp[i]["section"],
                "page_text_before": inp[i]["page_text_before"], "sentences": inp[i]["sentences"], "page_text_after": inp[i]["page_text_after"],
                "gold_events": [[e["subject"], e["verb"], e["object"], e["quote"]] for e in a["events"]],
                "gold_facts": [[f["subject"], f["relation"], f["object"], f.get("modality") or "actual", f.get("certainty") or "stated", f.get("asserted_by"), f["quote"]] for f in a["facts"]],
                "gold_tags": [[t["tag"], t["quote"]] for t in a["tags"]],
                "reviewer_notes": [h.get("why") for h in hist[i]],
                "second_reader": [{"n": l["n"], "class": l["class"], "real": l.get("real", True), "people": [nm(p) for p in l.get("people", [])],
                                   "events": [[e[0], nm(e[1]), nm(e[2])] for e in l.get("events", [])]} for l in blind[i]["lines"]],
                "second_reader_only_events": w["blind_only"], "gold_only_events": w["gold_only"], "gold_people_second_reader_omits": w["gold_people_unlisted"]})
with open(f"adj/chunk_{n}_adj_input.jsonl", "w") as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"chunk {n}: {len(out)} windows for the third look, {sum(len(r['second_reader_only_events']) + len(r['gold_only_events']) for r in out)} event differences")

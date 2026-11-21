#!/usr/bin/env python3
"""Input for the fact-layer third look: every training window with a script finding that needs reading
(a sentence nothing labels, a name that is not in the window, a name longer than the window writes it),
with the window, the page text around it, the gold rows and the reviewer notes.

    python3 facts/make_fl_input.py        -> facts/FL1_input.jsonl, facts/FL2_input.jsonl
"""
import collections, json, re
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
tr = {json.loads(l)["id"]: json.loads(l) for l in open("/home/goblin/student_runs_local/jjk_side/s2data/train.jsonl")}
d = json.load(open("facts/mech_candidates.json"))
SKIP = {944, 439, 474, 1507, 1170}          # lists and headings cut into fragments, nothing to label
find = collections.defaultdict(list)
for b, i, n, s in d["M4"]:
    if b not in SKIP: find[i].append({"type": "sentence_with_no_row_and_no_tag", "n": n, "sentence": s})
norm = lambda s: re.sub(r"\s+", " ", s or "").strip().lower()
words = lambda s: [w for w in re.findall(r"[^\W\d_]+", s.lower()) if len(w) >= 3]
for i, r in tr.items():
    g = hist[i][-1]; text = norm(r["passage"]); page = norm(r["page"])
    names = set()
    for e in g["events"]: names |= {e["subject"], e.get("object")}
    for f in g["facts"]: names.add(f["subject"])
    for nme in sorted(x for x in names if x):
        if norm(nme) in text: continue
        w = words(nme); inwin = [x for x in w if re.search(r"(?<!\w)" + re.escape(x) + r"(?!\w)", text)]
        if not inwin:
            if any(x in page for x in w): continue      # the page's own subject behind a pronoun: legal
            find[i].append({"type": "name_not_in_window", "name": nme})
        else:
            find[i].append({"type": "name_longer_than_the_window_writes_it", "name": nme, "words_in_window": inwin})
out = []
for i, fs in find.items():
    a = hist[i][-1]; w = inp[i]
    out.append({"b": bnum[i], "id": i, "series": tr[i]["series"], "page": tr[i]["page"], "section": w["section"],
                "page_text_before": w["page_text_before"], "sentences": w["sentences"], "page_text_after": w["page_text_after"],
                "gold_events": [[e["subject"], e["verb"], e["object"], e["quote"]] for e in a["events"]],
                "gold_facts": [[f["subject"], f["relation"], f["object"], f.get("modality") or "actual", f.get("certainty") or "stated", f.get("asserted_by"), f["quote"]] for f in a["facts"]],
                "gold_tags": [[t["tag"], t["quote"]] for t in a["tags"]],
                "reviewer_notes": [h.get("why") for h in hist[i]], "script_findings": fs})
out.sort(key=lambda r: r["b"]); half = (len(out) + 1) // 2
for k, part in (("FL1", out[:half]), ("FL2", out[half:])):
    with open(f"facts/{k}_input.jsonl", "w") as f:
        for r in part: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(k, len(part), "windows", collections.Counter(x["type"] for r in part for x in r["script_findings"]))

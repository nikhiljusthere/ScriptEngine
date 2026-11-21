#!/usr/bin/env python3
"""Blind second-reading input: the passages of a per-line file with their numbered sentences and candidate
list and the page text just before and after (from the downloaded page), and NO labels.

    python make_blind_input.py --series-root /home/goblin/ScriptEngine/series IN.jsonl OUT.jsonl [--split dev] [--ids FILE]
"""
import argparse, json, re, sqlite3

ap = argparse.ArgumentParser()
ap.add_argument("--series-root", required=True); ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--split"); ap.add_argument("--ids")
a = ap.parse_args()
norm = lambda s: " ".join(s.split())
rows = [json.loads(l) for l in open(a.inp)]
if a.split: rows = [r for r in rows if str(r.get("split", "")).startswith(a.split)]
if a.ids:
    keep = set(json.load(open(a.ids))); rows = [r for r in rows if r["id"] in keep]
dbs, pages, n_ctx = {}, {}, 0
with open(a.out, "w") as f:
    for r in rows:
        s = r["series"]
        if s not in dbs: dbs[s] = sqlite3.connect(f"file:{a.series_root}/{s}/facts.db?mode=ro", uri=True)
        if (s, r["page"]) not in pages:
            pages[(s, r["page"])] = norm(" ".join(x[0] for x in dbs[s].execute(
                "select s.text from sections s join documents d on d.id = s.document_id where d.title = ? order by s.ordinal", (r["page"],))))
        page, p = pages[(s, r["page"])], norm(r["passage"])
        i = page.find(p[:60])
        before, after = (page[max(0, i - 400):i], page[i + len(p):i + len(p) + 250]) if i >= 0 else ("", "")
        n_ctx += i >= 0
        user = r["messages"][1]["content"]
        sents = re.findall(r"^\[(\d+)\] (.*)$", user.split("Sentences:\n", 1)[1], flags=re.M)
        f.write(json.dumps({"id": r["id"], "series": s, "page": r["page"], "section": r.get("section", ""),
                            "page_text_before": before, "candidates": {str(i): c for i, c in enumerate(r["candidates"], 1)},
                            "sentences": {n: t for n, t in sents}, "page_text_after": after}, ensure_ascii=False) + "\n")
print(f"{len(rows)} windows -> {a.out}; with page context {n_ctx}; sentences {sum(1 for r in rows for _ in r['target']['lines'])}")

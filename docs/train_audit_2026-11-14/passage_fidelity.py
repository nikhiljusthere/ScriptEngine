#!/usr/bin/env python3
"""Check each training passage against the downloaded page (the series store built from the crawl).

For every window: is the passage found word for word in the stored text of its page; if not, how many of
its sentences are; and does it carry parser debris (template braces, link brackets, a hole where a link or
template was dropped). Also how the per-line builder's sentence splitter cuts it.

    python passage_fidelity.py --tools <repo>/tools --series-root /home/goblin/ScriptEngine/series FILE.jsonl
"""
import argparse, collections, json, re, sqlite3, sys

ap = argparse.ArgumentParser()
ap.add_argument("--tools", required=True); ap.add_argument("--series-root", required=True); ap.add_argument("file")
ap.add_argument("--examples", type=int, default=3)
a = ap.parse_args()
sys.path.insert(0, a.tools + "/train")
import fact_gate  # noqa: E402

norm = lambda s: " ".join(s.split())
DEBRIS = [("template braces", re.compile(r"\{\{|\}\}")), ("link brackets", re.compile(r"\[\[|\]\]")),
          ("empty brackets", re.compile(r"\(\s*\)|\[\s*\]")),
          ("hole after an article", re.compile(r"\b(a|an|the|of|by|with|in|to|as) (in|to|of|and|that|,|\.|was|is)\b(?<!to to)", re.I)),
          ("space before punctuation", re.compile(r"\w ([,.;:])(\s|$)")), ("html or file residue", re.compile(r"</?\w+>|\bFile:|\bthumb\|", re.I))]
ABBR = re.compile(r"\b(Dr|Mr|Mrs|Ms|St|Lt|Sgt|Jr|Sr|No|Vol|Ch|Ep|vs|Mt|Prof|Capt|Gen|Col)\.$")
rows = [json.loads(l) for l in open(a.file)]
dbs, pages = {}, {}
C = collections.Counter(); per = collections.defaultdict(collections.Counter); ex = collections.defaultdict(list)
for r in rows:
    s = r["series"]
    if s not in dbs:
        dbs[s] = sqlite3.connect(f"file:{a.series_root}/{s}/facts.db?mode=ro", uri=True)
    key = (s, r["page"])
    if key not in pages:
        t = [x[0] for x in dbs[s].execute("select s.text from sections s join documents d on d.id = s.document_id where d.title = ?", (r["page"],))]
        pages[key] = norm(" ".join(t)) if t else None
    C["windows"] += 1; per[s]["windows"] += 1
    p = norm(r["passage"]); page = pages[key]
    if page is None:
        C["page not in the store"] += 1; per[s]["page missing"] += 1
        if len(ex["page not in the store"]) < a.examples: ex["page not in the store"].append(f"[{s}] {r['page']}")
    elif p in page:
        C["passage found word for word"] += 1; per[s]["verbatim"] += 1
    else:
        ss = [x for x in fact_gate.sentences(r["passage"]) if len(x) > 25]
        hit = sum(norm(x) in page for x in ss)
        k = "all sentences found, order or joins differ" if ss and hit == len(ss) else "some sentences not in the stored page"
        C[k] += 1; per[s][k.split(",")[0][:24]] += 1
        if k.startswith("some") and len(ex[k]) < a.examples:
            miss = next(x for x in ss if norm(x) not in page)
            ex[k].append(f"[{s}] {r['page']}: {miss[:170]}")
    for name, rx in DEBRIS:
        m = rx.search(r["passage"])
        if m:
            C["debris: " + name] += 1
            if len(ex["debris: " + name]) < a.examples:
                i = m.start(); ex["debris: " + name].append(f"[{s}] {r['page']}: ...{r['passage'][max(0, i - 70):i + 60]}...".replace("\n", " / "))
    sents = fact_gate.sentences(r["passage"])
    C["sentences"] += len(sents)
    for x in sents:
        if ABBR.search(x.strip()):
            C["sentence cut after an abbreviation"] += 1
            if len(ex["sentence cut after an abbreviation"]) < a.examples: ex["sentence cut after an abbreviation"].append(f"[{s}] {x[-90:]}")
        if len(x.strip()) < 12: C["sentence under 12 characters"] += 1
        if x.strip()[:1].islower(): C["sentence starting lower-case"] += 1
for k, v in C.most_common():
    print(f"{v:6d}  {k}")
    for e in ex.get(k, []): print(f"            {e}")
print("by series:", {s: dict(c) for s, c in per.items()})

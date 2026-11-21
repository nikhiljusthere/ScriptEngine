#!/usr/bin/env python3
"""Source-blind adjudication sheet: the rows the student and the gold disagree on, shuffled, sources hidden.

A reader judges each row V (true to the passage and legal under the system prompt), W (defensible either
way / depends on a convention the prompt does not state) or X (wrong), and gives rows that encode the SAME
statement a shared group letter. unblind.py then reports, per source, how many scored errors are real.

    python build_sheet.py --tools <repo>/tools --gold dev_pool.jsonl --pred RUN/dev_preds_e1.jsonl \
        --out sheet.txt --key key.json [--per-series 4] [--seed 20261114]

Written for the 2026-11-14 analysis (40 dev_pool windows, 248 rows). Needs tools/train/score_layers_v2.py
and tools/eval_extraction.py from the big-review-flags branch.
"""
import argparse, collections, json, random, sys

ap = argparse.ArgumentParser()
ap.add_argument("--tools", required=True); ap.add_argument("--gold", required=True); ap.add_argument("--pred", required=True)
ap.add_argument("--out", required=True); ap.add_argument("--key", required=True)
ap.add_argument("--per-series", type=int, default=4); ap.add_argument("--seed", type=int, default=20261114)
a = ap.parse_args()
sys.path.insert(0, a.tools); sys.path.insert(0, a.tools + "/train")
import eval_extraction as ee, score_layers_v2 as sl  # noqa: E402

random.seed(a.seed)
gold = [json.loads(l) for l in open(a.gold)]
preds = sl.load(a.pred)
ev_ok = lambda p, g: ee.match((p.get("subject"), p.get("verb"), p.get("object")), (g.get("subject"), g.get("verb"), g.get("object")))
by = collections.defaultdict(list)
for g in gold:
    by[g["series"]].append(g)
sel = []
for s in sorted(by):
    c = [g for g in by[s] if 150 < len(g["passage"]) < 1400 and g["id"] in preds]
    random.shuffle(c); sel += c[:a.per_series]


def short(layer, x):
    if layer == "events":
        return f"EV  {x.get('subject')} | {x.get('verb')} | {x.get('object')}  «{x.get('quote')}»"
    if layer == "facts":
        extra = "".join(f" {k}={x.get(k)}" for k in ("modality", "certainty", "asserted_by", "canon") if x.get(k) not in (None, "actual", "stated"))
        return f"FA  {x.get('subject')} | {x.get('relation')} | {x.get('object')}{extra}  «{x.get('quote')}»"
    return f"TAG {x.get('tag')}  «{x.get('quote')}»"


key, out, n = {}, [], 0
for wi, g in enumerate(sel):
    p = preds[g["id"]]
    out.append(f"\n===== W{wi:02d} [{g['series']}] {g['page']} / {g['section']}\n{g['passage']}\n")
    items, matched = [], []
    for layer, ok in (("events", ev_ok), ("facts", sl.fact_match), ("tags", sl.tag_match)):
        pairs = sl.greedy(p[layer], g[layer], ok)[3]
        mp, mg = {id(x) for x, _ in pairs}, {id(y) for _, y in pairs}
        matched += [short(layer, y) for _, y in pairs]
        items += [("S", layer, x) for x in p[layer] if id(x) not in mp] + [("G", layer, x) for x in g[layer] if id(x) not in mg]
    out.append("  agreed rows: " + str(len(matched)))
    out += ["    = " + m for m in matched]
    random.shuffle(items)
    for src, layer, x in items:
        n += 1
        key[f"R{n:03d}"] = {"src": src, "layer": layer, "win": wi, "id": g["id"], "row": x}
        out.append(f"  R{n:03d} {short(layer, x)}")
open(a.out, "w").write("\n".join(out))
json.dump(key, open(a.key, "w"), ensure_ascii=False)
print("windows", len(sel), "rows to judge", n)

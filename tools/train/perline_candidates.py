#!/usr/bin/env python3
"""S1 of the per-line side test (owner 2026-11-14, relayed by the 9B analysis session): a page-disjoint
holdout of a series' gold_v2 train windows plus its dev windows, and for every window a candidate list of
entities built from the series store (a COPY of facts.db; read-only): the page's own node, every node the
page's node has an edge to, and every node whose name or alias occurs in the passage. Reports the share of
the gold's ends (event subject/object, fact subject/object; an other_verb object is a verb, not an end)
that some candidate covers under the event scorer's name rule (eval_extraction.same against the node name
or any alias).

    python3 tools/train/perline_candidates.py --series S --db COPY.db --split DIR --out DIR [--hold 150 --seed 7]
"""
import argparse, collections, json, random, re, sqlite3, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import eval_extraction as ee  # noqa: E402


def load_store(db):
    c = sqlite3.connect(f"file:{db}" if "?" in str(db) else f"file:{db}?mode=ro", uri=True)
    names = dict(c.execute("select id, name from nodes"))
    al = collections.defaultdict(set)
    for a, n in c.execute("select alias, node_id from aliases"):
        al[n].add(a)
    doc_node = {t: n for t, n in c.execute("select d.title, n.id from documents d join nodes n on n.document_id = d.id")}
    out_edges = collections.defaultdict(set)
    for s, t in c.execute("select source_id, target_id from edges"):
        out_edges[s].add(t)
    return names, al, doc_node, out_edges


def candidates(row, store):
    names, al, doc_node, out_edges = store
    page = row["page"]
    root = doc_node.get(page) or doc_node.get(page.split("/")[0])
    cand = set()
    if root is not None:
        cand.add(root); cand |= out_edges.get(root, set())
    text = row["passage"]
    for n, nm in names.items():
        for form in {nm} | al.get(n, set()):
            if len(form) >= 3 and re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", text):
                cand.add(n); break
    return sorted(cand, key=lambda n: names[n])


def ends(r):
    out = []
    for e in r["events"]:
        out += [("event", e.get("subject")), ("event", e.get("object"))]
    for f in r["facts"]:
        out.append(("fact_subject", f.get("subject")))
        if f.get("relation") != "other_verb":
            out.append(("fact_object", f.get("object")))
    return [(k, v) for k, v in out if v]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True); ap.add_argument("--db", required=True)
    ap.add_argument("--split", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--hold", type=int, default=150); ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    split, out = Path(a.split), Path(a.out); out.mkdir(parents=True, exist_ok=True)
    train = [json.loads(l) for l in open(split / "train.jsonl") if f'"series": "{a.series}"' in l]
    train = [r for r in train if r["series"] == a.series and r["source"] == "gold_v2"]
    dev = [json.loads(l) for l in open(split / "dev.jsonl")]
    dev = [r for r in dev if r["series"] == a.series]
    rng = random.Random(a.seed)
    pages = sorted({r["page"] for r in train}); rng.shuffle(pages)
    dev_pages = {r["page"] for r in dev}
    hold, got = set(), 0
    for p in pages:
        if got >= a.hold: break
        if p in dev_pages: continue
        hold.add(p); got += sum(r["page"] == p for r in train)
    held = [dict(r, split="holdout") for r in train if r["page"] in hold] + [dict(r, split="dev") for r in dev]
    store = load_store(a.db)
    names, al = store[0], store[1]
    cov = collections.Counter(); tot = collections.Counter(); sizes = []; miss = collections.Counter()
    with open(out / "holdout.jsonl", "w") as f:
        for r in held:
            cand = candidates(r, store)
            sizes.append(len(cand))
            forms = [(names[n], {names[n]} | al.get(n, set())) for n in cand]
            for k, v in ends(r):
                tot[k] += 1
                if any(any(ee.same(v, x) for x in fs) for _, fs in forms):
                    cov[k] += 1
                else:
                    miss[v] += 1
            f.write(json.dumps(dict(r, candidates=[names[n] for n in cand]), ensure_ascii=False) + "\n")
    tr_ids = {r["id"] for r in train if r["page"] not in hold}
    json.dump(sorted(tr_ids), open(out / "train_ids.json", "w"))
    sizes.sort()
    rep = {"series": a.series, "holdout_windows": len(held), "from_train": sum(r["split"] == "holdout" for r in held),
           "from_dev": len(dev), "held_pages": len(hold), "train_windows_left": len(tr_ids),
           "candidates_median": sizes[len(sizes) // 2], "candidates_p90": sizes[int(len(sizes) * .9)],
           "coverage": {k: f"{cov[k]}/{tot[k]} = {cov[k] / tot[k]:.3f}" for k in tot},
           "coverage_all": f"{sum(cov.values())}/{sum(tot.values())} = {sum(cov.values()) / sum(tot.values()):.3f}",
           "top_uncovered": miss.most_common(40)}
    json.dump(rep, open(out / "s1_report.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(rep, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()

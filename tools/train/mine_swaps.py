#!/usr/bin/env python3
"""Step 2a (2026-11-14 analysis): which label pairs the gold and the student swap on the same quote.
For every gold row with no strict partner, the student rows on an overlapping quote with the same subject
give a (gold label -> student label) pair; reported raw and after statement_norm (a pair that the normaliser
already merges is marked '='). Labels: EV:verb, FA:relation, FA:other_verb(lemma), TAG:tag.

    python3 tools/train/mine_swaps.py --gold TRAIN.jsonl --pred PREDS.jsonl [--pred ...] [--top 60]
"""
import argparse, collections, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools" / "train"))
import eval_extraction as ee  # noqa: E402
import score_layers_v2 as sl  # noqa: E402
from statement_norm import lemma, statement  # noqa: E402


def lab(r, L):
    if L == "events": return "EV:" + str(r.get("verb"))
    if L == "tags": return "TAG:" + str(r.get("tag"))
    m = "" if (r.get("modality") or "actual") == "actual" else "/" + r["modality"]
    if r.get("relation") == "other_verb": return f"FA:ov({lemma(r.get('object'))}){m}"
    return f"FA:{r.get('relation')}{m}"


def ov(a, b):
    a, b = (a or "").strip(), (b or "").strip()
    return bool(a) and bool(b) and (a in b or b in a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True); ap.add_argument("--pred", action="append", required=True)
    ap.add_argument("--top", type=int, default=60)
    a = ap.parse_args()
    gold = {}
    for l in open(a.gold):
        r = json.loads(l); gold[r["id"]] = r
    pairs, norm_same, n_win = collections.Counter(), {}, 0
    for pf in a.pred:
        for i, p in sl.load(pf).items():
            g = gold.get(i)
            if not g: continue
            n_win += 1
            G = [(L, r) for L in ("events", "facts", "tags") for r in g[L]]
            P = [(L, r) for L in ("events", "facts", "tags") for r in p[L]]
            for L, r in G:
                same = [(L2, q) for L2, q in P if lab(q, L2) == lab(r, L) and ov(q.get("quote"), r.get("quote"))]
                if same: continue
                near = [(L2, q) for L2, q in P if ov(q.get("quote"), r.get("quote"))
                        and (L2 == "tags" or L == "tags" or ee.same(q.get("subject"), r.get("subject")))]
                if not near:
                    pairs[(lab(r, L), "-")] += 1; continue
                for L2, q in near[:1]:
                    k = (lab(r, L), lab(q, L2)); pairs[k] += 1
                    if L != "tags" and L2 != "tags":
                        norm_same[k] = statement(r, L)[1:4:2] == statement(q, L2)[1:4:2]
    print(f"windows {n_win}; gold rows without a same-label student row on their quote: {sum(pairs.values())}")
    for (gl, pl), c in pairs.most_common(a.top):
        print(f"{c:5d}  {gl:32s} -> {pl:32s} {'=' if norm_same.get((gl, pl)) else ''}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Error breakdown of v2 predictions vs a v2 gold split (step 5 error analysis, 2026-11-14).

For each layer: FN / FP counts by verb / relation / tag, and for every unmatched row what the nearest
other-side row was on the same quote (the confusion: wrong relation, wrong modality, wrong end, moved to
another layer, or nothing at all). Matching rules are score_layers_v2's (fact_match, tag_match) and the event
scorer's name rule (eval_extraction.match), so the counts reconcile with its F1s.

    python tools/train/error_layers_v2.py --gold DEV_POOL.jsonl --pred RUN/dev_preds_e1.jsonl [--subset marvel+mcu]
        [--examples N]
"""
import argparse, collections, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools" / "train"))
import eval_extraction as ee  # noqa: E402
import score_layers_v2 as sl  # noqa: E402


def ev_ok(p, g):
    return ee.match((p.get("subject"), p.get("verb"), p.get("object")), (g.get("subject"), g.get("verb"), g.get("object")))


def overlap(a, b):
    a, b = (a or "").strip(), (b or "").strip()
    return bool(a) and bool(b) and (a in b or b in a)


def why_fact(p, others):
    """Why an unmatched fact p has no partner in others (same-quote rows on the other side)."""
    near = [g for g in others if overlap(p.get("quote"), g.get("quote"))]
    if not near:
        return "no_row_on_quote"
    for g in near:
        if g.get("relation") == p.get("relation"):
            if (g.get("modality") or "actual") != (p.get("modality") or "actual"):
                return "modality"
            return "ends"
    return "relation"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True); ap.add_argument("--pred", required=True)
    ap.add_argument("--subset", default="all"); ap.add_argument("--examples", type=int, default=0)
    a = ap.parse_args()
    gold = {}
    for l in open(a.gold):
        r = json.loads(l)
        if sl.SUBSETS[a.subset](r["series"]):
            gold[r["id"]] = r
    preds = sl.load(a.pred)
    C = collections.Counter
    ev_fn, ev_fp, f_fn, f_fp, t_fn, t_fp = C(), C(), C(), C(), C(), C()
    f_fn_why, f_fp_why, cross, conf = C(), C(), C(), C()
    win = C(); ex = collections.defaultdict(list)
    for i, g in gold.items():
        p = preds.get(i, {"events": [], "facts": [], "tags": []})
        ge, gf, gt = g["events"], g["facts"], g["tags"]
        pe, pf, pt = p["events"], p["facts"], p["tags"]
        if not (pe or pf or pt): win["pred_all_empty"] += 1
        # events
        _, _, _, pairs = sl.greedy(pe, ge, ev_ok)
        mp = {id(x) for x, _ in pairs}; mg = {id(y) for _, y in pairs}
        for x in ge:
            if id(x) not in mg:
                ev_fn[x.get("verb")] += 1
                near = [q for q in pe if overlap(q.get("quote"), x.get("quote"))]
                nf = [q for q in pf if overlap(q.get("quote"), x.get("quote"))]
                nt = [q for q in pt if overlap(q.get("quote"), x.get("quote"))]
                k = ("ev_wrongverb:" + x.get("verb") + "->" + near[0].get("verb")) if near and near[0].get("verb") != x.get("verb") else \
                    ("ev_ends" if near else ("as_fact:" + nf[0].get("relation") if nf else ("as_tag:" + nt[0].get("tag") if nt else "missed")))
                cross["gold_event " + k.split(":")[0] if k.startswith(("as_", "missed", "ev_ends")) else "gold_event ev_wrongverb"] += 1
                conf["E- " + k] += 1
                if a.examples and len(ex["ev_fn"]) < a.examples: ex["ev_fn"].append((g["page"], x, near or nf or nt))
        for x in pe:
            if id(x) not in mp:
                ev_fp[x.get("verb")] += 1
                nf = [q for q in gf if overlap(q.get("quote"), x.get("quote"))]
                nt = [q for q in gt if overlap(q.get("quote"), x.get("quote"))]
                ne = [q for q in ge if overlap(q.get("quote"), x.get("quote"))]
                k = "ev_vs_gold_event" if ne else ("gold_fact:" + nf[0].get("relation") if nf else ("gold_tag:" + nt[0].get("tag") if nt else "invented"))
                conf["E+ " + k] += 1
                if a.examples and len(ex["ev_fp"]) < a.examples: ex["ev_fp"].append((g["page"], x, ne or nf or nt))
        # facts
        _, _, _, pairs = sl.greedy(pf, gf, sl.fact_match)
        mp = {id(x) for x, _ in pairs}; mg = {id(y) for _, y in pairs}
        for x in gf:
            if id(x) not in mg:
                f_fn[x.get("relation")] += 1
                w = why_fact(x, pf)
                if w == "no_row_on_quote":
                    if any(overlap(q.get("quote"), x.get("quote")) for q in pe): w = "pred_event"
                    elif any(overlap(q.get("quote"), x.get("quote")) for q in pt): w = "pred_tag:" + next(q.get("tag") for q in pt if overlap(q.get("quote"), x.get("quote")))
                f_fn_why[w] += 1
                if w == "relation":
                    q = next(q for q in pf if overlap(q.get("quote"), x.get("quote")))
                    conf["F- rel %s->%s" % (x.get("relation"), q.get("relation"))] += 1
                if a.examples and len(ex["f_fn_" + w.split(":")[0]]) < a.examples:
                    ex["f_fn_" + w.split(":")[0]].append((g["page"], x, [q for q in pf + pe + pt if overlap(q.get("quote"), x.get("quote"))]))
        for x in pf:
            if id(x) not in mp:
                f_fp[x.get("relation")] += 1
                w = why_fact(x, gf)
                if w == "no_row_on_quote":
                    if any(overlap(q.get("quote"), x.get("quote")) for q in ge): w = "gold_event"
                    elif any(overlap(q.get("quote"), x.get("quote")) for q in gt): w = "gold_tag:" + next(q.get("tag") for q in gt if overlap(q.get("quote"), x.get("quote")))
                    else: w = "invented(quote uncovered in gold)"
                f_fp_why[w] += 1
                if a.examples and len(ex["f_fp_" + w.split(":")[0]]) < a.examples:
                    ex["f_fp_" + w.split(":")[0]].append((g["page"], x, [q for q in gf + ge + gt if overlap(q.get("quote"), x.get("quote"))]))
        # tags
        _, _, _, pairs = sl.greedy(pt, gt, sl.tag_match)
        mp = {id(x) for x, _ in pairs}; mg = {id(y) for _, y in pairs}
        for x in gt:
            if id(x) not in mg:
                nt = [q for q in pt if overlap(q.get("quote"), x.get("quote"))]
                k = ("wrongtag:%s->%s" % (x.get("tag"), nt[0].get("tag"))) if nt else (
                    "as_row" if any(overlap(q.get("quote"), x.get("quote")) for q in pe + pf) else "uncovered")
                t_fn[x.get("tag")] += 1; conf["T- " + k.split(":")[0] + (":" + x.get("tag") if not nt else ":" + k.split(":")[1])] += 1
        for x in pt:
            if id(x) not in mp:
                t_fp[x.get("tag")] += 1
                if any(overlap(q.get("quote"), x.get("quote")) for q in ge + gf):
                    conf["T+ gold_has_row_on_tagged_sentence:" + x.get("tag")] += 1
    def show(title, c, n=25):
        print(f"\n## {title} (total {sum(c.values())})")
        for k, v in c.most_common(n): print(f"  {v:4d}  {k}")
    print("windows", len(gold), dict(win))
    show("event FN by gold verb", ev_fn); show("event FP by pred verb", ev_fp)
    show("fact FN by gold relation", f_fn); show("fact FN why", f_fn_why)
    show("fact FP by pred relation", f_fp); show("fact FP why", f_fp_why)
    show("tag FN by gold tag", t_fn); show("tag FP by pred tag", t_fp)
    show("confusions", conf, 60)
    if a.examples:
        for k, v in ex.items():
            print(f"\n### examples {k}")
            for page, x, near in v:
                print(f"  [{page}] {json.dumps(x, ensure_ascii=False)[:300]}")
                for q in near[:2]: print(f"      ~ {json.dumps(q, ensure_ascii=False)[:300]}")


if __name__ == "__main__":
    main()

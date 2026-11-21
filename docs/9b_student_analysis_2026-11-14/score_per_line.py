#!/usr/bin/env python3
"""Score predictions on what the repo's definition of 100% asks of each line (COMPREHENSION_REMAINDER §5):
is the line classified, is it an event, and who takes part. The fine label (which of 62 relations) is ignored.

Per sentence of each passage, from the rows whose quote lies in it:
  has_row    the sentence carries a statement (an event or a fact) rather than only a tag
  is_event   the sentence carries an event row
  dimension  the coarse kinds present: event, relationship, interaction, possession, identity, state,
             knowledge, other (other_verb)
  people     the named ends of those rows (subject and object; an other_verb object is a verb, not an end)

    python score_per_line.py --tools <repo>/tools --gold dev_pool.jsonl --pred RUN/dev_preds_e1.jsonl [--subset anime]
"""
import argparse, json, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--tools", required=True); ap.add_argument("--gold", required=True)
ap.add_argument("--pred", action="append", required=True); ap.add_argument("--subset", default="all")
a = ap.parse_args()
sys.path.insert(0, a.tools); sys.path.insert(0, a.tools + "/train")
import eval_extraction as ee, score_layers_v2 as sl  # noqa: E402

GROUP = {r: g for g, rels in sl.GROUPS.items() for r in rels}
keep = {"all": lambda s: True, "anime": lambda s: s not in ("marvel", "mcu"), "marvel+mcu": lambda s: s in ("marvel", "mcu")}[a.subset]
sents = lambda p: [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", p) if len(s.strip()) >= 20]


def view(lab, s):
    on = lambda x: (x.get("quote") or "").strip() and (x["quote"].strip() in s)
    ev = [x for x in lab["events"] if on(x)]
    fa = [x for x in lab["facts"] if on(x)]
    dims = ({"event"} if ev else set()) | {("other" if GROUP.get(x.get("relation")) == "other_verb" else GROUP.get(x.get("relation"), "other")) for x in fa}
    people = [x.get(k) for x in ev for k in ("subject", "object")] + [x.get("subject") for x in fa] + \
             [x.get("object") for x in fa if x.get("relation") != "other_verb"]
    uniq = []
    for n in people:
        if n and not any(ee.same(n, m) for m in uniq):
            uniq.append(n)
    return bool(ev or fa), bool(ev), dims, uniq


def prf(tp, npred, ngold):
    p, r = (tp / npred if npred else 0.0), (tp / ngold if ngold else 0.0)
    return (2 * p * r / (p + r) if p + r else 0.0), p, r


gold = [json.loads(l) for l in open(a.gold)]
for path in a.pred:
    preds = sl.load(path)
    c = dict.fromkeys(("n", "row_tp", "row_p", "row_g", "ev_tp", "ev_p", "ev_g", "dim_tp", "dim_p", "dim_g", "pp_tp", "pp_p", "pp_g", "same_people", "with_people"), 0)
    for g in gold:
        if not keep(g["series"]) or g["id"] not in preds:
            continue
        for s in sents(g["passage"]):
            gr, ge, gd, gp = view(g, s)
            pr, pe, pd, pp = view(preds[g["id"]], s)
            c["n"] += 1
            c["row_tp"] += gr and pr; c["row_p"] += pr; c["row_g"] += gr
            c["ev_tp"] += ge and pe; c["ev_p"] += pe; c["ev_g"] += ge
            c["dim_tp"] += len(gd & pd); c["dim_p"] += len(pd); c["dim_g"] += len(gd)
            hit = sum(1 for n in pp if any(ee.same(n, m) for m in gp))
            c["pp_tp"] += hit; c["pp_p"] += len(pp); c["pp_g"] += len(gp)
            if gp or pp:
                c["with_people"] += 1
                c["same_people"] += (len(pp) == len(gp) == hit)
    name = path.split("/")[-1]
    print(f"{name}  [{a.subset}]  sentences {c['n']}")
    for lab, k in (("carries a statement", "row"), ("is an event", "ev"), ("coarse dimension", "dim"), ("people named", "pp")):
        f, p, r = prf(c[k + "_tp"], c[k + "_p"], c[k + "_g"])
        print(f"   {lab:20s} F1 {f:.3f}  P {p:.3f}  R {r:.3f}")
    print(f"   sentences where the set of people is exactly the gold's: {c['same_people']}/{c['with_people']} = {c['same_people'] / max(c['with_people'], 1):.1%}")

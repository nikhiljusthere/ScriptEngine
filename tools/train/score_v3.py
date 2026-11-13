#!/usr/bin/env python3
"""The step-1 yardstick of docs/9B_STUDENT_ANALYSIS_2026-11-14.md: every run reported two ways plus gates.

  strict     score_layers_v2 as before (events / facts / tags, F1 with bootstrap CI)
  statement  events and facts pooled, both sides mapped through statement_norm.statement, matched one-to-one
             on (class, actual?) with the event scorer's name rule on the ends (an end that is None on either
             side is not compared: `learned` has no object, other_verb "realized" carries the verb). A pred
             row with no partner whose quote sits on a gold crowd_end/no_doer tag is not counted as a false
             row (the audit judged most of those V or W: an unnamed individual written as an end). Tags: a
             gold tag counts as covered when the pred has a tag on an overlapping quote, any tag name.
  gates      sentence coverage (fact_gate.sentences; a sentence is covered when a row or tag quote lies
             inside it or contains it), verbatim quotes (quote is a substring of the passage), legality
             (fact_gate.validate shape/vocabulary problems per fact row; event verbs in the 12), JSON valid.

    python3 tools/train/score_v3.py --gold DEV_V3.jsonl --pred RUN/preds.jsonl [--pred ...] [--by-series]
"""
import argparse, json, random, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools" / "train"))
import eval_extraction as ee  # noqa: E402
import fact_gate  # noqa: E402
import score_layers_v2 as sl  # noqa: E402
from statement_norm import statement  # noqa: E402

VERBS = set(ee.VERBS) if hasattr(ee, "VERBS") else {"fought", "defeated", "killed", "captured", "escaped", "saved",
                                                     "betrayed", "sealed", "met", "arrived", "departed", "awakened"}
SYMC = {"FIGHT", "MEET", "ALLY"}


def ov(a, b):
    a, b = (a or "").strip(), (b or "").strip()
    return bool(a) and bool(b) and (a in b or b in a)


def st_match(p, g):
    (ps, pc, po, pa), (gs, gc, go, ga) = p[0], g[0]
    if pc != gc or pa != ga:
        return False
    if po is None or go is None:
        return ee.same(ps, gs)
    if ee.same(ps, gs) and ee.same(po, go):
        return True
    return pc in SYMC and ee.same(ps, go) and ee.same(po, gs)


def window_units(g, p):
    gst = [(statement(r, L), r.get("quote")) for L in ("events", "facts") for r in g[L]]
    pst = [(statement(r, L), r.get("quote")) for L in ("events", "facts") for r in p[L]]
    # dedupe each side (an event and a fact row stating the same thing count once)
    def dd(xs):
        out = []
        for x in xs:
            if not any(st_match(x, y) for y in out):
                out.append(x)
        return out
    gst, pst = dd(gst), dd(pst)
    tp, _, _, pairs = sl.greedy(pst, gst, st_match)
    matched = {id(a) for a, _ in pairs}
    soft = [t.get("quote") for t in g["tags"] if t.get("tag") in ("crowd_end", "no_doer")]
    fp = sum(1 for x in pst if id(x) not in matched and not any(ov(x[1], q) for q in soft))
    stu = (tp, tp + fp, tp, len(gst))
    tt = sum(1 for t in g["tags"] if any(ov(t.get("quote"), q.get("quote")) for q in p["tags"]))
    tp_t = sum(1 for q in p["tags"] if any(ov(t.get("quote"), q.get("quote")) for t in g["tags"]))
    return stu, (tp_t, len(p["tags"]), tt, len(g["tags"]))


def gates(g, p):
    passage = g["passage"]
    sents = fact_gate.sentences(passage)
    rows = [r for L in ("events", "facts", "tags") for r in p[L]]
    qs = [r.get("quote") or "" for r in rows]
    cov = sum(1 for s in sents if any(q and (q in s or s in q or ov(q, s)) for q in qs))
    verb = sum(1 for q in qs if q and q in passage)
    illegal = sum(1 for r in p["facts"] if fact_gate.validate(r)) + sum(1 for r in p["events"] if r.get("verb") not in VERBS)
    return len(sents), cov, len(qs), verb, illegal, len(p["facts"]) + len(p["events"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True); ap.add_argument("--pred", action="append", required=True)
    ap.add_argument("--by-series", action="store_true"); ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--common", action="store_true", help="score only the windows every --pred file has")
    a = ap.parse_args()
    gold_rows = [json.loads(l) for l in open(a.gold)]
    rng = random.Random(0)
    if a.common:
        ids = set.intersection(*(set(sl.load(pf)) for pf in a.pred))
        gold_rows = [r for r in gold_rows if r["id"] in ids]
    for pf in a.pred:
        preds = sl.load(pf)
        groups = {"all": gold_rows}
        if a.by_series:
            for s in sorted({r["series"] for r in gold_rows}):
                groups[s] = [r for r in gold_rows if r["series"] == s]
        for name, rows in groups.items():
            E = {"events": [], "facts": [], "tags": []}
            per = [window_units(g, preds.get(g["id"], E)) for g in rows]
            gt = [gates(g, preds.get(g["id"], E)) for g in rows]
            def f(us):
                f1, p, r = sl.prf(us)
                bs = sorted(sl.prf([us[rng.randrange(len(us))] for _ in us])[0] for _ in range(a.boot))
                return f"F1 {f1:.3f} [{bs[int(.025 * a.boot)]:.3f}-{bs[int(.975 * a.boot)]:.3f}] P {p:.3f} R {r:.3f}"
            valid = [preds[g["id"]]["valid"] for g in rows if g["id"] in preds and preds[g["id"]]["valid"] is not None]
            S = [sum(x[i] for x in gt) for i in range(6)]
            print(f"{Path(pf).parent.name}/{Path(pf).name} {name:9s} n={len(rows):4d} statements {f([u[0] for u in per])}")
            print(f"{'':40s} {name:9s} tags-any {f([u[1] for u in per])}")
            print(f"{'':40s} {name:9s} gates: coverage {S[1]}/{S[0]}={S[1]/max(S[0],1):.3f}  verbatim {S[3]}/{S[2]}={S[3]/max(S[2],1):.3f}"
                  f"  illegal {S[4]}/{S[5]}  json-valid {sum(valid)}/{len(valid)}  missing-pred {sum(g['id'] not in preds for g in rows)}")


if __name__ == "__main__":
    main()

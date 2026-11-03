#!/usr/bin/env python3
"""Score v2 predictions (events + facts + tags) against a v2 gold split, with bootstrap 95% CIs over windows.

Events go through the existing scorer (tools/eval_extraction.score, the one behind the .602 ship bar), so the
event number stays comparable with every earlier run. Facts and tags are scored here:
- a fact matches a gold fact when the relation and the modality are equal and both ends match under the event
  scorer's name rule (eval_extraction.same: shared word, short form, or the same string); symmetric relations
  match either way round; `other_verb` facts also need the same verb word (case-insensitive prefix, so
  "fought"/"fighting" do not match but "attack"/"attacked" do). Matching is one-to-one, greedy in gold order.
- a tag matches a gold tag with the same tag name whose quote overlaps it (either contains the other).
Precision / recall / F1 per layer, micro over windows; facts are also broken down by relation group, and
on the matched facts the fields the match ignores (certainty, asserted_by, canon) report their agreement.

    python tools/train/score_layers_v2.py --gold series/universal/training/student_v2_short/test.jsonl \
        --pred RUN/test_preds.jsonl [--pred OTHER.jsonl] [--subset marvel+mcu]

--pred: JSONL of {id, raw} (sft_qwen dev_preds_e*.jsonl, eval_base_v2.py output: the full model answer,
parsed here) or {id, events, facts, tags} (missing layers count as empty). The old eval_base.py keeps only
the last 3,000 chars of raw and parses events only: its files score facts/tags as all missed; use
eval_base_v2.py for v2 predictions. A v1 teacher file ({id, events}) still scores its event layer.
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "train"))
import eval_extraction as ee  # noqa: E402
import fact_gate  # noqa: E402

SUBSETS = {"all": lambda s: True, "pool": lambda s: s != "jjk",
           "marvel+mcu": lambda s: s in ("marvel", "mcu"), "jjk": lambda s: s == "jjk"}
SYM = set(fact_gate.SYMMETRIC) & {"friend_of", "rival_of", "married", "dated", "sibling_of", "allied_with"}
GROUPS = {
    "relationship": {"trained", "mentored", "recruited", "allied_with", "joined", "left_group", "member_of",
                     "leader_of", "friend_of", "rival_of", "parent_of", "sibling_of", "married", "dated"},
    "interaction": {"helped", "assisted", "protected", "contacted", "warned", "persuaded", "tricked", "ordered",
                    "hired", "paid", "gave", "took", "attacked", "interrogated", "apologised_to", "greeted"},
    "possession": {"created", "built", "stole", "used", "destroyed", "owns", "handed", "wielded", "wore", "piloted"},
    "identity": {"alias_of", "disguise_as", "revealed_as"},
    "state": {"gained_power", "lost_power", "transformed_into", "resides_at", "located_at", "dies", "born",
              "aged", "wounded", "healed", "kidnapped"},
    "knowledge": {"learned", "revealed", "discovered", "forgot", "remembered", "suspected"},
    "other_verb": {"other_verb"},
}


def parse_raw(raw):
    body = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.S)
    s, e = body.find("{"), body.rfind("}")
    try:
        d = json.loads(body[s:e + 1]) if s >= 0 and e > s else {}
    except ValueError:
        d = {}
    return d if isinstance(d, dict) else {}


def load(path):
    """{id: {events, facts, tags, valid}}.

    The model's own answer wins when the record carries it: sft_qwen.dev_generate and eval_base.py write
    {id, events, raw}, where `events` is the parsed event layer only, so reading the record's keys first
    scored every fact and tag as missed (2026-11-03 stage-8b check). A raw that does not parse (or the old
    eval_base.py's raw, cut to its last 3,000 chars) falls back to the record's own layer keys.
    `valid`: the raw parsed to a JSON object whose three layers are lists (None when there is no raw)."""
    out = {}
    for line in open(path):
        r = json.loads(line)
        d, valid = {}, None
        if isinstance(r.get("raw"), str):
            d = parse_raw(r["raw"])
            valid = bool(d) and all(isinstance(d.get(k), list) for k in ("events", "facts", "tags"))
        if not any(isinstance(d.get(k), list) for k in ("events", "facts", "tags")):
            d = r
        out[r["id"]] = {k: [x for x in (d.get(k) or []) if isinstance(x, dict)] for k in ("events", "facts", "tags")}
        out[r["id"]]["valid"] = valid
    return out


def verb_ok(a, b):
    a, b = (a or "").lower(), (b or "").lower()
    n = min(len(a), len(b), 5)
    return n >= 3 and a[:n] == b[:n]


def fact_match(p, g):
    if p.get("relation") != g.get("relation") or (p.get("modality") or "actual") != (g.get("modality") or "actual"):
        return False
    ps, po, gs, go = p.get("subject"), p.get("object"), g.get("subject"), g.get("object")
    if g.get("relation") == "other_verb":
        return ee.same(ps, gs) and verb_ok(po, go)
    if ee.same(ps, gs) and ee.same(po, go):
        return True
    return g.get("relation") in SYM and ee.same(ps, go) and ee.same(po, gs)


def tag_match(p, g):
    a, b = (p.get("quote") or "").strip(), (g.get("quote") or "").strip()
    return p.get("tag") == g.get("tag") and bool(a) and bool(b) and (a in b or b in a)


def greedy(preds, golds, ok):
    """One-to-one matches -> (tp, n_pred, n_gold, list of matched (pred, gold) pairs)."""
    used, pairs = set(), []
    for p in preds:
        i = next((i for i, g in enumerate(golds) if i not in used and ok(p, g)), None)
        if i is not None:
            used.add(i)
            pairs.append((p, golds[i]))
    return len(pairs), len(preds), len(golds), pairs


def prf(units):
    """units: (tp, n_pred, n_gold) or (tp_for_precision, n_pred, tp_for_recall, n_gold)."""
    units = [u if len(u) == 4 else (u[0], u[1], u[0], u[2]) for u in units]
    tpp, np_, tpr, ng = (sum(u[i] for u in units) for i in range(4))
    p, r = (tpp / np_ if np_ else 0.0), (tpr / ng if ng else 0.0)
    return (2 * p * r / (p + r) if p + r else 0.0), p, r


def ci(units, n_boot, rng):
    if not units:
        return 0.0, 0.0
    b = sorted(prf([units[rng.randrange(len(units))] for _ in units])[0] for _ in range(n_boot))
    return b[int(0.025 * n_boot)], b[int(0.975 * n_boot) - 1]


def score_layers(gold_rows, ee_gold, preds, sub="all"):
    """Per-window units for one subset -> {layer: units, by_group, attrs, summary, valid, n}, or None when
    the preds cover no gold window of the subset. A gold window missing from `preds` is skipped (as
    score_subsets does), so score only complete prediction files."""
    gold = {r["id"]: r for r in gold_rows}
    ids = [i for i, r in gold.items() if SUBSETS[sub](r.get("series")) and i in preds]
    if not ids:
        return None
    # events: the existing scorer on the same windows
    ev_gold = {k: v for k, v in ee_gold.items() if k in set(ids)}
    summary, units = ee.score(ev_gold, {i: {"events": preds[i]["events"]} for i in ev_gold})
    # score_subsets' rule: precision on pred - fp, recall on hit (an optional gold match is no FP)
    eu = [(u["pred"] - u["fp"], u["pred"], u["hit"], u["core"]) for u in units.values()]
    fu, tu, by = [], [], {g: [] for g in GROUPS}
    attrs = {"certainty": [0, 0], "asserted_by": [0, 0], "canon": [0, 0]}
    for i in ids:
        pf, gf = preds[i]["facts"], gold[i]["facts"]
        tp, n_p, n_g, pairs = greedy(pf, gf, fact_match)
        fu.append((tp, n_p, n_g))
        # on matched facts only: the fields the match ignores (modality is part of the match)
        for p, g in pairs:
            for k, same in (("certainty", (p.get("certainty") or "stated") == (g.get("certainty") or "stated")),
                            ("asserted_by", ee.same(p.get("asserted_by") or None, g.get("asserted_by") or None)),
                            ("canon", (p.get("canon") or None) == (g.get("canon") or None))):
                attrs[k][0] += bool(same)
                attrs[k][1] += 1
        for g, rels in GROUPS.items():
            pg = [f for f in pf if f.get("relation") in rels]
            gg = [f for f in gf if f.get("relation") in rels]
            if pg or gg:
                by[g].append(greedy(pg, gg, fact_match)[:3])
        tu.append(greedy(preds[i]["tags"], gold[i]["tags"], tag_match)[:3])
    vals = [preds[i].get("valid") for i in ids if preds[i].get("valid") is not None]
    return {"events": eu, "facts": fu, "tags": tu, "by_group": by, "attrs": attrs, "summary": summary,
            "valid": (sum(vals) / len(vals)) if vals else None, "n": len(ids)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--pred", action="append", required=True)
    ap.add_argument("--subset", action="append", default=None)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    gold_rows = [json.loads(l) for l in open(a.gold)]
    ee_gold = ee.load_gold(Path(a.gold))
    rng = random.Random(7)
    for path in a.pred:
        preds = load(path)
        name = Path(path).parent.name + "/" + Path(path).name
        for sub in a.subset or list(SUBSETS):
            s = score_layers(gold_rows, ee_gold, preds, sub)
            if s is None:
                continue
            for layer in ("events", "facts", "tags"):
                us = s[layer]
                f, p, r = prf(us)
                lo, hi = ci(us, a.boot, rng)
                print(f"{name:40s} {sub:11s} {layer:7s} n={len(us):4d}  F1 {f:.3f} [{lo:.3f}-{hi:.3f}]  P {p:.3f}  R {r:.3f}")
            valid = "n/a" if s["valid"] is None else f"{s['valid']:.3f}"
            print(f"{'':40s} {sub:11s} events  (eval_extraction scorer f1 {s['summary']['f1']}); "
                  f"v2 JSON valid {valid}")
            agree = "  ".join(f"{k} {v[0] / v[1]:.3f}" for k, v in s["attrs"].items() if v[1])
            if agree:
                print(f"{'':40s} {sub:11s}   facts matched={s['attrs']['certainty'][1]}: agreement {agree}")
            for g, us in s["by_group"].items():
                if us:
                    f, p, r = prf(us)
                    print(f"{'':40s} {sub:11s}   facts/{g:13s} F1 {f:.3f}  P {p:.3f}  R {r:.3f}  (gold {sum(u[2] for u in us)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

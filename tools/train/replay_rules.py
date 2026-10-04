#!/usr/bin/env python3
"""Offline replay of no-model post-rules on a saved drafter run (FLAWLESS
plan: precision levers tuned WITHOUT the GPU). For each candidate rule:
how many predicted rows it removes/rewrites, how many of those were TRUE
(matched a gold core event) — a rule is acceptable only at 0 true losses —
and the resulting scores.

    python tools/train/replay_rules.py --gold G --pred P [--stage pre_verify|final]
"""
import argparse, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools/train"))
import eval_extraction as E  # noqa: E402

# a modal that is not negated ("couldn't exorcise" still reports a fight)
MODAL = re.compile(r"\b(can|could|would|will)\b(?!n't| not)", re.I)
# any past-tense report beside the modal means something WAS done
PAST = re.compile(r"\b(\w{3,}ed|was|were|took|beat|fought|struck|met|got|had|went|came|ran|threw|hit|caught|fell|began|stood|fighting|battling)\b", re.I)
ABLE = re.compile(r"\b(was|were) (effortlessly |finally )?able to\b", re.I)
DEFEAT = re.compile(r"(defeat|beat|best|incapacitat|knock(ed|s)? (him |her |them )?out|(takes?|took|taking) .{0,40}?\bout\b|"
                    r"eliminat|finish(es|ed)? the fight|lost to|outclass|dispatch|came out on top|subdu|retreat)", re.I)


def r_modal(row, quote, window):
    """Capability/hypothetical modal in the quote -> not an event (keep 'was able to')."""
    if MODAL.search(quote) and not ABLE.search(quote) and not PAST.search(quote):
        return "drop"
    return None


def r_defeat_word(row, quote, window):
    if row.get("verb") == "defeated" and not DEFEAT.search(quote):
        return "to_fought"
    return None


def r_place_in_quote(row, quote, window):
    if row.get("verb") in ("arrived", "departed"):
        o = (row.get("object") or "").lower()
        words = [w for w in re.findall(r"[a-z0-9]+", o) if len(w) > 2 and w not in ("the",)]
        if words and not any(w in quote.lower() for w in words):
            return "drop"
    return None


RULES = {"modal": r_modal, "defeat_word": r_defeat_word, "place_in_quote": r_place_in_quote}


def apply(rows, window, rules):
    out = []
    for r in rows:
        q = r.get("quote") or ""
        act = None
        for name in rules:
            act = RULES[name](r, q, window) or act
            if act == "drop":
                break
        if act == "drop":
            continue
        if act == "to_fought":
            r = {**r, "verb": "fought"}
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True); ap.add_argument("--pred", required=True)
    ap.add_argument("--stage", default="pre_verify")
    a = ap.parse_args()
    E.QUOTE_MATCH = "window"
    G = {json.loads(l)["id"]: json.loads(l) for l in open(a.gold)}
    P = {json.loads(l)["id"]: json.loads(l) for l in open(a.pred)}
    import draft_v2 as D, verify_row_wiki as V
    wiki = V.Wiki(str(ROOT / "series/jjk/facts.db"))

    def run(rules):
        preds = {}
        for wid, p in P.items():
            g = G.get(wid)
            window = g["passage"] if g else ""
            rows = p.get("stages", {}).get(a.stage) if a.stage != "final" else p.get("events")
            rows = rows if rows is not None else p.get("events", [])
            kept, _ = D.check_rows(rows, window, wiki, V.BAD_END) if g else (rows, [])
            preds[wid] = {"events": apply(kept, window, rules)}
        s, _ = E.score(E.load_gold(Path(a.gold)), preds)
        return s, preds

    base, bp = run([])
    print(f"base  R={base['core_recall']:.3f} P={base['precision']:.3f} F1={base['f1']:.3f} fp={base['fp']}")
    for name in list(RULES) + ["ALL"]:
        rules = list(RULES) if name == "ALL" else [name]
        s, sp = run(rules)
        print(f"{name:14} R={s['core_recall']:.3f} P={s['precision']:.3f} F1={s['f1']:.3f} fp={s['fp']}  dR={s['core_recall']-base['core_recall']:+.3f}")


if __name__ == "__main__":
    main()

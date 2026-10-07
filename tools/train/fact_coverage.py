#!/usr/bin/env python3
"""Sentence-coverage reporting for the v2 fact layer (plan/EXTRACTION_PROCEDURE_V2.md SECTION C).

The flagger's MISS? cue (big_flags.py:197) is "this sentence has an event cue word and no row quote
touches it". v2 turns that into a coverage REPORT: every narrative sentence is either covered by an
event row, covered by a fact row, or excused by an allowed tag row -- and the sentences that are
none of those are printed as the worklist. Coverage becomes measurable instead of a judgement call,
which is what the owner asked for.

Why this file exists and not a flag inside big_flags.py: `tools/train/big_flags.py` is CLAUDE-OWNED
(owner 2026-10-07, plan/WINDOW_METHOD.md) and its `check()` only ever receives `events`. A facts
coverage gate therefore has to be a new module. Every change we think big_flags.py should get is
written to plan/FACT_LAYER_PROPOSALS_FOR_CLAUDE.md.

Two things this deliberately does NOT do, both of which the council caught:
  * it does NOT reuse big_flags.sentences(), which drops every span under 20 chars (big_flags.py:88)
    and is therefore blind to exactly the short declaratives ("He is her student") that carry the
    facts the owner is complaining about;
  * it does NOT accept a quote that merely CONTAINS a sentence (`sent in q`). big_flags.py:197 has no
    quote-length cap, so one paragraph quote "covers" forty sentences. A sentence counts as covered
    here only if some row quote lies INSIDE that sentence's span.

    python fact_coverage.py IDS.jsonl FILE.jsonl [--limit N] [--chars 1600]
    python fact_coverage.py IDS.jsonl FILE.jsonl --events-only
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[2]
ROOT = Path(os.environ.get("SCRIPTENGINE_ROOT", CODE))
sys.path.insert(0, str(CODE / "tools" / "train"))
sys.path.insert(0, str(ROOT / "tools" / "train"))
import big_flags as bf  # noqa: E402  (read-only: we call sentences() for the comparison only)
import fact_gate as fg  # noqa: E402

br = bf.br
TAGS = fg.TAGS


def segments(text):
    """Narrative sentences, as (index, text) spans. No length floor (see module docstring)."""
    out = []
    for i, s in enumerate(fg.sentences(text), 1):
        t = s.strip()
        if not t:
            continue
        out.append((i, t))
    return out


# wiki markup and link-list furniture. A window may be a whole template dump or a cast list, and
# those lines are NOT narrative sentences -- counting them as misses would make the coverage number
# meaningless (the three worst windows in the v1 baseline were exactly this).
WIKI_MARKUP = re.compile(r"\{\{|\}\}|\{\{[rm]\||\[\[|\]\]|\[\[Category|^\s*\||\|\s*[A-Za-z ]+\s*=")
# A narrative sentence carries a FUNCTION WORD or a VERB FORM. A link list ("Frank Dean",
# "Brooks Watten (Earth-616)", "Sacrifice Victims") has neither: it is a run of proper nouns and
# punctuation. Both tests are needed -- "Scott fought Kang" has a verb but no function word, and
# "Magnistrate's Wife" has neither, so a verb test alone fails in the other direction.
LOWER_FUNCTION = re.compile(
    r"\b(?:the|a|an|and|or|but|of|in|on|at|to|for|from|with|without|into|onto|over|under|after|"
    r"before|while|when|where|which|who|whom|whose|that|this|these|those|there|then|than|as|by|"
    r"is|are|was|were|be|been|being|has|have|had|having|does|did|do|will|would|can|could|shall|"
    r"should|may|might|must|not|no|his|her|their|its|he|she|they|them|him|it|itself|himself|"
    r"herself|themselves|if|so|because|although|though|since|until|unless|about|against|"
    r"during|within|upon|among|between|also|only|just|even|out|up|down|off|away|back|"
    r"toward|towards|instead|however|meanwhile|afterwards|later|once|again|still|yet)\b",
    re.I)
VERB_FORM = re.compile(
    r"\b\w+(?:ed|ing|es)\b"
    r"|\b(?:is|are|was|were|has|have|had|does|did|do|said|told|went|came|got|made|took|gave|left|"
    r"fell|felt|kept|held|brought|caught|taught|thought|fought|killed|met|fled|saved|sealed|"
    r"escaped|captured|betrayed|awakened|arrived|departed|became|born|grew|died)\b", re.I)


def is_furniture(t):
    """Is this segment list/table/template/dialogue furniture rather than a narrative sentence?

    Mirrors the exemptions big_flags.py already makes for MISS? (lines 192-194) and adds wiki
    markup, link lists and headings, because v2 must count those as tag-only rather than as misses.
    """
    s = (t or "").strip()
    if len(s) < 6:
        return True  # below_floor
    if s.lstrip()[:1] in '"“‘':
        return True  # dialogue
    if s.lstrip().startswith(("|", "*", "#", "-", "•", "†", "=", "[", "{")):
        return True  # list/table/heading/template
    if WIKI_MARKUP.search(s):
        return True  # wiki template or link markup
    if len(s) < 90 and (" - " in s or " | " in s or "\t" in s):
        return True  # short list entry
    # A link list is a run of proper nouns with no finite verb and no function word. This is what
    # separates "Frank Dean" (a list entry) from "Frank Dean was her student" (a fact).
    if not (LOWER_FUNCTION.search(s) or VERB_FORM.search(s)):
        return True
    return False


def covered(sent, quotes):
    """A sentence is covered when a row quote lies INSIDE it (never the reverse)."""
    ns = fg.norm(sent)
    for q in quotes:
        if not q:
            continue
        if q in sent:
            return True
        # a quote that is only the whole sentence, modulo trailing punctuation, still counts
        if fg.norm(q).rstrip(" .") == ns.rstrip(" ."):
            return True
    return False


def report(text, events=(), facts=(), tags=(), skip_furniture=True):
    """Coverage of one window.

    Returns dict(uncovered=[sentence texts], tagged=[...], narrative=N, covered=N, rate=float).
    """
    quotes = [e.get("quote") or "" for e in events] + [f.get("quote") or "" for f in facts]
    tag_quotes = [t.get("quote") or "" for t in tags]
    sents = segments(text)
    narrative = [t for _, t in sents if not (skip_furniture and is_furniture(t))]
    unc, tg = [], []
    for t in narrative:
        if covered(t, quotes):
            continue
        if any(q and (q in t or t in q) for q in tag_quotes):
            tg.append(t)
            continue
        unc.append(t)
    n = len(narrative)
    return {"narrative": n, "covered": n - len(unc), "uncovered": unc, "tagged": tg,
            "rate": (n - len(unc)) / n if n else 1.0}


def load_passages():
    return br.passages()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", help="JSONL with an id field, or a bare ids file")
    ap.add_argument("files", nargs="+", help="v2 label file(s), or the v1 labels.jsonl")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--chars", type=int, default=1600)
    ap.add_argument("--events-only", action="store_true",
                    help="ignore facts/tags: measures the v1 EVENT layer's coverage (the baseline)")
    ap.add_argument("--old-segmenter", action="store_true",
                    help="also report big_flags.sentences() so the denominator difference is visible")
    a = ap.parse_args()

    ids = []
    for line in open(a.ids):
        line = line.strip()
        if not line:
            continue
        try:
            ids.append(json.loads(line)["id"])
        except (ValueError, KeyError):
            ids.append(line)
    if a.limit:
        ids = ids[:a.limit]
    pas = load_passages()

    for path in a.files:
        pred = {}
        for line in open(path):
            r = json.loads(line)
            pred[r["id"]] = r
        N = C = U = T = MISS = 0
        rates = []
        worst = []
        old_n = old_c = 0
        for i in ids:
            r = pred.get(i)
            if r is None:
                continue
            text = pas.get(i, "")[:a.chars]
            if not text:
                continue
            ev = r.get("events") or []
            fa = [] if a.events_only else (r.get("facts") or [])
            tg = [] if a.events_only else (r.get("tags") or [])
            rep = report(text, ev, fa, tg)
            N += rep["narrative"]
            C += rep["covered"]
            U += len(rep["uncovered"])
            T += len(rep["tagged"])
            MISS += len(ev) + len(fa)
            rates.append(rep["rate"])
            if rep["uncovered"]:
                worst.append((len(rep["uncovered"]), i, rep["uncovered"]))
            if a.old_segmenter:
                # what the retired flagger's segmenter would have counted, for the delta
                for s in bf.sentences(text):
                    if is_furniture(s):
                        continue
                    old_n += 1
                    if covered(s, [e.get("quote") or "" for e in ev]):
                        old_c += 1
        name = Path(path).name
        rate = C / N if N else 1.0
        urate = U / N if N else 0.0
        print(f"{name}: windows={len(rates)} narrative_sentences={N} covered={C} "
              f"({rate * 100:.1f}%) uncovered={U} ({urate * 100:.1f}%) tagged={T} rows={MISS} "
              f"rows_per_window={MISS / len(rates) if rates else 0:.2f}")
        if a.old_segmenter:
            print(f"  (retired big_flags.sentences() denominator: {old_n} sentences, "
                  f"{old_c} covered = {old_c / old_n * 100 if old_n else 0:.1f}%)")
        if worst:
            worst.sort(reverse=True)
            print(f"  worst windows by uncovered sentences:")
            for k, i, sents_ in worst[:5]:
                print(f"    {i}: {k} uncovered -> {sents_[0][:150]!r}")


if __name__ == "__main__":
    main()

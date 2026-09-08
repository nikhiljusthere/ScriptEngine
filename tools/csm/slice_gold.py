#!/usr/bin/env python3
"""Slice the CSM gold spans verbatim out of the store (plan §5.5.1, 5.5a).

CSM-5 remainder of the CSM 100% campaign. The author is the grader trap
(plan §5.5): the executing agent writes the question, picks the gold span and
reports its own pass rate, which carries no information. §5.5.1's strongest
fix is **generator-sliced gold** — where the gold span is sliced directly out
of `sections.text` / the wiki's declared rosters, verbatim-substring becomes a
structural guarantee instead of a policed rule: rewording to pass becomes
impossible rather than forbidden.

This tool does the slicing for the CSM question sets. It is series-
parameterized (`--series`, CSM-centric by the standing rule — it never touches
JJK baselines) and **never fabricates a span**: every `verbatim_in_store`
value is a confirmed substring of `sections.text` (or a declared-roster
member), or null when no verbatim slice exists. A question with no verbatim
slice is marked `gold_mode: prose` and left to the retrieval test.

Sources sliced (whichever exist on disk):
  questions/<s>.json                         the seed bank (39 questions)
  reports/<s>/d4_open50_<s>.json             the D4 open-50 held-out set
  reports/<s>/census_roster_100_<s>.json     the frozen door census (roster)
  reports/<s>/census_narrative_100_<s>.json  the frozen door census (narrative)
  reports/<s>/t0_pilot_<s>.json              the T0 pilot set (CSM-6)

Output: reports/<s>/gold_sliced_<s>.json — a per-question map of
{id: {set, question, gold_mode, gold_terms, revid}}.

Run:  scriptengine/.venv/bin/python tools/csm/slice_gold.py --series csm
"""
import argparse
import json
import re
import sqlite3
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent

# Candidate set files, in processing order. Only the ones that exist are read;
# the census / T0 sets are produced by the CSM-6 instrument unit and are picked
# up automatically when they land.
SET_FILES = [
    ("seed", "questions/{s}.json"),
    ("d4-open50", "reports/{s}/d4_open50_{s}.json"),
    ("census-roster", "reports/{s}/census_roster_100_{s}.json"),
    ("census-narrative", "reports/{s}/census_narrative_100_{s}.json"),
    ("t0-pilot", "reports/{s}/t0_pilot_{s}.json"),
]


def load_rosters(series):
    """The wiki's declared rosters: [{name, match:[substrs], members:[...]}]."""
    path = REPO / "series" / series / "overrides.yaml"
    if not path.exists():
        return []
    return (yaml.safe_load(path.read_text()) or {}).get("rosters") or []


def roster_match(rosters, question):
    """The declared roster whose `match` substrings hit the question, choosing
    the one with the most members when several match (the most specific set)."""
    low = (question or "").lower()
    best, best_n = None, -1
    for r in rosters:
        if any((m or "").lower() in low for m in r.get("match") or []):
            n = len(r.get("members") or [])
            if n > best_n:
                best, best_n = r, n
    return best


def store(series):
    db = REPO / "series" / series / "facts.db"
    if not db.exists():
        return None
    return sqlite3.connect(db)


class Store:
    """The series' documents + sections, for verbatim slice lookups."""

    def __init__(self, series):
        self.conn = store(series)
        if self.conn is None:
            raise SystemExit(f"facts.db missing for {series!r}")
        self.docs = {r[0]: r[1] for r in
                     self.conn.execute("SELECT title, revid FROM documents")}
        self._text = {}  # title -> (blob, [(breadcrumb, text), ...])

    def resolve(self, subject):
        """Exact-title document for a subject, else None."""
        return subject if subject in self.docs else None

    def sections(self, title):
        if title in self._text:
            return self._text[title]
        rows = self.conn.execute(
            "SELECT breadcrumb, text FROM sections WHERE document_id="
            "(SELECT id FROM documents WHERE title=?)", (title,)).fetchall()
        self._text[title] = rows
        return rows

    def revid(self, title):
        return self.docs.get(title)

    def close(self):
        self.conn.close()


def find_verbatim(sections, term):
    """The original-casing span of `term` in the section blob, or None."""
    if not term:
        return None
    low_term = term.lower()
    for breadcrumb, text in sections:
        if not text:
            continue
        start = text.lower().find(low_term)
        if start != -1:
            return {"verbatim_in_store": text[start:start + len(term)],
                    "source_section": (breadcrumb or "").split(" / ")[-1].strip()}
    return None


def slice_seed_bank(questions, rosters, st, series):
    """The seed bank: every question carries its `answer` items + a subject,
    so the gold is sliced from the declared roster (set) or the subject's
    sections (fact)."""
    out = {}
    for q in questions:
        qid = q.get("id")
        qtext = q.get("question") or ""
        kind = q.get("kind")
        terms = [a.get("item") for a in (q.get("answer") or []) if a.get("item")]
        record = {"set": "seed", "question": qtext, "revid": q.get("source_revid"),
                  "gold_terms": []}
        if kind == "set":
            roster = roster_match(rosters, qtext)
            if roster and (roster.get("members") or []):
                record["gold_mode"] = "declared-roster"
                record["source_doc"] = f"series/{series}/overrides.yaml"
                record["source_section"] = f"rosters:{roster.get('name')}"
                record["gold_terms"] = [
                    {"term": m, "verbatim_in_store": m,
                     "source_doc": record["source_doc"],
                     "source_section": record["source_section"]}
                    for m in roster["members"]]
            else:
                record["gold_mode"] = slice_terms(terms, q.get("subject"), st, record)
        else:  # fact / prose
            record["gold_mode"] = slice_terms(terms, q.get("subject"), st, record)
        out[qid] = record
    return out


def slice_terms(terms, subject, st, record):
    """Slice each answer term verbatim out of the subject's sections."""
    if not st or not subject:
        if not terms:
            record["gold_terms"] = []
            return "prose"
        record["gold_terms"] = [
            {"term": t, "verbatim_in_store": None, "source_doc": None,
             "source_section": None} for t in terms]
        return "prose"
    title = st.resolve(subject)
    if title is None:
        record["gold_terms"] = [
            {"term": t, "verbatim_in_store": None, "source_doc": None,
             "source_section": None} for t in terms]
        return "prose"
    sections = st.sections(title)
    found = 0
    for t in terms:
        hit = find_verbatim(sections, t)
        if hit:
            found += 1
            record["gold_terms"].append(
                {"term": t, "verbatim_in_store": hit["verbatim_in_store"],
                 "source_doc": title, "source_section": hit["source_section"]})
        else:
            record["gold_terms"].append(
                {"term": t, "verbatim_in_store": None, "source_doc": title,
                 "source_section": None})
    if terms and found == len(terms):
        return "sliced"
    if found:
        return "partial"
    return "prose"


def slice_generic(questions, rosters, st, series, meta, set_name):
    """Non-seed sets (d4 open-50, census, T0 pilot). A question that carries an
    `answer` is sliced like the seed bank (declared roster for a set ask, the
    subject's sections otherwise); an open-ended question with no structured
    answer has no verbatim gold to slice — mark prose, never fabricate."""
    out = {}
    revid = (meta or {}).get("revid_fetched")
    for q in questions:
        qid = q.get("id") or q.get("q") or q.get("question")
        qtext = q.get("q") or q.get("question") or ""
        terms = [a.get("item") for a in (q.get("answer") or []) if a.get("item")]
        record = {"set": set_name, "question": qtext, "revid": q.get("source_revid", revid),
                  "gold_terms": []}
        if terms:
            if (q.get("kind") == "set" or q.get("expect_mode") == "roster"):
                roster = roster_match(rosters, qtext)
                if roster and (roster.get("members") or []):
                    record["gold_mode"] = "declared-roster"
                    record["source_doc"] = f"series/{series}/overrides.yaml"
                    record["source_section"] = f"rosters:{roster.get('name')}"
                    record["gold_terms"] = [
                        {"term": m, "verbatim_in_store": m,
                         "source_doc": record["source_doc"],
                         "source_section": record["source_section"]}
                        for m in roster["members"]]
                    out[qid] = record
                    continue
            record["gold_mode"] = slice_terms(terms, q.get("subject"), st, record)
        else:
            record["gold_mode"] = "prose"
            record["note"] = "open-ended / no structured answer — left to the retrieval test"
        out[qid] = record
    return out


def questions_of(data):
    """The question list of a set file, whatever its container."""
    if isinstance(data, list):
        return data, {}
    for key in ("questions", "items"):
        if isinstance(data.get(key), list):
            return data[key], data.get("meta") or {}
    return [], data.get("meta") or {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="csm")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    series = args.series
    out_path = (Path(args.out) if args.out
                else REPO / "reports" / series / f"gold_sliced_{series}.json")

    rosters = load_rosters(series)
    st = Store(series)
    result = {"meta": {
        "series": series,
        "generated": str(date.today()),
        "rule": "generator-sliced gold (plan §5.5.1): every verbatim_in_store is a "
                "confirmed substring of sections.text or a declared-roster member; "
                "null = no verbatim slice (prose mode, never fabricated)",
        "source_files": [],
        "roster_count": len(rosters),
    }, "questions": {}}
    counts = {}
    for set_name, tpl in SET_FILES:
        path = REPO / tpl.format(s=series)
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        questions, meta = questions_of(data)
        if not questions:
            continue
        result["meta"]["source_files"].append(path.relative_to(REPO).as_posix())
        if set_name == "seed":
            result["questions"].update(slice_seed_bank(questions, rosters, st, series))
        else:
            result["questions"].update(
                slice_generic(questions, rosters, st, series, meta, set_name))
        counts[set_name] = len(questions)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    st.close()

    modes = {}
    for rec in result["questions"].values():
        modes[rec["gold_mode"]] = modes.get(rec["gold_mode"], 0) + 1
    print(f"{len(result['questions'])} questions sliced across {len(counts)} set(s): "
          + ", ".join(f"{k}={v}" for k, v in counts.items()))
    print("gold_mode breakdown:", ", ".join(f"{k}={v}" for k, v in sorted(modes.items())))
    print(f"wrote {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
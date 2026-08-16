"""Does the relations table hold the relationships the wiki documents?

`canon-run` cannot answer this. Its bank has no relation-shaped set question on
any of the eight wikis -- twelve questions mention a relationship word and every
one of them is a fact or a roster of people -- and the relations table is not a
member source anyway: `build_roster` never reads it, and the only consumer is
`chronology.scaffold`, which is the arc scaffold rather than the enumeration
path. So the whole `relations` pass, 22,700 rows across eight wikis, sits
outside the number the project quotes, and a change to it moves nothing that is
measured.

That is what this module is for, and it is why the question "should plot
narration be declared as a relation section?" could not previously be settled
by measurement. It scores the coverage bank at `questions/_<series>_relations.json`
against the store: recall only, deliberately.

**Recall only.** The gold is every person this wiki heads a subsection for
inside a character's `Relationships` section -- structure, not prose, so no
judgement enters the transcription. The store legitimately holds more than
that: reading the story is the entire point of declaring `Plot` and `Synopsis`,
and a partner the wiki never gave a heading is not thereby wrong. Scoring
precision against this list would mark the intended gain as a defect. What the
extras are worth is a separate question, and this module reports them by
source section so it can be asked, rather than answering it with a number that
would not mean anything.

Needs neither the API server nor a model: pure SQLite, so it runs while the
27B is resident and an extraction is in flight.

    python -m scriptengine.eval.relation_coverage --series csm
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from scriptengine.config import get_settings, series_paths
from scriptengine.eval.canon_gold import norm
from scriptengine.stores.facts import FactStore

# The closed vocabulary the extraction prompt allows. Checked here because a
# value outside it is the signal to re-extract, and this is the one place that
# reads every stored relation for a series anyway.
VOCABULARY = (
    "ally", "enemy", "family", "friend", "romantic", "rival",
    "mentor", "student", "superior", "subordinate", "creator", "creation",
)

# Sections whose prose describes a relationship rather than narrating one. The
# split this module reports is between these and everything else, because that
# is the distinction the declaration question turns on.
DESCRIPTIVE = ("relationships",)


def bank_path(series: str, settings=None) -> Path:
    root = (settings or get_settings()).questions_root
    return root / f"_{series}_relations.json"


def load_bank(series: str, settings=None) -> list[dict]:
    path = bank_path(series, settings)
    if not path.exists():
        raise SystemExit(f"no relation coverage bank at {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    declared = raw.get("series")
    if declared != series:
        raise SystemExit(f"{path.name} declares series {declared!r}, not {series!r}")
    return list(raw.get("questions") or ())


def _descriptive(section: str) -> bool:
    return (section or "").split("/")[0].strip().lower() in DESCRIPTIVE


def score(series: str, settings=None) -> dict:
    paths = series_paths(series)
    questions = load_bank(series, settings)
    report: dict = {"series": series, "rows": [], "integrity": {}}

    with FactStore(paths.facts_db) as store:
        for question in questions:
            subject = question["subject"]
            gold = [item["item"] for item in question["answer"]]
            wanted = {norm(name) for name in gold}

            held: dict[str, list] = collections.defaultdict(list)
            for row in store.relations_of(subject):
                # Direction is not the claim. The wiki writes a relationship on
                # whichever page it feels like, and the gold is "these two have
                # a documented relationship", so the partner is whichever end
                # is not the subject.
                partner = (
                    row["other"] if norm(row["character"]) == norm(subject)
                    else row["character"]
                )
                held[norm(partner)].append(row)

            found = sorted(name for name in gold if norm(name) in held)
            missing = sorted(name for name in gold if norm(name) not in held)
            extra = sorted(
                {
                    (r["other"] if norm(r["character"]) == norm(subject)
                     else r["character"])
                    for key, rows in held.items() if key not in wanted
                    for r in rows
                }
            )
            narrated = sorted(
                {
                    name for name in extra
                    if all(
                        not _descriptive(r["section"])
                        for r in held[norm(name)]
                    )
                }
            )
            report["rows"].append({
                "id": question["id"],
                "subject": subject,
                "gold": len(gold),
                "found": len(found),
                "recall": round(len(found) / len(gold), 3) if gold else 0.0,
                "missing": missing,
                "extra": extra,
                "extra_from_narration_only": narrated,
            })

        # Integrity, over the whole series rather than the bank's subjects.
        vocabulary = collections.Counter()
        empty_quotes = 0
        by_source = collections.Counter()
        rows = store.connection.execute(
            "SELECT relation, quote, section FROM relations"
        ).fetchall()
        for row in rows:
            vocabulary[row["relation"]] += 1
            if len((row["quote"] or "").strip()) < 12:
                empty_quotes += 1
            by_source["described" if _descriptive(row["section"]) else "narrated"] += 1
        report["integrity"] = {
            "rows": len(rows),
            "characters": store.connection.execute(
                "SELECT COUNT(DISTINCT character) FROM relations"
            ).fetchone()[0],
            "outside_vocabulary": sorted(
                r for r in vocabulary if r not in VOCABULARY
            ),
            "quotes_too_short": empty_quotes,
            "by_source": dict(by_source),
        }

    gold_total = sum(r["gold"] for r in report["rows"])
    found_total = sum(r["found"] for r in report["rows"])
    report["summary"] = {
        "questions": len(report["rows"]),
        "gold": gold_total,
        "found": found_total,
        "recall": round(found_total / gold_total, 4) if gold_total else 0.0,
        "extra_partners": sum(len(r["extra"]) for r in report["rows"]),
        "extra_from_narration_only": sum(
            len(r["extra_from_narration_only"]) for r in report["rows"]
        ),
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series", default="csm")
    parser.add_argument("--json", action="store_true", help="the report, as JSON")
    args = parser.parse_args()

    report = score(args.series)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 0

    print(f"relation coverage: {args.series}\n")
    print(f"{'subject':22}{'gold':>5}{'found':>6}{'recall':>8}   {'extra':>5}  missing")
    for row in report["rows"]:
        missing = ", ".join(row["missing"]) or "-"
        print(
            f"{row['subject']:22}{row['gold']:5}{row['found']:6}"
            f"{row['recall']:8.1%}   {len(row['extra']):5}  {missing}"
        )

    summary, integrity = report["summary"], report["integrity"]
    print(
        f"\n{summary['found']}/{summary['gold']} documented partners held "
        f"({summary['recall']:.1%}) over {summary['questions']} subjects"
    )
    print(
        f"partners beyond the gold: {summary['extra_partners']}, of which "
        f"{summary['extra_from_narration_only']} are held only by narration"
    )
    print(
        f"\nstore: {integrity['rows']} rows over {integrity['characters']} "
        f"characters, {integrity['by_source']}"
    )
    outside = integrity["outside_vocabulary"]
    print(
        f"integrity: outside the closed vocabulary {outside or 'none'}, "
        f"quotes under 12 chars {integrity['quotes_too_short']}"
    )
    return 1 if outside or integrity["quotes_too_short"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

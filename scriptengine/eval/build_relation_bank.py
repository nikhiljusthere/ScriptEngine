"""Transcribe a relations coverage bank from the wiki's own section headings.

Kept in the repo rather than run once from a scratch directory, because the
gold it writes is only trustworthy if how it was derived is readable. Every
entry comes from structure -- a subheading inside a character's `Relationships`
section -- so no judgement enters the transcription and re-running it after a
re-crawl produces the same bank.

    python -m scriptengine.eval.build_relation_bank --series csm

**This only works on a wiki that heads each entry with the other person's
name.** Measured over the eight wikis on 2026-08-17, that is Chainsaw Man (14
subjects) and, partly, One Punch Man (3, and it keeps the section on a
`<Character>/Relationships` subpage whose headings are groups). The other six
name the section something else or keep no such section, and inventing gold for
them from prose would be researched gold, which is a different job with a
different standard of proof.

The output is `questions/_<series>_relations.json`. Underscore-prefixed so
`questions.load_all` skips it: this is coverage gold, transcribed from a
primary source but not independently researched, and it must not move the
headline number. See `docs/NEW_SERIES_PLAYBOOK.md`, "Build a bank, in two parts".
"""

from __future__ import annotations

import argparse
import collections
import json
import urllib.parse

from scriptengine.config import get_settings, load_overrides, series_paths
from scriptengine.retrieve import semantics as ont
from scriptengine.stores.facts import FactStore


def wiki_base(series: str, settings=None) -> str:
    """The wiki this series' bank names, rather than a table in this file.

    A `WIKI = {...}` map here would be the per-series hardcoding the project
    forbids, and the answer is already data: every bank records the site its
    answers were researched from.
    """
    root = (settings or get_settings()).questions_root
    raw = json.loads((root / f"{series}.json").read_text(encoding="utf-8"))
    base = (raw.get("wiki") or "").rstrip("/")
    if not base:
        raise SystemExit(f"questions/{series}.json names no wiki")
    return f"{base}/wiki/"


def headings(store: FactStore) -> dict[str, set[str]]:
    """`character -> the names its Relationships section heads`."""
    found: dict[str, set[str]] = collections.defaultdict(set)
    for row in store.connection.execute(
        "SELECT DISTINCT d.title, c.breadcrumb FROM chunks c"
        " JOIN documents d ON c.document_id = d.id"
        " WHERE d.page_type = 'character'"
        "   AND c.breadcrumb LIKE 'Relationships%'"
        " ORDER BY d.title"
    ):
        crumb = row["breadcrumb"] or ""
        if "/" not in crumb:
            continue
        found[row["title"]].add(crumb.split("/")[-1].strip())
    return found


def build(series: str, verified: str, settings=None) -> dict:
    paths = series_paths(series)
    overrides = load_overrides(paths)
    base = wiki_base(series, settings)
    questions = []
    with FactStore(paths.facts_db) as store:
        found = headings(store)
        for index, subject in enumerate(sorted(found), start=1):
            # A heading is gold only when the wiki types it as a character.
            # `Police Officers`, `Karaoke Friends`, `The dogs` and three
            # `Unnamed <relative>` headings are relationships the page
            # documents with nobody the graph can hold.
            people = sorted(
                name for name in found[subject]
                if ont.semantic_type(store, name, overrides) == ont.CHARACTER
            )
            if not people:
                continue
            questions.append({
                "id": f"{series}-rel-{index:02d}",
                "kind": "set",
                "question": f"Every documented relationship of {subject}",
                "subject": subject,
                # Recall-only. The store legitimately holds partners this
                # section never heads -- reading the story is the whole point
                # of declaring the narration sections -- so scoring precision
                # against this list would mark the intended gain as a defect.
                "scope": "core",
                "expect_mode": "relations",
                "tier": "wiki",
                "verified": verified,
                "sources": [base + urllib.parse.quote(subject.replace(" ", "_"))],
                "note": (
                    "Transcribed from the subheadings of this page's "
                    "`Relationships` section, which this wiki names after the "
                    "other person."
                ),
                "answer": [{"item": name, "aliases": []} for name in people],
            })
    return {"series": series, "questions": questions}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series", required=True)
    parser.add_argument("--verified", required=True, help="ISO date, e.g. 2026-08-17")
    args = parser.parse_args()

    settings = get_settings()
    bank = build(args.series, args.verified, settings)
    if not bank["questions"]:
        print(
            f"{args.series} heads no Relationships subsections with a character's"
            " name; nothing to transcribe."
        )
        return 1

    out = settings.questions_root / f"_{args.series}_relations.json"
    out.write_text(
        json.dumps(bank, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    pairs = sum(len(q["answer"]) for q in bank["questions"])
    print(f"{out.name}: {len(bank['questions'])} subjects, {pairs} pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

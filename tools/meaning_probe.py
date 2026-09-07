"""R1 probe: prove the meaning-index key and bound the model pass (no GPU).

Two read-only, offline checks against a stored `facts.db`, the go/no-go the
R1 council's "one thing to do first" demanded before any model batch:

  (i)   The `(subject, verb, object, arc_index)` key splits the live contested
        triples that B5's `(subject, verb, object)` key collides on -- the 112
        same-pair-different-arc meetings that R4 left as residue. Pure SQL
        over `events`, no model, no GPU.
  (ii)  The atemporal-complement size + `chapters`-fact coverage, so the model
        pass is *bounded and priced* rather than an unbounded ~48k-line batch:
        the meaning index only owes a `class`/`participants` answer for the
        lines `events` never classified (the atemporal two-thirds), and only
        the pages that file a `chapters` fact can carry a non-NULL `chapter`.

`--write-locators` (off by default) backfills the `meaning` table's SQL
columns for the atemporal complement -- `section_id`, `sentence_ordinal`,
`content_hash`, `chapter`, `revid` -- so the later model pass fills only
`class` / `participants` / `is_event`. This is the "pure-SQL backfill" that
bounds the model work; it needs no GPU.

Usage:
    python tools/meaning_probe.py [series] [--write-locators]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scriptengine.config import series_paths          # noqa: E402
from scriptengine.stores.facts import FactStore       # noqa: E402
from scriptengine.index.chunker import split_sentences  # noqa: E402


def _sections_with_chapters_fact(c) -> set[int]:
    """Section ids whose owning page files a resolvable `chapters` fact.

    A section's `chapter` locator is the wiki's own `chapters` fact on the
    page it lives on (verbatim, never a guess); pages that file none get a
    NULL. This is the coverage number that bounds how many meaning rows can
    carry a non-NULL `chapter`.
    """
    rows = c.execute(
        "SELECT DISTINCT s.id FROM sections s"
        " JOIN documents d ON d.id = s.document_id"
        " JOIN nodes n ON n.document_id = d.id"
        " JOIN facts f ON f.node_id = n.id AND LOWER(f.key) = 'chapters'"
    ).fetchall()
    return {row[0] for row in rows}


def key_proof(store: FactStore) -> dict:
    """(i) Does adding `arc_index` (or the owning page's `chapters` fact) to
    `(subject, verb, object)` split the contested triples? Pure SQL."""
    c = store.connection
    placed = c.execute(
        "SELECT COUNT(*) FROM (SELECT DISTINCT subject_name, verb, object_name"
        " FROM events WHERE arc_index IS NOT NULL)").fetchone()[0]
    contested = c.execute(
        "SELECT COUNT(*) FROM (SELECT subject_name, verb, object_name"
        " FROM events WHERE arc_index IS NOT NULL"
        " GROUP BY subject_name, verb, object_name"
        " HAVING COUNT(DISTINCT arc_index) >= 2)").fetchone()[0]
    t4 = c.execute(
        "SELECT COUNT(*) FROM (SELECT DISTINCT subject_name, verb, object_name,"
        " arc_index FROM events WHERE arc_index IS NOT NULL)").fetchone()[0]
    # A same-pair-same-arc meeting with more than one row is a *within-arc*
    # repeat: `arc_index` is the arc's story position, not the event's, so every
    # meeting of a pair inside one arc shares it. The meaning row's own
    # (section_id, sentence_ordinal) key is what splits those, so measure the
    # floor with the section added rather than asserting a clean 4-tuple.
    residual = c.execute(
        "SELECT COUNT(*) FROM (SELECT subject_name, verb, object_name, arc_index"
        " FROM events WHERE arc_index IS NOT NULL"
        " GROUP BY subject_name, verb, object_name, arc_index"
        " HAVING COUNT(*) > 1)").fetchone()[0]
    residual_5 = c.execute(
        "SELECT COUNT(*) FROM (SELECT subject_name, verb, object_name, arc_index,"
        " section_id FROM events WHERE arc_index IS NOT NULL"
        " GROUP BY subject_name, verb, object_name, arc_index, section_id"
        " HAVING COUNT(*) > 1)").fetchone()[0]
    # Breakdown of the contested triples: how many extra keys does the axis add?
    spread = c.execute(
        "SELECT COUNT(DISTINCT arc_index) AS k FROM events"
        " WHERE arc_index IS NOT NULL"
        " GROUP BY subject_name, verb, object_name"
        " HAVING COUNT(DISTINCT arc_index) >= 2 ORDER BY k DESC").fetchall()
    chaptered = c.execute(
        "SELECT COUNT(DISTINCT e.section_id) FROM events e"
        " WHERE e.arc_index IS NOT NULL AND e.section_id IS NOT NULL"
        " AND e.section_id IN (SELECT s.id FROM sections s"
        "   JOIN documents d ON d.id = s.document_id"
        "   JOIN nodes n ON n.document_id = d.id"
        "   JOIN facts f ON f.node_id = n.id AND LOWER(f.key) = 'chapters')").fetchone()[0]
    return {
        "placed_3tuples": placed,
        "contested_3tuples": contested,
        "distinct_4tuples": t4,
        "extra_keys_from_axis": t4 - placed,
        "within_arc_repeats": residual,
        "residual_after_section": residual_5,
        "sections_filing_chapters_fact": chaptered,
        "max_arc_spread": spread[0]["k"] if spread else 0,
    }


def complement(store: FactStore) -> dict:
    """(ii) Size of the atemporal complement + `chapters`-fact coverage.

    The meaning index owes a model answer only for the lines `events` never
    classified -- sections carrying no event row. That is the bounded pass;
    the ~48k corpus total is NOT it.
    """
    c = store.connection
    total_sections = c.execute(
        "SELECT COUNT(*) FROM sections").fetchone()[0]
    covered = {
        row[0] for row in c.execute(
            "SELECT DISTINCT section_id FROM events"
            " WHERE section_id IS NOT NULL").fetchall()
    }
    chaptered = _sections_with_chapters_fact(c)
    section_rows = c.execute("SELECT id, text FROM sections").fetchall()
    total_sentences = 0
    complement_sentences = 0
    complement_sections = 0
    complement_chaptered = 0
    per_doc: Counter[int] = Counter()
    for row in section_rows:
        n = len(split_sentences(row["text"] or ""))
        total_sentences += n
        if row[0] in covered:
            continue
        complement_sections += 1
        complement_sentences += n
        if row[0] in chaptered:
            complement_chaptered += 1
    return {
        "total_sections": total_sections,
        "event_covered_sections": len(covered),
        "complement_sections": complement_sections,
        "total_corpus_sentences": total_sentences,
        "complement_sentences": complement_sentences,
        "complement_sections_with_chapters_fact": complement_chaptered,
        "complement_sections_without_chapters_fact":
            complement_sections - complement_chaptered,
    }


def write_locators(store: FactStore) -> int:
    """Backfill the `meaning` table's SQL columns for the atemporal complement.

    The model columns (`class`, `participants`, `is_event`) stay NULL; this
    pass lays down the addressable key + the two locators so the model batch is
    a fill-in, not a from-scratch extract. `chapter` is the owning page's own
    `chapters` fact (verbatim); `revid` is the document's, so a re-crawl
    invalidates the row exactly when its line does.
    """
    store.ensure_meaning()
    c = store.connection
    covered = {
        row[0] for row in c.execute(
            "SELECT DISTINCT section_id FROM events"
            " WHERE section_id IS NOT NULL").fetchall()
    }
    chapter_by_doc = {
        row[0]: row[1] for row in c.execute(
            "SELECT DISTINCT n.document_id AS doc, f.value FROM facts f"
            " JOIN nodes n ON n.id = f.node_id"
            " WHERE LOWER(f.key) = 'chapters' AND n.document_id IS NOT NULL")
        .fetchall()
    }
    doc_revid = {
        row[0]: row[1] for row in c.execute(
            "SELECT id, revid FROM documents").fetchall()
    }
    section_rows = c.execute(
        "SELECT s.id, s.document_id, s.text FROM sections s").fetchall()
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    written = 0
    for s in section_rows:
        if s[0] in covered:
            continue
        doc_id = s[1]
        chapter = chapter_by_doc.get(doc_id)
        revid = doc_revid.get(doc_id)
        for ordinal, sentence in enumerate(split_sentences(s[2] or "")):
            digest = hashlib.sha256(sentence.encode("utf-8")).hexdigest()
            c.execute(
                "INSERT OR REPLACE INTO meaning"
                " (section_id, sentence_ordinal, content_hash, class, is_event,"
                "  participants, arc_index, chapter, revid, prompt_version,"
                "  model, extracted_at)"
                " VALUES (?, ?, ?, NULL, 0, NULL, NULL, ?, ?, NULL, NULL, ?)",
                (s[0], ordinal, digest, chapter, revid, now),
            )
            written += 1
    c.commit()
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("series", nargs="?", default="jjk")
    parser.add_argument(
        "--write-locators", action="store_true",
        help="backfill the `meaning` table's SQL columns for the atemporal "
             "complement (off by default; no GPU, but a state change)")
    args = parser.parse_args()

    path = series_paths(args.series).facts_db
    if not path.exists():
        print(f"no facts.db for series {args.series!r} at {path}")
        return 1
    with FactStore(path) as store:
        proof = key_proof(store)
        comp = complement(store)
        written = write_locators(store) if args.write_locators else None

    print(f"series: {args.series}   ({path.name})")
    print("\n(i) key proof -- does (s, v, o, arc_index) split the contested triples?")
    print(f"    distinct (s, v, o) with placement            = {proof['placed_3tuples']}")
    print(f"    ...contested (>=2 distinct arc_index)        = {proof['contested_3tuples']}")
    print(f"    distinct (s, v, o, arc_index)                = {proof['distinct_4tuples']}")
    print(f"    extra keys the axis adds (cross-arc)         = {proof['extra_keys_from_axis']}")
    print(f"    within-arc repeats on the 4-tuple            = {proof['within_arc_repeats']}")
    print(f"    ...residual once the section is added        = {proof['residual_after_section']}")
    print(f"    max arcs one (s, v, o) spreads across        = {proof['max_arc_spread']}")
    print(f"    sections filing a `chapters` fact            = {proof['sections_filing_chapters_fact']}")
    print(
        "    -> arc_index SPLITs the cross-arc contested triples; the within-arc\n"
        "       repeats fall to the section, which the meaning row's own key carries"
        if proof["residual_after_section"] == 0 else
        "    -> residual meetings share even a section; add time_rank to the key")

    print("\n(ii) atemporal complement -- the bounded model pass, not the corpus total")
    print(f"    total sections                               = {comp['total_sections']}")
    print(f"    sections `events` already classified         = {comp['event_covered_sections']}")
    print(f"    atemporal-complement sections                = {comp['complement_sections']}")
    print(f"    total corpus sentences (all sections)        = {comp['total_corpus_sentences']}")
    print(f"    atemporal-complement sentences (the batch)   = {comp['complement_sentences']}")
    print(f"      ...on a page with a `chapters` fact        = {comp['complement_sections_with_chapters_fact']}")
    print(f"      ...on a page with none (NULL chapter)      = {comp['complement_sections_without_chapters_fact']}")

    if written is not None:
        print(f"\n--write-locators: {written} meaning rows backfilled (model columns NULL)")
    else:
        print("\n(read-only; pass --write-locators to backfill the `meaning` locators)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
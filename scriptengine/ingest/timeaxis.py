"""The story's time axis: an orderable position for every placed event.

A relation places an event in an arc by *name* ("Shibuya Incident"), and a name
does not sort. To ask what a character knew at a given moment -- or to reject a
script line that reaches three arcs early -- an event needs an *index*, and the
three cheap signals that supply it, in the order the plan names them:

* **arc-named** -- the page is an arc, or names one in its `arc` fact. 100%
  reliable where present: the wiki filed the prose under the arc.
* **citations** -- the page's `chapters` fact, read against the chapter->arc map
  the corpus's own battle pages already state. Deterministic.
* **residue** -- neither reaches. That is where inference goes, and only there;
  a standing state the axis cannot place is a correct answer, not a miss.

Nothing here calls a model. It walks the wiki's own `previous`/`next` arc chain
(`chronology.chains`) and reads the `arc` and `chapters` facts the pages carry,
so the same question orders the timeline the same on Tuesday as on Monday.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from scriptengine.ingest.events import placement_pages
from scriptengine.retrieve import chronology
from scriptengine.stores.facts import FactStore

# The fact keys that name the arc a page belongs to. Every wiki spells it a
# little differently; the value still has to match an arc *page* to count.
_ARC_FACT_KEYS = ("arc", "story arc", "story_arcs")
_CHAPTER_FACT_KEYS = ("chapters",)

# A chapter span the wiki writes as `Chapter 213 - 215`, `Chapter 155 & 157`,
# `Chapter 84 - 85 & 88 - 90`, `Chapter 0-3`, or a bare `Chapter 4`. Split on
# the list separators, then expand a hyphen pair into the chapters it covers.
_SPAN_SEPARATORS = re.compile(r"[&•,]")
_LEADING_KIND = re.compile(r"^(chapter|volume)s?\s*", re.IGNORECASE)
_RANGE = re.compile(r"(\d+)\s*[-\u2013]\s*(\d+)")


@dataclass(frozen=True)
class PlacementAxis:
    """Where one placement page sits on the story's time axis.

    `arc` is the arc page it filed under (None on the residue), `index` its
    orderable position on that axis (None when the arc is off the story chain),
    and `signal` which of the three cheap signals placed it -- the report a
    residue pass reads to know what inference still has to do.
    """

    arc: str | None
    index: int | None
    signal: str  # "arc_page" | "arc_fact" | "chapters" | "residue"


def story_arc_index(store: FactStore) -> dict[str, int]:
    """arc name (lowercased) -> orderable position on the story's time axis.

    `chronology.chains` walks the wiki's own `previous`/`next` links and returns
    the ordered runs longest first, so the story (the longest run) takes the
    low positions and any filler run files after it. A name does not sort; this
    is what makes it orderable.
    """
    index: dict[str, int] = {}
    for chain in chronology.chains(store):
        for name in chain:
            index.setdefault(name.lower(), len(index))
    return index


def match_arc(store: FactStore, value: str | None) -> str | None:
    """Match an arc reference to the arc page the wiki actually has.

    The `arc` fact names the arc with or without its `Arc` suffix, and a
    double-arc event page writes both ("Culling Game Arc Shinjuku Showdown
    Arc"). Each shape is a lookup, not a guess: the value, the value with the
    suffix stripped, the value with the suffix added, and the first arc the
    value names when it names several.
    """
    if not value:
        return None
    pages = {a.lower(): a for a in chronology.arc_pages(store)}
    v = value.lower().strip()
    if v in pages:
        return pages[v]
    if v.endswith(" arc") and v[:-4] in pages:
        return pages[v[:-4]]
    if v + " arc" in pages:
        return pages[v + " arc"]
    first = re.match(r"(.+?)\s+arc\b", v)
    if first:
        stem = first.group(1).strip()
        for candidate in (stem, stem + " arc"):
            if candidate in pages:
                return pages[candidate]
    return None


def _chapter_numbers(value: str | None) -> list[int]:
    """The chapter numbers a `chapters` fact spans, in the order written."""
    if not value:
        return []
    body = _LEADING_KIND.sub("", value.strip())
    numbers: list[int] = []
    for piece in _SPAN_SEPARATORS.split(body):
        piece = piece.strip()
        if not piece:
            continue
        span = _RANGE.fullmatch(piece)
        if span:
            lo, hi = int(span.group(1)), int(span.group(2))
            if lo > hi:
                lo, hi = hi, lo
            numbers.extend(range(lo, hi + 1))
            continue
        match = re.fullmatch(r"\d+", piece)
        if match:
            numbers.append(int(piece))
    seen: set[int] = set()
    return [n for n in numbers if not (n in seen or seen.add(n))]


def chapter_arc_index(store: FactStore) -> dict[int, str]:
    """chapter number -> arc page, read off the corpus's own battle pages.

    A battle page names both the arc it belongs to and the chapters it spans, so
    every chapter the wiki files under an arc is a lookup. A chapter no battle
    files stays unmapped -- a gap in the wiki, not a number to invent.
    """
    out: dict[int, str] = {}
    rows = store.connection.execute(
        "SELECT f1.value AS arc, f2.value AS chapters FROM facts f1"
        " JOIN facts f2 ON f2.node_id = f1.node_id"
        " WHERE LOWER(f1.key) IN (?, ?, ?) AND LOWER(f2.key) = ?",
        (*_ARC_FACT_KEYS, *_CHAPTER_FACT_KEYS),
    ).fetchall()
    for row in rows:
        arc = match_arc(store, row["arc"])
        if not arc:
            continue
        for chapter in _chapter_numbers(row["chapters"]):
            out.setdefault(chapter, arc)
    return out


def _placement_facts(
    store: FactStore, pages: list[str]
) -> dict[str, tuple[str | None, str | None]]:
    """The `arc` and `chapters` fact values each placement page carries."""
    out: dict[str, tuple[str | None, str | None]] = {p: (None, None) for p in pages}
    if not pages:
        return out
    placeholders = ",".join("?" * len(pages))
    rows = store.connection.execute(
        f"SELECT n.name AS page, LOWER(f.key) AS key, f.value AS value"
        f" FROM facts f JOIN nodes n ON n.id = f.node_id"
        f" WHERE n.name IN ({placeholders})"
        f" AND LOWER(f.key) IN (?, ?, ?, ?)",
        (*pages, *_ARC_FACT_KEYS, *_CHAPTER_FACT_KEYS),
    ).fetchall()
    for row in rows:
        arc, chapters = out.get(row["page"], (None, None))
        if row["key"] in _ARC_FACT_KEYS:
            arc = row["value"]
        else:
            chapters = row["value"]
        out[row["page"]] = (arc, chapters)
    return out


def placement_time_axis(store: FactStore) -> dict[str, PlacementAxis]:
    """Where each placement page sits on the story's time axis.

    The page-level signal, not the section's: an event is stored under the page
    that stated it, and that page's place on the axis is what orders it. The
    cheap signals run in the plan's order and stop at the first that reaches.
    """
    index = story_arc_index(store)
    chapter_map = chapter_arc_index(store)
    arc_set = {a.lower() for a in chronology.arc_pages(store)}
    pages = placement_pages(store)
    facts = _placement_facts(store, pages)

    out: dict[str, PlacementAxis] = {}
    for page in pages:
        if page.lower() in arc_set:
            # The page *is* the arc: the strongest placement there is.
            out[page] = PlacementAxis(page, index.get(page.lower()), "arc_page")
            continue
        arc_value, chapter_value = facts[page]
        arc = match_arc(store, arc_value)
        if arc:
            out[page] = PlacementAxis(arc, index.get(arc.lower()), "arc_fact")
            continue
        for chapter in _chapter_numbers(chapter_value):
            if chapter in chapter_map:
                filed = chapter_map[chapter]
                out[page] = PlacementAxis(
                    filed, index.get(filed.lower()), "chapters"
                )
                break
        else:
            # The residue: no arc named, no citation the wiki files under an
            # arc. Inference is the only signal left, and this is where it goes.
            out[page] = PlacementAxis(None, None, "residue")
    return out


def backfill_event_arc_index(store: FactStore) -> dict[str, int]:
    """Store every event's position on the story axis, no model.

    The `arc_index` column is a read-time convenience so the global order is a
    plain `ORDER BY`; it is recomputed here from the placement axis, so a
    re-extraction or a re-crawl that moves an arc is picked up on the next run.
    The returned tally is the coverage number the residue pass reads: how many
    placement pages each cheap signal reaches, across every placement page, not
    just the ones that happen to carry an event.
    """
    store.ensure_events()
    if "arc_index" not in {
        row[1] for row in store.connection.execute("PRAGMA table_info(events)")
    }:
        store.connection.execute("ALTER TABLE events ADD COLUMN arc_index INTEGER")
        store.connection.commit()

    axis = placement_time_axis(store)
    page_index = {page: placed.index for page, placed in axis.items()}
    tally = {"arc_page": 0, "arc_fact": 0, "chapters": 0, "residue": 0}
    for placed in axis.values():
        tally[placed.signal] += 1

    for page in {
        row["arc_key"]
        for row in store.connection.execute("SELECT DISTINCT arc_key FROM events")
    }:
        store.connection.execute(
            "UPDATE events SET arc_index = ? WHERE arc_key = ? COLLATE NOCASE",
            (page_index.get(page), page),
        )
    store.connection.commit()
    tally["pages"] = len(axis)
    tally["rows"] = store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    return tally


def events_in_story_order(
    store: FactStore, subject: str | None = None
) -> list[dict]:
    """Every placed event, in canon order: arc first, the page's clock within.

    The door a script writer reads: an event filed in the Shibuya Incident arc
    (index 6) always precedes one filed in the Culling Game (index 7), which is
    what lets a continuity check say a line reaches three arcs early. Events
    whose page the cheap signals cannot place sort last, under no arc.
    """
    store.ensure_events()
    axis = placement_time_axis(store)
    arc_name = {page: placed.arc for page, placed in axis.items()}

    sql = (
        "SELECT arc_key, arc_index, subject_name, object_name, verb,"
        "        time_rank, temporal, quote FROM events"
    )
    args: list = []
    if subject:
        sql += " WHERE subject_name = ? COLLATE NOCASE"
        args.append(subject)
    sql += (
        " ORDER BY (arc_index IS NULL) ASC, arc_index ASC,"
        "          time_rank ASC, subject_name COLLATE NOCASE"
    )
    rows = [dict(row) for row in store.connection.execute(sql, args)]
    for row in rows:
        row["arc_name"] = arc_name.get(row["arc_key"])
    return rows
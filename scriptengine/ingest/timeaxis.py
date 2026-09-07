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

from scriptengine.ingest.events import EVENTIVE_VERBS, placement_pages
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


def _match_arc_value(pages: dict[str, str], value: str | None) -> str | None:
    """The arc-reference shapes against a precomputed `{arc-lower: arc page}` table.

    Split from `match_arc` so a caller that matches many values (the section
    signal) pays for the `arc_pages` read once, not per value.
    """
    if not value:
        return None
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


def match_arc(store: FactStore, value: str | None) -> str | None:
    """Match an arc reference to the arc page the wiki actually has.

    The `arc` fact names the arc with or without its `Arc` suffix, and a
    double-arc event page writes both ("Culling Game Arc Shinjuku Showdown
    Arc"). Each shape is a lookup, not a guess: the value, the value with the
    suffix stripped, the value with the suffix added, and the first arc the
    value names when it names several.
    """
    return _match_arc_value(
        {a.lower(): a for a in chronology.arc_pages(store)}, value
    )


def section_arc_index(store: FactStore) -> dict[int, tuple[int, str]]:
    """section_id -> (the story-axis index of the arc the section is named for,
    the section's owning page, lowercased).

    A character or synopsis page files its per-arc prose under sections titled
    after the arc ("Culling Game Arc"). The section *is* the placement: an event
    stated in that section sits in that arc even when the page itself is off the
    story chain (a character's own page is not on it). Resolved through the live
    `sections` table by id and the owning page is returned so the backfill can
    guard: a section only places the events it actually belongs to. A dangling or
    reused id -- a re-crawl that renumbered the section table -- yields no row and
    so no placement. That is a miss, never a wrong arc, because the wiki filed no
    placement there and none is invented.
    """
    index = story_arc_index(store)
    pages = {a.lower(): a for a in chronology.arc_pages(store)}
    out: dict[int, tuple[int, str]] = {}
    rows = store.connection.execute(
        "SELECT s.id, s.title, d.title AS page FROM sections s"
        " JOIN documents d ON d.id = s.document_id"
        " WHERE s.title IS NOT NULL AND TRIM(s.title) <> ''"
    )
    for row in rows:
        arc = _match_arc_value(pages, row["title"].strip())
        if arc is None:
            continue
        pos = index.get(arc.lower())
        if pos is None:
            continue
        out[row["id"]] = (pos, (row["page"] or "").lower())
    return out


def _supplementary_pages(store: FactStore) -> list[str]:
    """The chapter and episode pages, which file themselves under an arc.

    `placement_pages` is the prose-weight-ordered arc/event/battle set, where a
    wiki states what happened. A chapter or episode page states it too and
    carries its own `arc` fact, but it is not a placement type, so the axis
    walks these separately and applies the same `arc_fact`/`chapters` signals
    rather than leaving their events off the axis for want of a page-type match.
    """
    rows = store.connection.execute(
        "SELECT title FROM documents"
        " WHERE LOWER(page_type) IN ('chapter', 'episode')"
    )
    return [row["title"] for row in rows]


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
    The walk covers the placement pages plus the chapter/episode pages, which
    file themselves under an arc but are not placement types.
    """
    index = story_arc_index(store)
    chapter_map = chapter_arc_index(store)
    arc_set = {a.lower() for a in chronology.arc_pages(store)}
    pages = placement_pages(store) + _supplementary_pages(store)
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


def citation_arc_maps(
    store: FactStore,
) -> tuple[dict[int, int], dict[int, int]]:
    """chapter / episode number -> story-axis index, from the wiki's own filings.

    Chapters: the battle pages' `chapters` fact, which files every chapter a
    battle spans under that battle's arc (a `chapter_arc_index` lookup).
    Episodes: each episode page files itself under an arc in its own `arc`
    fact, and the axis already walks those pages. A number no wiki page files
    stays unmapped -- a wiki gap, not a number to invent.
    """
    index = story_arc_index(store)
    chapter_map = {
        chapter: index[arc.lower()]
        for chapter, arc in chapter_arc_index(store).items()
        if index.get(arc.lower()) is not None
    }
    episode_map: dict[int, int] = {}
    for title, placed in placement_time_axis(store).items():
        match = re.fullmatch(r"episode\s+(\d+)", title.strip(), re.IGNORECASE)
        if match is not None and placed.index is not None:
            episode_map[int(match.group(1))] = placed.index
    return chapter_map, episode_map


_PARENTHETICAL = re.compile(r"\(([^()]+)\)")
_CHAPTER_IN = re.compile(r"[Cc]hapters?\s*(\d+(?:\s*[-\u2013]\s*\d+)?)")
_EPISODE_IN = re.compile(r"[Ee]pisodes?\s*(\d+(?:\s*[-\u2013]\s*\d+)?)")


def _citation_groups(text: str | None) -> list[tuple[str, int]]:
    """The in-text chapter/episode citations in a stretch of section text.

    One `('ch', n)` / `('ep', n)` per cited number, ranges expanded. The
    wiki's side-story citations ("Modulo Chapter N") name a different
    numbering that files under no arc on the main chain, so their
    parentheticals are skipped: a miss, never a wrong arc.
    """
    out: list[tuple[str, int]] = []
    for group in _PARENTHETICAL.finditer(text or ""):
        inner = group.group(1)
        if "modulo" in inner.lower():
            continue
        for kind, pattern in (("ch", _CHAPTER_IN), ("ep", _EPISODE_IN)):
            for raw in pattern.findall(inner):
                pieces = re.split(r"\s*[-\u2013]\s*", raw)
                if len(pieces) == 2 and all(p.strip().isdigit() for p in pieces):
                    lo, hi = int(pieces[0]), int(pieces[1])
                    if lo > hi:
                        lo, hi = hi, lo
                    out.extend((kind, n) for n in range(lo, hi + 1))
                elif raw.strip().isdigit():
                    out.append((kind, int(raw.strip())))
    return out


def _citation_decision(
    maps: tuple[dict[int, int], dict[int, int]],
    arc_names: dict[int, str],
    quote: str | None,
    section_text: str | None,
) -> tuple[int | None, str, str]:
    """The arc a row's in-text citations ground it in -- or the triage reason.

    Returns ``(index, signal, detail)``: an index when one arc is determinate,
    else ``None`` with the reason the placement is owed but ungroundable. The
    paragraph rule: the wiki's citation follows the sentences it covers, so
    the paragraph that states the event is the one that files it; a paragraph
    whose citations all map to one arc places the row. The section rule: a
    section cited at least twice into a single arc has its scope fixed by the
    wiki, and every event stated in it sits in that arc. One citation files
    no scope; citations that span arcs file no single placement.
    """
    chapter_map, episode_map = maps
    text = section_text or ""

    def arcs_of(cites: list[tuple[str, int]]) -> set[int]:
        arcs = set()
        for kind, number in cites:
            index = (chapter_map if kind == "ch" else episode_map).get(number)
            if index is not None:
                arcs.add(index)
        return arcs

    para_cites: list[tuple[str, int]] = []
    located = False
    head = (quote or "").strip()[:60]
    if text and len(head) >= 20:
        # Whitespace-tolerant: the stored quote is the extraction's normalised
        # form, the section text is the page's; the first 60 chars still pin it.
        pattern = r"\s+".join(re.escape(part) for part in head.split())
        match = re.search(pattern, text)
        if match:
            located = True
            end = text.find("\n\n", match.start())
            para_cites = _citation_groups(
                text[match.start() : end if end > 0 else len(text)]
            )
    section_cites = _citation_groups(text)
    para_arcs = arcs_of(para_cites)
    section_arcs = arcs_of(section_cites)

    if len(para_arcs) == 1:
        return next(iter(para_arcs)), "para-citation", ""
    if len(section_cites) >= 2 and len(section_arcs) == 1:
        return next(iter(section_arcs)), "section-scope", ""

    prefix = "" if located else "quote-not-located; "
    if not section_cites:
        return None, prefix + "no-citation", ""
    if len(section_cites) == 1:
        return (
            None,
            prefix + "single-citation",
            "one in-text citation files no section scope",
        )
    if not section_arcs:
        refs = ", ".join(f"{k}{n}" for k, n in section_cites[:6])
        return None, prefix + "refs-unfiled", f"cited {refs} file under no arc"
    names = [arc_names[i] for i in sorted(section_arcs) if i in arc_names]
    return (
        None,
        prefix + "citations-span-arcs",
        "citations span " + " / ".join(names),
    )


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
    page_index = {page.lower(): placed.index for page, placed in axis.items()}
    section_map = section_arc_index(store)
    tally = {"arc_page": 0, "arc_fact": 0, "chapters": 0, "residue": 0}
    for placed in axis.values():
        tally[placed.signal] += 1

    # The section signal refines the page signal: an event stated in a section the
    # wiki named for an arc sits in that arc even when the page is off the story
    # chain. Guarded by the section's owning page (the backfill only applies it to
    # an event whose page the section actually belongs to), so a dangling or
    # reused section id -- a renumbering re-crawl -- misses, never misplaces.
    # `pair_index` records what the page+section signals gave each pair; the
    # citation pass below works only where they reached nothing.
    pair_index: dict[tuple[str, int | None], int | None] = {}
    for pair in store.connection.execute(
        "SELECT DISTINCT arc_key, section_id FROM events WHERE arc_key IS NOT NULL"
    ):
        page = pair["arc_key"]
        section_id = pair["section_id"]
        page_lower = page.lower()
        index = page_index.get(page_lower)
        section = section_map.get(section_id) if section_id is not None else None
        if section is not None and section[1] == page_lower:
            index = section[0]
        pair_index[(page_lower, section_id)] = index
        store.connection.execute(
            "UPDATE events SET arc_index = ?"
            " WHERE arc_key = ? COLLATE NOCASE AND section_id IS ?",
            (index, page, section_id),
        )

    # The third, weakest signal: the wiki's own in-text citation (R4, the D6
    # completion plan -- place what the citations ground, triage the rest).
    # It is per-row, because the quote decides which paragraph files the event:
    # the page and section signals above set one index per (page, section).
    # Modulo side-story citations are excluded by _citation_groups, so their
    # rows stay unplaced and land in the triage ledger with a reason. The tally
    # counts rows the citation signal places by right, not rows it UPDATEd this
    # run, so a second (settled) backfill reports the same number.
    maps = citation_arc_maps(store)
    arc_names = {i: a for a, i in story_arc_index(store).items()}
    section_texts = {
        row["id"]: (row["text"] or "")
        for row in store.connection.execute("SELECT id, text FROM sections")
    }
    citation_placed = 0
    for (page_lower, section_id) in sorted(
        (key for key, value in pair_index.items() if value is None),
        key=lambda key: (key[0], key[1] or -1),
    ):
        text = section_texts.get(section_id, "") if section_id is not None else ""
        for row in store.connection.execute(
            "SELECT subject_node, verb, object_node, section_id, time_rank,"
            " arc_index, quote FROM events WHERE arc_key = ? COLLATE NOCASE"
            " AND section_id IS ?",
            (page_lower, section_id),
        ):
            index, _signal, _detail = _citation_decision(
                maps, arc_names, row["quote"], text
            )
            if index is None:
                continue
            citation_placed += 1
            if row["arc_index"] is None:
                store.connection.execute(
                    "UPDATE events SET arc_index = ? WHERE subject_node = ?"
                    " AND verb = ? AND object_node IS ? AND section_id IS ?"
                    " AND time_rank IS ?",
                    (
                        index,
                        row["subject_node"],
                        row["verb"],
                        row["object_node"],
                        row["section_id"],
                        row["time_rank"],
                    ),
                )
    store.connection.commit()
    tally["citations"] = citation_placed
    tally["pages"] = len(axis)
    tally["rows"] = store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    return tally


def triage_unplaced(store: FactStore) -> list[dict]:
    """The ledger of every row the axis cannot place: the row and the reason.

    The R4 done-criterion (``COUNCIL_d6-completion.md``): an unplaced event is
    a legal outcome only with a recorded reason. The reasons are *derived*,
    not stored -- the same lookups the backfill ran -- so a re-crawl that moves
    a wiki filing moves the ledger with it. Run it on a settled store (the
    backfill ran; every door into the axis goes through ``recompute_temporal``,
    which runs it), or the ledger would list rows the backfill could place.
    """
    store.ensure_events()
    maps = citation_arc_maps(store)
    arc_names = {i: a for a, i in story_arc_index(store).items()}
    section_texts = {
        row["id"]: (row["text"] or "")
        for row in store.connection.execute("SELECT id, text FROM sections")
    }
    out: list[dict] = []
    for row in store.connection.execute(
        "SELECT e.doc_title AS page, s.title AS section, e.section_id,"
        " e.verb, e.subject_name, e.object_name, e.time_rank, e.quote"
        " FROM events e LEFT JOIN sections s ON s.id = e.section_id"
        " WHERE e.arc_index IS NULL ORDER BY e.doc_title, e.time_rank"
    ):
        text = (
            section_texts.get(row["section_id"], "")
            if row["section_id"] is not None
            else ""
        )
        index, reason, detail = _citation_decision(
            maps, arc_names, row["quote"], text
        )
        if index is not None:
            # The backfill runs before this door (recompute_temporal); a row it
            # could place but did not is a store the backfill never saw -- fail
            # loud rather than publish a wrong ledger.
            raise RuntimeError(
                f"triage ledger: {row['page']}:{row['verb']} "
                "is placeable but unplaced; run the backfill first"
            )
        out.append(
            {
                "page": row["page"],
                "section": row["section"],
                "subject": row["subject_name"],
                "verb": row["verb"],
                "object": row["object_name"],
                "time_rank": row["time_rank"],
                "reason": reason,
                "detail": detail,
            }
        )
    return out


def recompute_temporal(store: FactStore) -> dict:
    """Re-derive the ``temporal`` flag from the placement that already exists.

    The check-3 event test, keyed on the placement the backfill just computed:
    a row with an eventive verb the axis can place (``arc_index`` not null) is
    an event, ``temporal=1``; a row the axis cannot place is a standing state,
    ``temporal=0``. It does not ask whether ``arc_key`` resolves to a placement
    page -- a character or synopsis page title never will, by contract -- which
    is what froze ``temporal=1`` at the placement-set count while the corpus
    rows, placed by the section signal, sat mislabelled ``temporal=0``.

    Pure SQL over the columns the backfill wrote: no model, no GPU. Idempotent --
    a second run moves nothing. Returns the backfill tally plus the before/after
    ``temporal`` counts and how many rows each way moved.
    """
    store.ensure_events()
    tally = backfill_event_arc_index(store)
    marks = ",".join("?" for _ in EVENTIVE_VERBS)
    before = store.connection.execute(
        "SELECT COUNT(*) FROM events WHERE temporal = 1"
    ).fetchone()[0]
    promoted = store.connection.execute(
        f"SELECT COUNT(*) FROM events WHERE temporal = 0"
        f" AND arc_index IS NOT NULL AND verb IN ({marks})",
        tuple(EVENTIVE_VERBS),
    ).fetchone()[0]
    demoted = store.connection.execute(
        "SELECT COUNT(*) FROM events WHERE temporal = 1 AND arc_index IS NULL"
    ).fetchone()[0]
    store.connection.execute(
        f"UPDATE events SET temporal = CASE"
        f" WHEN arc_index IS NOT NULL AND verb IN ({marks}) THEN 1 ELSE 0 END",
        tuple(EVENTIVE_VERBS),
    )
    store.connection.commit()
    after = store.connection.execute(
        "SELECT COUNT(*) FROM events WHERE temporal = 1"
    ).fetchone()[0]
    unplaced = store.connection.execute(
        "SELECT COUNT(*) FROM events WHERE arc_index IS NULL"
    ).fetchone()[0]
    tally.update(
        temporal_before=before,
        temporal_after=after,
        temporal_promoted=promoted,
        temporal_demoted=demoted,
        temporal_unplaced=unplaced,
    )
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
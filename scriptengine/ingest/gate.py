"""The comprehension gate: three mechanical equality checks over the events table.

The plan's gate is not a grade -- there is no gold, nothing an agent can be
generous about. It is string and foreign-key equality, in three parts:

* **check 3 -- arc placement.** A temporal event states an order on the story;
  the arc it was read from must sit on the time axis. A row whose page the axis
  cannot place is a dangling placement, and it is recorded *as* a standing state
  (``temporal=0``) rather than left dangling. A write, reported as a count.
* **cross-page agreement.** The Shibuya fight is stated on Yuji's page, on
  Sukuna's page and on the arc page, by editors who did not write each other's
  pages. The same event, extracted independently from each, must carry a
  consistent arc placement. An agent cannot reword its way into agreement
  between authors it did not write -- so a disagreement here is a real,
  measured comprehension failure, not a model artefact.
* **coverage split.** The percentage of narrative beats that carry a surviving
  row, temporal versus atemporal.

Nothing here calls a model. It reads the events table and the time axis, and
reports what the wiki's own editors agreed -- and where they did not.
"""

from __future__ import annotations

from collections.abc import Sequence

from scriptengine.ingest import timeaxis
from scriptengine.ingest.events import extractable_sections, placement_pages
from scriptengine.stores.facts import FactStore

# A group this large with a minority arc is a modelling problem, not "the wiki
# disagrees with itself": enough independent editors placing the same event one
# way for the plurality to be coincidence is the case the halt rule flags.
_WELL_POPULATED = 4
_MINORITY_SHARE = 0.8


def arc_placement_violations(store: FactStore) -> list[dict]:
    """The temporal rows whose placement the time axis cannot reach.

    A row that states an order (``temporal=1``) but whose page is on the residue
    -- no ``arc_index`` -- is a dangling placement. Pure: it names the rows, it
    does not move them.
    """
    timeaxis.backfill_event_arc_index(store)
    rows = store.connection.execute(
        "SELECT arc_key, subject_name, verb, object_name, quote, time_rank"
        " FROM events WHERE temporal = 1 AND arc_index IS NULL"
        " ORDER BY arc_key, time_rank"
    ).fetchall()
    return [dict(row) for row in rows]


def enforce_arc_placement(store: FactStore) -> dict:
    """Check 3, applied: a dangling placement is recorded as a standing state.

    Flips every temporal row the axis cannot place to ``temporal=0`` in the
    events table, so a later read never sees a temporal event with no arc.
    Idempotent -- a second run finds nothing to move.
    """
    violations = arc_placement_violations(store)
    if violations:
        store.connection.execute(
            "UPDATE events SET temporal = 0 WHERE temporal = 1 AND arc_index IS NULL"
        )
        store.connection.commit()
    return {"flipped": len(violations), "rows": violations}


def _arc_names(store: FactStore) -> dict[int, str]:
    """arc_index -> the arc page it names, for a readable report.

    Mirrors ``story_arc_index`` (same ``chronology.chains`` walk) but keeps the
    page title's own casing, so a report reads "Shibuya Incident Arc" not
    "shibuya incident arc".
    """
    from scriptengine.retrieve import chronology

    by_position: dict[int, str] = {}
    for chain in chronology.chains(store):
        for name in chain:
            by_position.setdefault(len(by_position), name)
    return by_position


def cross_page_agreement(store: FactStore) -> dict:
    """The ungameable check: the same event, on several pages, in one arc.

    An event is ``(verb, participant-pair)``, the pair as a *set* -- ``A fought
    B`` and ``B fought A`` are one fight, whichever page named which as
    subject. A group whose rows come from two or more source pages and whose
    ``arc_index`` values do not all agree is a disagreement: independent
    editors placed the same event in different arcs. Every disagreement is
    returned in full -- both rows, their pages, quotes, ``arc_key`` and
    ``arc_index`` -- not a summary count.
    """
    timeaxis.backfill_event_arc_index(store)
    names = _arc_names(store)
    rows = [
        dict(row)
        for row in store.connection.execute(
            "SELECT verb, subject_node, subject_name, object_node, object_name,"
            " arc_key, arc_index, temporal, time_rank, quote FROM events"
        )
    ]

    groups: dict[tuple[str, frozenset[int]], list[dict]] = {}
    for row in rows:
        pair = frozenset((int(row["subject_node"]), int(row["object_node"])))
        groups.setdefault((row["verb"], pair), []).append(row)

    ordered = sorted(
        ((verb, pair, group) for (verb, pair), group in groups.items()),
        key=lambda item: (item[0], _node_names(item[1], item[2])),
    )

    stats = {"groups": len(groups), "multi_page_groups": 0, "agreeing": 0, "disagreeing": 0}
    disagreements: list[dict] = []
    for verb, pair, group in ordered:
        pages = {row["arc_key"].strip().lower() for row in group}
        if len(pages) < 2:
            continue
        stats["multi_page_groups"] += 1
        arcs = sorted({row["arc_index"] for row in group if row["arc_index"] is not None})
        if len(arcs) <= 1:
            stats["agreeing"] += 1
            continue
        stats["disagreeing"] += 1

        per_arc: dict[int | None, int] = {}
        for row in group:
            per_arc[row["arc_index"]] = per_arc.get(row["arc_index"], 0) + 1
        majority = max(per_arc.values()) / len(group)
        disagreements.append(
            {
                "verb": verb,
                "participants": _node_names(pair, group),
                "rows": [
                    {
                        "arc_key": row["arc_key"],
                        "arc_index": row["arc_index"],
                        "arc": names.get(row["arc_index"], "[unplaced]"),
                        "temporal": bool(row["temporal"]),
                        "time_rank": row["time_rank"],
                        "direction": f'{row["subject_name"]} -> {row["object_name"]}',
                        "quote": row["quote"],
                    }
                    for row in sorted(group, key=lambda r: (r["arc_index"] is None, r["arc_index"] or 0, r["arc_key"]))
                ],
                "arcs": arcs,
                "arc_span": (max(arcs) - min(arcs)) if arcs else 0,
                "adjacent": (max(arcs) - min(arcs)) == 1 if arcs else False,
                "participant_count": len(pair),
                "majority_share": round(majority, 3),
                "well_populated": len(group) >= _WELL_POPULATED,
                "modeling_problem": len(group) >= _WELL_POPULATED and majority < _MINORITY_SHARE,
            }
        )
    return {"stats": stats, "disagreements": disagreements, "arc_names": names}


def _node_names(pair: frozenset[int], rows: Sequence[dict]) -> list[str]:
    wanted = set(pair)
    seen: dict[int, str] = {}
    for row in rows:
        for node, label in ((int(row["subject_node"]), row["subject_name"]), (int(row["object_node"]), row["object_name"])):
            if node in wanted and node not in seen:
                seen[node] = label
    return [seen[n] for n in sorted(wanted)]


def coverage_split(store: FactStore) -> dict:
    """The percentage of narrative beats that carry a surviving row.

    A *beat* is one of the page's prose sections -- the unit the narrative
    retriever orders -- and a beat *carries* a row when some stored event was
    read out of it. The split is temporal versus atemporal, read after check 3
    has settled which rows are which.
    """
    beat_ids: set[int] = set()
    for page in placement_pages(store):
        for section in extractable_sections(store, page):
            beat_ids.add(int(section["id"]))
    total = len(beat_ids)
    if total == 0:
        return {"beats": 0, "any": 0.0, "temporal": 0.0, "atemporal": 0.0}

    by_section: dict[int, list[int]] = {}
    for row in store.connection.execute("SELECT section_id, temporal FROM events"):
        by_section.setdefault(int(row["section_id"]), []).append(int(row["temporal"]))

    any_beats = temporal_beats = atemporal_beats = 0
    for beat in beat_ids:
        flags = by_section.get(beat)
        if not flags:
            continue
        any_beats += 1
        if 1 in flags:
            temporal_beats += 1
        if 0 in flags:
            atemporal_beats += 1
    return {
        "beats": total,
        "any": round(any_beats / total, 4),
        "temporal": round(temporal_beats / total, 4),
        "atemporal": round(atemporal_beats / total, 4),
    }


def gate_report(store: FactStore) -> dict:
    """The gate, run in order: place, then agree, then cover.

    Check 3 mutates the table first, so the coverage split reads the settled
    temporal flags. The report is what a script writer -- and the twenty-failure
    acceptance set -- is meant to read.
    """
    check3 = enforce_arc_placement(store)
    agreement = cross_page_agreement(store)
    coverage = coverage_split(store)
    return {"check3": check3, "agreement": agreement, "coverage": coverage}
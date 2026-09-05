"""The continuity check: the D6-consumer, validation-layer scaffold.

The placement-signal fix put every placed event on the time axis
(``events.arc_index``), so this module can now do what the plan's continuity-
check was scoped for: answer what a subject knew up to a moment, and flag a
beat that references an event out of order -- a line that reaches three arcs
early. The design record is ``reports/comprehension/COUNCIL_continuity-check.md``.

Nothing here calls a model. It reads the events table, the time axis and the
cross-page agreement, and reports a *gap* -- the distance between the arc a beat
claims and the arc the event actually sits in. A gap is a **flag, not a
verdict**: a large gap is *either* an anachronism *or* a legitimate
flashback/recap, and deciding which is the writer's call, not the check's. The
check's job is to make the gap visible and cheap to enumerate.

This is a scaffold, not a consumer: nothing wires it into a script pipeline. The
consumer is the D6 write-layer (the "Owner of the 116" named in
``reports/comprehension/GATE.md``), which takes the gap flags and decides what
they mean. Until then this module is a set of pure, model-free lookups over the
fact store, each one independently testable.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from typing import Any

from scriptengine.ingest import gate
from scriptengine.stores.facts import FactStore

# A filing the wiki states on many pages under a coarse verb is "true in six
# arcs", not an error: a character arrives and departs in several arcs. Only an
# interaction verb carried across a gap of two arcs or more is an anachronism
# candidate -- the "event" kind of line the plan's continuity-check rejects.
_STATE_VERBS = frozenset({"arrived", "departed"})


def _participant_match(verb: str, participants: Sequence[str]) -> tuple[str, list[str]]:
    """A SQL predicate + params for the events rows a (verb, participants)
    filing names. The event row states the same two ends as subject and object,
    in either order, and the filing may name one participant (a self-event)."""
    verb = verb.strip().lower()
    parts = [p.strip().lower() for p in participants if p.strip()]
    if len(parts) == 1:
        predicate = (
            "LOWER(verb) = ? AND"
            " (LOWER(subject_name) = ? OR LOWER(object_name) = ?)"
        )
        return predicate, [verb, parts[0], parts[0]]
    first, second = parts[0], parts[1]
    predicate = (
        "LOWER(verb) = ? AND"
        " ((LOWER(subject_name) = ? AND LOWER(object_name) = ?)"
        "  OR (LOWER(subject_name) = ? AND LOWER(object_name) = ?))"
    )
    return predicate, [verb, first, second, second, first]


def adjudicated_arc(
    store: FactStore, *, verb: str, participants: Sequence[str]
) -> dict[str, Any]:
    """The arc a (verb, participants) filing actually sits in, adjudicated by the
    wiki's own cross-page majority.

    The mode ``arc_index`` over every placed row for the filing is the answer:
    the arc the majority of the pages that state the event file it under. A
    corpus truth, independent of the single ``events.arc_index`` a beat check
    validates -- so measuring a gap against it is not circular. A strict
    majority (the top count strictly above the rest) is a clean adjudication; a
    tie is reported as ``disputed`` rather than forced onto one arc.
    """
    predicate, params = _participant_match(verb, participants)
    rows = store.connection.execute(
        f"SELECT arc_index FROM events WHERE {predicate} AND arc_index IS NOT NULL",
        params,
    ).fetchall()
    if not rows:
        return {
            "actual": None,
            "arcs": [],
            "majority_share": 0.0,
            "disputed": False,
            "note": "no placed event matches this filing",
        }
    counts = Counter(row["arc_index"] for row in rows)
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    actual, top_count = ranked[0]
    disputed = len(ranked) > 1 and ranked[1][1] == top_count
    return {
        "actual": actual,
        "arcs": sorted(counts),
        "majority_share": round(top_count / len(rows), 3),
        "disputed": disputed,
        "note": "",
    }


def beat_gap(
    store: FactStore,
    *,
    verb: str,
    participants: Sequence[str],
    claimed_arc_index: int,
    threshold: int = 2,
) -> dict[str, Any]:
    """The one subtraction the continuity-check is made of: how far the arc a
    beat *claims* an event sits in is from the arc it actually sits in.

    ``claimed_arc_index`` is what the beat's source asserts (the writer places
    the event here); the event's own placement is the wiki's cross-page
    majority (``adjudicated_arc``). The gap is a **flag, not a verdict**: at or
    above ``threshold`` it means *look*, and whether that look finds an error
    or a legitimate flashback is the writer's call. The plan's "three arcs
    early" is ``threshold=3``; the corpus's common regime is 2.
    """
    adjudicated = adjudicated_arc(store, verb=verb, participants=participants)
    actual = adjudicated["actual"]
    if actual is None:
        return {
            "verb": verb,
            "participants": list(participants),
            "claimed": claimed_arc_index,
            "actual": None,
            "gap": None,
            "flagged": False,
            "disputed": False,
            "majority_share": 0.0,
            "note": adjudicated["note"],
        }
    gap = abs(claimed_arc_index - actual)
    return {
        "verb": verb,
        "participants": list(participants),
        "claimed": claimed_arc_index,
        "actual": actual,
        "gap": gap,
        "direction": "early" if claimed_arc_index < actual else "late",
        "flagged": gap >= threshold,
        "disputed": adjudicated["disputed"],
        "majority_share": adjudicated["majority_share"],
        "note": "",
    }


def walk_monotonicity(
    beats: Sequence[dict[str, Any]],
    *,
    threshold: int = 2,
    flashback: Sequence[int] = (),
) -> list[dict[str, Any]]:
    """The per-beat check composed over a beat sequence, in script order.

    Each beat carries the arc it is *about* (``arc_index``). A script that walks
    forward through the story should not jump *back* more than ``threshold``
    arcs and call it the present: that is either an anachronism or a legitimate
    flashback/recap, and ``flashback`` names the beats that are the latter (by
    index), so the check *reports* the jump rather than assuming it is an error.
    A flag, not a reject.
    """
    exempt = set(flashback)
    flags: list[dict[str, Any]] = []
    for index in range(1, len(beats)):
        previous = beats[index - 1].get("arc_index")
        current = beats[index].get("arc_index")
        if previous is None or current is None:
            continue
        jump = previous - current
        if jump >= threshold:
            flags.append(
                {
                    "index": index,
                    "from_arc": previous,
                    "to_arc": current,
                    "jump": jump,
                    "flashback": index in exempt,
                }
            )
    return flags


def knowledge_frontier(
    store: FactStore, subject: str, upto_arc_index: int
) -> list[dict[str, Any]]:
    """Everything ``subject`` took part in -- as actor or object -- at or before
    arc ``upto_arc_index``: what the subject could plausibly have known at the
    start of that arc. A plain prefix read of the time axis, in story order.

    This is the model-free answer to "what did X know". It is *not* a
    belief-state check ("did X know the reveal?"); it is the set of events that
    preceded the moment, and deciding which of those a line may reference is the
    writer's job, not this lookup's.
    """
    rows = store.connection.execute(
        "SELECT subject_name, verb, object_name, arc_index, arc_key"
        " FROM events WHERE arc_index IS NOT NULL AND arc_index <= ?"
        "   AND (subject_name = ? COLLATE NOCASE"
        "        OR object_name = ? COLLATE NOCASE)"
        " ORDER BY arc_index, time_rank",
        (upto_arc_index, subject, subject),
    ).fetchall()
    return [dict(row) for row in rows]


def triage_filings(store: FactStore, *, min_gap: int = 2) -> dict[str, Any]:
    """The cross-arc filings, triaged into classes and a gap histogram.

    This is the "residual disposition" the scoping council asked for: what the
    cross-page disagreements actually *are*, so a consumer knows which are worth
    consuming and which are the wiki's own boundary straddles or coarse-verb
    keying. Measured against the live store, not asserted.
    """
    report = gate.cross_page_agreement(store)
    disagreements = report["disagreements"]
    names = report["arc_names"]

    classes = {"adjacent": 0, "state_verb": 0, "interaction_verb": 0}
    premature: list[dict[str, Any]] = []
    delayed: list[dict[str, Any]] = []
    histogram: Counter = Counter()

    for filing in disagreements:
        histogram[filing["arc_span"]] += 1
        if filing["arc_span"] == 1:
            classes["adjacent"] += 1
            continue
        if filing["verb"].lower() in _STATE_VERBS:
            classes["state_verb"] += 1
            continue
        classes["interaction_verb"] += 1

        adjudicated = adjudicated_arc(
            store, verb=filing["verb"], participants=filing["participants"]
        )
        if adjudicated["actual"] is None:
            continue
        actual = adjudicated["actual"]
        case = _filing_case(filing, adjudicated, names)
        if actual - min(filing["arcs"]) >= min_gap:
            premature.append(case)
        if max(filing["arcs"]) - actual >= min_gap:
            delayed.append(_filing_case(filing, adjudicated, names, direction="late"))

    return {
        "total": len(disagreements),
        "classes": classes,
        "premature": premature,
        "delayed": delayed,
        "anachronism_core": len(premature) + len(delayed),
        "span_histogram": dict(sorted(histogram.items())),
        "arc_names": names,
    }


def _filing_case(
    filing: dict, adjudicated: dict, names: dict, direction: str = "early"
) -> dict[str, Any]:
    """A gold-set case: a filing's out-of-order arc versus the adjudicated one.

    An ``early`` filing is premature (stated earlier than where the event
    actually sits); a ``late`` one is delayed. Both are a line referencing an
    event out of order, which is what the continuity-check exists to flag.
    """
    arcs = filing["arcs"]
    claimed = min(arcs) if direction == "early" else max(arcs)
    actual = adjudicated["actual"]
    return {
        "verb": filing["verb"],
        "participants": filing["participants"],
        "claimed_arc_index": claimed,
        "claimed_arc": names.get(claimed, str(claimed)),
        "actual_arc_index": actual,
        "actual_arc": names.get(actual, str(actual)),
        "gap": abs(claimed - actual),
        "direction": direction,
        "majority_share": adjudicated["majority_share"],
    }


def run_gold(store: FactStore, cases: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Check a frozen gold set: every case's claimed arc must sit out of order
    with the adjudicated arc by at least its stated gap. A case passes when the
    live store reproduces the adjudicated arc it was frozen against, so a
    re-index that silently moved an event is caught. Exits the door with a
    failure count, not a pass: a gold set is a guard, not a score.
    """
    results = []
    for case in cases:
        gap = beat_gap(
            store,
            verb=case["verb"],
            participants=case["participants"],
            claimed_arc_index=case["claimed_arc_index"],
            threshold=case.get("min_gap", case.get("gap", 2)),
        )
        held = gap["actual"] == case["actual_arc_index"]
        results.append(
            {
                "verb": case["verb"],
                "participants": case["participants"],
                "direction": case.get("direction", ""),
                "expected_actual": case["actual_arc_index"],
                "held": held,
                "gap": gap["gap"],
            }
        )
    held = sum(1 for row in results if row["held"])
    return {"total": len(results), "held": held, "broken": len(results) - held, "cases": results}
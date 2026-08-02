"""Scoring retrieval against a gold set.

Nothing in the previous project could be verified. Its claims about accuracy —
"this is where accuracy is won or lost", in a docstring above code that raised
on import — were untestable, and so was any change anyone made to it.

The point of this module is not the score. It is that a change to chunking,
fusion or reranking now produces a number that moves, in a direction that can be
argued about.

Scoring is deliberately blunt: did the retrieval surface the page a human would
have opened, and does the returned text contain the fact that answers the
question? Both are checkable without a judge model, which keeps the suite fast
and its verdicts stable.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings

GOLD_DIR = Path(__file__).parent


def load_gold(series: str) -> dict[str, Any]:
    path = GOLD_DIR / f"gold_{series}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No gold set for {series!r}. Expected {path}. "
            "A series without one cannot be measured, only hoped about."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _hit_docs(question: dict[str, Any], titles: list[str]) -> bool:
    """Did retrieval surface at least one page a human would have opened?"""
    expected = question.get("expect_docs") or []
    if not expected:
        return True
    return any(doc in titles for doc in expected)


def _hit_text(question: dict[str, Any], haystack: str) -> bool:
    expected = question.get("expect_text") or []
    if not expected:
        return True
    lowered = haystack.lower()
    return all(fragment.lower() in lowered for fragment in expected)


def evaluate(
    paths: SeriesPaths, settings: Settings | None = None, top_k: int = 8
) -> dict[str, Any]:
    """Run every gold question and score it."""
    from scriptengine.retrieve.hybrid import HybridRetriever

    settings = settings or get_settings()
    gold = load_gold(paths.name)
    results: list[dict[str, Any]] = []

    handlers = {
        "narrative": _evaluate_narrative,
        "roster": _evaluate_roster,
        "sourcing": _evaluate_sourcing,
    }

    with HybridRetriever(paths, settings) as retriever:
        for question in gold["questions"]:
            started = time.monotonic()

            handler = handlers.get(question["kind"])
            if handler is not None:
                outcome = handler(paths, question)
            else:
                outcome = _evaluate_retrieval(retriever, question, top_k)

            outcome["id"] = question["id"]
            outcome["kind"] = question["kind"]
            outcome["question"] = question["question"]
            outcome["seconds"] = round(time.monotonic() - started, 2)
            results.append(outcome)

        retriever.release_models()

    by_kind: dict[str, list[bool]] = defaultdict(list)
    for outcome in results:
        by_kind[outcome["kind"]].append(outcome["passed"])

    passed = sum(1 for outcome in results if outcome["passed"])
    return {
        "series": paths.name,
        "questions": len(results),
        "passed": passed,
        "score": round(passed / len(results), 3) if results else 0.0,
        "by_kind": {
            kind: {
                "passed": sum(outcomes),
                "total": len(outcomes),
                "score": round(sum(outcomes) / len(outcomes), 3),
            }
            for kind, outcomes in sorted(by_kind.items())
        },
        "results": results,
    }


def _evaluate_retrieval(
    retriever: Any, question: dict[str, Any], top_k: int
) -> dict[str, Any]:
    result = retriever.search(question["question"], top_k=top_k)

    titles = [passage.doc_title for passage in result.passages]
    # Facts count as retrieved text: a question about a character's grade is
    # answered by the infobox, and requiring it to also appear in prose would
    # penalise the store for being exact.
    haystack = " ".join(
        [passage.text for passage in result.passages]
        + [f"{fact['label']} {fact['value']}" for fact in result.facts]
    )

    # Relations count too. "Which students attend Kyoto Jujutsu High?" is
    # answered by the edge `Aoi Todo -affiliation-> Kyoto ...`, which is
    # returned to the caller; scoring only passages would mark a correct graph
    # answer wrong.
    reachable = (
        titles
        + [fact["entity"] for fact in result.facts]
        + [relation["source"] for relation in result.relations]
        + [relation["target"] for relation in result.relations]
    )
    docs_ok = _hit_docs(question, reachable)
    text_ok = _hit_text(question, haystack)

    return {
        "passed": docs_ok and text_ok,
        "docs_ok": docs_ok,
        "text_ok": text_ok,
        "retrieved": titles[:5],
        "entities": result.entities[:4],
    }


def _evaluate_narrative(paths: SeriesPaths, question: dict[str, Any]) -> dict[str, Any]:
    from scriptengine.retrieve.narrative import NarrativeRetriever

    with NarrativeRetriever(paths) as retriever:
        narrative = retriever.timeline(question["question"], max_beats=40)

    wanted = question.get("expect_ordered_beats", 1)
    enough = len(narrative.beats) >= wanted

    ordered = [beat.order for beat in narrative.beats]
    in_order = ordered == sorted(ordered)

    times_ok = True
    if question.get("expect_times"):
        times_ok = any(beat.time for beat in narrative.beats)

    return {
        "passed": enough and in_order and times_ok,
        "beats": len(narrative.beats),
        "expected_beats": wanted,
        "in_order": in_order,
        "has_times": any(beat.time for beat in narrative.beats),
        "participants": narrative.participants[:5],
    }


def _evaluate_roster(paths: SeriesPaths, question: dict[str, Any]) -> dict[str, Any]:
    """Did the topic come back as the set it names?

    Scored on membership rather than on ranking, because a roster is only right
    when it is complete: "Every Rank of Curse" returning eight of twenty-two
    curses is a different script, not a slightly worse one.
    """
    from scriptengine.retrieve.roster import build_roster

    roster = build_roster(paths, question["question"])
    names = [member.name for member in roster.members]

    members_ok = all(
        expected in names for expected in question.get("expect_members") or []
    )
    groups_ok = all(
        expected in roster.groups for expected in question.get("expect_groups") or []
    )
    enough = len(roster.members) >= question.get("expect_min_members", 1)

    return {
        "passed": members_ok and groups_ok and enough,
        "subject": roster.subject,
        "basis": roster.basis,
        "members": len(roster.members),
        "groups": roster.groups[:6],
        "missing": [
            expected
            for expected in question.get("expect_members") or []
            if expected not in names
        ],
    }


def _evaluate_sourcing(paths: SeriesPaths, question: dict[str, Any]) -> dict[str, Any]:
    """Can a script tag every block of this topic with a chapter and episode?

    The regression guard for the failure that has already happened once here:
    references captured as structured objects and then dropped from every
    downstream text, so the scripts had nothing to cite and no number moved.
    """
    from scriptengine.retrieve.narrative import NarrativeRetriever

    with NarrativeRetriever(paths) as retriever:
        narrative = retriever.timeline(question["question"], max_beats=40)

    if not narrative.beats:
        return {"passed": False, "beats": 0, "sourced": 0}

    sourced = sum(1 for beat in narrative.beats if beat.source_span)
    ratio = sourced / len(narrative.beats)
    with_episode = sum(1 for beat in narrative.beats if "Episode" in beat.source_span)

    return {
        "passed": ratio >= question.get("expect_sourced_ratio", 0.9),
        "beats": len(narrative.beats),
        "sourced": sourced,
        "ratio": round(ratio, 3),
        "with_episode": with_episode,
        "subject": narrative.subject,
    }


def write_report(paths: SeriesPaths, report: dict[str, Any]) -> str:
    paths.audit.mkdir(parents=True, exist_ok=True)
    destination = paths.audit / "eval.json"
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return str(destination)

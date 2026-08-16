"""Rules the gold sets themselves have to obey.

`expect_any_text` was added for a real case: Akainu and Sakazuki are one
marine, and no passage uses both names, so requiring both failed a correct
answer. It is also exactly the kind of permissive primitive that can absorb a
future subject-resolution bug instead of catching it: listing two *different*
entities as interchangeable turns "the engine picked the wrong one" into a pass.

These tests exist so that use has to be argued for.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

GOLD = sorted(Path("scriptengine/eval").glob("gold_*.json"))


def _cases():
    for path in GOLD:
        data = json.loads(path.read_text(encoding="utf-8"))
        for question in data["questions"]:
            yield path.name, question


@pytest.mark.skipif(not GOLD, reason="gold sets not present")
def test_any_of_requires_a_justification():
    """A permissive assertion has to say why it is permissive."""
    missing = [
        f"{name}:{question['id']}"
        for name, question in _cases()
        if question.get("expect_any_text") and not question.get("note")
    ]
    assert not missing, f"expect_any_text without a note: {missing}"


@pytest.mark.skipif(not GOLD, reason="gold sets not present")
def test_any_of_lists_one_entity_not_several():
    """The alternatives must be names for the same thing.

    Two names for one marine is a synonym. Two marines is a subject-resolution
    bug wearing a permissive eval as camouflage, and this is the line between
    them: the alternatives have to share the case's own subject, or say in the
    note that they are aliases of each other.
    """
    suspect = []
    for name, question in _cases():
        alternatives = question.get("expect_any_text") or []
        if len(alternatives) < 2:
            continue
        note = (question.get("note") or "").lower()
        claims_alias = any(
            word in note for word in ("same", "alias", "also known", "one entity")
        )
        if not claims_alias:
            suspect.append(f"{name}:{question['id']} {alternatives}")
    assert not suspect, (
        "expect_any_text must state that the alternatives name one entity: "
        f"{suspect}"
    )


@pytest.mark.skipif(not GOLD, reason="gold sets not present")
def test_every_case_still_asserts_something():
    """A case that expects nothing passes forever and measures nothing."""
    empty = [
        f"{name}:{question['id']}"
        for name, question in _cases()
        if not any(
            question.get(key)
            for key in (
                "expect_text", "expect_any_text", "expect_docs", "expect_members",
                "expect_absent", "expect_groups", "expect_min_members",
                "expect_sourced_ratio", "expect_mode",
            )
        )
    ]
    assert not empty, f"gold cases asserting nothing: {empty}"

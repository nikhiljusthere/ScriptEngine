"""The pass that reads chapter and episode pages instead of character pages.

Written after the pass ran a whole wiki and stored nothing. 904 passages, 927
windows, **0 added and 0 failed**, which reads as "Chainsaw Man's chapters name
no abilities" and was in fact a pass that could not have stored a row on any
wiki: it reused `abilities.parse_response`, which builds fresh rows holding
`name`, `kind` and `reason`, so the `owner` it then required was always the
empty string and every candidate fell out of `if not name or not owner`.

Nothing here needs a model. The guards are what decide whether a narrative row
is worth storing, and each of them is a plain function over a passage the test
supplies.
"""

from __future__ import annotations

from typing import cast

from scriptengine.ingest import abilities as A
from scriptengine.ingest import narrative_abilities as N
from scriptengine.llm.client import LLMClient
from scriptengine.stores.facts import FactStore


class TestOwnerSurvivesParsing:
    """The regression: the field the pass keys on must reach the pass."""

    def test_the_owner_is_carried_through(self):
        found = A.parse_response(
            '{"abilities": [{"name": "Blood Chainsaw", "owner": "Power",'
            ' "kind": "technique", "reason": "shown cutting"}]}',
            keep=("owner",),
        )
        assert found == [
            {
                "name": "Blood Chainsaw",
                "kind": "technique",
                "reason": "shown cutting",
                "owner": "Power",
            }
        ]

    def test_the_ability_pass_is_unchanged_by_it(self):
        """`keep` is opt-in: the character-page pass must see the same rows."""
        answer = (
            '{"abilities": [{"name": "Godspeed", "owner": "Killua",'
            ' "kind": "technique", "reason": "electrified body"}]}'
        )
        assert A.parse_response(answer) == [
            {"name": "Godspeed", "kind": "technique", "reason": "electrified body"}
        ]

    def test_a_missing_owner_is_empty_rather_than_absent(self):
        """The pass tests `not owner`, so the key has to exist to be tested."""
        found = A.parse_response(
            '{"abilities": [{"name": "Godspeed", "kind": "technique"}]}',
            keep=("owner",),
        )
        assert found[0]["owner"] == ""

    def test_the_pass_asks_for_the_field_it_requires(self):
        """The prompt asks for `owner` and the guard rejects a row without one.

        Asserted against the module rather than a fixture because the failure
        this catches is silent: a parser that drops the field costs no error,
        no failure count and no row.
        """
        assert '"owner"' in N._TEMPLATE


class _Client:
    """A model that returns one canned answer, so the guards can be measured."""

    def __init__(self, answer: str):
        self.answer = answer
        self.calls = 0

    def complete(self, prompt, system=None, temperature=0.0, max_tokens=None):
        self.calls += 1
        return self.answer


PASSAGE = (
    "Power laughs as she points towards Makima, with Blood Chainsaw suddenly "
    "pushing out from within the bodies of her and the Public Safety members. "
    "Power yells out that she is the strongest as a bloodied Makima uses "
    "Angel's ability, creating a sword from 100 years of her lifespan."
)


def _extract(answer, characters, passage=PASSAGE):
    # Duck-typed stand-in for the LLM; the guards under test never touch the
    # parts of the client the fake does not implement.
    return N.extract_from_passage(
        cast(LLMClient, _Client(answer)), "csm", "Chapter 90", "Summary",
        passage, characters, set(),
    )


class TestGuards:
    def test_a_named_ability_with_a_named_owner_is_stored(self):
        found = _extract(
            '{"abilities": [{"name": "Blood Chainsaw", "owner": "Power",'
            ' "kind": "technique", "reason": "pushed out from bodies"}]}',
            {"power": "Power"},
        )
        assert [(owner, row["name"]) for owner, row in found] == [
            ("Power", "Blood Chainsaw")
        ]

    def test_provenance_names_the_page_it_was_read_from(self):
        """A narrative row has to stay tellable from an ability-list row."""
        found = _extract(
            '{"abilities": [{"name": "Blood Chainsaw", "owner": "Power",'
            ' "kind": "technique"}]}',
            {"power": "Power"},
        )
        assert found[0][1]["section"] == "Chapter 90 / Summary"

    def test_an_owner_the_wiki_does_not_type_as_a_character_is_dropped(self):
        found = _extract(
            '{"abilities": [{"name": "Blood Chainsaw", "owner": "Public Safety",'
            ' "kind": "technique"}]}',
            {"power": "Power"},
        )
        assert found == []

    def test_an_owner_the_passage_does_not_name_is_dropped(self):
        """"Everyone knows whose that is" must not get through."""
        found = _extract(
            '{"abilities": [{"name": "Blood Chainsaw", "owner": "Denji",'
            ' "kind": "technique"}]}',
            {"power": "Power", "denji": "Denji"},
        )
        assert found == []

    def test_an_ability_the_passage_does_not_name_is_dropped(self):
        found = _extract(
            '{"abilities": [{"name": "Blood Sword", "owner": "Power",'
            ' "kind": "technique"}]}',
            {"power": "Power"},
        )
        assert found == []

    def test_a_row_with_no_owner_at_all_is_dropped(self):
        found = _extract(
            '{"abilities": [{"name": "Blood Chainsaw", "kind": "technique"}]}',
            {"power": "Power"},
        )
        assert found == []

    def test_naming_nothing_is_a_valid_answer(self):
        assert _extract('{"abilities": []}', {"power": "Power"}) == []


class TestDeclaration:
    def test_off_until_a_series_declares_which_pages_to_read(self):
        """No declaration means no passages, not every page on the wiki."""

        class _Store:
            connection = None

        assert N.passages(cast(FactStore, _Store()), {}) == []
        assert N.passages(
            cast(FactStore, _Store()), {"ability_narrative_types": []}
        ) == []

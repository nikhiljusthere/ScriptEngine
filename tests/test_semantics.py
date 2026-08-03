"""Tests for what an entity is, as distinct from where the wiki filed it.

The failure these exist for: asked for the members of the Galactic Frieza Army,
the engine returned 230 pages — 121 characters, but also 37 races, 24
techniques, 18 planets and 6 battles. A planet is not a member of an army.
"""

from __future__ import annotations

import pytest

from scriptengine.retrieve import semantics
from scriptengine.retrieve.semantics import (
    expected_type,
    type_from_class,
    type_from_page_type,
)


class TestTypeFromPageType:
    @pytest.mark.parametrize(
        "page_type,expected",
        [
            # One vocabulary out of four wikis' spellings, matched on the tokens
            # inside the id rather than on a table of ids.
            ("character", semantics.CHARACTER),
            ("char_box", semantics.CHARACTER),
            ("hunterpedia_character", semantics.CHARACTER),
            ("bleach_wiki_character_arrancar", semantics.CHARACTER),
            ("race_infobox2", semantics.RACE),
            ("planet", semantics.LOCATION),
            ("island_box", semantics.LOCATION),
            ("faction", semantics.ORGANIZATION),
            ("crew_box", semantics.ORGANIZATION),
            ("bleach_wiki_zanpakut_technique", semantics.TECHNIQUE),
            ("weapon_box", semantics.ITEM),
            ("conflict", semantics.EVENT),
            ("bleach_wiki_episode", semantics.MEDIA),
            ("volume_box", semantics.MEDIA),
            ("", semantics.UNKNOWN),
            ("something_nobody_has_seen", semantics.UNKNOWN),
        ],
    )
    def test_a_wikis_own_infobox_name_folds_into_the_vocabulary(self, page_type, expected):
        assert type_from_page_type(page_type) == expected

    def test_a_series_can_declare_its_own(self):
        declared = {"semantic_types": {"weird_box": "item"}}
        assert type_from_page_type("weird_box", declared) == semantics.ITEM


class TestTypeFromClass:
    def test_it_separates_a_power_up_from_a_transformation(self):
        """Both sit in `Transformations`; only the `Class` field disagrees."""
        assert type_from_class("Power Up") == semantics.POWER_UP
        assert type_from_class("Transformation") == semantics.TRANSFORMATION

    def test_naming_both_reads_as_the_stronger(self):
        assert type_from_class("Power Up Transformation") == semantics.TRANSFORMATION
        assert type_from_class("Transformation/Power Up") == semantics.TRANSFORMATION


class TestExpectedType:
    def test_the_majority_is_what_the_set_is_made_of(self):
        types = {f"c{index}": semantics.CHARACTER for index in range(8)}
        types["p1"] = semantics.LOCATION
        types["r1"] = semantics.RACE
        assert expected_type(list(types), types) == semantics.CHARACTER

    def test_a_set_with_no_majority_is_left_alone(self):
        """Better to return a mixed set than to guess which half is wrong."""
        types = {"a": semantics.CHARACTER, "b": semantics.ITEM, "c": semantics.EVENT}
        assert expected_type(list(types), types) == semantics.UNKNOWN

    def test_unclassified_members_do_not_vote(self):
        types = {"a": semantics.CHARACTER, "b": semantics.UNKNOWN, "c": semantics.UNKNOWN}
        assert expected_type(list(types), types) == semantics.CHARACTER


# `_disagrees` lives in roster.py and is tested beside it, in
# tests/test_roster_validation.py — importing it here made this module
# uncollectable at any commit before roster.py grew the function.

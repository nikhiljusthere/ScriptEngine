"""Classing an ability by what the wiki says it *is*, not where it was filed.

`Every technique of Yuji Itadori` returned 16 names for an answer of 8. The
five the reader wanted were all there; the noise was `Manji Kick`,
`Taido Martial Arts`, `Knee Release`, `Divergent Fist` and `Black Flash`.

No rule about *sections* can remove them, and the corpus says so: `Black Flash`
is filed under `Cursed Energy` on four of the eight pages naming it,
`Physical Prowess` on two, `Overview` and `Abilities and Powers` on one each,
and `Reverse Cursed Technique` under four different headings across thirteen.
Where an ability is filed is an editor's decision made once per page. What it
*is* is a property of the ability, and the wiki states it on the ability's own
page: `type = Innate Technique` on `Shrine`, `Taijutsu` on `Divergent Fist`.

The rule these tests pin down is that rejection needs **positive** evidence.
Most abilities have no page at all -- `Dismantle`, `Cleave`, `Hometown Domain`
and `New Shadow Style: Simple Domain` have none anywhere on the Jujutsu Kaisen
wiki, and four of the eight wikis give abilities no pages ever -- so a filter
that required a class would delete the majority of every real answer.
"""

from __future__ import annotations

import pytest

from scriptengine.retrieve import roster as R
from scriptengine.stores.facts import FactStore

OVERRIDES = {
    "ability_class": {
        "field": "type",
        "map": {
            "Innate Technique": "cursed_technique",
            "Extension Technique": "cursed_technique",
            "Anti-Domain Technique": "cursed_technique",
            "Taijutsu": "physical",
        },
        "asks": [
            {"phrases": ["cursed technique", "technique"],
             "keep": ["cursed_technique"]},
        ],
    }
}


@pytest.fixture()
def store(tmp_path):
    with FactStore(tmp_path / "facts.db") as opened:
        opened.connection.executescript(
            "CREATE TABLE IF NOT EXISTS nodes"
            " (id INTEGER PRIMARY KEY, name TEXT, label TEXT,"
            "  document_id INTEGER, is_resolved INTEGER);"
            "CREATE TABLE IF NOT EXISTS facts"
            " (id INTEGER PRIMARY KEY, node_id INTEGER, key TEXT,"
            "  label TEXT, value TEXT, citation TEXT);"
        )
        rows = [
            ("Shrine", "Innate Technique"),
            ("Convergence", "Extension Technique"),
            ("Divergent Fist", "Taijutsu"),
            ("Black Flash", "Taijutsu"),
            # One page can name two, and the wiki writes them on one line.
            ("Simple Domain", "Anti-Domain Technique\nBarrier Technique"),
        ]
        for index, (name, value) in enumerate(rows, start=1):
            opened.connection.execute(
                "INSERT INTO nodes (id, name) VALUES (?, ?)", (index, name)
            )
            opened.connection.execute(
                "INSERT INTO facts (node_id, key, value) VALUES (?, 'type', ?)",
                (index, value),
            )
        # A prose-only ability: a node with no page and therefore no infobox.
        opened.connection.execute(
            "INSERT INTO nodes (id, name) VALUES (99, 'Dismantle')"
        )
        opened.connection.commit()
        yield opened


class TestReadingTheClass:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Shrine", "cursed_technique"),
            ("Convergence", "cursed_technique"),
            ("Divergent Fist", "physical"),
            ("Black Flash", "physical"),
        ],
    )
    def test_the_infobox_decides(self, store, name, expected):
        assert R.ability_class(store, name, OVERRIDES) == expected

    def test_an_ability_with_no_page_has_no_class(self, store):
        """And that is the common case, not an error."""
        assert R.ability_class(store, "Dismantle", OVERRIDES) == ""
        assert R.ability_class(store, "Hometown Domain", OVERRIDES) == ""

    def test_the_first_recognised_value_wins_on_a_multi_valued_field(self, store):
        """`Simple Domain` is `Anti-Domain Technique` *and* `Barrier Technique`."""
        assert R.ability_class(store, "Simple Domain", OVERRIDES) == "cursed_technique"

    def test_a_series_declaring_nothing_classes_nothing(self, store):
        assert R.ability_class(store, "Shrine", {}) == ""


class TestWhatTheQuestionAsks:
    def test_a_declared_phrase_selects_its_classes(self):
        assert R.wanted_classes(
            "Every technique of Yuji Itadori", OVERRIDES
        ) == frozenset({"cursed_technique"})

    def test_an_undeclared_question_filters_nothing(self):
        """Empty means "no opinion", which must not read as "keep nothing"."""
        assert R.wanted_classes("Every ability of Yuji Itadori", OVERRIDES) == frozenset()

    def test_the_longest_phrase_decides(self):
        """So `cursed technique` can be narrower than `technique`."""
        overrides = {
            "ability_class": {
                "field": "type",
                "map": {"Innate Technique": "cursed_technique"},
                "asks": [
                    {"phrases": ["technique"], "keep": ["wide"]},
                    {"phrases": ["cursed technique"], "keep": ["narrow"]},
                ],
            }
        }
        assert R.wanted_classes("Every cursed technique of X", overrides) == frozenset(
            {"narrow"}
        )


class TestRejectionNeedsPositiveEvidence:
    def test_a_class_outside_the_question_is_rejected(self, store):
        kept, rejected = R.drop_off_class(
            store, ["Shrine", "Divergent Fist", "Black Flash"],
            "Every technique of Yuji Itadori", OVERRIDES,
        )
        assert kept == ["Shrine"]
        assert {r["name"] for r in rejected} == {"Divergent Fist", "Black Flash"}
        assert {r["rule"] for r in rejected} == {"class"}

    def test_an_unclassified_member_is_kept(self, store):
        """The wiki said nothing, so nothing has been shown about it."""
        kept, rejected = R.drop_off_class(
            store, ["Shrine", "Dismantle", "Hometown Domain"],
            "Every technique of Yuji Itadori", OVERRIDES,
        )
        assert kept == ["Shrine", "Dismantle", "Hometown Domain"]
        assert rejected == []

    def test_a_question_asking_for_no_class_is_left_alone(self, store):
        """`Every ability of X` keeps Divergent Fist and Black Flash.

        Both really are Yuji's abilities. They are not Cursed Techniques, which
        is a narrower claim, and only the narrower question may drop them.
        """
        names = ["Shrine", "Divergent Fist", "Black Flash"]
        kept, rejected = R.drop_off_class(
            store, names, "Every ability of Yuji Itadori", OVERRIDES
        )
        assert kept == names
        assert rejected == []

    def test_it_never_empties_a_non_empty_set(self, store):
        """A drifted declaration must degrade to too-broad, never to nothing.

        The same guarantee `apply_constraints` gives, for the same reason: a
        list that is visibly too wide is usable and a blank one is not.
        """
        kept, rejected = R.drop_off_class(
            store, ["Divergent Fist", "Black Flash"],
            "Every technique of Yuji Itadori", OVERRIDES,
        )
        assert kept == ["Divergent Fist", "Black Flash"]
        assert rejected == []

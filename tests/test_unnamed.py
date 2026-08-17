"""Mentioned on a page is not the same as named by it.

`Every cursed technique of Sukuna` returned six names his page uses in passing:
`Metamorphosis`, `Enchain`, `Enma`, `Totality`, `Incarnation` and
`Cursed Energy Reinforcement`. No field rejects any of them -- none has a page
of its own, so the `type` and `user` fields are silent -- and the class and
owner gates therefore pass them through.

What separates them is the page's own formatting, captured at index time into
the `emphasis` table. A member survives if the wiki gave it a page *or* the
subject's page names it in bold.

Both halves matter. `Cursed Technique Lapse - Maximum Cursed Energy Output:
Blue` has no page anywhere and is bolded on Gojo's; a technique read off its
own page may never appear in bold on the character's.
"""

from __future__ import annotations

import pytest

from scriptengine.retrieve.roster import drop_unnamed
from scriptengine.stores.facts import FactStore

OVERRIDES = {
    "ability_class": {
        "field": "type",
        "map": {"Innate Technique": "cursed_technique"},
        "asks": [{"phrases": ["cursed technique", "technique"],
                  "keep": ["cursed_technique"]}],
    }
}

ASKS = "Every cursed technique of Sukuna"
DOES_NOT_ASK = "Every ability of Sukuna"


@pytest.fixture()
def store(tmp_path):
    with FactStore(tmp_path / "facts.db") as opened:
        opened.connection.executescript(
            "CREATE TABLE IF NOT EXISTS documents"
            " (id INTEGER PRIMARY KEY, title TEXT, page_type TEXT);"
        )
        opened.ensure_emphasis()
        # Sukuna's page, and one technique that has a page of its own.
        opened.connection.execute(
            "INSERT INTO documents (id, title, page_type) VALUES (1, 'Sukuna', 'character')"
        )
        opened.connection.execute(
            "INSERT INTO documents (id, title, page_type)"
            " VALUES (2, 'Malevolent Shrine', 'technique')"
        )
        # What his page names in bold. `Dismantle` has no page of its own.
        opened.add_emphasis(1, ["Dismantle", "Cleave", "Malevolent Shrine"])
        opened.connection.commit()
        yield opened


class TestKeeping:
    def test_a_name_the_page_bolds_survives_without_a_page(self, store):
        """`Dismantle` has no page anywhere on the wiki."""
        kept, rejected = drop_unnamed(
            store, ["Dismantle", "Metamorphosis"], "Sukuna", ASKS, OVERRIDES
        )
        assert kept == ["Dismantle"]
        assert [r["name"] for r in rejected] == ["Metamorphosis"]

    def test_a_page_of_its_own_survives_without_being_bolded(self, store):
        """The other half of the rule, and it covers a different blind spot."""
        kept, _ = drop_unnamed(
            store, ["Malevolent Shrine", "Enchain"], "Sukuna", ASKS, OVERRIDES
        )
        assert kept == ["Malevolent Shrine"]

    def test_the_reason_says_which_page_was_consulted(self, store):
        _kept, rejected = drop_unnamed(
            store, ["Cleave", "Totality"], "Sukuna", ASKS, OVERRIDES
        )
        assert "Sukuna" in rejected[0]["reason"]
        assert rejected[0]["rule"] == "unnamed"


class TestWhenItDoesNotRun:
    def test_a_question_that_asks_for_no_class_is_left_alone(self, store):
        """`Every ability of X` keeps `Immense Strength`, which is nobody's
        named technique and is still gold there."""
        names = ["Dismantle", "Metamorphosis", "Enchain"]
        assert drop_unnamed(store, names, "Sukuna", DOES_NOT_ASK, OVERRIDES) == (names, [])

    def test_an_unbuilt_emphasis_table_filters_nothing(self, store):
        """A store indexed before this existed has no rows, and every member
        would otherwise fail the second half at once."""
        names = ["Dismantle", "Metamorphosis"]
        assert drop_unnamed(store, names, "Nobody At All", ASKS, OVERRIDES) == (names, [])

    def test_no_subject_means_no_opinion(self, store):
        names = ["Metamorphosis"]
        assert drop_unnamed(store, names, "", ASKS, OVERRIDES) == (names, [])

    def test_it_never_empties_a_non_empty_set(self, store):
        """The guarantee `apply_constraints` gives, for the same reason."""
        names = ["Metamorphosis", "Enchain", "Enma"]
        assert drop_unnamed(store, names, "Sukuna", ASKS, OVERRIDES) == (names, [])

"""Single combat, decided by the wiki's side fields rather than the page title.

`How many 1v1 battles did Yuji Itadori have with named characters` returned 24
for an answer of 9 -- every battle he appears in, team fights and faction
brawls included. All nine gold were among them, so nothing was missing; the
question's own restriction was simply not being read.

Every battle page carries `side1` and `side2`, and a duel is exactly one
resolvable character on each. Measured over the 24, that keeps precisely the
nine gold and drops precisely the fifteen others.

**The title cannot be parsed instead**, and that is the point these tests pin
down. `Satoru Gojo vs. Sukuna: First Fight` and
`Satoru Gojo vs. Toji Fushiguro: Rematch` are duels whose titles carry a
qualifier; `Megumi Fushiguro vs. Reggie Star's Group` and
`Satoru Gojo vs. Mahito's Group` read as duels and hold four fighters in the
field. A title rule scores identically on the 24 and misclassifies all four.
"""

from __future__ import annotations

import pytest

from scriptengine.retrieve.roster import asks_one_on_one, side_fighters
from scriptengine.stores.facts import FactStore

CHARACTERS = (
    "Yuji Itadori", "Aoi Todo", "Megumi Fushiguro", "Nobara Kugisaki",
    "Maki Zenin", "Nobuaki Zenin", "Sukuna", "Mahito", "Panda", "Ko-Guy",
    "Haba", "Hanyu", "Hana Kurusu",
)


@pytest.fixture()
def store(tmp_path):
    with FactStore(tmp_path / "facts.db") as opened:
        opened.connection.executescript(
            "CREATE TABLE IF NOT EXISTS documents"
            " (id INTEGER PRIMARY KEY, title TEXT, page_type TEXT);"
        )
        for index, name in enumerate(CHARACTERS, start=1):
            opened.connection.execute(
                "INSERT INTO documents (id, title, page_type) VALUES (?, ?, ?)",
                (index, name, "character"),
            )
        # A cursed spirit species page, not a character. `Finger Bearer` is the
        # only extra that survives an arity-only rule: the fight really is one
        # against one, and the question asks for a named *character*.
        opened.connection.execute(
            "INSERT INTO documents (id, title, page_type) VALUES (99, ?, ?)",
            ("Finger Bearer", "species"),
        )
        opened.connection.commit()
        yield opened


class TestAsksOneOnOne:
    @pytest.mark.parametrize(
        "query",
        [
            "How many 1v1 battles did Yuji Itadori have with named characters",
            "every 1 v 1 fight of Sukuna",
            "one-on-one battles of Gojo",
            "one on one duels",
        ],
    )
    def test_recognised(self, query):
        assert asks_one_on_one(query) is True

    @pytest.mark.parametrize(
        "query", ["Every battle of Yuji Itadori", "Who did Sukuna fight?", ""]
    )
    def test_not_claimed_when_unasked(self, query):
        """`Every battle of X` must keep its team fights."""
        assert asks_one_on_one(query) is False


class TestSideFighters:
    def test_one_fighter_leaves_nothing_over(self, store):
        assert side_fighters(store, "Yuji Itadori") == (["Yuji Itadori"], "")

    def test_a_space_joined_side_resolves_to_two(self, store):
        """The field is not delimited consistently -- the same wiki writes
        `'Yuji Itadori\\nMegumi Fushiguro'` and `'Yuji Itadori Aoi Todo'` --
        so names are matched against real titles, never split on a character."""
        found, leftover = side_fighters(store, "Yuji Itadori Aoi Todo")
        assert sorted(found) == ["Aoi Todo", "Yuji Itadori"]
        assert leftover == ""

    def test_a_newline_joined_side_resolves_the_same(self, store):
        found, _ = side_fighters(store, "Yuji Itadori\nMegumi Fushiguro")
        assert sorted(found) == ["Megumi Fushiguro", "Yuji Itadori"]

    def test_longest_title_is_consumed_first(self, store):
        """`Maki Zenin vs. The Hei` has `side2 = 'Hei Nobuaki Zenin'`.

        Matching `Nobuaki Zenin` before any shorter name leaves `Hei` as
        residue -- a second fighter with no page. Shortest-first would eat
        `Zenin` and leave nonsense.
        """
        found, leftover = side_fighters(store, "Hei Nobuaki Zenin")
        assert found == ["Nobuaki Zenin"]
        assert leftover == "Hei"

    def test_a_parenthetical_state_is_not_a_second_fighter(self, store):
        """`Sukuna (16 Fingers)` says which Sukuna, not that two turned up."""
        assert side_fighters(store, "Sukuna (16 Fingers)") == (["Sukuna"], "")

    def test_a_faction_name_resolves_to_nobody(self, store):
        """`Cursed Spirits` and `Jujutsu Sorcerers` are not named characters,
        so they fail the same test without needing a rule of their own."""
        found, leftover = side_fighters(store, "Cursed Spirits")
        assert found == []
        assert leftover != ""

    def test_a_species_page_is_not_a_character(self, store):
        """`Finger Bearer` is one opponent, and not a named character."""
        found, _leftover = side_fighters(store, "Finger Bearer")
        assert found == []

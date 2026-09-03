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

from scriptengine.retrieve.roster import (
    asks_for_battles_in,
    battles_in,
    _fighter_role,
    _fighter_words,
    asks_one_on_one,
    side_fighters,
)
from scriptengine.stores.facts import FactStore

CHARACTERS = (
    "Yuji Itadori", "Aoi Todo", "Megumi Fushiguro", "Nobara Kugisaki",
    "Maki Zenin", "Nobuaki Zenin", "Sukuna", "Mahito", "Panda", "Ko-Guy",
    "Haba", "Hanyu", "Hana Kurusu",
)

# JJK's battle infobox vocabulary (series/jjk/overrides.yaml). The default
# `_BATTLE_SIDES` is `combatant1`/`abilities1`; without this the keys never match.
JJK_OVERRIDES = {"battle_relations": [
    {"side": "side1", "abilities": "powers1"},
    {"side": "side2", "abilities": "powers2"},
]}


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


class TestAsksForBattlesIn:
    @pytest.mark.parametrize(
        "query",
        [
            "Every Fight Mahoraga Has Ever Been In",
            "all battles of Sukuna",
            "each duel Gojo was in",
            "every match Yuji Itadori fought",
            # The question-worded twins: same set, asked as a wh-question.
            "Who did Sukuna fight?",
            "What battles was Mahoraga in?",
        ],
    )
    def test_recognised(self, query):
        assert asks_for_battles_in(query) is True

    @pytest.mark.parametrize(
        "query",
        [
            "Sukuna vs. Mahoraga",             # one named battle
            "Every technique of Sukuna",       # a kit, not his fights
            "",
        ],
    )
    def test_not_claimed_when_unasked(self, query):
        assert asks_for_battles_in(query) is False


class TestFighterWords:
    def test_the_last_word_is_the_name(self):
        """The canonical title is long; the infobox writes only the name."""
        words = _fighter_words("Eight-Handled Sword Divergent Sila Divine General Mahoraga")
        assert words == ["mahoraga"]

    def test_a_single_long_word_keeps_itself(self):
        assert _fighter_words("Mahoraga") == ["mahoraga"]

    def test_short_words_are_dropped(self):
        """`vs`, `the` and other short tokens identify nobody."""
        assert _fighter_words("vs the") == []

    def test_a_name_of_only_short_words_keeps_its_tokens(self):
        """`Ui Ui` has no word longer than three letters, so `content_words`
        dropped both and the battles-in route answered with the whole
        90-battle category. The raw tokens come back; the caller matches them
        at word boundaries."""
        assert _fighter_words("Ui Ui") == ["ui"]


@pytest.fixture()
def role_store(tmp_path):
    """Two battles: one where Mahoraga fights, one where it is Sukuna's tool."""
    store = FactStore(tmp_path / "facts.db")
    store.initialise()

    def battle(title, facts):
        doc = store.add_document(
            title=title, url="", page_type="battle", infobox_template="",
            lead=f"{title} is a fight.", word_count=4, revid=1, fetched_at="",
        )
        node = store.add_node(title, "battle", doc)
        for key, value in facts:
            store.add_fact(node_id=node, key=key, label=key, value=value, citation="")

    battle("Sukuna vs. Mahoraga", [("side1", "Sukuna"), ("side2", "Mahoraga")])
    battle("Sukuna vs. Yorozu", [
        ("side1", "Sukuna"), ("side2", "Yorozu"),
        ("powers1", "Mahoraga\nDismantle"),
    ])
    # A battle Mahoraga is not on at all.
    battle("Gojo vs. Toji", [("side1", "Satoru Gojo"), ("side2", "Toji Fushiguro")])
    # A two-letter fighter, and a page whose text only contains the token as a
    # substring (`circuit` has `ui` inside it but never names Ui Ui).
    battle("Mei Mei & Ui Ui vs. Smallpox Deity", [
        ("side1", "Mei Mei Ui Ui"), ("side2", "Smallpox Deity"),
    ])
    battle("Riko vs. Circuit", [("side1", "Riko"), ("side2", "Circuit")])

    yield store
    store.close()


class TestFighterRole:
    def test_direct_combatant(self, role_store):
        role = _fighter_role(role_store, "Sukuna vs. Mahoraga", "Mahoraga", JJK_OVERRIDES)
        assert role == "direct combatant"

    def test_deployed_as_a_tool(self, role_store):
        role = _fighter_role(role_store, "Sukuna vs. Yorozu", "Mahoraga", JJK_OVERRIDES)
        assert "deployed by" in role and "Sukuna" in role


class TestBattlesIn:
    def test_lists_only_the_fights_it_is_on(self, role_store):
        from scriptengine.retrieve.citations import EpisodeIndex
        roster = battles_in(role_store, EpisodeIndex(), "Mahoraga", 600, JJK_OVERRIDES)
        assert roster is not None
        titles = {m.name for m in roster.members}
        assert titles == {"Sukuna vs. Mahoraga", "Sukuna vs. Yorozu"}

    def test_a_fighter_on_no_battle_returns_none(self, role_store):
        from scriptengine.retrieve.citations import EpisodeIndex
        assert battles_in(role_store, EpisodeIndex(), "Panda", 600, JJK_OVERRIDES) is None

    def test_a_short_named_fighter_matches_at_word_boundaries(self, role_store):
        """`Ui Ui` has no long word. A substring search for `ui` would also land
        in `Circuit`; word-boundary matching names exactly the fight it is on."""
        from scriptengine.retrieve.citations import EpisodeIndex
        roster = battles_in(role_store, EpisodeIndex(), "Ui Ui", 600, JJK_OVERRIDES)
        assert roster is not None
        assert {m.name for m in roster.members} == {"Mei Mei & Ui Ui vs. Smallpox Deity"}

    def test_each_member_carries_its_role(self, role_store):
        from scriptengine.retrieve.citations import EpisodeIndex
        roster = battles_in(role_store, EpisodeIndex(), "Mahoraga", 600, JJK_OVERRIDES)
        assert roster is not None
        roles = {m.name: next(f["value"] for f in m.facts if f["field"] == "Role")
                 for m in roster.members}
        assert roles["Sukuna vs. Mahoraga"] == "direct combatant"
        assert "deployed by" in roles["Sukuna vs. Yorozu"]

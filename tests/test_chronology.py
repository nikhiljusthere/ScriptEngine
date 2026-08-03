"""Story order, walked from the wiki's own arc chain.

`Every arc in order` returned nothing: it is set-shaped, reached the roster
path, and answered with the 84 chapters of a single arc. Order was not
something the engine could express.

Arc pages carry `previous`/`next`, which is a linked list, so this needs no
inference at all. What it needs is care about *which* edges to follow — there
are 4,847 of them across these wikis and most join songs, volumes and Blu-rays.
"""

from __future__ import annotations

import pytest

from scriptengine.config import series_paths
from scriptengine.retrieve import chronology
from scriptengine.retrieve.roster import build_roster
from scriptengine.stores.facts import FactStore


def paths_for(series: str):
    paths = series_paths(series)
    if not paths.facts_db.exists():
        pytest.skip(f"{series} is not indexed")
    return paths


class TestWantsChronology:
    @pytest.mark.parametrize(
        "query",
        [
            "Every arc in order",
            "Timeline of Dragon Ball",
            "Every arc of One Punch Man",
            "Every saga in Dragon Ball",
            "What happened first, chronologically?",
        ],
    )
    def test_order_questions_are_recognised(self, query):
        assert chronology.wants_chronology(query)

    @pytest.mark.parametrize(
        "query",
        [
            "Every Saiyan transformation",
            "Every Nen type",
            "Every form of Goku",
            "Every member of the Straw Hat Pirates",
        ],
    )
    def test_membership_questions_are_not(self, query):
        assert not chronology.wants_chronology(query)


class TestChains:
    def test_only_arcs_are_walked(self):
        """`Ash Crow --next--> Berserk (2016) Original Soundtrack` is a real edge.

        Following it turns a story timeline into a discography.
        """
        paths = paths_for("berserk")
        with FactStore(paths.facts_db) as store:
            arcs = {name.lower() for name in chronology.arc_pages(store)}
            for chain in chronology.chains(store):
                for name in chain:
                    assert name.lower() in arcs

    def test_a_run_inside_a_longer_run_is_not_a_separate_run(self):
        """Berserk reported `Black Swordsman Arc` as its own chain and as part
        of the main one, because both lack a predecessor and they rejoin."""
        paths = paths_for("berserk")
        with FactStore(paths.facts_db) as store:
            found = chronology.chains(store)
        seen: set[str] = set()
        for chain in found:
            names = {name.lower() for name in chain}
            assert not names <= seen, "a chain wholly inside another was kept"
            seen |= names

    def test_a_circular_link_does_not_hang(self):
        following = {"A": "B", "B": "C", "C": "A"}
        assert chronology._walk("A", following) == ["A", "B", "C"]


class TestOrder:
    def test_one_piece_starts_where_one_piece_starts(self):
        roster = build_roster(paths_for("onepiece"), "Every arc in order")
        names = [member.name for member in roster.members]
        assert names[:6] == [
            "Romance Dawn Arc",
            "Orange Town Arc",
            "Syrup Village Arc",
            "Baratie Arc",
            "Arlong Park Arc",
            "Loguetown Arc",
        ]

    def test_dragon_ball_starts_where_dragon_ball_starts(self):
        roster = build_roster(paths_for("db"), "Timeline of Dragon Ball")
        names = [member.name for member in roster.members]
        assert names[:3] == [
            "Emperor Pilaf Saga",
            "Tournament Saga",
            "Red Ribbon Army Saga",
        ]

    def test_the_chain_reaches_the_end_of_the_story(self):
        """Folding `previous` edges in beside `next` indiscriminately cut Dragon
        Ball from 45 sagas to 21, stranding Cell and Buu in fragments."""
        roster = build_roster(paths_for("db"), "Timeline of Dragon Ball")
        assert len(roster.members) > 30

    @pytest.mark.parametrize(
        "series,banned",
        [
            ("onepiece", ("Goat Island Arc", "Boss Luffy Historical Special")),
            ("db", ("Dark Demon Realm Saga", "Demon God Demigra Saga")),
        ],
    )
    def test_side_chains_stay_out_of_the_story(self, series, banned):
        """Filler and Super Dragon Ball Heroes are separate runs, not the story."""
        roster = build_roster(paths_for(series), "Every arc in order")
        names = {member.name for member in roster.members}
        for name in banned:
            assert name not in names

    def test_a_member_appears_once(self):
        roster = build_roster(paths_for("onepiece"), "Every arc in order")
        names = [member.name for member in roster.members]
        assert len(names) == len(set(names))

    def test_position_is_carried(self):
        roster = build_roster(paths_for("jjk"), "Every arc in order")
        assert [member.group for member in roster.members[:3]] == ["1", "2", "3"]


class TestSpans:
    @pytest.mark.parametrize("series", ["jjk", "csm", "db"])
    def test_the_range_is_reported(self, series):
        roster = build_roster(paths_for(series), "Every arc in order")
        assert any(member.debut for member in roster.members)

    def test_one_piece_derives_rather_than_printing_auto(self):
        """One Piece stores the literal string `auto` — the wiki counts the
        chapters that link to the arc rather than recording a range."""
        roster = build_roster(paths_for("onepiece"), "Every arc in order")
        spans = " ".join(member.debut for member in roster.members)
        assert "auto" not in spans.lower()
        assert "chapters" in spans.lower()


class TestDeclining:
    @pytest.mark.parametrize("series", ["bleach", "hxh"])
    def test_a_wiki_with_no_arc_pages_declines(self, series):
        """Bleach keeps its arcs only inside episode titles. Inventing an order
        would be worse than not having one."""
        assert chronology.build_chronology(paths_for(series), "Every arc in order") is None


class TestNoRegression:
    @pytest.mark.parametrize(
        "series,query,basis",
        [
            ("db", "Every Saiyan transformation", "Transformations"),
            ("db", "Every race in Dragon Ball", "Races"),
            ("hxh", "Every Nen type", "Nen Types"),
            ("bleach", "Every Espada", "Espada"),
        ],
    )
    def test_set_questions_are_untouched(self, series, query, basis):
        assert build_roster(paths_for(series), query).basis == basis

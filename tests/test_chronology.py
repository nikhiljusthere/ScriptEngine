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


class TestHeading:
    """The arc section heading a script writes, from what the wiki wrote.

    `spans` is correct and returns four different shapes for the same idea --
    measured across One Punch Man and Jujutsu Kaisen, one range arrives as
    `30 • 31 • ... • 37`, as `Chapter 52 - 65` with the kind word inside the
    value, as `21 - Ongoing`, and as `193 (Online)`. A heading has to read as
    speech.
    """

    @pytest.mark.parametrize(
        "value, kind, expected",
        [
            # A bulleted run is one span, not eight citations.
            ("30 • 31 • 32 • 33 • 34 • 35 • 36 • 37", "MANGA CHAPTER",
             "MANGA CHAPTERS 30-37"),
            # The wiki already said "Chapter"; saying it twice reads badly.
            ("Chapter 52 - 65", "MANGA CHAPTER", "MANGA CHAPTERS 52-65"),
            # One instalment stays singular.
            ("1", "EPISODE", "EPISODE 1"),
            ("20", "MANGA CHAPTER", "MANGA CHAPTER 20"),
            # A range plus a straggler is still one span in a heading.
            ("Episode 22 - 24, 30", "EPISODE", "EPISODES 22-30"),
            # An open end is kept as written rather than invented.
            ("21 - Ongoing", "EPISODE", "EPISODES 21-Ongoing"),
            ("Episode 48 - TBA", "EPISODE", "EPISODES 48-TBA"),
            # Prequel chapters really are called `0-1` and `0-4`. Running them
            # together gives `0-1-0-4`, which cannot be read.
            ("Chapter 0-1 - 0-4", "MANGA CHAPTER", "MANGA CHAPTERS 0-1 to 0-4"),
            # Nothing to say stays nothing, rather than becoming a bare label.
            ("", "EPISODE", ""),
            ("auto", "MANGA CHAPTER", ""),
        ],
    )
    def test_says_one_span(self, value, kind, expected):
        assert chronology._said(value, kind) == expected

    def test_says_what_the_wiki_recorded(self):
        """`Saitama Introduction Arc | MANGA CHAPTERS 1-4, EPISODE 1`.

        Asserted because the One Punch Man wiki files the arc as chapters
        1 • 2 • 3 • 4 and episode 1, and this is that said aloud. A
        hand-written script happens to use the same line, which is a useful
        sanity check and not the reason this passes -- the sample scripts are
        written by a person and are a style reference, not a fact source. Where
        one disagrees with the wiki, the wiki wins and this test moves with it.
        """
        paths = paths_for("opm")
        with FactStore(paths.facts_db) as store:
            chapters, episodes = chronology.spans(store, "Saitama Introduction Arc")
            assert "1" in chapters and "4" in chapters
            assert chronology.heading(store, "Saitama Introduction Arc") == (
                "Saitama Introduction Arc | MANGA CHAPTERS 1-4, EPISODE 1"
            )

    def test_unadapted_arc_claims_no_episode(self):
        """An arc the anime has not reached must not be given an episode."""
        paths = paths_for("jjk")
        with FactStore(paths.facts_db) as store:
            said = chronology.heading(store, "Shinjuku Showdown Arc")
        assert "MANGA CHAPTERS 222-271" in said
        assert "EPISODE" not in said


class TestAppearances:
    """A character's arcs, in story order — the spine of a life script.

    `The Entire Life of Garou Explained` runs Garou Introduction, Hero Hunt,
    Monster Raid, Monster Association. The wikis already file character history
    under arc-named headings, so this needs no inference: 1,093 such chunks
    across Jujutsu Kaisen, 1,859 across One Punch Man.
    """

    def test_arcs_come_back_in_story_order(self):
        paths = paths_for("jjk")
        with FactStore(paths.facts_db) as store:
            found = [a.arc for a in chronology.appearances(store, "Yuji Itadori")]
        # Canon order, not alphabetical: Fearsome Womb opens the series and
        # Shinjuku Showdown closes it.
        assert found[0] == "Fearsome Womb Arc"
        assert found[-1] == "Shinjuku Showdown Arc"
        assert found.index("Shibuya Incident Arc") < found.index("Culling Game Arc")

    def test_heading_is_script_ready(self):
        paths = paths_for("opm")
        with FactStore(paths.facts_db) as store:
            found = chronology.appearances(store, "Saitama")
        assert found, "Saitama appears in no arc"
        # The opening heading of the hand-written One Punch Man script.
        assert found[0].heading == (
            "Saitama Introduction Arc | MANGA CHAPTERS 1-4, EPISODE 1"
        )

    def test_the_chunker_s_duplicates_are_dropped(self):
        """A section is chunked at two levels, so the same prose arrives twice.

        Counted raw, Yuji's part in the Shibuya Incident reads as 7,190 words
        against a page holding about half that, and a script built on it would
        say everything twice.
        """
        paths = paths_for("jjk")
        with FactStore(paths.facts_db) as store:
            found = chronology.appearances(store, "Yuji Itadori")
        for appearance in found:
            keys = [" ".join(p.split())[:160] for p in appearance.passages]
            assert len(keys) == len(set(keys)), f"{appearance.arc} repeats itself"

    def test_a_character_in_no_arc_is_empty_not_an_error(self):
        paths = paths_for("jjk")
        with FactStore(paths.facts_db) as store:
            assert chronology.appearances(store, "No Such Person At All") == []


class TestCast:
    """Who is in an arc, read back off the character pages.

    The two wikis disagree about recording it: One Punch Man arcs carry 172
    `characters` edges and Jujutsu Kaisen arcs carry none. Reading it off the
    character pages works on both.
    """

    def test_jjk_arc_has_a_cast_despite_no_edges(self):
        paths = paths_for("jjk")
        with FactStore(paths.facts_db) as store:
            who = chronology.cast(store, "Shibuya Incident Arc")
        assert len(who) > 20, "Shibuya is the largest arc in the series"
        # Ordered by how much of the arc is written on their page, so the
        # people it happened to come first.
        assert who[0] == "Yuji Itadori"
        for name in ("Satoru Gojo", "Megumi Fushiguro", "Mahito"):
            assert name in who

    def test_the_arc_itself_is_not_in_its_own_cast(self):
        paths = paths_for("jjk")
        with FactStore(paths.facts_db) as store:
            who = chronology.cast(store, "Shibuya Incident Arc")
        assert "Shibuya Incident Arc" not in who

    def test_only_characters(self):
        """`History` is a heading on places too, and a place is not a cast."""
        paths = paths_for("opm")
        with FactStore(paths.facts_db) as store:
            who = chronology.cast(store, "Monster Association Arc")
            from scriptengine.retrieve import semantics as ontology

            for name in who[:15]:
                assert ontology.semantic_type(store, name) == "character"

    def test_unknown_arc_is_empty_not_an_error(self):
        paths = paths_for("jjk")
        with FactStore(paths.facts_db) as store:
            assert chronology.cast(store, "No Such Arc At All") == []


class TestBeats:
    """Prose cut where its citations change — the shape a script is written in.

    The Hero Hunt Arc comes back as 864 words in two chunks; the hand-written
    script cuts the same material into eleven beats. Re-cutting prose someone
    has already written is the tedious half of the job.
    """

    def test_a_run_of_sentences_under_one_ref_is_one_beat(self):
        said = chronology.beats(
            "He arrives. He wins.(Chapter 4) Then he leaves.(Chapter 5)"
        )
        assert len(said) == 2
        assert said[0].text == "He arrives. He wins."
        assert "Chapter 4" in said[0].locator
        assert said[1].text == "Then he leaves."
        assert "Chapter 5" in said[1].locator

    def test_the_marker_is_said_in_the_locator_not_the_prose(self):
        """A beat's text is what gets read out; the ref is the tag on it."""
        said = chronology.beats("He wins the fight.(Chapter 4)")
        assert said[0].text == "He wins the fight."
        assert "(Chapter" not in said[0].text

    def test_unsourced_prose_still_becomes_a_beat(self):
        said = chronology.beats("Something happens with no reference at all.")
        assert len(said) == 1
        assert said[0].locator == ""


class TestScaffold:
    def test_a_section_a_writer_can_work_from(self):
        paths = paths_for("opm")
        with FactStore(paths.facts_db) as store:
            section = chronology.scaffold(store, "Garou", "Hero Hunt Arc")
        assert section is not None
        assert section.heading == (
            "Hero Hunt Arc | MANGA CHAPTERS 46-51, EPISODE 15"
        )
        assert len(section.beats) >= 5
        # Nearly every beat carries a locator; that is the whole point.
        assert sum(1 for b in section.beats if b.locator) >= len(section.beats) - 1
        assert "Water Stream Rock Smashing Fist" in section.abilities

    def test_beats_do_not_repeat_themselves(self):
        """Two cuts of one section overlap without either containing the other.

        Garou's Hero Hunt Arc came back saying `target Sweet Mask` twice, and
        with Chapter 49 after Chapter 50.
        """
        paths = paths_for("opm")
        with FactStore(paths.facts_db) as store:
            section = chronology.scaffold(store, "Garou", "Hero Hunt Arc")
        keys = [" ".join(b.text.split())[:120].lower() for b in section.beats]
        assert len(keys) == len(set(keys))

    def test_a_relation_scoped_to_another_arc_is_out_of_scope(self):
        """Garou is `ally` to Saitama only in the Ominous Future."""
        paths = paths_for("opm")
        with FactStore(paths.facts_db) as store:
            section = chronology.scaffold(store, "Garou", "Hero Hunt Arc")
        for tie in section.relations:
            assert "Ominous Future" not in tie

    def test_an_arc_the_character_is_not_in(self):
        paths = paths_for("opm")
        with FactStore(paths.facts_db) as store:
            assert chronology.scaffold(store, "Garou", "No Such Arc") is None

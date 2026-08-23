"""Tests for mode selection.

Two bugs prompted this file. `qa`, the hybrid retriever with a cross-encoder
over it, was unreachable from `auto`, because the router was
`"roster" if looks_like_enumeration(q) else "narrative"`. And that test is a
regex, so `What grade of sorcerer is Aoi Todo?` matched `grades? of` and came
back as a list of Todo's five battles.

Measured over 168 real queries, the regex and a structural read disagreed on 13,
all of them wh-questions. Those 13 are the cases below, in both directions: the
ones that must now reach `qa`, and the two that must stay `narrative`.
"""

from __future__ import annotations

import pytest

from scriptengine.retrieve import semantics
from scriptengine.retrieve.router import _NARRATIVE_VERBS, _WH, Route, route


class TestSignals:
    """The pieces the decision is made from, without touching a store."""

    @pytest.mark.parametrize(
        "query",
        ["What grade is X?", "Who killed Ace?", "Which division?", "how many are there"],
    )
    def test_interrogatives_are_recognised(self, query):
        assert _WH.match(query)

    @pytest.mark.parametrize("query", ["Every Apostle", "Shibuya Incident"])
    def test_statements_are_not(self, query):
        assert not _WH.match(query)

    def test_story_verbs_are_recognised(self):
        assert _NARRATIVE_VERBS.search("How did the Shibuya Incident unfold?")
        assert _NARRATIVE_VERBS.search("What happened in Marineford?")

    def test_a_verb_in_a_relative_clause_is_not_the_question(self):
        """"the punch that occurs when an attack lands" is a description.

        Only the head of the sentence decides, which is why `route` searches the
        first few words rather than the whole string.
        """
        query = "What is the strengthened punch that occurs when an attack lands?"
        head = " ".join(query.split()[:4])
        assert _NARRATIVE_VERBS.search(query)
        assert not _NARRATIVE_VERBS.search(head)


class TestRoute:
    """End to end, against the real stores; routing reads the ontology."""

    @pytest.mark.parametrize(
        "series,query",
        [
            # The regex misfires: enumeration words inside a fact lookup.
            ("jjk", "What grade of sorcerer is Aoi Todo?"),
            ("jjk", "What type of curse is Mahito?"),
            # Fact lookups that used to fall to narrative because `qa` was
            # unreachable from auto at all.
            ("db", "What race is Vegeta?"),
            ("onepiece", "What is Zoro's sword called?"),
            ("hxh", "What Nen type is Killua?"),
            ("db", "Who taught Goku the Kaio-ken?"),
            ("onepiece", "Who killed Ace?"),
        ],
    )
    def test_fact_lookups_reach_qa(self, series, query):
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        assert route(paths, query).mode == "qa"

    @pytest.mark.parametrize(
        "series,query",
        [
            ("jjk", "How did the Shibuya Incident unfold?"),
            ("onepiece", "What happened in Marineford?"),
            ("jjk", "Shibuya Incident"),
        ],
    )
    def test_story_questions_stay_narrative(self, series, query):
        """The half a bare wh-word rule got wrong."""
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        assert route(paths, query).mode == "narrative"

    @pytest.mark.parametrize(
        "series,query",
        [
            ("db", "Every Saiyan transformation"),
            ("hxh", "Every Nen type"),
            ("berserk", "Every Apostle"),
            ("hxh", "How many levels of Nen are there?"),
        ],
    )
    def test_sets_still_reach_roster(self, series, query):
        """The enumeration test agreed with structure on all 154 real topics,
        so this is the half that must not move."""
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        assert route(paths, query).mode == "roster"

    @pytest.mark.parametrize(
        "series,query",
        [
            ("hxh", "Who are the members of the Phantom Troupe?"),
            ("bleach", "Who are the current Gotei 13 captains?"),
            ("opm", "Who are the S-Class heroes in One Punch Man?"),
            # No enumeration word at all -- the plural noun is the only cue.
            ("jjk", "What are Sukuna's named cursed techniques?"),
            ("onepiece", "Who are the current members of the Straw Hat Pirates?"),
        ],
    )
    def test_a_plural_question_asks_for_the_list(self, series, query):
        """"Who are the members of X" is "Every member of X" with a question mark.

        Every one of these returned **zero** members before, because rule 3
        claims any interrogative for `qa` before the enumeration test is
        reached. Asked as a statement the same sets return 11 to 23. The bank
        could not see it: all 103 of its set questions opened with "Every".
        """
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        assert route(paths, query).mode == "roster"

    @pytest.mark.parametrize(
        "series,query",
        [
            ("jjk", "What is Sukuna's Domain Expansion?"),
            ("db", "Who taught Goku the Kaio-ken?"),
            ("onepiece", "Who killed Ace?"),
            ("bleach", "Who is the current Captain-Commander of the Gotei 13?"),
        ],
    )
    def test_a_singular_question_is_still_a_lookup(self, series, query):
        """The verb's number is the whole discriminator.

        Widening the plural rule to every wh-question would swallow the lookups
        rule 3 exists to protect -- "what grade of sorcerer **is** Yuji" reads
        as an enumeration and is not one.
        """
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        assert route(paths, query).mode == "qa"

    def test_the_reason_is_reported(self):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, "What grade of sorcerer is Aoi Todo?")
        assert "Aoi Todo" in chosen.why
        assert chosen.signals["set_shaped"] is True   # the regex still fires…
        assert chosen.mode == "qa"                     # …and no longer decides

    def test_routing_never_raises(self, tmp_path):
        """A router that throws takes every query down with it."""
        from scriptengine.config import SeriesPaths

        broken = SeriesPaths(name="nope", root=tmp_path / "nope")
        assert route(broken, "What race is Vegeta?").mode in {"qa", "roster", "narrative"}


class TestBattlesInRouting:
    """A fighter's whole fight list routes to roster, however it is worded.

    The set-shaped forms ("Every Fight Mahoraga Has Ever Been In") already reach
    the roster via the enumeration test. Their question-worded twins -- "Who did
    Mahoraga fight?" -- used to be claimed by rule 3 for `qa` before that test
    was reached, so they got a prose lookup instead of the list of battles. The
    guard probes whether this wiki actually holds a set of that fighter's fights;
    only then does the question earn a roster route.
    """

    @pytest.mark.parametrize(
        "query",
        [
            # Statement forms: the enumeration test claims these.
            "Every Fight Mahoraga Has Ever Been In",
            "All battles of Sukuna",
            "Each duel Gojo was in",
            # Question-worded twins: rule 2b must claim these before rule 3's qa.
            "Who did Mahoraga fight?",
            "What battles was Sukuna in?",
        ],
    )
    def test_fight_lists_reach_roster(self, query):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query).mode == "roster"

    def test_a_fighter_with_no_battles_stays_a_lookup(self):
        """A wh-fight question about a fighter on no battle page has no set to
        list, so it falls through rule 2b and is answered from prose."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        # `Ko-Guy` has no battle page in the jjk corpus, so there is no list.
        chosen = route(paths, "Who did Ko-Guy fight?")
        assert chosen.mode != "roster"

    def test_the_battles_in_signal_is_reported(self):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, "Who did Mahoraga fight?")
        assert chosen.signals["battles_in_ask"] is True
        assert chosen.mode == "roster"


class TestSubjectPreference:
    def test_packaging_never_becomes_the_subject(self):
        """"Who killed Ace?" resolved to `Legendary Hour`, an episode."""
        from scriptengine.config import series_paths

        paths = series_paths("onepiece")
        if not paths.facts_db.exists():
            pytest.skip("onepiece is not indexed")
        chosen = route(paths, "Who killed Ace?")
        assert chosen.signals["subject_type"] != semantics.MEDIA
        assert "Ace" in chosen.signals["subject"]

    @pytest.mark.parametrize(
        "series,query,owner",
        [
            ("onepiece", "What is Luffy's Devil Fruit?", "Luffy"),
            ("onepiece", "What is Zoro's sword?", "Zoro"),
            ("db", "What is Goku's technique?", "Goku"),
            ("bleach", "What is Ichigo's power?", "Ichigo"),
            ("hxh", "What is Killua's ability?", "Killua"),
            ("jjk", "What is Sukuna's domain?", "Sukuna"),
            ("csm", "What is Makima's ability?", "Makima"),
        ],
    )
    def test_a_possessive_names_the_subject(self, series, query, owner):
        """"What is Luffy's Devil Fruit?" answered `Goe Goe no Mi`.

        `Luffy` is an alias with no page of its own, and unresolved candidates
        were filtered out before the possessive could be read, leaving the
        question to choose between devil fruits.
        """
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        assert owner.lower() in str(route(paths, query).signals["subject"]).lower()

    def test_the_named_event_beats_the_place_it_happened(self):
        """`Shibuya Incident` must win over `Shibuya`, or the story question
        becomes a lookup about a location."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, "Shibuya Incident").signals["subject"] == "Shibuya Incident"


class TestArcsAreASetOnlyWhenAsked:
    """Naming an arc is naming a subject; asking for arcs is asking for a set.

    `wants_chronology` tested `\b(arc|saga)s?\b`, so every topic that mentioned
    an arc was answered with the ordered list of arcs. `Fearsome Womb Arc` is
    one arc's story, the shape a script about it needs, and it was coming
    back as a roster, which is the gold case `narrative-02` asserts against.
    """

    @pytest.mark.parametrize(
        "query",
        [
            "Every arc in order",
            "Every arc of One Punch Man",
            "All arcs",
            "How many arcs are there",
            "Every saga in Dragon Ball",
            "Timeline of Dragon Ball",
            "list the arcs",
        ],
    )
    def test_asking_for_the_set_wants_order(self, query):
        from scriptengine.retrieve.chronology import wants_chronology

        assert wants_chronology(query)

    @pytest.mark.parametrize(
        "query",
        [
            "Fearsome Womb Arc",
            "Shibuya Incident Arc",
            "Cell Saga",
            "Every Rank of Curse in Jujutsu Kaisen",
        ],
    )
    def test_naming_one_arc_is_a_subject_not_a_set(self, query):
        from scriptengine.retrieve.chronology import wants_chronology

        assert not wants_chronology(query)

    def test_the_gold_narrative_case_routes_narrative(self):
        """`narrative-02` in gold_jjk.json. It failed through the router while
        every path-level test passed, which is the failure this catches."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, "Fearsome Womb Arc").mode == "narrative"


class TestPhrasingRobustFieldQuestions:
    """A question naming an infobox field reaches qa in natural phrasing.

    The campaign's motive (2026-08-24) is that a question is answerable in
    any natural phrasing, so the bank keeps natural wording and the engine
    carries it. Two engine defects kept the natural phrasings on `narrative`,
    the one path that strips exactly these fields:

    - the wh test only fired on a wh-word at position 0, so "In which arc
      does X take place?" read as a statement; and
    - the field vocabulary did not name the battle-infobox fields JJK's
      battle pages record (arc, place, event, outcome, date), so even the
      wh-worded twins ("Where did X take place?") fell through on a battle
      subject, an event the story-type rule sends to narrative.

    Battle questions are rescued only by rule 6 (`interrogative and
    _asks_for_field`), so both halves of the fix live there: a robust opener
    and a corpus-intersected field vocabulary.
    """

    @pytest.mark.parametrize(
        "query",
        [
            # Prepositional wh-openers: the wh-word is not at position 0.
            "In which arc does Yuji Itadori vs. Mahito take place?",
            "In which episode is Satoru Gojo vs. Toji Fushiguro depicted?",
            "In which manga chapter does Yuji Itadori vs. Choso take place?",
            "During which arc does Yuji Itadori vs. Panda take place?",
            # `whom` was missing from the wh set entirely.
            "Whom did Toji Fushiguro kill?",
            # Battle-infobox fields the old vocabulary did not name.
            "Where did Yuji Itadori vs. Panda take place?",
            "When did Satoru Gojo vs. Sukuna take place?",
            "What was the result of Yuji Itadori vs. Mahito?",
            "What is the outcome of Toji Fushiguro vs. Kenjaku?",
            # Story-type subject (an event): rule 3 is off the table, so only
            # rule 6 -- interrogative + a named field -- can reach qa. This is
            # the field-vocabulary half of the fix in isolation.
            "Where does the Shibuya Incident take place?",
        ],
    )
    def test_battle_field_questions_reach_qa(self, query):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query).mode == "qa"

    def test_the_prepositional_opener_is_recognised(self):
        from scriptengine.retrieve.router import _is_interrogative

        for query in (
            "In which arc does X take place?",
            "On which event did X happen?",
            "During which saga did X happen?",
            "After which arc did X happen?",
            "Whom did X kill?",
        ):
            assert _is_interrogative(query)
        for query in (
            "Every arc",
            "Shibuya Incident",
            "In order to win the battle",
            "After the war, the story ends",
        ):
            assert not _is_interrogative(query)

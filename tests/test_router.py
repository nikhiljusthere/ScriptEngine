"""Tests for mode selection.

Two bugs prompted this file. `qa` — the hybrid retriever with a cross-encoder
over it — was unreachable from `auto`, because the router was
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
    """End to end, against the real stores — routing reads the ontology."""

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
        were filtered out before the possessive could be read — leaving the
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
    one arc's story — the shape a script about it needs — and it was coming
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

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
        # `Masamichi Yaga` has no battle page in the jjk corpus (he was a
        # non-combatant), so there is no list. (The test used `Ko-Guy` here
        # before a `Yuji Itadori vs. Ko-Guy` page landed; that fighter now
        # resolves to a real roster, which is the short-token fallback working.)
        chosen = route(paths, "Who did Masamichi Yaga fight?")
        assert chosen.mode != "roster"

    def test_the_battles_in_signal_is_reported(self):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, "Who did Mahoraga fight?")
        assert chosen.signals["battles_in_ask"] is True
        assert chosen.mode == "roster"

    def test_a_single_battle_question_stays_a_prose_lookup(self):
        """"Which battle in Ui Ui's battle history is listed as offscreen?" names
        one battle by a property, not the fighter's whole fight list. Its answer
        is a prose annotation (an offscreen fight with no page), so the
        battles-in roster must not claim it even though `Ui Ui` resolves a list
        of battles (G16). The wh-form is carved out of `battles_in_ask` and the
        question falls through rule 3 to `qa`."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(
            paths,
            "Which battle in Ui Ui's battle history is listed as offscreen?",
        )
        assert chosen.signals["battles_in_ask"] is False
        assert chosen.mode != "roster"


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

    def test_a_possessive_in_an_object_does_not_outrank_the_agent(self):
        """R5-b (G12): "Can Suguru Geto cast Curtain over a weaker sorcerer's
        barrier?" names Suguru Geto as the agent, but the possessive "a weaker
        sorcerer's" resolved the organization `Jujutsu Sorcerer` and outranked
        the agent, so a bare query landed on the wrong page focus. A possessive
        owner buried in a prepositional object must not win the boost; the
        named agent stays the subject (the topic case above is untouched)."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, "Can Suguru Geto cast Curtain over a weaker sorcerer's barrier?")
        assert chosen.signals["subject"] == "Suguru Geto"
        assert chosen.mode == "qa"

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
            # The scope preposition of a technique lookup (2026-09-03,
            # technique prose pass): the wh-word sits behind `against`.
            "Against which domains is X ineffective?",
        ):
            assert _is_interrogative(query)
        for query in (
            "Every arc",
            "Shibuya Incident",
            "In order to win the battle",
            "After the war, the story ends",
            "Against all odds, X prevailed",
        ):
            assert not _is_interrogative(query)


class TestPandaGaps:
    """G6 and G7, caught on the Panda page.

    G6: a `build_roster` that finds nothing returns a bare `Roster(subject=...)`
    whose confidence is the dataclass default "declared". `_resolves_a_set` read
    that default as "the set exists", so a counting question ("How many cores
    are inside Panda's body, and what are they?") and a plural fact lookup
    ("What are the kanji for Panda's name?") were handed to a roster that
    rendered nothing. The probe now demands a basis or a member, not the
    default.

    G7: the G4b effect form covered "what happens to X" only. Its hypothetical
    twin "What happens if one of Panda's cores is damaged?" asks the mechanism
    the page's prose answers, so `if` joins `to`; the past "happened" stays
    narrative either way.
    """

    @pytest.mark.parametrize(
        "query",
        [
            # G6: counting with no declared set behind the noun.
            "How many cores are inside Panda's body, and what are they?",
            # G6: a plural fact lookup, the kanji live on the page, not in a set.
            "What are the kanji for Panda's name?",
            # G7: the hypothetical mechanism form.
            "What happens if one of Panda's cores is damaged?",
        ],
    )
    def test_the_panda_gaps_reach_qa(self, query):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query).mode == "qa"

    @pytest.mark.parametrize(
        "query",
        [
            # The sets that must keep their roster route while the bare
            # fallthrough loses its.
            "What are Sukuna's named cursed techniques?",
            "What are all the aliases of Mahito?",
            "Who did Mahoraga fight?",
        ],
    )
    def test_genuine_sets_still_reach_roster(self, query):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query).mode == "roster"

    def test_the_effect_form_reaches_both_twins(self):
        from scriptengine.retrieve.router import _EFFECT_ON

        assert _EFFECT_ON.match("What happens to targets in Mahito's domain?")
        assert _EFFECT_ON.match("What happens if one of Panda's cores is damaged?")
        assert _EFFECT_ON.match("What will happen to the city?")
        # The past is an account, in both forms: `ed` breaks the match.
        assert not _EFFECT_ON.match("What happened to Nanami during the Shibuya Incident?")
        assert not _EFFECT_ON.match("What happened if the curse escaped?")

    def test_past_accounts_stay_narrative(self):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, "What happened to Nanami during the Shibuya Incident?").mode == "narrative"


class TestG17SingleFieldPlural:
    """G17 (Phantom Cursed Spirit Q001, 2026-08-31; numbered in R6 -- the run that
    found it mislabelled it G11, which is the R1 location-scoped outcome gap):
    a plural-shaped question that
    names a single-valued infobox field (the kanji of a name) is a lookup, not a
    set ask. On a subject that resolves a set (Phantom Cursed Spirit's battle
    roster) the plural rule used to claim it before rule 6 could rescue the
    field lookup, so the kanji -- carried by the qa beat -- was unservable. The
    fix defers the single-valued-field lookup to qa; multi-valued fields
    (chapters) and the genuine plural sets keep their roster route.
    """

    @pytest.mark.parametrize(
        "query,subject",
        [
            ("What are the kanji for Phantom Cursed Spirit's name?", "Phantom Cursed Spirit"),
            ("What are the romaji for Phantom Cursed Spirit's name?", "Phantom Cursed Spirit"),
        ],
    )
    def test_single_field_lookup_reaches_qa_on_a_set_subject(self, query, subject):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query, subject=subject).mode == "qa"

    @pytest.mark.parametrize(
        "query,subject",
        [
            ("What are all the chapters of the Culling Game?", "Culling Game"),
            ("What are Sukuna's named cursed techniques?", "Sukuna"),
        ],
    )
    def test_multi_valued_and_genuine_sets_still_reach_roster(self, query, subject):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query, subject=subject).mode == "roster"


class TestG20OnceFrontedMechanism:
    """G20 (Kechizu Q036, opened in R6, 2026-09-01): a mechanism question
    fronted by a temporal clause -- "Once Kechizu or Eso blood enters a
    target through wounds what happens during Decay?" -- opens with the
    clause, not a wh-word, so `_is_interrogative` read it as a statement and
    the question fell to the narrative default, where the subject page's
    section (the answer's home) is never walked. `once` joins the leading
    discourse markers; the `_WH_ANY` guard means a statement that merely
    starts with "once" is never promoted.
    """

    @pytest.mark.parametrize(
        "query,subject",
        [
            (
                "Once Kechizu or Eso blood enters a target through wounds what happens during Decay?",
                "Kechizu",
            ),
        ],
    )
    def test_once_fronted_mechanism_reaches_qa(self, query, subject):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query, subject=subject).mode == "qa"

    def test_a_statement_that_opens_with_once_stays_a_statement(self):
        from scriptengine.retrieve.router import _is_interrogative

        assert not _is_interrogative("Once the Culling Game began the sorcerers adapted")


class TestGetoGaps:
    """G8a-d, caught on Suguru Geto (2026-08-25), closed in release R1.

    G8a: a yes/no scope question ("Was Suguru Geto dependent on his curses
    in battle?") -- an auxiliary-fronted question is not a wh-question, so
    the wh-only test read it as a statement and an 87-beat battle narrative
    came back instead of the page that answers it.
    G8b: an event-name scope ("What was the true goal of the Night Parade of
    a Hundred Demons?") -- the question's own words resolve the *event*, and
    the page the question was authored against is never considered. The
    explicit `subject` (the scorer sends it, the G3a fix) now takes
    precedence over inference for the mode decision: a precedence rule, not
    an override -- a story-typed subject keeps the narrative read, and the
    qa wide search takes the subject as a focus either way.
    G8c: "Under what condition can Suguru Geto absorb a curse with no
    consequences?" -- `wants_chronology` substring-matched "sequence"
    inside "con-sequence-s" and the question walked a roster that renders
    nothing (the word-boundary fix is tested in TestWantsChronology).
    G8d: a possessive-noun bait ("Can Suguru Geto cast Curtain over a
    weaker sorcerer's barrier?") -- `_subject()` resolves `Jujutsu Sorcerer`
    (organization) off "sorcerer's" instead of Geto; the explicit subject
    takes precedence, and the yes/no recognition alone already reaches qa.
    """

    @pytest.mark.parametrize(
        "query",
        [
            # G8a: a yes/no with a scope phrase.
            "Was Suguru Geto dependent on his curses in battle?",
            # G8c: a condition question, not an order.
            "Under what condition can Suguru Geto absorb a curse with no consequences?",
        ],
    )
    def test_geto_questions_reach_qa(self, query):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query).mode == "qa"

    @pytest.mark.parametrize(
        "query,subject",
        [
            # G8b: the event scope only resolves the event from the query's words.
            ("What was the true goal of the Night Parade of a Hundred Demons?",
             "Suguru Geto"),
            # G8d: the possessive bait resolves the organization off "sorcerer's".
            ("Can Suguru Geto cast Curtain over a weaker sorcerer's barrier?",
             "Suguru Geto"),
        ],
    )
    def test_explicit_subject_wins_the_mode_decision(self, query, subject):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query, subject=subject).mode == "qa"

    def test_without_the_hint_the_event_keeps_its_narrative_read(self):
        """The hint is a precedence rule, not an override: without it, G8b's
        own words still resolve the event, and the event's narrative read
        (the shape the eval's story rows rest on) stands."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, "What was the true goal of the Night Parade of a Hundred Demons?")
        assert chosen.mode == "narrative"
        assert chosen.signals["subject"] == "Night Parade of a Hundred Demons"

    def test_a_yes_no_with_a_story_verb_stays_narrative(self):
        """`Did Sukuna kill Nanami?` is an account, not a lookup: the story
        verb the auxiliary fronts keeps it on narrative, the way the
        head-window check does for the wh form. This guard is the
        mitigation for the yes/no branch over-claiming; the opm canon
        baseline is the detector."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, "Did Sukuna kill Nanami?").mode == "narrative"

    def test_a_matched_partial_roster_is_not_a_set(self):
        """The partial-confidence guard, belt-and-braces behind G8c: a
        declared set the topic did not narrow (a matched phrase plus a
        qualifier nothing could be checked against, "used to trap") carries
        a partial confidence, and a counting question must read the number
        out of prose instead of walking a roster that renders the wrong
        set. The `matched` short-circuit used to admit it; the genuine
        count against the full set still earns its roster route."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, "How many of Suguru Geto's named techniques are used to trap?")
        assert chosen.mode != "roster"
        assert route(paths, "How many named techniques does Suguru Geto have?").mode == "roster"


class TestShokoGaps:
    """G9a/c/d, caught on Shoko Ieiri (2026-08-26), closed in release R1;
    G9b (the negated conditional / counterfactual) closed in release R5-a.

    G9b routed "What happened to Ijichi and Ino if they had not been treated
    by Shoko?" to a narrative that never carries the factual answer. The
    discriminator is the conditional clause (a past-perfect `if` clause or a
    `would` main clause), not the head verb: the hypothetical now reaches qa,
    while the past-factual form the eval gold row rests on ("What happened to
    Nanami during the Shibuya Incident?") has no clause and stays narrative.
    The controls below pin both sides of that line.
    """

    @pytest.mark.parametrize(
        "query",
        [
            # G9a: a yes/no.
            "Does Shoko have an innate cursed technique?",
            # G9c: a capability question.
            "Can Shoko teach someone how to use reverse cursed technique?",
            # G9d: a comparative.
            "Is it easier for Shoko to heal herself or others?",
        ],
    )
    def test_shoko_questions_reach_qa(self, query):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query).mode == "qa"

    @pytest.mark.parametrize(
        "query",
        [
            # G9b / R3: the negated-conditional / counterfactual shapes that
            # used to walk a narrative and never surface the factual answer.
            "What happened to Ijichi and Ino if they had not been treated by Shoko?",
            "What would Yuji have become if he had not become a sorcerer?",
            "What would have happened if Yuta had not pretended to kill Yuji?",
            "What would have happened to Megumi if Toji had not committed suicide to protect him?",
            "What would have happened if Naoya's domain had been able to detect Maki?",
            "What would have happened if Maki had not taken over the battle against Hanami?",
            "What would have happened if Shoko had not sutured Gojo's body for Yuta?",
        ],
    )
    def test_the_counterfactual_shapes_reach_qa(self, query):
        """R5-a: the clause, not the head verb, marks the hypothetical, and it
        is a lookup of what would have been the case, not an account."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, query)
        assert chosen.mode == "qa"
        assert chosen.signals["counterfactual"] is True

    @pytest.mark.parametrize(
        "query",
        [
            # The eval gold row: a past-factual account, no conditional clause.
            "What happened to Nanami during the Shibuya Incident?",
            # A plain past account, no conditional clause.
            "What happened to Gojo during the Shibuya Incident?",
        ],
    )
    def test_the_past_factual_forms_stay_narrative(self, query):
        """The discriminator must not swallow the past-factual account: these
        have no `if`/`would` clause, so they keep the narrative read the eval
        gold row rests on."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, query)
        assert chosen.mode == "narrative"
        assert chosen.signals["counterfactual"] is False


class TestEp14HowMechanism:
    """Ep14 (2026-09-01): a present-tense "how" question is a rule/mechanism
    lookup, not an account, even when its subject resolves to an event or
    battle. "How does a team win the Team Battle?" resolved `Sukuna vs. Jogo`
    (an event) and fell to the story-type narrative branch, where the win
    condition never appears; the forced-qa probe recovered it as the top chunk.
    The discriminator is tense: a present auxiliary (does/can/will/...) asks
    for the standing rule, a past "how did ...?" asks for the account, so the
    past form keeps its narrative read the eval's story rows rest on."""

    def test_a_how_mechanism_reaches_qa(self):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, "How does a team win the Team Battle?")
        assert chosen.mode == "qa"
        assert chosen.signals["how_mechanism"] is True

    @pytest.mark.parametrize(
        "query",
        [
            # Past-tense "how did ... unfold?" is an account, not a rule.
            "How did the Shibuya Incident unfold?",
            # The eval gold narrative row: a past-factual "what happened".
            "What happened to Nanami during the Shibuya Incident?",
        ],
    )
    def test_past_accounts_stay_narrative(self, query):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query).mode == "narrative"


class TestEpisodeAnchoredQa:
    """Ep pass (2026-09-01): an episode-anchored question ("...in Episode 40",
    "per Episode 41") is about one instalment's own prose, never the 59-episode
    wiki roster. A set cue ("what kind of X") or a plural verb ("who are ...")
    used to summon that roster -- infobox facts only, no plot prose -- so the
    page's answer was never in the bundle (the Eps 21/22/26/29/40 plural-ask /
    "what kind of X" retires, 2026-09-01). Route to qa on the anchored page,
    where a forced-qa probe recovers the answer as prose. The subject must
    resolve to a media page, so a character/arc subject and a non-episode
    plural list are left on the rules below."""

    @pytest.mark.parametrize(
        "query,subject",
        [
            # The flagged misroutes (Eps 21/29/40): set cue or plural verb,
            # episode-anchored, answer lives in the episode's plot prose.
            ("What kind of woman does Yu say is his ideal in Episode 29?", "Episode 29"),
            ("Who are Manami and Negi the former commanders of, per Episode 40?", "Episode 40"),
            ("What are the students asked if they prefer in Episode 21's juju stroll?", "Episode 21"),
        ],
    )
    def test_episode_anchored_reaches_qa(self, query, subject):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, query, subject=subject)
        assert chosen.mode == "qa"
        assert chosen.signals["episode_anchored"] is True

    def test_non_episode_plural_stays_roster(self):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        # A plural list with no episode anchor is a genuine set ask -> roster.
        assert route(paths, "What are the special grade sorcerers?").mode == "roster"

    def test_single_field_episode_lookup_stays_qa(self):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        # A kanji lookup is a single-valued field (rule 6), not a set/plural
        # prose ask, so the episode rule must defer it; it stays qa either way.
        assert route(
            paths, "What are the kanji for Episode 29's name?", subject="Episode 29"
        ).mode == "qa"

    def test_episode_anchored_set_cue_with_field_asker_reaches_qa(self):
        # ep47-064 (2026-09-02): "a member of the board" fires the set cue and
        # "result" maps to the single-value field `outcome`, so the old
        # `not asks_single_field` guard dropped this to the 59-episode roster --
        # infobox facts only, so the page's answer never reached the bundle.
        # With the guard gone, an episode-anchored plot question that merely
        # carries a field-asker word still reads from the anchored page.
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(
            paths,
            "What does a member of the board fear could result from the power vacuum, per Episode 47?",
            subject="Episode 47",
        )
        assert chosen.mode == "qa"
        assert chosen.signals["episode_anchored"] is True

    @pytest.mark.parametrize(
        "query,subject",
        [
            # F2 char-subject hijack (2026-09-02): a named character in the query
            # stole the subject off the episode, so the read keyed to the
            # character (narrative stream / roster) and the episode's beat was
            # never served. ep41-011 ("Toward what...", a leading-prep opener),
            # ep43-045 (a wh-word buried behind a noun phrase), ep52-017
            # (plural, the rule 5 roster pull), ep59-012 (yes/no).
            ("Toward what does Megumi desperately head on the verge of death, per Episode 41?", "Episode 41"),
            ("On what does Sukuna stand while looking over the destroyed remains of Shibuya, per Episode 41?", "Episode 41"),
            ("On her way to which floor does Nobara decide to exorcise Mahito, per Episode 43?", "Episode 43"),
            ("What are the jujutsu higher-ups attempting to do to Yaga, per Episode 52?", "Episode 52"),
            ("Does Yuta defeat all the other deadlock players, per Episode 59's summary?", "Episode 59"),
            # F4 roster-route (2026-09-02): an entity the query names resolves a
            # set, so the old set cue handed it that entity's roster -- infobox
            # facts only -- instead of the episode's prose (ep49).
            ("What are Death Paintings a combination of, per Episode 49?", "Episode 49"),
            ("What are sorcerers worth in the Culling Game, per Episode 49?", "Episode 49"),
            ("What are non-sorcerers worth in the Culling Game, per Episode 49?", "Episode 49"),
        ],
    )
    def test_char_and_entity_subjects_read_the_anchored_page(self, query, subject):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        chosen = route(paths, query, subject=subject)
        assert chosen.mode == "qa"
        assert chosen.signals["episode_anchored"] is True
        # The read is keyed to the authored instalment, not the named entity: a
        # route that fell to the character's page would name the character, not
        # the episode, in its reasoning.
        assert subject in chosen.why

    def test_char_subject_without_episode_anchor_stays_on_character(self):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        # No "per Episode N" anchor and a character authored page: the general-
        # ized rescue must NOT fire, so a character story beat keeps its
        # narrative read (the blast-radius guard for the F2/F4 rescue).
        chosen = route(paths, "Toward what does Megumi desperately head?", subject="Megumi Fushiguro")
        assert chosen.mode == "narrative"
        assert "Episode" not in chosen.why


class TestG28OoaListAsk:
    """G28 (Finding B, 2026-09-04): a page's order-of-appearance cast.

    "Which characters appear in X?" wants X's `Characters in Order of
    Appearance` -- a page-local, order-bearing list whose verbatim source is the
    page's own section. It is not a declared roster (the roster door serves the
    overrides.yaml sets, which do not exist yet) and can never reach rule 5:
    `_PLURAL_WH` is `^(who|what|which)\\s+(are|were)\\b`, so "which characters
    appear" sets no `plural_ask` and no set is probed. Without the `_OOA_ASK`
    rescue, a story-typed page (episode, music, chapter, event) fell to the
    story-type rule and narrated the list -- on a 12-name probe, `auto`
    (narrative) surfaced 1/12 on Aizo and 4/12 on Ao no Sumika, while `qa`
    returns the full OOA section (Aizo 45, Ao no Sumika 13). The fix routes
    these to `qa` permanently: the
    list is page-local and order-bearing, not a declared set, so there is no
    roster door to defer to. The rescue sits after rules 5 and 6; the guards pin
    that placement, so a future reorder trips the suite instead of re-routing.
    """

    @pytest.mark.parametrize(
        "series,query",
        [
            # Finding B: music and chapter pages whose OOA list was narrated.
            ("jjk", "Which characters appear in Aizo?"),
            ("jjk", "Which characters appear in Ao no Sumika?"),
            ("jjk", "Which characters appear in Chapter 1?"),
        ],
    )
    def test_ooa_list_ask_reaches_qa(self, series, query):
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        assert route(paths, query).mode == "qa"

    def test_a_plural_set_ask_keeps_its_roster_route(self):
        # "What are the fighters informed of, per Episode 51?" is worded like an
        # OOA ask ("what ... fighters") but is really a plural ask over the
        # episode's set, so rule 5 must claim it as a roster first. If the OOA
        # rescue were moved above rule 5 this would flip to qa.
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, "What are the fighters informed of, per Episode 51?").mode == "roster"

    def test_a_kanji_collision_is_a_lookup_not_a_cast(self):
        # "kanji characters" is a glyph lookup, not a cast list: the word
        # `characters` here means the name's glyphs, so it must read from the
        # page (qa), not summon a roster or a narrative read.
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert (
            route(paths, "What kanji characters compose the name Domain Amplification?").mode == "qa"
        )

    def test_an_opm_cover_credit_is_unchanged(self):
        # The capture set reaches OPM. A "who is featured" credit is a qa lookup
        # there, and the OOA rescue must not move it.
        from scriptengine.config import series_paths

        paths = series_paths("opm")
        if not paths.facts_db.exists():
            pytest.skip("opm is not indexed")
        assert (
            route(paths, "Who is featured on the cover of Volume 1 of One-Punch Man?").mode == "qa"
        )


class TestG29SingleValuePredicate:
    """G29 (Kinema-Cinema 'revealed to be' question, 2026-09-04): a plural ask
    whose wh-subject carries a single-valued copular predicate is ONE
    characterization, not a set to enumerate.

    'What are the curses at Kinema Cinema actually revealed to be, per Chapter
    20?' resolves to the chapter (a story-typed page); the G17 field guard is
    field-only, so rule 5 handed it a partial roster that cannot answer the
    prose (page-run chapter_20 was 2/3). The narrowed `_SINGLE_VALUE_PREDICATE`
    sets `asks_single_field`, clearing rule 5, and a qa rescue before the
    story-type rule serves the fact. The speculative forms ('classified as',
    'referred to as', ...) were DROPPED on purpose: a guard that *blocks* rule 5
    must stay narrow, or it closes the roster door on a genuine set ask. The two
    spec probes below pin that those set asks keep their roster route.
    """

    @pytest.mark.parametrize(
        "query",
        [
            # The verbatim regression: a chapter-typed subject, one characterization.
            "What are the curses at Kinema Cinema actually revealed to be, per Chapter 20?",
            # The group-2 'turn out to be' twin, same page.
            "What did the victims found at Kinema Cinema turn out to be, per Chapter 20?",
        ],
    )
    def test_single_value_characterization_reaches_qa(self, query):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query).mode == "qa"

    @pytest.mark.parametrize(
        "query",
        [
            # Speculative 'classified as' is NOT in the narrowed predicate, so
            # rule 5 keeps the roster route the question wants. If a speculative
            # form were added back to the predicate, these would flip to qa.
            "What are the cursed techniques classified as?",
            "What are the special grade sorcerers referred to as?",
            # A plain plural set ask with no copular predicate (a real bank
            # question, questions/jjk.json).
            "What are Sukuna's named cursed techniques?",
        ],
    )
    def test_speculative_and_genuine_set_asks_keep_roster(self, query):
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert route(paths, query).mode == "roster"

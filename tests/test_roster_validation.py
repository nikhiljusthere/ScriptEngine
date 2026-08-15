"""Tests for the membership validator.

The failure these exist for: "Every Saiyan transformation" returned Black
Frieza. The wiki files it under `Transformations` — correctly, it is one — and
nothing downstream ever asked the second half of the question. Retrieval was
never the problem; no embedding is involved in a roster at all.
"""

from __future__ import annotations

import pytest

from scriptengine.retrieve.roster import (
    Constraints,
    Profile,
    RosterDefinition,
    _media_of,
    apply_constraints,
    parse_constraints,
    validate_member,
)
from scriptengine.stores.facts import FactStore


@pytest.fixture()
def store(tmp_path):
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    yield store
    store.close()


@pytest.fixture()
def transformations(store):
    """The Dragon Ball shape, reduced to what the validator reads."""

    def page(title, categories, facts):
        document = store.add_document(
            title=title, url="", page_type="technique", infobox_template="",
            lead=f"{title} is a thing.", word_count=4, revid=1, fetched_at="",
        )
        store.add_categories(document, categories)
        node = store.add_node(title, "technique", document)
        store.add_aliases(node, [title])
        for label, value in facts:
            store.add_fact(
                node_id=node, key=label.lower(), label=label, value=value, citation=""
            )
        store.commit()
        return node

    page("Super Saiyan", ["Transformations", "Saiyans"],
         [("Users", "Goku, Vegeta"), ("Debut", 'Manga: "Life or Death"'),
          ("Class", "Transformation")])
    page("Black Frieza", ["Transformations", "Frieza's race"],
         [("Users", "Frieza"), ("Inventor", "Frieza"),
          ("Debut", 'Manga: "The Universe\'s Strongest Appears"'),
          # The field that used to leak: what it resembles, not what it is.
          ("Similar Techniques", "Super Full Power Orange Piccolo Super Saiyan")])
    page("Class-up", ["Transformations"],
         [("Debut", "Game: Dragon Ball Heroes")])
    page("Goku", ["Saiyans"], [("Race", "Saiyan")])
    page("Frieza", ["Frieza's race"], [("Race", "Frieza Clan (mutant)")])
    # The race has its own article, which is what makes "Saiyan" a constraint
    # rather than a genre word — see `_grounded`.
    page("Saiyan", ["Races"], [("Homeworld", "Planet Vegeta")])
    return store


@pytest.fixture()
def abilities(store):
    """Abilities with the links the real wiki carries: users and an inventor."""

    def page(title, categories, facts):
        document = store.add_document(
            title=title, url="", page_type="technique", infobox_template="",
            lead=f"{title} is a thing.", word_count=4, revid=1, fetched_at="",
        )
        store.add_categories(document, categories)
        node = store.add_node(title, "technique", document)
        store.add_aliases(node, [title])
        for label, value in facts:
            store.add_fact(
                node_id=node, key=label.lower(), label=label, value=value, citation=""
            )
        return node

    def link(source, relation, target):
        store.add_edge(
            source_id=store.node_by_name(source)["id"],
            relation=relation,
            target_id=store.node_by_name(target)["id"],
            confidence=1.0,
            provenance="infobox",
            section="",
        )

    page("Saiyan", ["Races"], [("Homeworld", "Planet Vegeta")])
    page("Earthling", ["Races"], [])
    page("Goku", [], [("Race", "Saiyan")])
    page("Vegeta", [], [("Race", "Saiyan")])
    page("Krillin", [], [("Race", "Earthling")])
    page("King Kai", [], [("Race", "North Kai")])

    page("Super Saiyan", ["Transformations"], [])
    link("Super Saiyan", "inventor", "Saiyan")
    link("Super Saiyan", "user", "Goku")

    # Taught by a North Kai, used by an Earthling as well as a Saiyan.
    page("Kaio-ken", ["Transformations"], [])
    link("Kaio-ken", "inventor", "King Kai")
    link("Kaio-ken", "user", "Goku")
    link("Kaio-ken", "user", "Krillin")

    page("Ultra Ego", ["Transformations"], [])
    link("Ultra Ego", "user", "Vegeta")

    page("Nameless State", ["Transformations"], [])
    store.commit()
    return store


class TestParseConstraints:
    def test_the_qualifier_is_what_the_set_name_does_not_explain(self):
        declared = RosterDefinition.parse(
            {"name": "Transformations", "match": ["transformation"], "category": "Transformations"}
        )
        constraints = parse_constraints("Every Saiyan transformation", declared, "dragonball")
        assert constraints.qualifier == ("saiyan",)
        assert constraints.scope == "canon"

    def test_the_series_name_is_not_a_qualifier(self):
        declared = RosterDefinition.parse(
            {"name": "Races", "match": ["race"], "category": "Races"}
        )
        constraints = parse_constraints("Every race in Dragon Ball", declared, "dragonball")
        assert constraints.qualifier == ()

    @pytest.mark.parametrize(
        "query",
        [
            "Every transformation ever",
            "Every transformation including games",
            "Every non-canon transformation",
        ],
    )
    def test_asking_for_everything_widens_the_scope(self, query):
        assert parse_constraints(query, None, "").scope == "all"

    def test_canon_is_the_default(self):
        assert parse_constraints("Every transformation", None, "").scope == "canon"


class TestMediaOf:
    @pytest.mark.parametrize(
        "debut,expected",
        [
            ('Manga: "Life or Death"', ["manga"]),
            ("Game: Dragon Ball Heroes", ["game"]),
            ("Dragon Ball Fusions", ["game"]),
            ("Movie: Resurrection 'F' Manga: \"Beerus\"", ["manga", "film"]),
        ],
    )
    def test_the_debut_field_already_names_the_medium(self, debut, expected):
        assert sorted(_media_of(debut)) == sorted(expected)


class TestValidateMember:
    def test_the_reported_failure_black_frieza(self, transformations):
        """Transformation yes, Saiyan no."""
        from scriptengine.retrieve.roster import _profile

        constraints = Constraints(qualifier=("saiyan",))
        reason = validate_member(
            transformations,
            _profile(transformations, "Black Frieza"),
            constraints,
            "Transformations",
        )
        assert reason == "not saiyan"

    def test_a_saiyan_form_survives(self, transformations):
        from scriptengine.retrieve.roster import _profile

        reason = validate_member(
            transformations,
            _profile(transformations, "Super Saiyan"),
            Constraints(qualifier=("saiyan",)),
            "Transformations",
        )
        assert reason == ""

    def test_game_content_is_out_of_scope_by_default(self, transformations):
        from scriptengine.retrieve.roster import _profile

        reason = validate_member(
            transformations,
            _profile(transformations, "Class-up"),
            Constraints(),
            "Transformations",
        )
        assert "outside the story" in reason

    def test_game_content_returns_when_asked_for(self, transformations):
        from scriptengine.retrieve.roster import _profile

        reason = validate_member(
            transformations,
            _profile(transformations, "Class-up"),
            Constraints(scope="all"),
            "Transformations",
        )
        assert reason == ""

    def test_an_index_page_is_not_a_member(self, transformations):
        reason = validate_member(
            transformations, Profile(name="List of Dragon Ball films"),
            Constraints(), "Films",
        )
        assert "index page" in reason

    def test_the_set_s_own_article_is_not_a_member(self, transformations):
        """`Dragon Ball (object)` inside `Dragon Balls`."""
        reason = validate_member(
            transformations, Profile(name="Dragon Ball (object)"),
            Constraints(), "Dragon Balls",
        )
        assert "describes the set" in reason


class TestProfileIsReadOnce:
    """One candidate, one read of the store.

    A profile costs four queries — categories, facts, debut edges, and the page
    type behind each edge — and the same candidate is profiled several times over
    in one request: `apply_constraints` builds one to validate a name and another
    to test the qualifier against it, `_outside_the_story` builds a third, and
    `classify` asks for a user's twice inside a single expression.
    """

    def test_the_same_candidate_is_not_read_twice(self, transformations):
        from scriptengine.retrieve.roster import _profile

        first = _profile(transformations, "Super Saiyan")
        statements = []
        transformations.connection.set_trace_callback(statements.append)
        second = _profile(transformations, "Super Saiyan")
        transformations.connection.set_trace_callback(None)

        assert not statements, "a memoised profile must not query again"
        assert second is first
        assert second == first

    def test_a_different_candidate_is_a_different_answer(self, transformations):
        from scriptengine.retrieve.roster import _profile

        assert _profile(transformations, "Super Saiyan").name == "Super Saiyan"
        assert _profile(transformations, "Black Frieza").name == "Black Frieza"
        assert "saiyans" in _profile(transformations, "Super Saiyan").haystack()
        assert "saiyans" not in _profile(transformations, "Black Frieza").haystack()

    def test_a_reopened_store_reads_the_corpus_again(self, transformations):
        """The memo dies with the store, so `index` cannot be served stale."""
        from scriptengine.retrieve.roster import _profile

        path = transformations.path
        assert "transformations" in _profile(transformations, "Class-up").haystack()
        transformations.close()

        with FactStore(path) as store:
            store.connection.execute("DELETE FROM categories")
            store.commit()

        with FactStore(path) as store:
            assert "transformations" not in _profile(store, "Class-up").haystack()


class TestAcquisition:
    """How an ability is come by, derived from the data rather than declared.

    "Every Saiyan transformation" kept Kaio-ken because Goku is a Saiyan and
    Goku uses it. King Kai invented it and Krillin knows it: it is teachable,
    and no Saiyan biology is involved.
    """

    def test_an_ability_its_race_invented_is_exclusive_to_them(self, abilities):
        from scriptengine.retrieve.roster import RACE_EXCLUSIVE, classify, race_vocabulary

        acquired = classify(abilities, "Super Saiyan", race_vocabulary(abilities))
        assert acquired.kind == RACE_EXCLUSIVE
        assert acquired.belongs_to("saiyan")

    def test_an_ability_taught_across_races_is_teachable(self, abilities):
        from scriptengine.retrieve.roster import TEACHABLE, classify, race_vocabulary

        acquired = classify(abilities, "Kaio-ken", race_vocabulary(abilities))
        assert acquired.kind == TEACHABLE
        assert not acquired.belongs_to("saiyan")

    def test_one_user_makes_it_theirs_and_their_race_s(self, abilities):
        """Ultra Ego: Vegeta alone, so Saiyan-exclusive until someone else has it."""
        from scriptengine.retrieve.roster import CHARACTER_SPECIFIC, classify, race_vocabulary

        acquired = classify(abilities, "Ultra Ego", race_vocabulary(abilities))
        assert acquired.kind == CHARACTER_SPECIFIC
        assert acquired.belongs_to("saiyan")

    def test_no_evidence_classifies_as_unknown(self, abilities):
        from scriptengine.retrieve.roster import UNKNOWN, classify, race_vocabulary

        acquired = classify(abilities, "Nameless State", race_vocabulary(abilities))
        assert acquired.kind == UNKNOWN
        assert not acquired.belongs_to("saiyan")

    def test_it_reclassifies_itself_when_another_race_acquires_it(self, abilities):
        """The property that makes this an ontology and not a lookup table.

        Nothing is written down, so a second race learning an ability changes
        what it is with no code and no config touched.
        """
        from scriptengine.retrieve.roster import (
            CHARACTER_SPECIFIC, TEACHABLE, classify, race_vocabulary
        )

        before = classify(abilities, "Ultra Ego", race_vocabulary(abilities))
        assert before.kind == CHARACTER_SPECIFIC

        krillin = abilities.node_by_name("Krillin")["id"]
        abilities.add_edge(
            source_id=abilities.node_by_name("Ultra Ego")["id"],
            relation="user",
            target_id=krillin,
            confidence=1.0,
            provenance="infobox",
            section="",
        )
        abilities.commit()

        after = classify(abilities, "Ultra Ego", race_vocabulary(abilities))
        assert after.kind == TEACHABLE
        assert not after.belongs_to("saiyan")


class TestDisagreement:
    """What a set will and will not admit, by semantic type.

    Lives here rather than beside the type vocabulary because `_disagrees` is
    roster code: testing it from `test_semantics.py` made that module
    uncollectable at every commit before this function existed.
    """

    def test_a_planet_is_not_a_member_of_an_army(self):
        from scriptengine.retrieve import semantics
        from scriptengine.retrieve.roster import _disagrees

        assert _disagrees(semantics.LOCATION, semantics.CHARACTER)
        assert _disagrees(semantics.RACE, semantics.CHARACTER)

    def test_abilities_never_reject_each_other(self):
        """Whether a page reads `technique` or `transformation` depends on
        whether an editor filled in a `Class` field, so the majority must not
        be allowed to throw out Super Saiyan for disagreeing with the
        techniques around it."""
        from scriptengine.retrieve import semantics
        from scriptengine.retrieve.roster import _disagrees

        assert not _disagrees(semantics.TRANSFORMATION, semantics.TECHNIQUE)
        assert not _disagrees(semantics.TECHNIQUE, semantics.TRANSFORMATION)

    def test_organisations_are_never_rejected(self):
        """Wikis reach for a group infobox for anything collective, so `Angel`
        and `Shadow Dragon` are typed that way on pages about races."""
        from scriptengine.retrieve import semantics
        from scriptengine.retrieve.roster import _disagrees

        assert not _disagrees(semantics.ORGANIZATION, semantics.RACE)
        assert not _disagrees(semantics.ORGANIZATION, semantics.CHARACTER)

    def test_nothing_is_rejected_when_the_set_has_no_shape(self):
        from scriptengine.retrieve import semantics
        from scriptengine.retrieve.roster import _disagrees

        assert not _disagrees(semantics.LOCATION, semantics.UNKNOWN)
        assert not _disagrees(semantics.UNKNOWN, semantics.CHARACTER)


class TestSubpages:
    """A page's alternate-continuity view is not a second entity.

    `Every Vasto Lorde` returned six, of which `Tier Harribel` and `Tier
    Harribel/Expanded Universe` were the same hollow twice. Across four wikis
    504 titles carry a slash and 97% have their parent in the store.
    """

    def test_a_subpage_of_a_page_in_the_store_is_not_a_member(self, transformations):
        from scriptengine.retrieve.roster import _profile

        reason = validate_member(
            transformations,
            _profile(transformations, "Super Saiyan/Expanded Universe"),
            Constraints(),
            "Transformations",
        )
        assert "subpage of 'Super Saiyan'" in reason

    def test_a_slash_with_no_parent_is_left_alone(self, transformations):
        """Some titles simply contain a slash — they are not subpages of
        anything, and rejecting them would lose a real member."""
        from scriptengine.retrieve.roster import _profile

        reason = validate_member(
            transformations,
            _profile(transformations, "Nothing/Here"),
            Constraints(),
            "Transformations",
        )
        assert "subpage" not in reason


class TestCanonMedia:
    """Films are canon on Dragon Ball and not on Hunterpedia."""

    def test_film_counts_as_canon_by_default(self):
        from scriptengine.retrieve.roster import canon_media

        assert "film" in canon_media(None)
        assert "film" in canon_media({})

    def test_a_series_can_say_otherwise(self):
        from scriptengine.retrieve.roster import canon_media

        assert canon_media({"canon_media": ["manga", "anime"]}) == {"manga", "anime"}

    def test_the_declared_set_reaches_validation(self):
        """Omokage is from a non-canon film, and Hunterpedia files that film
        under `anime debut` — only the target page's type gives it away."""
        constraints = parse_constraints(
            "Every member of the Phantom Troupe", None, "",
            {"canon_media": ["manga", "anime"]},
        )
        assert constraints.canon == frozenset({"manga", "anime"})


class TestDeclaredMembers:
    def test_a_set_can_be_named_outright(self, transformations):
        """For sets no wiki filed: there is no Gods of Destruction category."""
        from scriptengine.retrieve.roster import _declared_members

        definition = RosterDefinition.parse(
            {"name": "Named", "match": ["named"], "members": ["Super Saiyan", "Goku"]}
        )
        assert _declared_members(transformations, definition) == ["Super Saiyan", "Goku"]

    def test_a_name_the_store_does_not_have_is_dropped(self, transformations):
        """So a typo shows up as a short roster rather than a silent gap."""
        from scriptengine.retrieve.roster import _declared_members

        definition = RosterDefinition.parse(
            {"name": "Named", "match": ["named"], "members": ["Super Saiyan", "Mosco"]}
        )
        assert _declared_members(transformations, definition) == ["Super Saiyan"]


class TestApplyConstraints:
    def test_it_keeps_what_belongs_and_reports_what_does_not(self, transformations):
        kept, rejected = apply_constraints(
            transformations,
            ["Super Saiyan", "Black Frieza", "Class-up"],
            Constraints(qualifier=("saiyan",)),
            "Transformations",
        )
        assert kept == ["Super Saiyan"]
        assert {entry["name"] for entry in rejected} == {"Black Frieza", "Class-up"}
        assert all(entry["reason"] for entry in rejected)

    def test_it_never_turns_a_set_into_nothing(self, transformations):
        """A wiki that labels its fields differently must not lose the answer.

        Returning the unfiltered set is wrong in a visible way; returning an
        empty one is wrong in a way that looks like the set does not exist.
        """
        # `frieza` is grounded — the wiki has an article — but no member of this
        # list satisfies it, so validation would empty the set entirely.
        names = ["Super Saiyan"]
        kept, rejected = apply_constraints(
            transformations, names, Constraints(qualifier=("frieza",)), "Transformations"
        )
        assert kept == names
        # …and it says so, rather than passing the whole set off as checked.
        # "Every Frieza Race transformation" came back as all 160 wearing the
        # same `declared` badge as a set that really had been validated.
        assert [entry["reason"] for entry in rejected] == ["__unfiltered__"]

    def test_an_unfiltered_set_is_reported_as_weak(self, transformations):
        from scriptengine.retrieve.roster import Roster

        _, rejected = apply_constraints(
            transformations, ["Super Saiyan"],
            Constraints(qualifier=("frieza",)), "Transformations",
        )
        roster = Roster(subject="x", basis="Transformations", rejected=rejected)
        assert roster.unfiltered
        assert "treat it as the wrong set" in roster.warning

    def test_a_qualifier_the_wiki_has_no_article_for_is_not_a_constraint(
        self, transformations
    ):
        """"Every Cursed Technique of Sukuna" leaves `cursed` behind, and every
        technique on that wiki is cursed. Enforcing it lost Malevolent Shrine."""
        names = ["Super Saiyan", "Black Frieza"]
        kept, _ = apply_constraints(
            transformations, names, Constraints(qualifier=("cursed",)), "Transformations"
        )
        assert kept == names

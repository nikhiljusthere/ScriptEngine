"""Questions about one character's abilities.

Measured against online canon, seventeen such questions recovered 33 of 120
canon items and eleven of them returned nothing canon at all. Two causes, and
they are opposites:

* **Precision.** `Profile.identity` mashes every value of a multi-value infobox
  field into one string, so testing a character qualifier against it matched
  `Goku` inside `Goku Black` and kept `Super Saiyan Rosé` among Goku's forms.
* **Recall.** Four of these eight wikis give abilities no page at all. Luffy's
  Gears are headings on `Monkey D. Luffy/Abilities and Powers`, so a category —
  which is filed by kind — can never reach them, and "Every form of Luffy"
  answered with forty *people*.

The cases below are the specific ones that were wrong.
"""

from __future__ import annotations

import pytest

from scriptengine.config import load_overrides, series_paths
from scriptengine.retrieve import roster as R
from scriptengine.retrieve import semantics as ontology
from scriptengine.stores.facts import FactStore


def store_for(series: str):
    paths = series_paths(series)
    if not paths.facts_db.exists():
        pytest.skip(f"{series} is not indexed")
    return paths


class TestOwnership:
    """Ownership is an edge, not a substring of the page's text."""

    def test_a_namesake_is_not_the_owner(self):
        """`Super Saiyan Rosé` belongs to Goku Black, and was Goku's."""
        paths = store_for("db")
        with FactStore(paths.facts_db) as store:
            owned = {name.lower() for name in store.owned_by("Goku", R._BELONGS_RELATIONS)}
            assert "super saiyan blue" in owned
            assert "super saiyan rose" not in {n.replace("é", "e") for n in owned}

    def test_the_inverse_query_finds_what_the_outward_one_does(self):
        """`owned_by` and `linked_from` are the same edges, read both ways."""
        paths = store_for("db")
        with FactStore(paths.facts_db) as store:
            users = {u.lower() for u in store.linked_from("Super Saiyan Blue", R._BELONGS_RELATIONS)}
            assert "goku" in users
            assert "super saiyan blue" in {
                name.lower() for name in store.owned_by("Goku", R._BELONGS_RELATIONS)
            }

    def test_a_character_qualifier_rejects_a_page_it_does_not_own(self):
        paths = store_for("db")
        with FactStore(paths.facts_db) as store:
            owned = {"goku": R._owned_pages(store, "goku")}
            constraints = R.Constraints(qualifier=("goku",))
            reason = R.validate_member(
                store, R._profile(store, "Super Saiyan Rosé"), constraints,
                "Transformations", set(), owned,
            )
            assert reason, "a page Goku does not own must not survive his qualifier"


class TestSubject:
    """Which character the question is about."""

    @pytest.mark.parametrize(
        "series,words,expected",
        [
            # Subject ranking answered these with `Yamamoto Luffy`, `Manjaro`
            # and `Nen` — a different character, a different character, and an
            # item.
            ("onepiece", ["form", "luffy"], "Monkey D. Luffy"),
            ("onepiece", ["technique", "zoro"], "Roronoa Zoro"),
            ("hxh", ["nen", "ability", "killua"], "Killua Zoldyck"),
            ("hxh", ["nen", "ability", "kurapika"], "Kurapika"),
            ("csm", ["form", "denji"], "Denji"),
        ],
    )
    def test_the_largest_page_carrying_the_name_wins(self, series, words, expected):
        paths = store_for(series)
        overrides = load_overrides(paths)
        with FactStore(paths.facts_db) as store:
            chosen = R._character_subject(
                store, words, overrides, R.race_vocabulary(store), set()
            )
            assert chosen == expected

    def test_a_race_is_never_the_character(self):
        """Otherwise "Every Saiyan transformation" is about the Saiyan article."""
        paths = store_for("db")
        overrides = load_overrides(paths)
        with FactStore(paths.facts_db) as store:
            chosen = R._character_subject(
                store, ["saiyan", "transformation"], overrides,
                R.race_vocabulary(store), set(),
            )
            assert chosen == ""


class TestKinds:
    def test_a_fusion_is_not_a_form(self):
        """`Fusion Dance` is the ritual; Gogeta and Vegito are the entities."""
        paths = store_for("db")
        overrides = load_overrides(paths)
        with FactStore(paths.facts_db) as store:
            assert ontology.semantic_type(store, "Fusion Dance", overrides) not in (
                R._asked_kinds(["form"])
            )

    def test_form_and_technique_are_different_questions(self):
        assert R._asked_kinds(["form"]) == {ontology.TRANSFORMATION}
        assert R._asked_kinds(["technique"]) == {ontology.TECHNIQUE}
        assert R._asked_kinds(["gear"]) == {ontology.TRANSFORMATION}
        assert R._asked_kinds(["shibuya", "incident"]) == set()

    def test_ability_names_the_family_not_one_of_its_members(self):
        """"Every ability of X" must not exclude what the wiki filed as a form.

        Which of `technique` and `transformation` an ability gets depends on
        whether an editor filled a `Class` field, which is why
        `semantics.ABILITY_TYPES` says the two must never reject each other. The
        kind filter did exactly that whenever the question used the umbrella
        word: Rukia's `Sode no Shirayuki` is stored, hers, and a transformation.
        """
        widen = R.widen_umbrella
        assert widen(["ability"], {ontology.TECHNIQUE}) == {
            ontology.TECHNIQUE, ontology.TRANSFORMATION}
        assert widen(["abilities"], {ontology.TECHNIQUE}) == {
            ontology.TECHNIQUE, ontology.TRANSFORMATION}

    def test_a_specific_word_stays_specific(self):
        """Only the umbrella widens. "Every technique of X" is still techniques."""
        widen = R.widen_umbrella
        assert widen(["technique"], {ontology.TECHNIQUE}) == {ontology.TECHNIQUE}
        assert widen(["form"], {ontology.TRANSFORMATION}) == {ontology.TRANSFORMATION}
        # An umbrella word that did not ask for techniques changes nothing --
        # "every weapon" stays equipment however it is phrased.
        assert widen(["ability", "weapon"], {ontology.ITEM}) == {ontology.ITEM}

    def test_a_declared_member_survives_having_no_page(self):
        """`members:` is transcribed from the wiki, not read out of the index.

        Requiring a node scored three whole questions 0: the Four Kings of the
        World are plain text in a `notable members` field, six of the Band of
        the Falcon are sections of `Minor Characters`, and Himeno's `Ghost Devil
        Contract` is described on her page rather than filed as its own.
        """
        paths = store_for("berserk")
        declared = R.RosterDefinition(
            name="test", members=("Griffith", "King of the East"))
        with FactStore(paths.facts_db) as store:
            assert store.node_by_name("Griffith") is not None
            assert store.node_by_name("King of the East") is None
            assert R._declared_members(store, declared) == [
                "Griffith", "King of the East"]

    def test_a_category_read_still_drops_what_the_store_cannot_describe(self):
        """`keep_bare` is for hand-written lists only.

        A category read returning a name with no text is a stale index, not an
        answer, so that path keeps its filter.
        """
        import inspect

        source = inspect.getsource(R.build_roster)
        assert "keep_bare=bool(declared.members)" in source

    def test_a_roster_may_declare_the_person_it_is_about(self):
        """`subject:` is the exception to "a person beats a declared set".

        Without it "Every ability of Serpico" answers from his page's section
        headings while the three items the wiki lists sit in the store filed as
        equipment, which an ability question never asks for.
        """
        declared = R.RosterDefinition.parse({
            "name": "Serpico's abilities",
            "match": ["ability of serpico"],
            "subject": "Serpico",
            "members": ["Rapier", "Sylph Sword", "Sylph Cloak"],
        })
        assert declared.subject == "Serpico"
        assert declared.members == ("Rapier", "Sylph Sword", "Sylph Cloak")

        # Absent by default, so every existing declaration keeps the old
        # behaviour and the general path still wins.
        plain = R.RosterDefinition.parse({"name": "Apostles",
                                          "category": "Apostles"})
        assert plain.subject == ""

    def test_a_subject_roster_does_not_make_its_person_unnameable(self):
        """Declaring "…Saitama uses" must not stop `Saitama` naming a person.

        The set vocabulary exists so a word that names a set cannot also
        identify a character. A `subject:` roster names the person deliberately,
        so folding its words in taught the resolver that `saitama`, `garou`,
        `genos`, `bang` and `tatsumaki` were set words. Measured with 36 such
        rosters declared: every character-scoped One-Punch Man question fell to
        0% precision, including ones with nothing to do with the new sets.
        """
        registry = [
            R.RosterDefinition.parse({
                "name": "Every named Serious Series technique Saitama uses",
                "match": ["named serious series technique saitama uses"],
                "subject": "Saitama", "members": ["Serious Punch"]}),
            R.RosterDefinition.parse({
                "name": "Heroes", "match": ["hero", "heroes"],
                "category": "Heroes"}),
        ]
        vocabulary = {
            word
            for definition in registry
            if not definition.subject
            for phrase in (*definition.match, definition.name)
            for word in R.content_words(phrase)
        }
        assert "saitama" not in vocabulary, \
            "a subject roster poisoned the set vocabulary with its person"
        assert "heroes" in vocabulary or "hero" in vocabulary

    def test_a_stopword_is_dropped_whichever_path_found_it(self):
        """A declared non-ability must not come back as a heading or an edge.

        `ability_stopwords` gated the prose path alone, so `Other Abilities`
        still arrived as a heading and Dragon Ball's game-only fusions arrived
        both ways -- 65 members of one run, none of them canon anywhere.
        """
        overrides = {"ability_stopwords": ["Physical Abilities", "Vegecell"]}
        kept = R.drop_stopwords(
            ["Kamehameha", "Physical Abilities", "vegecell", "Instant Transmission"],
            overrides,
        )
        assert kept == ["Kamehameha", "Instant Transmission"]

    def test_a_series_with_no_stopwords_keeps_everything(self):
        assert R.drop_stopwords(["Rasengan"], {}) == ["Rasengan"]
        assert R.drop_stopwords(["Rasengan"], None) == ["Rasengan"]

    def test_equipment_is_never_admitted_by_the_umbrella(self):
        """`item` stays out, which is why `ABILITY_TYPES` excludes it too.

        Measured on the closed questions using an umbrella word: admitting items
        costs 35 wrong names to gain 18 right ones, where transformations alone
        gain 13 for 11. A zanpakutō is equipment, not an ability.
        """
        assert ontology.ITEM not in ontology.ABILITY_TYPES
        assert ontology.ITEM not in R.widen_umbrella(
            ["ability"], {ontology.TECHNIQUE})


class TestEndToEnd:
    def test_a_namesake_is_gone_from_gokus_forms(self):
        paths = store_for("db")
        roster = R.build_roster(paths, "Every form of Goku")
        names = {member.name for member in roster.members}
        assert "Super Saiyan Blue" in names
        # A ritual, not a form: the fusion *results* are the entities.
        assert "Fusion Dance" not in names
        # Goku Black's form, kept only because "goku" is inside "Goku Black".
        assert not any(name.startswith("Super Saiyan Ros") for name in names)
        # `Ultimate` is deliberately not asserted. It is Gohan's, and the wiki
        # does record Goku as one of its eighteen users — through Xenoverse.
        # The page's own debut is canon, because it is canon for Gohan, and
        # nothing in the data marks one user's use of a page as non-canon while
        # another's is. Removing it needs per-user scope the wiki does not
        # store, so it stays and is reported as a known miss.
        # The bound here used to be 42, the size of the unfiltered
        # `Transformations` category, because that category was the source.
        # It is not any more: the answer is now Goku's own
        # `Power and Abilities` page — whose 36 `;`-marked forms became real
        # headings — unioned with the pages he owns. More members, and more of
        # them right: canon recall on this question went 8 of 12 to 11 of 12.
        #
        # What still has to hold is that it is *his* list and not the series':
        # the category path offered 160 candidates.
        assert len(names) < 80, "this is Goku's page, not the series' category"

    def test_luffys_gears_come_from_headings(self):
        """They are `Devil Fruit / Gear 2`, not pages, and not `Former Pirates`."""
        paths = store_for("onepiece")
        roster = R.build_roster(paths, "Every Gear of Luffy")
        names = " ".join(member.name for member in roster.members).lower()
        assert "gear 2" in names and "gear 3" in names
        assert roster.confidence == "partial", "a heading is not a curated set"

    def test_two_characters_do_not_share_one_answer(self):
        """Killua and Kurapika both returned the identical 13 Greed Island cards."""
        paths = store_for("hxh")
        killua = R.build_roster(paths, "Every Nen ability of Killua")
        kurapika = R.build_roster(paths, "Every Nen ability of Kurapika")
        assert killua.basis != kurapika.basis

    def test_a_name_filtered_set_is_not_a_declared_answer(self):
        """Frieza's four came back `declared` holding two of his eight forms."""
        paths = store_for("db")
        roster = R.build_roster(paths, "Every transformation of Frieza")
        assert roster.confidence != "declared"

    def test_thin_ownership_does_not_claim_to_be_exact(self):
        """Bleach records one user edge for Ichigo across the whole wiki."""
        paths = store_for("bleach")
        roster = R.build_roster(paths, "Every technique of Ichigo Kurosaki")
        assert roster.confidence in ("partial", "weak", "")

    def test_headings_and_prose_are_added_not_chosen_between(self):
        """Luffy's Gears are split across the two readings of one page.

        The headings on his abilities page are `Gear 2`, `Gear 3`, `Gear 4` and
        `Gear 5 (Awakening)`; the prose under them names `Boundman`, `Tankman`
        and `Snakeman`. Preferring either one scored 3 of 6 — the union scores
        5, and no ordering of the two could have.
        """
        paths = store_for("onepiece")
        roster = R.build_roster(paths, "Every Gear of Luffy")
        names = " ".join(member.name for member in roster.members).lower()
        if "boundman" not in names:
            pytest.skip("prose abilities have not been extracted for this store")
        assert "gear 2" in names and "gear 3" in names
        assert "snakeman" in names and "tankman" in names
        assert roster.confidence == "partial"

    def test_extracted_abilities_never_claim_more_than_partial(self):
        """A model read them; the wiki did not file them."""
        paths = store_for("hxh")
        roster = R.build_roster(paths, "Every Nen ability of Killua")
        assert roster.confidence == "partial"

    @pytest.mark.parametrize(
        "name",
        [
            # Debuts in `Super Heroes are Born`, a Dragon Ball Super chapter.
            # A bare "heroes" substring test threw him out of the Red Ribbon
            # Army, along with Gamma 1 and Cell Max.
            "Dr. Hedo",
            "Gamma 1",
            "Cell Max",
            # Names Dragon Ball Heroes among its debuts and first appeared in
            # Resurrection 'F'. An any-test would drop it.
            "Super Saiyan Blue",
            # Names Heroes: Victory Mission and debuted in GT.
            "Super Saiyan 4",
            "Ultra Ego",
            "Perfected Ultra Instinct",
        ],
    )
    def test_a_canon_page_naming_a_game_survives(self, name):
        paths = store_for("db")
        overrides = load_overrides(paths)
        with FactStore(paths.facts_db) as store:
            profile = R._profile(store, name)
            if not profile.works:
                pytest.skip(f"{name} has no debut edges in this store")
            assert not R._game_only(store, profile, R.non_canon_works(overrides))

    @pytest.mark.parametrize(
        "name",
        [
            "Super Saiyan (Berserk)",
            "Super Saiyan God Super Saiyan (Universe Tree Power)",
            "Super Saiyan Rosé 2",
            "Evil Saiyan",
            "Xeno Cell",
            "Villainous Mode",          # Xenoverse, not Heroes
        ],
    )
    def test_a_page_only_a_game_ever_showed_is_dropped(self, name):
        """These are no longer filtered at query time — they are not indexed.

        `_game_only` used to be the assertion here. It cannot be any more:
        the page is gone from the store, so `_profile` returns nothing to
        judge. Absence is the stronger guarantee, and the one the declaration
        in `series/db/overrides.yaml` now buys.

        Checked against `documents` rather than `nodes`. A page other pages
        link to keeps a bare, unresolved node so the link is not silently
        lost — that is the graph working as designed, and it carries no text,
        no sections and no edges of its own.
        """
        paths = store_for("db")
        with FactStore(paths.facts_db) as store:
            row = store.connection.execute(
                "SELECT id FROM documents WHERE title = ? COLLATE NOCASE", (name,)
            ).fetchone()
            assert row is None

    def test_goku_keeps_his_forms_and_loses_the_games(self):
        paths = store_for("db")
        names = {m.name for m in R.build_roster(paths, "Every form of Goku").members}
        assert "Super Saiyan Blue" in names and "Super Saiyan 4" in names
        assert "Super Saiyan (Berserk)" not in names
        assert "Super Saiyan God Super Saiyan (Universe Tree Power)" not in names

    @pytest.mark.parametrize(
        "query,scope",
        [
            ("Every Saiyan transformation", "canon"),
            ("Every form of Goku", "canon"),
            ("Every Super Dragon Ball Heroes transformation", "all"),
            ("Every Xenoverse transformation", "all"),
            ("Every Dokkan Battle character", "all"),
        ],
    )
    def test_naming_the_work_asks_for_it_back(self, query, scope):
        """Without this the exclusion is a deletion, not an exclusion."""
        paths = store_for("db")
        overrides = load_overrides(paths)
        assert R.parse_constraints(query, None, "Dragon Ball", overrides).scope == scope

    @pytest.mark.parametrize(
        "series,query,basis",
        [
            ("db", "Every Saiyan transformation", "Transformations"),
            ("db", "Every Frieza Race transformation", "Transformations"),
            ("hxh", "Every Nen type", "Nen Types"),
            ("bleach", "Every Espada", "Espada"),
        ],
    )
    def test_set_questions_are_untouched(self, series, query, basis):
        """The character path must not reach a question about a race or a set."""
        paths = store_for(series)
        assert R.build_roster(paths, query).basis == basis

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
        assert len(names) < 42, "the unfiltered category answer was 42"

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

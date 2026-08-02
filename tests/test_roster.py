"""Tests for enumeration retrieval and subject ranking.

Between them these cover the two failures that made most script topics
unanswerable: "Every Rank of Curse in Jujutsu Kaisen" resolving to the series
page and returning one beat from `Volume 0`, and no mode able to return a set.
"""

from __future__ import annotations

import pytest

from scriptengine.config import SUBJECT_DEMOTE_TYPES, SUBJECT_TYPE_PRIORITY, subject_ranking
from scriptengine.retrieve.roster import (
    _choose_set,
    _grouping_field,
    _member_order,
    _work_words,
    Member,
    content_words,
    looks_like_enumeration,
)
from scriptengine.stores.facts import FactStore, rank_subjects


@pytest.fixture()
def store(tmp_path):
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    yield store
    store.close()


@pytest.fixture()
def wiki(store):
    """A miniature wiki: a series page, some curses, and the categories."""
    def page(title, page_type, categories=(), facts=()):
        document = store.add_document(
            title=title, url="", page_type=page_type, infobox_template="",
            lead=f"{title} is a thing.", word_count=4, revid=1, fetched_at="",
        )
        store.add_categories(document, categories)
        node = store.add_node(title, page_type, document)
        store.add_aliases(node, [title])
        for key, label, value in facts:
            store.add_fact(node_id=node, key=key, label=label, value=value, citation="")
        return node

    page("Jujutsu Kaisen", "series")
    page("Cursed Spirit", "species", ["Terminology"])
    curses = [
        ("Jogo", "Special Grade"),
        ("Hanami", "Special Grade"),
        ("Dagon", "Special Grade"),
        ("Ko-Guy", "Grade 2"),
        ("Kuchisake-Onna", "Grade 1"),
    ]
    for name, grade in curses:
        page(
            name, "character", ["Cursed Spirits"],
            [("class", "Grade", grade), ("status", "Status", "Deceased")],
        )
    store.add_aliases(store.node_by_name("Cursed Spirit")["id"], ["curse"])
    store.commit()
    return store


class TestSubjectRanking:
    def test_the_lists_are_overridable_per_wiki(self, tmp_path):
        demote, priority = subject_ranking({"subject_demote_types": ["episode"]})
        assert demote == ["episode"]
        assert priority == list(SUBJECT_TYPE_PRIORITY)

    def test_the_defaults_are_used_when_a_wiki_says_nothing(self):
        assert subject_ranking({}) == (
            list(SUBJECT_DEMOTE_TYPES), list(SUBJECT_TYPE_PRIORITY)
        )

    def test_the_series_page_stops_winning(self, wiki):
        # "Every Rank of Curse in Jujutsu Kaisen" resolved to `Jujutsu Kaisen`
        # on an exact alias match and came back as one beat from `Volume 0`.
        demote, priority = subject_ranking({})
        rows = rank_subjects(
            wiki.link_entities("Every Rank of Curse in Jujutsu Kaisen"), demote, priority
        )
        assert rows[0]["name"] != "Jujutsu Kaisen"

    def test_a_character_outranks_a_concept_page(self, wiki):
        # "Every Cursed Technique of Sukuna" resolved to the generic
        # `Cursed Technique` page, because it matched on a longer alias.
        wiki.add_aliases(wiki.add_node("Sukuna", "character", None), ["sukuna"])
        wiki.connection.execute("UPDATE nodes SET is_resolved = 1 WHERE name = 'Sukuna'")
        wiki.add_aliases(
            wiki.add_node("Cursed Technique", "technique", None), ["cursed technique"]
        )
        wiki.connection.execute(
            "UPDATE nodes SET is_resolved = 1 WHERE name = 'Cursed Technique'"
        )
        demote, priority = subject_ranking({})
        rows = rank_subjects(
            wiki.link_entities("Every Cursed Technique of Sukuna"), demote, priority
        )
        assert rows[0]["name"] == "Sukuna"

    def test_a_demoted_page_still_wins_when_nothing_else_matches(self, wiki):
        demote, priority = subject_ranking({})
        rows = rank_subjects(wiki.link_entities("Jujutsu Kaisen"), demote, priority)
        assert rows[0]["name"] == "Jujutsu Kaisen"


class TestEnumerationDetection:
    @pytest.mark.parametrize(
        "query",
        [
            "Every Apostle in Berserk Explained",
            "All Forbidden Jutsu in Naruto",
            "Every Level of the Abyss",
            "What It's Like to be Every Rank of Curse",
        ],
    )
    def test_a_set_topic_is_recognised(self, query):
        assert looks_like_enumeration(query)

    @pytest.mark.parametrize(
        "query", ["Shibuya Incident", "How did Gojo get sealed", "The Dark Continent"]
    )
    def test_an_account_is_not_a_set(self, query):
        assert not looks_like_enumeration(query)

    def test_the_words_that_name_the_set_are_kept(self):
        assert content_words("Every Rank of Curse in Jujutsu Kaisen") == [
            "rank", "curse", "jujutsu", "kaisen"
        ]


class TestChoosingTheSet:
    def test_a_category_the_wiki_curated_is_the_set(self, wiki):
        chosen = _choose_set(wiki, ["rank", "curse"], "Cursed Spirit", "species")
        assert chosen is not None
        kind, basis, names = chosen
        assert (kind, basis) == ("category", "Cursed Spirits")
        assert "Jogo" in names and len(names) == 5

    def test_the_words_naming_the_work_are_dropped_from_the_query(self, wiki):
        # "Jujutsu Kaisen" appears in most category names on a Jujutsu Kaisen
        # wiki. Left in the query they matched all of them, and "Every Domain
        # Expansion in Jujutsu Kaisen" enumerated the Modulo chapters.
        assert _work_words(wiki) == {"jujutsu", "kaisen"}

    def test_a_query_matching_nothing_returns_nothing(self, wiki):
        assert _choose_set(wiki, ["quidditch"], "Quidditch", "") is None


class TestGrouping:
    def test_a_tier_field_is_found_through_the_wikis_own_label(self, wiki):
        # The query says "rank", the wiki keys it `class` and labels it "Grade".
        names = ["Jogo", "Hanami", "Dagon", "Ko-Guy", "Kuchisake-Onna"]
        assert _grouping_field(wiki, names, ["rank", "curse"]) == ("class", "Grade")

    def test_a_status_field_is_not_a_tier(self, wiki):
        # Every member is "Deceased", which groups a roster into one group and
        # says nothing about the ranks the query asked for.
        names = ["Jogo", "Hanami", "Dagon", "Ko-Guy", "Kuchisake-Onna"]
        key, _ = _grouping_field(wiki, names, ["rank", "curse"])
        assert key != "status"

    def test_no_grouping_is_asked_for_and_none_is_invented(self, wiki):
        names = ["Jogo", "Hanami", "Dagon", "Ko-Guy", "Kuchisake-Onna"]
        assert _grouping_field(wiki, names, ["curse"]) == ("", "")


class TestMemberOrdering:
    def test_numbered_groups_sort_numerically(self):
        members = [
            Member(name="c", group="Grade 4"),
            Member(name="a", group="Grade 1"),
            Member(name="b", group="Grade 2"),
        ]
        members.sort(key=_member_order)
        assert [member.group for member in members] == ["Grade 1", "Grade 2", "Grade 4"]

    def test_unnumbered_groups_come_after_numbered_ones(self):
        members = [
            Member(name="a", group="Special Grade"),
            Member(name="b", group="Grade 2"),
        ]
        members.sort(key=_member_order)
        assert members[0].group == "Grade 2"

    def test_ungrouped_members_come_last(self):
        members = [Member(name="a"), Member(name="b", group="Grade 1")]
        members.sort(key=_member_order)
        assert members[0].name == "b"

    def test_members_of_a_group_stay_together(self):
        members = [
            Member(name="Jogo", group="Special Grade"),
            Member(name="Ko-Guy", group="Grade 2"),
            Member(name="Hanami", group="Special Grade"),
        ]
        members.sort(key=_member_order)
        assert [member.group for member in members] == [
            "Grade 2", "Special Grade", "Special Grade"
        ]

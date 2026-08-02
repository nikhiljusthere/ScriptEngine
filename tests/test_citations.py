"""Tests for turning wiki references into locators a script can say."""

from __future__ import annotations

import pytest

from scriptengine.retrieve.citations import (
    EpisodeIndex,
    Locator,
    attribute,
    coverage,
    locators,
    parse_locator,
    parse_markers,
    span,
    upgrade_markers,
)
from scriptengine.stores.facts import FactStore


@pytest.fixture()
def store(tmp_path):
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    yield store
    store.close()


class TestLocators:
    def test_a_marker_is_read_back_into_its_parts(self):
        locator = parse_locator("(Chapter 145, Episode 50)")
        assert locator.chapter == "145"
        assert locator.episode == "50"

    def test_a_chapter_only_marker_has_no_episode(self):
        assert parse_locator("(Chapter 242)").episode == ""

    def test_part_numbers_survive(self):
        assert parse_locator("(Chapter 0-4, Episode 4)").chapter == "0-4"

    def test_a_sequel_chapter_carries_its_work(self):
        locator = parse_locator("(Modulo Chapter 16)")
        assert (locator.work, locator.chapter) == ("Modulo", "16")
        assert locator.render() == "(Modulo Chapter 16)"

    def test_a_sequel_chapter_never_gains_an_episode(self):
        # The map is built from the main series' adaptation edges, so completing
        # a sequel chapter from it hands it an episode of the wrong anime.
        index = EpisodeIndex({"16": "7"})
        assert index.complete(parse_locator("(Modulo Chapter 16)")).episode == ""
        assert index.complete(parse_locator("(Chapter 16)")).episode == "7"

    def test_ordinary_prose_is_not_a_citation(self):
        assert parse_markers("They mention (the Chapter 5 fight) in passing.") == []

    def test_an_empty_locator_is_falsey(self):
        assert not Locator()
        assert Locator(chapter="1")

    def test_rendering_round_trips(self):
        assert parse_locator("(Chapter 8, Episode 4)").render() == "(Chapter 8, Episode 4)"

    def test_markers_are_found_where_they_sit(self):
        text = "He was sealed.(Chapter 90) Then freed.(Chapter 221, Episode 60)"
        found = parse_markers(text)
        assert [locator.chapter for _, _, locator in found] == ["90", "221"]
        assert found[0][0] < found[1][0]

    def test_ordinary_parentheses_are_not_markers(self):
        assert parse_markers("Yuji Itadori (the vessel) fights.") == []


class TestEpisodeIndex:
    def test_both_adaptation_relations_are_read(self, store):
        # Neither is complete on its own: on the Jujutsu Kaisen wiki
        # `anime episode` covers 185 chapters and `adapted from` covers 181.
        chapter = store.add_node("Chapter 1", "chapter")
        episode = store.add_node("Episode 1", "episode")
        other = store.add_node("Chapter 79", "chapter")
        thirty = store.add_node("Episode 30", "episode")
        store.add_edge(
            source_id=chapter, relation="anime episode", target_id=episode,
            confidence=0.95, provenance="infobox", section="",
        )
        store.add_edge(
            source_id=thirty, relation="adapted from", target_id=other,
            confidence=0.95, provenance="infobox", section="",
        )

        index = EpisodeIndex.from_store(store)
        assert index.episode_for("1") == "1"
        assert index.episode_for("79") == "30"

    def test_a_movie_is_not_an_episode(self, store):
        chapter = store.add_node("Chapter 0-1", "chapter")
        movie = store.add_node("Jujutsu Kaisen 0: The Movie", "anime")
        store.add_edge(
            source_id=chapter, relation="anime episode", target_id=movie,
            confidence=0.95, provenance="infobox", section="",
        )
        assert EpisodeIndex.from_store(store).episode_for("0-1") == ""

    def test_an_unadapted_chapter_stays_unadapted(self):
        # The wiki cites chapters the anime has not reached. Inventing an
        # episode for them is exactly what the annotation rules forbid.
        assert EpisodeIndex({"79": "30"}).complete(Locator(chapter="266")) == Locator(
            chapter="266"
        )

    def test_an_episode_already_stated_is_left_alone(self):
        index = EpisodeIndex({"79": "99"})
        assert index.complete(Locator(chapter="79", episode="30")).episode == "30"


class TestUpgradeMarkers:
    def test_a_chapter_gains_its_episode(self):
        text = upgrade_markers("He fought.(Chapter 79)", EpisodeIndex({"79": "30"}))
        assert text == "He fought.(Chapter 79, Episode 30)"

    def test_an_unmapped_chapter_is_untouched(self):
        text = "He fought.(Chapter 266)"
        assert upgrade_markers(text, EpisodeIndex({"79": "30"})) == text

    def test_no_index_changes_nothing(self):
        assert upgrade_markers("He fought.(Chapter 79)", None) == "He fought.(Chapter 79)"


class TestAttribution:
    # MediaWiki puts one reference at the end of the passage it supports. Only
    # 12.8% of the sentences in a fetched Shibuya Incident bundle carried a
    # locator; reading each reference as covering the sentences before it is
    # what the citation means, and what makes every block taggable.

    def test_a_reference_covers_the_sentences_before_it(self):
        found = attribute("Alpha. Beta. Gamma.(Chapter 145, Episode 50)")
        assert [s.locator.chapter for s in found] == ["145", "145", "145"]
        assert [s.inherited for s in found] == [True, True, False]

    def test_each_reference_covers_only_back_to_the_previous_one(self):
        found = attribute("Alpha.(Chapter 10) Beta. Gamma.(Chapter 20)")
        assert [s.locator.chapter for s in found] == ["10", "20", "20"]

    def test_sentences_after_the_last_reference_fall_back_to_it(self):
        found = attribute("Alpha.(Chapter 10) Beta. Gamma.")
        assert [s.locator.chapter for s in found] == ["10", "10", "10"]

    def test_prose_with_no_reference_gets_no_locator(self):
        assert all(not s.locator for s in attribute("Alpha. Beta."))

    def test_episodes_are_filled_in_while_attributing(self):
        found = attribute("Alpha. Beta.(Chapter 79)", EpisodeIndex({"79": "30"}))
        assert all(s.locator.episode == "30" for s in found)

    def test_empty_text_yields_nothing(self):
        assert attribute("") == []


class TestSpan:
    def test_one_place_reads_as_one_place(self):
        assert span([Locator(chapter="145", episode="50")]) == "Chapter 145, Episode 50"

    def test_two_places_are_named(self):
        found = [Locator(chapter="10"), Locator(chapter="16")]
        assert span(found) == "Chapters 10 and 16"

    def test_a_run_collapses_to_a_range(self):
        found = [Locator(chapter=str(n)) for n in (90, 91, 92)]
        assert span(found) == "Chapters 90-92"

    def test_chapters_sort_numerically(self):
        found = [Locator(chapter="100"), Locator(chapter="9")]
        assert span(found) == "Chapters 9 and 100"

    def test_nothing_sourced_spans_nothing(self):
        assert span([]) == ""

    def test_each_work_is_ranged_separately(self):
        # Merging them gives "Chapters 16-235", a range spanning two manga that
        # contains neither of the chapters actually cited.
        found = [
            Locator(chapter="235"),
            Locator(chapter="16", work="Modulo"),
            Locator(chapter="15", work="Modulo"),
        ]
        assert span(found) == "Chapter 235, Modulo Chapters 15 and 16"

    def test_locators_are_distinct_and_in_order(self):
        found = locators(attribute("A.(Chapter 5) B.(Chapter 5) C.(Chapter 6)"))
        assert [locator.chapter for locator in found] == ["5", "6"]


class TestCoverage:
    def test_inheritance_is_reported_separately_from_direct_citation(self):
        # `cited_directly` is where the wiki wrote a reference; `with_chapter`
        # is what those references cover. Conflating them would hide the failure
        # this metric exists to catch.
        measured = coverage("Alpha. Beta. Gamma.(Chapter 145, Episode 50)")
        assert measured["sentences"] == 3
        assert measured["with_chapter"] == 3
        assert measured["with_episode"] == 3
        assert measured["cited_directly"] == 1

    def test_uncited_prose_scores_zero(self):
        measured = coverage("Alpha. Beta.")
        assert measured["with_chapter"] == 0

"""Tests for the scoring that decides which set a topic means.

These cover the failure that made every enumeration on the two largest wikis
wrong: a query naming the series — "Every race in Dragon Ball" — handed its
words to every category the wiki had named after itself, so `Dragon Ball Z
episodes` outscored `Races` and the answer came back as 150 episode titles.
One Piece did the same thing with `One Piece Volumes`.
"""

from __future__ import annotations

import json

import pytest

from scriptengine.config import series_paths
from scriptengine.retrieve.roster import (
    RosterDefinition,
    _asks_for_packaging,
    _score,
    content_words,
    rate_match,
    strip_work_title,
    work_title,
)


class TestStripWorkTitle:
    def test_removes_the_series_name(self):
        assert strip_work_title("Every race in Dragon Ball", "dragonball") == (
            "Every race in"
        )

    def test_removes_it_from_a_category_name(self):
        assert strip_work_title("Dragon Ball Z episodes", "dragonball") == "Z episodes"
        assert strip_work_title("One Piece Volumes", "onepiece") == "Volumes"

    def test_keeps_a_name_that_only_looks_like_the_title(self):
        """The adversarial case, and the reason matching is exact.

        "Dragon Balls" concatenates to `dragonballs`, which is not the wiki's
        name, so the object keeps the words that identify it. Stripping here
        would delete the entire query.
        """
        assert strip_work_title("All types of Dragon Balls", "dragonball") == (
            "All types of Dragon Balls"
        )

    def test_leaves_everything_else_alone(self):
        assert strip_work_title("Every Cursed Technique", "jujutsukaisen") == (
            "Every Cursed Technique"
        )

    def test_no_title_is_a_no_op(self):
        assert strip_work_title("Every race", "") == "Every race"

    def test_survives_an_empty_query(self):
        assert strip_work_title("", "dragonball") == ""


class TestWorkTitle:
    def test_reads_the_host_from_the_manifest(self, tmp_path, monkeypatch):
        paths = series_paths("db")
        monkeypatch.setattr(
            type(paths), "manifest", property(lambda self: tmp_path / "manifest.json")
        )
        (tmp_path / "manifest.json").write_text(
            json.dumps({"wiki": "https://dragonball.fandom.com"}), encoding="utf-8"
        )
        assert work_title(paths) == "dragonball"

    def test_missing_manifest_is_not_an_error(self, tmp_path, monkeypatch):
        paths = series_paths("db")
        monkeypatch.setattr(
            type(paths), "manifest", property(lambda self: tmp_path / "absent.json")
        )
        assert work_title(paths) == ""


class TestPackaging:
    @pytest.mark.parametrize(
        "query", ["Every One Piece movie", "Every volume", "All the episodes"]
    )
    def test_recognises_a_request_for_packaging(self, query):
        assert _asks_for_packaging(content_words(query))

    def test_a_story_question_is_not_one(self):
        assert not _asks_for_packaging(content_words("Every race"))

    def test_packaging_loses_when_it_was_not_asked_for(self):
        """`Z episodes` must not beat `Races` for a question about races."""
        words = content_words("Every race")
        episodes, _ = _score("Z episodes", words, [], wants_packaging=False)
        races, _ = _score("Races", words, [], wants_packaging=False)
        assert races > episodes

    def test_packaging_still_wins_when_it_was_asked_for(self):
        words = content_words("Every movie")
        movies, _ = _score("Movies", words, [], wants_packaging=True)
        assert movies > 0


class TestRateMatch:
    """Discovery cannot refuse to answer, so it has to say how sure it is."""

    def test_a_name_the_topic_explains_is_exact(self):
        confidence, unmatched = rate_match("Races", content_words("Every race"), [])
        assert (confidence, unmatched) == ("exact", [])

    def test_an_extra_word_makes_it_partial_and_names_the_word(self):
        """The failure this exists for: the crew's weapons, not the crew."""
        confidence, unmatched = rate_match(
            "Straw Hat Pirates' Creations",
            content_words("Every Straw Hat Pirate"),
            [],
        )
        assert confidence == "partial"
        assert unmatched == ["creations"]

    def test_matching_nothing_the_topic_asked_for_is_weak(self):
        confidence, _ = rate_match(
            "Rosward Family", content_words("Every Saiyan in One Piece"), []
        )
        assert confidence == "weak"

    def test_the_subject_can_account_for_a_word(self):
        confidence, unmatched = rate_match(
            "Cursed Spirits", content_words("Every rank of curse"), ["spirit"]
        )
        assert (confidence, unmatched) == ("exact", [])

    def test_a_warning_is_only_raised_when_there_is_something_to_say(self):
        from scriptengine.retrieve.roster import Roster

        assert not Roster(subject="x", confidence="exact").warning
        assert not Roster(subject="x", confidence="declared").warning
        assert "creations" in Roster(
            subject="x", basis="Straw Hat Pirates' Creations",
            confidence="partial", unmatched=["creations"],
        ).warning


class TestDeclarationShapes:
    def test_categories_declares_a_union(self):
        """Distinct from `groups`, where the groups are themselves the members."""
        definition = RosterDefinition.parse(
            {
                "name": "Races and Tribes",
                "match": ["race"],
                "categories": ["Races and Tribes", "Artificial Races"],
            }
        )
        assert definition.categories == ("Races and Tribes", "Artificial Races")
        assert not definition.groups

    def test_sections_of_declares_a_page(self):
        definition = RosterDefinition.parse(
            {"name": "Marine Ranks", "match": ["marine rank"], "sections_of": "Marine Ranks"}
        )
        assert definition.sections_of == "Marine Ranks"

    def test_a_bare_series_name_would_match_everything(self):
        """Why `Dragon Balls` declares only the qualified phrasings.

        Declaring a bare "dragon ball" made every enumeration on that wiki
        resolve to the Dragon Balls set, because every one of them says the
        series' name somewhere.
        """
        greedy = RosterDefinition.parse(
            {"name": "Dragon Balls", "match": ["dragon ball"], "category": "Balls"}
        )
        assert greedy.matches("Every race in Dragon Ball")

        declared = RosterDefinition.parse(
            {
                "name": "Dragon Balls",
                "match": ["type of dragon ball", "types of dragon ball"],
                "category": "Balls",
            }
        )
        assert not declared.matches("Every race in Dragon Ball")
        assert declared.matches("All types of Dragon Balls")

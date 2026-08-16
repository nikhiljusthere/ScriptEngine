"""Scoring the relations table, which the canon bank does not reach.

The gap this covers is not a bug in any one function. `canon-run` has no
relation-shaped set question on any wiki, and `build_roster` never reads the
relations table, so 22,700 extracted rows sat outside every number the project
quotes. A declaration that changed them -- `relation_sections` -- therefore
could not be kept or reverted on evidence.

These run on a store built in the test, so they assert the scoring rules
rather than any wiki's contents.
"""

from __future__ import annotations

import json

import pytest

from scriptengine.eval import relation_coverage as R
from scriptengine.stores.facts import FactStore


def _save(store, rows):
    """`save_relations` replaces one character at a time, so group first."""
    by_subject: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_subject.setdefault(row["character"], []).append(row)
    for character, found in by_subject.items():
        store.save_relations(character, found, 1, "test", "test-model")


def _bank(tmp_path, questions, series="csm"):
    root = tmp_path / "questions"
    root.mkdir(exist_ok=True)
    (root / f"_{series}_relations.json").write_text(
        json.dumps({"series": series, "questions": questions}), encoding="utf-8"
    )
    return root


class TestDirection:
    def test_a_partner_counts_from_either_end(self, tmp_path, monkeypatch):
        """The wiki writes the relationship on whichever page it feels like.

        Geto's page carries the Gojo relationship and Gojo's may not carry
        Geto's, so a gold pair scored one-way would report a miss on a
        relationship the store holds. Here the row is written on Aki's page and
        the question is asked about Denji.
        """
        paths = _prepare(tmp_path, monkeypatch, rows=[
            {"character": "Aki Hayakawa", "other": "Denji", "relation": "ally",
             "section": "Relationships / Denji", "quote": "they live together"},
        ], gold=["Aki Hayakawa"])
        report = R.score("csm", paths)
        assert report["summary"]["recall"] == 1.0
        assert report["rows"][0]["missing"] == []


class TestSectionSplit:
    @pytest.mark.parametrize(
        "section,descriptive",
        [
            ("Relationships / Denji", True),
            ("Relationships", True),
            ("Synopsis / Public Safety Saga / Katana Man arc", False),
            ("Plot / Academy Saga", False),
            ("History", False),
        ],
    )
    def test_description_is_told_from_narration(self, section, descriptive):
        """The declaration question turns on exactly this split."""
        assert R._descriptive(section) is descriptive


class TestScoring:
    def test_a_documented_partner_the_store_holds_is_recall(self, tmp_path, monkeypatch):
        paths = _prepare(tmp_path, monkeypatch, rows=[
            {"character": "Denji", "other": "Power", "relation": "friend",
             "section": "Relationships / Power", "quote": "they live together"},
        ], gold=["Power"])
        report = R.score("csm", paths)
        assert report["summary"]["found"] == 1
        assert report["summary"]["recall"] == 1.0

    def test_a_documented_partner_the_store_lacks_is_a_miss(self, tmp_path, monkeypatch):
        paths = _prepare(tmp_path, monkeypatch, rows=[], gold=["Power"])
        report = R.score("csm", paths)
        assert report["rows"][0]["missing"] == ["Power"]
        assert report["summary"]["recall"] == 0.0

    def test_a_partner_the_wiki_never_headed_is_extra_not_wrong(
        self, tmp_path, monkeypatch
    ):
        """Reading the story is the point; an extra is a result, not a defect.

        Scored as precision it would read as an error, which is why this bank
        is recall-only: declaring `Plot` is *meant* to add partners the
        `Relationships` section does not head.
        """
        paths = _prepare(tmp_path, monkeypatch, rows=[
            {"character": "Denji", "other": "Power", "relation": "friend",
             "section": "Relationships / Power", "quote": "they live together"},
            {"character": "Denji", "other": "Katana Man", "relation": "enemy",
             "section": "Synopsis / Katana Man arc", "quote": "stabs him repeatedly"},
        ], gold=["Power"])
        report = R.score("csm", paths)
        assert report["summary"]["recall"] == 1.0
        assert report["rows"][0]["extra"] == ["Katana Man"]
        assert report["rows"][0]["extra_from_narration_only"] == ["Katana Man"]

    def test_an_extra_the_relationships_section_also_states_is_not_narration(
        self, tmp_path, monkeypatch
    ):
        """Only partners held *solely* by narration are the declaration's doing."""
        paths = _prepare(tmp_path, monkeypatch, rows=[
            {"character": "Denji", "other": "Beam", "relation": "friend",
             "section": "Relationships / Beam", "quote": "carries him around"},
        ], gold=["Power"])
        report = R.score("csm", paths)
        assert report["rows"][0]["extra"] == ["Beam"]
        assert report["rows"][0]["extra_from_narration_only"] == []


class TestIntegrity:
    def test_a_relation_outside_the_closed_set_is_reported(self, tmp_path, monkeypatch):
        paths = _prepare(tmp_path, monkeypatch, rows=[
            {"character": "Denji", "other": "Power", "relation": "roommate",
             "section": "Relationships / Power", "quote": "they live together"},
        ], gold=["Power"])
        report = R.score("csm", paths)
        assert report["integrity"]["outside_vocabulary"] == ["roommate"]

    def test_a_quote_too_short_to_check_is_counted(self, tmp_path, monkeypatch):
        paths = _prepare(tmp_path, monkeypatch, rows=[
            {"character": "Denji", "other": "Power", "relation": "friend",
             "section": "Relationships / Power", "quote": "yes"},
        ], gold=["Power"])
        report = R.score("csm", paths)
        assert report["integrity"]["quotes_too_short"] == 1


class TestBank:
    def test_a_bank_filed_under_the_wrong_series_is_refused(self, tmp_path):
        root = _bank(tmp_path, [], series="csm")
        (root / "_csm_relations.json").write_text(
            json.dumps({"series": "jjk", "questions": []}), encoding="utf-8"
        )
        settings = _Settings(root)
        with pytest.raises(SystemExit):
            R.load_bank("csm", settings)

    def test_a_missing_bank_is_refused_rather_than_scored_as_zero(self, tmp_path):
        with pytest.raises(SystemExit):
            R.load_bank("csm", _Settings(tmp_path / "nothing"))


class _Settings:
    def __init__(self, root):
        self.questions_root = root


def _prepare(tmp_path, monkeypatch, rows, gold):
    """A store and a one-question bank, wired to where the scorer looks."""
    from scriptengine.config import SeriesPaths

    series_root = tmp_path / "series" / "csm"
    series_root.mkdir(parents=True, exist_ok=True)
    facts = series_root / "facts.db"
    with FactStore(facts) as store:
        store.ensure_relations()
        if rows:
            _save(store, rows)

    root = _bank(tmp_path, [{
        "id": "csm-rel-01",
        "kind": "set",
        "question": "Every documented relationship of Denji",
        "subject": "Denji",
        "scope": "core",
        "expect_mode": "relations",
        "tier": "wiki",
        "verified": "2026-08-17",
        "sources": ["https://chainsaw-man.fandom.com/wiki/Denji"],
        "answer": [{"item": name, "aliases": []} for name in gold],
    }])

    monkeypatch.setattr(
        R, "series_paths",
        lambda series: SeriesPaths(name=series, root=series_root),
    )
    return _Settings(root)

"""Tests for the narrative route."""

from __future__ import annotations

import sqlite3

from scriptengine.retrieve.citations import EpisodeIndex
from scriptengine.retrieve.narrative import NarrativeRetriever
from scriptengine.stores.facts import FactStore


class _Store(FactStore):
    """Serves fixed section rows as real `sqlite3.Row`s; the DB constructor
    is never run."""

    def __init__(self, rows: list[dict]) -> None:
        self._conn = sqlite3.connect(":memory:")
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(
            "CREATE TABLE sections (title TEXT, breadcrumb TEXT,"
            " word_count INTEGER, text TEXT)"
        )
        self._conn.executemany(
            "INSERT INTO sections VALUES (?,?,?,?)",
            [(r["title"], r["breadcrumb"], r["word_count"], r["text"]) for r in rows],
        )
        self._conn.commit()

    def document_sections(self, title: str) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT title, breadcrumb, word_count, text FROM sections"
        ).fetchall()


def _retriever(rows: list[dict]) -> NarrativeRetriever:
    # Bypass __init__ (which opens a series on disk): the method under test
    # only touches `store` and the `_episodes` backing field.
    retriever = object.__new__(NarrativeRetriever)
    retriever.store = _Store(rows)
    retriever._episodes = EpisodeIndex()
    return retriever


def _row(title: str, words: int) -> dict:
    return {
        "title": title,
        "breadcrumb": title,
        "word_count": words,
        "text": " ".join(f"word{i}" for i in range(words)),
    }


class TestNarrativeSectionFloor:
    def test_a_short_furniture_section_is_not_a_beat(self):
        # G15 (2026-08-31): the floor was lifted once as part of the chunker
        # fix and the `sourcing-01` gold regressed (35/40) -- the Shibuya
        # Incident beat stream gained 4-word furniture sections ("Teams",
        # "Navigation") that carry no refs, and the unsourced table sections
        # they pushed into the top-40 window dropped the sourced ratio under
        # the 0.9 contract. The narrative path writes scripts, so every beat
        # must be sourceable; short-section reachability lives in the chunker
        # (the qa path), where the floor is gone.
        retriever = _retriever([_row("Teams", 4), _row("Overview", 40)])
        beats = retriever._beats_from_page("Shibuya Incident", 10)
        assert [beat.title for beat in beats] == ["Overview"]

    def test_a_substantial_section_is_a_beat(self):
        retriever = _retriever([_row("Aftermath", 123)])
        beats = retriever._beats_from_page("Kokichi Muta vs. Mahito", 10)
        assert [beat.title for beat in beats] == ["Aftermath"]

    def test_an_empty_section_is_not_a_beat(self):
        retriever = _retriever([{**_row("Empty", 40), "text": ""}])
        assert retriever._beats_from_page("X", 10) == []


class TestG30ShortProseSection:
    def test_a_short_summary_section_is_a_beat(self):
        # G30 (2026-09-04): the 12-word Epilogue Summary must beat on the
        # narrative path even though it is under the G15 20-word floor; a page's
        # own Summary/Synopsis is prose, not the furniture that floor guards.
        retriever = _retriever([_row("Summary", 12), _row("Teams", 4)])
        beats = retriever._beats_from_page("Epilogue", 10)
        assert [beat.title for beat in beats] == ["Summary"]

    def test_a_short_synopsis_section_is_a_beat(self):
        # Ko-Guy's 19-word Synopsis is the corpus's only short Synopsis.
        retriever = _retriever([_row("Synopsis", 19), _row("Navigation", 4)])
        beats = retriever._beats_from_page("Ko-Guy", 10)
        assert [beat.title for beat in beats] == ["Synopsis"]

    def test_short_furniture_still_floors(self):
        # The G15 guard is intact: a short non-prose section is not a beat, so
        # the `sourcing-01` invariant (every beat sourceable) still holds.
        retriever = _retriever([_row("Teams", 4), _row("Navigation", 5)])
        assert retriever._beats_from_page("Shibuya Incident", 10) == []

    def test_a_substantial_nonprose_section_is_still_a_beat(self):
        # The exemption only lifts the floor for prose titles; a long section
        # clears the 20-word floor and beats regardless of title.
        retriever = _retriever([_row("Trivia", 40)])
        beats = retriever._beats_from_page("A Character", 10)
        assert [beat.title for beat in beats] == ["Trivia"]
"""Tests for the vector store.

These use a real embedded Qdrant against a temporary directory, because the
defect that motivated them only appeared across client sessions: the count was
correct while one client was open and wrong when the next one opened the same
folder.
"""

from __future__ import annotations

import pytest

from scriptengine.stores.vectors import VectorStore

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

DIMENSIONS = 8


def chunk(chunk_id: int) -> dict:
    return {
        "chunk_id": chunk_id,
        "doc_title": "Aoi Todo",
        "breadcrumb": "Abilities",
        "level": 2,
        "ordinal": chunk_id,
    }


def vector(seed: float) -> list[float]:
    return [seed] * DIMENSIONS


class TestRebuild:
    def test_recreate_leaves_no_points_behind(self, tmp_path):
        # Point ids are SQLite rowids, and rowids restart at 1 when the tables
        # are dropped. A vector left over from a previous build resolves against
        # whatever row holds that id now, so a search returns confident,
        # well-scored, entirely unrelated text.
        path = tmp_path / "vectors"

        with VectorStore(path) as store:
            store.recreate(DIMENSIONS)
            store.upsert([chunk(i) for i in range(1, 11)], [vector(i) for i in range(1, 11)])
            assert store.count() == 10

        with VectorStore(path) as store:
            store.recreate(DIMENSIONS)
            store.upsert([chunk(i) for i in range(1, 4)], [vector(i) for i in range(1, 4)])

        # The check that matters is made by a *new* client: the earlier defect
        # was invisible until the storage directory was reopened.
        with VectorStore(path) as store:
            assert store.count() == 3
            points, _ = store.client.scroll(
                collection_name="chunks", limit=100, with_payload=False
            )
            assert {point.id for point in points} == {1, 2, 3}

    def test_a_store_survives_being_reopened(self, tmp_path):
        path = tmp_path / "vectors"
        with VectorStore(path) as store:
            store.recreate(DIMENSIONS)
            store.upsert([chunk(1)], [vector(1)])

        with VectorStore(path) as store:
            assert store.exists()
            assert store.count() == 1


class TestSearch:
    @pytest.fixture()
    def store(self, tmp_path):
        store = VectorStore(tmp_path / "vectors")
        store.recreate(DIMENSIONS)
        store.upsert(
            [
                {**chunk(1), "level": 0, "doc_title": "Aoi Todo"},
                {**chunk(2), "level": 2, "doc_title": "Aoi Todo"},
                {**chunk(3), "level": 2, "doc_title": "Boogie Woogie"},
            ],
            [vector(1.0), vector(0.9), vector(0.8)],
        )
        yield store
        store.close()

    def test_all_levels_are_searched_by_default(self, store):
        # Document cards are level 0. Filtering them out made them dead weight:
        # embedded, stored, and never looked at, when a card is exactly what
        # answers "what is X".
        levels = {hit["level"] for hit in store.search(vector(1.0), limit=10)}
        assert 0 in levels and 2 in levels

    def test_a_level_filter_is_honoured_when_asked_for(self, store):
        hits = store.search(vector(1.0), limit=10, levels=[2])
        assert {hit["level"] for hit in hits} == {2}

    def test_results_can_be_narrowed_to_documents(self, store):
        hits = store.search(vector(1.0), limit=10, doc_titles=["Boogie Woogie"])
        assert {hit["doc_title"] for hit in hits} == {"Boogie Woogie"}

    def test_scores_are_higher_is_better(self, store):
        hits = store.search(vector(1.0), limit=3)
        assert hits[0]["vector_score"] >= hits[-1]["vector_score"]

    def test_an_empty_store_returns_nothing(self, tmp_path):
        with VectorStore(tmp_path / "empty") as store:
            store.recreate(DIMENSIONS)
            assert store.search(vector(1.0)) == []

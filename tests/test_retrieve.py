"""Tests for fusion, deduplication and narrative ordering."""

from __future__ import annotations

from scriptengine.retrieve.hybrid import Passage, _deduplicate, reciprocal_rank_fusion
from scriptengine.retrieve.narrative import extract_time, instalment_number


def passage(chunk_id: int, text: str, score: float = 0.0) -> Passage:
    return Passage(
        chunk_id=chunk_id, text=text, doc_title="Aoi Todo",
        breadcrumb="Abilities", score=score,
    )


class TestFusion:
    def test_a_chunk_found_by_two_retrievers_outranks_one_found_by_one(self):
        # The central property: agreement between independent retrievers is
        # evidence, and RRF needs no score calibration to use it — cosine
        # similarity and BM25 are not comparable quantities.
        fused = reciprocal_rank_fusion({"vector": [1, 2], "lexical": [2, 3]})
        assert fused[2][0] > fused[1][0]
        assert fused[2][0] > fused[3][0]

    def test_rank_order_within_one_retriever_is_preserved(self):
        fused = reciprocal_rank_fusion({"vector": [1, 2, 3]})
        assert fused[1][0] > fused[2][0] > fused[3][0]

    def test_the_contributing_retrievers_are_recorded(self):
        fused = reciprocal_rank_fusion({"vector": [7], "lexical": [7], "graph": [7]})
        assert set(fused[7][1]) == {"vector", "lexical", "graph"}

    def test_no_rankings_fuse_to_nothing(self):
        assert reciprocal_rank_fusion({}) == {}

    def test_a_larger_k_flattens_the_ranking(self):
        steep = reciprocal_rank_fusion({"v": [1, 2]}, k=1)
        flat = reciprocal_rank_fusion({"v": [1, 2]}, k=1000)
        assert steep[1][0] - steep[2][0] > flat[1][0] - flat[2][0]


class TestDeduplication:
    def test_overlapping_passages_collapse(self):
        # Consecutive chunks share sentences by design, so a strong match often
        # surfaces the same content two or three times, spending the context
        # budget a script needs for breadth.
        shared = " ".join(f"word{i}" for i in range(40))
        kept = _deduplicate([
            passage(1, shared + " tail one"),
            passage(2, shared + " tail two"),
        ])
        assert len(kept) == 1

    def test_distinct_passages_are_all_kept(self):
        kept = _deduplicate([
            passage(1, " ".join(f"alpha{i}" for i in range(40))),
            passage(2, " ".join(f"beta{i}" for i in range(40))),
        ])
        assert len(kept) == 2

    def test_the_first_passage_wins(self):
        shared = " ".join(f"word{i}" for i in range(40))
        kept = _deduplicate([passage(1, shared), passage(2, shared)])
        assert kept[0].chunk_id == 1

    def test_deduplicating_nothing_is_safe(self):
        assert _deduplicate([]) == []


class TestInstalmentOrdering:
    def test_instalments_sort_numerically_not_alphabetically(self):
        # "Chapter 10" sorts before "Chapter 9" as text, which would silently
        # scramble every timeline.
        titles = ["Chapter 10", "Chapter 9", "Chapter 100", "Chapter 2"]
        ordered = sorted(titles, key=instalment_number)
        assert ordered == ["Chapter 2", "Chapter 9", "Chapter 10", "Chapter 100"]

    def test_kinds_sort_separately(self):
        chapter = instalment_number("Chapter 5")
        episode = instalment_number("Episode 5")
        assert chapter is not None and episode is not None
        assert chapter[0] != episode[0]

    def test_part_numbers_are_understood(self):
        assert instalment_number("Chapter 0-1") == instalment_number("Chapter 0.1")

    def test_a_plain_title_is_not_an_instalment(self):
        assert instalment_number("Aoi Todo") is None
        assert instalment_number("Shibuya Incident") is None

    def test_case_does_not_matter(self):
        assert instalment_number("chapter 16") == instalment_number("Chapter 16")


class TestTimeExtraction:
    def test_a_clock_time_is_read_from_a_heading(self):
        assert extract_time("7:00 P.M. - 8:31 P.M. Shibuya") == "7:00 PM"

    def test_the_meridiem_is_normalised(self):
        assert extract_time("9:15 a.m. Meiji-Jingumae") == "9:15 AM"
        assert extract_time("10:51 PM Outside Shibuya Station") == "10:51 PM"

    def test_a_heading_without_a_time_yields_nothing(self):
        assert extract_time("Abilities and Powers") == ""

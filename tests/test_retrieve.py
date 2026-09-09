"""Tests for fusion, deduplication and narrative ordering."""

from __future__ import annotations

from scriptengine.retrieve.hybrid import Passage, _deduplicate, reciprocal_rank_fusion
from scriptengine.retrieve.hybrid import _query_covered
from scriptengine.retrieve.narrative import extract_time, instalment_number


def passage(chunk_id: int, text: str, score: float = 0.0) -> Passage:
    return Passage(
        chunk_id=chunk_id, text=text, doc_title="Aoi Todo",
        breadcrumb="Abilities", score=score,
    )


class TestFusion:
    def test_a_chunk_found_by_two_retrievers_outranks_one_found_by_one(self):
        # The central property: agreement between independent retrievers is
        # evidence, and RRF needs no score calibration to use it: cosine
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
        ordered = sorted(
            titles, key=lambda title: instalment_number(title) or (7, 0.0)
        )
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


class TestQueryCoverage:
    """The d5 recall guard's predicate: a passage covers the query when it
    holds the query's own words. The guard (in `HybridRetriever.search`) keeps
    such a passage out of the rerank cut -- the CSM d5 sweep measured the
    lexical-rank-0/1 chunk of a verbatim-sentence query evicted by the
    cross-encoder (csmd5-*, gate400-* rows)."""

    D5_QUERY = (
        "While Yoru believes that Nayuta is likely dead, Denji refuses to "
        "believe that she is gone."
    )

    def test_a_verbatim_passage_covers_the_query(self):
        text = self.D5_QUERY + " He then explains why he cannot reflect on his mistakes."
        assert _query_covered(self.D5_QUERY, text)

    def test_case_and_plurals_do_not_break_coverage(self):
        query = "The Death Devil has finally descended to Earth"
        text = "The Death Devils have finally descended to the earth of the story."
        assert _query_covered(query, text)

    def test_a_topically_similar_passage_does_not_cover(self):
        # Same topic, different words: containment stays below the threshold,
        # so the guard must not fire and the reranker's order stands.
        text = "Denji fights the devil in the city while the devil hunters watch."
        assert not _query_covered(self.D5_QUERY, text)

    def test_a_short_question_is_below_the_guard(self):
        # Fewer than three content words: containment means nothing, and the
        # guard must stay inert for short writer questions (the JJK-eval shape).
        assert not _query_covered("Who is Aki Hayakawa?", "Aki Hayakawa is a Devil Hunter.")
        assert not _query_covered("Who is Aki Hayakawa?", "Aki Hayakawa is a Devil Hunter who wields the Gun Devil.")


class TestQueryCoverRecallGuard:
    """`search()` re-admits a query-covering passage the rerank cut dropped,
    at the tail of the beam, without growing it past top_k (d5, 2026-09-09).

    Model-free: a tmp store (no vectors directory, so the vector leg is absent)
    and a fake reranker that reproduces the cross-encoder's measured failure --
    it ranks name-dense distractors above the short verbatim chunk."""

    QUERY = (
        "While Yoru believes that Nayuta is likely dead, Denji refuses to "
        "believe that she is gone."
    )

    class _TopicalReranker:
        """Scores topical density, not verbatim agreement: the distractors win."""

        def score(self, query, texts):
            return [0.9 if "pochita" in text.lower() else 0.1 for text in texts]

    def _retriever(self, tmp_path, reranker):
        from scriptengine.config import Settings, SeriesPaths
        from scriptengine.retrieve.hybrid import HybridRetriever
        from scriptengine.stores.facts import FactStore

        paths = SeriesPaths(name="test", root=tmp_path)
        store = FactStore(paths.facts_db)
        store.initialise()
        doc = store.add_document(
            title="Test Page", url="", page_type="character",
            infobox_template="T", lead="Test Page is a character.",
            word_count=6, revid=1, fetched_at="",
        )
        # One chunk verbatim contains the query; ten name-dense distractors
        # name its words (so they enter the lexical shortlist) but cover none
        # of its sentence, and each carries a unique 40-word tail so dedup
        # keeps all of them -- the d5 shape: the target is the lexical #1,
        # the reranker buries it.
        store.add_chunk(
            document_id=doc, section_id=None, parent_id=None, level=2, ordinal=0,
            doc_title="Test Page", breadcrumb="Plot",
            text=self.QUERY + " He then explains why he cannot reflect.",
        )
        for index in range(1, 11):
            tail = " ".join(f"w{index}_{j}" for j in range(40))
            store.add_chunk(
                document_id=doc, section_id=None, parent_id=None, level=2, ordinal=index,
                doc_title="Test Page", breadcrumb=f"Section {index}",
                text=f"Pochita and Denji with Yoru discuss being dead in room {index}. {tail}",
            )
        store.rebuild_fts()
        store.commit()
        store.close()

        class _NoModel:
            """The vector leg is absent (no vectors dir), so the embedder is never called."""

        return HybridRetriever(paths, Settings(), embedder=_NoModel(), reranker=reranker)

    def test_a_buried_verbatim_passage_is_readmitted_at_the_tail(self, tmp_path):
        retriever = self._retriever(tmp_path, self._TopicalReranker())
        try:
            result = retriever.search(self.QUERY, top_k=8, expand_parents=False, rerank=True)
        finally:
            retriever.close()
        target = next(p for p in result.dropped + result.passages if p.ordinal == 0)
        assert target in result.passages, (
            "the query-covering chunk the rerank buried must be re-admitted"
        )
        assert len(result.passages) == 8, "the beam must not grow past top_k"
        assert result.passages[-1].ordinal == 0, "recovered passages fill the tail"

    def test_the_guard_is_inert_when_the_rerank_already_ranks_the_target(self, tmp_path):
        class _AgreeingReranker:
            """The cross-encoder did its job: the verbatim chunk ranks first."""

            def score(self, query, texts):
                return [0.1 if "pochita" in text.lower() else 0.9 for text in texts]

        retriever = self._retriever(tmp_path, _AgreeingReranker())
        try:
            result = retriever.search(self.QUERY, top_k=8, expand_parents=False, rerank=True)
        finally:
            retriever.close()
        assert result.passages[0].ordinal == 0
        assert len(result.passages) == 8

    def _retriever_covering_tail(self, tmp_path, reranker):
        """The pre-fix regime: the dropped tail is *mostly* query-covering.

        Same store shape as `_retriever`, but the ten name-dense distractors
        are replaced by seventeen *covering* ones -- each repeats the query's
        own words, so each passes `_query_covered` -- and the target chunk's
        sentence order is shuffled so dedup (first-40-word shingle) does not
        absorb it into a distractor. With L = 10 covering passages in the
        tail and top_k = 8, the uncapped splice went negative (re-admission
        silently no-oped, the internal list grew past the shortlist) or, at
        L == top_k, replaced the rerank top entirely.
        """
        from scriptengine.config import Settings, SeriesPaths
        from scriptengine.retrieve.hybrid import HybridRetriever
        from scriptengine.stores.facts import FactStore

        paths = SeriesPaths(name="test", root=tmp_path)
        store = FactStore(paths.facts_db)
        store.initialise()
        doc = store.add_document(
            title="Test Page", url="", page_type="character",
            infobox_template="T", lead="Test Page is a character.",
            word_count=6, revid=1, fetched_at="",
        )
        # The verbatim target: every content word of the query, in a different
        # sentence order than the distractors' opening, so the dedup shingle
        # keeps it distinct.
        store.add_chunk(
            document_id=doc, section_id=None, parent_id=None, level=2, ordinal=0,
            doc_title="Test Page", breadcrumb="Plot",
            text=(
                "He then explains why he cannot reflect. Denji refuses to "
                "believe that Nayuta is gone while Yoru believes that she is "
                "likely dead, while Yoru believes that Nayuta is likely dead."
            ),
        )
        for index in range(1, 18):
            tail = " ".join(f"cov{index}_{j}" for j in range(40))
            store.add_chunk(
                document_id=doc, section_id=None, parent_id=None, level=2, ordinal=index,
                doc_title="Test Page", breadcrumb=f"Section {index}",
                text=(
                    "While Yoru believes that Nayuta is likely dead, Denji "
                    f"refuses to believe that she is gone, marker {index}: " + tail
                ),
            )
        store.rebuild_fts()
        store.commit()
        store.close()

        class _NoModel:
            """The vector leg is absent (no vectors dir), so the embedder is never called."""

        return HybridRetriever(paths, Settings(), embedder=_NoModel(), reranker=reranker)

    def test_the_cap_keeps_the_splice_a_tail_fill_when_the_tail_is_mostly_covering(self, tmp_path):
        # Council R-2+R-3 (2026-09-09): the re-admission cap. With 17 covering
        # distractors the tail holds 10 query-covering passages (L = 10 > top_k
        # = 8), the regime where the uncapped splice went negative or, at
        # L == top_k, swapped the rerank top. The capped splice is
        # order-preserving: the re-admitted passages keep rerank order as a
        # subsequence of the shortlist.
        class _HostileReranker:
            """Strict, deterministic ordering: every covering distractor
            outranks the verbatim target, and marker N outranks marker N+1."""

            def score(self, query, texts):
                out = []
                for text in texts:
                    for i in range(1, 18):
                        if f"marker {i}:" in text:
                            out.append(0.9 - i * 0.001)
                            break
                    else:
                        out.append(0.1)
                return out

        retriever = self._retriever_covering_tail(tmp_path, _HostileReranker())
        try:
            result = retriever.search(self.QUERY, top_k=8, expand_parents=False, rerank=True)
        finally:
            retriever.close()
        assert len(result.passages) == 8, "the beam must not grow past top_k"
        assert result.passages[0].ordinal == 1, (
            "the rerank #1 keeps the top slot -- no full swap"
        )
        assert [p.ordinal for p in result.passages[1:]] == list(range(9, 16)), (
            "the tail seven hold the re-admitted covering distractors in rerank order"
        )
        ids = [p.chunk_id for p in result.passages + result.dropped]
        assert len(ids) == len(set(ids)), (
            "the uncapped splice grew the internal list past the shortlist, "
            "duplicating chunks in the result"
        )

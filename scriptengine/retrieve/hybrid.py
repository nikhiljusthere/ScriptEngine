"""Hybrid retrieval: vector, lexical and graph, fused and reranked.

The shape is inherited from the previous project, which had it right even
though it never ran: retrieve three ways, fuse the rankings, rerank the
shortlist with a cross-encoder, then expand each survivor to its section for
context.

What changed is what sits underneath (SQLite instead of Neo4j, FTS5 instead of
an in-memory BM25 index) and two corrections:

* entity linking matches whole words against an alias table rather than asking
  whether one string appears inside another, so "Ryu" no longer matches inside
  "Ryomen".
* the vector search is filtered by *document*, chosen via the graph, rather than
  by a per-chunk entity list. A single mis-tagged chunk used to be invisible to
  a query naming its own subject.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from scriptengine.config import Settings, SeriesPaths, get_settings
from scriptengine.index.embedder import (
    Embedder,
    Reranker,
    shared_embedder,
    shared_reranker,
)
from scriptengine.stores import lexical
from scriptengine.stores.facts import FactStore
from scriptengine.stores.vectors import VectorStore, shared_reader

logger = logging.getLogger(__name__)


@dataclass
class Passage:
    """One retrieved passage, with everything needed to cite it."""

    chunk_id: int
    text: str
    doc_title: str
    breadcrumb: str
    ordinal: int = 0
    score: float = 0.0
    parent_text: str = ""
    sources: list[str] = field(default_factory=list)   # which retrievers found it
    # The fused rank before the cross-encoder overwrote `score`. Kept because
    # losing it makes "the right chunk was retrieved and then buried"
    # indistinguishable from "it was never retrieved", which are different bugs
    # in different halves of the pipeline.
    rrf_score: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "doc_title": self.doc_title,
            "breadcrumb": self.breadcrumb,
            "score": round(self.score, 4),
            "sources": self.sources,
            **({"parent_text": self.parent_text} if self.parent_text else {}),
        }


@dataclass
class Retrieved:
    """The full result of a query, including how it was reached."""

    query: str
    passages: list[Passage] = field(default_factory=list)
    # Shortlisted, reranked, and then cut by `top_k`. Diagnostic only, since nothing
    # downstream reads it, but it is the only place a fusion or rerank loss is
    # visible after the fact.
    dropped: list[Passage] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    facts: list[dict[str, Any]] = field(default_factory=list)
    relations: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "entities": self.entities,
            "related": self.related,
            "facts": self.facts,
            "relations": self.relations,
            "passages": [passage.as_dict() for passage in self.passages],
        }


def reciprocal_rank_fusion(
    rankings: dict[str, list[int]], k: int = 60
) -> dict[int, tuple[float, list[str]]]:
    """Combine rankings by reciprocal rank.

    RRF needs no score calibration between retrievers, which matters because
    cosine similarity, BM25 and graph distance are not comparable quantities. A
    chunk found by two retrievers outranks one found by a single retriever more
    confidently, which is exactly the signal wanted here.
    """
    fused: dict[int, tuple[float, list[str]]] = {}
    for source, ranking in rankings.items():
        for rank, chunk_id in enumerate(ranking):
            score, sources = fused.get(chunk_id, (0.0, []))
            fused[chunk_id] = (score + 1.0 / (k + rank + 1), [*sources, source])
    return fused


class HybridRetriever:
    """Queries one series."""

    def __init__(
        self,
        paths: SeriesPaths,
        settings: Settings | None = None,
        embedder: Embedder | None = None,
        reranker: Reranker | None = None,
    ) -> None:
        self.paths = paths
        self.settings = settings or get_settings()
        self.store = FactStore(paths.facts_db)
        # Shared, for the same reason the models are: opening a local Qdrant
        # collection reads every vector off disk, which was 3.15 of the 3.87
        # seconds a warm `qa` request spent.
        self.vectors = shared_reader(paths.vectors) if paths.vectors.exists() else None
        # Shared across requests by default. Constructing a fresh pair here gave
        # every query a cold model: `_model` starts at None, so the first use
        # reloaded 3.6 GB of weights. An explicit instance still wins, which is
        # what indexing and the tests pass.
        self.embedder = embedder or shared_embedder(self.settings)
        self.reranker = reranker or shared_reranker(self.settings)

    def __enter__(self) -> "HybridRetriever":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        """Close what this retriever owns, and nothing that outlives it.

        The vector store is shared between requests now, so closing it here
        would make every request pay the 3.15s reload the sharing exists to
        avoid, and the second request would be closing a handle the third is
        about to use. `recreate()` drops the shared reader itself, which is the
        one case where the handle must not survive.
        """
        self.store.close()

    def release_models(self) -> None:
        """Give the GPU back once nothing has used it for a while.

        This used to unload unconditionally, which meant every request reloaded
        both models: two consecutive `qa` requests measured 16.8s and 18.9s on a
        warm CUDA server, with no warm-up between them. ComfyUI still gets the
        VRAM back -- `model_idle_unload_seconds` decides when, and the API sweeps
        on a timer so an idle server frees the GPU without waiting for a request.

        A long-running job that wants the GPU back *now* can still call
        `unload()` on the models directly.
        """
        self.embedder.unload_if_idle()
        self.reranker.unload_if_idle()

    # ── the pipeline ─────────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        top_k: int | None = None,
        expand_parents: bool = True,
        rerank: bool = True,
    ) -> Retrieved:
        top_k = top_k or self.settings.final_top_k
        result = Retrieved(query=query)

        # 1. Which entities does the query name?
        entities = self.store.link_entities(query)
        entity_ids = [int(row["id"]) for row in entities]
        result.entities = [row["name"] for row in entities]

        # 2. What is one or two hops away from them?
        related = self.store.neighbours(
            entity_ids, depth=self.settings.graph_hop_depth, min_confidence=0.5
        )
        result.related = [row["name"] for row in related[:40]]

        # 3. Structured facts and relationships, which need no retrieval at all.
        for row in entities[:5]:
            for fact in self.store.facts_for(row["name"]):
                result.facts.append(
                    {
                        "entity": row["name"],
                        "key": fact["key"],
                        "label": fact["label"] or fact["key"],
                        "value": fact["value"],
                        "citation": fact["citation"],
                    }
                )

        # 3b. A named battle page is the question's own subject even when
        #     `link_entities` missed it: `vs.` tokenises apart from the
        #     stored alias, so "Yuji Itadori vs. Panda" never links and the
        #     fight's own infobox (arc, place, outcome, chapters) would stay
        #     out of the bundle unless the rank happened to surface the page.
        #     The phrasing-robustness requirement (2026-08-24) pays for those
        #     facts up front, the way the entity facts above are paid for.
        from scriptengine.retrieve.roster import battle_facts

        battle = battle_facts(self.store, query)
        if battle and battle[0]["entity"] not in result.entities:
            result.facts = battle + result.facts
            result.entities.insert(0, battle[0]["entity"])
        # Graph edges say X is linked to Y; they carry no words. The
        # LLM-extracted `relations` rows carry the verbatim `quote` and `era`
        # that actually answer "who is X to Y" / "what is the relationship
        # between X and Y", and they live in a separate table the edge walk
        # above never touches. Both ways: the wiki writes a relationship on
        # whichever page it feels like, so a question about the top entity
        # wants the rows it owns and the rows that name it. A question can
        # name several characters ("Who are Saitama and Genos to Bang?"), so
        # the top three linked entities are unioned and duplicates dropped --
        # the pair's row may be filed under either end. Edge rows keep their
        # shape and gain empty quote/era so both kinds share one form.
        for row in self.store.edges_for(entity_ids, min_confidence=0.9, limit=40):
            result.relations.append({
                "source": row["source"], "relation": row["relation"],
                "target": row["target"], "confidence": row["confidence"],
                "quote": "", "era": "",
            })
        seen = {(r["source"], r["relation"], r["target"], r["quote"])
                for r in result.relations}
        for entity in entities[:3]:
            for row in self.store.relations_of(entity["name"], both_ways=True):
                key = (row["character"], row["relation"], row["other"],
                       row["quote"] or "")
                if key in seen:
                    continue
                seen.add(key)
                result.relations.append({
                    "source": row["character"], "relation": row["relation"],
                    "target": row["other"], "confidence": 1.0,
                    "quote": row["quote"] or "", "era": row["era"] or "",
                })

        # 4. Three retrievers.
        rankings: dict[str, list[int]] = {}
        candidates: dict[int, dict[str, Any]] = {}

        lexical_hits = lexical.search(
            self.store, query, limit=self.settings.lexical_top_k
        )
        rankings["lexical"] = [hit["chunk_id"] for hit in lexical_hits]
        for hit in lexical_hits:
            candidates.setdefault(hit["chunk_id"], hit)

        if self.vectors is not None and self.vectors.exists():
            focus = [row["name"] for row in entities[:3]] + [
                row["name"] for row in related[:12]
            ]
            for source, hits in self._vector_search(query, focus).items():
                rankings[source] = [hit["chunk_id"] for hit in hits]
                for hit in hits:
                    candidates.setdefault(hit["chunk_id"], hit)

        graph_hits = self.store.chunks_for_nodes(
            [int(row["id"]) for row in related[:20]] + entity_ids, limit=30
        )
        rankings["graph"] = [int(row["id"]) for row in graph_hits]
        for row in graph_hits:
            candidates.setdefault(int(row["id"]), dict(row) | {"chunk_id": int(row["id"])})

        if not candidates:
            return result

        # 5. Fuse.
        fused = reciprocal_rank_fusion(rankings, k=self.settings.rrf_k)
        ordered = sorted(fused.items(), key=lambda item: item[1][0], reverse=True)

        shortlist_size = max(top_k * 4, 24)
        shortlist = [chunk_id for chunk_id, _ in ordered[:shortlist_size]]
        rows = {row["id"]: row for row in self.store.chunks_by_id(shortlist)}

        passages = []
        for chunk_id in shortlist:
            row = rows.get(chunk_id)
            if row is None:
                continue
            score, sources = fused[chunk_id]
            passages.append(
                Passage(
                    chunk_id=chunk_id,
                    text=row["text"],
                    doc_title=row["doc_title"],
                    breadcrumb=row["breadcrumb"],
                    ordinal=row["ordinal"],
                    score=score,
                    rrf_score=score,
                    sources=sources,
                )
            )

        # 6. Rerank the shortlist with a cross-encoder, which reads the query and
        #    the passage together instead of comparing two independent vectors.
        if rerank and passages:
            scores = self.reranker.score(query, [p.text for p in passages])
            for passage, score in zip(passages, scores):
                passage.score = score
            passages.sort(key=lambda p: p.score, reverse=True)

        deduplicated = _deduplicate(passages)
        passages, result.dropped = deduplicated[:top_k], deduplicated[top_k:]

        # 7. Expand each survivor to its section, so a quoted passage carries the
        #    context around it rather than arriving as an orphaned fragment.
        if expand_parents:
            for passage in passages:
                parent = self.store.parent_of(passage.chunk_id)
                if parent is not None and parent["text"] != passage.text:
                    passage.parent_text = parent["text"]

        result.passages = passages
        return result

    def _vector_search(
        self, query: str, focus: list[str]
    ) -> dict[str, list[dict[str, Any]]]:
        """Dense search, run both narrowed to graph-selected pages and wide open.

        Running both and letting fusion decide is deliberate. Narrowing to the
        pages the graph picked out is a strong precision signal when entity
        linking was right, and a blindfold when it was wrong: asking about "a
        promise made in exchange for power" links "sorcerer" and then searches
        only the pages about sorcerers, never reaching Binding Vow.

        A chunk found by both searches ranks higher under RRF, so the precision
        benefit survives without the failure mode.
        """
        vector = self.embedder.encode_query(query)
        limit = self.settings.vector_top_k
        searches = {"vector": self.vectors.search(vector, limit=limit)}

        if focus:
            narrowed = self.vectors.search(vector, limit=limit, doc_titles=focus)
            if narrowed:
                searches["vector_focused"] = narrowed

        return searches


def _deduplicate(passages: list[Passage]) -> list[Passage]:
    """Drop near-identical passages produced by chunk overlap.

    Consecutive chunks share sentences by design, so a strong match often
    surfaces the same content two or three times. Keeping all of them wastes
    the context budget that a script needs for breadth.
    """
    kept: list[Passage] = []
    seen: set[frozenset[str]] = set()

    for passage in passages:
        words = passage.text.lower().split()
        # A shingle of the opening is enough to catch overlap duplicates
        # without the cost of comparing every pair in full.
        fingerprint = frozenset(words[:40])
        if any(
            len(fingerprint & existing) >= min(len(fingerprint), len(existing)) * 0.8
            for existing in seen
        ):
            continue
        seen.add(fingerprint)
        kept.append(passage)

    return kept

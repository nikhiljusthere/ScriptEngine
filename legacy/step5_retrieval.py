"""
Step 3: Hybrid retrieval, vector search + BM25 + graph traversal → rerank
This is where accuracy is won or lost.
"""

import re
import json
from typing import List, Dict, Optional, Tuple

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny, MatchValue
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from neo4j import GraphDatabase
import numpy as np

# ── Config ────────────────────────────────────────────────────────────────────
QDRANT_HOST      = "localhost"
QDRANT_PORT      = 6333
COLLECTION_NAME  = "wiki_chunks"
NEO4J_URI        = "bolt://localhost:7687"
NEO4J_USER       = "neo4j"
NEO4J_PASSWORD   = "password"

EMBED_MODEL      = "BAAI/bge-large-en-v1.5"
RERANK_MODEL     = "BAAI/bge-reranker-v2-m3"   # best accuracy reranker

VECTOR_TOP_K     = 20    # retrieve this many from vector search
BM25_TOP_K       = 20    # retrieve this many from BM25
GRAPH_HOP_DEPTH  = 2     # how many hops to traverse in graph
FINAL_TOP_K      = 8     # after reranking, pass this many to LLM


# ─────────────────────────────────────────────────────────────────────────────
# 3A. Load models
# ─────────────────────────────────────────────────────────────────────────────

class Models:
    _embedder  = None
    _reranker  = None

    @classmethod
    def embedder(cls) -> SentenceTransformer:
        if cls._embedder is None:
            cls._embedder = SentenceTransformer(EMBED_MODEL, device="cuda")
            cls._embedder.max_seq_length = 512
        return cls._embedder

    @classmethod
    def reranker(cls) -> CrossEncoder:
        if cls._reranker is None:
            # CrossEncoder runs query+chunk together, much more accurate than bi-encoder
            cls._reranker = CrossEncoder(RERANK_MODEL, device="cuda", max_length=512)
        return cls._reranker


# ─────────────────────────────────────────────────────────────────────────────
# 3B. BM25 index (built once, held in memory)
# BM25 is critical for exact character/technique name matching
# ─────────────────────────────────────────────────────────────────────────────

class BM25Index:
    def __init__(self):
        self.chunks: List[Dict] = []
        self.index: Optional[BM25Okapi] = None

    def build(self, qdrant_client: QdrantClient):
        """Pull all level-2 chunks from Qdrant and build BM25 index."""
        print("Building BM25 index from Qdrant...")
        all_chunks = []
        offset = None

        while True:
            results, offset = qdrant_client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[FieldCondition(key="level", match=MatchValue(value=2))]
                ),
                limit=1000,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            if not results:
                break
            for r in results:
                all_chunks.append({
                    "chunk_id": r.id,
                    "text":     r.payload["text"],
                    "payload":  r.payload
                })
            if offset is None:
                break

        self.chunks = all_chunks

        # tokenize for BM25
        tokenized = [self._tokenize(c["text"]) for c in all_chunks]
        self.index = BM25Okapi(tokenized)
        print(f"BM25 index built with {len(all_chunks)} chunks.")

    def _tokenize(self, text: str) -> List[str]:
        # lowercase, split on non-alphanumeric
        return re.findall(r'\b\w+\b', text.lower())

    def search(self, query: str, top_k: int = BM25_TOP_K) -> List[Dict]:
        if self.index is None:
            raise RuntimeError("BM25 index not built. Call .build() first.")
        tokens = self._tokenize(query)
        scores = self.index.get_scores(tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    **self.chunks[idx],
                    "bm25_score": float(scores[idx])
                })
        return results


# ─────────────────────────────────────────────────────────────────────────────
# 3C. Vector search
# ─────────────────────────────────────────────────────────────────────────────

def embed_query(query: str) -> list:
    """Embed query with BGE query prefix."""
    model = Models.embedder()
    vec = model.encode(
        ["Represent this question for searching relevant passages: " + query],
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    return vec[0].tolist()


def vector_search(
    client: QdrantClient,
    query: str,
    top_k: int = VECTOR_TOP_K,
    entity_filter: Optional[List[str]] = None
) -> List[Dict]:
    """
    Search Qdrant by vector similarity.
    Optionally filter by entities mentioned in the query.
    """
    query_vec = embed_query(query)

    qdrant_filter = Filter(
        must=[FieldCondition(key="level", match=MatchValue(value=2))]
    )

    # if we know which entities are in the query, filter to chunks mentioning them
    # this dramatically improves precision
    if entity_filter:
        qdrant_filter = Filter(
            must=[
                FieldCondition(key="level", match=MatchValue(value=2)),
                FieldCondition(key="entities", match=MatchAny(any=entity_filter))
            ]
        )

    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        query_filter=qdrant_filter,
        limit=top_k,
        with_payload=True
    )

    return [
        {
            "chunk_id":    h.id,
            "text":        h.payload["text"],
            "payload":     h.payload,
            "vector_score": h.score
        }
        for h in hits
    ]


# ─────────────────────────────────────────────────────────────────────────────
# 3D. Graph traversal: find related entities and their documents
# ─────────────────────────────────────────────────────────────────────────────

class GraphRetriever:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def get_related_entities(
        self,
        entity_names: List[str],
        depth: int = GRAPH_HOP_DEPTH
    ) -> List[Dict]:
        """
        Given entity names, traverse graph to find related entities.
        Returns list of {entity, relation, related_entity, source_doc}
        """
        if not entity_names:
            return []

        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity)
                WHERE e.name IN $names
                MATCH path = (e)-[r*1..$depth]-(related)
                RETURN
                    e.name         AS source,
                    type(r[-1])    AS relation,
                    related.name   AS related,
                    related.type   AS related_type
                LIMIT 100
            """, names=entity_names, depth=depth)

            rows = []
            for record in result:
                rows.append({
                    "source":       record["source"],
                    "relation":     record["relation"],
                    "related":      record["related"],
                    "related_type": record["related_type"]
                })
            return rows

    def get_documents_for_entities(self, entity_names: List[str]) -> List[str]:
        """Return document titles that mention any of these entities."""
        if not entity_names:
            return []
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity)-[:MENTIONED_IN]->(d:Document)
                WHERE e.name IN $names
                RETURN DISTINCT d.title AS title
                LIMIT 50
            """, names=entity_names)
            return [r["title"] for r in result]


# ─────────────────────────────────────────────────────────────────────────────
# 3E. Parent context expansion
# When a small chunk matches, fetch its parent section for more context
# ─────────────────────────────────────────────────────────────────────────────

def expand_to_parent(
    client: QdrantClient,
    chunks: List[Dict]
) -> List[Dict]:
    """
    For each level-2 chunk, fetch its level-1 parent section text.
    Returns enriched chunks with parent_text added.
    """
    parent_ids = list({
        c["payload"]["parent_id"]
        for c in chunks
        if c["payload"].get("parent_id")
    })

    if not parent_ids:
        return chunks

    parent_results = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=parent_ids,
        with_payload=True
    )

    parent_map = {r.id: r.payload.get("text", "") for r in parent_results}

    for chunk in chunks:
        pid = chunk["payload"].get("parent_id")
        chunk["parent_text"] = parent_map.get(pid, "")

    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# 3F. Merge vector + BM25 results (Reciprocal Rank Fusion)
# ─────────────────────────────────────────────────────────────────────────────

def reciprocal_rank_fusion(
    vector_results: List[Dict],
    bm25_results:   List[Dict],
    k: int = 60
) -> List[Dict]:
    """
    RRF score = sum(1 / (rank + k)) across retrieval methods.
    Merges results without needing to normalize different score scales.
    """
    scores: Dict[str, float] = {}
    all_chunks: Dict[str, Dict] = {}

    for rank, item in enumerate(vector_results):
        cid = item["chunk_id"]
        scores[cid]     = scores.get(cid, 0) + 1 / (rank + k)
        all_chunks[cid] = item

    for rank, item in enumerate(bm25_results):
        cid = item["chunk_id"]
        scores[cid]     = scores.get(cid, 0) + 1 / (rank + k)
        all_chunks[cid] = item

    # sort by RRF score descending
    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
    merged = []
    for cid in sorted_ids:
        chunk = all_chunks[cid]
        chunk["rrf_score"] = scores[cid]
        merged.append(chunk)

    return merged


# ─────────────────────────────────────────────────────────────────────────────
# 3G. Reranker: the most important accuracy step
# ─────────────────────────────────────────────────────────────────────────────

def rerank(query: str, chunks: List[Dict], top_k: int = FINAL_TOP_K) -> List[Dict]:
    """
    CrossEncoder reranker scores each (query, chunk) pair jointly.
    Far more accurate than bi-encoder similarity alone.
    Uses parent_text if available for richer context.
    """
    reranker = Models.reranker()

    pairs = []
    for chunk in chunks:
        # use parent text if available; gives reranker more context
        context = chunk.get("parent_text", "") or chunk["text"]
        if chunk["text"] not in context:
            context = chunk["text"] + "\n\n" + context
        pairs.append([query, context[:1000]])  # cap at 1000 chars

    scores = reranker.predict(pairs, batch_size=32, show_progress_bar=False)

    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)

    reranked = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]


# ─────────────────────────────────────────────────────────────────────────────
# 3H. Entity extraction from query (lightweight)
# ─────────────────────────────────────────────────────────────────────────────

def extract_query_entities(query: str, known_entities: List[str]) -> List[str]:
    """Find known entities mentioned in the query."""
    query_lower = query.lower()
    found = []
    for entity in known_entities:
        if entity.lower() in query_lower:
            found.append(entity)
    return found


# ─────────────────────────────────────────────────────────────────────────────
# 3I. Main retrieval function: call this from your QA pipeline
# ─────────────────────────────────────────────────────────────────────────────

class HybridRetriever:
    def __init__(self):
        self.qdrant       = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.bm25         = BM25Index()
        self.graph        = GraphRetriever()
        self.entity_list  = self._load_entities()

        # build BM25 index on startup (loads all chunks into RAM)
        # for 10k files ~500k chunks this may use 2-4GB RAM, which is acceptable
        self.bm25.build(self.qdrant)

    def _load_entities(self) -> List[str]:
        try:
            with open("entities.json") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def retrieve(self, query: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Full hybrid retrieval pipeline.
        Returns: (final_chunks, graph_context)
        """

        # 1. extract entities from query
        query_entities = extract_query_entities(query, self.entity_list)

        # 2. graph traversal: find related entities
        graph_relations = self.graph.get_related_entities(query_entities)
        related_entity_names = list({r["related"] for r in graph_relations})
        all_relevant_entities = list(set(query_entities + related_entity_names))

        # 3. get docs from graph that are relevant
        graph_doc_titles = self.graph.get_documents_for_entities(all_relevant_entities)

        # 4. vector search (with entity filter if we have entities)
        entity_filter = all_relevant_entities if all_relevant_entities else None
        vector_results = vector_search(
            self.qdrant, query, VECTOR_TOP_K, entity_filter=entity_filter
        )

        # 5. if entity filter returned few results, do unfiltered search too
        if len(vector_results) < 5:
            vector_results = vector_search(self.qdrant, query, VECTOR_TOP_K)

        # 6. BM25 search
        bm25_results = self.bm25.search(query, BM25_TOP_K)

        # 7. graph-boosted search: fetch chunks from graph-identified docs
        graph_boosted = []
        if graph_doc_titles:
            graph_boosted = self._fetch_chunks_by_doc_titles(
                graph_doc_titles[:10], query
            )

        # 8. merge all results via RRF
        merged = reciprocal_rank_fusion(vector_results, bm25_results)

        # add graph-boosted chunks (not in merged yet)
        existing_ids = {c["chunk_id"] for c in merged}
        for gc in graph_boosted:
            if gc["chunk_id"] not in existing_ids:
                gc["rrf_score"] = 0.01  # lower priority than direct matches
                merged.append(gc)
                existing_ids.add(gc["chunk_id"])

        # 9. parent context expansion
        merged = expand_to_parent(self.qdrant, merged)

        # 10. rerank
        final_chunks = rerank(query, merged, FINAL_TOP_K)

        return final_chunks, graph_relations

    def _fetch_chunks_by_doc_titles(
        self,
        doc_titles: List[str],
        query: str
    ) -> List[Dict]:
        """Fetch level-2 chunks from specific documents."""
        query_vec = embed_query(query)
        hits = self.qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vec,
            query_filter=Filter(
                must=[
                    FieldCondition(key="level", match=MatchValue(value=2)),
                    FieldCondition(key="doc_title", match=MatchAny(any=doc_titles))
                ]
            ),
            limit=10,
            with_payload=True
        )
        return [
            {"chunk_id": h.id, "text": h.payload["text"],
             "payload": h.payload, "vector_score": h.score}
            for h in hits
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Quick test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    retriever = HybridRetriever()

    test_queries = [
        "What techniques does Kusakabe use against Sukuna?",
        "How does Simple Domain work?",
        "Who is the head of New Shadow Style?",
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        chunks, graph = retriever.retrieve(q)
        print(f"  Graph relations found: {len(graph)}")
        print(f"  Final chunks: {len(chunks)}")
        for i, c in enumerate(chunks[:3]):
            print(f"  [{i+1}] ({c['payload']['doc_title']} / {c['payload']['section']}) "
                  f"score={c['rerank_score']:.3f}")
            print(f"       {c['text'][:120]}...")

"""Vector storage, via Qdrant in local (embedded) mode.

Same client API as the server, no process to manage. Each series gets its own
storage directory, so deleting a series is deleting a folder.

Qdrant's local mode holds an exclusive lock on its directory, so the store is
opened lazily and closed explicitly — otherwise indexing and serving in the same
session fight over it.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterable, Sequence

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PointStruct,
    VectorParams,
)

logger = logging.getLogger(__name__)

COLLECTION = "chunks"


class VectorStore:
    """Embedded vector storage for one series."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self._client: QdrantClient | None = None

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(path=str(self.path))
        return self._client

    def __enter__(self) -> "VectorStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    # ── writing ──────────────────────────────────────────────────────────────

    def recreate(self, dimensions: int) -> None:
        """Start a fresh collection. Indexing is a rebuild, not an append."""
        self.client.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=dimensions, distance=Distance.COSINE),
        )

    def upsert(self, chunks: Sequence[dict[str, Any]], vectors: Sequence[Sequence[float]]) -> None:
        """Store vectors keyed by chunk id.

        The chunk id from SQLite is reused as the point id, so a vector hit maps
        straight back to a row without a second lookup table to keep in sync.
        """
        points = [
            PointStruct(
                id=int(chunk["chunk_id"]),
                vector=list(vector),
                payload={
                    "doc_title": chunk["doc_title"],
                    "breadcrumb": chunk["breadcrumb"],
                    "level": chunk["level"],
                    "page_type": chunk.get("page_type", ""),
                    "ordinal": chunk.get("ordinal", 0),
                },
            )
            for chunk, vector in zip(chunks, vectors)
        ]
        if points:
            self.client.upsert(collection_name=COLLECTION, points=points, wait=False)

    # ── reading ──────────────────────────────────────────────────────────────

    def search(
        self,
        vector: Sequence[float],
        limit: int = 30,
        levels: Iterable[int] | None = None,
        doc_titles: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Nearest chunks, optionally restricted to a level or a set of pages.

        Filtering is by document rather than by "entities mentioned in the
        chunk". The previous design filtered on a per-chunk entity list built by
        substring matching, so a single mis-tagged chunk was invisible to a
        query naming its subject. Restricting to graph-selected documents keeps
        the precision benefit without letting a tagging error erase content.
        """
        # Only levels 0 and 2 are ever embedded, and both should be searchable.
        # Filtering to level 2 — as this did — made every document card dead
        # weight: they were embedded, stored, and then never looked at, which is
        # precisely what a question like "what is a binding vow" needs, since a
        # card carries the page's title, type, infobox facts and lead together.
        conditions = []
        wanted = list(levels) if levels is not None else []
        if wanted:
            conditions.append(
                FieldCondition(key="level", match=MatchAny(any=wanted))
                if len(wanted) > 1
                else FieldCondition(key="level", match=MatchValue(value=wanted[0]))
            )
        titles = list(doc_titles or ())
        if titles:
            conditions.append(
                FieldCondition(key="doc_title", match=MatchAny(any=titles))
            )

        hits = self.client.query_points(
            collection_name=COLLECTION,
            query=list(vector),
            query_filter=Filter(must=conditions) if conditions else None,
            limit=limit,
            with_payload=True,
        ).points

        return [
            {
                "chunk_id": int(hit.id),
                "doc_title": hit.payload.get("doc_title", ""),
                "breadcrumb": hit.payload.get("breadcrumb", ""),
                "level": hit.payload.get("level", 2),
                "vector_score": float(hit.score),
            }
            for hit in hits
        ]

    def count(self) -> int:
        try:
            return int(self.client.count(collection_name=COLLECTION).count)
        except Exception:
            return 0

    def exists(self) -> bool:
        try:
            return self.client.collection_exists(COLLECTION)
        except Exception:
            return False

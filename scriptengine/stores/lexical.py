"""BM25 search over the chunk text, via SQLite FTS5.

Lexical retrieval is not a fallback here. Character names, technique names and
episode titles are exactly the queries where dense vectors are weakest — an
embedding of "Boogie Woogie" is not reliably nearer to the passage naming it
than to a hundred other technique descriptions — and where term matching is
strongest.

FTS5 provides BM25 natively and on disk. The previous implementation scrolled
every chunk out of the vector store into RAM and rebuilt a `rank_bm25` index at
each process start, which meant the first query after launch paid for the whole
corpus.
"""

from __future__ import annotations

import re
import sqlite3
from typing import Any

from scriptengine.stores.facts import FactStore

# FTS5 treats these as query syntax. A user asking about `Sukuna's "Domain"`
# would otherwise raise a parse error rather than return results.
_FTS_SPECIAL = re.compile(r'["\'()*:^{}\[\]~+\-]')
_TOKEN = re.compile(r"[\w’]+", re.UNICODE)


def build_match_query(text: str) -> str:
    """Turn free text into a safe FTS5 MATCH expression.

    Each term is quoted, and terms are OR-ed so that a long question still
    matches passages containing only part of it. BM25 then ranks by how many of
    them a passage contains and how rare those terms are, which is the behaviour
    we want: matching more of the query should score higher, but matching some
    of it should not score zero.
    """
    tokens = [token for token in _TOKEN.findall(_FTS_SPECIAL.sub(" ", text)) if token]
    if not tokens:
        return ""
    return " OR ".join(f'"{token}"' for token in tokens)


def search(
    store: FactStore,
    query: str,
    limit: int = 30,
    level: int = 2,
) -> list[dict[str, Any]]:
    """Rank chunks by BM25.

    FTS5's `bm25()` returns a negative number, more negative meaning a better
    match. It is negated here so that every retriever in the system reports
    "higher is better" and fusion does not have to special-case one of them.
    """
    match = build_match_query(query)
    if not match:
        return []

    try:
        rows = store.connection.execute(
            """
            SELECT c.id, c.text, c.doc_title, c.breadcrumb, c.level,
                   c.document_id, c.section_id, c.parent_id, c.ordinal,
                   bm25(chunks_fts, 1.0, 0.5, 0.75) AS score
            FROM chunks_fts
            JOIN chunks c ON c.id = chunks_fts.rowid
            WHERE chunks_fts MATCH ? AND c.level = ?
            ORDER BY score
            LIMIT ?
            """,
            (match, level, limit),
        ).fetchall()
    except sqlite3.OperationalError:
        # A malformed expression should return nothing, not break the query.
        return []

    return [
        {
            "chunk_id": row["id"],
            "text": row["text"],
            "doc_title": row["doc_title"],
            "breadcrumb": row["breadcrumb"],
            "level": row["level"],
            "document_id": row["document_id"],
            "section_id": row["section_id"],
            "parent_id": row["parent_id"],
            "ordinal": row["ordinal"],
            "lexical_score": -float(row["score"]),
        }
        for row in rows
    ]

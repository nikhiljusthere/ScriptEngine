"""The fact store: documents, graph, facts and full-text index in one SQLite file.

Replaces Neo4j and `rank_bm25`. Beyond removing a Docker dependency, this fixes
two concrete defects in the previous design:

* the graph query used ``[r*1..$depth]``, a parameterised variable-length bound
  that Neo4j rejects outright, so graph retrieval failed at runtime. The
  recursive CTE here takes its depth as an ordinary parameter.
* BM25 was rebuilt in memory from a full scroll of the vector store on every
  process start. FTS5 keeps the index on disk.
"""

from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

# Longest alias phrase considered when linking a query to entities. "Kyoto
# Metropolitan Curse Technical College" is six words; beyond that the cost of
# enumerating n-grams stops paying for itself.
MAX_ALIAS_WORDS = 6

_WORD = re.compile(r"[\w'’-]+", re.UNICODE)


class FactStore:
    """Read/write access to one series' `facts.db`."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    # ── lifecycle ────────────────────────────────────────────────────────────

    def __enter__(self) -> "FactStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()

    def initialise(self) -> None:
        self.connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.connection.commit()

    def reset(self) -> None:
        """Drop everything and recreate. Indexing is idempotent by rebuilding."""
        tables = [
            "chunk_nodes", "chunks_fts", "chunks", "facts", "edges",
            "aliases", "nodes", "sections", "documents", "meta",
        ]
        for table in tables:
            self.connection.execute(f"DROP TABLE IF EXISTS {table}")
        self.connection.commit()
        self.initialise()

    def set_meta(self, key: str, value: str) -> None:
        self.connection.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    def get_meta(self, key: str, default: str = "") -> str:
        row = self.connection.execute(
            "SELECT value FROM meta WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    # ── writing ──────────────────────────────────────────────────────────────

    def add_document(
        self,
        *,
        title: str,
        url: str,
        page_type: str,
        infobox_template: str,
        lead: str,
        word_count: int,
        revid: int,
        fetched_at: str,
    ) -> int:
        cursor = self.connection.execute(
            "INSERT INTO documents"
            " (title, url, page_type, infobox_template, lead, word_count, revid, fetched_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            " ON CONFLICT(title) DO UPDATE SET"
            "   url = excluded.url, page_type = excluded.page_type,"
            "   infobox_template = excluded.infobox_template, lead = excluded.lead,"
            "   word_count = excluded.word_count, revid = excluded.revid,"
            "   fetched_at = excluded.fetched_at",
            (title, url, page_type, infobox_template, lead, word_count, revid, fetched_at),
        )
        if cursor.lastrowid:
            return cursor.lastrowid
        row = self.connection.execute(
            "SELECT id FROM documents WHERE title = ?", (title,)
        ).fetchone()
        return int(row["id"])

    def add_section(
        self,
        *,
        document_id: int,
        title: str,
        breadcrumb: str,
        level: int,
        ordinal: int,
        text: str,
        word_count: int,
    ) -> int:
        cursor = self.connection.execute(
            "INSERT INTO sections"
            " (document_id, title, breadcrumb, level, ordinal, text, word_count)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (document_id, title, breadcrumb, level, ordinal, text, word_count),
        )
        return int(cursor.lastrowid)

    def add_node(
        self, name: str, label: str = "unknown", document_id: int | None = None
    ) -> int:
        """Create or update an entity.

        A node is often created as an unresolved link target before the page
        backing it is indexed, so an existing row is only upgraded — a real
        label and document never get overwritten by a later bare mention.
        """
        resolved = 1 if document_id is not None else 0
        self.connection.execute(
            "INSERT INTO nodes (name, label, document_id, is_resolved)"
            " VALUES (?, ?, ?, ?)"
            " ON CONFLICT(name) DO UPDATE SET"
            "   label = CASE WHEN excluded.label != 'unknown'"
            "                THEN excluded.label ELSE nodes.label END,"
            "   document_id = COALESCE(excluded.document_id, nodes.document_id),"
            "   is_resolved = MAX(nodes.is_resolved, excluded.is_resolved)",
            (name, label, document_id, resolved),
        )
        row = self.connection.execute(
            "SELECT id FROM nodes WHERE name = ?", (name,)
        ).fetchone()
        return int(row["id"])

    def add_aliases(self, node_id: int, aliases: Iterable[str]) -> None:
        self.connection.executemany(
            "INSERT OR IGNORE INTO aliases (alias, node_id) VALUES (?, ?)",
            [(alias.strip().lower(), node_id) for alias in aliases if alias.strip()],
        )

    def add_edge(
        self,
        *,
        source_id: int,
        relation: str,
        target_id: int,
        confidence: float,
        provenance: str,
        section: str,
    ) -> None:
        self.connection.execute(
            "INSERT OR IGNORE INTO edges"
            " (source_id, relation, target_id, confidence, provenance, section)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (source_id, relation, target_id, confidence, provenance, section),
        )

    def add_fact(
        self, *, node_id: int, key: str, label: str, value: str, citation: str
    ) -> None:
        self.connection.execute(
            "INSERT INTO facts (node_id, key, label, value, citation)"
            " VALUES (?, ?, ?, ?, ?)",
            (node_id, key, label, value, citation),
        )

    def add_chunk(
        self,
        *,
        document_id: int,
        section_id: int | None,
        parent_id: int | None,
        level: int,
        ordinal: int,
        doc_title: str,
        breadcrumb: str,
        text: str,
    ) -> int:
        cursor = self.connection.execute(
            "INSERT INTO chunks"
            " (document_id, section_id, parent_id, level, ordinal,"
            "  doc_title, breadcrumb, text, word_count)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                document_id, section_id, parent_id, level, ordinal,
                doc_title, breadcrumb, text, len(text.split()),
            ),
        )
        return int(cursor.lastrowid)

    def link_chunk_nodes(self, chunk_id: int, node_ids: Iterable[int]) -> None:
        self.connection.executemany(
            "INSERT OR IGNORE INTO chunk_nodes (chunk_id, node_id) VALUES (?, ?)",
            [(chunk_id, node_id) for node_id in node_ids],
        )

    def rebuild_fts(self) -> None:
        """Populate the external-content FTS5 index from `chunks`."""
        self.connection.execute(
            "INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')"
        )
        self.connection.commit()

    def commit(self) -> None:
        self.connection.commit()

    # ── reading ──────────────────────────────────────────────────────────────

    def counts(self) -> dict[str, int]:
        tables = ("documents", "sections", "nodes", "edges", "facts", "chunks")
        return {
            table: int(
                self.connection.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            )
            for table in tables
        }

    def node_by_name(self, name: str) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT * FROM nodes WHERE name = ? COLLATE NOCASE", (name,)
        ).fetchone()

    def link_entities(self, text: str) -> list[sqlite3.Row]:
        """Find entities mentioned in `text`, matching on whole words only.

        The previous implementation asked ``entity.lower() in text.lower()`` for
        every known entity against every chunk. That is quadratic, and it is
        wrong: "Ryu" matches inside "Ryomen", and the false tag then silently
        removes correct chunks from the filtered vector search.

        Enumerating word n-grams and looking each one up makes boundary errors
        impossible by construction, and turns the scan into an index hit.
        """
        words = _WORD.findall(text)
        if not words:
            return []

        candidates: set[str] = set()
        lowered = [word.lower() for word in words]
        for size in range(1, min(MAX_ALIAS_WORDS, len(lowered)) + 1):
            for start in range(len(lowered) - size + 1):
                candidates.add(" ".join(lowered[start : start + size]))

        placeholders = ",".join("?" * len(candidates))
        # Ranking, in order of how much the match is worth trusting:
        #   1. the matched phrase is the page's own title — unambiguous
        #   2. a page actually backs the entity, so there is something to say
        #   3. a longer matched phrase, which is the more specific reading
        #      ("Kyoto Jujutsu High" over "Kyoto")
        # Harvested aliases are useful but ambiguous: prose writes
        # `[[Sorcerer Clan|Gojo]]` as well as `[[Satoru Gojo|Gojo]]`, and the
        # named page should win over the incidental one.
        return self.connection.execute(
            f"""
            SELECT n.*, MAX(LENGTH(a.alias)) AS match_length,
                   MAX(a.alias = LOWER(n.name)) AS exact
            FROM nodes n
            JOIN aliases a ON a.node_id = n.id
            WHERE a.alias IN ({placeholders})
            GROUP BY n.id
            ORDER BY exact DESC, n.is_resolved DESC, match_length DESC
            """,
            tuple(candidates),
        ).fetchall()

    def neighbours(
        self, node_ids: Sequence[int], depth: int = 2, min_confidence: float = 0.5
    ) -> list[sqlite3.Row]:
        """Entities reachable within `depth` hops, nearest first.

        Edges are traversed in both directions: "Todo affiliation Kyoto High"
        should also let a question about Kyoto High reach Todo.
        """
        if not node_ids:
            return []

        placeholders = ",".join("?" * len(node_ids))
        rows = self.connection.execute(
            f"""
            WITH RECURSIVE reachable(node_id, depth) AS (
                SELECT id, 0 FROM nodes WHERE id IN ({placeholders})
                UNION
                SELECT
                    CASE WHEN e.source_id = r.node_id THEN e.target_id
                         ELSE e.source_id END,
                    r.depth + 1
                FROM reachable r
                JOIN edges e
                  ON e.source_id = r.node_id OR e.target_id = r.node_id
                WHERE r.depth < ? AND e.confidence >= ?
            )
            SELECT n.*, MIN(r.depth) AS hops
            FROM reachable r
            JOIN nodes n ON n.id = r.node_id
            WHERE r.depth > 0
            GROUP BY n.id
            ORDER BY hops ASC, n.is_resolved DESC
            """,
            (*node_ids, depth, min_confidence),
        ).fetchall()
        return rows

    def edges_for(
        self, node_ids: Sequence[int], min_confidence: float = 0.5, limit: int = 60
    ) -> list[sqlite3.Row]:
        """Relationships touching these entities, strongest evidence first."""
        if not node_ids:
            return []
        placeholders = ",".join("?" * len(node_ids))
        return self.connection.execute(
            f"SELECT s.name AS source, e.relation, t.name AS target,"
            f"       e.confidence, e.provenance, e.section"
            f" FROM edges e"
            f" JOIN nodes s ON s.id = e.source_id"
            f" JOIN nodes t ON t.id = e.target_id"
            f" WHERE (e.source_id IN ({placeholders}) OR e.target_id IN ({placeholders}))"
            f"   AND e.confidence >= ?"
            f" ORDER BY e.confidence DESC"
            f" LIMIT ?",
            (*node_ids, *node_ids, min_confidence, limit),
        ).fetchall()

    def facts_for(self, name: str) -> list[sqlite3.Row]:
        """Structured facts for one entity. A lookup, not a search."""
        return self.connection.execute(
            "SELECT f.key, f.label, f.value, f.citation"
            " FROM facts f JOIN nodes n ON n.id = f.node_id"
            " WHERE n.name = ? COLLATE NOCASE"
            " ORDER BY f.id",
            (name,),
        ).fetchall()

    def chunks_by_id(self, chunk_ids: Sequence[int]) -> list[sqlite3.Row]:
        if not chunk_ids:
            return []
        placeholders = ",".join("?" * len(chunk_ids))
        return self.connection.execute(
            f"SELECT * FROM chunks WHERE id IN ({placeholders})", tuple(chunk_ids)
        ).fetchall()

    def parent_of(self, chunk_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT p.* FROM chunks c JOIN chunks p ON p.id = c.parent_id"
            " WHERE c.id = ?",
            (chunk_id,),
        ).fetchone()

    def chunks_for_nodes(
        self, node_ids: Sequence[int], level: int = 2, limit: int = 40
    ) -> list[sqlite3.Row]:
        if not node_ids:
            return []
        placeholders = ",".join("?" * len(node_ids))
        return self.connection.execute(
            f"SELECT DISTINCT c.* FROM chunks c"
            f" JOIN chunk_nodes cn ON cn.chunk_id = c.id"
            f" WHERE cn.node_id IN ({placeholders}) AND c.level = ?"
            f" LIMIT ?",
            (*node_ids, level, limit),
        ).fetchall()

    def document_sections(self, title: str) -> list[sqlite3.Row]:
        """A document's sections in page order — the basis of narrative retrieval."""
        return self.connection.execute(
            "SELECT s.* FROM sections s JOIN documents d ON d.id = s.document_id"
            " WHERE d.title = ? COLLATE NOCASE"
            " ORDER BY s.ordinal",
            (title,),
        ).fetchall()

    def iter_chunks(self, level: int | None = None) -> Iterable[sqlite3.Row]:
        if level is None:
            yield from self.connection.execute("SELECT * FROM chunks ORDER BY id")
        else:
            yield from self.connection.execute(
                "SELECT * FROM chunks WHERE level = ? ORDER BY id", (level,)
            )

    def stats(self) -> dict[str, Any]:
        counts = self.counts()
        counts["types"] = {
            row["page_type"]: row["n"]
            for row in self.connection.execute(
                "SELECT page_type, COUNT(*) AS n FROM documents"
                " GROUP BY page_type ORDER BY n DESC"
            )
        }
        counts["resolved_nodes"] = int(
            self.connection.execute(
                "SELECT COUNT(*) AS n FROM nodes WHERE is_resolved = 1"
            ).fetchone()["n"]
        )
        return counts

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

import json
import re
import sqlite3
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

# Longest alias phrase considered when linking a query to entities. "Kyoto
# Metropolitan Curse Technical College" is six words; beyond that the cost of
# enumerating n-grams stops paying for itself.
MAX_ALIAS_WORDS = 6

_WORD = re.compile(r"[\w'’-]+", re.UNICODE)

# Instalment-style aliases ("chapter 5", "episode 19") and bare numbers ("19")
# are harvested from instalment page titles. They only count as mentions when
# the query names the instalment kind: "19 Days without Satoru Gojo" contains
# the n-gram "19", which links to "Episode 19" and hijacks the whole request.
_INSTALMENT_ALIAS = re.compile(
    r"^(chapter|episode|volume|ova|special|film|movie|arc)s?\s+[\d.\-]+$",
    re.IGNORECASE,
)
_BARE_NUMBER_ALIAS = re.compile(r"^\d+([.\-]\d+)?$")
_INSTALMENT_WORDS = {
    "chapter", "episode", "volume", "ova", "special", "film", "movie", "arc",
}


# Infobox parameters that describe the page's presentation, its Japanese
# rendering, or its place in a navigation chain rather than its subject.
# Rendering them into a script's context spends budget on furniture: a narrative
# bundle led with `prev`, `next`, `romaji` and `kanji` before it reached the
# event's own chapter range.
NOISE_FACT_KEYS = frozenset({
    "romaji", "kanji", "japanese", "name", "image", "image gallery", "imagesize",
    "caption", "cover", "bgcolor", "color", "pages", "issue", "next",
    "previous", "prev", "chapter title", "opening song", "ending song",
})


def _is_packaging(label: str) -> bool:
    """Is this page type an episode, chapter, volume or other packaging?

    `SUBJECT_DEMOTE_TYPES` lists literal infobox ids, and those ids are
    per-wiki: it demotes `episode` on Dragon Ball and misses `episode_box` on
    One Piece, `hunterpedia_episode_2011` on Hunterpedia,
    `bleach_wiki_episode` on Bleach. Measured, the list matched 11 of its 12 ids
    on Jujutsu Kaisen (where it was written) and 1 of 12 on One Piece, leaving
    2,676 of its pages eligible to be chosen as the subject of a question.

    So the id is folded into the shared vocabulary first, and the explicit list
    is kept as an override for anything that fold gets wrong.
    """
    from scriptengine.retrieve.semantics import MEDIA, type_from_page_type

    return type_from_page_type(label) == MEDIA


def rank_subjects(
    rows: Sequence[Any], demote: Sequence[str], priority: Sequence[str]
) -> list[Any]:
    """Re-rank linked entities by how likely each is to be a script's subject.

    `link_entities` ranks by how confident the *match* is, which is the right
    answer for search and the wrong one for "what is this script about". Asked
    for "Every Rank of Curse in Jujutsu Kaisen" it returns the series page
    `Jujutsu Kaisen` first, an exact alias match, and the timeline came back
    as a single beat from `Volume 0`. Asked for "Every Cursed Technique of
    Sukuna" it returns the generic `Cursed Technique` concept page ahead of
    Sukuna, because "cursed technique" is the longer alias.

    So the sort is: pages that package the work go last; among the rest the
    wiki's own page type decides, since a script is about a person or an event
    far more often than about a concept; and the match confidence `link_entities`
    already computed breaks the remaining ties.

    Type priority is checked before exactness deliberately. "Jujutsu" is an
    exact match for the technique page on a query about curse ranks, and it is
    still not what the script is about.
    """
    demoted = {t.lower() for t in demote}
    order = {t.lower(): index for index, t in enumerate(priority)}
    unranked = len(order)

    def key(pair: tuple[int, Any]) -> tuple[int, int, int, int]:
        index, row = pair
        label = (row["label"] or "unknown").lower()
        return (
            1 if (label in demoted or _is_packaging(label)) else 0,
            order.get(label, unranked),
            0 if row["exact"] else 1,
            index,
        )

    return [row for _, row in sorted(enumerate(rows), key=key)]


def _tail_pattern(leaf: str) -> re.Pattern[str]:
    """SQLite's ``breadcrumb LIKE '%/ ' || leaf``, as a regex.

    Needed because `%` and `_` are wildcards to LIKE and real headings contain
    them: `100% Full Power` is one of Frieza's forms, and its pattern
    `%/ 100% full power` has a wildcard in the middle. A plain `endswith` would
    match fewer pages than the query it replaces, which is a behaviour change
    dressed up as an optimisation.

    LIKE folds case for ASCII only, which `IGNORECASE | ASCII` reproduces; its
    wildcards match newlines, which `DOTALL` does.
    """
    body = "".join(
        "." if character == "_" else ".*" if character == "%" else re.escape(character)
        for character in leaf
    )
    return re.compile(
        ".*" + re.escape("/ ") + body, re.IGNORECASE | re.ASCII | re.DOTALL
    )


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
            "aliases", "nodes", "categories", "sections", "documents", "meta",
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

    def add_categories(self, document_id: int, categories: Iterable[str]) -> None:
        self.connection.executemany(
            "INSERT OR IGNORE INTO categories (document_id, category) VALUES (?, ?)",
            [
                (document_id, category.strip())
                for category in categories
                if category and category.strip()
            ],
        )

    def add_node(
        self, name: str, label: str = "unknown", document_id: int | None = None
    ) -> int:
        """Create or update an entity.

        A node is often created as an unresolved link target before the page
        backing it is indexed, so an existing row is only upgraded: a real
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
        tables = (
            "documents", "sections", "categories", "nodes", "edges", "facts", "chunks",
        )
        counts: dict[str, int] = {}
        for table in tables:
            try:
                counts[table] = int(
                    self.connection.execute(
                        f"SELECT COUNT(*) AS n FROM {table}"
                    ).fetchone()["n"]
                )
            except sqlite3.OperationalError:
                # A store built by an older schema is missing tables added
                # since. Reporting zero and carrying on is right: this is what
                # `list`, `catalogue` and `/series` call to *describe* a series,
                # and refusing to describe a stale index is how you end up
                # unable to see that it is stale.
                counts[table] = 0
        return counts

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
        # The same words with possessives removed. `_WORD` keeps the apostrophe
        # deliberately, since names like `Zabuza's` and `O'Hara` both occur.
        # so "Ichigo's" was one token that matched no alias, and
        # "What is Ichigo's Zanpakuto?" linked *nothing at all*. Both spellings
        # are offered rather than picking one, because the possessive form is
        # occasionally the real title.
        plain = [
            word[:-2] if word.endswith("'s") or word.endswith("’s") else word.rstrip("'’")
            for word in lowered
        ]
        for sequence in (lowered, plain):
            for size in range(1, min(MAX_ALIAS_WORDS, len(sequence)) + 1):
                for start in range(len(sequence) - size + 1):
                    phrase = " ".join(sequence[start : start + size]).strip()
                    if phrase:
                        candidates.add(phrase)

        mentions_instalment = any(word in _INSTALMENT_WORDS for word in lowered)
        placeholders = ",".join("?" * len(candidates))
        # Ranking, in order of how much the match is worth trusting:
        #   1. the matched phrase is the page's own title, unambiguous
        #   2. a page actually backs the entity, so there is something to say
        #   3. a longer matched phrase, which is the more specific reading
        #      ("Kyoto Jujutsu High" over "Kyoto")
        #   4. the shortest node name, the entity itself rather than one of
        #      its event pages. "Yuji" matches both "Yuji Itadori" and "Yuji
        #      Itadori, Maki Zenin & Hana Kurusu vs. Sukuna" with the same
        #      alias; the character page is the hub, and it should win.
        # Harvested aliases are useful but ambiguous: prose writes
        # `[[Sorcerer Clan|Gojo]]` as well as `[[Satoru Gojo|Gojo]]`, and the
        # named page should win over the incidental one.
        rows = self.connection.execute(
            f"""
            SELECT n.*,
                   MAX(a.alias) AS matched_alias,
                   MAX(a.alias = LOWER(n.name)) AS exact,
                   MAX(LENGTH(a.alias)) AS match_length
            FROM nodes n
            JOIN aliases a ON a.node_id = n.id
            WHERE a.alias IN ({placeholders})
            GROUP BY n.id
            ORDER BY exact DESC, n.is_resolved DESC, match_length DESC,
                     MIN(LENGTH(n.name)) ASC
            """,
            tuple(candidates),
        ).fetchall()

        # An instalment alias only counts when the query says the instalment
        # kind; a bare number on its own is not a mention of "Episode 19".
        if not mentions_instalment:
            rows = [
                row
                for row in rows
                if not (
                    _INSTALMENT_ALIAS.match(row["matched_alias"] or "")
                    or _BARE_NUMBER_ALIAS.match(row["matched_alias"] or "")
                )
            ]
        return rows

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

    def linked_from(self, name: str, relations: Sequence[str]) -> list[str]:
        """Pages this one points at through the named infobox fields.

        The infobox rows arrive already resolved by MediaWiki, so `user` on
        `Kaio-ken` is a list of pages (Goku, Krillin, Yamcha) rather than a
        string to be parsed. Ability classification reads them to decide whether
        something is race-exclusive or merely teachable.
        """
        if not relations:
            return []
        placeholders = ",".join("?" * len(relations))
        return [
            row["target"]
            for row in self.connection.execute(
                f"SELECT DISTINCT t.name AS target FROM edges e"
                f" JOIN nodes s ON s.id = e.source_id"
                f" JOIN nodes t ON t.id = e.target_id"
                f" WHERE s.name = ? COLLATE NOCASE"
                f"   AND LOWER(e.relation) IN ({placeholders})",
                (name, *[r.lower() for r in relations]),
            )
        ]

    def owned_by(self, owner: str, relations: Sequence[str]) -> list[str]:
        """Pages that name `owner` through the named infobox fields.

        `linked_from` walks out of a page; this walks into one. Having only the
        outward direction is why a character qualifier was tested against page
        *text* rather than against the ownership the wiki actually recorded:

            Super Saiyan Rosé   users = Goku Black, Fused Zamasu, …

        "goku" is a substring of that string, so it was kept as one of Goku's
        forms. The edge rows are already resolved to one row per user, so asking
        which pages name `Goku` cannot match `Goku Black`; they are different
        nodes. No flat-text test can make that distinction, because the wiki
        writes every user of a page into a single field.
        """
        if not relations:
            return []
        placeholders = ",".join("?" * len(relations))
        return [
            row["source"]
            for row in self.connection.execute(
                f"SELECT DISTINCT s.name AS source FROM edges e"
                f" JOIN nodes s ON s.id = e.source_id"
                f" JOIN nodes t ON t.id = e.target_id"
                f" WHERE t.name = ? COLLATE NOCASE"
                f"   AND LOWER(e.relation) IN ({placeholders})",
                (owner, *[r.lower() for r in relations]),
            )
        ]

    def sections_of(self, page: str) -> list[sqlite3.Row]:
        """Every section of a page and of its subpages, once each.

        `DISTINCT` is not cosmetic: chunks carry both a level-1 and a level-2
        row for the same breadcrumb, so counting them raw doubles every member
        derived from a heading.

        Subpages are included because the wikis that keep abilities as prose
        also tend to move them off the character's page.
        `Monkey D. Luffy/Abilities and Powers` is where the Gears are, and
        Luffy's own page has no ability section at all.
        """
        return self.connection.execute(
            "SELECT c.breadcrumb AS breadcrumb, d.title AS title,"
            "       c.text AS text, MIN(c.ordinal) AS ordinal"
            " FROM chunks c JOIN documents d ON d.id = c.document_id"
            " WHERE d.title = ? COLLATE NOCASE OR d.title LIKE ? COLLATE NOCASE"
            " GROUP BY d.title, c.breadcrumb"
            " ORDER BY d.title, ordinal",
            (page, f"{page}/%"),
        ).fetchall()

    def pages_per_section(self, leaves: Sequence[str]) -> dict[str, int]:
        """How many pages carry each of these section headings.

        The wiki's own templates repeat: `Physical Abilities` heads a section on
        216 One-Punch Man pages and `Nen` on 258 Hunterpedia ones, because every
        character article is built from the same skeleton. A heading that names
        an actual ability does not repeat: `Gear 2` appears on two pages,
        `Gear 5 (Awakening)` on one, `Berserker Armor` on four.

        That gap is what separates a container from a member, and it is a
        property of the corpus rather than of any series, so it needs no
        declaration.

        One scan, not one per heading. This used to run

            WHERE LOWER(TRIM(c.breadcrumb)) = ? OR LOWER(TRIM(c.breadcrumb)) LIKE ?

        once per leaf. Wrapping the column in `LOWER(TRIM(...))` puts every
        index out of reach, so each of those was a full scan of all 68,904 chunk
        rows at ~60ms, and a Goku roster passes 64 headings: 4.6s of a 7.5s
        request. The same two predicates evaluated over a single pass of the
        34,011 distinct (heading, page) pairs are flat in the number of headings
        instead of linear in it, measured on `series/db`, headings against
        seconds:

            1      0.059 → 0.098      64     3.869 → 0.099   (39x)
            8      0.478 → 0.097     128     7.731 → 0.103   (75x)
            32     1.878 → 0.100     174    10.492 → 0.098  (108x)

        One heading is the only input this loses on, and nothing asks for one:
        the sole caller, `roster._drop_templates`, hands over a whole roster.
        """
        if not leaves:
            return {}
        wanted = {name.strip().lower() for name in leaves if name.strip()}
        found: dict[str, set[int]] = {leaf: set() for leaf in wanted}
        # `LIKE '%/ ' || leaf` says the crumb *ends* at this heading, so the
        # leaves a crumb answers to are its own tail segments, so a dict lookup
        # each, for as many `/ ` as the crumb has (three, at the deepest
        # measured). Only headings holding a LIKE wildcard need the pattern.
        plain = {leaf for leaf in wanted if "%" not in leaf and "_" not in leaf}
        wildcards = [(leaf, _tail_pattern(leaf)) for leaf in wanted - plain]

        # The crumb is still normalised by SQLite rather than by Python, because
        # the two disagree: SQLite's LOWER folds ASCII only, so `Hiroshi Ōtake`
        # keeps its `Ō` and does not match a Python-lowered `ōtake`. Folding it
        # here instead would quietly change which headings match.
        pages: dict[str, set[int]] = {}
        for row in self.connection.execute(
            "SELECT DISTINCT LOWER(TRIM(c.breadcrumb)) AS crumb,"
            "       c.document_id AS document_id"
            " FROM chunks c WHERE c.breadcrumb IS NOT NULL"
        ):
            pages.setdefault(row["crumb"], set()).add(row["document_id"])

        for crumb, documents in pages.items():
            if crumb in found:                       # the `=` arm
                found[crumb] |= documents
            cut = crumb.find("/ ")
            while cut != -1:                         # the LIKE arm
                tail = crumb[cut + 2:]
                if tail in plain:
                    found[tail] |= documents
                cut = crumb.find("/ ", cut + 1)
            for leaf, pattern in wildcards:
                if pattern.fullmatch(crumb):
                    found[leaf] |= documents
        return {leaf: len(documents) for leaf, documents in found.items()}

    def pages_named(self, word: str, limit: int = 12) -> list[sqlite3.Row]:
        """Root pages whose title contains `word`, largest first.

        Rolled up to the root page because these wikis split a major character
        across subpages, and the parts outweigh the whole: the four largest
        pages matching "luffy" are `Monkey D. Luffy/History/Non-Canon`,
        `/Relationships/Citizens`, `/Relationships/Pirates` and
        `/Relationships/Emperors`, none of which is Luffy. Summing them onto
        `Monkey D. Luffy` puts the character first, which is what asking about
        "Luffy" means, and stops `Yamamoto Luffy`, a different character
        entirely, from being the answer.
        """
        return self.connection.execute(
            "SELECT CASE WHEN instr(d.title, '/') > 0"
            "            THEN substr(d.title, 1, instr(d.title, '/') - 1)"
            "            ELSE d.title END AS root,"
            "       COUNT(c.id) AS size"
            " FROM documents d LEFT JOIN chunks c ON c.document_id = d.id"
            " WHERE d.title LIKE ? COLLATE NOCASE"
            " GROUP BY root ORDER BY size DESC LIMIT ?",
            (f"%{word}%", limit),
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

    def ensure_semantics(self) -> None:
        """Create the classification table if this store predates it.

        Every other table is rebuilt by `index`, so a schema change reaches them
        on the next run. This one deliberately survives `reset()`: it holds
        minutes of local inference per wiki, which means an existing store has
        to be able to grow it in place.
        """
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS semantics ("
            " title TEXT PRIMARY KEY, revid INTEGER, prompt_version TEXT,"
            " semantic_type TEXT, properties TEXT, reason TEXT, model TEXT,"
            " classified_at TEXT)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_semantics_type"
            " ON semantics(semantic_type)"
        )

    def ensure_abilities(self) -> None:
        """Create the extracted-abilities table if this store predates it.

        Survives `reset()` for the same reason `semantics` does: it holds
        minutes of local inference per wiki, and an `index` run must not throw
        that away.
        """
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS abilities ("
            " character TEXT, name TEXT, kind TEXT, acquired TEXT, section TEXT,"
            " revid INTEGER, prompt_version TEXT, reason TEXT, model TEXT,"
            " extracted_at TEXT,"
            " PRIMARY KEY (character, name))"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS abilities_by_character"
            " ON abilities (character COLLATE NOCASE)"
        )
        # Added after the table existed, so a store built before it needs the
        # column rather than a migration script.
        if "acquired" not in {
            row[1] for row in self.connection.execute("PRAGMA table_info(abilities)")
        }:
            self.connection.execute("ALTER TABLE abilities ADD COLUMN acquired TEXT")
        self.connection.commit()

    def abilities_of(self, character: str, kinds: Sequence[str] = ()) -> list[sqlite3.Row]:
        """Abilities extracted for one character. A keyed lookup, never a model.

        Retrieval reads this table and nothing else, so the same question
        answers the same way twice and the eval sets stay a regression guard.
        """
        # `acquired` was added after these stores were written, and a series
        # that has not been re-extracted since does not have the column. Naming
        # it unconditionally raised `OperationalError`, which the handler below
        # turned into "this character has no abilities" -- silently, for every
        # character of four wikis at once, and a canon run lost 152 items to it
        # before anything said a word. Asked for rather than assumed.
        columns = "name, kind, acquired, section, reason"
        try:
            present = {
                row[1] for row in self.connection.execute(
                    "PRAGMA table_info(abilities)")
            }
        except sqlite3.OperationalError:
            return []
        if not present:
            return []
        if "acquired" not in present:
            columns = "name, kind, section, reason"

        try:
            if kinds:
                placeholders = ",".join("?" * len(kinds))
                return self.connection.execute(
                    f"SELECT {columns} FROM abilities"
                    f" WHERE character = ? COLLATE NOCASE AND kind IN ({placeholders})"
                    " ORDER BY rowid",
                    (character, *kinds),
                ).fetchall()
            return self.connection.execute(
                f"SELECT {columns} FROM abilities"
                " WHERE character = ? COLLATE NOCASE ORDER BY rowid",
                (character,),
            ).fetchall()
        except sqlite3.OperationalError:
            # A store built before extraction existed holds none, which is a
            # complete answer.
            return []

    def extraction_state(self, character: str) -> sqlite3.Row | None:
        """What revision and prompt this character was last extracted under."""
        try:
            return self.connection.execute(
                "SELECT revid, prompt_version FROM abilities"
                " WHERE character = ? COLLATE NOCASE LIMIT 1",
                (character,),
            ).fetchone()
        except sqlite3.OperationalError:
            return None

    def save_abilities(
        self,
        character: str,
        found: Sequence[dict[str, str]],
        revid: int | None,
        prompt_version: str,
        model: str,
    ) -> None:
        """Replace everything stored for one character, in one transaction.

        Replaced rather than merged: a re-run under a new prompt or a new
        revision is the whole answer for that character, and leaving the old
        rows behind would silently union two different prompts' opinions.
        """
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.connection.execute(
            "DELETE FROM abilities WHERE character = ? COLLATE NOCASE", (character,)
        )
        self.connection.executemany(
            "INSERT OR REPLACE INTO abilities"
            " (character, name, kind, acquired, section, revid, prompt_version,"
            "  reason, model, extracted_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    character,
                    str(row.get("name") or "").strip(),
                    str(row.get("kind") or "").strip().lower(),
                    (str(row.get("acquired") or "innate").strip().lower() or "innate"),
                    str(row.get("section") or "").strip(),
                    revid,
                    prompt_version,
                    str(row.get("reason") or "").strip()[:300],
                    model,
                    stamp,
                )
                for row in found
                if str(row.get("name") or "").strip()
            ],
        )
        self.connection.commit()

    def ensure_relations(self) -> None:
        """Create the extracted-relations table if this store predates it.

        Survives `reset()` for the same reason `abilities` does: it holds local
        inference an `index` run must not throw away.

        Keyed on all three of subject, other and relation. Two characters can
        hold more than one relation at once and the wiki says so -- Gojo and
        Geto are classmates *and* enemies -- and keying on the pair alone would
        keep whichever was written last.
        """
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS relations ("
            " character TEXT, other TEXT, relation TEXT, era TEXT, section TEXT,"
            " quote TEXT, revid INTEGER, prompt_version TEXT, model TEXT,"
            " extracted_at TEXT,"
            " PRIMARY KEY (character, other, relation))"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS relations_by_character"
            " ON relations (character COLLATE NOCASE)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS relations_by_other"
            " ON relations (other COLLATE NOCASE)"
        )
        self.connection.commit()

    def relations_of(self, character: str, both_ways: bool = True) -> list[sqlite3.Row]:
        """Relations extracted for one character. A keyed lookup, never a model.

        `both_ways` also returns the rows where this character is the *other*
        end, because the wiki writes a relationship on whichever page it feels
        like: Geto's page carries the Gojo relationship and Gojo's may not carry
        Geto's. A script asking "who is Gojo to" wants both.
        """
        try:
            if both_ways:
                return self.connection.execute(
                    "SELECT character, other, relation, era, section, quote"
                    " FROM relations WHERE character = ? COLLATE NOCASE"
                    "    OR other = ? COLLATE NOCASE",
                    (character, character),
                ).fetchall()
            return self.connection.execute(
                "SELECT character, other, relation, era, section, quote"
                " FROM relations WHERE character = ? COLLATE NOCASE",
                (character,),
            ).fetchall()
        except sqlite3.OperationalError:
            # A store built before relations existed. Nothing is extracted in
            # it, which is a complete answer.
            return []

    def relation_state(self, character: str) -> sqlite3.Row | None:
        """What prompt and revision this character's relations were read under."""
        try:
            return self.connection.execute(
                "SELECT revid, prompt_version FROM relations"
                " WHERE character = ? COLLATE NOCASE LIMIT 1",
                (character,),
            ).fetchone()
        except sqlite3.OperationalError:
            return None

    def save_relations(
        self,
        character: str,
        found: Sequence[dict[str, str]],
        revid: int | None,
        prompt_version: str,
        model: str,
    ) -> None:
        """Replace everything stored for one character, in one transaction.

        Replaced rather than merged, exactly as `save_abilities` is: a re-run
        under a new prompt is the whole answer for that character, and keeping
        the old rows would union two prompts' opinions.

        Only rows where the subject is this character are deleted. A row naming
        them as the *other* end belongs to whoever's page it was read from, and
        deleting it here would throw away that page's reading.
        """
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.connection.execute(
            "DELETE FROM relations WHERE character = ? COLLATE NOCASE", (character,)
        )
        self.connection.executemany(
            "INSERT OR REPLACE INTO relations"
            " (character, other, relation, era, section, quote, revid,"
            "  prompt_version, model, extracted_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    character,
                    str(row.get("other") or "").strip(),
                    str(row.get("relation") or "").strip().lower(),
                    str(row.get("era") or "").strip(),
                    str(row.get("section") or "").strip(),
                    str(row.get("quote") or "").strip()[:400],
                    revid,
                    prompt_version,
                    model,
                    stamp,
                )
                for row in found
                if str(row.get("other") or "").strip()
                and str(row.get("relation") or "").strip()
            ],
        )
        self.connection.commit()

    def semantics_of(self, title: str) -> dict[str, Any] | None:
        """The stored classification for one page, or ``None``.

        Read on every roster query, so it must stay a keyed lookup: the whole
        point of classifying at index time is that retrieval does no reasoning.
        """
        try:
            row = self.connection.execute(
                "SELECT semantic_type, properties, reason, revid, prompt_version"
                " FROM semantics WHERE title = ? COLLATE NOCASE",
                (title,),
            ).fetchone()
        except sqlite3.OperationalError:
            # A store built before classification existed. Nothing is classified
            # in it, which is a complete answer.
            return None
        if not row:
            return None
        try:
            properties = json.loads(row["properties"] or "{}")
        except json.JSONDecodeError:
            properties = {}
        return {
            "semantic_type": row["semantic_type"] or "",
            "properties": properties if isinstance(properties, dict) else {},
            "reason": row["reason"] or "",
            "revid": row["revid"],
            "prompt_version": row["prompt_version"] or "",
        }

    def save_semantics(
        self,
        title: str,
        revid: int | None,
        prompt_version: str,
        semantic_type: str,
        properties: dict[str, Any],
        reason: str,
        model: str,
    ) -> None:
        self.connection.execute(
            "INSERT INTO semantics"
            " (title, revid, prompt_version, semantic_type, properties, reason,"
            "  model, classified_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            " ON CONFLICT(title) DO UPDATE SET"
            "   revid = excluded.revid,"
            "   prompt_version = excluded.prompt_version,"
            "   semantic_type = excluded.semantic_type,"
            "   properties = excluded.properties,"
            "   reason = excluded.reason,"
            "   model = excluded.model,"
            "   classified_at = excluded.classified_at",
            (
                title,
                revid,
                prompt_version,
                semantic_type,
                json.dumps(properties, ensure_ascii=False),
                reason,
                model,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )

    def categories_of(self, title: str) -> list[str]:
        """Every category one page is filed under.

        Membership validation reads these: the Dragon Ball wiki files
        `Black Frieza` under both `Transformations` and `Frieza's race`, which
        is what makes it answerable that it does not belong in a list of Saiyan
        transformations.
        """
        return [
            row["category"]
            for row in self.connection.execute(
                "SELECT c.category FROM categories c"
                " JOIN documents d ON d.id = c.document_id"
                " WHERE d.title = ? COLLATE NOCASE",
                (title,),
            )
        ]

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
        # The order matters even though these rows are only a ranking input:
        # reciprocal rank fusion weights position, and `LIMIT` without
        # `ORDER BY` handed it whatever order SQLite happened to scan in. That
        # made the graph retriever's contribution to the fused score arbitrary
        # and non-reproducible across rebuilds.
        return self.connection.execute(
            f"SELECT DISTINCT c.* FROM chunks c"
            f" JOIN chunk_nodes cn ON cn.chunk_id = c.id"
            f" WHERE cn.node_id IN ({placeholders}) AND c.level = ?"
            f" ORDER BY c.document_id, c.ordinal"
            f" LIMIT ?",
            (*node_ids, level, limit),
        ).fetchall()

    # ── enumeration ──────────────────────────────────────────────────────────
    #
    # Three ways a wiki already states "these things belong together". A roster
    # script needs a complete set, and retrieval ranks; it does not enumerate.

    def nodes_by_label(self, label: str, limit: int = 200) -> list[sqlite3.Row]:
        """Every resolved entity of one page type, e.g. every `technique`."""
        return self.connection.execute(
            "SELECT * FROM nodes WHERE label = ? COLLATE NOCASE AND is_resolved = 1"
            " ORDER BY name LIMIT ?",
            (label, limit),
        ).fetchall()

    def documents_in_category(self, category: str, limit: int = 200) -> list[sqlite3.Row]:
        """Pages the wiki filed under one category."""
        return self.connection.execute(
            "SELECT d.* FROM documents d"
            " JOIN categories c ON c.document_id = d.id"
            " WHERE c.category = ? COLLATE NOCASE"
            " ORDER BY d.title LIMIT ?",
            (category, limit),
        ).fetchall()

    def categories_like(self, term: str, limit: int = 20) -> list[sqlite3.Row]:
        """Categories whose name contains `term`, largest first."""
        return self.connection.execute(
            "SELECT c.category, COUNT(*) AS members FROM categories c"
            " WHERE c.category LIKE ? COLLATE NOCASE"
            " GROUP BY c.category ORDER BY members DESC LIMIT ?",
            (f"%{term}%", limit),
        ).fetchall()

    def fact_groups(self, key: str, limit: int = 400) -> list[sqlite3.Row]:
        """Who holds which value of one infobox field.

        The wiki's own answer to "what are the ranks": the distinct values of
        `grade` across every page that declares one, and who holds each. No
        prose is involved, so nothing is missed and nothing is invented.
        """
        return self.connection.execute(
            "SELECT f.value, n.name, n.label FROM facts f"
            " JOIN nodes n ON n.id = f.node_id"
            " WHERE f.key = ? COLLATE NOCASE AND n.is_resolved = 1"
            " ORDER BY f.value, n.name LIMIT ?",
            (key, limit),
        ).fetchall()

    def fact_keys(self, limit: int = 400) -> list[sqlite3.Row]:
        """Infobox fields in use, with the wiki's label and how many declare each.

        The label matters as much as the key: Jujutsu Kaisen stores a curse's
        rank under `class` and renders it as "Grade", so a query asking about
        grades only finds the field through the label.
        """
        return self.connection.execute(
            "SELECT key, MAX(label) AS label, COUNT(DISTINCT node_id) AS holders"
            " FROM facts GROUP BY key ORDER BY holders DESC LIMIT ?",
            (limit,),
        ).fetchall()

    def edges_by_relation(self, relation: str, limit: int = 2000) -> list[sqlite3.Row]:
        """Every edge of one kind, as ``(source, target)`` names."""
        return self.connection.execute(
            "SELECT s.name AS source, t.name AS target FROM edges e"
            " JOIN nodes s ON s.id = e.source_id"
            " JOIN nodes t ON t.id = e.target_id"
            " WHERE e.relation = ? LIMIT ?",
            (relation, limit),
        ).fetchall()

    def document_lead(self, title: str) -> str:
        row = self.connection.execute(
            "SELECT lead FROM documents WHERE title = ? COLLATE NOCASE", (title,)
        ).fetchone()
        return (row["lead"] or "") if row else ""

    def document_sections(self, title: str) -> list[sqlite3.Row]:
        """A document's sections in page order, the basis of narrative retrieval."""
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

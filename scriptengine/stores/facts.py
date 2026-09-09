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
import logging
import re
import sqlite3
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scriptengine.ingest.verbatim import quoted_in
from scriptengine.index.chunker import sentence_content_hash, split_sentences

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

# The frozen four-word semantic vocabulary for the per-line meaning index (R1).
# A `CHECK` in the `meaning` table enforces it so a stored row can never carry
# a class the pass does not emit. Deliberately a constant: the pass and the
# store must agree on the words, and neither may drift.
MEANING_CLASSES = ("event", "standing state", "trait", "trivia")

# The `meaning` table's full DDL, shared by the fresh-create and the contract
# migration so the two paths cannot diverge. Carries the durable key
# (doc_title, section_ordinal, sentence_ordinal, content_hash) and the quality
# contract: the class vocabulary CHECK and the `is_event` derivation CHECK.
_MEANING_TABLE_DDL = (
    "CREATE TABLE IF NOT EXISTS meaning ("
    " section_id INTEGER NOT NULL REFERENCES sections(id)"
    "   ON DELETE CASCADE,"
    " sentence_ordinal INTEGER NOT NULL DEFAULT 0,"
    " content_hash TEXT,"
    " class TEXT CHECK (class IS NULL OR class IN"
    "   ('event', 'standing state', 'trait', 'trivia')),"
    " is_event INTEGER NOT NULL DEFAULT 0 CHECK (is_event ="
    "   CASE WHEN class = 'event' AND arc_index IS NOT NULL"
    "   THEN 1 ELSE 0 END),"
    " participants TEXT, arc_index INTEGER, chapter TEXT,"
    " doc_title TEXT NOT NULL DEFAULT '',"
    " section_ordinal INTEGER NOT NULL DEFAULT 0,"
    " revid INTEGER, prompt_version TEXT, model TEXT,"
    " extracted_at TEXT,"
    " PRIMARY KEY (section_id, sentence_ordinal))"
)

# Longest alias phrase considered when linking a query to entities. "Kyoto
# Metropolitan Curse Technical College" is six words; beyond that the cost of
# enumerating n-grams stops paying for itself.
MAX_ALIAS_WORDS = 6

_WORD = re.compile(r"[\w'’-]+", re.UNICODE)

# A qualified title the query names outright, "Noritoshi Kamo (Ancestor)".
# `_WORD` drops the parentheses, so the word n-grams above yield "noritoshi kamo
# ancestor" and never the alias's "noritoshi kamo (ancestor)" -- the qualified
# entity then links only through its unqualified base, whose `exact` flag loses
# to the base-name entity's. Capture the "Name (Qualifier)" span verbatim and
# offer its lowercased form as an extra candidate. Each base word must start
# uppercase (a proper-noun run), so the base is the entity's name, not the
# sentence that leads into it ("...about Noritoshi Kamo (Ancestor)" captures
# "Noritoshi Kamo", not "What are ... about Noritoshi Kamo").
_QUALIFIED = re.compile(r"([A-Z][\w'’\-]*(?:\s+[A-Z][\w'’\-]*)*)\s*\(([^()]+)\)")

logger = logging.getLogger(__name__)

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


class ResetRefusedError(RuntimeError):
    """A rebuild was refused because the derived model layers are non-empty and
    the rebuild was not forced. See `FactStore.require_rebuild`. This is the
    reset guard (0B): a reflexive `index` must never destroy an extraction
    pass; an explicit `--force` rebuilds and remaps the rows instead of wiping."""


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

    def reset(self) -> dict[str, list[dict[str, Any]]]:
        """Drop everything, recreate it, and return the derived layers' rows.

        The two derived, model-built tables -- ``events`` and ``meaning`` --
        are keyed on this build's ``nodes``/``sections`` ids, which a rebuild
        renumbers, so a plain drop would orphan their rows. Before dropping,
        their rows are snapshotted -- each carrying its durable key,
        (doc_title, section_ordinal) plus the participant names for ``events``
        and sentence_ordinal / content_hash for ``meaning`` -- and, when
        non-empty, written to the crash-recovery file beside the database
        (:meth:`_snapshot_path`). The in-memory snapshot is what a live build
        hands back to :meth:`remap_derived` after the base tables are
        repopulated, which re-keys each surviving row onto its new ids and
        drops only what went stale (its document's ``revid`` changed),
        orphaned (its section or node no longer exists) or unverified (the
        section's content moved under a parser fix and no longer proves the
        row). A build that dies between the drop and the remap recovers from
        the file instead: the next run finds the derived layers empty, passes
        the guard, and :meth:`remap_derived` -- called with no snapshot --
        reads the file. The guard that stops a reflexive rebuild from ever
        reaching this point lives in :meth:`require_rebuild`, not here.

        Returns the snapshot (possibly empty); hand it to ``remap_derived``.
        """
        # Guarantee the durable-key columns exist and are backfilled before the
        # snapshot, so a store that predates them can still be remapped. Only
        # touch a derived table that actually exists: on a fresh store neither
        # does, and its base tables (which the backfills read) do not yet.
        snapshot: dict[str, list[dict[str, Any]]] = {}
        for table in ("events", "meaning"):
            exists = self.connection.execute(
                "SELECT name FROM sqlite_master"
                " WHERE type = 'table' AND name = ?", (table,)
            ).fetchone()
            if exists is None:
                continue
            (self.ensure_events if table == "events"
             else self.ensure_meaning)()
            snapshot[table] = [
                dict(row) for row in self.connection.execute(
                    f"SELECT * FROM {table}"
                )
            ]
        # Written before the drop, so the file and the tables can never both
        # be gone: a crash after the drop is exactly the case the file
        # recovers. An empty snapshot never overwrites the file, because a
        # re-run after a crash finds the derived layers already empty and
        # must leave the recovery copy in place.
        if any(snapshot.values()):
            self._write_snapshot_file(snapshot)
        tables = [
            # `events` + `meaning` drop with the base tables on every rebuild;
            # the snapshot this method returns keeps their rows alive for
            # `remap_derived` to re-key onto the new build's ids.
            "events",
            "meaning",
            "chunk_nodes", "chunks_fts", "chunks", "facts", "edges",
            "aliases", "nodes", "categories", "emphasis", "sections",
            "documents", "meta",
        ]
        for table in tables:
            self.connection.execute(f"DROP TABLE IF EXISTS {table}")
        self.connection.commit()
        self.initialise()
        return snapshot

    def _snapshot_path(self) -> Path:
        """The crash-recovery copy of the last ``reset``'s snapshot.

        A forced rebuild is a multi-minute base load between the drop and the
        remap, so a death in that window used to wipe the extraction rows for
        good. ``reset`` writes the file before dropping the derived tables
        and :meth:`remap_derived` deletes it once the rows are back in the
        new build; anything in between is recoverable.
        """
        return self.path.with_name(self.path.name + ".reset-snapshot")

    def _write_snapshot_file(self, snapshot: dict[str, list[dict[str, Any]]]) -> None:
        self._snapshot_path().write_text(
            json.dumps(snapshot, ensure_ascii=False), encoding="utf-8"
        )

    def _read_snapshot_file(self) -> dict[str, list[dict[str, Any]]]:
        path = self._snapshot_path()
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise RuntimeError(
                f"the reset snapshot {path.name} is unreadable ({error}); the "
                "derived rows it holds cannot be remapped. Restore the file, "
                "or delete it deliberately and re-extract, then re-run the "
                "forced index"
            ) from error

    def _drop_snapshot_file(self) -> None:
        self._snapshot_path().unlink(missing_ok=True)

    def require_rebuild(self, *, force: bool = False) -> None:
        """The reset guard (0B): refuse a rebuild while the derived model
        layers are non-empty, unless ``force``.

        ``build.py`` calls this before :meth:`reset`. A reflexive ``index``
        must not destroy an extraction pass (the 24,000-sentence ``meaning``
        one) -- that is the one failure that costs days. An explicit
        ``--force`` rebuild is allowed; its rows are *remapped* onto the new
        graph by :meth:`remap_derived`, not wiped, so even a forced rebuild
        loses nothing that is stale, orphaned or unverified. Raises
        :class:`ResetRefusedError` when the guard fires.
        """
        present = []
        for table in ("events", "meaning"):
            exists = self.connection.execute(
                "SELECT name FROM sqlite_master"
                " WHERE type = 'table' AND name = ?", (table,)
            ).fetchone()
            if exists is None:
                continue
            count = self.connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            if count:
                present.append(f"`{table}` ({count:,} rows)")
        if present and not force:
            raise ResetRefusedError(
                "refusing to rebuild: the derived model layers are non-empty"
                f" -- {', '.join(present)}. A rebuild renumbers the section/"
                "node ids their rows are keyed on. Pass --force to rebuild;"
                " the rows are remapped onto the new graph, not wiped."
            )

    def remap_derived(
        self, snapshot: dict[str, list[dict[str, Any]]] | None = None
    ) -> dict[str, dict[str, int]]:
        """Re-key a :meth:`reset` snapshot onto the freshly built tables.

        Call this after the base tables (``documents`` / ``sections`` /
        ``nodes``) have been repopulated by an ``index`` rebuild. For each
        derived row its durable key is resolved to this build's new ids:

        * ``events``: (doc_title, section_ordinal) -> the new ``section_id``;
          ``subject_name`` / ``object_name`` -> the new ``subject_node`` /
          ``object_node`` (via ``nodes.name``);
        * ``meaning``: (doc_title, section_ordinal) -> the new ``section_id``,
          and the ``sentence_ordinal`` follows the sentence itself, re-keyed
          to where its ``content_hash`` now sits in the re-split section --
          order-preservingly, the k-th stored copy of a sentence taking the
          k-th occurrence, so identical sentences never collapse into one row.

        A row is dropped, and counted, in three cases:

        * *stale* -- its document's ``revid`` changed between the extract and
          this build, so the text it was read from no longer matches;
        * *orphaned* -- its section or a participant node no longer exists in
          this build;
        * *unverified* -- its section resolved but no longer proves the row:
          an ordinal shift can re-key a row onto a different section with no
          ``revid`` change at all (ordinals are assigned by enumeration after
          the section filter, so a parser fix that adds or removes a section
          shifts every later ordinal). The row is therefore re-checked
          against the target section's own text with the same predicate the
          extraction passes used to store it -- the quote for ``events``, the
          sentence's ``content_hash`` for ``meaning`` -- and drops rather
          than silently inheriting an attribution to text that does not say
          it. A section that never changed passes both checks untouched. The
           re-keyed rows are committed in a single transaction, all or
           nothing: a crash mid-remap recovers the whole snapshot from the
           file, never half of it.

        When ``snapshot`` is not given (the crash-recovery path: a build that
        died after :meth:`reset` and before the remap left the derived
        layers empty, so the guard let this re-run through), the snapshot is
        read from the crash-recovery file :meth:`reset` wrote, and the file
        is deleted once the rows are back in the new build. Returns a
        per-table report::

            {"events":  {"before": n, "remapped": x, "stale": y,
                         "orphaned": z, "unverified": w},
             "meaning": {"before": n, "remapped": x, "stale": y,
                         "orphaned": z, "unverified": w}}
        """
        report: dict[str, dict[str, int]] = {}
        if not snapshot:
            snapshot = self._read_snapshot_file()
        if not snapshot:
            return report

        # (doc_title, section_ordinal) -> (new section_id, the doc's new revid).
        section_key = {
            (row[0], row[1]): (row[2], row[3])
            for row in self.connection.execute(
                "SELECT d.title, s.ordinal, s.id, d.revid"
                " FROM sections s JOIN documents d ON s.document_id = d.id"
            )
        }
        # The target sections' own text, for the unverified check: a row is
        # re-anchored only while the section still says what the row says.
        section_text = {
            row[0]: row[1] or ""
            for row in self.connection.execute("SELECT id, text FROM sections")
        }
        # node name (case-insensitive) -> new node id.
        node_key = {
            row[0].lower(): row[1]
            for row in self.connection.execute("SELECT name, id FROM nodes")
        }
        # Per-section sentence identity, computed once per section and cached:
        # the re-split set of sentence hashes a stored meaning row must sit in.
        section_sentences: dict[int, list[str]] = {}
        section_hashes: dict[int, list[str]] = {}

        def sentences_of(section_id: int) -> list[str]:
            if section_id not in section_sentences:
                section_sentences[section_id] = split_sentences(
                    section_text.get(section_id, "")
                )
            return section_sentences[section_id]

        def hashes_of(section_id: int) -> list[str]:
            if section_id not in section_hashes:
                section_hashes[section_id] = [
                    sentence_content_hash(s) for s in sentences_of(section_id)
                ]
            return section_hashes[section_id]

        # ── events ─────────────────────────────────────────────────────────
        events = snapshot.get("events")
        if events:
            stats = {"before": len(events), "remapped": 0, "stale": 0,
                     "orphaned": 0, "unverified": 0}
            rows = []
            for row in events:
                new_section, doc_revid = section_key.get(
                    (row["doc_title"], row["section_ordinal"]), (None, None)
                )
                if new_section is None:
                    stats["orphaned"] += 1
                    continue
                if row["revid"] is not None and doc_revid is not None \
                        and row["revid"] != doc_revid:
                    stats["stale"] += 1
                    continue
                new_subject = node_key.get((row["subject_name"] or "").lower())
                new_object = node_key.get((row["object_name"] or "").lower())
                if new_subject is None or new_object is None:
                    stats["orphaned"] += 1
                    continue
                if not quoted_in(
                    row["quote"] or "", section_text.get(new_section, "")
                ):
                    stats["unverified"] += 1
                    continue
                rows.append((
                    new_subject, row["subject_name"],
                    new_object, row["object_name"],
                    row["verb"], row["arc_key"],
                    new_section, row["quote"], row["temporal"], row["time_rank"],
                    row["arc_index"], row["doc_title"], row["section_ordinal"],
                    row["revid"], row["prompt_version"], row["model"],
                    row["extracted_at"],
                ))
            self.connection.executemany(
                "INSERT OR REPLACE INTO events"
                " (subject_node, subject_name, object_node, object_name, verb,"
                "  arc_key, section_id, quote, temporal, time_rank,"
                "  arc_index, doc_title, section_ordinal,"
                "  revid, prompt_version, model, extracted_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
            stats["remapped"] = len(rows)
            report["events"] = stats

        # ── meaning ────────────────────────────────────────────────────────
        meanings = snapshot.get("meaning")
        if meanings:
            stats = {"before": len(meanings), "remapped": 0, "stale": 0,
                     "orphaned": 0, "unverified": 0}
            # First pass: resolve each row's destination section and drop the
            # stale, orphaned and unverified ones, exactly as the events pass.
            survivors: list[tuple[dict[str, Any], int]] = []
            for row in meanings:
                new_section, doc_revid = section_key.get(
                    (row["doc_title"], row["section_ordinal"]), (None, None)
                )
                if new_section is None:
                    stats["orphaned"] += 1
                    continue
                if row["revid"] is not None and doc_revid is not None \
                        and row["revid"] != doc_revid:
                    stats["stale"] += 1
                    continue
                if not (row["content_hash"]
                        and row["content_hash"] in hashes_of(new_section)):
                    stats["unverified"] += 1
                    continue
                survivors.append((row, new_section))
            # Second pass, per section in old-ordinal order: the k-th
            # surviving row with a given content_hash takes the k-th
            # occurrence of that hash in the re-split sentence list. On a
            # section that did not change, that is exactly the row's old
            # ordinal; and two identical sentences keep two rows instead of
            # both landing on the first occurrence, where the (section,
            # ordinal) primary key would collapse them into one silently.
            groups: dict[int, list[tuple[dict[str, Any], int]]] = {}
            for row, new_section in survivors:
                groups.setdefault(new_section, []).append((row, new_section))
            rows = []
            for new_section, group in groups.items():
                group.sort(key=lambda pair: pair[0]["sentence_ordinal"])
                occurrences: dict[str, list[int]] = {}
                for position, h in enumerate(hashes_of(new_section)):
                    occurrences.setdefault(h, []).append(position)
                taken: dict[str, int] = {}
                for row, _ in group:
                    h = row["content_hash"]
                    k = taken.get(h, 0)
                    positions = occurrences.get(h, [])
                    if k >= len(positions):
                        # The re-split section holds fewer copies of this
                        # sentence than the stored rows: the extras lost their
                        # proof and drop, counted.
                        stats["unverified"] += 1
                        continue
                    rows.append((
                        new_section, positions[k], h,
                        row["class"], row["is_event"], row["participants"],
                        row["arc_index"], row["chapter"],
                        row["doc_title"], row["section_ordinal"],
                        row["revid"], row["prompt_version"], row["model"],
                        row["extracted_at"],
                    ))
                    taken[h] = k + 1
            self.connection.executemany(
                "INSERT OR REPLACE INTO meaning"
                " (section_id, sentence_ordinal, content_hash, class, is_event,"
                "  participants, arc_index, chapter,"
                "  doc_title, section_ordinal,"
                "  revid, prompt_version, model, extracted_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
            stats["remapped"] = len(rows)
            report["meaning"] = stats

        # One commit for the whole remap, all or nothing. If the events were
        # committed on their own, a crash in between would leave the meaning
        # rows only in the crash file; the re-run's non-empty snapshot would
        # then clobber that file and the loss would be silent. With a single
        # commit, a crash before it recovers from the file, and a crash after
        # it re-snapshots the fully remapped store (idempotent, same rows).
        if events or meanings:
            self.connection.commit()
        unverified = sum(r["unverified"] for r in report.values())
        if unverified:
            logger.warning(
                "remap dropped %d row(s) as unverified -- their section no "
                "longer proves them: %s",
                unverified,
                " ".join(
                    f"{name} {r['unverified']}"
                    for name, r in report.items()
                    if r["unverified"]
                ),
            )
        # The rows are back in the new build; the crash-recovery copy has done
        # its job and stays behind only if it was the last word on them.
        self._drop_snapshot_file()
        return report

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
        # `lastrowid` is Optional in the sqlite3 stubs; after an INSERT that
        # just succeeded it is always set.
        return int(cursor.lastrowid or 0)

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
        # `lastrowid` is Optional in the sqlite3 stubs; after an INSERT that
        # just succeeded it is always set.
        return int(cursor.lastrowid or 0)

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

    def subject_node_name(self, subject: str) -> str | None:
        """The node a subject names, by its own name or an editor-maintained alias.

        The facts-side twin of `passages_for_subject`, which resolves the same
        way for documents: a node's canonical name so `facts_for` can be called
        on it, since that lookup is a plain `nodes.name` match with no alias
        path. A subject that is neither a node name nor an alias (a misspelling,
        an un-crawled page) returns None and the caller's ranked behaviour stands
        unchanged. Several nodes sharing an alias: the shortest resolved name
        wins, the way `passages_for_subject` orders its hits.
        """
        if not subject or not subject.strip():
            return None
        name = subject.strip()
        row = self.connection.execute(
            "SELECT name FROM nodes WHERE name = ? COLLATE NOCASE", (name,)
        ).fetchone()
        if row is not None:
            return row["name"]
        row = self.connection.execute(
            "SELECT n.name FROM aliases a"
            " JOIN nodes n ON n.id = a.node_id"
            " WHERE a.alias = ?"
            " ORDER BY n.is_resolved DESC, LENGTH(n.name) ASC LIMIT 1",
            (name.lower(),),
        ).fetchone()
        return row["name"] if row is not None else None

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

        # A qualified title named outright ("Noritoshi Kamo (Ancestor)") links
        # exactly through its parenthetical, so the qualified entity's `exact`
        # flag can win over the unqualified base name (see `_QUALIFIED`).
        for base, qual in _QUALIFIED.findall(text):
            candidates.add(f"{base} ({qual})".lower())

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

    def ensure_emphasis(self) -> None:
        """Names each page puts in bold: what it names, not what it mentions.

        Rebuilt by `index` like `documents` and `chunks`, because it is derived
        from the stored wikitext and costs nothing to recompute -- unlike
        `semantics`, `abilities` and `relations`, which hold local inference and
        deliberately survive `reset()`.
        """
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS emphasis ("
            " document_id INTEGER NOT NULL, name TEXT NOT NULL,"
            " PRIMARY KEY (document_id, name))"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_emphasis_name"
            " ON emphasis(name COLLATE NOCASE)"
        )

    def add_emphasis(self, document_id: int, names: Iterable[str]) -> None:
        self.connection.executemany(
            "INSERT OR IGNORE INTO emphasis (document_id, name) VALUES (?, ?)",
            [(document_id, name.strip()) for name in names if name.strip()],
        )

    def emphasised_on(self, title: str) -> set[str]:
        """The folded names this page bolds, or an empty set.

        Empty when the page has none *and* when the table has not been built
        yet, and the caller must treat those the same: a filter that fired on
        an unbuilt table would empty every roster on a store indexed before
        this existed.
        """
        try:
            rows = self.connection.execute(
                "SELECT e.name FROM emphasis e JOIN documents d"
                " ON e.document_id = d.id WHERE d.title = ? COLLATE NOCASE",
                (title,),
            ).fetchall()
        except sqlite3.OperationalError:
            return set()
        return {(row["name"] or "").strip().lower() for row in rows if row["name"]}

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

    def add_abilities(
        self,
        rows: Sequence[tuple[str, dict[str, str]]],
        prompt_version: str,
        model: str,
    ) -> int:
        """Add rows without removing what is already stored.

        `save_abilities` replaces a character's whole set, which is right when
        one pass owns the answer for that character. The narrative pass does not
        own it: it reads chapter and episode pages, attributes what it finds to
        whoever the prose names, and contributes to characters another pass has
        already written. Replacing there would delete the section-derived rows.

        `INSERT OR IGNORE` rather than `OR REPLACE`, so a name already read off
        the character's own page keeps that provenance in `section`. A chapter
        summary is the weaker source of the two, and it should not overwrite the
        stronger one.
        """
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        before = self.connection.execute(
            "SELECT COUNT(*) FROM abilities").fetchone()[0]
        self.connection.executemany(
            "INSERT OR IGNORE INTO abilities"
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
                    None,
                    prompt_version,
                    str(row.get("reason") or "").strip()[:300],
                    model,
                    stamp,
                )
                for character, row in rows
                if str(row.get("name") or "").strip() and character.strip()
            ],
        )
        self.connection.commit()
        after = self.connection.execute(
            "SELECT COUNT(*) FROM abilities").fetchone()[0]
        return after - before

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

    def ensure_events(self) -> int:
        """Create the extracted-events table, or rebuild it with its FKs.

        The rows reference `nodes` and `sections`, whose ids renumber on every
        rebuild. Each row therefore also carries its durable key -- (doc_title,
        section_ordinal) plus the participant names and `time_rank` -- and an
        `index` rebuild remaps the rows onto the new ids through it
        (`remap_derived`), so nothing is wiped. A row is only ever dropped when
        the remap finds it stale (its document's `revid` changed), orphaned
        (its section or a participant no longer exists) or unverified (its
        section moved under a parser fix and no longer says what the row
        says). `revid` is the
        staleness signal the remap trusts: a row whose source document was
        re-crawled since extraction is dropped for re-extraction, not remapped
        onto text it no longer matches. That is the id-stability fix the 3b
        council queued, made durable: before the FKs a renumbering re-crawl left
        the numeric refs pointing at ids that no longer existed and every reader
        had to guard individually; before the durable key the guard was a wipe,
        so a reflexive `cli index` destroyed the extracted pass. Now the guard
        (`require_rebuild`) refuses a non-forced rebuild while the layer is
        non-empty, and a forced rebuild remaps instead of wiping.

        Stores that predate the FKs (or the durable-key columns) are migrated
        here: missing columns are added and backfilled from `sections` and
        `documents`, and the table is rebuilt with its references keeping only
        rows whose refs still resolve (a dangling row is a miss every reader
        already guards for, so dropping it loses nothing the guards allowed).

        Returns the number of rows the migration dropped; 0 on a clean
        store or a fresh table.

        Keyed on (subject, verb, object, section, time_rank): the same pair
        meets twice on one page (Sukuna fights Jogo in the station and again
        outside it) and each meeting is a separate event at a separate place
        on the arc's time axis. `time_rank` is the event's position on that
        axis -- lower is earlier, fractions allowed within a section;
        `temporal=0` marks a standing state (or an off-axis event, like a
        death that predates the arc) the axis cannot place.
        """
        legacy = (
            self.connection.execute(
                "SELECT name FROM sqlite_master"
                " WHERE type = 'table' AND name = 'events'"
            ).fetchone()
            is not None
        )
        if legacy:
            columns = {
                row[1] for row in self.connection.execute(
                    "PRAGMA table_info(events)")
            }
            # The `arc_index` check runs first so the migration's SELECT sees
            # every column the new table carries.
            if "arc_index" not in columns:
                self.connection.execute(
                    "ALTER TABLE events ADD COLUMN arc_index INTEGER"
                )
            # The durable-key columns (0C) were added after the table existed,
            # so a store built before them needs the columns plus a one-time
            # backfill, not a migration script.
            added_durable = False
            if "doc_title" not in columns:
                self.connection.execute(
                    "ALTER TABLE events ADD COLUMN doc_title"
                    " TEXT NOT NULL DEFAULT ''"
                )
                added_durable = True
            if "section_ordinal" not in columns:
                self.connection.execute(
                    "ALTER TABLE events ADD COLUMN section_ordinal"
                    " INTEGER NOT NULL DEFAULT 0"
                )
                added_durable = True
            if added_durable:
                # Backfill the rows written before the columns existed. A row
                # whose section no longer resolves keeps the column defaults
                # (the COALESCE is what makes the NOT NULLs hold for it: the
                # scalar subquery yields no row, and a bare NULL assignment
                # would raise IntegrityError, blocking the rebuild) and is
                # dropped as orphaned by the next remap -- the same fate its
                # dangling FK already gave it.
                self.connection.execute(
                    "UPDATE events SET doc_title = COALESCE(("
                    "   SELECT d.title FROM sections s"
                    "   JOIN documents d ON s.document_id = d.id"
                    "   WHERE s.id = events.section_id), '')"
                    ", section_ordinal = COALESCE(("
                    "   SELECT s.ordinal FROM sections s"
                    "   WHERE s.id = events.section_id), 0)"
                    " WHERE doc_title = ''"
                )
            if not self.connection.execute(
                "PRAGMA foreign_key_list(events)"
            ).fetchall():
                return self._migrate_events_to_fk()
        else:
            self.connection.execute(
                "CREATE TABLE IF NOT EXISTS events ("
                " subject_node INTEGER REFERENCES nodes(id) ON DELETE CASCADE,"
                " subject_name TEXT,"
                " object_node INTEGER REFERENCES nodes(id) ON DELETE CASCADE,"
                " object_name TEXT, verb TEXT, arc_key TEXT,"
                " section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,"
                " quote TEXT, temporal INTEGER, time_rank REAL,"
                " arc_index INTEGER,"
                " doc_title TEXT NOT NULL DEFAULT '',"
                " section_ordinal INTEGER NOT NULL DEFAULT 0,"
                " revid INTEGER, prompt_version TEXT,"
                " model TEXT, extracted_at TEXT,"
                " PRIMARY KEY (subject_node, verb, object_node, section_id,"
                " time_rank))"
            )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS events_by_arc"
            " ON events (arc_key COLLATE NOCASE)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS events_by_subject"
            " ON events (subject_node)"
        )
        self.connection.commit()
        return 0

    def _migrate_events_to_fk(self) -> int:
        """Rebuild `events` with its FKs, keeping only resolvable rows."""
        self.connection.execute(
            "CREATE TABLE events_fk_migrated ("
            " subject_node INTEGER REFERENCES nodes(id) ON DELETE CASCADE,"
            " subject_name TEXT,"
            " object_node INTEGER REFERENCES nodes(id) ON DELETE CASCADE,"
            " object_name TEXT, verb TEXT, arc_key TEXT,"
            " section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,"
            " quote TEXT, temporal INTEGER, time_rank REAL,"
            " arc_index INTEGER,"
            " doc_title TEXT NOT NULL DEFAULT '',"
            " section_ordinal INTEGER NOT NULL DEFAULT 0,"
            " revid INTEGER, prompt_version TEXT,"
            " model TEXT, extracted_at TEXT,"
            " PRIMARY KEY (subject_node, verb, object_node, section_id,"
            " time_rank))"
        )
        self.connection.execute(
            "INSERT INTO events_fk_migrated"
            " (subject_node, subject_name, object_node, object_name, verb,"
            "  arc_key, section_id, quote, temporal, time_rank, arc_index,"
            "  doc_title, section_ordinal,"
            "  revid, prompt_version, model, extracted_at)"
            " SELECT subject_node, subject_name, object_node, object_name,"
            "  verb, arc_key, section_id, quote, temporal, time_rank,"
            "  arc_index,"
            "  COALESCE(("
            "   SELECT d.title FROM sections s"
            "   JOIN documents d ON s.document_id = d.id"
            "   WHERE s.id = events.section_id), ''),"
            "  COALESCE(("
            "   SELECT s.ordinal FROM sections s"
            "   WHERE s.id = events.section_id), 0),"
            "  revid, prompt_version, model, extracted_at"
            " FROM events"
            " WHERE (subject_node IS NULL"
            "        OR subject_node IN (SELECT id FROM nodes))"
            "   AND (object_node IS NULL"
            "        OR object_node IN (SELECT id FROM nodes))"
            "   AND (section_id IS NULL"
            "        OR section_id IN (SELECT id FROM sections))"
        )
        before = self.connection.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        kept = self.connection.execute(
            "SELECT COUNT(*) FROM events_fk_migrated").fetchone()[0]
        dropped = before - kept
        self.connection.execute("DROP TABLE events")
        self.connection.execute(
            "ALTER TABLE events_fk_migrated RENAME TO events")
        if dropped:
            logger.warning(
                "events FK migration dropped %d/%d row(s) whose node or "
                "section refs no longer resolve; re-run events-extract to "
                "repopulate", dropped, before,
            )
        return dropped

    def ensure_meaning(self) -> int:
        """Create the per-line meaning index (R1) if this store predates it.

        Keyed on `sections` ids, which renumber on every rebuild, so the row
        also carries its durable key -- (doc_title, section_ordinal) +
        sentence_ordinal + content_hash -- and an `index` rebuild remaps it
        onto the new section id through that key (`remap_derived`), so nothing
        is wiped: a row is only dropped when the remap finds it stale,
        orphaned or unverified (its section's content moved and no longer
        proves it). The two
        locators that make a line addressable, `arc_index` (story axis; NULL = a
        line the extractor could not place there -- unverified, not asserted
        atemporal) and `chapter` (the owning page's own `chapters` fact,
        verbatim; NULL = the wiki gives none), are backfilled in SQL. `class`
        is drawn from `MEANING_CLASSES`, `participants` is the model's, and
        `is_event` is derived (class = 'event' AND arc_index IS NOT NULL), not
        an independent model channel -- the DDL CHECK keeps it that way.

        Returns the number of rows a contract migration dropped; 0 on a clean
        store or a fresh table.
        """
        legacy = (
            self.connection.execute(
                "SELECT sql FROM sqlite_master"
                " WHERE type = 'table' AND name = 'meaning'"
            ).fetchone()
            is not None
        )
        if legacy:
            return self._migrate_meaning_to_contract()
        self.connection.execute(_MEANING_TABLE_DDL)
        self._create_meaning_indexes()
        self.connection.commit()
        return 0

    def _create_meaning_indexes(self) -> None:
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS meaning_by_class"
            " ON meaning (class)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS meaning_by_arc"
            " ON meaning (arc_index)"
        )

    def _migrate_meaning_to_contract(self) -> int:
        """Rebuild a pre-contract `meaning` table with the durable key + checks.

        SQLite cannot add a CHECK to an existing column, so a table built
        before the quality contract is rebuilt with the full DDL and its rows
        carried over. A row whose `class` falls outside `MEANING_CLASSES`, or
        whose `is_event` drifted from its inputs, is dropped and counted: it is
        a model output the contract rejects, and the pass refills it.
        """
        sql = self.connection.execute(
            "SELECT sql FROM sqlite_master"
            " WHERE type = 'table' AND name = 'meaning'"
        ).fetchone()[0]
        columns = {
            row[1] for row in self.connection.execute(
                "PRAGMA table_info(meaning)")
        }
        has_class_check = "CHECK (class IS NULL" in sql
        if "doc_title" in columns and "section_ordinal" in columns \
                and has_class_check:
            return 0
        has_durable = "doc_title" in columns and "section_ordinal" in columns
        durable_select = (
            "COALESCE(doc_title, ''), COALESCE(section_ordinal, 0)"
            if has_durable else "'', 0"
        )
        self.connection.execute("ALTER TABLE meaning RENAME TO meaning_old")
        self.connection.execute(_MEANING_TABLE_DDL.replace(
            "CREATE TABLE IF NOT EXISTS meaning", "CREATE TABLE meaning"))
        before = self.connection.execute(
            "SELECT COUNT(*) FROM meaning_old").fetchone()[0]
        self.connection.execute(
            "INSERT INTO meaning ("
            " section_id, sentence_ordinal, content_hash, class, is_event,"
            " participants, arc_index, chapter,"
            " doc_title, section_ordinal,"
            " revid, prompt_version, model, extracted_at)"
            " SELECT section_id, sentence_ordinal, content_hash, class,"
            "   is_event, participants, arc_index, chapter,"
            f"   {durable_select},"
            "   revid, prompt_version, model, extracted_at"
            " FROM meaning_old"
            " WHERE class IS NULL OR class IN"
            "   ('event', 'standing state', 'trait', 'trivia')"
            " AND is_event = CASE WHEN class = 'event'"
            "   AND arc_index IS NOT NULL THEN 1 ELSE 0 END"
        )
        kept = self.connection.execute(
            "SELECT COUNT(*) FROM meaning").fetchone()[0]
        dropped = before - kept
        self.connection.execute("DROP TABLE meaning_old")
        self._create_meaning_indexes()
        if dropped:
            logger.warning(
                "meaning contract migration dropped %d/%d row(s) whose class "
                "or is_event violates the frozen contract; re-run the pass "
                "to repopulate", dropped, before,
            )
        return dropped

    def events_of(self, arc_key: str) -> list[sqlite3.Row]:
        """Placed events for one arc, in time-axis order. A keyed lookup."""
        try:
            return self.connection.execute(
                "SELECT subject_node, subject_name, object_node, object_name,"
                "        verb, section_id, quote, temporal, time_rank"
                " FROM events WHERE arc_key = ? COLLATE NOCASE"
                " ORDER BY time_rank",
                (arc_key,),
            ).fetchall()
        except sqlite3.OperationalError:
            # A store built before events existed. Nothing is extracted in it,
            # which is a complete answer.
            return []

    def event_state(self, arc_key: str) -> sqlite3.Row | None:
        """What prompt and revision this arc's events were read under."""
        try:
            return self.connection.execute(
                "SELECT revid, prompt_version, model FROM events"
                " WHERE arc_key = ? COLLATE NOCASE LIMIT 1",
                (arc_key,),
            ).fetchone()
        except sqlite3.OperationalError:
            return None

    def save_events(
        self,
        arc_key: str,
        found: Sequence[dict[str, Any]],
        revid: int | None,
        prompt_version: str,
        model: str,
    ) -> int:
        """Replace everything stored for one arc, in one transaction.

        Replaced rather than merged, exactly as `save_relations` is: a re-run
        under a new prompt is the whole answer for that arc.
        """
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        # The durable key is resolved once for the arc's sections, not per row:
        # `section_id` renumbers on a rebuild, but (doc_title, section_ordinal)
        # does not, so a remap can re-key this arc's rows onto a new build.
        section_ids = {
            int(row["section_id"]) for row in found if row.get("section_id")
        }
        durable: dict[int, tuple[str, int]] = {}
        if section_ids:
            placeholders = ",".join("?" for _ in section_ids)
            durable = {
                row[0]: (row[1], row[2])
                for row in self.connection.execute(
                    "SELECT s.id, d.title, s.ordinal"
                    " FROM sections s JOIN documents d ON s.document_id = d.id"
                    f" WHERE s.id IN ({placeholders})",
                    list(section_ids),
                )
            }

        def durable_of(section_id: Any) -> tuple[str, int]:
            return durable.get(int(section_id), ("", 0))

        self.connection.execute(
            "DELETE FROM events WHERE arc_key = ? COLLATE NOCASE", (arc_key,)
        )
        self.connection.executemany(
            "INSERT OR REPLACE INTO events"
            " (subject_node, subject_name, object_node, object_name, verb,"
            "  arc_key, section_id, quote, temporal, time_rank,"
            "  doc_title, section_ordinal, revid,"
            "  prompt_version, model, extracted_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    int(row["subject_node"]),
                    str(row["subject_name"]).strip(),
                    int(row["object_node"]),
                    str(row["object_name"]).strip(),
                    str(row["verb"]).strip().lower(),
                    arc_key,
                    int(row["section_id"]),
                    str(row.get("quote") or "").strip()[:400],
                    1 if row.get("temporal", True) else 0,
                    float(row["time_rank"]),
                    *durable_of(row["section_id"]),
                    revid,
                    prompt_version,
                    model,
                    stamp,
                )
                for row in found
                if row.get("subject_node") and row.get("object_node") and row.get("verb")
            ],
        )
        self.connection.commit()
        return self.connection.execute(
            "SELECT COUNT(*) FROM events WHERE arc_key = ? COLLATE NOCASE",
            (arc_key,),
        ).fetchone()[0]

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

    def passages_for_subject(self, subject: str) -> list[sqlite3.Row]:
        """Every level-0 (the document's lead card) and level-2 passage of the
        page `subject` names, in the wiki's own
        section order.

        The entity-anchored recall floor (R6): a question authored against a
        page must be able to read that page's text whether or not any single
        passage of it outranks the rest of the corpus. The ranked beam answers
        "what is most relevant to this phrasing"; this answers "what does the
        page say", and the two only coincide when the phrasing's keywords
        overlap the answer's words. The G5/G11/G13/G14 failures (Kechizu 036,
        Tsumiki's kanji meanings, Toge 051) all sat on the subject page and
        below the beam at once. A store lookup, not a similarity search: the
        beam still decides what *else* fills the budget, never whether the
        subject's own page shows up at all.

        The level-0 card is part of the floor by construction (G-CSM-2 /
        csm-fact-06, 2026-09-09): a subject whose key line lives only in the
        lead paragraph is reachable through the floor even when no section
        passage of the page ever enters the beam.

        A subject that resolves to no document (a bare alias, an un-crawled
        page, a misspelling) yields an empty list and the caller's ranked
        behaviour stands unchanged.

        Resolution, in order of confidence: the page's own title, case-
        insensitive, then an editor-maintained alias. Aliases are stored folded
        to lower case (see the `aliases` table), so the probe is a plain index
        hit. When several nodes share an alias the shortest resolved name wins:
        the character page is the hub, for the same reason `link_entities`
        orders its results.
        """
        if not subject or not subject.strip():
            return []
        name = subject.strip()
        row = self.connection.execute(
            "SELECT d.id FROM documents d WHERE d.title = ? COLLATE NOCASE",
            (name,),
        ).fetchone()
        if row is None:
            row = self.connection.execute(
                "SELECT n.document_id AS id FROM aliases a"
                " JOIN nodes n ON n.id = a.node_id"
                " WHERE a.alias = ? AND n.document_id IS NOT NULL"
                " ORDER BY n.is_resolved DESC, LENGTH(n.name) ASC LIMIT 1",
                (name.lower(),),
            ).fetchone()
        if row is None or row["id"] is None:
            return []
        # The parent join is what keeps the floor's passages the same shape as
        # the beam's: a quoted passage carries its section, not just itself.
        # Level 0 (the document card) and level 2: see the docstring above for
        # why the card is part of the floor.
        return self.connection.execute(
            "SELECT c.*, p.text AS parent_text"
            " FROM chunks c LEFT JOIN chunks p ON p.id = c.parent_id"
            " WHERE c.document_id = ? AND c.level IN (0, 2)"
            " ORDER BY c.ordinal",
            (row["id"],),
        ).fetchall()

    def synopsis_subpage_passages(self, subject: str) -> list[sqlite3.Row]:
        """The passages of a character's separate /Synopsis page (where this
        wiki files a character's story beats when the main page carries no
        History of its own), shaped exactly like `passages_for_subject`.

        The entity-anchored floor (R6) reads the page a question is authored
        against, and a story question ("what is the history of X?") authored on
        a character whose main page has no History section must still reach the
        /Synopsis subpage that carries it (the F2 gap: the qa door resolved to
        the main page and never bridged, so six characters' History sat on the
        subpage and out of the bundle at once). Resolution is structural, not
        by name: the subject's own character page plus its character_synopsis
        sibling, titled '<character>/Synopsis' -- the wiki's own filing
        convention. A subject that is not a character, or a character with no
        synopsis page, yields [] and the caller's floor stands unchanged.
        """
        if not subject or not subject.strip():
            return []
        name = subject.strip()
        row = self.connection.execute(
            "SELECT d.id FROM documents d WHERE d.title = ? COLLATE NOCASE",
            (name,),
        ).fetchone()
        if row is None:
            row = self.connection.execute(
                "SELECT n.document_id AS id FROM aliases a"
                " JOIN nodes n ON n.id = a.node_id"
                " WHERE a.alias = ? AND n.document_id IS NOT NULL"
                " ORDER BY n.is_resolved DESC, LENGTH(n.name) ASC LIMIT 1",
                (name.lower(),),
            ).fetchone()
        if row is None or row["id"] is None:
            return []
        # The main page must be a character the wiki filed a separate synopsis
        # under; a battle or technique subject has no /Synopsis twin.
        node = self.connection.execute(
            "SELECT n.label AS label, d.title AS title FROM nodes n"
            " JOIN documents d ON d.id = n.document_id"
            " WHERE n.document_id = ? AND n.is_resolved = 1 LIMIT 1",
            (row["id"],),
        ).fetchone()
        if node is None or node["label"] != "character" or not node["title"]:
            return []
        sub = self.connection.execute(
            "SELECT d.id FROM documents d JOIN nodes n ON n.document_id = d.id"
            " WHERE d.title = ? || '/Synopsis' COLLATE NOCASE"
            " AND n.label = 'character_synopsis' LIMIT 1",
            (node["title"],),
        ).fetchone()
        if sub is None:
            return []
        return self.connection.execute(
            "SELECT c.*, p.text AS parent_text"
            " FROM chunks c LEFT JOIN chunks p ON p.id = c.parent_id"
            " WHERE c.document_id = ? AND c.level = 2"
            " ORDER BY c.ordinal",
            (sub["id"],),
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
        counts: dict[str, Any] = self.counts()
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

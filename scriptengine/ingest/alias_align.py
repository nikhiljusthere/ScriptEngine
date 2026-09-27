"""The names a wiki's disambiguation pages file, aligned to canonical nodes. (plan §C3, A1b)

A disambiguation page (`page_type: disambiguation`) is the wiki's own
statement of what a bare term ("Spider-Man") refers to: its list fields
(`others`, `related`, `teams`, `media`, `main_articleN`) file the entries,
and each entry is the wiki's pointer to the canonical entity. This pass
parses the entries -- first line of each `;`-part, with the image suffix
`<name> from <file>.jpg` stripped, bare image filenames skipped, and a
part's several entities (unpacked from `X and Y` / `X, Y` joins) filed
individually -- and resolves each against the store's nodes then its
aliases (exact = 1.0, alias = 0.9). A resolved entry name is promoted into
the `aliases` table, so the term's referents are graph-traversable; an
unresolved name is counted, written to a `disambig_unresolved` fact under
`disambig:<page>` provenance and flagged -- never invented.

The list-field key names are a wiki convention, so they live in the
series' `disambig_list_keys:` override (Marvel files its entries under
`others`/`related`/`teams`/`media`; the MCU wiki has no disambiguation
pages, so it declares none). Deterministic, no model. The
cross-corpus half of plan §C3 (marvel <-> mcu <-> cc.db alias tables,
checked against the MCU-wiki `Appearances` lists) is a follow-up that
needs its own `subject_aliases:` override and is recorded as such.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from scriptengine.config import SeriesPaths, load_overrides
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

# Exact node names outrank aliases, and the two confidences are the only two
# the mechanism knows: the store said the name, or the store said the name's
# alias. Anything weaker (fuzzy, cross-wiki) is a different, unshipped rule.
_EXACT = 1.0
_ALIAS = 0.9

# `Abominations (Earth-122) from Hulk Vol 5 5 001.jpg` -> the name part. The
# image reference is everything after the last ` from `: wiki filenames carry
# spaces (`Hulk Vol 5 5 001.jpg`), so a bare-token match would miss them.
_IMG_SUFFIX = re.compile(r"^(?P<name>.*\S)\s+from\s+\S.*\.(?:jpe?g|png)\s*$", re.IGNORECASE)
# A bare image filename (`Spider-Man Vol 4 1 Unknown.jpg`): no name to file.
_IMG_ONLY = re.compile(r"\.(?:jpe?g|png|jp)$", re.IGNORECASE)


def _list_keys(overrides: dict) -> tuple[str, ...]:
    raw = overrides.get("disambig_list_keys") or []
    if not isinstance(raw, list):
        raise ValueError(f"`disambig_list_keys` must be a list, got {type(raw).__name__}")
    return tuple(str(key) for key in raw)


def _parse_entries(part: str) -> list[str]:
    """The entry names in one `;`-separated part.

    Each part is a line of the wiki's own list: the name, then an optional
    image reference. The name is the first non-image line; a `<name> from
    <image>` line contributes the name; a bare image filename contributes
    nothing (the wiki editor pasted a file where a name would have been).
    One part may file several entities, joined with ` and ` or `, ` -- the
    split is deterministic: a Marvel-DB entity name never carries either.
    """
    names: list[str] = []
    for line in (ln.strip() for ln in part.strip().splitlines()):
        if not line:
            continue
        match = _IMG_SUFFIX.match(line)
        if match:
            line = match.group("name").strip()
        elif _IMG_ONLY.search(line):
            continue
        for name in re.split(r"\s+and\s+|,", line):
            name = name.strip()
            if name:
                names.append(name)
        break
    return names


def _resolve_map(store: FactStore) -> dict[str, tuple[int, float]]:
    """Name (casefolded) -> (node_id, confidence), aliases first, names on top."""
    resolve: dict[str, tuple[int, float]] = {}
    for alias, node_id in store.connection.execute("SELECT alias, node_id FROM aliases"):
        resolve[alias.casefold()] = (node_id, _ALIAS)
    for name, node_id in store.connection.execute(
        "SELECT name, id FROM nodes WHERE name IS NOT NULL"
    ):
        resolve[name.casefold()] = (node_id, _EXACT)
    return resolve


def align(paths: SeriesPaths, limit: int = 0) -> dict[str, Any]:
    """Promote the resolvable disambiguation entries into the `aliases` table."""
    overrides = load_overrides(paths)
    keys = _list_keys(overrides)
    report: dict[str, Any] = {
        "list_keys": list(keys),
        "pages": 0,
        "entries": 0,
        "image_only": 0,
        "resolved_exact": 0,
        "resolved_alias": 0,
        "already": 0,
        "unresolved": 0,
        "unresolved_names": [],
    }
    if not keys:
        return report

    with FactStore(paths.facts_db) as store:
        resolve = _resolve_map(store)
        node_by_doc = {
            row[0]: row[1]
            for row in store.connection.execute(
                "SELECT document_id, id FROM nodes WHERE document_id IS NOT NULL"
            )
        }
        query = "SELECT id, title FROM documents WHERE page_type = 'disambiguation' ORDER BY id"
        if limit:
            query += f" LIMIT {int(limit)}"
        for document_id, title in store.connection.execute(query):
            report["pages"] += 1
            node_id = node_by_doc.get(document_id)
            if node_id is None:
                continue
            for key in keys:
                for (value,) in store.connection.execute(
                    "SELECT value FROM facts WHERE node_id = ? AND key = ?", (node_id, key)
                ):
                    for part in str(value).split(";"):
                        names = _parse_entries(part)
                        if not names:
                            if part.strip():
                                report["image_only"] += 1
                            continue
                        for name in names:
                            report["entries"] += 1
                            hit = resolve.get(name.casefold())
                            if hit is None:
                                report["unresolved"] += 1
                                if len(report["unresolved_names"]) < 200:
                                    report["unresolved_names"].append(name)
                                # The flag, durable and queryable: which terms the
                                # wiki files as entries but the store has no node
                                # for -- the raw material for the cross-corpus pass.
                                exists = store.connection.execute(
                                    "SELECT 1 FROM facts WHERE node_id = ? AND key = 'disambig_unresolved'"
                                    " AND value = ? AND citation = ?",
                                    (node_id, name, f"disambig:{title}"),
                                ).fetchone()
                                if not exists:
                                    store.connection.execute(
                                        "INSERT INTO facts (node_id, key, value, citation)"
                                        " VALUES (?, 'disambig_unresolved', ?, ?)",
                                        (node_id, name, f"disambig:{title}"),
                                    )
                                continue
                            target, confidence = hit
                            cursor = store.connection.execute(
                                "INSERT OR IGNORE INTO aliases (alias, node_id) VALUES (?, ?)",
                                (name, target),
                            )
                            if cursor.rowcount:
                                report["resolved_exact" if confidence == _EXACT else "resolved_alias"] += 1
                            else:
                                report["already"] += 1
        store.connection.commit()
        if report["pages"]:
            logger.info(
                "alias-align %s: %d pages, %d entries, %d written (%d exact / %d alias), "
                "%d already, %d unresolved",
                paths.name,
                report["pages"],
                report["entries"],
                report["resolved_exact"] + report["resolved_alias"],
                report["resolved_exact"],
                report["resolved_alias"],
                report["already"],
                report["unresolved"],
            )
    return report
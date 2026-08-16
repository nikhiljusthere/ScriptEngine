"""Graph-driven ability lookup for a character.

The knowledge graph already knows who uses what: every ability page carries a
`user` edge (confidence 0.95, from the infobox) to every character that uses
it, a `debut` edge to the chapter it first appeared in, and an `anime debut`
edge to the episode. This module walks that graph *backwards* from a character
instead of asking the retriever to rank prose, so "list Yuji's abilities"
returns the whole set even when the character's own page was never crawled
(which is exactly why the retriever missed Black Flash for Yuji Itadori).

For each ability found:

- `debut` / `anime debut`: where the ability first appeared anywhere.
- the `Usage / <character>` section of the ability's page, where *this*
  character uses it, with the `{{Ref|chap=N}}` citations collected from that
  section as the chapter list. That is "shown, not just talked about".
"""

from __future__ import annotations

import json
import re
from typing import Any

from scriptengine.config import SeriesPaths
from scriptengine.ingest.crawler import sanitise_filename
from scriptengine.stores.facts import FactStore

MAX_ABILITIES = 15
USAGE_CHARS = 900
MAX_CHARACTER_SECTIONS = 5

_CHAPTER_RE = re.compile(r"Chapter\s+(\d+)", re.IGNORECASE)


def _chapter_number(text: str) -> int | None:
    match = _CHAPTER_RE.search(text or "")
    return int(match.group(1)) if match else None


def _load_page(paths: SeriesPaths, title: str) -> dict[str, Any] | None:
    """The stored crawl JSON for a page (sections carry Ref citations)."""
    path = paths.wikitext / f"{sanitise_filename(title)}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _usage_chapters(page: dict[str, Any], character: str) -> list[int]:
    """Chapter refs from the `Usage / <character>` section of an ability page."""
    chapters: set[int] = set()
    for section in page.get("sections", []):
        if section.get("path") != ["Usage"]:
            continue
        if (section.get("title") or "").strip() != character:
            continue
        for citation in section.get("citations", []):
            chap = (citation.get("params") or {}).get("chap")
            if chap and chap.isdigit():
                chapters.add(int(chap))
    return sorted(chapters)


def collect_abilities(
    paths: SeriesPaths,
    entity: str,
    *,
    max_abilities: int = MAX_ABILITIES,
    usage_chars: int = USAGE_CHARS,
    max_character_sections: int = MAX_CHARACTER_SECTIONS,
) -> dict[str, Any] | None:
    """Every ability a character uses, with debut and per-character usage.

    Returns ``None`` when the entity cannot be resolved at all.
    """
    with FactStore(paths.facts_db) as store:
        node = store.node_by_name(entity)
        if node is None:
            matches = store.link_entities(entity)
            if not matches:
                return None
            node = matches[0]
        character_id = int(node["id"])
        character = node["name"]

        rows = store.connection.execute(
            "SELECT s.id, s.name, s.label"
            " FROM edges e"
            " JOIN nodes s ON s.id = e.source_id"
            " WHERE e.relation = 'user' AND e.target_id = ? AND e.confidence >= 0.9"
            " ORDER BY s.name",
            (character_id,),
        ).fetchall()

        abilities: list[dict[str, Any]] = []
        for row in rows:
            ability_id = int(row["id"])
            ability = row["name"]

            meta: dict[str, str] = {}
            for edge in store.edges_for([ability_id], min_confidence=0.9, limit=40):
                if edge["relation"] in ("debut", "anime debut", "type"):
                    meta.setdefault(edge["relation"], edge["target"])

            usage_text = ""
            for section in store.document_sections(ability):
                if section["breadcrumb"] == f"Usage / {character}":
                    usage_text = section["text"] or ""
                    break

            page = _load_page(paths, ability)
            chapters = _usage_chapters(page, character) if page is not None else []

            abilities.append(
                {
                    "name": ability,
                    "label": row["label"],
                    "type": meta.get("type", ""),
                    "debut": meta.get("debut", ""),
                    "anime_debut": meta.get("anime debut", ""),
                    "usage": usage_text[:usage_chars],
                    "usage_chapters": chapters,
                }
            )

        # First appearance first; abilities without a debut chapter last.
        abilities.sort(
            key=lambda a: (
                _chapter_number(a["debut"]) is None,
                _chapter_number(a["debut"]) or 0,
            )
        )
        abilities = abilities[:max_abilities]

        character_sections: list[dict[str, str]] = []
        for section in store.document_sections(character):
            if (section["breadcrumb"] or "").startswith("Abilities and Powers"):
                character_sections.append(
                    {
                        "breadcrumb": section["breadcrumb"],
                        "text": (section["text"] or "")[:usage_chars],
                    }
                )
                if len(character_sections) >= max_character_sections:
                    break

    return {
        "series": paths.name,
        "entity": character,
        "query_entity": entity,
        "abilities": abilities,
        "character_sections": character_sections,
    }

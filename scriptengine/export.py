"""Export a series' graph to an Obsidian vault.

Obsidian's graph view is built from markdown files joined by ``[[wikilinks]]``,
and the fact store already holds exactly that shape: directed, typed edges
between named nodes. This module renders it read-only: no changes to
ingestion, retrieval, or the schema.

Vault layout, one per series at ``series/<name>/obsidian/``:

    README.md       how to open the folder as a vault
    nodes/          one file per node; unresolved link targets are stubs
    documents/      one readable page per crawled document, prose re-linked

Filenames reuse the crawler's ``sanitise_filename``; when two titles collide on
disk they get a deterministic numeric suffix, and every ``[[link]]`` is written
to the collided filename so nothing in the vault dangles.
"""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

from scriptengine.config import SeriesPaths
from scriptengine.index.chunker import BOILERPLATE_SECTIONS
from scriptengine.ingest.crawler import load_pages, sanitise_filename
from scriptengine.ingest.documents import Link, WikiPage
from scriptengine.ingest.wikitext import extract_links
from scriptengine.stores.facts import FactStore

# A hub like "Yuji Itadori" points at hundreds of pages. The cap keeps one file
# from becoming a wall of links; after 500 bullets a file stops being a graph
# node and starts being a table of contents.
MAX_EDGES_PER_NODE = 500

_HEADING = re.compile(r"^(={2,6})\s*.+?\s*\1\s*$", re.MULTILINE)


def _collision_map(names: Iterable[str]) -> dict[str, str]:
    """Map every name to a filesystem-safe filename, unique case-insensitively.

    Windows treats ``Todo.md`` and ``todo.md`` as the same file, so collisions
    are detected on the folded name and resolved with a deterministic numeric
    suffix. The sorted iteration decides who keeps the plain name, which makes
    the mapping identical on every run.
    """
    used: set[str] = set()
    mapping: dict[str, str] = {}
    for name in sorted(names, key=str.casefold):
        base = sanitise_filename(name)
        candidate = base
        counter = 2
        while candidate.casefold() in used:
            candidate = f"{base}_{counter}"
            counter += 1
        used.add(candidate.casefold())
        mapping[name] = candidate
    return mapping


def _frontmatter(fields: dict[str, Any], citations: dict[str, str]) -> str:
    block = dict(fields)
    if citations:
        block["_citations"] = citations
    rendered = yaml.safe_dump(block, sort_keys=False, allow_unicode=True).rstrip()
    return f"---\n{rendered}\n---"


def _fact_properties(
    facts: Iterable[Any], taken: set[str]
) -> tuple[dict[str, str], dict[str, str]]:
    """Facts as frontmatter properties, plus a citation map keyed by property.

    The wiki's own label is the property name when it has one, else the
    infobox key, both already in the store. A property that collides with an
    earlier one (``type`` is a common infobox parameter and also the page's
    discovered type) is skipped: the file already says it.
    """
    properties: dict[str, str] = {}
    citations: dict[str, str] = {}
    for fact in facts:
        name = (fact["label"] or fact["key"] or "value").strip()
        if not name or name in taken or name in properties:
            continue
        properties[name] = fact["value"]
        if fact["citation"]:
            citations[name] = fact["citation"]
    return properties, citations


def _write_node(
    out: Path,
    name: str,
    filename: str,
    label: str,
    is_resolved: int,
    aliases: list[str],
    facts: list[Any],
    relations: list[tuple[str, str]],
    filenames: dict[str, str],
) -> None:
    taken = set("url _citations".split())
    fields: dict[str, Any] = {}
    if label and label != "unknown":
        fields["type"] = label
        taken.add("type")
    if aliases:
        fields["aliases"] = sorted(aliases)
        taken.add("aliases")
    fields["resolved"] = bool(is_resolved)
    taken.add("resolved")

    properties, citations = _fact_properties(facts, taken)
    fields.update(properties)

    lines = [_frontmatter(fields, citations), "", f"# {name}", ""]
    if relations:
        lines.append("## Relations")
        lines.append("")
        for other, relation in relations:
            target = filenames[other]
            if relation == "mentions":
                lines.append(f"- [[{target}]]")
            else:
                display = relation.replace("[", "").replace("]", "").strip()
                lines.append(f"- [[{target}|{display}]]")
        lines.append("")
    (out / f"{filename}.md").write_text("\n".join(lines), encoding="utf-8")


def _write_document(
    out: Path,
    page: WikiPage,
    filename: str,
    page_type: str,
    url: str,
    facts: list[Any],
    filenames: dict[str, str],
) -> None:
    taken = set("type url resolved aliases _citations".split())
    fields: dict[str, Any] = {}
    if page_type and page_type != "unknown":
        fields["type"] = page_type
    if url:
        fields["url"] = url

    properties, citations = _fact_properties(facts, taken)
    fields.update(properties)

    lines = [_frontmatter(fields, citations), "", f"# {page.title}", ""]
    if page.lead:
        lines.append(_relink(page.lead, _lead_links(page), filenames))
        lines.append("")
    for section in page.sections:
        if section.title.casefold() in BOILERPLATE_SECTIONS:
            continue
        text = _relink(section.text, section.links, filenames)
        if not text.strip():
            continue
        heading = "#" * min(section.level, 6)
        lines.append(f"{heading} {section.title}")
        lines.append("")
        lines.append(text)
        lines.append("")
    (out / f"{filename}.md").write_text("\n".join(lines), encoding="utf-8")


def _lead_links(page: WikiPage) -> list[Link]:
    """The page's own links, parsed from its wikitext before the first heading.

    The lead is stored stripped, so its links have to come from the raw text:
    the infobox and the opening paragraph both sit before the first heading.
    """
    match = _HEADING.search(page.wikitext)
    lead_wikitext = page.wikitext[: match.start()] if match else page.wikitext
    return extract_links(lead_wikitext)


def _relink(text: str, links: Iterable[Link], filenames: dict[str, str]) -> str:
    """Replace link display text with ``[[target|display]]``, in order.

    Each link is rendered at the first occurrence of its display text at or
    after the previous match, so repeated displays consume separate spans.
    Targets with no vault file (interwiki links, links the crawl never saw)
    stay plain: every ``[[link]]`` written resolves to a file.
    """
    spans: list[tuple[int, int, str]] = []
    cursor = 0
    for link in links:
        display = link.display
        start = text.find(display, cursor)
        if start < 0:
            continue
        filename = filenames.get(link.target)
        if filename is None:
            continue
        end = start + len(display)
        rendered = (
            f"[[{filename}]]" if filename == display else f"[[{filename}|{display}]]"
        )
        spans.append((start, end, rendered))
        cursor = end
    if not spans:
        return text
    out = text
    for start, end, rendered in reversed(spans):
        out = out[:start] + rendered + out[end:]
    return out


def export_obsidian(
    paths: SeriesPaths,
    out_dir: str | Path | None = None,
    min_confidence: float = 0.4,
    include_documents: bool = True,
) -> dict[str, Any]:
    """Render `series/<name>/obsidian/` from the fact store. Read-only.

    Returns a small report dict (counts, vault path) for the CLI.
    """
    out = Path(out_dir) if out_dir else paths.root / "obsidian"
    if out.exists():
        shutil.rmtree(out)
    nodes_dir = out / "nodes"
    nodes_dir.mkdir(parents=True)
    docs_dir = out / "documents"
    if include_documents:
        docs_dir.mkdir()

    if not paths.facts_db.exists():
        raise FileNotFoundError(
            f"Series {paths.name!r} is not indexed: no facts.db. Run `index` first."
        )

    with FactStore(paths.facts_db) as store:
        nodes = store.connection.execute(
            "SELECT name, label, is_resolved FROM nodes ORDER BY name COLLATE NOCASE"
        ).fetchall()

        edge_rows = store.connection.execute(
            "SELECT s.name AS source, e.relation, t.name AS target"
            " FROM edges e"
            " JOIN nodes s ON s.id = e.source_id"
            " JOIN nodes t ON t.id = e.target_id"
            " WHERE e.confidence >= ?"
            " ORDER BY e.confidence DESC, e.relation, t.name",
            (min_confidence,),
        ).fetchall()

        facts_by_name: dict[str, list[Any]] = {}
        for fact in store.connection.execute(
            "SELECT n.name AS entity, f.key, f.label, f.value, f.citation"
            " FROM facts f JOIN nodes n ON n.id = f.node_id"
            " ORDER BY n.name COLLATE NOCASE, f.id"
        ):
            facts_by_name.setdefault(fact["entity"], []).append(fact)

        aliases_by_name: dict[str, list[str]] = {}
        for row in store.connection.execute(
            "SELECT n.name AS entity, a.alias"
            " FROM aliases a JOIN nodes n ON n.id = a.node_id"
            " ORDER BY n.name COLLATE NOCASE, a.alias"
        ):
            aliases_by_name.setdefault(row["entity"], []).append(row["alias"])

        documents_by_title = {
            row["title"]: row
            for row in store.connection.execute(
                "SELECT title, page_type, url FROM documents"
            )
        }

    filenames = _collision_map(row["name"] for row in nodes)

    edges_by_node: dict[str, list[tuple[str, str]]] = {}
    seen: dict[str, set[tuple[str, str]]] = {}
    for row in edge_rows:
        if row["source"] == row["target"]:
            continue
        for name, other in (
            (row["source"], row["target"]),
            (row["target"], row["source"]),
        ):
            bucket = edges_by_node.get(name)
            if bucket is None:
                bucket = []
                edges_by_node[name] = bucket
                seen[name] = {(other, row["relation"])}
            elif (other, row["relation"]) in seen[name]:
                continue
            elif len(bucket) >= MAX_EDGES_PER_NODE:
                continue
            else:
                seen[name].add((other, row["relation"]))
            bucket.append((other, row["relation"]))

    pages = {}
    if include_documents and paths.wikitext.exists():
        pages = {page.title: page for page in load_pages(paths)}

    stub_count = 0
    for row in nodes:
        if not row["is_resolved"]:
            stub_count += 1
        _write_node(
            nodes_dir,
            row["name"],
            filenames[row["name"]],
            row["label"],
            row["is_resolved"],
            aliases_by_name.get(row["name"], []),
            facts_by_name.get(row["name"], []),
            edges_by_node.get(row["name"], []),
            filenames,
        )

    doc_count = 0
    if include_documents:
        for row in nodes:
            if not row["is_resolved"]:
                continue
            page = pages.get(row["name"])
            document = documents_by_title.get(row["name"])
            if page is None or document is None:
                continue
            _write_document(
                docs_dir,
                page,
                filenames[row["name"]],
                document["page_type"],
                document["url"] or "",
                facts_by_name.get(row["name"], []),
                filenames,
            )
            doc_count += 1

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    (out / "README.md").write_text(
        f"# ScriptEngine export: {paths.name}\n\n"
        f"The wiki graph of series `{paths.name}`, exported read-only from "
        f"`facts.db` on {generated} (edges at confidence >= {min_confidence:g}).\n\n"
        f"- **`nodes/`**: one file per node ({len(nodes):,}); files with "
        f"`resolved: false` in the frontmatter are links the crawl never reached.\n"
        f"- **`documents/`**: one readable page per crawled document "
        f"({doc_count:,}).\n\n"
        f"## Open this folder as a vault\n\n"
        f"1. Obsidian → **Open folder as vault**.\n"
        f"2. Pick `{out}`.\n"
        f"3. Graph view (`Ctrl`+`G` / `Cmd`+`G`) → enable *Links* under filters.\n\n"
        f"Notes: regenerating while Obsidian has this folder open rewrites every "
        f"file; close Obsidian first, or accept the refresh.",
        encoding="utf-8",
    )

    return {
        "vault": str(out),
        "series": paths.name,
        "nodes": len(nodes),
        "documents": doc_count,
        "stubs": stub_count,
        "edges": len(edge_rows),
        "min_confidence": min_confidence,
    }

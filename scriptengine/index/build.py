"""Building the index: crawled pages in, queryable stores out.

Indexing is a rebuild rather than an append. Both stores are recreated from the
pages on disk, which makes the result a pure function of the corpus — re-running
after an extraction fix produces exactly what a fresh run would, with no
half-updated state to reason about. Re-crawling is the expensive step; this one
is cheap enough to repeat.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Iterable

from scriptengine.config import Settings, SeriesPaths, get_settings, load_overrides
from scriptengine.index.chunker import Chunk, chunk_page, embeddable
from scriptengine.index.embedder import Embedder
from scriptengine.ingest.crawler import load_extracted, load_manifest
from scriptengine.ingest.documents import WikiPage
from scriptengine.stores.facts import FactStore
from scriptengine.stores.vectors import VectorStore

logger = logging.getLogger(__name__)

Progress = Callable[[str, int, int], None]


def build_index(
    paths: SeriesPaths,
    settings: Settings | None = None,
    *,
    embed: bool = True,
    progress: Progress | None = None,
) -> dict[str, Any]:
    """Populate `facts.db` and the vector store from `series/<name>/wikitext`.

    `embed=False` builds everything except the vectors, which is useful when
    the GPU is busy: the fact store, the graph and BM25 search are all fully
    functional without them.
    """
    settings = settings or get_settings()
    manifest = load_manifest(paths)

    # Loading, discovery and re-extraction all happen in `load_extracted`, so
    # that `audit` and `index` can never disagree about what the corpus holds.
    logger.info("loading and re-extracting the corpus")
    pages, ontology = load_extracted(paths, load_overrides(paths))
    if not pages:
        return {"error": "no crawled pages found; run `crawl` first"}
    logger.info("vocabulary: %s types across %s pages", len(ontology.types), len(pages))

    report: dict[str, Any] = {"series": paths.name, "pages": len(pages)}

    with FactStore(paths.facts_db) as store:
        store.reset()
        chunks_by_page = _load_documents(store, pages, progress)
        _load_graph(store, pages, progress)
        chunk_rows = _load_chunks(store, pages, chunks_by_page, progress)
        store.rebuild_fts()
        store.set_meta("wiki", manifest.get("wiki") or "")
        store.set_meta("embed_model", settings.embed_model)
        store.commit()
        report["stats"] = store.stats()

    report["chunks"] = len(chunk_rows)
    report["embedded"] = 0

    if embed and chunk_rows:
        report["embedded"] = _embed_chunks(paths, settings, chunk_rows, progress)

    return report


def _load_documents(
    store: FactStore, pages: Iterable[WikiPage], progress: Progress | None
) -> dict[str, list[Chunk]]:
    """Insert documents and sections, and chunk each page."""
    chunks_by_page: dict[str, list[Chunk]] = {}
    pages = list(pages)

    for index, page in enumerate(pages):
        document_id = store.add_document(
            title=page.title,
            url=page.url,
            page_type=page.page_type,
            infobox_template=page.infobox_template,
            lead=page.lead,
            word_count=page.word_count,
            revid=page.revid,
            fetched_at=page.fetched_at,
        )

        store.add_categories(document_id, page.categories)

        for ordinal, section in enumerate(page.sections):
            store.add_section(
                document_id=document_id,
                title=section.title,
                breadcrumb=section.breadcrumb,
                level=section.level,
                ordinal=ordinal,
                text=section.text,
                word_count=section.word_count,
            )

        chunks_by_page[page.title] = chunk_page(page)

        if progress and index % 100 == 0:
            progress("documents", index + 1, len(pages))

    store.commit()
    return chunks_by_page


def _load_graph(
    store: FactStore, pages: Iterable[WikiPage], progress: Progress | None
) -> None:
    """Insert nodes, aliases, facts and edges.

    Nodes are created for every page first, so that an edge pointing at a page
    crawled later still resolves. Unresolved targets — links to pages the crawl
    never reached — are created as bare nodes and flagged, rather than dropped:
    knowing that Todo is affiliated with something is worth more than silence,
    even when that something has no page here.
    """
    pages = list(pages)
    node_ids: dict[str, int] = {}

    for page in pages:
        row = store.connection.execute(
            "SELECT id FROM documents WHERE title = ?", (page.title,)
        ).fetchone()
        node_id = store.add_node(page.title, page.page_type, row["id"] if row else None)
        node_ids[page.title] = node_id
        store.add_aliases(node_id, [page.title, *page.aliases])

    for target, alias in _harvest_link_aliases(pages).items():
        node_id = node_ids.get(target)
        if node_id is not None:
            store.add_aliases(node_id, alias)

    for index, page in enumerate(pages):
        source_id = node_ids[page.title]

        for fact in page.facts:
            store.add_fact(
                node_id=source_id,
                key=fact.key,
                label=fact.label,
                value=fact.value,
                citation="; ".join(c.describe() for c in fact.citations),
            )

        for edge in page.edges:
            target_id = node_ids.get(edge.target)
            if target_id is None:
                target_id = store.add_node(edge.target)
                node_ids[edge.target] = target_id
                store.add_aliases(target_id, [edge.target])

            store.add_edge(
                source_id=source_id,
                relation=edge.relation,
                target_id=target_id,
                confidence=edge.confidence,
                provenance=edge.provenance,
                section=edge.section,
            )

        if progress and index % 100 == 0:
            progress("graph", index + 1, len(pages))

    store.commit()


def _harvest_link_aliases(
    pages: list[WikiPage], min_occurrences: int = 3
) -> dict[str, set[str]]:
    """Learn the names people actually use, from how they write their links.

    A wiki's own redirects are thinner than they look — Jujutsu Kaisen redirects
    "Todo Aoi" to "Aoi Todo" but not the bare "Todo", so a question asking about
    Todo reaches nothing. Yet the prose is full of ``[[Aoi Todo|Todo]]``.

    The display text of a wikilink is an editor stating what that page is
    commonly called, and it costs nothing extra: the links were already parsed.
    Requiring several independent occurrences keeps one-off phrasings ("his best
    friend", "the man himself") out of the alias table.
    """
    counts: dict[tuple[str, str], int] = {}

    for page in pages:
        seen_here: set[tuple[str, str]] = set()
        for link in [*page.links, *(l for s in page.sections for l in s.links)]:
            display = link.display.strip()
            if not display or display.lower() == link.target.lower():
                continue
            # Aliases are names, not sentences.
            if len(display) > 60 or len(display.split()) > 6:
                continue
            seen_here.add((link.target, display))
        for key in seen_here:
            counts[key] = counts.get(key, 0) + 1

    aliases: dict[str, set[str]] = {}
    for (target, display), count in counts.items():
        if count >= min_occurrences:
            aliases.setdefault(target, set()).add(display)
    return aliases


def _load_chunks(
    store: FactStore,
    pages: Iterable[WikiPage],
    chunks_by_page: dict[str, list[Chunk]],
    progress: Progress | None,
) -> list[dict[str, Any]]:
    """Insert chunks, wire parents, and link each chunk to the entities it names.

    Returns the level-0 and level-2 chunks, which are what gets embedded.
    """
    pages = list(pages)
    to_embed: list[dict[str, Any]] = []

    for index, page in enumerate(pages):
        chunks = chunks_by_page.get(page.title, [])
        if not chunks:
            continue

        row = store.connection.execute(
            "SELECT id FROM documents WHERE title = ?", (page.title,)
        ).fetchone()
        if row is None:
            continue
        document_id = int(row["id"])

        section_ids = [
            int(section["id"]) for section in store.document_sections(page.title)
        ]
        # Maps a chunk's ordinal to its database id, so a level-2 chunk can point
        # at the level-1 parent inserted moments earlier.
        ids_by_ordinal: dict[int, int] = {}

        for chunk in chunks:
            section_id = None
            if chunk.section_index is not None and chunk.section_index < len(section_ids):
                section_id = section_ids[chunk.section_index]

            parent_id = (
                ids_by_ordinal.get(chunk.parent_ordinal)
                if chunk.parent_ordinal is not None
                else None
            )

            chunk_id = store.add_chunk(
                document_id=document_id,
                section_id=section_id,
                parent_id=parent_id,
                level=chunk.level,
                ordinal=chunk.ordinal,
                doc_title=chunk.doc_title,
                breadcrumb=chunk.breadcrumb,
                text=chunk.text,
            )
            ids_by_ordinal[chunk.ordinal] = chunk_id

            if chunk.entities:
                placeholders = ",".join("?" * len(chunk.entities))
                rows = store.connection.execute(
                    f"SELECT id FROM nodes WHERE name IN ({placeholders})",
                    tuple(chunk.entities),
                ).fetchall()
                store.link_chunk_nodes(chunk_id, [int(r["id"]) for r in rows])

            if chunk.level in (0, 2):
                to_embed.append(
                    {
                        "chunk_id": chunk_id,
                        "text": chunk.text,
                        "doc_title": chunk.doc_title,
                        "breadcrumb": chunk.breadcrumb,
                        "level": chunk.level,
                        "ordinal": chunk.ordinal,
                        "page_type": page.page_type,
                    }
                )

        if progress and index % 100 == 0:
            progress("chunks", index + 1, len(pages))

    store.commit()
    return to_embed


def _embed_chunks(
    paths: SeriesPaths,
    settings: Settings,
    chunks: list[dict[str, Any]],
    progress: Progress | None,
) -> int:
    """Embed and store vectors, in batches so memory stays flat."""
    embedder = Embedder(settings)
    logger.info(
        "embedding %s chunks with %s on %s",
        len(chunks), settings.embed_model, embedder.device,
    )

    with VectorStore(paths.vectors) as vectors:
        vectors.recreate(embedder.dimensions)

        batch_size = max(settings.embed_batch_size * 8, 128)
        done = 0
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            encoded = embedder.encode_passages([chunk["text"] for chunk in batch])
            vectors.upsert(batch, encoded)
            done += len(batch)
            if progress:
                progress("embedding", done, len(chunks))

        # A vector store holding more points than the chunks that produced them
        # is corrupt, not merely untidy: point ids are SQLite rowids, and a
        # stale one resolves against whatever row now holds that id.
        stored = vectors.count()
        if stored != done:
            logger.error(
                "vector store holds %s points but %s chunks were embedded; "
                "delete %s and re-run `index`",
                stored, done, paths.vectors,
            )

    embedder.unload()
    return done


def index_status(paths: SeriesPaths) -> dict[str, Any]:
    """What has been built for a series."""
    status: dict[str, Any] = {
        "series": paths.name,
        "crawled_pages": len(list(paths.wikitext.glob("*.json")))
        if paths.wikitext.exists()
        else 0,
        "facts_db": paths.facts_db.exists(),
        "vectors": paths.vectors.exists(),
    }
    if status["facts_db"]:
        with FactStore(paths.facts_db) as store:
            status["stats"] = store.stats()
    if status["vectors"]:
        with VectorStore(paths.vectors) as vectors:
            status["vector_count"] = vectors.count()
    return status


def write_status(paths: SeriesPaths, report: dict[str, Any]) -> str:
    paths.audit.mkdir(parents=True, exist_ok=True)
    destination = paths.audit / "index.json"
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return str(destination)

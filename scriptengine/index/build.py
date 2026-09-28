"""Building the index: crawled pages in, queryable stores out.

Indexing is a rebuild rather than an append. Both stores are recreated from the
pages on disk, which makes the result a pure function of the corpus, so re-running
after an extraction fix produces exactly what a fresh run would, with no
half-updated state to reason about. Re-crawling is the expensive step; this one
is cheap enough to repeat.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Iterable

from scriptengine.config import Settings, SeriesPaths, get_settings, load_overrides
from scriptengine.index.chunker import (
    Chunk,
    chunk_page,
    effective_boilerplate_sections,
    embeddable,
)
from scriptengine.ingest.canon import (
    discounted_works,
    keep_sections,
    page_is_discounted,
)
from scriptengine.index.embedder import Embedder
from scriptengine.ingest.crawler import load_extracted, load_manifest
from scriptengine.ingest.documents import WikiPage
from scriptengine.ingest.wikitext import emphasised_names
from scriptengine.stores.facts import FactStore
from scriptengine.stores.vectors import VectorStore

logger = logging.getLogger(__name__)

Progress = Callable[[str, int, int], None]


def build_index(
    paths: SeriesPaths,
    settings: Settings | None = None,
    *,
    embed: bool = True,
    force: bool = False,
    progress: Progress | None = None,
) -> dict[str, Any]:
    """Populate `facts.db` and the vector store from `series/<name>/wikitext`.

    `embed=False` builds everything except the vectors, which is useful when
    the GPU is busy: the fact store, the graph and BM25 search are all fully
    functional without them.

    `force` controls what a rebuild does to the two derived, model-built
    layers (`events`, `meaning`). By default a rebuild is *refused* while they
    are non-empty (`ResetRefusedError`) -- a reflexive `index` must not destroy
    an extraction pass. With `force=True` the rebuild proceeds and the rows are
    snapshotted with their durable key then re-keyed onto the new build's ids by
`remap_derived`, so nothing is wiped: only rows that went stale (their
     document's `revid` changed), orphaned, or unverified (their section no
     longer proves them) are dropped, each counted and reported.
    """
    settings = settings or get_settings()
    manifest = load_manifest(paths)
    overrides = load_overrides(paths)

    # Loading, discovery and re-extraction all happen in `load_extracted`, so
    # that `audit` and `index` can never disagree about what the corpus holds.
    logger.info("loading and re-extracting the corpus")
    pages, ontology = load_extracted(paths, overrides)
    if not pages:
        return {"error": "no crawled pages found; run `crawl` first"}
    logger.info("vocabulary: %s types across %s pages", len(ontology.types), len(pages))

    report: dict[str, Any] = {"series": paths.name, "pages": len(pages)}

    # The works this series does not count are dropped here rather than
    # filtered later, so nothing downstream can reach them at all.
    works = discounted_works(overrides)
    if works:
        before = len(pages)
        # A debut target is judged on its own title *and* its own categories,
        # so the whole corpus has to be to hand before any page is judged.
        categories_by_title = {
            page.title.lower(): page.categories for page in pages
        }
        dropped = {
            page.title
            for page in pages
            if page_is_discounted(page, works, categories_by_title)
        }
        # A subpage goes with its parent. `Xeno Trunks` was dropped on its own
        # title while `Xeno Trunks/Biography` and `/Power and Abilities` stayed,
        # because a subpage carries neither the categories nor the debut that
        # settled the parent.
        pages = [
            page
            for page in pages
            if page.title not in dropped
            and page.title.split("/", 1)[0] not in dropped
        ]
        report["dropped_pages"] = before - len(pages)
        report["pages"] = len(pages)
        logger.info(
            "dropped %s pages belonging only to %s discounted works",
            before - len(pages), len(works),
        )
    else:
        dropped = set()

    with FactStore(paths.facts_db) as store:
        # The reset guard (0B): refuse a non-forced rebuild while the derived
        # layers are non-empty, so a reflexive `index` never destroys an
        # extraction pass. A forced rebuild proceeds; the rows are snapshotted
        # by `reset` and re-keyed onto the new build's ids below, not wiped.
        store.require_rebuild(force=force)
        snapshot = store.reset()
        # A wiki can promote engine-default boilerplate to content (JJK's
        # `References` carries trivia the span-recall oracle must reach), so the
        # chunker skips the wiki's effective set, not just the global one.
        boilerplate = effective_boilerplate_sections(overrides)
        chunks_by_page = _load_documents(
            store, pages, progress, works, dropped, boilerplate
        )
        node_ids, alias_resolver = _load_graph(
            store, pages, progress, dropped, overrides
        )
        # Facts the wiki declares and the extractor cannot derive (interval
        # states: what a character's state was *during* an arc, which the
        # infobox's current-state read cannot express). Per-wiki data in
        # `overrides.yaml` (`extra_facts`); applied after the graph, when the
        # node ids exist, so a re-index recreates them.
        report["declared_facts"] = _apply_declared_facts(
            store, node_ids, overrides.get("extra_facts") or [], dropped
        )
        chunk_rows = _load_chunks(
            store, pages, chunks_by_page, progress, alias_resolver
        )
        store.rebuild_fts()
        # Re-key the snapshotted derived layers onto the build that just ran:
        # their section/node ids were renumbered, but their durable keys
        # (doc_title + section_ordinal, participant names) still resolve. Rows
        # whose document's revid changed, whose section/node vanished, or whose
        # section moved under a parser fix and no longer proves the row (the
        # quote / sentence hash fails against the new text) are dropped and
        # reported, so a stale extraction can never masquerade as current.
        # `reset` also wrote the snapshot to a file beside the database, so a
        # build that dies in the minutes between the drop and this call is
        # recoverable: the next run finds the layers empty, passes the guard,
        # and `remap_derived` reads the file (the call here passes the
        # in-memory copy, which takes precedence). A fresh build (no derived
        # layers yet) has an empty snapshot: no-op.
        report["remap"] = store.remap_derived(snapshot)
        # What was removed, recorded for the query path.
        #
        # Retrieval cannot re-derive it: the page is gone, so there is no
        # debut left to judge, and a name with no page is exactly the shape
        # prose extraction exists to keep (`Dismantle` has no page either).
        # The `abilities` table also survives `reset()` by design, so it still
        # holds rows read out of prose before the removal: `Goku` had
        # `Super Saiyan (Berserk)` among his forms with the page, the heading
        # and the edge all already gone.
        store.set_meta("dropped_titles", json.dumps(sorted(dropped)))
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
    store: FactStore,
    pages: Iterable[WikiPage],
    progress: Progress | None,
    works: tuple[str, ...] = (),
    dropped: set[str] | None = None,
    boilerplate: set[str] | None = None,
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

        # What this page *names*, as against what it merely mentions. Computed
        # here because `strip_markup` removes the page's own emphasis along
        # with everything else, so once a chunk is stored the distinction is
        # unrecoverable. See `wikitext.emphasised_names`.
        store.add_emphasis(
            document_id,
            emphasised_names(
                "\n".join(section.wikitext or "" for section in page.sections)
            ),
        )

        # A kept page may still have a discounted work's corner in it,
        # `Goku/Biography` carries a seven-saga Super Dragon Ball Heroes
        # subtree. Dropped once, so sections and chunks agree.
        page.sections = keep_sections(page.sections, works, dropped)

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

        chunks_by_page[page.title] = chunk_page(page, boilerplate=boilerplate)

        if progress and index % 100 == 0:
            progress("documents", index + 1, len(pages))

    store.commit()
    return chunks_by_page


def _root_of(title: str) -> str:
    """The page a subpage's names are about.

    `Iron Man/Avengers Assassinated` writing "Tony Stark" is evidence about
    the `Iron Man` page, not about a second entity, so alias claims from a
    subpage count for its root.
    """
    return title.split("/", 1)[0]


def _build_alias_resolver(
    pages: list[WikiPage],
    usage: dict[str, set[str]],
    overrides: dict[str, Any],
    node_ids: dict[str, int],
) -> dict[str, int]:
    """Which page's node a bare alias name resolves to, by the wiki's own evidence.

    A name like `Tony Stark` that is not itself a page title (the live wiki's
    page is `#REDIRECT [[Iron Man]]`, and redirects are followed, not
    crawled) would otherwise spawn a stub node that forks the entity: every
    edge and chunk link written under the bare name lands on the stub. The
    name resolves to a page's node when the wiki's evidence points at exactly
    one page:

    - a page's own `aliases` / `redirects` fields name it;
    - at least three independent pages write ``[[Page|Name]]`` (the same
      usage evidence the harvest feeds the alias table);
    - a name several pages claim stays unresolved: a coin-flip merge is
      worse than the stub it replaces.

    The inferred evidence applies only when the series declares
    `alias_merge: true` in `overrides.yaml`: a bare-name merge reshapes the
    graph that drives retrieval, so every wiki opts in on its own evidence
    and the 100% baselines stay byte-identical (architect 2026-09-28, P2b
    merge census: the un-gated heuristic absorbed 28 stub nodes in csm
    alone). An `alias_map` pin is a declaration in its own right and always
    applies; a title the build does not hold is skipped with a warning,
    never invented.
    """
    ov = overrides or {}
    claimers: dict[str, set[str]] = {}

    def claim(name: str, page_title: str) -> None:
        root = _root_of(page_title)
        if root in node_ids:
            claimers.setdefault(name.strip().lower(), set()).add(root)

    if ov.get("alias_merge"):
        for page in pages:
            for name in [*page.aliases, *page.redirects]:
                claim(name, page.title)
        for target, names in usage.items():
            if target in node_ids:
                for name in names:
                    claim(name, target)

    resolver: dict[str, int] = {
        name: node_ids[next(iter(roots))]
        for name, roots in claimers.items()
        if len(roots) == 1
    }
    for name, title in ((overrides or {}).get("alias_map") or {}).items():
        title = str(title).strip()
        node_id = node_ids.get(title)
        if node_id is None:
            logger.warning(
                "alias_map %r -> %r skipped: no such page in this build", name, title,
            )
            continue
        resolver[str(name).strip().lower()] = node_id
    return resolver


def _load_graph(
    store: FactStore,
    pages: Iterable[WikiPage],
    progress: Progress | None,
    dropped: set[str] | None = None,
    overrides: dict[str, Any] | None = None,
) -> tuple[dict[str, int], dict[str, int]]:
    """Insert nodes, aliases, facts and edges.

    Nodes are created for every page first, so that an edge pointing at a page
    crawled later still resolves. Unresolved targets (links to pages the crawl
    never reached) are created as bare nodes and flagged, rather than dropped:
    knowing that Todo is affiliated with something is worth more than silence,
    even when that something has no page here. One exception: a target the
    wiki's own alias evidence points at a single page merges into that page's
    node (`_build_alias_resolver`) instead of forking a stub.

    Returns the title-to-node-id map (so a later build step can resolve a
    declared fact by the name the wiki wrote it under) and the alias resolver
    (so chunk entity links follow the same merge).
    """
    pages = list(pages)
    dropped = dropped or set()
    node_ids: dict[str, int] = {}

    for page in pages:
        row = store.connection.execute(
            "SELECT id FROM documents WHERE title = ?", (page.title,)
        ).fetchone()
        node_id = store.add_node(page.title, page.page_type, row["id"] if row else None)
        node_ids[page.title] = node_id
        store.add_aliases(node_id, [page.title, *page.aliases])

    usage = _harvest_link_aliases(pages)
    for target, alias in usage.items():
        node_id = node_ids.get(target)
        if node_id is not None:
            store.add_aliases(node_id, alias)
    resolver = _build_alias_resolver(pages, usage, overrides or {}, node_ids)
    merged_names: set[str] = set()

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
            # An edge to a page this series does not count is not an unresolved
            # target, it is a removed one. `Goku` still lists
            # `Super Saiyan (Berserk)` among his users, and ownership reads
            # those edges, so leaving them put the form back in "Every form of
            # Goku" after the page and the heading had both gone.
            if edge.target in dropped:
                continue
            target_id = node_ids.get(edge.target)
            if target_id is None:
                # The wiki's own alias evidence may point this bare name at a
                # single page's node: merge instead of forking a stub.
                target_id = resolver.get(edge.target.strip().lower())
                if target_id is not None:
                    node_ids[edge.target] = target_id
                    merged_names.add(edge.target)
                else:
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

    for name in sorted(merged_names):
        # The merged name is now a known alias of the page's node: record it
        # (idempotent) so alias lookups find it, as the harvest would have.
        store.add_aliases(resolver[name.strip().lower()], [name])

    store.commit()
    if resolver:
        logger.info(
            "alias resolution: %s names merge into their page's node", len(resolver),
        )
    return node_ids, resolver


def _apply_declared_facts(
    store: FactStore,
    node_ids: dict[str, int],
    declared: Iterable[dict[str, Any]],
    dropped: set[str] | None,
) -> dict[str, Any]:
    """Upsert the facts a wiki declares in `overrides.yaml` under `extra_facts`.

    These hold only inside a story window (a character dead before the arc
    being written), so the infobox extractor, which reads the entity's current
    page, cannot derive them. Declared by node name; a node the build dropped
    or never crawled is skipped, not created: a declaration about an absent
    page is a fix, not content to invent. Each (node, key) is replaced, never
    appended, so a key the infobox already carries cannot double.
    """
    dropped = dropped or set()
    applied: list[str] = []
    skipped: list[str] = []
    for fact in declared:
        name = str(fact.get("node") or "")
        key = str(fact.get("key") or "")
        value = str(fact.get("value") or "")
        if not name or not key or not value:
            skipped.append(f"{name or '(unnamed)'}: node, key and value are required")
            continue
        node_id = node_ids.get(name)
        if node_id is None or name in dropped:
            skipped.append(f"{name}: no node in this build")
            continue
        store.connection.execute(
            "DELETE FROM facts WHERE node_id = ? AND key = ?", (node_id, key)
        )
        store.add_fact(
            node_id=node_id,
            key=key,
            label=str(fact.get("label") or key),
            value=value,
            citation=str(fact.get("citation") or ""),
        )
        applied.append(f"{name}/{key}")
    for reason in skipped:
        logger.warning("declared fact skipped: %s", reason)
    return {"applied": applied, "skipped": skipped}


def _harvest_link_aliases(
    pages: list[WikiPage], min_occurrences: int = 3
) -> dict[str, set[str]]:
    """Learn the names people actually use, from how they write their links.

    A wiki's own redirects are thinner than they look: Jujutsu Kaisen redirects
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
    resolver: dict[str, int] | None = None,
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
                    f"SELECT id, name FROM nodes WHERE name IN ({placeholders})",
                    tuple(chunk.entities),
                ).fetchall()
                linked = {int(r["id"]) for r in rows}
                found = {r["name"] for r in rows}
                # An entity written under a page's alias (the wiki's own
                # display name) links to that page's node, not a stub: the
                # same merge the graph edges follow above.
                if resolver:
                    for name in chunk.entities:
                        if name not in found:
                            node_id = resolver.get(name.strip().lower())
                            if node_id is not None:
                                linked.add(node_id)
                store.link_chunk_nodes(chunk_id, list(linked))

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

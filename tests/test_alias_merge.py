"""Bare-name alias merging at index time (architect steer 2026-09-28).

The mcu wiki's `Tony Stark` page is a `#REDIRECT [[Iron Man]]`, and redirects
are followed, not crawled: the corpus holds the `Iron Man` page and never the
redirect. Every edge and chunk entity written under the bare name therefore
forked a stub node (2,997 edges, 13,304 chunk links in the live store,
measured 2026-09-28). The steer: no store surgery — the index rebuild is the
only writer, so the fix lands in the build, from the wiki's own evidence:

- usage: at least three independent pages write ``[[Page|Name]]`` (the same
  evidence the alias harvest already keeps);
- claims: a page's own `aliases` / `redirects` fields name it, and a subpage's
  claims count for its root page;
- declaration: `overrides.yaml` `alias_map` pins a name and wins over the
  inferred evidence.

A name two or more pages claim stays a stub: a coin-flip merge is worse than
the stub it replaces.

The inferred evidence (usage + claims) is gated behind `alias_merge: true`
in the series' `overrides.yaml`: a bare-name merge reshapes the graph that
drives retrieval, so every wiki opts in on its own evidence and the 100%
baselines stay byte-identical (architect 2026-09-28, P2b merge census: the
un-gated heuristic absorbed 28 stub nodes in csm alone). An `alias_map` pin
is a declaration in its own right and applies even without `alias_merge`.
"""

from __future__ import annotations

import pytest

from scriptengine.index.build import _load_chunks, _load_graph
from scriptengine.index.chunker import Chunk
from scriptengine.ingest.documents import Edge, Link, WikiPage
from scriptengine.stores.facts import FactStore

EDGE_PAGE = "Stark Weapons Smuggling Conspiracy"


@pytest.fixture()
def store(tmp_path):
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    yield store
    store.close()


def _page(
    title: str,
    *,
    page_type: str = "list",
    aliases: list[str] | None = None,
    edges: list[Edge] | None = None,
    links: list[Link] | None = None,
) -> WikiPage:
    return WikiPage(
        title=title,
        url="",
        page_type=page_type,
        aliases=list(aliases or []),
        edges=list(edges or []),
        links=list(links or []),
    )


def _voters() -> list[WikiPage]:
    """Three independent pages writing `[[Iron Man|Tony Stark]]`."""
    return [
        _page(title, links=[Link(target="Iron Man", display="Tony Stark")])
        for title in ("Battle of Sokovia", "Stark Expo", "Stark Industries")
    ]


def _edge_page() -> WikiPage:
    return _page(
        EDGE_PAGE,
        edges=[
            Edge(
                source=EDGE_PAGE, relation="mentions", target="Tony Stark"
            )
        ],
    )


def _node_ids_by_name(store: FactStore) -> dict[str, int]:
    rows = store.connection.execute("SELECT name, id FROM nodes").fetchall()
    return {row["name"]: int(row["id"]) for row in rows}


def _aliases_of(store: FactStore, node_id: int) -> set[str]:
    rows = store.connection.execute(
        "SELECT alias FROM aliases WHERE node_id = ?", (node_id,)
    ).fetchall()
    return {row["alias"] for row in rows}


class TestUsageMerge:
    MERGE = {"alias_merge": True}

    def test_unambiguous_usage_merges_the_bare_name_into_the_page_node(
        self, store: FactStore
    ):
        pages = [_page("Iron Man"), *_voters(), _edge_page()]
        node_ids, resolver = _load_graph(
            store, pages, None, None, self.MERGE
        )

        assert "tony stark" in resolver
        by_name = _node_ids_by_name(store)
        assert "Tony Stark" not in by_name  # no stub forked
        edge = store.connection.execute(
            "SELECT target_id FROM edges WHERE relation = 'mentions'"
        ).fetchone()
        assert edge["target_id"] == by_name["Iron Man"]
        # The merged name is a first-class alias of the page's node.
        assert "tony stark" in _aliases_of(store, by_name["Iron Man"])

    def test_two_pages_claiming_the_name_keep_the_stub(self, store: FactStore):
        # Usage points at Iron Man, but two pages' alias fields claim the
        # name: no inference, the stub stays.
        pages = [
            _page("Iron Man", aliases=["Tony Stark"]),
            _page("Stark Industries 2", aliases=["Tony Stark"]),
            *_voters(),
            _edge_page(),
        ]
        node_ids, resolver = _load_graph(
            store, pages, None, None, self.MERGE
        )

        assert "tony stark" not in resolver
        by_name = _node_ids_by_name(store)
        assert "Tony Stark" in by_name  # the stub was forked
        edge = store.connection.execute(
            "SELECT target_id FROM edges WHERE relation = 'mentions'"
        ).fetchone()
        assert edge["target_id"] == by_name["Tony Stark"]


class TestClaimMerge:
    MERGE = {"alias_merge": True}

    def test_a_subpages_alias_claims_count_for_their_root(self, store: FactStore):
        # One claim from the subpage's own alias fields is enough, and it
        # counts for the root page the subpage is about.
        pages = [
            _page("Iron Man"),
            _page("Iron Man/Avengers Assassinated", aliases=["Tony Stark"]),
            _edge_page(),
        ]
        node_ids, resolver = _load_graph(
            store, pages, None, None, self.MERGE
        )
        assert resolver.get("tony stark") == node_ids["Iron Man"]

    def test_unbacked_names_still_fork_bare_nodes(self, store: FactStore):
        pages = [
            _page("Iron Man"),
            _page(
                EDGE_PAGE,
                edges=[
                    Edge(
                        source=EDGE_PAGE,
                        relation="mentions",
                        target="Nobody Ever Wrote",
                    )
                ],
            ),
        ]
        node_ids, resolver = _load_graph(store, pages, None, None, {})
        assert "nobody ever wrote" not in resolver
        by_name = _node_ids_by_name(store)
        assert "Nobody Ever Wrote" in by_name
        assert "nobody ever wrote" in _aliases_of(
            store, by_name["Nobody Ever Wrote"]
        )


class TestGatedByDeclaration:
    def test_default_off_keeps_bare_names_forking_even_with_evidence(
        self, store: FactStore
    ):
        # A wiki that declares nothing keeps its graph as-is: the unambiguous
        # usage evidence must not reshape it (the 100% baselines stay
        # byte-identical; architect 2026-09-28).
        pages = [_page("Iron Man"), *_voters(), _edge_page()]
        node_ids, resolver = _load_graph(store, pages, None, None, {})

        assert "tony stark" not in resolver
        by_name = _node_ids_by_name(store)
        assert "Tony Stark" in by_name  # the stub was forked
        edge = store.connection.execute(
            "SELECT target_id FROM edges WHERE relation = 'mentions'"
        ).fetchone()
        assert edge["target_id"] == by_name["Tony Stark"]

    def test_an_explicit_false_disables_the_inference(self, store: FactStore):
        pages = [_page("Iron Man"), *_voters(), _edge_page()]
        node_ids, resolver = _load_graph(
            store, pages, None, None, {"alias_merge": False}
        )

        assert resolver == {}


class TestDeclarationMerge:
    # No `alias_merge` key: a pin is a declaration in its own right and
    # applies even on a wiki that opts out of the inference.
    OVERRIDES = {"alias_map": {"tony stark": "Iron Man"}}

    def test_the_declaration_pins_a_name_with_no_evidence(self, store: FactStore):
        pages = [_page("Iron Man"), _edge_page()]
        node_ids, resolver = _load_graph(store, pages, None, None, self.OVERRIDES)
        assert resolver.get("tony stark") == node_ids["Iron Man"]
        by_name = _node_ids_by_name(store)
        assert "Tony Stark" not in by_name

    def test_the_declaration_beats_ambiguous_evidence(self, store: FactStore):
        pages = [
            _page("Iron Man", aliases=["Tony Stark"]),
            _page("Stark Industries 2", aliases=["Tony Stark"]),
            *_voters(),
            _edge_page(),
        ]
        node_ids, resolver = _load_graph(
            store, pages, None, None, self.OVERRIDES
        )
        # Two claimers would have forked the stub; the pin wins.
        assert resolver.get("tony stark") == node_ids["Iron Man"]
        by_name = _node_ids_by_name(store)
        assert "Tony Stark" not in by_name

    def test_a_declaration_to_a_missing_page_is_skipped_not_invented(
        self, store: FactStore
    ):
        overrides = {"alias_map": {"ghost": "No Such Page"}}
        pages = [
            _page("Iron Man"),
            _page(
                EDGE_PAGE,
                edges=[
                    Edge(
                        source=EDGE_PAGE, relation="mentions", target="Ghost"
                    )
                ],
            ),
        ]
        node_ids, resolver = _load_graph(store, pages, None, None, overrides)
        assert resolver == {}
        by_name = _node_ids_by_name(store)
        assert "No Such Page" not in by_name  # never invented
        assert "Ghost" in by_name  # fell back to the plain stub


class TestChunkEntityMerge:
    def test_chunk_entities_follow_the_same_merge(self, store: FactStore):
        pages = [_page("Iron Man"), *_voters()]
        chunk_owner = "Battle of Sokovia"
        store.add_document(
            title=chunk_owner,
            url="",
            page_type="event",
            infobox_template="",
            lead="",
            word_count=0,
            revid=1,
            fetched_at="",
        )
        node_ids, resolver = _load_graph(
            store, pages, None, None, {"alias_merge": True}
        )
        chunk = Chunk(
            level=1,
            text="Tony Stark builds the mark XLIX.",
            doc_title=chunk_owner,
            ordinal=0,
            entities=["Tony Stark"],
        )
        _load_chunks(store, pages, {chunk_owner: [chunk]}, None, resolver)
        by_name = _node_ids_by_name(store)
        assert "Tony Stark" not in by_name
        links = store.connection.execute(
            """
            SELECT n.name FROM chunk_nodes cn
            JOIN chunks c ON c.id = cn.chunk_id
            JOIN nodes n ON n.id = cn.node_id
            WHERE c.document_id = (
                SELECT id FROM documents WHERE title = ?
            )
            """,
            (chunk_owner,),
        ).fetchall()
        assert [row["name"] for row in links] == ["Iron Man"]
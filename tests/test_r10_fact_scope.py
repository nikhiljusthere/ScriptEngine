"""R10: a story that lives only in fact values must enter the queue.

Marvel's two biggest narrative stores (``history`` 127k rows, ``synopsis*``
~40k rows) were never declared in ``events.narrative_fact_keys``, and the
fact passages only ran for pages already queued by the section rules -- so
a page whose story sits in a `history` or `synopsis*` value with no prose
section was never read. The fix is generic (declaration, not engine):

* ``narrative_fact_keys`` declares the wiki's narrative fact keys;
  ``fact_pages`` reaches the pages whose declared values hold a
  panel-eligible sentence and joins them to the ``all`` queue even when the
  page carries no extractable section at all;
* ``excluded_fact_keys`` records the prose keys the wiki deliberately does
  not read, each with a counted reason, so the dry-run census reports them
  -- counted, never silent.

A wiki that declares nothing (JJK, CSM) sees ``fact_pages`` as ``[]`` and
its ``all`` page list is byte-identical to the pre-fix tree.
"""

from __future__ import annotations

import pytest

from scriptengine.ingest.events import (
    build_passages,
    excluded_fact_keys,
    fact_key_census,
    fact_pages,
    fact_passages,
    prose_scope,
    scope_plan,
)
from scriptengine.stores.facts import FactStore

OVERRIDES = """\
events:
  placement_types: [arc]
  narrative_fact_keys:
    - history
    - synopsis*
  excluded_fact_keys:
    - {key: "trivia*", reason: "trivia, not narrative"}
"""

SILENT_OVERRIDES = "events:\n  placement_types: [arc]\n"

# Panel-eligible (one sentence of >= 6 words each), densest last.
SYNOPSIS_ORIGIN = (
    "The first instalment follows Zed as the island burns "
    "and he finds the relic at the temple door."
)
SYNOPSIS_RELIC = (
    "In the second instalment, Zed crosses the shattered archipelago to "
    "reach the drowned city, where the temple bells still ring for the "
    "tide-fishers who never returned home."
)
TRIVIA_DEAD_END = (
    "This page was created on a quiet Tuesday and the editor kept the "
    "blue banner because it matched the site."
)
PLOT_SECTION = (
    "Yara storms the lighthouse while the tide turns and Zed seals the "
    "relic in the drowned vault before the bells stop."
)


def _build(root, overrides_text: str) -> FactStore:
    """One placement page, two fact-only comic pages, one junk page.

    `Origin of Zed` and `Zed's Relic` carry no section: their story lives
    entirely in a declared `synopsis*` value. `Dead End`'s only declared
    value (`history`) holds no panel-eligible sentence, and its prose value
    sits on an excluded key -- no rule may queue it.
    """
    root.mkdir()
    (root / "overrides.yaml").write_text(overrides_text, encoding="utf-8")
    store = FactStore(root / "facts.db")
    store.initialise()
    c = store.connection
    c.executemany(
        "INSERT INTO documents (id, title, page_type) VALUES (?, ?, ?)",
        [
            (1, "Zed vs Yara", "arc"),
            (2, "Origin of Zed", "comic"),
            (3, "Zed's Relic", "comic"),
            (4, "Dead End", "comic"),
        ],
    )
    c.executemany(
        "INSERT INTO nodes (id, name, document_id, is_resolved) VALUES (?, ?, ?, 1)",
        [
            (1, "Zed vs Yara", 1),
            (2, "Origin of Zed", 2),
            (3, "Zed's Relic", 3),
            (4, "Dead End", 4),
        ],
    )
    c.execute(
        "INSERT INTO sections (id, document_id, title, breadcrumb, ordinal, text)"
        " VALUES (1, 1, 'Plot', 'Zed vs Yara / Plot', 0, ?)",
        (PLOT_SECTION,),
    )
    c.executemany(
        "INSERT INTO facts (node_id, key, value) VALUES (?, ?, ?)",
        [
            (2, "synopsis1", SYNOPSIS_ORIGIN),
            (3, "synopsis2", SYNOPSIS_RELIC),
            (4, "history", "TBD"),
            (4, "trivia", TRIVIA_DEAD_END),
        ],
    )
    c.commit()
    return store


@pytest.fixture()
def factwiki(tmp_path):
    store = _build(tmp_path / "factwiki", OVERRIDES)
    yield store
    store.close()


@pytest.fixture()
def silentwiki(tmp_path):
    store = _build(tmp_path / "silentwiki", SILENT_OVERRIDES)
    yield store
    store.close()


class TestFactScope:
    def test_fact_only_pages_join_all_and_only_all(self, factwiki):
        pages, by_page = scope_plan(factwiki, "all")
        assert "Origin of Zed" in pages
        assert "Zed's Relic" in pages

        # No other rule reaches them: they are in no placement, corpus or
        # prose queue, only the fact scope.
        placement, _ = scope_plan(factwiki, "placement")
        corpus_pages, _ = scope_plan(factwiki, "corpus")
        prose_pages, _ = prose_scope(factwiki)
        for page in ("Origin of Zed", "Zed's Relic"):
            assert page not in placement
            assert page not in corpus_pages
            assert page not in prose_pages

        # The page carries no section: the extractor reads it through the
        # fact passages, in in-value order.
        assert by_page["Origin of Zed"] == []
        passages = build_passages(factwiki, "Origin of Zed", [], "all", None)
        fact_passages = [p for p in passages if p["kind"] == "fact"]
        assert [p["passage"] for p in fact_passages] == ["fact:synopsis1"]
        assert SYNOPSIS_ORIGIN in fact_passages[0]["text"]

    def test_fact_pages_order_densest_first(self, factwiki):
        # The relic page's value is denser (27 words vs 18): it reads first.
        assert fact_pages(factwiki) == ["Zed's Relic", "Origin of Zed"]

    def test_junk_and_excluded_values_never_queue_the_page(self, factwiki):
        pages, _ = scope_plan(factwiki, "all")
        assert "Dead End" not in pages
        assert fact_pages(factwiki) == ["Zed's Relic", "Origin of Zed"]

    def test_scopes_other_than_all_gain_no_fact_pages(self, factwiki):
        for scope in ("placement", "corpus"):
            pages, _ = scope_plan(factwiki, scope)
            assert "Origin of Zed" not in pages


class TestCensus:
    def test_census_reports_declared_and_excluded(self, factwiki):
        rows = {row["key"]: row for row in fact_key_census(factwiki, None)}
        assert rows["synopsis1"]["status"] == "declared"
        assert rows["synopsis2"]["status"] == "declared"
        assert rows["history"]["status"] == "declared"
        # `TBD` holds no panel-eligible sentence: prose 0, nothing to queue.
        assert rows["history"]["prose"] == 0
        assert rows["trivia"]["status"] == "excluded"
        assert rows["trivia"]["reason"] == "trivia, not narrative"
        assert rows["trivia"]["prose"] == 1

    def test_excluded_keys_do_not_enter_the_queue(self, factwiki):
        # The exclusion is counted, not read: no fact passage for `trivia`.
        assert fact_passages(factwiki, "Dead End") == []


class TestSilentWiki:
    def test_no_declaration_is_a_noop(self, silentwiki):
        assert fact_pages(silentwiki) == []
        assert excluded_fact_keys(silentwiki) == []
        assert fact_key_census(silentwiki, None) == []

        pages, _ = scope_plan(silentwiki, "all")
        placement, _ = scope_plan(silentwiki, "placement")
        corpus_pages, _ = scope_plan(silentwiki, "corpus")
        prose_pages, _ = prose_scope(silentwiki)
        # The pre-R10 union, byte-identical: a wiki that declares no fact
        # keys loses nothing and gains nothing.
        assert set(pages) == set(placement) | set(corpus_pages) | set(prose_pages)
        assert "Origin of Zed" not in pages
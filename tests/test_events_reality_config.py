"""R8: reality partitioning is a wiki declaration, not an engine rule.

The architect's finding: the engine must carry the generic resolver only;
a wiki's reality-naming convention (title suffix, the fact that carries it,
how values fold) lives in its `overrides.yaml` `events: reality:` block.
Three tests prove the split:

* a non-Marvel convention -- an `Alt N` title suffix, an `alt` fact key,
  `ALT-N` value folding -- partitions candidates exactly as declared;
* the multi-reality rule's default: a wiki-level `default_reality` reaches
  pages with no signal of their own, only where the overrides declare it;
* a wiki that declares nothing (the mcu/jjk shape) gets no partitioning:
  the same suffixed titles carry no reality and the page reality is None.
"""

from __future__ import annotations

import pytest

from scriptengine.ingest.events import (
    _wiki_default_reality,
    normalize_reality,
    page_reality,
    participant_candidates,
    pick_candidate,
    reality_config,
)
from scriptengine.stores.facts import FactStore

# A convention nothing in the engine knows: an `Alt N` title suffix, an
# `alt` fact key, and values that may carry the prefix in any case.
OVERRIDES = """\
events:
  reality:
    title_pattern: '\\(Alt (\\d+)\\)\\s*$'
    value_patterns:
      - '(?i)^alt[- ]?(\\d+)$'
    fact_key: alt
"""


@pytest.fixture()
def declared(tmp_path):
    """A store whose wiki declares the `Alt` convention."""
    root = tmp_path / "altwiki"
    root.mkdir()
    (root / "overrides.yaml").write_text(OVERRIDES, encoding="utf-8")
    store = FactStore(root / "facts.db")
    store.initialise()
    c = store.connection
    c.executemany(
        "INSERT INTO documents (id, title, page_type) VALUES (?, ?, ?)",
        [(1, "Zed", "character"), (2, "Zed (Alt 7)", "character")],
    )
    c.executemany(
        "INSERT INTO nodes (id, name, document_id, is_resolved) VALUES (?, ?, ?, 1)",
        [(1, "Zed", 1), (2, "Zed (Alt 7)", 2)],
    )
    c.executemany(
        "INSERT INTO facts (node_id, key, value) VALUES (?, ?, ?)",
        # `unknown` folds to None: the base variant; `ALT-7` folds to `7`.
        [(1, "alt", "unknown"), (2, "alt", "ALT-7")],
    )
    # The suffixed variant reaches the bare name's bucket through the alias
    # table, exactly the way `Conan (Earth-16356)` reaches `Conan`.
    c.execute("INSERT INTO aliases (alias, node_id) VALUES ('zed', 2)")
    c.commit()
    yield store
    store.close()


@pytest.fixture()
def silent(tmp_path):
    """The same store with no `reality` block: no partitioning (R8)."""
    root = tmp_path / "plainwiki"
    root.mkdir()
    (root / "overrides.yaml").write_text("events:\n  placement_types: [arc]\n",
                                         encoding="utf-8")
    store = FactStore(root / "facts.db")
    store.initialise()
    c = store.connection
    c.executemany(
        "INSERT INTO documents (id, title, page_type) VALUES (?, ?, ?)",
        [(1, "Zed", "character"), (2, "Zed (Alt 7)", "character")],
    )
    c.executemany(
        "INSERT INTO nodes (id, name, document_id, is_resolved) VALUES (?, ?, ?, 1)",
        [(1, "Zed", 1), (2, "Zed (Alt 7)", 2)],
    )
    c.executemany(
        "INSERT INTO facts (node_id, key, value) VALUES (?, ?, ?)",
        [(1, "alt", "unknown"), (2, "alt", "ALT-7")],
    )
    c.execute("INSERT INTO aliases (alias, node_id) VALUES ('zed', 2)")
    c.commit()
    yield store
    store.close()


OVERRIDES_DEFAULT = """\
events:
  reality:
    title_pattern: '\\(Alt (\\d+)\\)\\s*$'
    value_patterns:
      - '(?i)^alt[- ]?(\\d+)$'
    fact_key: alt
  default_reality: 7
"""


@pytest.fixture()
def defaulted(tmp_path):
    """The `Alt` convention plus a declared wiki-level default reality."""
    root = tmp_path / "defwiki"
    root.mkdir()
    (root / "overrides.yaml").write_text(OVERRIDES_DEFAULT, encoding="utf-8")
    store = FactStore(root / "facts.db")
    store.initialise()
    c = store.connection
    c.executemany(
        "INSERT INTO documents (id, title, page_type) VALUES (?, ?, ?)",
        [(1, "Zed", "character"), (2, "Zed (Alt 7)", "character")],
    )
    c.executemany(
        "INSERT INTO nodes (id, name, document_id, is_resolved) VALUES (?, ?, ?, 1)",
        [(1, "Zed", 1), (2, "Zed (Alt 7)", 2)],
    )
    c.executemany(
        "INSERT INTO facts (node_id, key, value) VALUES (?, ?, ?)",
        [(1, "alt", "unknown"), (2, "alt", "ALT-7")],
    )
    c.execute("INSERT INTO aliases (alias, node_id) VALUES ('zed', 2)")
    c.commit()
    yield store
    store.close()


def test_the_declared_convention_partitions_candidates(declared):
    cfg = reality_config(declared)
    assert cfg["fact_key"] == "alt"
    assert cfg["title_pattern"] is not None
    assert cfg["value_patterns"] and len(cfg["value_patterns"]) == 1

    # Value folding is the wiki's rule: `ALT-7` -> `7`, `unknown` -> None.
    assert normalize_reality("ALT-7", cfg) == "7"
    assert normalize_reality("alt 7", cfg) == "7"
    assert normalize_reality("unknown", cfg) is None

    cands = participant_candidates(declared)
    zed = {c[0]: c[2] for c in cands["zed"]}
    # The suffixed variant carries its title's reality; the base one, whose
    # fact says `unknown`, carries none.
    assert zed == {1: None, 2: "7"}

    # A page in reality `7` resolves to the variant; no page reality falls
    # back to the base.
    assert pick_candidate(cands["zed"], "7") == (2, "Zed (Alt 7)", "7")
    assert pick_candidate(cands["zed"], None) == (1, "Zed", None)


def test_the_declared_convention_reads_the_page_reality(declared):
    # The title's declared pattern, then the wiki's default (undeclared here).
    assert page_reality(declared, "Battle (Alt 7)") == "7"
    assert page_reality(declared, "Battle") is None


def test_a_wiki_that_declares_nothing_gets_no_partitioning(silent):
    cfg = reality_config(silent)
    assert cfg == {}

    cands = participant_candidates(silent)
    # The suffixed title matches no declared pattern and the fact key is
    # undeclared: no candidate carries a reality, and the two variants are
    # an explicit ambiguity -- the wiki's silence, not the engine's guess.
    zed = {c[0]: c[2] for c in cands["zed"]}
    assert zed == {1: None, 2: None}
    assert isinstance(pick_candidate(cands["zed"], None), dict)
    assert page_reality(silent, "Battle (Alt 7)") is None


def test_the_default_reality_reaches_only_declared_wikis(defaulted, silent):
    # The multi-reality rule: a page with no signal of its own takes the
    # wiki's declared default, and the resolver then picks the variant that
    # reality names.
    assert _wiki_default_reality(defaulted) == "7"
    assert page_reality(defaulted, "Battle") == "7"
    cands = participant_candidates(defaulted)
    assert pick_candidate(
        cands["zed"], page_reality(defaulted, "Battle")
    ) == (2, "Zed (Alt 7)", "7")

    # Where the overrides declare no default, the same page stays
    # reality-free: the default is a declaration, not an engine fallback.
    assert _wiki_default_reality(silent) is None
    assert page_reality(silent, "Battle") is None
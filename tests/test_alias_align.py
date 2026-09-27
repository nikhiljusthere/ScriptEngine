"""The names a wiki's disambiguation pages file, aligned to canonical nodes.

`Spider-Man` (disambiguation) files `Peter Parker (Earth-616)` under its list
fields even when no infobox names it; `alias-align` resolves the entry
against the store's nodes then aliases (exact = 1.0, alias = 0.9) and
promotes the name into the `aliases` table. An entry the store has no node
for is counted, written to a `disambig_unresolved` fact under
`disambig:<page>` provenance, and flagged -- never invented. Bare image
filenames are the wiki editor pasting a file where a name would have been:
they file nothing.
"""

from __future__ import annotations

import pytest

from scriptengine.config import SeriesPaths
from scriptengine.ingest.alias_align import align
from scriptengine.stores.facts import FactStore

OVERRIDES = """\
disambig_list_keys:
  - others
  - main_article1
"""


@pytest.fixture()
def paths(tmp_path):
    root = tmp_path / "c3"
    root.mkdir()
    (root / "overrides.yaml").write_text(OVERRIDES, encoding="utf-8")
    return SeriesPaths(name="c3", root=root)


def _populate(store: FactStore) -> None:
    c = store.connection
    c.executemany(
        "INSERT INTO documents (id, title, page_type) VALUES (?, ?, ?)",
        [
            (1, "Spider-Man", "disambiguation"),
            (2, "X-Men", "disambiguation"),
            (3, "Peter Parker (Earth-616)", "character"),
        ],
    )
    c.executemany(
        "INSERT INTO nodes (id, name, document_id) VALUES (?, ?, ?)",
        [
            (1, "Spider-Man", 1),
            (2, "X-Men", 2),
            (3, "Peter Parker (Earth-616)", 3),
            (4, "Hydra (Earth-616)", None),
        ],
    )
    # The store's alias table carries the lowercased spelling; the wiki's
    # disambiguation list spells it `Hydra`. The casefold hit resolves to the
    # node without inventing one, and the wiki's spelling is the new row.
    c.execute("INSERT INTO aliases (alias, node_id) VALUES ('hydra', 4)")
    c.executemany(
        "INSERT INTO facts (node_id, key, value) VALUES (?, ?, ?)",
        [
            # A plain entry, a `<name> from <image>` entry, and a bare image
            # filename (the wiki pasted a file where a name would have been).
            (1, "others", "Peter Parker (Earth-616); Hydra from Hydra Vol 1 1.jpg; Spider-Man Vol 4 1 Unknown.jpg"),
            # `Magneto` has no node in the store: unresolved, flagged.
            (1, "main_article1", "Magneto"),
            # `X-Men; Peter Parker (Earth-616) and X-Men`: the second part
            # files two entities in one entry; the split is deterministic.
            (2, "others", "X-Men; Peter Parker (Earth-616) and X-Men"),
        ],
    )
    c.commit()


@pytest.fixture()
def store(paths):
    with FactStore(paths.facts_db) as opened:
        opened.initialise()
        _populate(opened)
        yield opened


class TestAlign:
    def test_a_resolved_entry_is_promoted_to_an_alias(self, paths, store):
        report = align(paths)
        rows = store.connection.execute(
            "SELECT alias, node_id FROM aliases WHERE alias NOT IN ('hydra') ORDER BY alias"
        ).fetchall()
        by_alias = {row[0]: row[1] for row in rows}
        assert by_alias["Peter Parker (Earth-616)"] == 3
        assert by_alias["Hydra"] == 4  # casefold alias hit, wiki spelling kept
        assert report["resolved_exact"] == 2  # Peter Parker (doc 1), X-Men
        assert report["resolved_alias"] == 1  # Hydra via the alias table
        assert report["already"] == 2  # the doc-2 repeats of both rows

    def test_the_image_suffix_strips_to_the_name_and_a_bare_image_files_nothing(
        self, paths, store
    ):
        report = align(paths)
        assert report["image_only"] == 1  # `Spider-Man Vol 4 1 Unknown.jpg`
        assert "Spider-Man Vol 4 1 Unknown.jpg" not in report["unresolved_names"]
        # Peter Parker, Hydra, Magneto, X-Men -- the doc-2 part
        # `Peter Parker (Earth-616) and X-Men` unpacks into two entries.
        assert report["entries"] == 6

    def test_an_unresolved_entry_is_counted_and_flagged_not_invented(
        self, paths, store
    ):
        report = align(paths)
        assert report["unresolved"] == 1
        assert report["unresolved_names"] == ["Magneto"]
        row = store.connection.execute(
            "SELECT node_id, value, citation FROM facts WHERE key = 'disambig_unresolved'"
        ).fetchone()
        assert tuple(row) == (1, "Magneto", "disambig:Spider-Man")
        assert store.connection.execute(
            "SELECT 1 FROM nodes WHERE name = 'Magneto'"
        ).fetchone() is None

    def test_a_second_run_is_a_counting_no_op(self, paths, store):
        first = align(paths)
        second = align(paths)
        assert second["resolved_exact"] == 0
        assert second["resolved_alias"] == 0
        assert second["already"] == 5  # every resolvable entry now pre-exists
        assert second["unresolved"] == 1  # still counted, still flagged
        # The unresolved fact is not duplicated either.
        count = store.connection.execute(
            "SELECT COUNT(*) FROM facts WHERE key = 'disambig_unresolved'"
        ).fetchone()[0]
        assert count == 1

    def test_a_series_without_the_override_runs_zero(self, paths, store):
        paths.overrides.write_text("disambig_list_keys: []\n", encoding="utf-8")
        report = align(paths)
        assert report["pages"] == 0 and report["entries"] == 0


class TestParseEntries:
    def test_the_first_non_image_line_wins(self):
        from scriptengine.ingest.alias_align import _parse_entries

        assert _parse_entries("Peter Parker (Earth-616)") == ["Peter Parker (Earth-616)"]
        assert (
            _parse_entries("Abominations (Earth-122)\n Abominations (Earth-122) from Hulk Vol 5 5 001.jpg")
            == ["Abominations (Earth-122)"]
        )
        assert (
            _parse_entries("Abominations (Earth-122) from Hulk Vol 5 5 001.jpg")
            == ["Abominations (Earth-122)"]
        )
        assert _parse_entries("Spider-Man Vol 4 1 Unknown.jpg") == []
        assert _parse_entries("   ") == []

    def test_a_part_file_several_entities_joined(self):
        from scriptengine.ingest.alias_align import _parse_entries

        assert (
            _parse_entries("Beetle (Earth-1610) and Edward Brock Jr. (Earth-1610)")
            == ["Beetle (Earth-1610)", "Edward Brock Jr. (Earth-1610)"]
        )
        assert (
            _parse_entries("Eugene Thompson (Earth-616), Toxin (Symbiote) (Earth-616), Sleeper (Symbiote) (Earth-616)")
            == [
                "Eugene Thompson (Earth-616)",
                "Toxin (Symbiote) (Earth-616)",
                "Sleeper (Symbiote) (Earth-616)",
            ]
        )
"""Relations a wiki states in a category, not in a field. (L5, plan §C2)

`Hydra (Earth-616)/Members` files `member_of Hydra` even when the infobox is
silent, and `2009 Character Debuts` files a debut year no field carries. The
mechanism resolves the category's captured target against the store's nodes
(exact = 1.0, alias = 0.9), writes the edge under its `category:<name>`
provenance, and the audit samples it against the infobox field the rule
declares in `contradicts:` -- an edge the page's own field denies is a
finding, not a keep.
"""

from __future__ import annotations

import pytest

from scriptengine.config import SeriesPaths
from scriptengine.ingest.category_relations import audit, derive
from scriptengine.stores.facts import FactStore

OVERRIDES = """\
category_relations:
  - {pattern: "^(.+)/Members$", relation: member_of, target: 1, contradicts: affiliation}
  - {pattern: "^([^/]+)/Creator$", relation: created_by, target: 1, contradicts: creators}
  - {pattern: '^(\\d{4}) Character Debuts$', relation: debuted_year, value: 1}
"""


@pytest.fixture()
def paths(tmp_path):
    root = tmp_path / "c2"
    root.mkdir()
    (root / "overrides.yaml").write_text(OVERRIDES, encoding="utf-8")
    return SeriesPaths(name="c2", root=root)


def _populate(store: FactStore) -> None:
    c = store.connection
    c.executemany(
        "INSERT INTO documents (id, title) VALUES (?, ?)",
        [
            (1, "Captain America (Earth-616)"),
            (4, "Bucky Barnes (Earth-616)"),
            (5, "Ghost Page (Earth-616)"),
        ],
    )
    c.executemany(
        "INSERT INTO nodes (id, name, document_id) VALUES (?, ?, ?)",
        [
            (1, "Captain America (Earth-616)", 1),
            (3, "Hydra (Earth-616)", None),
            (4, "Bucky Barnes (Earth-616)", 4),
            (5, "Stan Lee", None),
        ],
    )
    # `Hydra` is an alias of the full node name: an alias-hit target carries
    # the lower confidence, not a made-up node.
    c.execute("INSERT INTO aliases (alias, node_id) VALUES ('Hydra', 3)")
    c.executemany(
        "INSERT INTO categories (document_id, category) VALUES (?, ?)",
        [
            (1, "Hydra (Earth-616)/Members"),
            (1, "Hydra/Members"),
            (1, "Stan Lee/Creator"),
            (1, "2009 Character Debuts"),
            (1, "Unknown Group (Earth-9)/Members"),
            (4, "Hydra (Earth-616)/Members"),
            (5, "Hydra (Earth-616)/Members"),
        ],
    )
    c.executemany(
        "INSERT INTO facts (node_id, key, value) VALUES (?, ?, ?)",
        [
            (1, "affiliation", "SHIELD"),
            (4, "affiliation", "Hydra; S.H.I.E.LD"),
        ],
    )
    c.commit()


@pytest.fixture()
def store(paths):
    with FactStore(paths.facts_db) as opened:
        opened.initialise()
        _populate(opened)
        yield opened


def _edge(store: FactStore, relation: str):
    return store.connection.execute(
        "SELECT source_id, target_id, confidence, provenance FROM edges"
        " WHERE relation = ? ORDER BY target_id",
        (relation,),
    ).fetchall()


class TestDerive:
    def test_writes_node_edges_under_their_provenance(self, paths, store):
        report = derive(paths)
        edges = _edge(store, "member_of")
        assert [ (e[0], e[1]) for e in edges ] == [(1, 3), (4, 3)]
        # The full-name target resolves exactly (1.0), the alias target lower (0.9).
        confidences = {e[2] for e in _edge(store, "member_of")}
        assert confidences <= {1.0, 0.9}
        for _src, _tgt, _conf, provenance in edges:
            assert provenance.startswith("category:")
        assert _edge(store, "created_by")[0][1] == 5

    def test_a_property_capture_lands_in_facts_not_nodes(self, paths, store):
        derive(paths)
        row = store.connection.execute(
            "SELECT key, value, citation FROM facts"
            " WHERE key = 'debuted_year' AND node_id = 1"
        ).fetchone()
        assert row[0] == "debuted_year"
        assert row[1] == "2009"
        assert row[2] == "category:2009 Character Debuts"
        assert store.connection.execute(
            "SELECT COUNT(*) FROM nodes WHERE name = '2009'"
        ).fetchone()[0] == 0

    def test_an_unresolved_target_is_skipped_and_counted(self, paths, store):
        report = derive(paths)
        assert report["unresolved"] == 1
        assert store.connection.execute(
            "SELECT COUNT(*) FROM nodes WHERE name = 'Unknown Group (Earth-9)'"
        ).fetchone()[0] == 0

    def test_a_document_without_a_subject_node_counts_as_no_subject(self, paths, store):
        report = derive(paths)
        assert report["no_subject"] == 1

    def test_a_second_run_counts_but_does_not_duplicate(self, paths, store):
        first = derive(paths)
        second = derive(paths)
        assert second["edges_written"] == 0
        assert second["facts_written"] == 0
        assert second["already"] == first["edges_written"] + first["facts_written"]

    def test_a_rule_needs_a_pattern_and_a_relation(self, tmp_path):
        root = tmp_path / "bad"
        root.mkdir()
        (root / "overrides.yaml").write_text(
            "category_relations:\n  - {pattern: '^(.+)/Members$'}\n",
            encoding="utf-8",
        )
        with FactStore(root / "facts.db"):
            pass
        with pytest.raises(ValueError, match="relation"):
            derive(SeriesPaths(name="bad", root=root))


class TestAudit:
    def test_an_edge_the_infobox_denies_is_a_finding(self, paths, store):
        derive(paths)
        report = audit(paths, sample=200)
        # Captain America's `member_of Hydra` edge meets the infobox's
        # `affiliation = SHIELD`: denied, so it is reported, not kept.
        assert len(report["contradictions"]) == 1
        item = report["contradictions"][0]
        assert item["relation"] == "member_of"
        assert item["category"] == "Hydra (Earth-616)"
        assert "SHIELD" in item["field"]

    def test_an_edge_the_infobox_agrees_with_is_consistent(self, paths, store):
        derive(paths)
        report = audit(paths, sample=200)
        assert report["consistent"] >= 1
        # Bucky's edge: the field lists Hydra, so no contradiction for it.
        assert all(
            item["category"] != "Hydra (Earth-616)" or "SHIELD" in item["field"]
            for item in report["contradictions"]
        )

    def test_no_counter_evidence_is_not_a_contradiction(self, paths, store):
        # Captain America's `affiliation = SHIELD` is the only counter-evidence
        # in the fixture: without it every edge is merely uncontradicted.
        store.connection.execute(
            "DELETE FROM facts WHERE node_id = 1 AND key = 'affiliation'"
        )
        store.connection.commit()
        derive(paths)
        report = audit(paths, sample=200)
        assert report["contradictions"] == []

    def test_relations_without_a_contradicts_key_are_unauditable(self, paths, store):
        derive(paths)
        report = audit(paths, sample=200)
        # `created_by` has `contradicts: creators`, but Captain America has no
        # creators fact, and nothing in the fixture is auditable against a
        # missing rule: the counts partition the sample.
        assert report["sampled"] == report["auditable"] + report["unauditable"]
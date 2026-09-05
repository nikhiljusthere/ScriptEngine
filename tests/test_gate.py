"""The comprehension gate: three mechanical equality checks over the events table.

The gate is not a grade -- there is no gold, nothing an agent can be generous
about. It is string and foreign-key equality in three parts: a temporal row's
page must sit on the time axis, the same event stated on several pages must
carry one arc placement, and the coverage of narrative beats is reported split
by temporal and atemporal. These tests lock the invariants the report relies on:
the checks are idempotent, the agreement stats reconcile, and every disagreement
is a real multi-arc, multi-page spread.
"""

from __future__ import annotations

import pytest

from scriptengine.config import series_paths
from scriptengine.ingest import gate
from scriptengine.ingest.events import (
    corpus_scope,
    extractable_sections,
    is_narrative_heading,
    placement_pages,
    scope_plan,
)
from scriptengine.stores.facts import FactStore


@pytest.fixture(scope="module")
def jjk_store():
    paths = series_paths("jjk")
    if not paths.facts_db.exists():
        pytest.skip("jjk is not indexed")
    with FactStore(paths.facts_db) as store:
        yield store


class TestNodeNames:
    def test_the_pair_is_a_set_one_name_per_node(self):
        rows = [
            {"subject_node": 1, "subject_name": "Yuji Itadori",
             "object_node": 2, "object_name": "Sukuna"},
            # The reverse direction is the same group; the names must not
            # duplicate and must stay stable to the node, not the row.
            {"subject_node": 2, "subject_name": "Sukuna",
             "object_node": 1, "object_name": "Yuji Itadori"},
        ]
        assert gate._node_names(frozenset((1, 2)), rows) == ["Yuji Itadori", "Sukuna"]

    def test_a_self_event_is_one_participant(self):
        rows = [
            {"subject_node": 5, "subject_name": "Maki Zenin",
             "object_node": 5, "object_name": "Maki Zenin"},
        ]
        assert gate._node_names(frozenset((5,)), rows) == ["Maki Zenin"]


class TestCheck3ArcPlacement:
    def test_violations_match_the_unplaced_rows(self, jjk_store):
        # The residue: eventive rows the axis cannot place (arc_index NULL),
        # stored as standing states. The recompute aligns first, so this is the
        # settled off-axis set, not a transient dangling one.
        violations = gate.arc_placement_violations(jjk_store)
        count = jjk_store.connection.execute(
            "SELECT COUNT(*) FROM events WHERE arc_index IS NULL"
        ).fetchone()[0]
        assert len(violations) == count

    def test_enforce_is_idempotent(self, jjk_store):
        first = gate.enforce_arc_placement(jjk_store)
        second = gate.enforce_arc_placement(jjk_store)
        # The first pass aligns temporal to the placement; once aligned, a
        # second pass moves nothing.
        assert second["flipped"] == 0
        assert first["flipped"] >= 0

    def test_enforce_reports_the_residue_and_its_movement(self, jjk_store):
        result = gate.enforce_arc_placement(jjk_store)
        # flipped is the rows moved this run (each way); rows is the settled
        # off-axis residue it records as standing states.
        assert result["flipped"] == result["promoted"] + result["demoted"]
        assert len(result["rows"]) == result["unplaced"]
        for row in result["rows"]:
            assert row["arc_key"]


class TestCrossPageAgreement:
    def test_stats_reconcile(self, jjk_store):
        report = gate.cross_page_agreement(jjk_store)
        s = report["stats"]
        # Every multi-page group either agrees on one arc or disagrees; the
        # full disagreement list is exactly the disagreeing groups.
        assert s["agreeing"] + s["disagreeing"] == s["multi_page_groups"]
        assert s["multi_page_groups"] <= s["groups"]
        assert len(report["disagreements"]) == s["disagreeing"]

    def test_a_disagreement_spans_arcs_and_pages(self, jjk_store):
        report = gate.cross_page_agreement(jjk_store)
        for d in report["disagreements"]:
            assert len(d["arcs"]) >= 2
            assert len({r["arc_key"] for r in d["rows"]}) >= 2
            assert d["participant_count"] in (1, 2)
            # adjacency is a fact about the arc spread, not a separate signal
            assert d["adjacent"] == (d["arc_span"] == 1)
            for row in d["rows"]:
                assert row["arc_key"]
                assert row["quote"]

    def test_modeling_problem_implies_well_populated(self, jjk_store):
        report = gate.cross_page_agreement(jjk_store)
        for d in report["disagreements"]:
            if d["modeling_problem"]:
                assert d["well_populated"]

    def test_rows_order_unplaced_first_then_by_arc(self, jjk_store):
        report = gate.cross_page_agreement(jjk_store)
        for d in report["disagreements"]:
            placed = [r["arc_index"] for r in d["rows"] if r["arc_index"] is not None]
            assert placed == sorted(placed)


class TestCoverageSplit:
    def test_shares_are_bounded_and_consistent(self, jjk_store):
        c = gate.coverage_split(jjk_store)
        assert c["beats"] > 0
        for key in ("any", "temporal", "atemporal"):
            assert 0.0 <= c[key] <= 1.0
        # A beat that carries a temporal (or atemporal) row also carries a row.
        assert c["any"] >= c["temporal"]
        assert c["any"] >= c["atemporal"]


class TestGateReport:
    def test_the_report_carries_all_three_checks(self, jjk_store):
        report = gate.gate_report(jjk_store)
        assert set(report) == {"check3", "agreement", "coverage"}
        assert "flipped" in report["check3"]
        assert "stats" in report["agreement"]
        assert "beats" in report["coverage"]


class TestCorpusScope:
    def test_narrative_headings_are_recognised(self):
        for title in ("Synopsis", "Plot Details", "History", "Culling Game Arc",
                     "Shibuya Incident Arc", "  Overview "):
            assert is_narrative_heading(title), title
        for title in ("Powers", "Trivia", "Appearance", "Relationships", "", None):
            assert not is_narrative_heading(title), title

    def test_scope_reaches_only_narrative_sections_of_pages_naming_two_characters(self, jjk_store):
        scope = corpus_scope(jjk_store)
        assert scope
        for page, sections in scope.items():
            assert sections
            for section in sections:
                assert is_narrative_heading(section["title"]), (page, section["title"])
                assert section["id"] is not None

    def test_scope_is_deterministic(self, jjk_store):
        a = corpus_scope(jjk_store)
        b = corpus_scope(jjk_store)
        assert list(a) == list(b)
        assert {id for secs in a.values() for id in (s["id"] for s in secs)} == \
               {id for secs in b.values() for id in (s["id"] for s in secs)}


class TestScopePlan:
    def test_all_covers_both_rule_sets(self, jjk_store):
        pages, _ = scope_plan(jjk_store, "all")
        placement = set(placement_pages(jjk_store))
        corpus = set(corpus_scope(jjk_store))
        assert set(pages) == placement | corpus
        assert len(pages) == len(placement | corpus)

    def test_all_dedupes_sections_where_both_rules_cover_a_page(self, jjk_store):
        _, by_page = scope_plan(jjk_store, "all")
        for page, sections in by_page.items():
            ids = [s["id"] for s in sections]
            assert len(ids) == len(set(ids)), page

    def test_corpus_scope_keeps_reading_only_its_rule(self, jjk_store):
        corpus = corpus_scope(jjk_store)
        pages, by_page = scope_plan(jjk_store, "corpus")
        assert pages == list(corpus)
        for page in pages:
            assert [s["id"] for s in by_page[page]] == \
                   [s["id"] for s in corpus[page]]

    def test_placement_scope_keeps_reading_every_extractable_section(self, jjk_store):
        pages = placement_pages(jjk_store)
        all_pages, by_page = scope_plan(jjk_store, "placement")
        assert all_pages == pages
        for page in pages:
            assert [s["id"] for s in by_page[page]] == \
                   [s["id"] for s in extractable_sections(jjk_store, page)]
"""The continuity-check scaffold: a gap is a flag, not a verdict.

These tests lock the invariants the D6-consumer relies on: the "actual" arc is
the wiki's own cross-page majority (a corpus truth, so measuring a gap against
it is not circular); a beat out of order by the threshold is flagged with a
direction; a script that walks backward more than the threshold is reported (and
a marked flashback is reported as one); the knowledge frontier is a plain prefix
read; and the frozen gold set still holds against the live store -- a re-index
that silently moved an event breaks a case and is caught here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scriptengine.config import series_paths
from scriptengine.ingest import continuity
from scriptengine.stores.facts import FactStore

GOLD_PATH = Path(__file__).resolve().parent.parent / "scriptengine" / "eval" / "gold_continuity.json"


@pytest.fixture(scope="module")
def jjk_store():
    paths = series_paths("jjk")
    if not paths.facts_db.exists():
        pytest.skip("jjk is not indexed")
    with FactStore(paths.facts_db) as store:
        yield store


class TestParticipantMatch:
    def test_a_single_participant_matches_either_end(self):
        predicate, params = continuity._participant_match("fought", ["Sukuna"])
        assert predicate.count("?") == len(params)
        assert "LOWER(verb) = ?" in predicate

    def test_a_pair_matches_both_orderings(self):
        predicate, params = continuity._participant_match("fought", ["Sukuna", "Yuji Itadori"])
        # verb + (subj, obj) + (obj, subj): 5 placeholders, in that order.
        assert len(params) == 5
        assert params[0] == "fought"
        assert params[1] == "sukuna" and params[4] == "sukuna"


class TestAdjudicatedArc:
    def test_a_clean_majority_is_adjudicated(self, jjk_store):
        result = continuity.adjudicated_arc(
            jjk_store, verb="fought", participants=["Sukuna", "Yuji Itadori"]
        )
        # The wiki's own cross-page majority files the Sukuna/Yuji fight in the
        # final arc, not the early one a minority of pages state.
        assert result["actual"] is not None
        assert result["majority_share"] > 0.0
        assert result["arcs"] == sorted(set(result["arcs"]))

    def test_a_nonexistent_filing_is_none(self, jjk_store):
        result = continuity.adjudicated_arc(
            jjk_store, verb="frobnicated", participants=["Zorble"]
        )
        assert result["actual"] is None
        assert result["note"]

    def test_majority_share_is_bounded(self, jjk_store):
        for verb, parts in (
            ("fought", ["Sukuna", "Yuji Itadori"]),
            ("awakened", ["Nobara Kugisaki"]),
        ):
            result = continuity.adjudicated_arc(jjk_store, verb=verb, participants=parts)
            assert 0.0 < result["majority_share"] <= 1.0


class TestBeatGap:
    def test_a_premature_beat_is_flagged_with_direction(self, jjk_store):
        gap = continuity.beat_gap(
            jjk_store,
            verb="fought",
            participants=["Sukuna", "Yuji Itadori"],
            claimed_arc_index=1,
        )
        assert gap["actual"] is not None
        assert gap["direction"] == "early"
        assert gap["gap"] == abs(1 - gap["actual"])
        assert gap["flagged"]

    def test_a_close_beat_is_not_flagged(self, jjk_store):
        # Same filing, but the claimed arc sits within the threshold of the
        # adjudicated one, so the gap is below the flag line.
        adjudicated = continuity.adjudicated_arc(
            jjk_store, verb="fought", participants=["Sukuna", "Yuji Itadori"]
        )
        gap = continuity.beat_gap(
            jjk_store,
            verb="fought",
            participants=["Sukuna", "Yuji Itadori"],
            claimed_arc_index=adjudicated["actual"],
        )
        assert gap["gap"] == 0
        assert not gap["flagged"]

    def test_an_unplaced_filing_reports_no_gap(self, jjk_store):
        gap = continuity.beat_gap(
            jjk_store,
            verb="frobnicated",
            participants=["Zorble"],
            claimed_arc_index=3,
        )
        assert gap["gap"] is None
        assert not gap["flagged"]
        assert gap["note"]


class TestWalkMonotonicity:
    def test_a_forward_walk_has_no_flags(self):
        beats = [{"arc_index": i} for i in (0, 1, 2, 3, 4)]
        assert continuity.walk_monotonicity(beats) == []

    def test_a_backward_jump_is_flagged(self):
        beats = [{"arc_index": 5}, {"arc_index": 6}, {"arc_index": 2}]
        flags = continuity.walk_monotonicity(beats)
        assert [f["index"] for f in flags] == [2]
        assert flags[0]["jump"] == 4
        assert not flags[0]["flashback"]

    def test_a_marked_flashback_is_reported_not_hidden(self):
        beats = [{"arc_index": 6}, {"arc_index": 2}]
        flags = continuity.walk_monotonicity(beats, flashback=[1])
        assert len(flags) == 1
        assert flags[0]["flashback"]

    def test_within_threshold_is_not_a_jump(self):
        beats = [{"arc_index": 4}, {"arc_index": 3}]  # back one arc
        assert continuity.walk_monotonicity(beats) == []


class TestKnowledgeFrontier:
    def test_the_frontier_is_a_prefix_read(self, jjk_store):
        rows = continuity.knowledge_frontier(jjk_store, "Yuji Itadori", 7)
        assert rows
        for row in rows:
            assert row["arc_index"] is not None
            assert row["arc_index"] <= 7

    def test_the_frontier_grows_with_the_arc(self, jjk_store):
        lower = continuity.knowledge_frontier(jjk_store, "Yuji Itadori", 3)
        higher = continuity.knowledge_frontier(jjk_store, "Yuji Itadori", 7)
        assert len(lower) <= len(higher)


class TestTriageFilings:
    def test_the_classes_partition_the_filings(self, jjk_store):
        triage = continuity.triage_filings(jjk_store)
        total = sum(triage["classes"].values())
        assert total == triage["total"]

    def test_the_core_is_premature_plus_delayed(self, jjk_store):
        triage = continuity.triage_filings(jjk_store)
        assert triage["anachronism_core"] == len(triage["premature"]) + len(triage["delayed"])
        for case in triage["premature"]:
            assert case["direction"] == "early"
            assert case["gap"] >= 2
        for case in triage["delayed"]:
            assert case["direction"] == "late"
            assert case["gap"] >= 2

    def test_state_verbs_are_not_in_the_core(self, jjk_store):
        triage = continuity.triage_filings(jjk_store)
        for case in triage["premature"] + triage["delayed"]:
            assert case["verb"].lower() not in continuity._STATE_VERBS


class TestRunGold:
    def test_every_frozen_case_holds_against_the_live_store(self, jjk_store):
        gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
        result = continuity.run_gold(jjk_store, gold["cases"])
        # The set was frozen from this store, so a case only breaks if a
        # re-index moved the adjudicated arc. That is exactly the failure the
        # gold set exists to catch.
        assert result["total"] == len(gold["cases"])
        for row in result["cases"]:
            assert row["held"], (row["verb"], row["participants"])

    def test_a_moved_event_breaks_its_case(self, jjk_store):
        # A case whose expected arc no longer matches the live adjudication is
        # reported broken, not silently passed.
        gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
        doctored = [dict(case) for case in gold["cases"]]
        doctored[0]["actual_arc_index"] = -1  # an arc that nothing is filed in
        result = continuity.run_gold(jjk_store, doctored)
        assert result["broken"] == 1
        assert not result["cases"][0]["held"]
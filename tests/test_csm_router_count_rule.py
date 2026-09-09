"""G-CSM-1 (red list R-1): a count phrasing about a declared roster must reach
the roster door, however the set name is wrapped.

The door itself serves the csm sets correctly in declared mode
(`reports/csm/GCSM1_ROSTER_DOOR.md`: 5/5 and 4/4) -- the debt was the routing.
Two shapes kept the count phrasings on `qa` while the door sat unused:

* the set name inside the prepositional phrase -- "members are in the Four
  Horsemen" -- which the router's G1 scope strip removed before the declared
  phrase could match (csm-set-15; the same shape on db "across the
  multiverse");
* the count phrasing's own `many` surviving into the constraint parse as a
  qualifier nothing could be checked against (`__unverified__'many'` ->
  partial), which the R1-d counting gate then refused (csm-set-14).

The fix is in `router._resolves_a_set` (the counting probe) and is gated on
the series' own declared rosters: a wiki that declares none resolves no set
for a counting topic, so the rule cannot fire there. The JJK/OPM pins below
are the JJK-100% invariance check at router level (the four standing gates
re-run at gate time).
"""

from __future__ import annotations

import pytest

from scriptengine.retrieve.router import route


class TestCsmCountRule:
    """csm-set-14 / csm-set-15: the bank's two count phrasings, verbatim."""

    @pytest.mark.parametrize(
        "query",
        [
            # csm-set-14: the set name is the prepositional object, and the
            # shorter declared phrase leaves "exist" / "Hunters" behind.
            "How many special divisions exist in Public Safety Devil Hunters?",
            # csm-set-15: "in the Four Horsemen" used to be scope-stripped
            # before any declared phrase could match.
            "How many members are in the Four Horsemen?",
        ],
    )
    def test_count_phrasings_reach_the_roster_door(self, query):
        from scriptengine.config import series_paths

        paths = series_paths("csm")
        if not paths.facts_db.exists():
            pytest.skip("csm is not indexed")
        chosen = route(paths, query)
        assert chosen.mode == "roster"
        assert chosen.signals["counting"] is True

    def test_the_door_still_serves_the_declared_members(self):
        """Routing is half the fix; the half it routes to must actually
        render the declared set (the GCSM1 door receipt's 5/5 and 4/4).
        Membership, not order: member order is a render concern
        (`_member_order`), not the door's contract."""
        from scriptengine.config import series_paths
        from scriptengine.retrieve.roster import build_roster

        paths = series_paths("csm")
        if not paths.facts_db.exists():
            pytest.skip("csm is not indexed")
        roster = build_roster(
            paths, "How many special divisions exist in Public Safety Devil Hunters?"
        )
        assert {m.name for m in roster.members} == {
            "Tokyo Special Division 1",
            "Tokyo Special Division 4",
            "Tokyo Special Division 5",
            "Tokyo Special Division 6",
            "Tokyo Special Division 7",
        }
        horsemen = build_roster(paths, "How many members are in the Four Horsemen?")
        assert {m.name for m in horsemen.members} == {
            "Control Devil",
            "War Devil",
            "Famine Devil",
            "Death Devil",
        }


class TestCountRuleIsGatedOnDeclaredRosters:
    """A series without declared rosters has nothing for the rule to fire on,
    and a count the wiki holds no set for is still a number in prose."""

    def test_a_series_without_rosters_is_unaffected(self, tmp_path):
        """No `rosters:` in overrides and no store: the counting probe
        resolves no set, the question falls through rule 3 to `qa`, and
        routing never raises (the existing `test_routing_never_raises`
        shape, on the counting path)."""
        from scriptengine.config import SeriesPaths

        paths = SeriesPaths(name="no-rosters", root=tmp_path / "no-rosters")
        chosen = route(
            paths, "How many special divisions exist in Public Safety Devil Hunters?"
        )
        assert chosen.mode == "qa"
        assert chosen.signals["counting"] is True

    @pytest.mark.parametrize(
        "series,query",
        [
            # The docstring case: a number in prose, no set behind it.
            ("jjk", "How many wards did Kenjaku's chain reaction compromise?"),
        ],
    )
    def test_a_count_with_no_set_stays_a_prose_lookup(self, series, query):
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        assert route(paths, query).mode == "qa"


class TestCountRuleLeavesOtherSeriesUnchanged:
    """JJK-100% invariance at router level. The R1-d guard: a count of a
    SUBSET of a set ("...used to trap") reads the number out of prose, and the
    count of the whole set keeps its roster route."""

    def test_a_subset_count_stays_a_prose_lookup(self):
        """The R1-d pin (`test_a_matched_partial_roster_is_not_a_set`): the
        qualifier the set cannot check keeps the question on `qa`."""
        from scriptengine.config import series_paths

        paths = series_paths("jjk")
        if not paths.facts_db.exists():
            pytest.skip("jjk is not indexed")
        assert (
            route(paths, "How many of Suguru Geto's named techniques are used to trap?")
            .mode
            != "roster"
        )

    @pytest.mark.parametrize(
        "series,query",
        [
            # The full-set count keeps its roster route (the R1-d pin's twin).
            ("jjk", "How many named techniques does Suguru Geto have?"),
            # hxh's declared `Nen Types` groups roster: the wiki's six aura
            # types asked with another word for them (2026-08-19 widening).
            ("hxh", "How many levels of Nen are there?"),
            # The "in the X" / "across the multiverse" shapes on other wikis:
            # the declared set is served, which is the fix's whole point, and
            # the two that already reached the door must not move.
            ("db", "How many Gods of Destruction exist across the multiverse?"),
            # csm council R-1 (chairman, 2026-09-09): the second csm delta - the
            # declared set covers the "in Tokyo" scope, so the flip is positive.
            ("csm", "How many special divisions are in Tokyo?"),
            ("opm", "How many hero classes are in the Hero Association in One Punch Man?"),
            (
                "onepiece",
                "How many Sweet Commanders are in the Big Mom Pirates in One Piece?",
            ),
        ],
    )
    def test_genuine_counts_keep_their_roster_route(self, series, query):
        from scriptengine.config import series_paths

        paths = series_paths(series)
        if not paths.facts_db.exists():
            pytest.skip(f"{series} is not indexed")
        assert route(paths, query).mode == "roster"


class TestCouncilR1BlastRadiusPins:
    """Council R-1 (chairman, 2026-09-09): the fix's discovery-side blast
    radius, pinned so it is a documented residual instead of a silent delta.
    The kept prepositional phrase also completes *discovered* set names - a
    mechanical name-guard was verified infeasible without breaking the Geto
    and hxh pins (basis shapes: non-contiguous word order / synonym), so the
    accepted cases are pinned as roster and tripwired by the gate-4
    pre-registration in `reports/csm/receipts/iter1_r1_router_run.md`."""

    def test_opm_blizzard_count_documents_the_gate4_delta(self):
        """opm-set-16 verbatim (`questions/opm.json:1785`, gold `qa` / canon
        38): post-fix the routing serves the discovered 9-member "The Blizzard
        Group" set. If canon-run opm drops 236/236 on this row only, the
        pre-registered ruling is the gold-shape decision (restore the set
        shape, or re-baseline with a record) - never 'log and move on'."""
        from scriptengine.config import series_paths

        paths = series_paths("opm")
        if not paths.facts_db.exists():
            pytest.skip("opm is not indexed")
        assert (
            route(paths, "How many members are in the Blizzard Group in One Punch Man?").mode
            == "roster"
        )

    def test_onepiece_marines_count_pins_the_discovery_side_residual(self):
        """Accepted wrong-set serving: the kept "in the Marines" phrase
        completes the DISCOVERED "Marine Commanders" set (not the asked set).
        Pinned so a future guard or re-route must consciously move it - the
        stamp row in `reports/csm/miss_queue_csm_iter1.jsonl` carries the
        zero-new-miss pass criterion."""
        from scriptengine.config import series_paths

        paths = series_paths("onepiece")
        if not paths.facts_db.exists():
            pytest.skip("onepiece is not indexed")
        assert (
            route(paths, "How many Sweet Commanders are in the Marines?").mode == "roster"
        )
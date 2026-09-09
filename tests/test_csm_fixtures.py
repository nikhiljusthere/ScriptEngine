"""CSM 5.3 pilot fixtures (CSM 100% campaign, Wave-2 CSM-5 remainder unit).

Plan §5.3: "G1–G30 transfers free" was asserted, never tested — the regression
suite is guarded almost entirely by JJK fixtures, and CSM's closure-loop fixes
exercise CSM code paths that have no CSM-shaped coverage. The CSM-5 unit adds
one CSM-shaped fixture per code path the CSM fixes actually exercise.

JJK-100% invariant: CSM work lands in CSM-centric files only, so these live in
this file, parameterized on the CSM store (`series_paths("csm")`) — never a
change to a JJK test file or baseline.

Zero GPU: every fixture here is model-free (router mode selection + SQL store
reads). The bundle-level G-CSM-2 check (the qa passage leg returning nothing)
needs the model and is deferred to the orchestrator's model window / closure
loop; this file guards its *store-level* precondition instead (the subject's
own passage floor is intact), and the pre-registered expected failure is the
red list (`reports/csm/red_list_csm.md`).

The CSM-3b roster-door fix (served_text flattens members/passages) is already
guarded by `tests/test_span_recall.py::test_roster_shaped_bundle_hits_and_
counts_member_names` — recorded in `reports/csm/CSM5_REMAINDER.md`, not
duplicated here.
"""

from __future__ import annotations

import pytest

from scriptengine.config import series_paths
from scriptengine.retrieve.router import route
from scriptengine.stores.facts import FactStore


def _csm_paths():
    paths = series_paths("csm")
    if not paths.facts_db.exists():
        pytest.skip("csm is not indexed")
    return paths


class TestGCSM1CountPhrasingsReachTheRosterDoor:
    """G-CSM-1 — count phrasings bypass the declared-roster door.

    The router sends both of the seed bank's count questions to `qa` (the
    subject resolves to an entity / organization), where the bundle carries 0
    members, so `csm-set-14` (0/5) and `csm-set-15` (0/4) sit at recall 0. The
    roster door itself answers both correctly in declared mode — the members
    (the Public Safety special divisions, the Four Horsemen) are declared in
    `series/csm/overrides.yaml` and the Four Horsemen have *pageless* members
    (Control/Death/Famine/War Devils carry no pages of their own), so the door
    must serve them in declared mode, not by walking a page.

    Fix belongs to CSM-3's door work (the router's count rule). Until it lands
    these assertions are the debt: marked xfail so the suite states G-CSM-1.
    The marker (and this class) comes out when the fix makes them pass.
    """

    @pytest.mark.parametrize(
        "query",
        [
            "How many special divisions exist in Public Safety Devil Hunters?",
            "How many members are in the Four Horsemen?",
        ],
    )
    @pytest.mark.xfail(
        strict=False,
        reason="G-CSM-1: the router routes count phrasings to `qa` (0 members) "
               "instead of the declared-roster door; fix is CSM-3's door work. "
               "Non-strict so closing the gap (xpass) does not break the gate.",
    )
    def test_a_count_phrasing_wants_the_declared_roster(self, query):
        paths = _csm_paths()
        mode = route(paths, query).mode
        assert mode == "roster", f"{query!r} routed to {mode!r}, wants the roster door"


class TestGCSM2SubjectPassageFloorIsIntact:
    """G-CSM-2 — the qa passage leg returns nothing on CSM for subject-named
    questions; the store-level precondition is what this guards.

    "What is Denji's hybrid transformation trigger?" returned 0 passages even
    with an explicit `subject: "Denji"`; the bundle was answered by the
    facts + relations channels alone, so facts documented only in prose (the
    Denji trigger, Makima's PM contract) were unreachable. COUNCIL_csm-1b-2
    ruled the gap is the qa passage / retrieval leg, *not* an extraction-prompt
    fix. The bundle leg is model-bound (deferred to the closure loop); what is
    model-free and testable here is its precondition: the subject's *own* page
    carries the prose passages the floor should walk. If that floor is empty or
    led by another document, the debt is deeper than the budget/ranking leg.
    """

    @pytest.mark.parametrize(
        "question,subject",
        [
            ("What is Denji's hybrid transformation trigger?", "Denji"),
            ("What is Makima's contract with the Prime Minister?", "Makima"),
        ],
    )
    def test_the_subjects_own_page_leads_its_passage_floor(self, question, subject):
        paths = _csm_paths()
        with FactStore(paths.facts_db) as store:
            floor = store.passages_for_subject(subject)
        assert floor, f"no passage floor for {subject!r} — the qa leg has nothing to walk"
        # the floor is keyed to the subject's own page (its title or a /subpage),
        # not an unrelated document that merely mentions the subject.
        own = [p for p in floor
               if p["doc_title"] == subject or p["doc_title"].startswith(subject + "/")]
        assert own, f"the passage floor for {subject!r} is led by other documents"

    def test_the_floor_carries_the_pages_own_lead_card(self):
        """csm-fact-06 / red-list R-2: the debt line is in the subject's lead.

        \"What is Denji's hybrid transformation trigger?\" returned 0 passages
        with an explicit subject, because the trigger (\"pulling a cord on his
        chest\") is documented only in Denji's level-0 document card -- the
        title/facts/lead chunk -- and the floor was level-2 only, while the
        lexical and graph legs are level-2 too, so the card was structurally
        unreachable for a subject-named qa question. The card is now part of
        the floor; this guards that the exact debt line is structurally
        reachable from it (model-free; the bundle leg is the model-bound half
        of the closure loop)."""
        paths = _csm_paths()
        with FactStore(paths.facts_db) as store:
            floor = store.passages_for_subject("Denji")
        cards = [p for p in floor if p["level"] == 0]
        assert cards, "the subject's own lead (the level-0 document card) is not in the floor"
        assert cards[0]["breadcrumb"] == "Denji", "the card is the subject page's own lead"
        assert any("pulling a cord" in p["text"] for p in cards), (
            "the G-CSM-2 debt line (Denji's trigger, documented only in the "
            "lead) is not in the subject floor"
        )


class TestGCSM1RosterDoorServesPagelessMembers:
    """The declared-roster door must serve members that have no page of their
    own (the Four Horsemen: Control/Death/Famine/War Devils are declared in
    `series/csm/overrides.yaml` but carry no articles), in declared mode — the
    raw receipt is `reports/csm/GCSM1_ROSTER_DOOR.md`. This is model-free
    (offline store resolution) and states the door half of G-CSM-1 that is
    *not* the router's job: even once the router routes the count to the door,
    the door must still return the pageless set."""

    def test_the_four_horsemen_roster_is_declared_with_pageless_members(self):
        paths = _csm_paths()
        from scriptengine.retrieve.roster import build_roster
        from scriptengine.config import get_settings

        roster = build_roster(paths, "How many members are in the Four Horsemen?",
                              get_settings())
        names = {m.name for m in roster.members}
        assert names == {"Control Devil", "Death Devil", "Famine Devil", "War Devil"}
        # declared mode: the set comes from the wiki's own declaration, not a page walk
        assert roster.kind == "declared"
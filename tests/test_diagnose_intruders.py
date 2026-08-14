"""The intruder diagnosis has to agree with the precision it explains.

`diagnose_misses.py` buckets what did not come back; this is the mirror for what
came back and should not have. Its numbers appear in the report beside the
precision figure, so the arithmetic below is not an implementation detail: if
the two disagree, the remediation table points at the wrong fix.
"""

from __future__ import annotations

from scriptengine.eval import canon_report
from scriptengine.eval.canon_gold import norm
from scriptengine.eval.diagnose_intruders import _matched_keys, is_lead_row


def _precision_denominator(canon, members):
    """Intruders, the way the report computes them."""
    matched = _matched_keys(canon, members)
    return [m for m in members if norm(m) not in matched]


def test_matched_keys_agrees_with_the_precision_numerator():
    canon = [("Perfect Cell", ["perfect form"]), ("Larva", [])]
    members = ["Perfect Form", "Larva", "Kamehameha"]
    matched = _matched_keys(canon, members)
    assert len(matched) == 2
    assert _precision_denominator(canon, members) == ["Kamehameha"]


def test_one_canon_item_claims_only_one_member():
    """Two spellings of the same form are one hit and one intruder.

    This is `score_sets`'s rule, not a choice made here: an item takes the
    *first* alias it finds, so a set returning both "Imperfect Form" and
    "Imperfect Cell" scores 1/2 rather than 2/2. Reproducing it is what makes
    the intruder count the exact complement of the precision numerator -- and
    surfacing that second name is the point, because it is a bank problem
    rather than an engine one.
    """
    canon = [("Imperfect Cell", ["imperfect form"])]
    members = ["Imperfect Cell", "Imperfect Form"]
    assert len(_matched_keys(canon, members)) == 1
    assert _precision_denominator(canon, members) == ["Imperfect Form"]


def test_an_unmatched_canon_item_contributes_no_key():
    canon = [("Semi-Perfect Cell", []), ("Larva", [])]
    members = ["Larva", "Cellin"]
    assert _matched_keys(canon, members) == {norm("Larva")}
    assert _precision_denominator(canon, members) == ["Cellin"]


def test_lead_rows_are_the_page_title_not_a_shallow_breadcrumb():
    """Depth is a property of the wiki; the lead is a property of the page.

    One-Punch Man nests (`Abilities and Powers / Human / Fighting Style`) and
    Dragon Ball does not (`Abilities`). Asking "does the breadcrumb contain a
    `/`" therefore called every Dragon Ball row lead-level, which inflated the
    run's lead-row count from 45 to 259 and would have sent Phase 1 after a
    filter five times larger than the one that exists.
    """
    assert is_lead_row("Garou", "Garou")
    assert is_lead_row("", "Cell")
    assert not is_lead_row("Abilities", "Cell")
    assert not is_lead_row("Power", "Cell")
    assert not is_lead_row("Abilities and Powers / Human / Fighting Style", "Garou")


def test_report_renders_the_intruder_section_and_survives_without_it():
    scores = {"summary": {}, "rows": [], "facts": []}
    meta = {"run_id": "test", "series": ["opm"]}
    intruders = {
        "buckets": {"prose row": 3, "heading": 1},
        "sections": {"Abilities and Powers / Fighting Style": 3},
        "single_source": 3, "corroborated": 1, "lead_level": 1,
    }

    with_them = canon_report.render(scores, {}, {}, meta, intruders=intruders)
    assert "## Where the wrong names come from" in with_them
    assert "prose row" in with_them
    assert "Abilities and Powers / Fighting Style" in with_them

    # `intruders` is new and optional, and an older run folder has no such
    # artifact to pass.
    without = canon_report.render(scores, {}, {}, meta)
    assert "## Where the wrong names come from" not in without

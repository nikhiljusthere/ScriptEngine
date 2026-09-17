"""CSM-2 scope logic in `tools/coverage_report.py` (pilot scope, council item 2).

The campaign scope (page_scope / unknown_pages / remainder_note) lives in
`series/<name>/overrides.yaml`; the tool must classify every store page type
and every `unknown` page, and exit non-zero when one is not declared —
"silence must become an error". Hermetic tests for the classifier + the
real-oversight check against the CSM store (skipped when series/ is absent).
"""
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import pytest

import coverage_report as cr
from scriptengine.config import load_overrides, series_paths

PS = {
    "types": {
        "character": {"in_scope": True, "archetype": "character"},
        "unknown": {"in_scope": False, "archetype": "item"},
    },
    "unknown_pages": {"Contract": {"in_scope": True, "archetype": "item"}},
    "remainder_note": "note",
}


def test_unclassified_page_type_is_a_violation():
    docs = [("Some Page", "character"), ("Other", "mystery_type")]
    violations = cr.scope_violations(docs, PS)
    assert len(violations) == 1
    assert "'mystery_type'" in violations[0]


def test_unknown_page_without_disposition_is_a_violation():
    docs = [("Orphan Unknown", "unknown")]
    assert len(cr.scope_violations(docs, PS)) == 1
    assert "Orphan Unknown" in cr.scope_violations(docs, PS)[0]


def test_fully_classified_store_has_no_violations():
    docs = [("Denji", "character"), ("Contract", "unknown")]
    assert cr.scope_violations(docs, PS) == []


def test_in_scope_predicate_type_and_per_page():
    assert cr.in_scope("character", "Denji", PS)
    assert not cr.in_scope("unknown", "Popularity Polls", PS)
    assert cr.in_scope("unknown", "Contract", PS)


def test_missing_page_scope_raises(monkeypatch):
    monkeypatch.setattr(cr, "load_overrides", lambda paths: {})
    with pytest.raises(cr.ScopeError):
        cr.load_page_scope(SimpleNamespace(overrides=Path("series/x/overrides.yaml")))


@pytest.mark.skipif(
    not (ROOT / "series/csm/overrides.yaml").exists()
    or not (ROOT / "series/csm/facts.db").exists(),
    reason="CSM series data not present on this machine",
)
def test_csm_scope_classifies_the_whole_store():
    """The CSM declarations (CSM-2) cover the entire CSM store: 0
    unclassified, 0 undisposed unknown pages, and the declared in-scope
    set is 469 type pages + 4 unknown pages = 473. (Council #32 P-6, drift
    D30, flipped chapter_box (232) + story_arcs_box (14) in-scope: the
    pre-D2 227 + 246 = 473 -- COVERAGE.md 473/537.)"""
    paths = series_paths("csm")
    ps = cr.load_page_scope(paths)
    docs = [
        (r[0], r[1])
        for r in __import__("sqlite3").connect(paths.facts_db).execute(
            "SELECT title, page_type FROM documents")
    ]
    assert len(docs) == 537
    assert cr.scope_violations(docs, ps) == []
    in_scope = sum(1 for title, pt in docs if cr.in_scope(pt, title, ps))
    assert in_scope == 473
    unknown_titles = {t for t, pt in docs if pt == "unknown"}
    assert len(unknown_titles) == 14
    assert unknown_titles <= set(ps["unknown_pages"])
    assert {t for t, d in ps["unknown_pages"].items() if d.get("in_scope")} == \
        {"Contract", "Hell", "World", "Aging's World"}


@pytest.mark.skipif(
    not (ROOT / "series/jjk/overrides.yaml").exists(),
    reason="JJK series data not present on this machine",
)
def test_jjk_scope_encodes_the_legacy_in_scope_sets():
    """Byte-identity regression: the JJK declarations must reproduce the
    retired IN_SCOPE_TYPES / IN_SCOPE_PAGES exactly."""
    ps = cr.load_page_scope(series_paths("jjk"))
    assert {pt for pt, v in ps["types"].items() if v.get("in_scope")} == \
        {"item", "location", "organizations", "species", "simple_box", "occupation"}
    assert {t for t, d in ps["unknown_pages"].items() if d.get("in_scope")} == \
        {"Jujutsu Regulations"}
    # the remainder note is the former hardcoded paragraph, verbatim
    assert "volume, blu_ray_dvd, music, game, series, anime, novel" in ps["remainder_note"]
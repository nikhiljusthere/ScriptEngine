"""R-6 (CSM iter1, 2026-09-10): the narrative door's per-wiki subject-alias map.

CSM's alias table carries only the full arc titles ("Bomb Girl arc"); the bare
display names the questions actually use resolved to nothing, so the narrative
door missed on them (miss queue door-nar-None x3, fix class R-6). The fix is a
per-wiki map in series/csm/overrides.yaml consulted at query time by
retrieve/narrative.py (config.subject_aliases): model-free, no reindex.
"""
import pytest

from scriptengine.config import load_overrides, series_paths, subject_aliases
from scriptengine.retrieve.narrative import NarrativeRetriever


def test_subject_aliases_maps_csm_display_names():
    assert subject_aliases(None) == {}
    aliases = subject_aliases(load_overrides(series_paths("csm")))
    assert aliases == {
        "introduction": "Introduction arc",
        "bomb girl": "Bomb Girl arc",
        "international assassins": "International Assassins arc",
    }


def test_narrative_timeline_resolves_bare_csm_arc_display_names():
    paths = series_paths("csm")
    if not paths.facts_db.exists():
        pytest.skip("csm is not indexed")
    with NarrativeRetriever(paths) as r:
        for display, canonical in (
            ("Introduction", "Introduction arc"),
            ("Bomb Girl", "Bomb Girl arc"),
            ("International Assassins", "International Assassins arc"),
        ):
            narrative = r.timeline(
                f"What happened in the {display}, in order?", max_beats=5
            )
            assert narrative.subject == canonical


def test_authored_floor_consults_the_alias_map():
    paths = series_paths("csm")
    if not paths.facts_db.exists():
        pytest.skip("csm is not indexed")
    with NarrativeRetriever(paths) as r:
        # The floor keys on the resolved node, so a bare display name must
        # yield the same floor as the canonical name (either one).
        for display, canonical in (
            ("Bomb Girl", "Bomb Girl arc"),
            ("Introduction", "Introduction arc"),
        ):
            assert r.authored_floor(display, 5) == r.authored_floor(canonical, 5)
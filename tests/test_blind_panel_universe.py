"""Regression: blind_panel._universe must actually parse the (Earth-N) marker.

The sealed 2026-09-27 panel v1 (commit e4ef2c75) was drawn with the
universe-variant class's eligibility filter silently a no-op: the marker
check compared an 8-char slice against the 7-char string "(Earth-" (which
can never be equal), so _universe returned "" for every title and the
filter kept everything the SQL selected -- including primary-universe
(616/199999) subjects. v1 therefore contains one subject (Snake Sanchus
(Earth-616)) that violates the class's declared eligibility; the panel was
re-sealed as v2 on 2026-09-27 after the fix (known_diffs C1-adjacent tool
record). The state-over-time class is unaffected (its filter uses the
affiliation-fact SQL, not _universe).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "marvel"))

import blind_panel  # noqa: E402


def test_universe_parses_earth_marker():
    assert blind_panel._universe("Peter Parker (Earth-12629)") == "12629"
    assert blind_panel._universe("Snake Sanchus (Earth-616)") == "616"
    assert blind_panel._universe("Mushkan (Earth-616)") == "616"
    # the LAST marker wins (nested/compound titles)
    assert blind_panel._universe(
        "John Jonah Jameson (Warp World) (Earth-616)") == "616"
    assert blind_panel._universe("No marker here") == ""
    assert blind_panel._universe("Character") == ""


def test_universe_variant_filter_excludes_primary_universes():
    """The class's declared eligibility: universe is not 616/199999."""
    f = blind_panel.CLASSES["universe-variant"]["filter"]
    assert not f("Snake Sanchus (Earth-616)")     # primary 616
    assert not f("Peter Parker (Earth-199999)")   # primary 199999
    assert f("Peter Parker (Earth-12629)")        # non-primary variant
    assert f("Rahne Sinclair (Earth-32000)")      # non-primary variant


def test_drawn_panel_subjects_satisfy_their_class_filter():
    """Every panel row must satisfy its own class filter (v2 invariant)."""
    rows = [
        __import__("json").loads(l)
        for l in blind_panel._panel_path("marvel").read_text().splitlines()
        if l.strip()
    ]
    assert rows, f"panel {blind_panel._panel_path('marvel')} missing"
    for r in rows:
        f = blind_panel.CLASSES[r["class"]]["filter"] \
            if r["class"] == "universe-variant" else None
        if f is not None:
            assert f(r["subject"]), (
                f"panel subject {r['subject']!r} violates the "
                f"universe-variant eligibility (primary universe kept)")
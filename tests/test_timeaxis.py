"""The story's time axis: an orderable position for every placed event.

A name does not sort; an index does. The axis converts the arc the wiki filed
each placement page under into an orderable position, from the cheap signals
(arc-page, arc-fact, citation) with inference reserved for the residue. These
tests lock the invariants a script writer's continuity check depends on: the
story chain orders canonically, the cheap signals reach every placement page the
wiki can place, and the global read is monotonic in that order.
"""

from __future__ import annotations

import pytest

from scriptengine.config import series_paths
from scriptengine.ingest import timeaxis
from scriptengine.stores.facts import FactStore


@pytest.fixture(scope="module")
def jjk_store():
    paths = series_paths("jjk")
    if not paths.facts_db.exists():
        pytest.skip("jjk is not indexed")
    with FactStore(paths.facts_db) as store:
        yield store


class TestStoryArcIndex:
    def test_story_chains_order_canonically(self, jjk_store):
        index = timeaxis.story_arc_index(jjk_store)
        # The story is a single run in JJK; the arcs must line up canonically,
        # early arcs before late ones, regardless of the run's absolute length.
        order = [
            "Cursed Child Arc",
            "Fearsome Womb Arc",
            "Vs. Mahito Arc",
            "Kyoto Goodwill Event Arc",
            "Shibuya Incident Arc",
            "Culling Game Arc",
            "Shinjuku Showdown Arc",
        ]
        positions = [index[a.lower()] for a in order if a.lower() in index]
        assert len(positions) >= 5, "the story chain must reach most JJK arcs"
        assert positions == sorted(positions)

    def test_shibuya_precedes_culling_game(self, jjk_store):
        index = timeaxis.story_arc_index(jjk_store)
        assert index["shibuya incident arc"] < index["culling game arc"]


class TestMatchArc:
    @pytest.mark.parametrize(
        "value, want",
        [
            ("Culling Game", "Culling Game Arc"),
            ("Shibuya Incident Arc", "Shibuya Incident Arc"),
            ("Gojo's Past", "Gojo's Past Arc"),
            # A double-arc event page names both arcs; the first is the one it
            # files under, and the match must not be thrown by the second.
            ("Culling Game Arc Shinjuku Showdown Arc", "Culling Game Arc"),
        ],
    )
    def test_reference_shapes_resolve(self, jjk_store, value, want):
        assert timeaxis.match_arc(jjk_store, value) == want

    def test_unknown_arc_does_not_guess(self, jjk_store):
        assert timeaxis.match_arc(jjk_store, "An Arc That Is Not One") is None
        assert timeaxis.match_arc(jjk_store, None) is None


class TestChapterArcIndex:
    def test_chapters_file_to_their_arc(self, jjk_store):
        chapter_map = timeaxis.chapter_arc_index(jjk_store)
        # A chapter the wiki files under an arc is a lookup, not a guess.
        assert chapter_map[213] == "Culling Game Arc"
        assert chapter_map[14] == "Fearsome Womb Arc"
        assert chapter_map[80] == "Shibuya Incident Arc"

    def test_a_chapter_no_battle_files_is_unmapped(self, jjk_store):
        # A chapter number outside every arc's stated span is a gap in the wiki,
        # and the axis must not invent an arc for it.
        chapter_map = timeaxis.chapter_arc_index(jjk_store)
        assert 9999 not in chapter_map


class TestPlacementTimeAxis:
    def test_every_placement_page_is_accounted_for(self, jjk_store):
        axis = timeaxis.placement_time_axis(jjk_store)
        signals = {p.signal for p in axis.values()}
        assert signals <= {"arc_page", "arc_fact", "chapters", "residue"}
        # The cheap signals are the point: the residue is a small remainder the
        # wiki gives no signal for, not the common case.
        placed = sum(1 for p in axis.values() if p.signal != "residue")
        assert placed >= 0.9 * len(axis)

    def test_story_arc_pages_place_themselves(self, jjk_store):
        axis = timeaxis.placement_time_axis(jjk_store)
        for arc in (
            "Shibuya Incident Arc",
            "Culling Game Arc",
            "Shinjuku Showdown Arc",
        ):
            if arc in axis:
                assert axis[arc].signal == "arc_page"
                assert axis[arc].arc == arc
                assert axis[arc].index is not None


class TestEventsInStoryOrder:
    def test_arc_index_is_monotonic(self, jjk_store):
        rows = timeaxis.events_in_story_order(jjk_store)
        assert rows, "the store must carry placed events"
        positions = [
            r["arc_index"] if r["arc_index"] is not None else float("inf")
            for r in rows
        ]
        assert positions == sorted(positions)

    def test_earlier_arcs_precede_later_ones(self, jjk_store):
        rows = timeaxis.events_in_story_order(jjk_store)
        shibuya = [r for r in rows if r["arc_name"] == "Shibuya Incident Arc"]
        culling = [r for r in rows if r["arc_name"] == "Culling Game Arc"]
        if shibuya and culling:
            assert max(r["arc_index"] for r in shibuya) < min(
                r["arc_index"] for r in culling
            )

    def test_subject_filter_keeps_order(self, jjk_store):
        rows = timeaxis.events_in_story_order(jjk_store, subject="Yuji Itadori")
        assert rows, "Yuji Itadori states events on the placement pages"
        positions = [
            r["arc_index"] if r["arc_index"] is not None else float("inf")
            for r in rows
        ]
        assert positions == sorted(positions)
        assert all(r["subject_name"] == "Yuji Itadori" for r in rows)


class TestBackfill:
    def test_backfill_places_every_row(self, jjk_store):
        tally = timeaxis.backfill_event_arc_index(jjk_store)
        assert tally["rows"] > 0
        # A row may sit off the axis only if it is atemporal (temporal=0: a
        # standing state the axis cannot order) or it is filed under a residue
        # page the cheap signals did not reach. Every temporal row is placed.
        # Temporality, not page provenance, is what decides: corpus pages whose
        # events the axis cannot order are stored atemporal, so they are the
        # expected off-axis set, not a leak.
        residue = [
            page
            for page, placed in timeaxis.placement_time_axis(jjk_store).items()
            if placed.signal == "residue"
        ]
        connection = jjk_store.connection
        null_rows = connection.execute(
            "SELECT COUNT(*) FROM events WHERE arc_index IS NULL"
        ).fetchone()[0]
        if residue:
            placeholders = ",".join("?" * len(residue))
            allowed_off = connection.execute(
                f"SELECT COUNT(*) FROM events "
                f"WHERE temporal = 0 OR arc_key IN ({placeholders})",
                residue,
            ).fetchone()[0]
        else:
            allowed_off = connection.execute(
                "SELECT COUNT(*) FROM events WHERE temporal = 0"
            ).fetchone()[0]
        assert null_rows == allowed_off
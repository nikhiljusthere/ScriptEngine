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
from scriptengine.ingest.events import EVENTIVE_VERBS
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


class TestSectionArcIndex:
    def test_only_on_chain_arc_sections_resolve(self, jjk_store):
        # A section places events only when its title names an arc the wiki has
        # AND that arc is on the story chain; everything else resolves to nothing.
        section_map = timeaxis.section_arc_index(jjk_store)
        assert section_map, "at least one section is named for an on-chain arc"

    def test_section_index_agrees_with_the_arc_page(self, jjk_store):
        # A section titled for an arc lands on the same axis position as the arc
        # page itself: the section and the page that names the arc cannot diverge.
        section_map = timeaxis.section_arc_index(jjk_store)
        index = timeaxis.story_arc_index(jjk_store)
        connection = jjk_store.connection
        for sid, (pos, _page) in section_map.items():
            title = connection.execute(
                "SELECT title FROM sections WHERE id = ?", (sid,)
            ).fetchone()["title"]
            arc = timeaxis.match_arc(jjk_store, title.strip())
            assert arc is not None
            assert index[arc.lower()] == pos

    def test_non_arc_section_does_not_place(self, jjk_store):
        # A section the wiki did not name for an arc ("Plot Details", "Summary",
        # "History") carries no placement of its own and stays out of the map.
        section_map = timeaxis.section_arc_index(jjk_store)
        generic = {"plot details", "summary", "synopsis", "overview", "history", "plot"}
        connection = jjk_store.connection
        for sid, _ in section_map.items():
            title = connection.execute(
                "SELECT title FROM sections WHERE id = ?", (sid,)
            ).fetchone()["title"]
            assert title.strip().lower() not in generic


class TestBackfill:
    def test_total_rows_are_intact(self, jjk_store):
        # The backfill re-derives placement; it must never add or drop a row.
        tally = timeaxis.backfill_event_arc_index(jjk_store)
        rows = jjk_store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        assert tally["rows"] == rows

    def test_temporal_rows_are_placed(self, jjk_store):
        # The invariant a continuity check depends on: a row that states an order
        # (temporal=1) carries an arc_index, so it can be ordered canonically. A
        # row that states no order may sit off the axis; a row that does, may not.
        timeaxis.backfill_event_arc_index(jjk_store)
        dangling = jjk_store.connection.execute(
            "SELECT COUNT(*) FROM events WHERE temporal = 1 AND arc_index IS NULL"
        ).fetchone()[0]
        assert dangling == 0

    def test_section_signal_recovers_the_arc_named_rows(self, jjk_store):
        # The ledger: 995 events sit under arc-named sections on off-chain pages
        # (mostly character/synopsis). The section signal places exactly those.
        section_map = timeaxis.section_arc_index(jjk_store)
        timeaxis.backfill_event_arc_index(jjk_store)
        connection = jjk_store.connection
        placed = 0
        for sid, (pos, page) in section_map.items():
            placed += connection.execute(
                "SELECT COUNT(*) FROM events WHERE section_id = ? AND arc_key = ?"
                " COLLATE NOCASE AND arc_index = ?",
                (sid, page, pos),
            ).fetchone()[0]
        assert placed == 995

    def test_citation_signal_places_the_cited_rows(self, jjk_store):
        # The third, weakest signal (R4): a row the page and section signals left
        # off the axis is grounded by the wiki's own in-text citation -- the
        # paragraph that states it, or a section cited at least twice into one
        # arc. The tally counts rows placed by right, so a settled re-run reports
        # the same number; the residue it cannot ground keeps arc_index NULL.
        tally = timeaxis.backfill_event_arc_index(jjk_store)
        assert tally["citations"] == 90
        unplaced = jjk_store.connection.execute(
            "SELECT COUNT(*) FROM events WHERE arc_index IS NULL"
        ).fetchone()[0]
        assert unplaced == 64

    def test_side_story_citations_place_nothing(self, jjk_store):
        # "Modulo Chapter N" citations name the wiki's side-story numbering, which
        # files under no arc on the main chain. The signal must skip them: a
        # miss, never a wrong arc.
        timeaxis.backfill_event_arc_index(jjk_store)
        placed = jjk_store.connection.execute(
            "SELECT COUNT(*) FROM events WHERE arc_key LIKE ?"
            " AND arc_index IS NOT NULL",
            ("Modulo Chapter%",),
        ).fetchone()[0]
        assert placed == 0

    def test_triage_ledger_accounts_for_every_unplaced_row(self, jjk_store):
        # The R4 done-criterion: an unplaced event is a legal outcome only with a
        # recorded reason. One ledger row per unplaced row, each carrying the
        # reason -- which wiki filing is missing -- not a bare NULL.
        timeaxis.backfill_event_arc_index(jjk_store)
        ledger = timeaxis.triage_unplaced(jjk_store)
        unplaced = jjk_store.connection.execute(
            "SELECT COUNT(*) FROM events WHERE arc_index IS NULL"
        ).fetchone()[0]
        assert len(ledger) == unplaced
        assert all(entry["reason"] for entry in ledger)

    def test_arc_named_section_places_its_events(self, jjk_store):
        # An event stated in a section the wiki named for an on-chain arc sits in
        # that arc even when the owning page (a character) is off the story chain.
        section_map = timeaxis.section_arc_index(jjk_store)
        timeaxis.backfill_event_arc_index(jjk_store)
        connection = jjk_store.connection
        checked = 0
        for sid, (pos, page) in section_map.items():
            for row in connection.execute(
                "SELECT arc_index FROM events WHERE section_id = ? AND arc_key = ?"
                " COLLATE NOCASE",
                (sid, page),
            ):
                assert row["arc_index"] == pos
                checked += 1
        assert checked > 0

    def test_section_guard_requires_the_owning_page(self, jjk_store):
        # A section only places the events on its own page. An event that carries
        # the section id from a *different* page is left to the page signal and
        # never given the section's arc -- the guard that keeps a dangling or
        # reused id (a renumbering re-crawl) a miss, not a wrong arc.
        section_map = timeaxis.section_arc_index(jjk_store)
        timeaxis.backfill_event_arc_index(jjk_store)
        connection = jjk_store.connection
        for sid, (pos, page) in section_map.items():
            foreign = connection.execute(
                "SELECT COUNT(*) FROM events WHERE section_id = ? AND arc_key <> ?"
                " COLLATE NOCASE AND arc_index = ?",
                (sid, page, pos),
            ).fetchone()[0]
            assert foreign == 0


class TestStoreAxisBackfill:
    """R3: the wiki's declared store axis is the weakest placement signal.

    A row the page, section and citation signals missed inherits the rank
    of its page on the declared axis -- the wiki's own clock, per
    partition -- and the axis' partition value, written to the
    `partition` column. A wiki that declares no axis sees the step as a
    no-op, so its rows keep their baseline.
    """

    OVERRIDES = """\
events:
  axis:
    date_keys: [releasedate]
    partition_key: reality
"""

    @pytest.fixture()
    def axis_store(self, tmp_path):
        """Two episode instalments, dated, filed under one reality.

        Neither instalment carries an `arc` or chapter fact, so the story
        axis and the section signal reach no row: only the declared store
        axis can place them."""
        root = tmp_path / "axiswiki"
        root.mkdir()
        (root / "overrides.yaml").write_text(self.OVERRIDES, encoding="utf-8")
        store = FactStore(root / "facts.db")
        store.initialise()
        c = store.connection
        c.executemany(
            "INSERT INTO documents (id, title, page_type) VALUES (?, ?, ?)",
            [(1, "Ep One", "episode"), (2, "Ep Two", "episode")],
        )
        c.executemany(
            "INSERT INTO sections"
            " (id, document_id, title, breadcrumb, level, ordinal, text,"
            " word_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (1, 1, "Plot", "", 1, 0, "Ep One happens.", 10),
                (2, 2, "Plot", "", 1, 0, "Ep Two happens.", 10),
            ],
        )
        c.executemany(
            "INSERT INTO nodes (id, name, document_id, is_resolved)"
            " VALUES (?, ?, ?, 1)",
            [(1, "Ep One", 1), (2, "Ep Two", 2)],
        )
        c.executemany(
            "INSERT INTO facts (id, node_id, key, value) VALUES (?, ?, ?, ?)",
            [
                (1, 1, "releasedate", "March 2020"),
                (2, 1, "reality", "Earth-838"),
                (3, 2, "releasedate", "April 2020"),
                (4, 2, "reality", "Earth-838"),
            ],
        )
        c.executemany(
            "INSERT INTO events (subject_node, subject_name, object_node,"
            " object_name, verb, arc_key, section_id, quote, time_rank,"
            " passage, doc_title, section_ordinal)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, '', ?, '', ?, ?)",
            [
                (1, "Ep One", 2, "Ep Two", "defeats", "Ep One", 1, 1,
                 "Ep One", 0),
                (1, "Ep One", 2, "Ep Two", "defeats", "Ep Two", 2, 1,
                 "Ep Two", 0),
            ],
        )
        c.commit()
        return store

    def test_declared_axis_places_the_missed_rows_with_partition(
        self, axis_store
    ):
        tally = timeaxis.backfill_event_arc_index(axis_store)
        rows = {
            row["arc_key"]: row
            for row in axis_store.connection.execute(
                'SELECT arc_key, arc_index, "partition" FROM events'
                " ORDER BY arc_key"
            )
        }
        # Both rows the story signals missed; the declared axis reached both.
        assert tally["store_axis"] == 2
        # The axis' order, not an invention: the earlier date sits first.
        assert rows["Ep One"]["arc_index"] < rows["Ep Two"]["arc_index"]
        # The axis' partition value, written to the column.
        assert rows["Ep One"]["partition"] == "Earth-838"
        assert rows["Ep Two"]["partition"] == "Earth-838"

    def test_axis_tally_is_stable_across_reruns(self, axis_store):
        # The tally counts reach, not updates: a settled re-run reports the
        # same number and moves nothing.
        first = timeaxis.backfill_event_arc_index(axis_store)
        placed = {
            row["arc_key"]: row["arc_index"]
            for row in axis_store.connection.execute(
                "SELECT arc_key, arc_index FROM events"
            )
        }
        second = timeaxis.backfill_event_arc_index(axis_store)
        assert second["store_axis"] == first["store_axis"] == 2
        same = axis_store.connection.execute(
            "SELECT COUNT(*) FROM events WHERE arc_index IS NOT NULL"
        ).fetchone()[0]
        assert same == 2
        for key, value in placed.items():
            assert axis_store.connection.execute(
                "SELECT arc_index FROM events WHERE arc_key = ?", (key,)
            ).fetchone()[0] == value

    def test_a_wiki_that_declares_no_axis_sees_a_noop(self, jjk_store):
        # jjk declares no `events: axis:` block: the step is a no-op, no row
        # gains a partition value, and the tally reports zero reach.
        tally = timeaxis.backfill_event_arc_index(jjk_store)
        assert tally["store_axis"] == 0
        set_ = jjk_store.connection.execute(
            'SELECT COUNT(*) FROM events WHERE "partition" IS NOT NULL'
        ).fetchone()[0]
        assert set_ == 0


class TestRecomputeTemporal:
    def test_temporal_tracks_the_placement(self, jjk_store):
        # After the recompute the flag agrees with the placement: no temporal
        # row sits off the axis, and no placed eventive row is left recorded as
        # a state. That is the invariant a time-axis ordering depends on.
        tally = timeaxis.recompute_temporal(jjk_store)
        connection = jjk_store.connection
        dangling = connection.execute(
            "SELECT COUNT(*) FROM events WHERE temporal = 1 AND arc_index IS NULL"
        ).fetchone()[0]
        assert dangling == 0
        hidden = connection.execute(
            "SELECT COUNT(*) FROM events WHERE temporal = 0"
            f" AND arc_index IS NOT NULL AND verb IN ({', '.join('?' * len(EVENTIVE_VERBS))})",
            tuple(EVENTIVE_VERBS),
        ).fetchone()[0]
        assert hidden == 0
        assert (
            tally["temporal_after"]
            == tally["temporal_before"]
            + tally["temporal_promoted"]
            - tally["temporal_demoted"]
        )

    def test_recompute_is_idempotent(self, jjk_store):
        first = timeaxis.recompute_temporal(jjk_store)
        second = timeaxis.recompute_temporal(jjk_store)
        assert second["temporal_promoted"] == 0
        assert second["temporal_demoted"] == 0
        assert second["temporal_after"] == first["temporal_after"]
"""C4 T2: section-like passages in the events store.

The `passage` column (R4/R7 storage): '' marks a row read from a section;
'fact:<key>' and 'lead' mark a row read from a declared narrative fact value
or the page lead, whose `section_id` is NULL and whose durable key is
(doc_title, section_ordinal, passage).

Locks: the PK carries `passage` (two fact values of one page stating the same
(S, v, O) at the same axis rank both store); the save path dedups window
overlap and replaces per passage (a re-run of one passage never wipes a
sibling's rows); a store that already had its FKs when the column landed is
repaired in place; and `remap_derived` re-anchors passage rows onto a
rebuild -- stale revids drop, a changed fact value drops its rows as
unverified, unchanged sources remap.
"""

from __future__ import annotations

import pytest

from scriptengine.ingest.events import build_passages
from scriptengine.stores.facts import FactStore


@pytest.fixture()
def store(tmp_path):
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    yield store
    store.close()


def base(store: FactStore) -> tuple[int, int, int, int]:
    """One arc page with a section, two participants and a history fact."""
    doc = store.add_document(
        title="Test Arc", url="", page_type="event",
        infobox_template="Event Infobox",
        lead="The arc opens with Steve fighting Peggy.",
        word_count=8, revid=1, fetched_at="",
    )
    section = store.add_section(
        document_id=doc, title="Plot", breadcrumb="Test Arc/Plot", level=2,
        ordinal=0, text="Steve fights Peggy at the laboratory.", word_count=7,
    )
    steve = store.add_node("Steve", "character", doc)
    peggy = store.add_node("Peggy", "character", doc)
    store.add_fact(
        node_id=steve, key="history", label="History",
        value="Steve met Peggy in 1942.", citation="",
    )
    return doc, section, steve, peggy


def section_row(section: int, steve: int, peggy: int) -> dict:
    return {
        "subject_node": steve, "subject_name": "Steve",
        "object_node": peggy, "object_name": "Peggy",
        "verb": "fights", "section_id": section,
        "quote": "Steve fights Peggy at the laboratory.",
        "temporal": True, "time_rank": 1.0,
    }


def fact_row(steve: int, peggy: int, key: str = "history") -> dict:
    return {
        "subject_node": steve, "subject_name": "Steve",
        "object_node": peggy, "object_name": "Peggy",
        "verb": "met", "section_id": None,
        "quote": "Steve met Peggy in 1942.",
        "temporal": False, "time_rank": 1.0,
        "passage": f"fact:{key}",
    }


def lead_row(steve: int, peggy: int) -> dict:
    return {
        "subject_node": steve, "subject_name": "Steve",
        "object_node": peggy, "object_name": "Peggy",
        "verb": "fights", "section_id": None,
        "quote": "The arc opens with Steve fighting Peggy.",
        "temporal": True, "time_rank": 1.0,
        "passage": "lead",
    }


class TestPassagePrimaryKey:
    def test_fresh_schema_pk_includes_passage(self, store):
        _, _, steve, peggy = base(store)
        store.ensure_events()
        pk = {
            row[1] for row in store.connection.execute(
                "PRAGMA table_info(events)")
            if row[5]
        }
        assert pk == {
            "subject_node", "verb", "object_node", "section_id",
            "time_rank", "passage",
        }

    def test_two_fact_values_same_svo_rank_both_store(self, store):
        _, _, steve, peggy = base(store)
        store.ensure_events()
        stored, dedup = store.save_events(
            "Test Arc",
            [fact_row(steve, peggy, "history"),
             fact_row(steve, peggy, "synopsis")],
            revid=1, prompt_version="p1", model="m",
        )
        # Same (S, v, O), both at the page's axis rank, section_id NULL:
        # without `passage` in the PK the second would replace the first.
        assert stored == 2
        assert dedup == 0
        passages = {
            row[0] for row in store.connection.execute(
                "SELECT DISTINCT passage FROM events WHERE arc_key = 'Test Arc'")
        }
        assert passages == {"fact:history", "fact:synopsis"}


class TestSavePath:
    def test_dedup_same_quote_two_windows(self, store):
        _, _, steve, peggy = base(store)
        store.ensure_events()
        stored, dedup = store.save_events(
            "Test Arc", [fact_row(steve, peggy), fact_row(steve, peggy)],
            revid=1, prompt_version="p1", model="m",
        )
        assert stored == 1
        assert dedup == 1

    def test_per_passage_replace_preserves_siblings(self, store):
        _, _, steve, peggy = base(store)
        store.ensure_events()
        store.save_events(
            "Test Arc",
            [fact_row(steve, peggy), lead_row(steve, peggy)],
            revid=1, prompt_version="p1", model="m",
        )
        # A re-run that only re-reads the history value must not wipe the
        # lead's row: the replace is per passage, not per arc.
        stored, _ = store.save_events(
            "Test Arc",
            [{**fact_row(steve, peggy), "verb": "befriended"}],
            revid=1, prompt_version="p2", model="m",
        )
        assert stored == 1
        assert store.event_passages("Test Arc") == {"fact:history", "lead"}
        verbs = {
            row[0] for row in store.connection.execute(
                "SELECT verb FROM events WHERE arc_key = 'Test Arc'")
        }
        assert verbs == {"befriended", "fights"}


class TestMigration:
    def test_store_with_old_pk_is_repaired(self, store):
        """The state the live stores are in: FKs + `passage` column, but the
        pre-T2 five-part key. The same rebuild repairs the key in place."""
        doc, section, steve, peggy = base(store)
        # The base schema now creates `events` itself; simulate the live
        # store's pre-T2 state (FKs + `passage`, old five-part key) by
        # rebuilding the table on that key.
        store.connection.execute("DROP TABLE events")
        store.connection.execute(
            "CREATE TABLE events ("
            " subject_node INTEGER REFERENCES nodes(id) ON DELETE CASCADE,"
            " subject_name TEXT,"
            " object_node INTEGER REFERENCES nodes(id) ON DELETE CASCADE,"
            " object_name TEXT, verb TEXT, arc_key TEXT,"
            " section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,"
            " quote TEXT, temporal INTEGER, time_rank REAL,"
            " arc_index INTEGER,"
            " doc_title TEXT NOT NULL DEFAULT '',"
            " section_ordinal INTEGER NOT NULL DEFAULT 0,"
            " passage TEXT NOT NULL DEFAULT '',"
            " revid INTEGER, prompt_version TEXT,"
            " model TEXT, extracted_at TEXT,"
            " PRIMARY KEY (subject_node, verb, object_node, section_id,"
            " time_rank))"
        )
        row = section_row(section, steve, peggy)
        store.connection.execute(
            "INSERT INTO events (subject_node, subject_name, object_node,"
            " object_name, verb, arc_key, section_id, quote, temporal,"
            " time_rank, arc_index, doc_title, section_ordinal, passage,"
            " revid, prompt_version, model, extracted_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (steve, "Steve", peggy, "Peggy", "fights", "Test Arc", section,
             row["quote"], 1, 1.0, None, "Test Arc", 0, "", 1, "p1", "m", ""),
        )
        dropped = store.ensure_events()
        assert dropped == 0
        pk = {
            row[1] for row in store.connection.execute(
                "PRAGMA table_info(events)")
            if row[5]
        }
        assert "passage" in pk
        assert store.connection.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0] == 1


class TestRemap:
    def _rebuild(self, store, *, history_changed: bool = False):
        """A rebuild that renumbers every id; optionally moves a fact value."""
        doc = store.add_document(
            title="Test Arc", url="", page_type="event",
            infobox_template="Event Infobox",
            lead="The arc opens with Steve fighting Peggy.",
            word_count=8, revid=1, fetched_at="",
        )
        section = store.add_section(
            document_id=doc, title="Plot", breadcrumb="Test Arc/Plot",
            level=2, ordinal=0,
            text="Steve fights Peggy at the laboratory.", word_count=7,
        )
        steve = store.add_node("Steve", "character", doc)
        peggy = store.add_node("Peggy", "character", doc)
        store.add_fact(
            node_id=steve, key="history", label="History",
            value=("Steve met Peggy in 1945."
                   if history_changed else "Steve met Peggy in 1942."),
            citation="",
        )
        return section, steve, peggy

    def test_remap_rekeys_and_reanchors(self, store):
        _, section, steve, peggy = base(store)
        store.ensure_events()
        store.save_events(
            "Test Arc",
            [section_row(section, steve, peggy), fact_row(steve, peggy),
             lead_row(steve, peggy)],
            revid=1, prompt_version="p1", model="m",
        )
        snapshot = store.reset()
        assert snapshot["events"], "the reset must snapshot the rows"
        new_section, _, _ = self._rebuild(store)
        report = store.remap_derived(snapshot)
        stats = report["events"]
        assert stats["remapped"] == 3
        assert stats["orphaned"] == stats["stale"] == stats["unverified"] == 0
        rows = {
            r[1]: r[0] for r in store.connection.execute(
                "SELECT section_id, passage FROM events"
            )
        }
        assert rows[""] == new_section, "the section row re-keys onto the new id"
        assert rows["fact:history"] is None, "fact rows stay section-less"
        assert rows["lead"] is None, "lead rows stay section-less"

    def test_remap_drops_unverified_fact_value(self, store):
        _, _, steve, peggy = base(store)
        store.ensure_events()
        store.save_events(
            "Test Arc", [fact_row(steve, peggy)],
            revid=1, prompt_version="p1", model="m",
        )
        snapshot = store.reset()
        self._rebuild(store, history_changed=True)
        report = store.remap_derived(snapshot)
        # The value no longer says what the row's quote says: dropped for
        # re-extraction, not silently re-anchored.
        assert report["events"]["unverified"] == 1
        assert store.connection.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0] == 0

    def test_remap_drops_stale_revid(self, store):
        _, section, steve, peggy = base(store)
        store.ensure_events()
        store.save_events(
            "Test Arc", [section_row(section, steve, peggy)],
            revid=1, prompt_version="p1", model="m",
        )
        snapshot = store.reset()
        doc = store.add_document(
            title="Test Arc", url="", page_type="event",
            infobox_template="Event Infobox", lead="", word_count=0,
            revid=2, fetched_at="",  # the page was re-crawled
        )
        store.add_section(
            document_id=doc, title="Plot", breadcrumb="Test Arc/Plot",
            level=2, ordinal=0,
            text="Steve fights Peggy at the laboratory.", word_count=7,
        )
        store.add_node("Steve", "character", doc)
        store.add_node("Peggy", "character", doc)
        report = store.remap_derived(snapshot)
        assert report["events"]["stale"] == 1
        assert store.connection.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0] == 0

    def test_pilot_shaped_section_row_survives_a_force_rebuild(self, store):
        """The mcu pilot's writer bug (2026-09-28, bug A): the section rows
        stored the SECTION TITLE in `passage`, which the remap reads as a
        section-less passage -- verified against nothing, dropped on the
        next `--force` rebuild. The committed design: `passage` stays ''
        (the section's own marker), so the row re-keys on
        (doc_title, section_ordinal) and its quote re-verifies against the
        section's text. This test drives the row through the writer's own
        passage builder, not a hand-built dict."""
        _, section, steve, peggy = base(store)
        store.ensure_events()
        srow = store.connection.execute(
            "SELECT * FROM sections WHERE id = ?", (section,)
        ).fetchone()
        passages = build_passages(store, "Test Arc", [srow], "placement", None)
        # The writer's contract: the section's own marker, never its title.
        assert passages[0]["passage"] == ""
        store.save_events(
            "Test Arc",
            [
                {
                    "subject_node": steve, "subject_name": "Steve",
                    "object_node": peggy, "object_name": "Peggy",
                    "verb": "fights", "section_id": section,
                    "quote": "Steve fights Peggy at the laboratory.",
                    "temporal": True, "time_rank": 0.0,
                    "passage": passages[0]["passage"],
                }
            ],
            revid=1, prompt_version="p1", model="m",
        )
        stored = store.connection.execute(
            "SELECT section_id, section_ordinal, passage FROM events"
        ).fetchone()
        assert tuple(stored) == (section, 0, ""), "the row anchors on its section"
        snapshot = store.reset()
        new_section, _, _ = self._rebuild(store)
        report = store.remap_derived(snapshot)
        assert report["events"]["remapped"] == 1
        assert report["events"]["unverified"] == 0
        row = store.connection.execute(
            "SELECT section_id, section_ordinal, passage FROM events"
        ).fetchone()
        assert tuple(row) == (new_section, 0, ""), "re-keyed onto the new build"
"""The threaded extraction driver is a sliding window (2026-09-29, review R11).

The old loop mapped `workers * 4` pages and waited for the slowest before the
next chunk, idling every other LLM slot behind one long page. The window keeps
every slot busy; what it must not change is what lands in the store. These
tests drive the threaded path with a stub model whose pages finish out of order
(and one that fails) and check it stores exactly what the serial path stores.
"""
from __future__ import annotations

import json
import threading
import time

import pytest

from scriptengine.config import SeriesPaths, Settings
from scriptengine.ingest import events
from scriptengine.stores.facts import FactStore

PAGES = [f"Arc {i}" for i in range(9)]
FAILING = "Arc 4"
# Pages finish in reverse of the order they are submitted: the first pages
# are the slowest, so a chunk-and-wait loop and a window diverge in timing.
DELAY = {page: 0.02 * (len(PAGES) - i) for i, page in enumerate(PAGES)}

ANSWER = {
    "events": [
        {
            "subject": "Steve",
            "verb": "fought",
            "object": "Peggy",
            "quote": "Steve fights Peggy at the laboratory",
        }
    ]
}


class SlowStub:
    """`LLMClient`'s surface: a per-page delay, one page that fails."""

    lock = threading.Lock()
    in_flight = 0
    peak = 0

    def __init__(self, settings: Settings | None = None, workdir: str = "") -> None:
        pass

    def available(self) -> bool:
        return True

    def complete(self, prompt: str, system: str = "", temperature: float = 0.2,
                 max_tokens: int = 1024, extra_body: dict | None = None) -> str:
        page = next((p for p in PAGES if f"{p}\n" in prompt or f"{p}:" in prompt
                     or f'"{p}"' in prompt or p in prompt), None)
        cls = type(self)
        with cls.lock:
            cls.in_flight += 1
            cls.peak = max(cls.peak, cls.in_flight)
        try:
            time.sleep(DELAY.get(page, 0.01))
            if page == FAILING:
                raise RuntimeError("stub failure")
            return json.dumps(ANSWER)
        finally:
            with cls.lock:
                cls.in_flight -= 1


def _series(tmp_path, name: str) -> SeriesPaths:
    root = tmp_path / name
    root.mkdir()
    store = FactStore(root / "facts.db")
    store.initialise()
    for title in PAGES:
        doc = store.add_document(
            title=title, url="", page_type="event",
            infobox_template="Event Infobox", lead="",
            word_count=21, revid=1, fetched_at="",
        )
        store.add_section(
            document_id=doc, title="Plot", breadcrumb=f"{title}/Plot", level=2,
            ordinal=0,
            text=(f"In {title} the laboratory explodes as Steve fights Peggy at"
                  " the laboratory and the fight continues for several minutes"
                  " before Steve finally wins."),
            word_count=24,
        )
    for person in ("Steve", "Peggy"):
        doc = store.add_document(
            title=person, url="", page_type="character",
            infobox_template="Character Infobox",
            lead=f"{person} is a character in the series.",
            word_count=7, revid=1, fetched_at="",
        )
        store.add_node(person, "character", doc)
    store.commit()
    store.close()
    return SeriesPaths(name=name, root=root)


def _rows(paths: SeriesPaths) -> list[tuple]:
    with FactStore(paths.facts_db) as store:
        store.ensure_events()
        return sorted(
            tuple(row) for row in store.connection.execute(
                "SELECT arc_key, subject_node, verb, object_node, section_id,"
                " quote, passage FROM events"
            )
        )


@pytest.fixture()
def stub(monkeypatch):
    SlowStub.in_flight = SlowStub.peak = 0
    monkeypatch.setattr(events, "LLMClient", SlowStub)


def test_window_stores_what_the_serial_path_stores(tmp_path, stub):
    settings = Settings(series_root=tmp_path, llm_model="stub")
    serial = _series(tmp_path, "serial")
    threaded = _series(tmp_path, "threaded")

    one = events.extract_events_series(serial, settings=settings, workers=1)
    many = events.extract_events_series(threaded, settings=settings, workers=3)

    # Section ids are per-store but assigned in the same order, so the row
    # sets compare exactly.
    assert _rows(threaded) == _rows(serial)
    for key in ("considered", "extracted", "failed", "events", "proposed", "kept"):
        assert many[key] == one[key], key
    assert many["failed"] == 1 and many["extracted"] == len(PAGES) - 1


def test_window_keeps_every_slot_busy(tmp_path, stub):
    settings = Settings(series_root=tmp_path, llm_model="stub")
    paths = _series(tmp_path, "busy")
    events.extract_events_series(paths, settings=settings, workers=3)
    assert SlowStub.peak == 3

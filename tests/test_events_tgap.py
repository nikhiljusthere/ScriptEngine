"""T-GAP: the extraction path is tested end to end without a network.

The council's gap: no test ever drove `extract_events_series` with a model, so
the read path (scope plan, passages, gates, store) and the write path were only
exercised in pieces. Two tests close it:

* a stub-LLM integration test drives the whole driver -- `scope_plan` to
  `save_events` -- with a canned answer, and checks the row that lands in the
  store and the accounting around it (one event kept, the unquoted lead
  candidate counted, a re-run cached);
* a CLI dry-run smoke proves `events-extract --dry-run` lists what it would
  read and constructs no model at all.
"""

from __future__ import annotations

import json

import pytest

from scriptengine.cli import app as cli_app
from scriptengine.config import SeriesPaths, Settings, get_settings
from scriptengine.ingest import events
from scriptengine.stores.facts import FactStore

# The one answer the model ever gives. `fought` is in the closed eventive set;
# the quote is verbatim in the Plot section and in no other passage, so the
# section row is kept and the lead candidate is the counted `unquoted` class.
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


class StubLLMClient:
    """`LLMClient`'s surface, canned: `available` + `complete`, no network."""

    instances: list[StubLLMClient] = []

    def __init__(self, settings: Settings | None = None, workdir: str = "") -> None:
        self.settings = settings
        self.calls: list[str] = []
        type(self).instances.append(self)

    def available(self) -> bool:
        return True

    def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.2,
        max_tokens: int = 1024,
        extra_body: dict | None = None,
    ) -> str:
        self.calls.append(prompt)
        return json.dumps(ANSWER)


class NoModelAllowed:
    """A model constructor that fails loudly if a dry run ever reaches it."""

    attempts = 0

    def __new__(cls, *args: object, **kwargs: object) -> "NoModelAllowed":
        cls.attempts += 1
        raise AssertionError("the dry run must not construct a model")


@pytest.fixture()
def series(tmp_path, monkeypatch):
    """One indexed series: an event page, two resolved characters, no axis."""
    root = tmp_path / "tgap"
    root.mkdir()
    store = FactStore(root / "facts.db")
    store.initialise()
    doc = store.add_document(
        title="Test Arc", url="", page_type="event",
        infobox_template="Event Infobox",
        lead="The arc opens with Steve fighting Peggy.",
        word_count=8, revid=1, fetched_at="",
    )
    # 21 words: above the 20-word prose floor `placement_pages` applies, so the
    # event page weighs into the placement queue (a shorter section would leave
    # it out and the driver would read nothing).
    section = store.add_section(
        document_id=doc, title="Plot", breadcrumb="Test Arc/Plot", level=2,
        ordinal=0,
        text=("The laboratory explodes as Steve fights Peggy at the laboratory"
              " and the fight continues for several minutes before Steve"
              " finally wins."),
        word_count=21,
    )
    # The character nodes must be backed by their own character pages: a node
    # backed by a placement-type (container) page is excluded from the
    # participant pool, so events cannot point at it.
    steve_doc = store.add_document(
        title="Steve", url="", page_type="character",
        infobox_template="Character Infobox",
        lead="Steve is a character in the series.",
        word_count=7, revid=1, fetched_at="",
    )
    peggy_doc = store.add_document(
        title="Peggy", url="", page_type="character",
        infobox_template="Character Infobox",
        lead="Peggy is a character in the series.",
        word_count=7, revid=1, fetched_at="",
    )
    steve = store.add_node("Steve", "character", steve_doc)
    peggy = store.add_node("Peggy", "character", peggy_doc)
    store.commit()
    store.close()

    StubLLMClient.instances = []
    settings = Settings(series_root=tmp_path, llm_model="stub")
    monkeypatch.setattr(events, "LLMClient", StubLLMClient)
    yield SeriesPaths(name="tgap", root=root), settings, section, steve, peggy


def test_driver_stores_the_stubbed_event(series):
    paths, settings, section, steve, peggy = series
    report = events.extract_events_series(paths, settings=settings)

    # One page considered and extracted; the section row stored, nothing failed.
    assert report["considered"] == 1
    assert report["extracted"] == 1
    assert report["failed"] == 0
    assert report["events"] == 1
    assert report["proposed"] == 1
    assert report["kept"] == 1
    assert StubLLMClient.instances and len(StubLLMClient.instances[0].calls) == 1

    with FactStore(paths.facts_db) as store:
        store.ensure_events()
        row = store.connection.execute(
            "SELECT subject_node, verb, object_node, section_id, quote"
            " FROM events WHERE arc_key = 'Test Arc'"
        ).fetchone()
    assert row is not None
    assert row["subject_node"] == steve
    assert row["verb"] == "fought"
    assert row["object_node"] == peggy
    assert row["section_id"] == section
    assert row["quote"] == "Steve fights Peggy at the laboratory"


def test_driver_caches_the_rerun(series):
    paths, settings = series[0], series[1]
    events.extract_events_series(paths, settings=settings)
    calls_after_first = len(StubLLMClient.instances[0].calls)

    report = events.extract_events_series(paths, settings=settings)
    assert report["cached"] == 1
    assert report["extracted"] == 0
    assert len(StubLLMClient.instances[0].calls) == calls_after_first


def test_all_scope_reads_the_lead_and_counts_the_unquoted(series):
    paths, settings, _, _, _ = series
    report = events.extract_events_series(
        paths, settings=settings, scope="all"
    )

    # The all scope adds the lead passage: two model calls, and the lead's
    # candidate -- whose quote is verbatim in no lead sentence -- is the
    # counted `unquoted` class, not a silence.
    assert len(StubLLMClient.instances[0].calls) == 2
    assert report["events"] == 1
    assert report["dropped"]["unquoted"] == 1


def test_cli_dry_run_lists_pages_and_calls_no_model(series, tmp_path, monkeypatch):
    paths, settings = series[0], series[1]
    NoModelAllowed.attempts = 0
    monkeypatch.setattr(events, "LLMClient", NoModelAllowed)
    monkeypatch.setenv("SCRIPTENGINE_SERIES_ROOT", str(tmp_path))
    get_settings.cache_clear()
    try:
        from typer.testing import CliRunner

        result = CliRunner().invoke(
            cli_app, ["events-extract", "--series", "tgap", "--dry-run"]
        )
        assert result.exit_code == 0, result.output
        assert "would be read" in result.output
        assert "Test Arc" in result.output
        assert "Plot" in result.output
        assert NoModelAllowed.attempts == 0
    finally:
        get_settings.cache_clear()

def test_a_small_page_is_read_in_one_packed_call(series, monkeypatch):
    """Owner 2026-09-29: "smaller pages can be read in whole". With the pack
    size set, the lead and the Plot section go in one call, and the row is
    still anchored to the passage that holds its quote (the section)."""
    paths, settings, section, steve, peggy = series
    monkeypatch.setenv("SCRIPTENGINE_EVENTS_PACK_CHARS", "10000")
    report = events.extract_events_series(
        paths, settings=settings, scope="all"
    )

    assert len(StubLLMClient.instances[0].calls) == 1
    assert report["events"] == 1
    assert report["dropped"]["unquoted"] == 0
    with FactStore(paths.facts_db) as store:
        store.ensure_events()
        row = store.connection.execute(
            "SELECT section_id, passage, subject_node, object_node FROM events"
        ).fetchone()
    assert row["section_id"] == section and row["passage"] == ""
    assert (row["subject_node"], row["object_node"]) == (steve, peggy)


def test_a_page_over_the_pack_size_is_read_per_passage(series, monkeypatch):
    paths, settings, _, _, _ = series
    monkeypatch.setenv("SCRIPTENGINE_EVENTS_PACK_CHARS", "50")
    events.extract_events_series(paths, settings=settings, scope="all")
    assert len(StubLLMClient.instances[0].calls) == 2


def test_the_model_mention_is_stored_beside_the_resolved_name(series):
    """R12: the raw mention survives, so a resolver fix can re-resolve stored
    rows instead of re-reading the corpus."""
    paths, settings, _, _, _ = series
    events.extract_events_series(paths, settings=settings)
    with FactStore(paths.facts_db) as store:
        store.ensure_events()
        row = store.connection.execute(
            "SELECT subject_mention, object_mention FROM events").fetchone()
    assert (row["subject_mention"], row["object_mention"]) == ("Steve", "Peggy")


def test_a_reread_that_finds_nothing_clears_the_old_rows(series, monkeypatch):
    """A passage re-read under a new model or prompt that yields no rows must
    not keep the previous run's rows (2026-09-29 model trials: 23 stale rows
    survived on re-read pages)."""
    paths, settings, _, _, _ = series
    events.extract_events_series(paths, settings=settings)

    class EmptyStub(StubLLMClient):
        def complete(self, prompt, system="", temperature=0.2,
                     max_tokens=1024, extra_body=None):
            self.calls.append(prompt)
            return json.dumps({"events": []})

    monkeypatch.setattr(events, "LLMClient", EmptyStub)
    report = events.extract_events_series(paths, settings=settings, refresh=True)
    assert report["extracted"] == 1 and report["events"] == 0
    with FactStore(paths.facts_db) as store:
        store.ensure_events()
        left = store.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert left == 0


def test_a_wiki_declares_its_extra_verbs(tmp_path):
    """events: extra_verbs extends the closed set for that wiki only; a wiki
    that declares nothing keeps the shared set (JJK/CSM byte-identical)."""
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    assert events.eventive_verbs(store) == events.EVENTIVE_VERBS
    (tmp_path / "overrides.yaml").write_text(
        "events:\n  extra_verbs: [defeated, Escaped]\n", encoding="utf-8")
    assert events.eventive_verbs(store) == events.EVENTIVE_VERBS | {"defeated", "escaped"}
    store.close()


def test_null_object_is_self_only_for_awakened_and_incomplete_otherwise(series, monkeypatch):
    paths, settings, _, steve, _ = series

    class NullObjectStub(StubLLMClient):
        def complete(self, prompt, system="", temperature=0.2,
                     max_tokens=1024, extra_body=None):
            self.calls.append(prompt)
            return json.dumps({"events": [
                {"subject": "Steve", "verb": "awakened", "object": None,
                 "quote": "Steve fights Peggy at the laboratory"},
                {"subject": "Steve", "verb": "fought", "object": None,
                 "quote": "Steve fights Peggy at the laboratory"},
            ]})

    monkeypatch.setattr(events, "LLMClient", NullObjectStub)
    report = events.extract_events_series(paths, settings=settings)
    assert report["dropped"]["incomplete"] == 1
    with FactStore(paths.facts_db) as store:
        store.ensure_events()
        rows = store.connection.execute(
            "SELECT verb, subject_node, object_node FROM events").fetchall()
    assert [(r["verb"], r["subject_node"], r["object_node"]) for r in rows] == [
        ("awakened", steve, steve)]


def test_the_system_prompt_describes_only_the_wikis_verbs():
    shared = events.system_prompt(events.EVENTIVE_VERBS)
    extended = events.system_prompt(events.EVENTIVE_VERBS | {"defeated"})
    assert "- defeated:" not in shared and "- defeated:" in extended
    # The page never enters the shared prefix (the prefix cache's premise).
    assert "{page}" not in shared and "Page:" not in shared


def test_verify_sets_the_confidence_flag_and_skips_checked_rows(series, monkeypatch):
    paths, settings, _, _, _ = series
    events.extract_events_series(paths, settings=settings)

    class YesStub(StubLLMClient):
        def complete(self, prompt, system="", temperature=0.2,
                     max_tokens=1024, extra_body=None):
            self.calls.append(prompt)
            assert "Steve fights Peggy at the laboratory" in prompt
            assert "- fought:" in system
            return "Yes"

    monkeypatch.setattr(events, "LLMClient", YesStub)
    tally = events.verify_events(paths, settings=settings, workers=2)
    assert tally["checked"] == 1 and tally["yes"] == 1
    with FactStore(paths.facts_db) as store:
        store.ensure_events()
        assert store.connection.execute(
            "SELECT verified FROM events").fetchone()[0] == 1
    assert events.verify_events(paths, settings=settings)["checked"] == 0


def test_an_empty_reply_is_retried_before_the_page_fails(series, monkeypatch):
    paths, settings, _, _, _ = series
    from scriptengine.llm.client import LLMUnavailable

    class FlakyStub(StubLLMClient):
        empties = 2

        def complete(self, prompt, system="", temperature=0.2,
                     max_tokens=1024, extra_body=None):
            self.calls.append(prompt)
            if type(self).empties:
                type(self).empties -= 1
                raise LLMUnavailable("stub returned no content.")
            return json.dumps(ANSWER)

    monkeypatch.setattr(events, "LLMClient", FlakyStub)
    report = events.extract_events_series(paths, settings=settings)
    assert report["failed"] == 0 and report["events"] == 1

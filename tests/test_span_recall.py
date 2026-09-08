"""Tests for span-recall: line-level reachability of an indexed corpus."""

from __future__ import annotations

import pytest

from scriptengine.eval import span_recall as sr
from scriptengine.stores.facts import FactStore


# --------------------------------------------------------------- segmentation

def test_citation_hanging_off_a_full_stop_still_ends_a_sentence():
    """The corpus writes "...a cliff.(Chapter 151) He thinks...", no space.

    A naive `(?<=[.!?])\\s+` split welds the two together and then probes with
    the blob. On the JJK corpus that hid ~5,400 sentences inside neighbours.
    """
    text = ("Maki was thrown into a cliff by the attack.(Chapter 151) "
            "He thinks to himself about how she is not Toji after all.")
    out = sr.sentences(text, min_words=6)
    assert len(out) == 2
    assert out[0].endswith("(Chapter 151)")
    assert out[1].startswith("He thinks")


def test_abbreviation_does_not_end_a_sentence():
    text = "Mr. Takagi made a deal with the boy about joining the Occult Club."
    assert sr.sentences(text, min_words=6) == [text]


def test_short_fragments_and_table_rows_are_not_probes():
    """Neither carries enough signal to query with; both yield false alarms."""
    assert sr.sentences("He fell down.", min_words=6) == []
    row = "Start | End | Title | Album | 00:02 | 00:25 | Your Battle Is Mine"
    assert sr.sentences(row, min_words=6) == []


# ----------------------------------------------------------------- comparison

def test_decite_lets_prose_be_compared_against_prose():
    """Sections render "(Chapter 143)" where beats render "(Chapter 143, Episode 49)".

    Comparing raw text fails on the citation rather than the prose -- measured
    at 71% of apparent span-misses against under 10% of hits.
    """
    section = "Yuji was born in Sendai City.(Chapter 143)"
    beat = "Yuji was born in Sendai City.(Chapter 143, Episode 49)"
    assert section not in beat
    assert sr.decite(section) in sr.decite(beat)


def test_boilerplate_excludes_link_lists_but_never_references():
    # References carries real trivia prose on chapter pages -- excluding it
    # would have hidden a genuine chunking gap.
    assert sr.is_boilerplate("Navigation")
    assert sr.is_boilerplate("  See Also  ")
    assert not sr.is_boilerplate("References")
    assert not sr.is_boilerplate("Synopsis / Culling Game Arc")


# -------------------------------------------------------------------- tier 0

@pytest.fixture()
def series(tmp_path, monkeypatch):
    """A one-document series whose Trivia section is deliberately unchunked."""
    root = tmp_path / "series"
    (root / "demo").mkdir(parents=True)
    store = FactStore(root / "demo" / "facts.db")
    store.initialise()
    doc = store.add_document(
        title="Chapter 1", url="http://example/1", page_type="chapter",
        infobox_template="", lead="", word_count=0, revid=1, fetched_at="",
    )
    covered = "Yuji throws the chunk of building at the man standing there."
    orphan = "The chapter title is a reference to a song by another artist."
    store.add_section(document_id=doc, title="Plot Details",
                      breadcrumb="Plot Details", level=2, ordinal=1,
                      text=covered, word_count=len(covered.split()))
    store.add_section(document_id=doc, title="References",
                      breadcrumb="References", level=2, ordinal=2,
                      text=orphan, word_count=len(orphan.split()))
    store.add_section(document_id=doc, title="Navigation",
                      breadcrumb="Navigation", level=2, ordinal=3,
                      text="Chapter 1 Chapitre 1 Capitulo 1 Kapitel 1 Hoofdstuk",
                      word_count=5)
    # Only the plot prose is chunked -- References is left out on purpose.
    store.add_chunk(document_id=doc, section_id=None, parent_id=None, level=2,
                    ordinal=1, doc_title="Chapter 1", breadcrumb="Plot Details",
                    text=covered)
    store.commit()
    store.close()

    monkeypatch.setenv("SCRIPTENGINE_SERIES_ROOT", str(root))
    return root


def test_index_coverage_finds_an_unchunked_section(series):
    from scriptengine.config import Settings

    result = sr.index_coverage("demo", Settings(series_root=series), min_words=6)
    assert result["missing"] == 1
    miss = result["misses"][0]
    assert miss["breadcrumb"] == "References"
    assert miss["doc_has_chunks"] is True   # the doc indexed; the section did not
    assert result["coverage"] < 1.0


def test_navigation_boilerplate_is_excluded_by_default(series):
    """Interwiki name lists are dropped on purpose; counting them buries findings."""
    from scriptengine.config import Settings

    settings = Settings(series_root=series)
    default = sr.index_coverage("demo", settings, min_words=6)
    audited = sr.index_coverage("demo", settings, min_words=6,
                                include_boilerplate=True)
    assert default["boilerplate_skipped"] == 1
    assert audited["missing"] > default["missing"]


def test_missing_index_is_an_error_not_a_score(tmp_path):
    from scriptengine.config import Settings

    with pytest.raises(sr.SpanRecallError):
        sr.index_coverage("nope", Settings(series_root=tmp_path))


# --------------------------------------------------- CSM-3 (D5 infrastructure)

def test_tier0_command_is_registered_under_both_names():
    """CSM-3(f): tier 0 is `chunk-containment`; `span-recall` stays an alias."""
    from scriptengine.cli import app

    names = {c.name for c in app.registered_commands}
    assert {"chunk-containment", "span-recall"} <= names


@pytest.fixture()
def panel_series(tmp_path, monkeypatch):
    """Two fully-chunked documents: 7 in-floor sentences + one 5-word line."""
    root = tmp_path / "series"
    (root / "demo").mkdir(parents=True)
    store = FactStore(root / "demo" / "facts.db")
    store.initialise()
    docs = [
        ("Chapter 1", [
            "Yuji throws the chunk of building at the man standing there.",
            "The chapter title is a reference to a song by another artist.",
            "Maki walks to the edge of the street and waits for the bus.",
            "Nobara's hammer is stored in a closet behind the school gate.",
        ]),
        ("Chapter 2", [
            "Suguru Geto watches the festival from the rooftop of the hall.",
            "The festival lantern is hung from the old cherry tree outside.",
            "A crowd gathers around the food stalls before the parade begins.",
        ]),
    ]
    for title, sents in docs:
        doc = store.add_document(
            title=title, url=f"http://example/{title}", page_type="chapter",
            infobox_template="", lead="", word_count=0, revid=1, fetched_at="",
        )
        text = " ".join(sents) + " This is a short line."
        store.add_section(document_id=doc, title="Plot Details",
                          breadcrumb="Plot Details", level=2, ordinal=1,
                          text=text, word_count=len(text.split()))
        store.add_chunk(document_id=doc, section_id=None, parent_id=None, level=2,
                        ordinal=1, doc_title=title, breadcrumb="Plot Details",
                        text=text)
    store.commit()
    store.close()
    monkeypatch.setenv("SCRIPTENGINE_SERIES_ROOT", str(root))
    return root


def test_build_panel_is_deterministic_and_held_out_is_disjoint(panel_series):
    """A pinned panel must not shuffle: two builds, same order, same hash."""
    from scriptengine.config import Settings

    settings = Settings(series_root=panel_series)
    a = sr.build_panel("demo", settings, min_words=6, held_out=2)
    b = sr.build_panel("demo", settings, min_words=6, held_out=2)
    assert a["panel"] == b["panel"]
    assert a["hash"] == b["hash"]
    assert a["panel_size"] == 5 and a["held_out_size"] == 2  # 7 in-floor lines
    assert not (set(map(tuple, a["panel"])) & set(map(tuple, a["held_out"])))
    # the 5-word line stays out of the panel (the declared floor)
    all_rows = [tuple(r) for r in a["panel"] + a["held_out"]]
    assert all(len(row[2].split()) >= 6 for row in all_rows)


def _bundle(title: str, sentence: str) -> dict:
    return {"mode": "qa", "truncated": False,
            "beats": [{"doc_title": title, "text": sentence}]}


def test_panel_resume_is_idempotent_and_hit_rate_uses_full_panel(tmp_path,
                                                                   monkeypatch):
    """Resume keyed (title, sentence), jsonl rewritten not append-duped, and
    hit_rate over the full panel (a partial run must not read as a rate).
    """
    import json

    panel = [("Chapter 1", "Plot Details",
              f"Probe sentence number {i} for the panel test.") for i in range(4)]
    results = tmp_path / "sweep_qa.jsonl"

    calls = {"n": 0}

    def flaky(query, series_, timeout, base, door=None):
        calls["n"] += 1
        if calls["n"] <= 2:  # a crash-like run: two served, two failed
            return _bundle("Chapter 1", query)
        raise ConnectionError("server went away")

    monkeypatch.setattr(sr, "_ask", flaky)
    r1 = sr.recall("demo", panel=panel, results_path=results, door="qa")
    assert r1["counts"] == {"HIT": 2, "MISS_DOC": 0, "MISS_SPAN": 0,
                            "TRUNCATED": 0, "ERROR": 2}
    assert r1["hit_rate"] == 0.5  # 2 of the 4-probe panel, not 2/2

    def fixed(query, series_, timeout, base, door=None):
        return _bundle("Chapter 1", query)

    monkeypatch.setattr(sr, "_ask", fixed)
    r2 = sr.recall("demo", panel=panel, results_path=results, door="qa")
    assert r2["probes"] == 4 and r2["counts"]["HIT"] == 4
    assert r2["hit_rate"] == 1.0
    rows = [json.loads(l) for l in
            results.read_text(encoding="utf-8").splitlines() if l]
    assert len(rows) == 4  # the ERROR rows were re-probed, nothing duplicated

    r3 = sr.recall("demo", panel=panel, results_path=results, door="qa")
    assert r3["probes"] == 4 and r3["counts"]["HIT"] == 4
    rows = [json.loads(l) for l in
            results.read_text(encoding="utf-8").splitlines() if l]
    assert len(rows) == 4  # a second resume is a no-op


def test_door_is_forwarded_to_the_context_request(tmp_path, monkeypatch):
    seen = []

    def spy(query, series_, timeout, base, door=None):
        seen.append(door)
        return {"mode": "narrative", "truncated": False,
                "beats": [{"doc_title": "Chapter 1", "text": query}]}

    monkeypatch.setattr(sr, "_ask", spy)
    sr.recall("demo",
              panel=[("Chapter 1", "Plot", "One narrative door probe sentence here.")],
              results_path=tmp_path / "sweep_narrative.jsonl", door="narrative")
    assert seen == ["narrative"]

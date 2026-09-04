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

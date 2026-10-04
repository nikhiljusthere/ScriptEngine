"""The window builder (2026-09-30, windowing-100 council).

A window is a span of whole-sentence ordinals over the index's sentence
grid, one sub-topic per window, packed to a 2,000-char cap with a
whole-sentence carry -- never a character slice. These tests pin the
invariants the verdict stands on:

* the grid is the index's grid (the chunker's, byte-identical);
* a window's text is a verbatim section slice;
* the windows' hashes union to the section's whole grid (no sentence
  goes unread);
* no window crosses a sub-topic boundary;
* the cap holds (except a single oversized sentence, counted);
* the carry: the next window re-reads the previous one's tail, so a
  quote of at most cap-carry chars that straddles a cut sits wholly in
  the next window;
* ids are content-addressed (the window's sentence-hash list is in the
  key: same-titled sections with different text are distinct windows,
  identical text collapses to one) and stable within a generation,
  16 hex like the old pool's;
* and the council's process gate: the builder run over the whole JJK
  store at zero LLM cost, reporting the window-count delta against the
  old character-sliced windows before the 300k-page scale-out is priced.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from scriptengine.ingest.abilities import _windows
from scriptengine.ingest.windows import (
    CURRENT_GEN,
    DEFAULT_CAP_CHARS,
    DEFAULT_CARRY_CHARS,
    Window,
    build_windows,
    quote_sentence_span,
    section_subtopics,
    sentence_spans,
    window_id,
)
from scriptengine.index.chunker import _section_items, split_sentences

# ── Fixtures ───────────────────────────────────────────────────────────────

# A technique-list section: a bare heading joining the entry it heads, then
# label lines one per item, 3+ items so the section is item-ized.
TECHNIQUES = (
    "Innate Technique\n"
    "Simple Domain: A barrier technique that neutralizes an enemy domain's sure hit.\n"
    "\n"
    "Cursed Tool: A sword that channels cursed energy into its edge.\n"
    "\n"
    "Curse Manipulation: The user redirects a curse's momentum back at its caster.\n"
)

# Prose, one item (a paragraph): the section is a single sub-topic that
# packs and carries on its own.
def prose(n: int) -> str:
    return " ".join(
        f"Sentence {k} states that the jujutsu sorcerer's domain extends {k} "
        "meters into the void and its sure-hit effect follows the user."
        for k in range(1, n + 1)
    )


def section_windows(n: int, **kw) -> tuple[str, list[Window]]:
    text = prose(n)
    return text, build_windows("Page One", "Abilities", text, **kw)


def _cast_variant(brand: str) -> str:
    """Same shape (same sentence count and lengths), different text: the
    doc-545 "Cast" collision in miniature -- the spans (sub, s_start,
    s_end) are identical across brands, only the content differs."""
    return " ".join(
        f"Member {k} of {brand} is a sorcerer of the Tokyo jujutsu branch."
        for k in range(1, 41)
    )


# ── The grid is the index's grid ──────────────────────────────────────────


def test_grid_matches_chunker_on_tricky_text():
    """sentence_spans mirrors split_sentences: same sentences, same order,
    with a character span each. Tricky cases: the citation locator (the cut
    waits for it), the abbreviation re-join across a line break, and
    Japanese, which must not break the [A-Z0-9] lookahead."""
    tricky = (
        "Megumi took over Geto's body.(Chapter 145, Episode 50) Now known "
        "as the Jogo, Vol. 5\nCh. 12 records the domain's first use."
        " 呪術師の領域は発動した。"
    )
    spans = sentence_spans(tricky)
    assert [s[2] for s in spans] == split_sentences(tricky)
    # Every span is the sentence's own characters in the text, in order.
    for start, end, sentence in spans:
        assert tricky[start:end].strip() == sentence
        assert start < end
    assert spans == sorted(spans, key=lambda s: s[0])


def test_grid_matches_chunker_on_empty_and_plain():
    assert sentence_spans("") == []
    assert [s[2] for s in sentence_spans("One. Two! Three?")] == split_sentences(
        "One. Two! Three?"
    )


def test_grid_spans_cover_abbreviation_merges():
    """A merged sentence keeps the first piece's start and the last piece's
    end, so the window slice covers the whole merged sentence even when the
    section wrote it across a line break."""
    spans = sentence_spans("Rank Vol. 5\nCh. 12 lists the tools.")
    sentences = [s[2] for s in spans]
    assert sentences == split_sentences("Rank Vol. 5\nCh. 12 lists the tools.")
    assert len(spans) == 1
    start, end, merged = spans[0]
    assert "Rank Vol. 5\nCh. 12 lists the tools."[:start].strip() == ""
    # The chunker's merge joins the re-split pieces with a single space but
    # keeps each piece's own text, so the line break inside "5\nCh."
    # survives: the grid sentence is the section's own characters, and the
    # window slice covering the span re-splits to the very same sentence.
    assert merged == "Rank Vol. 5\nCh. 12 lists the tools."
    assert "Vol. 5\nCh. 12" in "Rank Vol. 5\nCh. 12 lists the tools."[start:end]


# ── Sub-topics are the wiki's own items ───────────────────────────────────


def test_subtopics_match_the_index_itemizer():
    """The sub-topic count and grouping agree with the index itemizer the
    chunker runs, so the extractor's topicing cannot drift from the
    index's itemization."""
    from scriptengine.index.chunker import _section_items

    assert len(section_subtopics(TECHNIQUES)) == len(_section_items(TECHNIQUES)) == 3
    # A bare heading is not an item: it heads the entry below and joins it.
    items = _section_items(TECHNIQUES)
    assert items[0].startswith("Innate Technique Simple Domain:")
    subs = section_subtopics(TECHNIQUES)
    assert subs[0].title == "Innate Technique"
    assert "Simple Domain:" in TECHNIQUES[subs[0].start : subs[0].end]
    # The items tile the section: no gaps, in order.
    assert subs[0].start == 0
    for earlier, later in zip(subs, subs[1:]):
        assert earlier.end == later.start
    assert subs[-1].end == len(TECHNIQUES)


def test_short_section_is_one_subtopic():
    """Fewer than three items is the index's own threshold: the whole
    section is one sub-topic, and a marker-free section never segments."""
    subs = section_subtopics(prose(40))
    assert len(subs) == 1
    assert subs[0].title == ""
    assert subs[0].start == 0 and subs[0].end == len(prose(40))
    assert section_subtopics("") == [] or len(section_subtopics("")) == 1


# ── The window invariants ─────────────────────────────────────────────────


def test_windows_are_verbatim_section_slices():
    """A window's text is section_text[start:end] for the slice between its
    first and last sentence: every character a quote in the window covers
    is in the section it was read from."""
    text, windows = section_windows(30)
    assert windows
    spans = sentence_spans(text)
    for window in windows:
        assert window.text == text[spans[window.s_start][0] : spans[window.s_end][1]]
        assert window.text in text
        assert window.chars == len(window.text)


def test_windows_never_cut_a_sentence():
    """A window starts and ends on a grid sentence: its hash list is
    exactly its span's, and its text re-splits to the same number of
    sentences -- whole sentences in, whole sentences out."""
    from scriptengine.index.chunker import sentence_content_hash

    text, windows = section_windows(30)
    grid = [s[2] for s in sentence_spans(text)]
    for window in windows:
        assert window.hashes == tuple(
            sentence_content_hash(s) for s in grid[window.s_start : window.s_end + 1]
        )
        assert len(split_sentences(window.text)) == window.s_end - window.s_start + 1


def test_hash_union_covers_the_grid():
    """No sentence goes unread: the windows' hashes union to the section's
    whole grid, and each window's hashes are exactly its span's."""
    from scriptengine.index.chunker import sentence_content_hash

    text, windows = section_windows(30)
    grid = [sentence_content_hash(s) for s in [t for _a, _b, t in sentence_spans(text)]]
    union: set[str] = set()
    for window in windows:
        assert window.hashes == tuple(grid[window.s_start : window.s_end + 1])
        assert len(window.hashes) == window.s_end - window.s_start + 1
        union.update(window.hashes)
    assert union == set(grid)


def test_no_window_crosses_a_subtopic():
    """A sub-topic boundary always ends a window, so one window is one
    topic: the n=0 class (a multi-topic window whose events are
    attributed to none of its topics) is structurally impossible. Every
    sub-topic also gets its windows: a boundary never drops the rest of
    the section (the drop the old break had)."""
    from scriptengine.index.chunker import sentence_content_hash

    windows = build_windows("Page One", "Cursed Techniques", TECHNIQUES)
    subs = section_subtopics(TECHNIQUES)
    spans = sentence_spans(TECHNIQUES)
    sub_starts = [sub.start for sub in subs]
    import bisect

    for window in windows:
        first = max(0, bisect.bisect_right(sub_starts, spans[window.s_start][0]) - 1)
        last = max(0, bisect.bisect_right(sub_starts, spans[window.s_end][0]) - 1)
        assert first == last == window.sub
        assert window.text and window.id
    # Every sub-topic is reached: one window per sub-topic here (each is a
    # single-sentence entry), and the hashes union to the whole grid.
    assert [w.sub for w in windows] == list(range(len(subs)))
    grid = [sentence_content_hash(s) for s in (t for _a, _b, t in spans)]
    union: set[str] = set()
    for window in windows:
        union.update(window.hashes)
    assert union == set(grid)


def test_cap_held():
    """Every window fits the 2,000-char cap; the cap is measured on the
    verbatim slice, the section's own whitespace included."""
    _text, windows = section_windows(40)
    assert windows
    for window in windows:
        assert window.chars <= DEFAULT_CAP_CHARS


def test_oversized_sentence_gets_its_own_window():
    """A single sentence longer than the cap cannot be cut: it gets its
    own window, over the cap, and the caller can count it -- the window is
    a view, and a view cannot hide a character."""
    long_sentence = "The domain expansion " + "boundless " * 400 + "engulfs the field."
    text = f"Intro line one.\n{long_sentence}\nOutro line two."
    windows = build_windows("Page", "Domain", text)
    big = [w for w in windows if w.chars > DEFAULT_CAP_CHARS]
    assert len(big) == 1
    assert big[0].s_start == big[0].s_end  # a single sentence, uncut
    assert long_sentence in big[0].text
    # The neighbours still pack normally around it.
    assert sum(w.chars for w in windows) >= len(text) - 3


def test_carry_re_reads_the_tail():
    """The next window starts at the previous one's tail, back over the
    longest whole-sentence run that fits under the carry -- at least two
    sentences while the tail allows, never more than the carry's chars."""
    text, windows = section_windows(40)
    assert len(windows) >= 2
    for earlier, later in zip(windows, windows[1:]):
        # Progress: the next window starts at or inside the previous one.
        assert later.s_start <= earlier.s_end
        # The re-read is the carry: whole sentences, bounded by the cap.
        carried = earlier.s_end - later.s_start + 1
        assert carried >= 1
        carry_chars = len(
            text[
                spans_start(text, later.s_start) : spans_end(text, earlier.s_end)
            ]
        )
        # Either the carry fits the bound, or the last sentence alone is
        # over it (the documented exception).
        last_sentence = _sentence_at(text, earlier.s_end)
        assert carry_chars <= DEFAULT_CARRY_CHARS or last_sentence is not None and len(last_sentence) > DEFAULT_CARRY_CHARS
        # Two sentences while the tail allows: equal-length prose sentences
        # here, so a 1-sentence carry means even the pair was over bound.
        if carried == 1:
            pair = _sentence_at(text, earlier.s_end - 1) + " " + last_sentence
            assert len(pair) > DEFAULT_CARRY_CHARS


def test_quote_of_cap_minus_carry_is_safe_across_every_cut():
    """The council's guarantee, re-derived and made strict: with cap B and
    carry C, a quote of length at most B - C that straddles a cut (its
    pre-cut depth within the carry) sits wholly in the next window. The
    test pins the provable bound B - C - s_max - 1 -- one sentence of
    slack, so the next window's cap-bound end cannot fall short of the
    quote -- and checks it exhaustively at every start in the carry
    regions. The campaign's working bound is B - C = 1,750; the gold's
    longest quote is 231, far under either.

    The second half pins the *exact* envelope, both directions: the only
    safe-length quotes in no window at all are the straddlers whose
    pre-cut depth exceeds the carry -- the zone (end_k - safe,
    start_{k+1}) at each cut, the documented G1 loss (a quote that deep
    before the cut is not re-read, and it ends past the window that
    ends there) -- plus the tail past the section's last sentence, which
    no window can hold. Pinning both directions keeps the builder from
    silently losing, or silently claiming, a quote.
    """
    text, windows = section_windows(60)
    spans = sentence_spans(text)
    s_max = max(len(sentence) for _a, _b, sentence in spans)
    safe = DEFAULT_CAP_CHARS - DEFAULT_CARRY_CHARS - s_max - 1
    # A straddler: a quote starting in the re-read tail (the carry region
    # between two windows) ends past the earlier window's end and sits
    # wholly in the next window.
    straddled = 0
    for earlier, later in zip(windows, windows[1:]):
        p = spans[later.s_start][0]
        e = spans[earlier.s_end][1]
        assert p <= e  # the carry re-reads the tail
        for q in range(p, min(e, len(text) - safe) + 1):
            quote = text[q : q + safe]
            assert quote in later.text, (
                f"a {safe}-char quote starting {e - q} chars before the "
                "earlier window's end is not whole in the next window"
            )
            straddled += 1
    assert straddled >= 1
    # The exact envelope: a safe-length quote is in a window unless its
    # start sits in a loss zone -- (end_k - safe, start_{k+1}) at some
    # cut, where the quote ends past the window that ends there but
    # starts before the next window begins (pre-cut depth beyond the
    # carry: the G1 loss) -- or in the tail past the section's last
    # sentence, which no window can hold.
    for q in range(0, len(text) - safe + 1, 7):
        quote = text[q : q + safe]
        covered = any(quote in w.text for w in windows)
        in_loss_zone = any(
            spans[earlier.s_end][1] - safe < q < spans[later.s_start][0]
            for earlier, later in zip(windows, windows[1:])
        )
        in_tail = q > spans[windows[-1].s_end][1] - safe
        assert covered == (not in_loss_zone and not in_tail), (
            f"a {safe}-char quote at {q} is "
            f"{'covered' if covered else 'lost'} but the envelope says "
            f"{'lost' if in_loss_zone or in_tail else 'covered'}"
        )


def test_prose_section_packs_and_carries():
    """A marker-free section is one sub-topic: it packs to the cap and
    carries across its own cuts, with no sub-topic boundary involved."""
    text, windows = section_windows(25)
    assert all(w.sub == 0 for w in windows)
    assert len(windows) >= 2
    # The windows' slices, in order, cover the whole section's text.
    covered = 0
    for window in windows:
        covered = max(covered, text.find(window.text) + len(window.text))
    assert covered >= len(text) - 50  # the last carry's tail


def test_short_section_is_one_window():
    windows = build_windows("Page", "Trivia", "His favourite food is bread and ajillo.")
    assert len(windows) == 1
    assert windows[0].text == "His favourite food is bread and ajillo."
    assert windows[0].s_start == 0 and windows[0].s_end == 0


def test_empty_section_has_no_windows():
    assert build_windows("Page", "References", "") == []
    assert build_windows("Page", "References", "   \n  ") == []


# ── The id ─────────────────────────────────────────────────────────────────


def test_id_is_sixteen_hex_and_matches_the_spec():
    """sha256(gen|page|section|sub|s_start:s_end|h1|h2|...)[ :16] --
    16 hex, content-addressed (the window's sentence-hash list is in
    the key), so done-logs keyed on the id survive the supersede."""
    h1, h2, h3 = "a1" * 32, "b2" * 32, "c3" * 32
    wid = window_id(1, "Tsurugi Okkotsu", "Cursed Techniques", 0, 0, 4, (h1, h2, h3))
    assert re.fullmatch(r"[0-9a-f]{16}", wid)
    key = f"1|Tsurugi Okkotsu|Cursed Techniques|0|0:4|{h1}|{h2}|{h3}"
    assert wid == hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    assert window_id(1, "Tsurugi Okkotsu", "Cursed Techniques", 0, 0, 4, (h1, h2, h3)) == wid
    # A different generation, span, or content is a different id.
    assert window_id(2, "Tsurugi Okkotsu", "Cursed Techniques", 0, 0, 4, (h1, h2, h3)) != wid
    assert window_id(1, "Tsurugi Okkotsu", "Cursed Techniques", 0, 0, 5, (h1, h2, h3)) != wid
    assert window_id(1, "Tsurugi Okkotsu", "Cursed Techniques", 0, 0, 4, (h1, h2)) != wid


def test_ids_are_deterministic_per_generation():
    # gen=1 pinned explicitly: the default is CURRENT_GEN now, and the
    # point of the test is that gen 1 and gen 2 build disjoint ids.
    text, windows = section_windows(40, gen=1)
    again = build_windows("Page One", "Abilities", text, gen=1)
    assert [w.id for w in windows] == [w.id for w in again]
    assert len({w.id for w in windows}) == len(windows)
    gen2 = build_windows("Page One", "Abilities", text, gen=2)
    assert {w.id for w in gen2}.isdisjoint({w.id for w in windows})
    # The cross-generation invariant is the hash list, not the id: the same
    # spans keep the same hashes across generations.
    assert [w.hashes for w in windows] == [w.hashes for w in gen2]
    assert [w.s_end - w.s_start for w in windows] == [
        w.s_end - w.s_start for w in gen2
    ]


def test_same_titled_sections_with_different_text_get_distinct_ids():
    """The 2026-10-04 defect (doc 545's five "Cast" sections): the key
    without content collided id-for-id on same-titled sections of one
    page, and build_trainset.py's id-dedup silently dropped a distinct
    window. The key now carries the window's sentence-hash list, so the
    same (page, section, sub, span) with different text is a distinct
    id."""
    cast_a = build_windows("Doc 545", "Cast", _cast_variant("Ala"))
    cast_b = build_windows("Doc 545", "Cast", _cast_variant("Alb"))
    ids = [w.id for w in cast_a + cast_b]
    assert len(set(ids)) == len(ids)
    # The old key (without the hashes) really did collide here: the
    # variants are the same length, so their spans match window for
    # window and only the content separates the ids.
    assert [(w.sub, w.s_start, w.s_end) for w in cast_a] == [
        (w.sub, w.s_start, w.s_end) for w in cast_b
    ]


def test_identical_text_collapses_to_one_id():
    """Identical read = identical answer: the same (page, section) text
    builds to the same ids -- an unchanged re-ingest keeps its ids, and
    a duplicate same-titled same-text section is one window in the
    universe, not a phantom pair."""
    text = _cast_variant("Ala")
    first = build_windows("Doc 545", "Cast", text)
    again = build_windows("Doc 545", "Cast", text)
    assert [w.id for w in first] == [w.id for w in again]
    assert len({w.id for w in first}) == len(first)


def test_build_windows_defaults_to_current_gen():
    """The old default of gen=1 was a footgun: CURRENT_GEN is 2 and
    every engine caller passes gen= explicitly, so only new tooling
    could build gen-1 ids against the gen-2 store. The default is
    CURRENT_GEN."""
    text = prose(10)
    defaulted = build_windows("Page One", "Abilities", text)
    explicit = build_windows("Page One", "Abilities", text, gen=CURRENT_GEN)
    assert [w.id for w in defaulted] == [w.id for w in explicit]
    assert all(w.gen == CURRENT_GEN for w in defaulted)


# ── The quote resolver (the window-level G1's lookup) ─────────────────────


def test_quote_sentence_span_resolves_covering_sentences():
    text = (
        "The domain expands. Its barrier severs the link. The sure hit "
        "follows the user's curse."
    )
    assert quote_sentence_span(text, "severs the link") == (1, 1)
    # A quote across a boundary resolves to both sentences it covers.
    assert quote_sentence_span(text, "barrier severs the link. The sure") == (1, 2)
    # A quote the section does not say is None: the G1 fails loud, not
    # attributed to sentences that do not cover it.
    assert quote_sentence_span(text, "the domain collapses") is None
    assert quote_sentence_span(text, "") is None
    assert quote_sentence_span("", "anything") is None


def test_quote_span_at_a_window_uses_relative_ordinals():
    """At a window, run the resolver on the window's text and add the
    window's s_start: the absolute ordinals a row's quote_span carries."""
    text, windows = section_windows(40)
    full = [s[2] for s in sentence_spans(text)]
    mid = windows[1]
    sentence = full[mid.s_start + 1]
    relative = quote_sentence_span(mid.text, sentence)
    assert relative is not None
    assert (mid.s_start + relative[0], mid.s_start + relative[1]) == (
        mid.s_start + 1,
        mid.s_start + 1,
    )


# ── The old character-sliced windows, for the delta ───────────────────────


def test_old_character_windows_cut_mid_sentence():
    """The defect the supersede removes: the old 4000/300 slide cuts
    characters, so a boundary window starts mid-sentence and its first
    line is not a sentence of the grid it claims to be read from."""
    text = prose(80)  # ~7,600 chars: three old windows
    old = _windows(text)
    assert len(old) >= 2
    sentences = {s[2] for s in sentence_spans(text)}
    mid_starts = [w[:40] for w in old[1:]]
    assert any(
        start not in "".join(sentences) for start in mid_starts
    ) or any(
        not any(s.startswith(w[0]) for s in sentences) for w in old[1:]
    )


# ── The council's process gate: the JJK store delta ───────────────────────


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _jjk_db() -> Path | None:
    db = _repo_root() / "series" / "jjk" / "facts.db"
    return db if db.exists() else None


def test_jjk_store_window_count_delta(tmp_path):
    """The builder is pure, so the whole JJK store runs through it at zero
    LLM cost before the 300k-page scale-out is priced on it: the report
    says how many windows the new grid costs against the old
    character-sliced 4000/300, section by section."""
    db = _jjk_db()
    if db is None:
        pytest.skip("the JJK store is not checked out")
    out = tmp_path / "window_delta.json"
    result = subprocess.run(
        [
            sys.executable,
            str(_repo_root() / "tools" / "train" / "window_delta_report.py"),
            "--db",
            str(db),
            "--json",
            str(out),
        ],
        cwd=_repo_root(),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(out.read_text(encoding="utf-8"))

    assert report["sections_with_text"] > 0
    assert report["new_windows"] > 0
    assert report["old_windows"] > 0
    # The only way a window exceeds the cap is a single oversized
    # sentence: the two counts must agree.
    assert report["over_cap_windows"] == report["oversized_windows"]
    # The grid is the index's grid on the store's own text: every section's
    # window hashes re-split to the section's sentences.
    import sqlite3

    from scriptengine.index.chunker import sentence_content_hash, split_sentences

    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT d.title AS page, s.title AS section, s.text"
        " FROM sections s JOIN documents d ON d.id = s.document_id"
        " WHERE COALESCE(LENGTH(s.text), 0) > 0"
        " LIMIT 200"
    ).fetchall()
    assert rows
    for row in rows:
        text = row["text"]
        grid = [sentence_content_hash(s) for s in split_sentences(text)]
        windows = build_windows(row["page"], row["section"], text)
        union: set[str] = set()
        for window in windows:
            assert window.hashes == tuple(
                grid[window.s_start : window.s_end + 1]
            ), row["page"]
            union.update(window.hashes)
        assert union == set(grid), row["page"]
        for window in windows:
            assert window.text in text or not text.strip()
    # The delta itself: print it, and keep the report for the owner.
    print(
        f"JJK store delta: {report['sections_with_text']} sections, "
        f"{report['old_windows']} old (4000/300 char-sliced) windows -> "
        f"{report['new_windows']} new (grid) windows "
        f"({report['delta']:+d}); {report['oversized_windows']} oversized "
        f"sentence windows; {report['subtopics']} sub-topics."
    )


# ── Helpers ────────────────────────────────────────────────────────────────


def spans_start(text: str, ordinal: int) -> int:
    return sentence_spans(text)[ordinal][0]


def spans_end(text: str, ordinal: int) -> int:
    return sentence_spans(text)[ordinal][1]


def _sentence_at(text: str, ordinal: int) -> str | None:
    spans = sentence_spans(text)
    if ordinal < 0 or ordinal >= len(spans):
        return None
    return spans[ordinal][2]
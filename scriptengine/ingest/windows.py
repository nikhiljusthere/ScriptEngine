"""Whole-sentence windows over the index's sentence grid (2026-09-30).

The windowing-100 council verdict (plan/COUNCIL_WINDOWING_100_DEFINITION.md):
a window is a *view over the index's sentence grid*, never a character slice.
The old ``_windows`` cut 4,000-character runs off section text, and 7% of the
old campaign's passages began mid-sentence, so a quote read across a cut
could not be anchored to any whole sentence -- rows the grid no longer
proves. Supersede, don't salvage: only ~117 of ~1,500 windows (about 8%)
were verified on the old grid, and re-running those is cheaper than proving
a salvage safe.

A window is a span of consecutive sentence ordinals, ``s_start..s_end``,
over one *sub-topic* of a section; its text is the verbatim slice of the
section from the span's first sentence to its last. The grid is the
index's own -- ``split_sentences`` and ``sentence_content_hash``, shared
from ``scriptengine.index.chunker`` -- so the extractor and the index share
one grid (C8) and cannot drift, and a window's ``hashes`` list is exactly
the re-keyable invariant ``FactStore.remap_derived`` works on: stable
within a generation, re-anchored across generations order-preservingly by
the sentence hashes, never by the id.

Invariants (tests/test_windows.py):

* **Verbatim span.** A window's text is ``section_text[a:b]`` -- the slice
  from its first sentence's span to its last -- so every character a quote
  in the window covers is in the section it was read from.
* **Hash-union coverage.** The windows' ``hashes`` union to the section's
  whole grid: no sentence goes unread.
* **One sub-topic per window.** A window's ordinals never cross a
  sub-topic boundary, so a window is one topic -- D6's "read every line as
  one topic" falls out of the structure, not the prompt -- and the
  n=0 class (a multi-topic window whose events are attributed to none of
  its topics) is structurally impossible.
* **The cap.** A window is at most ``cap_chars`` (2,000; the binding
  constraint is the ~2-2.5 KB harness truncation, not the 3B student's
  4,096-token sequence -- 2,000 chars is roughly 570 tokens), except a
  single sentence longer than the cap, which gets its own window and is
  counted, not hidden.
* **The carry.** The next window starts at the previous one's tail, back
  over the longest whole-sentence run that fits under ``carry_chars``
  (250) -- at least two sentences while the tail allows. A quote that
  straddles a cut with its pre-cut depth within the carry is fully
  contained in the next window, so every quote of at most
  ``cap_chars - carry_chars`` (1,750) chars is safe across every cut --
  pinned in test at the strict bound (one sentence of slack). The
  gold's longest quote is 231, so no gold quote can be lost at a
  boundary; anything beyond it fails the window-level G1 loudly instead
  of being attributed to sentences that do not cover it.

Sub-topics come from the wiki's own structure, the index itemizer's unit
(``chunker._section_items``): a ``Label: description`` line, a bullet, a
paragraph -- and a bare heading line joining the entry it heads. A section
with fewer than three items is one sub-topic, the whole text: the index's
own ``len(items) >= 3`` threshold in ``chunk_page``, so the extractor's
topicing cannot disagree with the index's itemization. No free-form topic
segmentation -- "one sub-topic where structurally possible".
"""

from __future__ import annotations

import bisect
import hashlib
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass

from scriptengine.index.chunker import (
    _ABBREVIATIONS,
    _BARE_HEADING,
    _SENTENCE_BREAK,
    _TRAILING_TOKEN,
    sentence_content_hash,
    split_sentences,
)
from scriptengine.ingest.verbatim import fold

# The cap is derived, not guessed (council 2026-09-30): the 3B student's
# 4,096-token sequence is not binding -- 2,000 chars is about 570 tokens.
# What binds is the harness's ~2-2.5 KB truncation of the passage slot and
# the over-stuffing flag: a 4,000-char window read 2,000 chars and claimed
# the rest. 2,000 stays under the truncation with room for the prompt.
DEFAULT_CAP_CHARS = 2000

# The carry is the quote-safety bound: with cap B and carry C, a quote
# of length <= B - C that straddles a cut with its pre-cut depth within
# the carry sits wholly in the next window; the provable variant pins B -
# C - s_max - 1 (one sentence of slack). 250 clears the gold's longest
# quote (231) with margin; the campaign's working bound is B - C = 1,750,
# and re-tuning the figure re-derives the guarantee, it does not guess
# one.
DEFAULT_CARRY_CHARS = 250

# The builder generation the windowing-100 rebuild runs under (council
# 2026-09-30: "this rebuild = gen 2"). The id is gen-scoped by contract:
# stable across re-runs and re-ingests that leave a section's text
# unchanged, and it changes when the gen (or cap, sub-topic split, or
# text) changes -- which is correct, because the remappable invariant is
# the window's ``hashes`` list, which survives any of those.
CURRENT_GEN = 2


@dataclass(frozen=True)
class Subtopic:
    """One structural unit of a section: the wiki's own item.

    ``title`` is the item's heading line (its label for a
    ``Label: description`` item) or ``""`` for the whole-section
    sub-topic. ``start``/``end`` are the item's character span in the
    section text: from its first line to the next item's first line, so
    the items tile the section with no gaps.
    """

    title: str
    start: int
    end: int


@dataclass(frozen=True)
class Window:
    """One read unit: a whole-sentence span over one sub-topic.

    ``s_start``/``s_end`` are ordinals into the section's grid
    (``sentence_spans``), so ``hashes`` is the grid's
    ``sentence_content_hash`` list for that span -- the re-keyable
    invariant, and the exact-sentence attribution a stored row's
    ``quote_span`` resolves onto. ``text`` is the verbatim section slice
    the model reads. ``id`` is content-addressed (the window's own
    ``hashes`` list is in the key: same-titled sections with different
    text are distinct windows, identical text collapses to one) and
    stable within a generation: 16 hex, the same shape as the old
    pool's, so a done-log keyed on the id re-keys by re-running the
    builder, and ``n`` becomes display-only (ordinals shift per page,
    ids do not).
    """

    id: str
    gen: int
    page: str
    section: str
    sub: int
    s_start: int
    s_end: int
    hashes: tuple[str, ...]
    text: str

    @property
    def chars(self) -> int:
        return len(self.text)

    @property
    def quote_span(self) -> tuple[int, int]:
        """The sentence ordinals a quote in this window can resolve to:
        the window's own span. D-T attribution lands on exact sentences,
        not just the source section -- strictly stronger than the gate's
        bar."""
        return (self.s_start, self.s_end)


def sentence_spans(text: str) -> list[tuple[int, int, str]]:
    """The index's sentence grid with character spans:
    ``(start, end, sentence)`` for each sentence of
    ``split_sentences(text)``, in grid order.

    The span is the sentence's own characters in ``text`` (the leading
    and trailing whitespace the grid trims is left out), so a window is
    the verbatim section slice from its first span's start to its last
    span's end. Mirrors ``chunker.split_sentences`` exactly -- same
    break regex, same abbreviation re-join -- and the mirror is pinned
    by test: the sentences, in order, equal the chunker's, on the same
    text. The mirror exists rather than a new split because the grid is
    shared (C8): a second splitter is a second grid, and a second grid
    is where the extractor and the index drift apart.
    """
    raw = text or ""
    pieces: list[tuple[int, int, str]] = []
    start = 0
    for match in _SENTENCE_BREAK.finditer(raw):
        # The citation locator belongs to the sentence it cites, so the cut
        # is made after it, not before (the chunker's rule, kept verbatim).
        raw_end = match.end("tail")
        segment = raw[start:raw_end]
        piece = segment.strip()
        if piece:
            a = start + (len(segment) - len(segment.lstrip()))
            b = raw_end - (len(segment) - len(segment.rstrip()))
            pieces.append((a, b, piece))
        start = match.end()
    segment = raw[start:]
    tail = segment.strip()
    if tail:
        a = start + (len(segment) - len(segment.lstrip()))
        b = start + len(segment) - (len(segment) - len(segment.rstrip()))
        pieces.append((a, b, tail))

    if not pieces:
        return []

    spans: list[tuple[int, int, str]] = [pieces[0]]
    for a, b, part in pieces[1:]:
        last_a, last_b, last_text = spans[-1]
        # "Vol. 5" + "Ch. 12" re-joins the way the chunker re-joins: the
        # merged sentence keeps the first piece's start and the last one's
        # end, so the window slice still covers it whole.
        match = _TRAILING_TOKEN.search(last_text)
        if match and match.group(1).lower() in _ABBREVIATIONS:
            spans[-1] = (last_a, b, f"{last_text} {part}")
        else:
            spans.append((a, b, part))
    return spans


def section_subtopics(text: str) -> list[Subtopic]:
    """A section's sub-topics, from the wiki's own structure.

    One per item, the index itemizer's unit: every non-empty line is its
    own item -- a ``Label: description`` line, a trivia bullet, a
    paragraph -- and a bare heading line (short, no colon, not a
    sentence) is not an item: it heads the entry below and joins it, the
    way ``chunker._section_items`` joins it, so the group name stays
    around the member. A section with fewer than three items is one
    sub-topic, the whole text: the index's own ``len(items) >= 3``
    threshold in ``chunk_page``.
    """
    raw = text or ""
    lines: list[tuple[int, int, str]] = []
    offset = 0
    for line in raw.split("\n"):
        stripped = line.strip()
        if stripped:
            a = offset + (len(line) - len(line.lstrip()))
            b = offset + len(line) - (len(line) - len(line.rstrip()))
            lines.append((a, b, stripped))
        offset += len(line) + 1

    items: list[tuple[int, int, str]] = []
    i = 0
    while i < len(lines):
        a, b, line = lines[i]
        if _BARE_HEADING.match(line) and i + 1 < len(lines):
            # The heading joins the entry it heads (the chunker's rule):
            # the item's span runs to the end of the line below, and the
            # line below is consumed with it.
            items.append((a, lines[i + 1][1], line))
            i += 2
        else:
            items.append((a, b, line))
            i += 1

    if len(items) < 3:
        return [Subtopic("", 0, len(raw))]

    subs: list[Subtopic] = []
    for k, (a, _b, title) in enumerate(items):
        # The item's span runs to the next item's first line, so blank
        # lines between items belong to the item above and the items
        # tile the section.
        end = items[k + 1][0] if k + 1 < len(items) else len(raw)
        subs.append(Subtopic(title, a, end))
    return subs


def window_id(
    gen: int,
    page: str,
    section: str,
    sub: int,
    s_start: int,
    s_end: int,
    hashes: Sequence[str],
) -> str:
    """A window's identity: content-addressed, stable within a generation.

    ``sha256(gen|page|section|sub|s_start:s_end|h1|h2|...)[ :16]`` --
    16 hex, the old pool's shape, so done-logs keyed on the id survive
    the supersede. The key carries the window's ``sentence_content_hash``
    list (2026-10-04 fix): the key without content collided id-for-id
    on same-titled sections -- the JJK universe had 7 such ids spanning
    13 windows (7 pages; doc 545 alone has five "Cast" sections), and
    in every collision the texts differ, so the emitter's id-dedup and
    ``build_trainset.py``'s were silently dropping a distinct window.
    Content-addressed, same-titled sections with different text get
    distinct ids, an unchanged re-ingest keeps the id (same grid, same
    hashes), and identical text collapses to one id (identical read =
    identical answer, so the collapse is correct). The cross-generation
    invariant is the window's ``hashes`` list, not the id: a rebuilt
    store re-keys windows the way ``FactStore.remap_derived`` re-keys
    rows, by the sentence hashes order-preservingly.
    """
    joined = "|".join(hashes)
    key = f"{gen}|{page}|{section}|{sub}|{s_start}:{s_end}|{joined}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


# The default is CURRENT_GEN, not 1 (2026-10-04): CURRENT_GEN is 2 and
# every engine caller passes gen= explicitly, so the old default of 1
# could only fire in new tooling -- which would then build gen-1 ids
# against the gen-2 store.
def build_windows(
    page: str,
    section: str,
    text: str,
    *,
    gen: int = CURRENT_GEN,
    cap_chars: int = DEFAULT_CAP_CHARS,
    carry_chars: int = DEFAULT_CARRY_CHARS,
) -> list[Window]:
    """Every read unit of one section: whole-sentence spans, one
    sub-topic each, packed to the cap with a whole-sentence carry.

    ``page``/``section`` are the labels the caller's rows carry (the
    store's document title and section title for a store run; the
    passage label for an extraction pass) and go into the id only.
    Empty text yields no windows; the caller decides what an unread
    section means (for the extraction campaign: an ID-keyed, cacheable
    empty result -- a result, not a silence, J6.8).
    """
    raw = text or ""
    spans = sentence_spans(raw)
    if not spans:
        return []
    hashes = [sentence_content_hash(sentence) for _a, _b, sentence in spans]
    subs = section_subtopics(raw)
    sub_starts = [sub.start for sub in subs]

    # Each sentence's ordinal belongs to the sub-topic whose span holds
    # its start. The ordinals fall out in text order and the sub-topics
    # tile the section, so each sub-topic's ordinals are one contiguous
    # run -- which is what keeps a window from crossing a boundary.
    sub_of = [
        max(0, bisect.bisect_right(sub_starts, start) - 1)
        for start, _b, _s in spans
    ]

    windows: list[Window] = []
    i = 0
    n = len(spans)
    while i < n:
        sub = sub_of[i]
        last = i
        while last + 1 < n and sub_of[last + 1] == sub:
            last += 1
        # Pack whole sentences to the cap. The window's text is the
        # verbatim slice, so the cap is measured on the slice -- the
        # section's own whitespace included -- not on the joined
        # sentences. A sub-topic boundary always ends a window.
        j = i
        while j < last and spans[j + 1][1] - spans[i][0] <= cap_chars:
            j += 1
        windows.append(
            Window(
                id=window_id(gen, page, section, sub, i, j, hashes[i : j + 1]),
                gen=gen,
                page=page,
                section=section,
                sub=sub,
                s_start=i,
                s_end=j,
                hashes=tuple(hashes[i : j + 1]),
                text=raw[spans[i][0] : spans[j][1]],
            )
        )
        # A sub-topic boundary always ends a window: the carry never
        # crosses one, so one window is one topic.
        if j == last:
            if last + 1 >= n:
                break
            i = last + 1
            continue
        # The carry: the longest whole-sentence run at the window's tail
        # that fits under carry_chars. The next window starts there, so
        # a quote straddling the cut stays covered while its pre-cut
        # depth stays within the carry. If the run takes the whole
        # window (a window under the carry), drop the first sentence
        # rather than re-reading it all: the only way a next window
        # exists is an oversized next sentence, and progress is the
        # invariant. If even the last sentence alone is over the
        # carry, it carries by itself (documented exception: the
        # guarantee then weakens to its own depth, and the window-level
        # G1 makes the loss loud, not silent).
        k = j
        while k > i and spans[j][1] - spans[k - 1][0] <= carry_chars:
            k -= 1
        i = k if k > i else i + 1
    return windows


def quote_sentence_span(text: str, quote: str) -> tuple[int, int] | None:
    """The first and last grid ordinals covering ``quote`` in ``text`` --
    D-T attribution to exact sentences.

    The quote is located as the verbatim slice it is: its first
    occurrence's character span, mapped onto the grid's spans. ``None``
    while the quote is not verbatim in the text -- which is the point of
    the window-level G1: a quote the window does not carry can no
    longer be attributed to sentences that do not cover it. At a
    window, run it on the window's text and add the window's ``s_start``
    to both ordinals.
    """
    raw = text or ""
    q = (quote or "").strip()
    if not q:
        return None
    at = raw.find(q)
    if at < 0:
        return None
    end = at + len(q)
    covering = [
        index
        for index, (a, b, _s) in enumerate(sentence_spans(raw))
        if a < end and b > at
    ]
    if not covering:
        return None
    return covering[0], covering[-1]


def _tidy_positions(text: str) -> tuple[str, list[int]]:
    """The verbatim predicate's tidy of ``text`` (``fold`` + whitespace
    collapse, without the final strip -- a stripped query finds the same
    span), with each tidy character's source index in ``text``.

    Unicode's decomposition maps are per code point, so the per-character
    walk below is the whole-string ``fold`` itself, not an approximation:
    a character that ``quoted_in`` accepts is located here, and the
    mapping never loses a match the predicate made.
    """
    chars: list[str] = []
    positions: list[int] = []
    for index, ch in enumerate(text):
        for piece in unicodedata.normalize("NFKD", ch):
            if unicodedata.combining(piece):
                continue
            piece = piece.lower()
            if piece.isspace():
                if chars and chars[-1] == " ":
                    continue  # the run keeps its first character's position
                chars.append(" ")
                positions.append(index)
            else:
                chars.append(piece)
                positions.append(index)
    return "".join(chars), positions


def quote_grid_span(text: str, quote: str) -> tuple[int, int] | None:
    """The first and last grid ordinals ``quote`` covers in ``text``, or
    ``None`` while the quote is not in the text even after the verbatim
    predicate's own folding (diacritics, whitespace).

    The search is ``quoted_in``'s search -- the same fold and whitespace
    collapse, so a quote verbatim under the predicate (a reflowed line, a
    folded diacritic) still maps onto the grid -- and the span is reported
    in the section's own ordinals, the window's ``quote_span`` vocabulary.
    ``quote_sentence_span`` is the exact-slice variant; this one is the
    gate's, because a quote the predicate accepts must not fail to map.
    """
    raw = text or ""
    spans = sentence_spans(raw)
    query = re.sub(r"\s+", " ", fold(quote or "")).strip()
    if not spans or not query:
        return None
    tidied, positions = _tidy_positions(raw)
    at = tidied.find(query)
    if at < 0:
        return None
    a = positions[at]
    b = positions[at + len(query) - 1]
    covering = [
        index
        for index, (span_a, span_b, _s) in enumerate(spans)
        if span_a <= b and span_b > a
    ]
    if not covering:
        return None
    return covering[0], covering[-1]


def quote_window(
    page: str,
    section: str,
    text: str,
    quote: str,
    *,
    gen: int = CURRENT_GEN,
    cap_chars: int = DEFAULT_CAP_CHARS,
    carry_chars: int = DEFAULT_CARRY_CHARS,
    windows: list[Window] | None = None,
) -> Window | None:
    """The grid window whose span covers the quote's sentence span, or
    ``None`` -- the window-level G1 (council 2026-09-30): a quote the
    grid does not carry in one window can no longer be attributed to
    sentences that do not cover it; the failure is loud, never silent.

    A quote straddling a cut with its pre-cut depth inside the carry sits
    in the next window and passes; a quote deeper than the carry fails --
    the documented weakening at a single oversized sentence. ``page`` and
    ``section`` feed the window ids only; the containment result depends
    on the text's own grid, so the gate may label freely. Pass a caller's
    already-built ``windows`` to skip the rebuild.
    """
    span = quote_grid_span(text, quote)
    if span is None:
        return None
    a, b = span
    built = (
        windows
        if windows is not None
        else build_windows(
            page, section, text,
            gen=gen, cap_chars=cap_chars, carry_chars=carry_chars,
        )
    )
    for window in built:
        if window.s_start <= a and b <= window.s_end:
            return window
    return None
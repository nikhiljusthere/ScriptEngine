"""Chunking, driven by the section tree the API supplied.

Three levels:

* **0, document card.** Title, type, infobox facts and lead, rendered
  compactly. Facts are stored as facts in SQLite *and* rendered here, so that a
  semantic query like "who is tall and blond" can still reach a height and hair
  colour that only exist as infobox parameters. Storing them twice is
  deliberate: one form is exact, the other is searchable.
* **1, section.** The whole section, kept as the parent used to expand context
  around a hit. Not embedded.
* **2, passage.** The retrieval unit, split within a known section.

Because sections are known rather than inferred, every chunk carries a real
breadcrumb. The previous chunker inferred headings with a rule that never
matched the corpus, so every page collapsed to a single unnamed section and the
whole hierarchy was inert.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from scriptengine.ingest.documents import WikiPage

# A sentence ends at `.!?`, optionally followed by a closing quote and by the
# citation locator the wiki put there. Without the locator branch the split
# never fires after "…took over Geto's body.(Chapter 145, Episode 50) Now known
# as…", because the character before the space is `)`, and two sentences merge
# into one chunk and, worse, into one citation, so the sentence the ref
# actually covers cannot be told from the one after it.
_SENTENCE_BREAK = re.compile(
    r'(?<=[.!?])'
    r'(?P<tail>["\']?(?:\((?:[A-Z][A-Za-z\']*\s)?(?:Chapter|Episode|Volume)'
    r'\s[\d.\-]+(?:,\s*[^)]*)?\))?)'
    r'\s+(?=["\']?[A-Z0-9])'
)

# Wiki prose is dense with abbreviations that end in a full stop: "Vol. 5",
# "Ch. 12", "9:15 P.M. Shibuya". Splitting after them chops sentences in half.
# Python's `re` only allows fixed-width lookbehind, so rather than encode this
# in the pattern, candidate splits are re-joined when the left side ends with
# one of these.
_ABBREVIATIONS = frozenset(
    """vol ch no nos mr mrs ms dr st jr sr prof fig ep eps approx etc vs
    i.e e.g a.m p.m u.s ltd inc co dept est cf al""".split()
)

_TRAILING_TOKEN = re.compile(r"([\w.]+)\.$")

# The wiki writes a list section one entry per line: `Label: description`
# for technique lists, plain bullets for Trivia, and bare heading lines
# (`Innate Technique`) that sit above the entries they group. Packing 350
# words across entries (the old rolling pass) mixed four or five entries
# into one passage, so a question about one entry ("What does Yuta's
# Unlimited Void look like?") got a passage the cross-encoder read as about
# five techniques at once and buried under the subject's other pages -- the
# campaign's G3.
#
# The 2026-08-25 correction: the first cut split only on `Label:` lines, so a
# Trivia section (bullets, no labels) dumped its whole unlabeled tail into
# one 330-word catchall and the small bullets ("His maternal grandfather is
# Danish.", 7 words) stopped being served for their questions. The unit is
# therefore the line -- the wiki's own item -- with bare headings joining the
# entry they head, and only short items packed.
_BARE_HEADING = re.compile(r"^[^:.!?]{1,39}$")

# Sections that describe the page rather than the subject. Dropping them keeps
# navigation furniture out of retrieval. These are MediaWiki-wide conventions.
BOILERPLATE_SECTIONS = {
    "references", "navigation", "external links", "see also",
    "site navigation", "gallery", "image gallery", "notes",
}


def effective_boilerplate_sections(overrides: dict | None = None) -> set[str]:
    """The section titles a wiki treats as boilerplate.

    A wiki may promote engine-default boilerplate to content: JJK's `References`
    section carries trivia the span-recall oracle must reach (it is deliberately
    in the oracle's scope, so the chunker has to index it too). The override's
    `content_sections` are subtracted from the global set; the 555 empty JJK
    References still die in the `word_count == 0` guard, so no empty chunk forms.
    """
    extra = ((overrides or {}).get("content_sections") or [])
    return BOILERPLATE_SECTIONS - {title.strip().lower() for title in extra}


@dataclass
class Chunk:
    level: int
    text: str
    doc_title: str
    breadcrumb: str = ""
    ordinal: int = 0
    section_index: int | None = None       # index into the page's section list
    parent_ordinal: int | None = None      # ordinal of the level-1 parent
    entities: list[str] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return len(self.text.split())


def split_sentences(text: str) -> list[str]:
    """Split into sentences, keeping abbreviations and citation markers intact."""
    pieces: list[str] = []
    start = 0
    for match in _SENTENCE_BREAK.finditer(text or ""):
        # The locator belongs to the sentence it cites, so the cut is made after
        # it, not before.
        piece = text[start : match.end("tail")].strip()
        if piece:
            pieces.append(piece)
        start = match.end()
    tail = (text or "")[start:].strip()
    if tail:
        pieces.append(tail)

    parts = [part for part in pieces if part]
    if not parts:
        return []

    merged = [parts[0]]
    for part in parts[1:]:
        match = _TRAILING_TOKEN.search(merged[-1])
        ends_in_abbreviation = bool(match) and match.group(1).lower() in _ABBREVIATIONS
        if ends_in_abbreviation:
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)
    return merged


def _section_items(text: str) -> list[str]:
    """A section's own items: one per non-empty line, headings attached.

    A bare heading line (short, no colon, not a sentence: the wiki's
    `Innate Technique` over its technique entries) is not an item; it heads
    the entry below it and joins that item so the embedding keeps the group
    name around the member. Everything else -- a `Label: description` line,
    a Trivia bullet, a paragraph -- is its own line in the wiki source and
    its own item here.
    """
    lines = [line.strip() for line in (text or "").split("\n")]
    items: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line:
            i += 1
            continue
        if _BARE_HEADING.match(line) and i + 1 < len(lines) and lines[i + 1]:
            items.append(f"{line} {lines[i + 1]}")
            i += 2
            continue
        items.append(line)
        i += 1
    return items


def _passages_from_items(
    items: list[str], target_words: int, overlap_words: int, min_words: int
) -> list[str]:
    """Pack a section's items into passages.

    A substantial item (>= min_words) is its own passage: the entry's label
    is the query's anchor, and packing it under a neighbor's description is
    what buried `Unlimited Void`. Short items (< min_words -- `Favorite food:
    Bread and ajillo.` is five words) still pack toward the target, because
    a five-word passage embeds noisily than one that carries its list
    context; an item longer than the target packs its own sentences.
    """
    passages: list[str] = []
    small: list[str] = []
    small_words = 0
    for item in items:
        words = len(item.split())
        if words >= min_words:
            if small:
                item = " ".join([*small, item])
                words = len(item.split())
                small, small_words = [], 0
            if words > target_words:
                passages.extend(split_passage(item, target_words, overlap_words, min_words))
            else:
                passages.append(item)
        else:
            small.append(item)
            small_words += words + 1
            if small_words >= target_words:
                passages.append(" ".join(small))
                small, small_words = [], 0
    if small:
        tail = " ".join(small)
        if passages and len(tail.split()) < min_words:
            passages[-1] = f"{passages[-1]} {tail}"
        else:
            passages.append(tail)
    return passages


def split_passage(
    text: str, target_words: int, overlap_words: int, min_words: int
) -> list[str]:
    """Split a section into overlapping passages at sentence boundaries.

    Overlap carries whole sentences rather than a fixed word count, so a passage
    never begins mid-clause: a chunk starting "of his hands, Todo can swap"
    embeds poorly and reads worse when quoted in a script.
    """
    sentences = split_sentences(text)
    if not sentences:
        return []

    passages: list[str] = []
    current: list[str] = []
    current_words = 0

    for sentence in sentences:
        words = len(sentence.split())

        if current_words + words > target_words and current:
            passages.append(" ".join(current))
            carried: list[str] = []
            carried_words = 0
            for previous in reversed(current):
                previous_words = len(previous.split())
                if carried_words + previous_words > overlap_words:
                    break
                carried.insert(0, previous)
                carried_words += previous_words
            current = carried
            current_words = carried_words

        current.append(sentence)
        current_words += words

    if current:
        tail = " ".join(current)
        # Absorb a trailing fragment rather than emitting a stub chunk.
        if passages and len(tail.split()) < min_words:
            passages[-1] = f"{passages[-1]} {tail}"
        else:
            passages.append(tail)

    return passages


def render_document_card(page: WikiPage, max_facts: int = 24) -> str:
    """A compact, readable summary of what the page is and states.

    Written as labelled lines rather than prose. The embedding model handles
    "Grade: Grade 1" perfectly well, and a generated sentence would invent
    relationships between facts that the wiki never asserted.
    """
    lines = [page.title]
    if page.page_type and page.page_type != "unknown":
        lines.append(f"Type: {page.page_type.replace('_', ' ')}")

    for fact in page.facts[:max_facts]:
        label = fact.label or fact.key.replace("_", " ").title()
        lines.append(f"{label}: {fact.value}")

    if page.lead:
        lines.append("")
        lines.append(page.lead)

    return "\n".join(lines).strip()


def chunk_page(
    page: WikiPage,
    *,
    target_words: int = 350,
    overlap_words: int = 60,
    min_words: int = 20,
    boilerplate: set[str] | None = None,
) -> list[Chunk]:
    """Produce every chunk for one page, in document order.

    `ordinal` is the position in the page. Narrative retrieval reads it to
    return an arc in the order it happened rather than in the order a similarity
    score ranked it.
    """
    chunks: list[Chunk] = []
    ordinal = 0

    card = render_document_card(page)
    if card:
        chunks.append(
            Chunk(
                level=0,
                text=card,
                doc_title=page.title,
                breadcrumb=page.title,
                ordinal=ordinal,
                entities=sorted(
                    {link.target for fact in page.facts for link in fact.links}
                ),
            )
        )
        ordinal += 1

    for index, section in enumerate(page.sections):
        skip = boilerplate if boilerplate is not None else BOILERPLATE_SECTIONS
        if section.title.strip().lower() in skip:
            continue
        # G15 (2026-08-27): the old `word_count < min_words` floor silently
        # dropped whole factual sections -- Kaito Yuki's 19-word Personality
        # section indexed zero chunks, so no retrieval path could reach it,
        # and 1,660 corpus sections sat under the floor. Item-headed sections
        # were already kept however short (the name is the point, and
        # `_section_roster` reads chunks, so dropping the chunk drops the
        # member with it); a plain short section is content, not noise, so
        # only sections with no text of their own are skipped now.
        if section.word_count == 0:
            continue

        parent_ordinal = ordinal
        chunks.append(
            Chunk(
                level=1,
                text=section.text,
                doc_title=page.title,
                breadcrumb=section.breadcrumb,
                ordinal=ordinal,
                section_index=index,
                entities=sorted({link.target for link in section.links}),
            )
        )
        ordinal += 1

        # A list section is chunked per item, not packed across items: the
        # item is the retrieval unit (see `_section_items`), short items pack
        # with their neighbors, and a long item packs its own sentences.
        items = _section_items(section.text)
        if len(items) >= 3:
            passages = _passages_from_items(items, target_words, overlap_words, min_words)
        else:
            passages = split_passage(section.text, target_words, overlap_words, min_words)
        for passage in passages:
            chunks.append(
                Chunk(
                    level=2,
                    text=passage,
                    doc_title=page.title,
                    breadcrumb=section.breadcrumb,
                    ordinal=ordinal,
                    section_index=index,
                    parent_ordinal=parent_ordinal,
                    entities=sorted({link.target for link in section.links}),
                )
            )
            ordinal += 1

    return chunks


def embeddable(chunks: list[Chunk]) -> list[Chunk]:
    """Levels 0 and 2. Level 1 exists to expand context, not to be retrieved."""
    return [chunk for chunk in chunks if chunk.level in (0, 2)]

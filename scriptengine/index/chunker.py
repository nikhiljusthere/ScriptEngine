"""Chunking, driven by the section tree the API supplied.

Three levels:

* **0 — document card.** Title, type, infobox facts and lead, rendered
  compactly. Facts are stored as facts in SQLite *and* rendered here, so that a
  semantic query like "who is tall and blond" can still reach a height and hair
  colour that only exist as infobox parameters. Storing them twice is
  deliberate: one form is exact, the other is searchable.
* **1 — section.** The whole section, kept as the parent used to expand context
  around a hit. Not embedded.
* **2 — passage.** The retrieval unit, split within a known section.

Because sections are known rather than inferred, every chunk carries a real
breadcrumb. The previous chunker inferred headings with a rule that never
matched the corpus, so every page collapsed to a single unnamed section and the
whole hierarchy was inert.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from scriptengine.ingest.documents import WikiPage

_SENTENCE = re.compile(r'(?<=[.!?])["\']?\s+(?=["\']?[A-Z0-9])')

# Wiki prose is dense with abbreviations that end in a full stop — "Vol. 5",
# "Ch. 12", "9:15 P.M. Shibuya". Splitting after them chops sentences in half.
# Python's `re` only allows fixed-width lookbehind, so rather than encode this
# in the pattern, candidate splits are re-joined when the left side ends with
# one of these.
_ABBREVIATIONS = frozenset(
    """vol ch no nos mr mrs ms dr st jr sr prof fig ep eps approx etc vs
    i.e e.g a.m p.m u.s ltd inc co dept est cf al""".split()
)

_TRAILING_TOKEN = re.compile(r"([\w.]+)\.$")

# Sections that describe the page rather than the subject. Dropping them keeps
# navigation furniture out of retrieval. These are MediaWiki-wide conventions.
BOILERPLATE_SECTIONS = {
    "references", "navigation", "external links", "see also",
    "site navigation", "gallery", "image gallery", "notes",
}


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
    """Split into sentences, keeping abbreviations intact."""
    parts = [part.strip() for part in _SENTENCE.split(text) if part.strip()]
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


def split_passage(
    text: str, target_words: int, overlap_words: int, min_words: int
) -> list[str]:
    """Split a section into overlapping passages at sentence boundaries.

    Overlap carries whole sentences rather than a fixed word count, so a passage
    never begins mid-clause — a chunk starting "of his hands, Todo can swap"
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
        if section.title.strip().lower() in BOILERPLATE_SECTIONS:
            continue
        if section.word_count < min_words:
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

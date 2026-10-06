"""Sourcing a script that already exists.

The writing path gets its locators for free: the research context arrives with
`(Chapter N, Episode M)` markers in it, and the writer tags each block as it
goes. A script written before this existed, or written somewhere else, has no
such help, and re-deriving its sources by hand is the job nobody wants to do.

So this runs the pipeline backwards. Each block of prose is used as a query
against the index, the passages that come back carry the wiki's own references,
and the locators on those references become the block's tag.

**The script's words are never touched.** Not reworded, not reordered, not
re-wrapped. A tag is appended to a block or the block is returned exactly as it
arrived, and `unannotate` reverses the operation to prove it: strip the tags
back off and you have the input, byte for byte. That property is a test, because
it is the only thing standing between this and quietly rewriting someone's
script.

The second rule is the one the annotation rules already state: when the evidence
does not agree, say nothing. A block whose hits point at four different chapters
is a block this cannot source, and an untagged line is honest where a guessed
chapter is not.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings, load_overrides
from scriptengine.retrieve import citations as cite

# A script is blank-line separated: a bold title, `* **Heading**` lines, and
# paragraphs of narration. Only the narration is a candidate for a tag.
_HEADING = re.compile(r"^\s*(?:\*\s*)?\*\*.+\*\*\s*$")
_REFERENCES = re.compile(r"^\s*\*?References:?\*?\s*$", re.IGNORECASE)

# A tag this module appended, for `unannotate`. Anchored to the end of a block
# and preceded by a space, which is exactly how `annotate` writes it.
#
# The plurals matter: a block covering more than one chapter is tagged with a
# span, "(Chapters 118 and 119, Episode 41)", and a pattern that only knew the
# singular left those behind. The round-trip check caught it and refused to
# write, which is what that check is for.
_APPENDED = re.compile(
    r" \((?:[A-Z][A-Za-z']*\s+)?(?:Chapters?|Episodes?|Volumes?)\s+[^)]*\)$"
)

# How many passages to weigh per block. Enough for agreement to mean something,
# small enough that the cross-encoder cost stays sane over a 60-block script.
TOP_K = 6

# A locator has to turn up in at least this many of a block's hits before it is
# believed. One passage agreeing with itself is not agreement.
MIN_AGREEMENT = 2

# Blocks shorter than this are stage directions, one-line asides or fragments;
# there is not enough text in them to retrieve honestly against.
MIN_BLOCK_WORDS = 12

# How far a tag may span before it stops being a citation. A section on a wiki
# can carry references from across the whole manga, and rendering all of them
# gives "(Chapters 1-171, Episodes 1-58)": technically true, useless on screen,
# and worse than saying nothing. Past this the single best-supported locator is
# used instead, and if that cannot be picked the block is left alone.
MAX_SPAN_CHAPTERS = 8


@dataclass
class Block:
    """One piece of the script, and what was found for it."""

    text: str
    kind: str = "prose"                 # prose | heading | blank
    tag: str = ""
    sources: list[str] = field(default_factory=list)
    considered: int = 0

    @property
    def rendered(self) -> str:
        return f"{self.text} {self.tag}" if self.tag else self.text


@dataclass
class Annotated:
    blocks: list[Block] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(block.rendered for block in self.blocks)

    @property
    def tagged(self) -> int:
        return sum(1 for b in self.blocks if b.tag)

    @property
    def candidates(self) -> int:
        return sum(1 for b in self.blocks if b.kind == "prose")

    def summary(self) -> dict[str, Any]:
        return {
            "blocks": len(self.blocks),
            "prose_blocks": self.candidates,
            "tagged": self.tagged,
            "untagged": self.candidates - self.tagged,
        }


def split_blocks(script: str) -> list[Block]:
    """Break a script into blocks without losing a character of it.

    Line-based rather than paragraph-based so that blank lines, headings and
    spacing all survive reassembly exactly. `"\\n".join(b.text ...)` returns the
    input.
    """
    blocks: list[Block] = []
    for line in (script or "").split("\n"):
        if not line.strip():
            kind = "blank"
        elif _HEADING.match(line) or _REFERENCES.match(line):
            kind = "heading"
        else:
            kind = "prose"
        blocks.append(Block(text=line, kind=kind))
    return blocks


def _is_taggable(block: Block) -> bool:
    if block.kind != "prose":
        return False
    # A block that already carries a locator is left alone: the script said it
    # first, and this is not in the business of second-guessing the writer.
    if cite.parse_markers(block.text):
        return False
    return len(block.text.split()) >= MIN_BLOCK_WORDS


def annotate(
    script: str,
    paths: SeriesPaths,
    settings: Settings | None = None,
    top_k: int = TOP_K,
    min_agreement: int = MIN_AGREEMENT,
    min_score: float | None = None,
) -> Annotated:
    """Tag each block of `script` with the chapter and episode behind it."""
    from scriptengine.retrieve.hybrid import HybridRetriever
    from scriptengine.stores.facts import FactStore

    settings = settings or get_settings()
    blocks = split_blocks(script)

    with FactStore(paths.facts_db) as store:
        episodes = cite.EpisodeIndex.from_store(store, load_overrides(paths))

    with HybridRetriever(paths, settings) as retriever:
        for block in blocks:
            if not _is_taggable(block):
                continue
            result = retriever.search(block.text, top_k=top_k, rerank=True)
            block.considered = len(result.passages)
            tag, sources = _agree(result.passages, episodes, min_agreement, min_score)
            block.tag, block.sources = tag, sources
        retriever.release_models()

    return Annotated(blocks=blocks)


def _agree(
    passages: list[Any],
    episodes: cite.EpisodeIndex,
    min_agreement: int,
    min_score: float | None,
) -> tuple[str, list[str]]:
    """The locator the retrieved passages agree on, or nothing.

    Agreement is counted per distinct passage rather than per mention, so one
    section that repeats the same reference eight times does not outvote eight
    sections that each name a different one.
    """
    votes: Counter = Counter()
    seen: dict[str, str] = {}

    for passage in passages:
        if min_score is not None and passage.score < min_score:
            continue
        # The passage's own references first, because they are the ones next to
        # the sentences that matched. Only when it carries none does the whole
        # section stand in, and a section can span half the manga.
        found = cite.locators(cite.attribute(passage.text, episodes))
        if not found:
            body = getattr(passage, "parent_text", "") or ""
            found = cite.locators(cite.attribute(body, episodes))
        if not found:
            # The page may *be* the instalment. One Piece and Berserk write a
            # summary page per chapter and cite almost none of it, so the title
            # is the only locator their prose has, and it is a real one.
            from_title = cite.locator_from_title(passage.doc_title)
            if from_title:
                found = [episodes.complete(from_title)]
        for locator in {locator.render() for locator in found if locator}:
            votes[locator] += 1
            seen[locator] = passage.doc_title

    agreed = [text for text, count in votes.items() if count >= min_agreement]
    if not agreed:
        return "", []

    # Keep the most-supported locators, then render them as one span so a block
    # covering two chapters reads as a range rather than a list.
    best = max(votes[text] for text in agreed)
    kept = [text for text in agreed if votes[text] == best]
    if _too_wide(kept):
        # Narrow to the single strongest rather than claiming the whole range.
        kept = [max(kept, key=lambda text: (votes[text], text))]
        if _too_wide(kept):
            return "", []

    span = cite.span([cite.parse_locator(text) for text in kept])
    return (f"({span})" if span else ""), sorted({seen[text] for text in kept})


def _too_wide(rendered: list[str]) -> bool:
    """True when these locators cover more chapters than a tag usefully can."""
    numbers = []
    for text in rendered:
        locator = cite.parse_locator(text)
        head = (locator.chapter or "").split("-")[0]
        try:
            numbers.append(float(head))
        except ValueError:
            continue
    return bool(numbers) and (max(numbers) - min(numbers)) > MAX_SPAN_CHAPTERS


def unannotate(script: str) -> str:
    """Remove tags this module appended. The inverse of `annotate`.

    Exists so the guarantee can be tested rather than asserted: strip the tags
    off a cited script and it must be the input again, byte for byte.
    """
    return "\n".join(
        _APPENDED.sub("", line) for line in (script or "").split("\n")
    )

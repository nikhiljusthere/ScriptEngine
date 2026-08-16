"""Turning wiki references into locators a script can say out loud.

A script line has to end with the chapter and episode it comes from. The wiki
supplies that, but not in the shape a script needs, and two gaps sat between
the two:

* **Refs are sparse in prose.** MediaWiki convention puts one ``{{Ref}}`` at the
  end of the passage it supports, not on every sentence. Measured on a fetched
  Shibuya Incident bundle, 12.8% of sentences and 68 of 128 beats carried any
  locator at all. The fix is not to invent citations, it is to read the one the
  page already made: a ref covers the sentences before it, back to the previous
  ref. That is what placing it there means.
* **Half the refs name a chapter and no episode.** Corpus-wide, 7,548 refs carry
  ``chap`` and only 3,815 carry ``ep``. The missing half is not missing at all:
  the wiki states it elsewhere, as ``Chapter N -anime episode-> Episode M`` and
  ``Episode M -adapted from-> Chapter N`` edges, which the graph already holds.
  Resolving through those two relations is a lookup, not a guess, and a chapter
  the anime never adapted correctly resolves to nothing and stays a bare
  ``(Chapter N)``.

Nothing here is series-specific: numbered instalments and citation templates are
how wikis work.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, Sequence

if TYPE_CHECKING:  # pragma: no cover - typing only
    from scriptengine.stores.facts import FactStore

# The locators `wikitext.strip_markup` inlines into section prose, e.g.
# "(Chapter 143, Episode 30)", "(Chapter 143)", "(Modulo Chapter 16)". Matched
# where they sit, because where they sit is the citation's scope.
#
# The optional leading word is the work a sequel's numbering belongs to. It has
# to be part of the pattern rather than stripped later: "Chapter 16" and
# "Modulo Chapter 16" are different chapters of different manga, and treating
# them as one is how a script ends up citing the wrong volume of the wrong work.
_MARKER = re.compile(
    # The number has to follow the kind immediately, so ordinary prose like
    # "(the Chapter 5 fight)" is not mistaken for a citation.
    r"\((?:[A-Z][A-Za-z']*\s+)?(?:Chapter|Episode|Volume)\s+[\d.\-]+(?:,\s*[^)]*)?\)"
)
# Every kind takes the optional work prefix, not just chapters. Dragon Ball
# numbers Z, Super, GT, Daima and Heroes separately and cites episodes far more
# often than chapters, and Berserk labels manga and anime episodes apart, so an
# episode that loses its work is an episode of the wrong series.
_CHAPTER = re.compile(r"(?:([A-Z][A-Za-z']*)\s+)?Chapter\s+([\d.\-]+)")
_EPISODE = re.compile(r"(?:([A-Z][A-Za-z']*)\s+)?Episode\s+([\d.\-]+)")
_VOLUME = re.compile(r"(?:([A-Z][A-Za-z']*)\s+)?Volume\s+([\d.\-]+)")

# Instalment titles as the graph stores them: "Chapter 143", "Episode 30".
_TITLE_NUMBER = re.compile(r"^(chapter|episode)\s+([\d.\-]+)$", re.IGNORECASE)


@dataclass(frozen=True)
class Locator:
    """Where a claim comes from, in the form a script says it.

    `work` names the sequel or spin-off a numbering belongs to, empty for the
    main series. It is part of the identity: Modulo Chapter 16 and Chapter 16
    are different chapters of different manga.
    """

    chapter: str = ""
    episode: str = ""
    volume: str = ""
    work: str = ""

    def __bool__(self) -> bool:
        return bool(self.chapter or self.episode or self.volume)

    def render(self) -> str:
        parts = []
        if self.chapter:
            parts.append(f"Chapter {self.chapter}")
        if self.episode:
            parts.append(f"Episode {self.episode}")
        if self.volume and not parts:
            parts.append(f"Volume {self.volume}")
        if not parts:
            return ""
        # The work qualifies the whole citation, so it is said once at the
        # front. "(Z Episode 130, Chapter 44)" reads correctly; prefixing every
        # part would give "(Z Episode 130, Z Chapter 44)".
        if self.work:
            parts[0] = f"{self.work} {parts[0]}"
        return f"({', '.join(parts)})"


@dataclass
class SentenceCitation:
    """One sentence and the reference that covers it."""

    text: str
    locator: Locator = field(default_factory=Locator)
    inherited: bool = False     # True when the ref sits on a neighbouring sentence


class EpisodeIndex:
    """Chapter number -> episode title, straight from the graph.

    Both relations are read because neither is complete on its own: on the
    Jujutsu Kaisen wiki `anime episode` covers 185 chapters and `adapted from`
    covers 181, and their union is every chapter the anime has reached.
    """

    def __init__(self, chapter_to_episode: dict[str, str] | None = None) -> None:
        self._episodes: dict[str, str] = dict(chapter_to_episode or {})

    @classmethod
    def from_store(cls, store: "FactStore") -> "EpisodeIndex":
        mapping: dict[str, str] = {}

        # Chapter -> Episode.
        for row in store.edges_by_relation("anime episode"):
            chapter = _instalment_number(row["source"], "chapter")
            episode = _instalment_number(row["target"], "episode")
            if chapter and episode:
                mapping.setdefault(chapter, episode)

        # Episode -> Chapter, the same statement written from the other end.
        for row in store.edges_by_relation("adapted from"):
            episode = _instalment_number(row["source"], "episode")
            chapter = _instalment_number(row["target"], "chapter")
            if chapter and episode:
                mapping.setdefault(chapter, episode)

        return cls(mapping)

    def __len__(self) -> int:
        return len(self._episodes)

    def episode_for(self, chapter: str) -> str:
        """The episode that adapted `chapter`, or "" when the anime has not."""
        return self._episodes.get(str(chapter).strip(), "")

    def complete(self, locator: Locator) -> Locator:
        """Fill in the episode when the graph knows it and the ref did not.

        A chapter of another work is left alone. The map is built from the main
        series' `Chapter N -anime episode-> Episode M` edges, so completing
        Modulo Chapter 16 from it would hand the sequel an episode of the first
        anime: a wrong number stated with the same confidence as a right one.
        """
        if locator.work or locator.episode or not locator.chapter:
            return locator
        episode = self.episode_for(locator.chapter)
        if not episode:
            return locator
        return Locator(chapter=locator.chapter, episode=episode, volume=locator.volume)


def _instalment_number(title: str, kind: str) -> str:
    match = _TITLE_NUMBER.match((title or "").strip())
    if not match or match.group(1).lower() != kind:
        return ""
    return match.group(2)


def parse_locator(marker: str) -> Locator:
    """Read one inline marker back into its parts."""
    chapter = _CHAPTER.search(marker)
    episode = _EPISODE.search(marker)
    volume = _VOLUME.search(marker)
    work = ""
    for match in (chapter, episode, volume):
        if match and match.group(1):
            work = match.group(1)
            break
    return Locator(
        chapter=chapter.group(2) if chapter else "",
        episode=episode.group(2) if episode else "",
        volume=volume.group(2) if volume else "",
        work=work,
    )


# A page that *is* an instalment: "Chapter 1015", "Episode 970",
# "Modulo Chapter 16", "Episode 0-1 (Manga)".
_INSTALMENT_TITLE = re.compile(
    r"^(?:([A-Z][A-Za-z']*)\s+)?(Chapter|Episode|Volume)\s+([\d.\-]+)"
    r"(?:\s*\((?:(?:19|20)\d\d\s+)?(Manga|Anime)\))?$",
    re.IGNORECASE,
)


def locator_from_title(title: str) -> Locator:
    """The locator a page carries by being that instalment.

    Not every wiki cites its own prose. One Piece writes 1,191 chapter pages and
    1,172 episode pages, each with a full summary, and puts a `<ref>` on almost
    none of it; its references point at video games and publishers. Berserk is
    the same. But a claim retrieved from the page titled "Chapter 1015" is
    sourced to Chapter 1015 as surely as if the sentence carried a footnote, and
    reading the title is not an inference.

    Returns an empty locator for an ordinary page, which is most of them.
    """
    match = _INSTALMENT_TITLE.match((title or "").strip())
    if not match:
        return Locator()
    work, kind, number, medium = match.groups()
    # "Episode 137 (Manga)" is Berserk saying which of its two numberings this
    # is; the suffix is the qualifier, not part of the name.
    work = (medium or work or "").strip()
    kind = kind.lower()
    return Locator(
        chapter=number if kind == "chapter" else "",
        episode=number if kind == "episode" else "",
        volume=number if kind == "volume" else "",
        work=work.title() if work else "",
    )


def parse_markers(text: str) -> list[tuple[int, int, Locator]]:
    """Every inline locator in `text` as ``(start, end, Locator)``."""
    found: list[tuple[int, int, Locator]] = []
    for match in _MARKER.finditer(text or ""):
        locator = parse_locator(match.group(0))
        if locator:
            found.append((match.start(), match.end(), locator))
    return found


def upgrade_markers(text: str, index: EpisodeIndex | None) -> str:
    """Rewrite ``(Chapter 79)`` as ``(Chapter 79, Episode 30)`` where known.

    Enrichment only: a marker the graph cannot complete is left exactly as the
    wiki wrote it, so an unadapted chapter never acquires an episode.
    """
    if index is None or not text:
        return text

    def replace(match: re.Match[str]) -> str:
        locator = parse_locator(match.group(0))
        if not locator:
            return match.group(0)
        completed = index.complete(locator)
        return completed.render() if completed != locator else match.group(0)

    return _MARKER.sub(replace, text)


def attribute(text: str, index: EpisodeIndex | None = None) -> list[SentenceCitation]:
    """Assign every sentence the reference that covers it.

    The nearest ref *after* a sentence is the one that cites it, and that is where
    an editor puts it. Sentences trailing the last ref fall back to it, since
    the alternative is leaving the tail of every section unsourced.
    """
    from scriptengine.index.chunker import split_sentences

    sentences = split_sentences(text or "")
    if not sentences:
        return []

    own: list[Locator] = []
    for sentence in sentences:
        markers = parse_markers(sentence)
        own.append(markers[-1][2] if markers else Locator())

    # Look ahead for the covering ref, then behind for the tail.
    resolved: list[SentenceCitation] = []
    following: list[Locator] = [Locator()] * len(sentences)
    carried = Locator()
    for position in range(len(sentences) - 1, -1, -1):
        if own[position]:
            carried = own[position]
        following[position] = carried

    trailing = Locator()
    for position, sentence in enumerate(sentences):
        locator = following[position] or trailing
        if own[position]:
            trailing = own[position]
        elif locator:
            trailing = locator
        if index is not None:
            locator = index.complete(locator)
        resolved.append(
            SentenceCitation(
                text=sentence, locator=locator, inherited=not bool(own[position])
            )
        )
    return resolved


def locators(sentences: Iterable[SentenceCitation]) -> list[Locator]:
    """Distinct locators, in the order they first cover something."""
    seen: list[Locator] = []
    for sentence in sentences:
        if sentence.locator and sentence.locator not in seen:
            seen.append(sentence.locator)
    return seen


def span(found: Sequence[Locator]) -> str:
    """Collapse locators into one readable range.

    ``Chapters 90-92, Episodes 35-36``, or ``Chapter 145, Episode 50`` when a
    passage sits in one place. This is the tag the writer puts at the end of the
    block, so it has to read as speech, not as a citation list.

    Each work is ranged separately. A passage citing both the main series and
    the sequel would otherwise collapse to "Chapters 16-235", a range spanning
    two manga that contains neither of the chapters actually cited.
    """
    parts: list[str] = []
    for work in _distinct_works(found):
        here = [locator for locator in found if locator.work == work]
        chapters = _numbers(locator.chapter for locator in here)
        episodes = _numbers(locator.episode for locator in here)
        mine: list[str] = []
        if chapters:
            mine.append(_range("Chapter", chapters))
        if episodes:
            mine.append(_range("Episode", episodes))
        if mine and work:
            mine[0] = f"{work} {mine[0]}"
        parts.extend(mine)
    return ", ".join(parts)


def _distinct_works(found: Sequence[Locator]) -> list[str]:
    """Works present, main series first."""
    seen: list[str] = []
    for locator in found:
        if locator.work not in seen:
            seen.append(locator.work)
    return sorted(seen, key=lambda work: (work != "", work))


def _numbers(values: Iterable[str]) -> list[str]:
    seen: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    return sorted(seen, key=_sort_key)


def _sort_key(value: str) -> tuple[float, float]:
    head, _, tail = value.partition("-")
    try:
        return (float(head), float(tail) if tail else 0.0)
    except ValueError:
        return (float("inf"), 0.0)


def _range(kind: str, values: list[str]) -> str:
    if len(values) == 1:
        return f"{kind} {values[0]}"
    if len(values) == 2:
        return f"{kind}s {values[0]} and {values[1]}"
    return f"{kind}s {values[0]}-{values[-1]}"


def coverage(text: str, index: EpisodeIndex | None = None) -> dict[str, int]:
    """How much of a passage can be sourced. Used by `cli audit`."""
    sentences = attribute(text, index)
    return {
        "sentences": len(sentences),
        "with_chapter": sum(1 for s in sentences if s.locator.chapter),
        "with_episode": sum(1 for s in sentences if s.locator.episode),
        "cited_directly": sum(1 for s in sentences if s.locator and not s.inherited),
    }

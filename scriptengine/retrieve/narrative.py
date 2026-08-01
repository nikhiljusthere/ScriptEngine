"""Narrative retrieval: events in the order they happened.

Relevance ranking answers questions. It does not write scripts.

Asked about the Shibuya Incident, a QA retriever returns the eight most similar
fragments in similarity order — which is a fine answer to "what was the Shibuya
Incident" and a useless basis for a twelve-minute video. A script needs the
event in sequence: what happened, to whom, in what order, and what it caused.

Two orderings are available, and both come from data already extracted:

* **within a page** — sections carry their position in the article, and a wiki
  writes chronologically. The Shibuya Incident page is literally ordered
  "7:00 P.M. Shibuya", "8:31 P.M. Fukutoshin Line Platform", and so on.
* **across pages** — chapter, episode and volume titles carry numbers, and arc
  pages link to their chapters. Sorting on those numbers gives a real timeline.

Nothing here is series-specific: numbered instalments and ordered sections are
how wikis work, not how Jujutsu Kaisen works.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings
from scriptengine.stores.facts import FactStore

# Instalment numbers: "Chapter 16", "Episode 8", "Volume 5", "Chapter 0-1".
_INSTALMENT = re.compile(
    r"^(chapter|episode|volume|ova|special|film|movie|arc)\s+([\d.\-]+)", re.IGNORECASE
)

# Times used as section headings on event pages: "9:15 P.M. Shibuya Station".
_TIME_HEADING = re.compile(
    r"(\d{1,2}):(\d{2})\s*([AaPp])\.?\s*[Mm]\.?", re.IGNORECASE
)

# Page types that represent something that happens, rather than something that is.
EVENT_TYPES = {"battle", "event", "story_arcs", "chapter", "episode", "arc"}


@dataclass
class Beat:
    """One ordered step of a narrative."""

    order: int
    title: str
    text: str
    doc_title: str
    breadcrumb: str
    time: str = ""
    participants: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "order": self.order,
            "title": self.title,
            "doc_title": self.doc_title,
            "breadcrumb": self.breadcrumb,
            "text": self.text,
        }
        if self.time:
            payload["time"] = self.time
        if self.participants:
            payload["participants"] = self.participants
        return payload


@dataclass
class Narrative:
    subject: str
    beats: list[Beat] = field(default_factory=list)
    participants: list[str] = field(default_factory=list)
    related_pages: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "participants": self.participants,
            "related_pages": self.related_pages,
            "beats": [beat.as_dict() for beat in self.beats],
        }


def instalment_number(title: str) -> tuple[int, float] | None:
    """Sort key for "Chapter 16" and friends, or None if it is not one.

    Returns `(kind, number)` so chapters, episodes and volumes each sort within
    their own sequence rather than interleaving.
    """
    match = _INSTALMENT.match(title.strip())
    if not match:
        return None

    kinds = {
        "chapter": 0, "episode": 1, "volume": 2,
        "ova": 3, "special": 4, "film": 5, "movie": 5, "arc": 6,
    }
    raw = match.group(2).replace("-", ".")
    try:
        # "0.1" and "0-1" are both "chapter zero, part one".
        parts = raw.split(".")
        number = float(f"{parts[0]}.{parts[1]}") if len(parts) > 1 else float(parts[0])
    except ValueError:
        return None

    return kinds[match.group(1).lower()], number


def extract_time(heading: str) -> str:
    """Pull a clock time out of a section heading, if it has one."""
    match = _TIME_HEADING.search(heading)
    if not match:
        return ""
    meridiem = "PM" if match.group(3).lower() == "p" else "AM"
    return f"{match.group(1)}:{match.group(2)} {meridiem}"


class NarrativeRetriever:
    """Builds ordered accounts of events for one series."""

    def __init__(self, paths: SeriesPaths, settings: Settings | None = None) -> None:
        self.paths = paths
        self.settings = settings or get_settings()
        self.store = FactStore(paths.facts_db)

    def __enter__(self) -> "NarrativeRetriever":
        return self

    def __exit__(self, *_: object) -> None:
        self.store.close()

    def close(self) -> None:
        self.store.close()

    # ── entry point ──────────────────────────────────────────────────────────

    def timeline(self, subject: str, max_beats: int = 40) -> Narrative:
        """Return `subject` as ordered beats.

        Resolves the subject through the alias table first, so "Shibuya" and
        "The Shibuya Incident" reach the same page.
        """
        entities = self.store.link_entities(subject)
        node = None
        for candidate in entities:
            if candidate["label"] in EVENT_TYPES or not node:
                node = candidate
                if candidate["label"] in EVENT_TYPES:
                    break

        if node is None:
            return Narrative(subject=subject)

        narrative = Narrative(subject=node["name"])
        narrative.beats = self._beats_from_page(node["name"], max_beats)
        narrative.participants = self._participants(int(node["id"]))
        narrative.related_pages = self._ordered_related(int(node["id"]))

        # An arc page is often a table of contents rather than a narrative. When
        # its own sections yield little, fall back to the chapters it links to,
        # in numbered order.
        if len(narrative.beats) < 3 and narrative.related_pages:
            narrative.beats = self._beats_from_pages(
                narrative.related_pages, max_beats
            )

        return narrative

    # ── ordering ─────────────────────────────────────────────────────────────

    def _beats_from_page(self, title: str, max_beats: int) -> list[Beat]:
        """A page's own sections, in the order the article presents them."""
        beats: list[Beat] = []

        for section in self.store.document_sections(title):
            if not section["text"] or section["word_count"] < 20:
                continue
            beats.append(
                Beat(
                    order=len(beats) + 1,
                    title=section["title"],
                    text=section["text"],
                    doc_title=title,
                    breadcrumb=section["breadcrumb"],
                    time=extract_time(section["breadcrumb"]),
                )
            )
            if len(beats) >= max_beats:
                break

        return beats

    def _beats_from_pages(self, titles: list[str], max_beats: int) -> list[Beat]:
        """One beat per linked page, in instalment order."""
        beats: list[Beat] = []

        for title in titles:
            sections = self.store.document_sections(title)
            body = next(
                (
                    section for section in sections
                    if section["title"].lower() in {"summary", "plot", "plot details", "synopsis"}
                ),
                sections[0] if sections else None,
            )
            if body is None or not body["text"]:
                continue

            beats.append(
                Beat(
                    order=len(beats) + 1,
                    title=title,
                    text=body["text"],
                    doc_title=title,
                    breadcrumb=body["breadcrumb"],
                )
            )
            if len(beats) >= max_beats:
                break

        return beats

    def _ordered_related(self, node_id: int) -> list[str]:
        """Linked pages that are numbered instalments, in numeric order.

        Sorting by number rather than by title is the whole point: "Chapter 10"
        sorts before "Chapter 9" alphabetically, which would silently scramble
        every timeline.
        """
        numbered: list[tuple[tuple[int, float], str]] = []

        for row in self.store.edges_for([node_id], min_confidence=0.3, limit=400):
            for name in (row["source"], row["target"]):
                key = instalment_number(name)
                if key is not None:
                    numbered.append((key, name))

        seen: set[str] = set()
        ordered: list[str] = []
        for _, name in sorted(numbered, key=lambda pair: pair[0]):
            if name not in seen:
                seen.add(name)
                ordered.append(name)
        return ordered

    def _participants(self, node_id: int) -> list[str]:
        """Characters involved, taken from the strong (infobox) edges."""
        participants: list[str] = []
        for row in self.store.edges_for([node_id], min_confidence=0.9, limit=200):
            for name in (row["source"], row["target"]):
                node = self.store.node_by_name(name)
                if node and node["label"] == "character" and name not in participants:
                    participants.append(name)
        return participants

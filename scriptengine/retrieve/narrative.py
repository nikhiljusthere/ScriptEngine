"""Narrative retrieval: events in the order they happened.

Relevance ranking answers questions. It does not write scripts.

Asked about the Shibuya Incident, a QA retriever returns the eight most similar
fragments in similarity order, which is a fine answer to "what was the Shibuya
Incident" and a useless basis for a twelve-minute video. A script needs the
event in sequence: what happened, to whom, in what order, and what it caused.

Two orderings are available, and both come from data already extracted:

* **within a page**: sections carry their position in the article, and a wiki
  writes chronologically. The Shibuya Incident page is literally ordered
  "7:00 P.M. Shibuya", "8:31 P.M. Fukutoshin Line Platform", and so on.
* **across pages**: chapter, episode and volume titles carry numbers, and arc
  pages link to their chapters. Sorting on those numbers gives a real timeline.

Nothing here is series-specific: numbered instalments and ordered sections are
how wikis work, not how Jujutsu Kaisen works.
"""

from __future__ import annotations

import os
import re
import sqlite3
from dataclasses import dataclass, field
from typing import Any, cast

from scriptengine.config import (
    SeriesPaths,
    Settings,
    get_settings,
    load_overrides,
    subject_aliases,
    subject_ranking,
)
from scriptengine.retrieve import citations as cite
from scriptengine.retrieve.roster import content_words
from scriptengine.stores.facts import FactStore, rank_subjects

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

# For the character fallback, individual instalment pages ("Chapter 5") are too
# granular to tell a story: a character links to hundreds of them and the
# timeline becomes a chapter list. Only pages that gather many events into one
# narrative qualify.
_CHARACTER_EVENT_TYPES = {"battle", "event", "story_arcs", "arc"}

# G30 (2026-09-04): a page's own short prose section. The G15 floor below drops
# 4-word furniture ("Teams", "Navigation", unsourced tables) that carries no
# refs; a page's own Summary/Synopsis is real prose, not furniture, so a short
# one (e.g. the 12-word Epilogue Summary) must still become a beat. Kept narrow
# on evidence: "plot", "plot details" and "synopses" match zero sections in the
# JJK corpus, so they stay floored -- add one only when a failing question proves
# a short section of that title exists.
_PAGE_PROSE_SECTIONS = {"summary", "synopsis"}

# Pages worth reaching for once the subject's own page is exhausted. Battles
# describe the fights an event page only summarises, and technique pages carry
# the usage chapters behind them. Character pages are excluded on purpose: a
# biography is not a beat, and an event links dozens of them.
NEIGHBOUR_TYPES = {"battle", "event", "story_arcs", "arc", "technique"}


def events_order_enabled() -> bool:
    """Whether beats are reordered onto the extracted events' time axis.

    Read on every call, so a process serving both paths can flip the door
    test without a restart. Off by default: the reorder is under test and
    the narrative path's default behaviour must not move until the gates
    have passed (comprehension build, Phase 1).
    """
    return os.environ.get("SCRIPTENGINE_EVENTS_ORDER", "0") == "1"

# Words that carry no information about what a script wants to hear about.
_QUERY_STOPWORDS = {
    "i", "want", "you", "to", "a", "the", "topic", "on", "about", "and", "or",
    "with", "from", "that", "this", "like", "would", "have", "had", "has",
    "make", "made", "making", "were", "was", "been", "being", "his", "her",
    "their", "they", "them", "then", "than", "till", "until", "during", "over",
    "into", "out", "off", "for", "against", "took", "take", "taken", "place",
    "what", "which", "where", "when", "how", "who", "start", "ended", "end",
    "begin", "before", "after", "between", "such", "some", "certain", "other",
    "also", "very", "just", "only", "one", "two", "three", "will", "can",
    "could", "should", "would", "shall", "may", "might", "must", "not", "no",
    "yes", "write", "script", "scripts", "topic", "title", "word", "words",
    "line", "lines", "section", "sections", "division", "divide", "divided",
    "guess", "educated", "explain", "explanation", "instead", "along", "since",
    "though", "through", "without", "happened", "happen", "happens", "days",
    "day", "period", "time", "times", "major", "include", "including",
}

# "19 days" carries the story where "19" and "days" alone do not: Gojo was
# sealed for nineteen days, and the phrase names that whole stretch of the
# timeline. Numbers are dropped from the word tokens, so the phrase is kept
# whole.
_DURATION = re.compile(
    r"\b(\d{1,3})\s+(days?|weeks?|months?|years?)\b", re.IGNORECASE
)

# List-style sections ("Chapters", "Battles & Events", "Characters Introduced")
# make every arc page mention "chapter", "battles" and "events", so scoring
# against them would make every event look relevant to every query.
_LIST_SECTION_TITLES = {
    "chapters", "episodes", "volumes", "characters introduced",
    "characters in order of appearance", "terminology introduced", "terms",
    "settings", "trivia", "navigation", "battles", "battles & events",
    "locations", "media", "gallery", "references", "chapter navigation",
    "volume navigation", "plot", "summary",
}


def _query_content_tokens(query: str, subject: str) -> set[str]:
    """Content words in the query, minus stopwords and the subject's own name."""
    ignored = _QUERY_STOPWORDS | {word.lower() for word in re.findall(r"\w+", subject)}
    tokens = {
        word.lower()
        for word in re.findall(r"[A-Za-z']{4,}", query)
        if word.lower() not in ignored
    }
    tokens.update(
        f"{match.group(1)} {match.group(2).lower()}"
        for match in _DURATION.finditer(query)
        if f"{match.group(1)} {match.group(2).lower()}" not in ignored
    )
    return tokens


def _event_token_hits(
    candidate: sqlite3.Row, store: "FactStore", tokens: set[str]
) -> set[str]:
    """Which of the query's content tokens appear in the event's prose."""
    if not tokens:
        return set()
    sections = store.document_sections(candidate["name"])
    prose = [
        section
        for section in sections
        if section["title"].strip().lower() not in _LIST_SECTION_TITLES
    ]
    text = (
        candidate["name"] + " " + " ".join(s["text"] for s in prose)
    ).lower()
    return {token for token in tokens if token in text}


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
    # Where this beat comes from, as the script says it out loud. `citations`
    # lists every locator the beat's prose resolves to; `source_span` collapses
    # them into the one tag that goes at the end of the block.
    citations: list[str] = field(default_factory=list)
    source_span: str = ""

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
        if self.citations:
            payload["citations"] = self.citations
        if self.source_span:
            payload["source_span"] = self.source_span
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
        overrides = load_overrides(paths)
        self._overrides = overrides
        self.demote, self.priority = subject_ranking(overrides)
        self.aliases = subject_aliases(overrides)
        self._episodes: cite.EpisodeIndex | None = None

    @property
    def episodes(self) -> cite.EpisodeIndex:
        """Chapter -> episode, built once per retriever."""
        if self._episodes is None:
            self._episodes = cite.EpisodeIndex.from_store(self.store, self._overrides)
        return self._episodes

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
        entities = rank_subjects(
            self.store.link_entities(self._alias_text(subject)),
            self.demote,
            self.priority,
        )

        # `rank_subjects` already put the likeliest subject first: pages that
        # package the work (the series, a volume, an episode) go last, and among
        # the rest the wiki's own page type decides. Before it existed, "Every
        # Rank of Curse in Jujutsu Kaisen" resolved to the series page and came
        # back as one beat from `Volume 0`, and "Every Cursed Technique of
        # Sukuna" resolved to the generic `Cursed Technique` page.
        #
        # Type priority also outranks the words the subject names, which is
        # how the roster-empty fallback could hand `Every Fight Mahoraga Has
        # Ever Been In` back as `Sukuna vs. Yorozu`: every event page beats the
        # technique that shares the word with the question. The same overlap
        # test the router's `_subject` and `build_roster` run has to happen
        # before the first-resolved pick, or the three retrievers resolve the
        # same question to different pages.
        asked = set(content_words(subject))
        entities = [
            row
            for _, row in sorted(
                enumerate(entities),
                key=lambda item: (
                    not bool(set(content_words(item[1]["name"])) & asked),
                    item[0],
                ),
            )
        ]

        # A resolved page still wins over an unresolved one at equal rank:
        # there is nothing to say about a node with no article behind it.
        node = next((row for row in entities if row["is_resolved"]), None)
        if node is None and entities:
            node = entities[0]

        if node is None:
            return Narrative(subject=subject)

        narrative = Narrative(subject=node["name"])

        # A character page is a biography, not an event list. A script wants
        # what happened to the character, so the character's events and battles
        # are the timeline even when the character page resolves (Gojo's own
        # sections are Appearance, Personality, Cursed Technique, not a
        # narrative). The biography sections are only a fallback when the
        # character has no recorded events.
        if node["label"] in {"character", "character_synopsis", "unknown"}:
            beats = self._beats_from_character_events(node, max_beats, subject)
            if len(beats) < 3:
                beats = self._beats_from_page(node["name"], max_beats)
        else:
            beats = self._beats_from_page(node["name"], max_beats)
            # A specific query names what the script is about: keep the
            # sections that mention it, in order, so the budget reaches the
            # story's end instead of running out in the middle of a giant
            # page ("sealed and freed" lands on the sealing and the unsealing,
            # not on the opening festival).
            tokens = _query_content_tokens(subject, node["name"])
            if len(tokens) >= 2:
                beats = self._filter_matches(beats, tokens)

        narrative.beats = beats
        narrative.participants = self._participants(int(node["id"]))
        narrative.related_pages = self._ordered_related(int(node["id"]))

        # An arc page is often a table of contents rather than a narrative. When
        # its own sections yield little, fall back to the chapters it links to,
        # in numbered order.
        if len(narrative.beats) < 3 and narrative.related_pages:
            narrative.beats = self._beats_from_pages(
                narrative.related_pages, max_beats
            )
            tokens = _query_content_tokens(subject, node["name"])
            if len(tokens) >= 2:
                narrative.beats = self._filter_matches(narrative.beats, tokens)

        if len(narrative.beats) < max_beats:
            narrative.beats.extend(
                self._beats_from_neighbours(
                    node, max_beats - len(narrative.beats), narrative.beats, subject
                )
            )
            for order, beat in enumerate(narrative.beats, start=1):
                beat.order = order

        # The article's section order is organized by stage, not by the
        # story's clock: the 10:01 C Tower beat is written before 9:22
        # Shibuya Station. Where the arc carries extracted events, their time
        # axis orders the beats, and a section that carries none inherits the
        # last placed position, so a Prologue still reads first and an
        # Aftermath still reads last.
        if events_order_enabled() and len(narrative.beats) >= 2:
            narrative.beats = self._reorder_by_events(narrative.beats)
            for order, beat in enumerate(narrative.beats, start=1):
                beat.order = order

        return narrative

    def _alias_text(self, subject: str) -> str:
        """``subject`` plus the canonical names its per-wiki display names resolve to.

        The alias table carries only full page titles (CSM's "Bomb Girl arc"),
        so a question that names the arc by its bare display name links nothing.
        The per-wiki map (``config.subject_aliases``) resolves the display name,
        and the canonical name links through its own alias row.
        """
        if not self.aliases:
            return subject
        norm = " " + re.sub(r"[^a-z0-9]+", " ", subject.lower()) + " "
        hits = [c for d, c in self.aliases.items() if f" {d} " in norm]
        return " ".join([subject, *hits]) if hits else subject

    def authored_floor(self, subject: str, max_beats: int) -> list[Beat]:
        """The page a question is authored against, as its own section beats.

        The narrative read resolves the query's own words, and a question written
        against a fight ("what happens after Yuji regains control of his body?")
        resolves to the character the query names, walking that character's
        events -- never the fight's own page, where the Aftermath the question
        asks about is written. The qa path guards this with the entity-anchored
        floor (R6); the narrative path needs the same one, or a battle question
        routed here can never read the battle it is about.

        Only event-type pages carry a narrative of their own -- a battle's
        Prologue / Battle / Aftermath is a story, but a character's Appearance
        and Personality sections are a biography -- so a non-event subject
        yields no floor and the query-driven timeline stands unchanged.
        """
        node = self.store.node_by_name(
            self.aliases.get(subject.strip().lower()) or subject
        )
        if node is None or not node["is_resolved"] or node["label"] not in EVENT_TYPES:
            return []
        return self._beats_from_page(node["name"], max_beats)

    # ── ordering ─────────────────────────────────────────────────────────────

    def annotate(self, beat: Beat) -> Beat:
        """Attach the chapter and episode the beat's prose is sourced to.

        Two steps, both lookups rather than guesses. Markers the wiki wrote as
        a bare `(Chapter 79)` gain their episode from the graph's chapter/episode
        edges; then every sentence is attributed to the ref that covers it, so a
        beat whose only ref sits in its last paragraph still reports the span.
        """
        beat.text = cite.upgrade_markers(beat.text, self.episodes)
        sentences = cite.attribute(beat.text, self.episodes)
        found = cite.locators(sentences)
        beat.citations = [locator.render() for locator in found]
        beat.source_span = cite.span(found)
        return beat

    def _reorder_by_events(self, beats: list[Beat]) -> list[Beat]:
        """Reorder the subject page's beats onto the extracted events' time axis.

        The subject's own page always leads the stream (its sections come
        first, and the multi-page fallback and the neighbour stream only ever
        append), so its beats are the first document in the list. Only those
        are reordered: the neighbour beats are a separate stream of related
        pages whose order the events do not cover, and they keep their
        relative order behind the reordered page. A beat's section carries the
        event with the earliest `time_rank` in that section, and a section
        with no event inherits the rank of the last section that had one, so
        an unranked Prologue stays first and an unranked Aftermath stays last.
        Beats keep their `order` until `timeline` renumbers them.
        """
        if len(beats) < 2:
            return beats
        doc_title = beats[0].doc_title
        events = self.store.events_of(doc_title)
        if not events:
            return beats
        section_rank: dict[int, float] = {}
        for event in events:
            if not event["temporal"]:
                continue
            rank = float(event["time_rank"])
            section_id = int(event["section_id"])
            if section_id not in section_rank or rank < section_rank[section_id]:
                section_rank[section_id] = rank
        if not section_rank:
            return beats
        # Section id -> the beat that is that section, by the section's title.
        title_to_section: dict[str, int] = {}
        for section in self.store.document_sections(doc_title):
            title_to_section.setdefault(
                str(section["title"]).strip(), int(section["id"])
            )

        main = [beat for beat in beats if beat.doc_title == doc_title]
        others = [beat for beat in beats if beat.doc_title != doc_title]

        # Walk the page's beats in article order, carrying the last seen rank
        # forward so unranked sections inherit position rather than sorting
        # to the end.
        last_rank = float("-inf")
        keys: list[tuple[float, int]] = []
        for index, beat in enumerate(main):
            section_id = title_to_section.get(beat.title.strip())
            rank = section_rank.get(section_id) if section_id is not None else None
            if rank is not None:
                last_rank = rank
            keys.append((last_rank, index))
        reordered = [main[index] for _, index in sorted(keys)]
        return reordered + others

    def _beats_from_page(self, title: str, max_beats: int) -> list[Beat]:
        """A page's own sections, in the order the article presents them."""
        beats: list[Beat] = []

        for section in self.store.document_sections(title):
            # G15 (2026-08-31): this floor was lifted once as part of the
            # chunker fix and the `sourcing-01` gold regressed (35/40): the
            # Shibuya Incident beat stream gained 4-word furniture sections
            # ("Teams", "Navigation") that carry no refs and pushed unsourced
            # table sections into the top-40 window. The narrative path is a
            # script-writing path -- every beat must be sourceable -- so the
            # floor stays here. Short-section reachability lives in the
            # chunker (the qa path), where the floor is gone.
            if not section["text"]:
                continue
            # G30 (2026-09-04): a short Summary/Synopsis is the page's own prose
            # and must beat; only furniture still floors (G15: every beat
            # sourceable). See _PAGE_PROSE_SECTIONS for why the set is narrow.
            if (
                section["word_count"] < 20
                and section["title"].strip().lower() not in _PAGE_PROSE_SECTIONS
            ):
                continue
            beats.append(
                self.annotate(
                    Beat(
                        order=len(beats) + 1,
                        title=section["title"],
                        text=section["text"],
                        doc_title=title,
                        breadcrumb=section["breadcrumb"],
                        time=extract_time(section["breadcrumb"]),
                    )
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
                self.annotate(
                    Beat(
                        order=len(beats) + 1,
                        title=title,
                        text=body["text"],
                        doc_title=title,
                        breadcrumb=body["breadcrumb"],
                    )
                )
            )
            if len(beats) >= max_beats:
                break

        return beats

    def _beats_from_neighbours(
        self,
        node: dict[str, Any],
        room: int,
        existing: list[Beat],
        query: str,
    ) -> list[Beat]:
        """The pages the subject's own page leans on, in instalment order.

        A 3,000-word script written from one document reads like that document.
        The Shibuya Incident bundle was 128 beats and every one of them came from
        the `Shibuya Incident` page, while the battle pages it links (where the
        fights are actually described, blow by blow, with their own refs) were
        never reached. Only the strong (infobox) edges are followed, so this
        picks up the pages the wiki itself says belong to the event rather than
        everything the prose happens to mention.
        """
        if room <= 0:
            return []

        seen = {(beat.doc_title, beat.breadcrumb) for beat in existing}
        tokens = _query_content_tokens(query, node["name"])

        candidates: list[tuple[tuple[int, float], sqlite3.Row]] = []
        named: set[str] = {node["name"]}
        for row in self.store.edges_for([node["id"]], min_confidence=0.9, limit=200):
            for name in (row["source"], row["target"]):
                if name in named:
                    continue
                named.add(name)
                candidate = self.store.node_by_name(name)
                if (
                    candidate is None
                    or not candidate["is_resolved"]
                    or candidate["label"] not in NEIGHBOUR_TYPES
                ):
                    continue
                related = self._ordered_related(int(candidate["id"]))
                if related:
                    # `_ordered_related` only returns titles with a parseable
                    # instalment number, so this cannot be None.
                    key = cast("tuple[int, float]", instalment_number(related[0]))
                else:
                    key = (7, 0.0)
                candidates.append((key, candidate))

        beats: list[Beat] = []
        for _, candidate in sorted(candidates, key=lambda pair: pair[0]):
            if len(beats) >= room:
                break
            for beat in self._beats_from_page(candidate["name"], room - len(beats)):
                identity = (beat.doc_title, beat.breadcrumb)
                if identity in seen:
                    continue
                seen.add(identity)
                beats.append(beat)
                if len(beats) >= room:
                    break

        if len(tokens) >= 2:
            beats = [
                beat
                for beat in beats
                if any(token in f"{beat.title} {beat.text}".lower() for token in tokens)
            ]
        return beats

    def _filter_matches(self, beats: list[Beat], tokens: set[str]) -> list[Beat]:
        """Keep only beats that mention a query token, preserving their order.

        A story beats budget, and the Shibuya Incident page alone runs eighty
        thousand characters. For a specific query the beats that mention its
        words are the story ("sealed", "freed"); the gaps are skipped rather
        than letting a twenty-thousand-token budget run out before the
        unsealing arrives. Order is untouched: skipped beats leave gaps, never
        reorderings, and the survivors keep their place in the timeline.
        """
        if not tokens:
            return beats
        filtered = [
            beat
            for beat in beats
            if any(
                token in f"{beat.title} {beat.text}".lower() for token in tokens
            )
        ]
        return filtered if filtered else beats

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

    def _beats_from_character_events(
        self, node: dict[str, Any], max_beats: int, query: str = ""
    ) -> list[Beat]:
        """Events and battles the character participates in, chronologically.

        Ordered by each event's earliest linked instalment ("Chapter 83" for
        the Shibuya Incident, "Chapter 138" for the Culling Game Arc), so the
        narrative reads in story order rather than alphabetically.

        When the query names content, the events that match it most strongly
        anchor the timeline: "sealed ... freed" scores the Shibuya Incident
        highest, so the sealing and the unsealing-era events lead (in
        instalment order within each score band), everything from the anchor's
        instalment onward is kept, and his childhood is not. The strongest
        events come first so the budget reaches the end of the story, and a
        twenty-thousand-token bundle that ate the Shibuya Incident page in
        strict order would never reach the unsealing. Generic words
        ("without") score every page equally and anchor nothing.
        """
        relevant_tokens = _query_content_tokens(query, node["name"])

        events: list[tuple[tuple[int, float], sqlite3.Row, set[str], int]] = []
        seen: set[str] = set()

        for row in self.store.edges_for([node["id"]], min_confidence=0.3, limit=1000):
            for name in (row["source"], row["target"]):
                if name == node["name"] or name in seen:
                    continue
                seen.add(name)
                candidate = self.store.node_by_name(name)
                if (
                    candidate is None
                    or candidate["label"] not in _CHARACTER_EVENT_TYPES
                    or not candidate["is_resolved"]
                ):
                    continue
                related = self._ordered_related(int(candidate["id"]))
                if related:
                    # `_ordered_related` only returns titles with a parseable
                    # instalment number, so this cannot be None.
                    key = cast("tuple[int, float]", instalment_number(related[0]))
                else:
                    key = (7, 0.0)
                hits = _event_token_hits(candidate, self.store, relevant_tokens)
                title_hits = {
                    token for token in relevant_tokens
                    if token in candidate["name"].lower()
                }
                events.append((key, candidate, hits, len(hits) + len(title_hits)))

        if not events:
            return []

        # The strongest matches anchor the timeline; the band below them is
        # kept as context. For "sealed ... freed" the pages that mention both
        # (the Shibuya Incident, the unsealing fight) anchor, and everything
        # from their instalment onward is kept; his childhood is not. A weak
        # query where nothing scores above 1 falls back to the full
        # chronological timeline. A single rare phrase can still anchor
        # ("19 days" matches only the Culling Game page, so it anchors there).
        best = max(score for _, _, _, score in events)
        min_score = max(1, best - 1)
        strong = [event for event in events if event[3] >= min_score]
        if strong:
            best_events = [event for event in events if event[3] == best]
            threshold = min(event[0] for event in best_events)
            events = [
                event for event in events
                if event[0] >= threshold or event[3] == best
            ]

        # A query with two or more content words keeps only the sections that
        # mention them, so the budget covers the whole arc instead of running
        # out inside the first event page. A single phrase ("19 days", "origin")
        # is not filtered: its era is the answer, not just the pages that
        # spell the phrase out. Zero-hit events are dropped: a page that
        # mentions none of the query's words contributes nothing to it.
        filter_matches = len(relevant_tokens) >= 2
        if filter_matches:
            events = [event for event in events if event[2]]

        beats: list[Beat] = []
        for _, event, _, _ in sorted(
            events,
            key=lambda pair: (-pair[3], pair[0]) if filter_matches else pair[0],
        ):
            if len(beats) >= max_beats:
                break
            event_beats = self._beats_from_page(
                event["name"], max_beats - len(beats)
            )
            # Arc pages are tables of contents: "Culling Game Arc" links to
            # Chapters 138-221 but writes no prose of its own. Fall back to
            # the instalments it links, in numbered order.
            if len(event_beats) < 3:
                related = self._ordered_related(int(event["id"]))
                event_beats = self._beats_from_pages(
                    related, max_beats - len(beats)
                )
            if filter_matches:
                event_beats = self._filter_matches(event_beats, relevant_tokens)
            beats.extend(event_beats)
        return beats

    def _participants(self, node_id: int) -> list[str]:
        """Characters involved, taken from the strong (infobox) edges."""
        participants: list[str] = []
        for row in self.store.edges_for([node_id], min_confidence=0.9, limit=200):
            for name in (row["source"], row["target"]):
                node = self.store.node_by_name(name)
                if node and node["label"] == "character" and name not in participants:
                    participants.append(name)
        return participants

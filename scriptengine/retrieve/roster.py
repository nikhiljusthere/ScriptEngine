"""Enumeration: every member of a set, not the eight passages nearest a query.

Four of the five scripts in `sample scripts/` are rosters — "Every Apostle in
Berserk", "Every Forbidden Jutsu in Naruto", "Every Level of the Abyss", "What
It's Like to be Every Rank of Curse". They are lists by construction: one
section per member, in a deliberate order.

Neither existing mode can produce one. `qa` ranks passages and returns the
eight most similar, which is a sample of a set and not the set. `narrative`
walks one page's sections in order, which is a story and not a list. Asked for
"Every Rank of Curse in Jujutsu Kaisen" the engine used to return a single beat
from the `Volume 0` page.

A wiki already states its sets three ways, and this module reads all three and
keeps whichever answers the query best:

* **category** — `Cursed Spirits`, `Domain Expansions`, `Curse Users`. An editor
  put each page there by hand; that is a membership list.
* **page type** — every page whose infobox is the `Technique Infobox`. The
  ontology discovers those per wiki, so this needs no configuration.
* **infobox field** — the distinct values of one parameter across everything
  that declares it. Grouping the 43 pages that declare `class` by its value is
  literally the list of curse grades, straight out of the infoboxes.

Nothing here names a series. The field that holds a rank is found through the
wiki's own label for it ("Grade"), not through a table of field names.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from scriptengine.config import (
    SeriesPaths,
    Settings,
    get_settings,
    load_overrides,
    subject_ranking,
)
from scriptengine.retrieve import citations as cite
from scriptengine.stores.facts import NOISE_FACT_KEYS, FactStore, rank_subjects

# Phrasings that ask for a set rather than a story. A script titled "Every X"
# wants all of X.
_ENUMERATION = re.compile(
    r"\b(every|all|each|list of|ranks? of|types? of|kinds? of|levels? of|"
    r"grades? of|tiers? of|forms? of|members? of)\b",
    re.IGNORECASE,
)

# Words that say nothing about which set is wanted.
_STOPWORDS = {
    "every", "all", "each", "the", "of", "in", "and", "or", "a", "an", "list",
    "explained", "simply", "script", "video", "about", "what", "its", "it",
    "is", "are", "be", "to", "from", "for", "with", "you", "your", "we",
    "like", "being", "there", "their", "them", "this", "that", "how", "why",
}

# A publication date says nothing about the subject in a roster, on top of the
# presentational parameters every renderer skips.
_NOISE_FACTS = NOISE_FACT_KEYS | {"date"}

# Page types that name the work itself. Their titles supply the words a query
# uses to say which wiki it means — "in Jujutsu Kaisen" — which say nothing
# about which set inside it is wanted. Left in, they matched every category the
# wiki named after itself, and "Every Domain Expansion in Jujutsu Kaisen"
# enumerated the Jujutsu Kaisen Modulo chapters.
_WORK_TYPES = {"series", "anime", "manga", "novel", "game", "stage_play"}

# Words that ask for the set to be grouped into tiers rather than listed flat.
_GROUPING_HINTS = {
    "rank", "ranks", "grade", "grades", "level", "levels", "tier", "tiers",
    "class", "classes", "kind", "kinds", "type", "types", "stage", "stages",
}

MAX_MEMBERS = 40
# Generous on purpose: how much of each member a bundle can afford depends on
# how many members there are and on the caller's budget, so the trimming is done
# where the budget is known and this is only a ceiling.
MEMBER_CHARS = 6000
MIN_MEMBERS = 3

_TRAILING_NUMBER = re.compile(r"(\d+)\s*$")
_WORD = re.compile(r"[A-Za-z']+")


@dataclass
class Member:
    """One entry of the roster, with everything a section about it needs."""

    name: str
    label: str = ""
    group: str = ""                                  # e.g. "Grade 1"
    facts: list[dict[str, str]] = field(default_factory=list)
    debut: str = ""                                  # "(Chapter 16, Episode 7)"
    text: str = ""
    breadcrumb: str = ""
    citations: list[str] = field(default_factory=list)
    source_span: str = ""

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "label": self.label,
            "facts": self.facts,
            "text": self.text,
        }
        for key in ("group", "debut", "breadcrumb", "source_span"):
            if getattr(self, key):
                payload[key] = getattr(self, key)
        if self.citations:
            payload["citations"] = self.citations
        return payload


@dataclass
class Roster:
    """A set the wiki declared, rendered as ordered members."""

    subject: str
    basis: str = ""                                  # what the set was read from
    kind: str = ""                                   # category | type | field
    members: list[Member] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "basis": self.basis,
            "kind": self.kind,
            "groups": self.groups,
            "members": [member.as_dict() for member in self.members],
        }


def looks_like_enumeration(query: str) -> bool:
    """True when the topic asks for a set rather than an account."""
    return bool(_ENUMERATION.search(query or ""))


def content_words(text: str) -> list[str]:
    """The words that say which set is wanted."""
    return [
        word.lower()
        for word in _WORD.findall(text or "")
        if len(word) > 2 and word.lower() not in _STOPWORDS
    ]


def _overlap(candidate: str, words: list[str]) -> int:
    """How many of the query's words the candidate's name contains.

    Prefix matching, so "curse" reaches "Cursed Spirits" and "technique"
    reaches "Extension Techniques" without a stemmer.
    """
    lowered = (candidate or "").lower()
    return sum(1 for word in words if word[:5] in lowered)


def build_roster(
    paths: SeriesPaths,
    query: str,
    settings: Settings | None = None,
    max_members: int = MAX_MEMBERS,
    member_chars: int = MEMBER_CHARS,
) -> Roster:
    """Resolve `query` to a set the wiki declares, and render its members."""
    settings = settings or get_settings()
    demote, priority = subject_ranking(load_overrides(paths))
    words = content_words(query)

    with FactStore(paths.facts_db) as store:
        episodes = cite.EpisodeIndex.from_store(store)
        entities = rank_subjects(store.link_entities(query), demote, priority)
        subject = next(
            (row["name"] for row in entities if row["is_resolved"]),
            entities[0]["name"] if entities else query,
        )
        subject_label = next(
            (row["label"] for row in entities if row["is_resolved"]), ""
        )

        work = _work_words(store)
        words = [word for word in words if word not in work]

        best = _choose_set(store, words, subject, subject_label)
        if best is None:
            return Roster(subject=subject)

        kind, basis, names = best
        group_key, group_label = _grouping_field(store, names, words)
        members = [
            _render_member(store, episodes, name, group_key, member_chars)
            for name in names[:max_members]
        ]
        members = [member for member in members if member.text or member.facts]
        members.sort(key=lambda member: _member_order(member))

    roster = Roster(
        subject=subject,
        basis=f"{basis} ({group_label})" if group_label else basis,
        kind=kind,
        members=members,
    )
    roster.groups = _distinct([member.group for member in members if member.group])
    return roster


# ── choosing which set the query means ───────────────────────────────────────


def _work_words(store: FactStore) -> set[str]:
    """Words that name the work itself, not a set inside it."""
    words: set[str] = set()
    placeholders = ",".join("?" * len(_WORK_TYPES))
    rows = store.connection.execute(
        f"SELECT title FROM documents WHERE page_type IN ({placeholders})",
        tuple(_WORK_TYPES),
    ).fetchall()
    for row in rows:
        words.update(content_words(row["title"]))
    return words


def _score(basis: str, words: list[str], subject_words: list[str]) -> tuple[int, float]:
    """How well a set's own name answers the query.

    The query's words count double: they are what was asked for. The subject's
    words break the tie that the query cannot — "Every Rank of Curse" matches
    both `Cursed Spirits` and `Curse Users` equally, and the subject the query
    resolved to (`Cursed Spirit`) says which one it meant.

    The second number is how much of the set's name was matched, so a name that
    is entirely about the query beats a longer one that merely contains it.
    """
    matched = _overlap(basis, words) * 2 + _overlap(basis, subject_words)
    size = len(content_words(basis)) or 1
    return matched, matched / size


def _choose_set(
    store: FactStore, words: list[str], subject: str, subject_label: str
) -> tuple[str, str, list[str]] | None:
    """Return ``(kind, basis, member names)`` for the best-supported set.

    Scored on how well the set's own name answers the query, then on how much
    of that name the query accounts for, then on size: a set of three is often a
    coincidence, a set of twenty is usually the answer.
    """
    subject_words = content_words(subject)
    candidates: list[tuple[int, float, int, str, str, list[str]]] = []

    for term in _distinct([*words, *subject_words]):
        for row in store.categories_like(term, limit=8):
            if row["members"] < MIN_MEMBERS:
                continue
            names = [
                document["title"]
                for document in store.documents_in_category(row["category"], limit=200)
            ]
            matched, ratio = _score(row["category"], words, subject_words)
            candidates.append(
                (matched, ratio, len(names), "category", row["category"], names)
            )

    # The subject's own page type: asked about a technique, enumerate techniques.
    for label in _distinct([subject_label, *words]):
        if not label:
            continue
        rows = store.nodes_by_label(label.rstrip("s"), limit=200) or store.nodes_by_label(
            label, limit=200
        )
        if len(rows) >= MIN_MEMBERS:
            matched, ratio = _score(label, words, subject_words)
            candidates.append(
                (matched, ratio, len(rows), "type", label, [row["name"] for row in rows])
            )

    if not candidates:
        return None

    # A hand-curated category beats a page type at equal relevance: the wiki
    # chose its members, the type is everything that happens to share an infobox.
    ranking = {"category": 0, "type": 1}
    candidates.sort(
        key=lambda item: (-item[0], -item[1], ranking[item[3]], -item[2])
    )
    matched, _, _, kind, basis, names = candidates[0]
    if matched == 0:
        return None
    return kind, basis, names


def _grouping_field(
    store: FactStore, names: list[str], words: list[str]
) -> tuple[str, str]:
    """The infobox field the members should be grouped by, if the query asks.

    "Every Rank of Curse" is a set of curses grouped by rank. The field that
    holds a rank is found through the wiki's own label for it — Jujutsu Kaisen
    stores it as `class` and labels it "Grade" — so nothing here needs to know
    what a grade is.
    """
    if not names or not words:
        return "", ""

    # "Every Rank of Curse" asks for tiers even though no field is called
    # "rank": Jujutsu Kaisen keys the tier as `class` and labels it "Grade".
    # Both words come from the same small closed vocabulary that every wiki uses
    # for tiers, so a query written with one of them may match a field named
    # with another. That is a synonym rule over a fixed list, not a guess about
    # the data: matching on shape instead picked `race`, whose values all read
    # "Cursed Spirit", and `status`, whose values are "Alive" and "Deceased".
    wants_grouping = any(word in _GROUPING_HINTS for word in words)
    holders = set(names)
    best: tuple[int, int, str, str] | None = None

    for row in store.fact_keys(limit=200):
        key, label = row["key"], row["label"] or ""
        if key in _NOISE_FACTS:
            continue
        score = max(_overlap(key, words), _overlap(label, words))
        if not score and wants_grouping and _names_a_tier(key, label):
            score = 1
        if not score:
            continue
        values = [
            group["value"]
            for group in store.fact_groups(key, limit=2000)
            if group["name"] in holders
        ]
        distinct = len(set(values))
        # A field every member answers differently is an attribute, not a
        # grouping; one they all share is not a grouping either.
        if len(values) < MIN_MEMBERS or distinct < 2 or distinct > len(values) * 0.8:
            continue
        if best is None or (score, len(values)) > (best[0], best[1]):
            best = (score, len(values), key, label or key)

    return (best[2], best[3]) if best else ("", "")


def _names_a_tier(key: str, label: str) -> bool:
    """True when the wiki's own name for a field is tier vocabulary."""
    return any(
        name.strip().lower() in _GROUPING_HINTS for name in (key, label) if name
    )


# ── rendering one member ─────────────────────────────────────────────────────


def _render_member(
    store: FactStore,
    episodes: cite.EpisodeIndex,
    name: str,
    group_key: str,
    member_chars: int,
) -> Member:
    node = store.node_by_name(name)
    member = Member(name=name, label=node["label"] if node else "")

    facts = store.facts_for(name)
    for row in facts:
        if row["key"] in _NOISE_FACTS or not row["value"]:
            continue
        member.facts.append(
            {"field": row["label"] or row["key"], "value": row["value"]}
        )
        if group_key and row["key"] == group_key:
            member.group = row["value"]

    member.debut = _debut(facts, episodes)
    member.text, member.breadcrumb = _member_prose(store, name, member_chars)
    member.text = cite.upgrade_markers(member.text, episodes)

    found = cite.locators(cite.attribute(member.text, episodes))
    member.citations = [locator.render() for locator in found]
    member.source_span = cite.span(found)
    return member


def _debut(facts: list[Any], episodes: cite.EpisodeIndex) -> str:
    """The member's first appearance, manga and anime together."""
    chapter = episode = ""
    for row in facts:
        value = row["value"] or ""
        if row["key"] == "debut" and not chapter:
            match = re.search(r"Chapter\s+([\d.\-]+)", value, re.IGNORECASE)
            chapter = match.group(1) if match else ""
        if row["key"] in {"anime debut", "debutanime"} and not episode:
            match = re.search(r"Episode\s+([\d.\-]+)", value, re.IGNORECASE)
            episode = match.group(1) if match else ""

    locator = cite.Locator(chapter=chapter, episode=episode)
    return episodes.complete(locator).render()


def _member_prose(store: FactStore, name: str, member_chars: int) -> tuple[str, str]:
    """The lead plus the page's meatiest real section, capped."""
    from scriptengine.index.chunker import BOILERPLATE_SECTIONS

    lead = store.document_lead(name)
    sections = [
        row
        for row in store.document_sections(name)
        if (row["text"] or "")
        and row["title"].strip().lower() not in BOILERPLATE_SECTIONS
    ]
    sections.sort(key=lambda row: row["word_count"], reverse=True)

    body = sections[0] if sections else None
    breadcrumb = body["breadcrumb"] if body is not None else ""
    text = "\n\n".join(part for part in (lead, body["text"] if body is not None else "") if part)
    return text[:member_chars], breadcrumb


def _member_order(member: Member) -> tuple[int, float, str, str]:
    """Group first, then the member's name.

    Numbered groups sort by their number — plain numeric order, ascending, with
    no claim about which end is stronger — and groups the wiki did not number
    ("Special Grade") come after them. The script decides which direction to
    walk the list; the engine only has to keep members of one group together.
    """
    match = _TRAILING_NUMBER.search(member.group or "")
    if member.group and match:
        return (0, float(match.group(1)), member.group, member.name)
    if member.group:
        return (1, 0.0, member.group, member.name)
    return (2, 0.0, "", member.name)


def _distinct(values: list[str]) -> list[str]:
    seen: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    return seen

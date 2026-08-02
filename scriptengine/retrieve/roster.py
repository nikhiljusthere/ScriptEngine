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

# Categories the wiki keeps for the pages it could not classify, or for material
# outside the story. They are the opposite of what an enumeration wants, and
# they win on name matching precisely because they are named after the thing
# being asked for: "Every Nen Type" scored "Unknown Nen type users" (247 members)
# above Enhancers, Transmuters and Conjurers, which share no word with the query.
_ANTI_SET_WORDS = (
    "unknown", "unnamed", "unidentified", "unconfirmed", "non-canon",
    "noncanon", "outside", "possible", "former", "deceased", "list of",
    "candidates", "images", "gallery",
)

# Chainsaw Man lists 88 devils and One-Punch Man 219 mysterious beings. A cap of
# 40 silently answered "Every Devil" with half of them, which is a different
# script rather than a shorter one. The token budget in `_roster_context` is what
# actually decides how many fit; this only stops a runaway set.
MAX_MEMBERS = 150
# Generous on purpose: how much of each member a bundle can afford depends on
# how many members there are and on the caller's budget, so the trimming is done
# where the budget is known and this is only a ceiling.
MEMBER_CHARS = 6000
MIN_MEMBERS = 3

_TRAILING_NUMBER = re.compile(r"(\d+)\s*$")
_WORD = re.compile(r"[A-Za-z']+")


@dataclass(frozen=True)
class RosterDefinition:
    """A set this wiki declares, and the phrases that ask for it.

    Discovery scores the wiki's own vocabulary against the words in a topic,
    which is what let five wikis work with no code. It also cannot bridge the
    gap between what a viewer says and what an editor wrote: One-Punch Man files
    its monsters under `Mysterious Beings`, and no amount of scoring turns
    "monster" into that. Worse, a category named for the pages the wiki *could
    not* classify wins by containing the query's words — "Every Nen Type"
    resolved to `Unknown Nen type users`, 247 of them, instead of the six Nen
    categories.

    So the sets that matter are declared per series instead of guessed at. A
    declared topic resolves the same way every time; anything undeclared still
    goes through discovery.
    """

    name: str
    match: tuple[str, ...] = ()
    category: str = ""
    label: str = ""                                  # a discovered page type
    fact: tuple[str, str] = ("", "")                 # (key, value)
    group_by: str = ""
    # Group name -> the category holding its members. When set, the roster's
    # members *are* the groups: "Every Nen Type" is six types, not 111 users.
    groups: dict[str, str] = field(default_factory=dict)

    @classmethod
    def parse(cls, raw: dict) -> "RosterDefinition | None":
        name = str(raw.get("name") or "").strip()
        if not name:
            return None
        fact = raw.get("fact") or {}
        return cls(
            name=name,
            match=tuple(str(m).strip().lower() for m in (raw.get("match") or []) if m),
            category=str(raw.get("category") or ""),
            label=str(raw.get("label") or ""),
            fact=(str(fact.get("key") or ""), str(fact.get("value") or "")),
            group_by=str(raw.get("group_by") or ""),
            groups={str(k): str(v) for k, v in (raw.get("groups") or {}).items()},
        )

    def matched_phrase(self, query: str) -> str:
        """The longest declared phrase this topic contains, or ""."""
        lowered = f" {query.lower()} "
        best = ""
        for phrase in self.match:
            if re.search(rf"\b{re.escape(phrase)}s?\b", lowered) and len(phrase) > len(best):
                best = phrase
        return best

    def matches(self, query: str) -> int:
        """Length of the longest declared phrase this topic contains, else 0.

        Length rather than a boolean so "s-class hero" beats "hero" when a
        series declares both.
        """
        return len(self.matched_phrase(query))


def load_rosters(overrides: dict | None) -> list[RosterDefinition]:
    """The sets a series declares, from `series/<name>/overrides.yaml`."""
    declared = []
    for raw in (overrides or {}).get("rosters") or []:
        if isinstance(raw, dict):
            definition = RosterDefinition.parse(raw)
            if definition is not None:
                declared.append(definition)
    return declared


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
    """Resolve `query` to a set, declared if this series declares one."""
    settings = settings or get_settings()
    overrides = load_overrides(paths)
    demote, priority = subject_ranking(overrides)
    words = content_words(query)

    # Longest declared phrase wins, so a series can declare both "hero" and
    # "s-class hero" and the more specific topic gets the smaller set.
    declared = max(
        (d for d in load_rosters(overrides) if d.matches(query)),
        key=lambda d: d.matches(query),
        default=None,
    )

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

        # A declared set is a general one. When the topic narrows to a person,
        # the person wins: "Every Cursed Technique of Sukuna" wants Sukuna's
        # kit, not all 38 innate techniques, and a phrase broad enough to be
        # worth declaring is broad enough to swallow that.
        if declared is not None and _names_a_character(
            query, subject, subject_label, declared.matched_phrase(query)
        ):
            declared = None

        if declared is not None:
            if declared.groups:
                return _group_roster(store, episodes, declared, member_chars)
            names = _declared_members(store, declared)
            if names:
                members = _render_all(
                    store, episodes, names[:max_members], declared.group_by, member_chars
                )
                roster = Roster(
                    subject=declared.name, basis=declared.name, kind="declared",
                    members=members,
                )
                roster.groups = _distinct(
                    [m.group for m in members if m.group]
                )
                return roster

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


def _names_a_character(
    query: str, subject: str, subject_label: str, phrase: str
) -> bool:
    """True when the topic names a person on top of the set it asked for.

    The test is what the character contributes *beyond* the declared phrase,
    because these wikis name characters after the sets they belong to. "Every
    Monster" resolves to the character `TV Junkyard Monster` and "Every Public
    Safety Devil Hunter" to `Devil Hunter`, and in both the only word shared
    with the query is the phrase itself, so neither narrows anything. "Every
    Cursed Technique of Sukuna" contributes `sukuna`, which does.
    """
    if "character" not in (subject_label or "").lower():
        return False
    shared = set(content_words(subject)) & set(content_words(query))
    return bool(shared - set(content_words(phrase)))


def _declared_members(store: FactStore, declared: RosterDefinition) -> list[str]:
    """The pages behind a declared set, however the wiki holds them."""
    if declared.category:
        return [
            row["title"]
            for row in store.documents_in_category(declared.category, limit=400)
        ]
    if declared.label:
        return [row["name"] for row in store.nodes_by_label(declared.label, limit=400)]

    key, value = declared.fact
    if key:
        wanted = value.strip().lower()
        return [
            row["name"]
            for row in store.fact_groups(key, limit=4000)
            # `startswith` because a wiki writes "Devil (formerly) Fiend" in the
            # same field it writes "Devil".
            if not wanted or row["value"].strip().lower().startswith(wanted)
        ]
    return []


def _render_all(
    store: FactStore,
    episodes: cite.EpisodeIndex,
    names: list[str],
    group_by: str,
    member_chars: int,
) -> list[Member]:
    members = [
        _render_member(store, episodes, name, group_by, member_chars)
        for name in names
    ]
    members = [member for member in members if member.text or member.facts]
    members.sort(key=_member_order)
    return members


def _group_roster(
    store: FactStore,
    episodes: cite.EpisodeIndex,
    declared: RosterDefinition,
    member_chars: int,
) -> Roster:
    """A roster whose members are the groups themselves.

    "Every Nen Type" wants the six types, each with the people who use it — not
    a flat list of every Nen user. Hunterpedia holds the types only as
    categories, with no field on a character saying which one they are, so the
    set has to be assembled from the categories themselves.
    """
    members: list[Member] = []
    for name, category in declared.groups.items():
        rows = store.documents_in_category(category, limit=400)
        if not rows:
            continue
        holders = [row["title"] for row in rows]
        member = _render_member(store, episodes, name, "", member_chars)
        member.name = name
        member.group = declared.name
        member.facts = [
            {"field": "Members", "value": str(len(holders))},
            {"field": "Includes", "value": ", ".join(holders[:12])},
        ] + member.facts
        members.append(member)

    roster = Roster(
        subject=declared.name, basis=declared.name, kind="declared", members=members
    )
    roster.groups = [member.name for member in members]
    return roster


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
    lowered = (basis or "").lower()
    if any(word in lowered for word in _ANTI_SET_WORDS):
        # Halved rather than excluded: on a wiki where every set is named this
        # way it is still better than nothing, but it must never beat a real one.
        matched = matched // 2
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
            member.group = _group_label(row["value"])

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


def _group_label(value: str) -> str:
    """The tier a member belongs to, from a field that is often free text.

    Wikis qualify these values in prose: Chainsaw Man writes "Devil (80%)
    Fiend (20%, formerly)" in `species`, and One-Punch Man writes "Demon (Hero
    Association rating) Dragon (Actual)" in `level`. Grouping on the raw string
    gives one group per member, which is not a grouping at all. The first clause
    is the answer the wiki leads with.
    """
    first = (value or "").splitlines()[0] if value else ""
    return re.split(r"\s*[(\[]", first, maxsplit=1)[0].strip() or first.strip()


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

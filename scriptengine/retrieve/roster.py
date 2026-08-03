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

import json
import re
from collections.abc import Sequence
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
from scriptengine.retrieve import semantics as ontology
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

# Words that name what *kind* of set is wanted rather than narrowing it. They
# survive the set's own phrase — "Every Frieza Race transformation" leaves
# `frieza` and `race` behind once `Transformations` is accounted for — and
# enforcing `race` against every member rejected all 160 of them, which the
# never-empty guard then handed back whole. The constraint was `frieza`.
_SET_WORDS = {
    "race", "races", "species", "clan", "tribe", "form", "forms",
    "transformation", "transformations", "technique", "techniques",
    "ability", "abilities", "power", "powers", "member", "members",
    "user", "users", "state", "states", "mode", "modes",
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

# Categories that name how the work was *published* rather than a set inside the
# story. A wiki that prefixes those categories with its own title — most of them
# do — hands them every word of any query that names the series, so they win an
# enumeration outright: "Every race in Dragon Ball" returned the 150 titles of
# `Dragon Ball Z episodes`, and "Every race in One Piece" returned 116 volumes.
#
# Stripping the series' name from the query was the obvious fix and the wrong
# one: it also deletes the query. "All types of Dragon Balls" is asking about an
# object whose name *is* the series title, and it answers correctly today.
#
# So packaging is not banned, it is made to wait its turn. It can still win —
# "Every One Piece movie" should return `One Piece Movies` — but only when the
# query asked for packaging. Otherwise a set named after the story beats it.
_PACKAGING_WORDS = (
    "episode", "volume", "chapter", "saga", "arc", "film", "movie",
    "song", "album", "soundtrack", "opening", "ending", "game",
    "special", "merchandise", "video", "manga", "anime", "novel",
)

# Chainsaw Man lists 88 devils and One-Punch Man 219 mysterious beings. A cap of
# 40 silently answered "Every Devil" with half of them, which is a different
# script rather than a shorter one. The token budget in `_roster_context` is what
# actually decides how many fit; this only stops a runaway set.
#
# Raised from 150 after `Transformations` turned out to hold 160: the ten over
# the line were dropped without a word, which is the same failure at a different
# size. When even 300 is not enough the roster now says `capped`.
MAX_MEMBERS = 300
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
    # Several categories that together make one set. Distinct from `groups`,
    # where the groups *are* the members: One Piece keeps artificial races in
    # their own category, but "every race" wants all of them in one list, not a
    # list of two category names.
    categories: tuple[str, ...] = ()
    # Named outright, for a set the wiki never filed anywhere. There is no
    # Gods of Destruction category on the Dragon Ball wiki, and Hunterpedia's
    # `Royal Guards` page names its three members only in prose. This is data
    # about one series living in that series' own config, which is where
    # category names and match phrases already live.
    members: tuple[str, ...] = ()
    # A page whose sections *are* the set. Some sets are never a category
    # because no member has its own article: One Piece writes all twenty-two
    # Marine ranks as sections of `Marine Ranks`, and asking for them by
    # category returns `Marine Officers` — fourteen people, not the ladder.
    sections_of: str = ""
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
            categories=tuple(
                str(c).strip() for c in (raw.get("categories") or []) if c
            ),
            members=tuple(str(m).strip() for m in (raw.get("members") or []) if m),
            sections_of=str(raw.get("sections_of") or ""),
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
    # How much of the set's own name the topic actually asked for.
    #
    # Discovery returns its best-scoring candidate and used to have no way to
    # say the best was weak, so "Every Straw Hat Pirate" answered with
    # `Straw Hat Pirates' Creations` — the crew's weapons — and looked exactly
    # like a set that matched perfectly. The score is reported rather than
    # enforced: on a wiki whose only category for something is oddly named, a
    # partial match is still the answer, and the caller is the one that knows
    # whether 14 is the number it expected.
    confidence: str = "declared"                     # declared | exact | partial | weak
    unmatched: list[str] = field(default_factory=list)
    # Membership validation: how many the wiki's set held, and what was turned
    # away. Reported rather than applied quietly, because a list dropping from
    # 160 to 41 is something the caller has to be able to see and disagree with.
    candidates: int = 0
    rejected: list[dict[str, str]] = field(default_factory=list)
    scope: str = "canon"
    # The declared phrase that claimed this topic, or "" when it reached
    # discovery instead. Diagnostic: it separates "the registry sent this to the
    # wrong set" from "nothing was declared and scoring guessed".
    matched: str = ""
    # True when the set was larger than `MAX_MEMBERS` and the tail was dropped.
    # Silence here is how ten transformations went missing from a list of 160.
    capped: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "basis": self.basis,
            "kind": self.kind,
            "groups": self.groups,
            "confidence": self.confidence,
            "unmatched": self.unmatched,
            "candidates": self.candidates,
            "rejected": self.rejected,
            "scope": self.scope,
            "capped": self.capped,
            "members": [member.as_dict() for member in self.members],
        }

    @property
    def unfiltered(self) -> bool:
        """True when every candidate failed and the set was handed back whole."""
        return any(entry.get("reason") == "__unfiltered__" for entry in self.rejected)

    @property
    def unverified(self) -> str:
        """The words the topic narrowed by that nothing could be checked against."""
        for entry in self.rejected:
            reason = entry.get("reason", "")
            if reason.startswith("__unverified__"):
                return reason[len("__unverified__"):]
        return ""

    @property
    def warning(self) -> str:
        """What to tell a caller that asked for a set and got this one."""
        if self.unfiltered:
            return (
                f"nothing in {self.basis!r} satisfied the topic, so the whole set "
                "is shown unfiltered — treat it as the wrong set"
            )
        if self.capped:
            return (
                f"{self.basis!r} has {self.capped} members and only "
                f"{len(self.members)} were rendered — the rest were dropped"
            )
        if self.candidates and not self.members:
            return (
                f"{self.basis!r} has {self.candidates} members and none of them "
                "satisfied the topic"
            )
        if self.unverified:
            # Deliberately not "names nothing this wiki records" — that was the
            # old, narrower reason, and reusing it told a caller that `quincy`
            # was unknown on a wiki with fifty-four of them. What is true in
            # every case reaching here is that the word changed nothing.
            return (
                f"{self.unverified} did not narrow this set — every member was "
                f"kept, so this is all of {self.basis!r}"
            )
        if self.confidence in {"declared", "exact"}:
            return ""
        asked = ", ".join(self.unmatched)
        if self.confidence == "weak":
            return (
                f"{self.basis!r} matched nothing the topic asked for — "
                "this is probably not the set you meant"
            )
        return f"{self.basis!r} is narrower than the topic: {asked} was not asked for"


def looks_like_enumeration(query: str) -> bool:
    """True when the topic asks for a set rather than an account."""
    return bool(_ENUMERATION.search(query or ""))


def content_words(text: str) -> list[str]:
    """The words that say which set is wanted.

    Possessives are stripped. `_WORD` keeps the apostrophe, so "Sukuna's"
    tokenised as `sukuna's` and never matched `sukuna` — which meant that in
    "What is Sukuna's Domain Expansion?" the entity scored zero against the
    question and `Domain Expansion` won the subject on two words to nothing.
    That is the most natural way to ask a fact question, and it lost every time.
    """
    words = []
    for word in _WORD.findall(text or ""):
        lowered = word.lower()
        if lowered.endswith("'s") or lowered.endswith("s'"):
            lowered = lowered[:-2] if lowered.endswith("'s") else lowered[:-1]
        lowered = lowered.strip("'")
        if len(lowered) > 2 and lowered not in _STOPWORDS:
            words.append(lowered)
    return words


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
    # Scored on the query with the wiki's own name taken out, so "Every race in
    # Dragon Ball" competes for sets the way "Every race" does. The declared
    # registry above still sees the whole query, because a series may well
    # declare a set whose name contains the title.
    title = work_title(paths)
    words = content_words(strip_work_title(query, title))
    constraints = Constraints()

    # Longest declared phrase wins, so a series can declare both "hero" and
    # "s-class hero" and the more specific topic gets the smaller set.
    registry = load_rosters(overrides)
    declared = max(
        (d for d in registry if d.matches(query)),
        key=lambda d: d.matches(query),
        default=None,
    )
    # Every word this series uses to name a set. A word in here cannot be what
    # identifies a person, however many characters are named after it.
    vocabulary = {
        word
        for definition in registry
        for phrase in (*definition.match, definition.name)
        for word in content_words(phrase)
    }

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
            query, subject, subject_label, vocabulary
        ):
            declared = None

        constraints = parse_constraints(query, declared, title, overrides)

        if declared is not None:
            if declared.sections_of:
                roster = _sections_roster(store, declared, member_chars)
                if roster.members:
                    return roster
            if declared.groups:
                return _group_roster(store, episodes, declared, member_chars)
            names = _declared_members(store, declared)
            if names:
                # The category is what the wiki keeps; the topic may have asked
                # for less of it. `Transformations` holds Black Frieza because
                # it is one — "Saiyan" is the part only validation can enforce.
                candidates = len(names)
                names, rejected = apply_constraints(
                    store, names, constraints, declared.name, overrides=overrides
                )
                members = _render_all(
                    store, episodes, names[:max_members], declared.group_by, member_chars
                )
                roster = Roster(
                    subject=declared.name, basis=declared.name, kind="declared",
                    members=members, candidates=candidates, rejected=rejected,
                    scope=constraints.scope,
                    capped=len(names) if len(names) > max_members else 0,
                    matched=declared.matched_phrase(query),
                )
                # A declared set that survived nothing is not a declared answer.
                if roster.unfiltered:
                    roster.confidence = "weak"
                elif roster.unverified:
                    # The set is the wiki's, but the topic asked for less of it.
                    roster.confidence = "partial"
                roster.groups = _distinct(
                    [m.group for m in members if m.group]
                )
                return roster

        work = _work_words(store)
        words = [word for word in words if word not in work]

        best = _choose_set(store, words, subject, subject_label, title)
        if best is None:
            return Roster(subject=subject)

        kind, basis, names, confidence, unmatched = best
        # Discovery chose this set *using* the topic's words, so those words
        # cannot also be a constraint on its members: "Every Angel" picks
        # `Angels`, and nothing inside it has to say "angel" again.
        discovered = Constraints(
            qualifier=tuple(
                word
                for word in constraints.qualifier
                if not _mentions(basis.lower(), word)
            ),
            scope=constraints.scope,
            canon=constraints.canon,
        )
        candidates = len(names)
        names, rejected = apply_constraints(
            store, names, discovered, basis, overrides=overrides
        )

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
        confidence=confidence,
        unmatched=unmatched,
        candidates=candidates,
        rejected=rejected,
        scope=constraints.scope,
        capped=len(names) if len(names) > max_members else 0,
    )
    roster.groups = _distinct([member.group for member in members if member.group])
    return roster


# ── choosing which set the query means ───────────────────────────────────────


def _names_a_character(
    query: str, subject: str, subject_label: str, vocabulary: set[str]
) -> bool:
    """True when the topic names a person on top of the set it asked for.

    The test is what the character contributes beyond this series' own set
    vocabulary, because these wikis name characters after the sets they belong
    to. `TV Junkyard Monster`, `Devil Hunter` and `Dragon` are all character
    pages, and all of them share only set words with the topics that reach
    them, so none narrows anything. `Sukuna` shares `sukuna`, which is a name
    and not a set, so "Every Cursed Technique of Sukuna" is his kit rather than
    all 38 innate techniques.
    """
    if "character" not in (subject_label or "").lower():
        return False
    shared = set(content_words(subject)) & set(content_words(query))
    return bool(shared - vocabulary)


def _declared_members(store: FactStore, declared: RosterDefinition) -> list[str]:
    """The pages behind a declared set, however the wiki holds them."""
    if declared.members:
        # Checked against the store, so a typo or a renamed page shows up as a
        # short roster in `cli rosters` rather than as a silent omission.
        return [name for name in declared.members if store.node_by_name(name)]
    if declared.sections_of:
        rows, depth = _section_levels(store, declared.sections_of)
        return [row["title"] for row in rows if row["level"] == depth]
    if declared.categories:
        return _distinct(
            [
                row["title"]
                for category in declared.categories
                for row in store.documents_in_category(category, limit=400)
            ]
        )
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


def _section_levels(store: FactStore, page: str) -> tuple[list[Any], int]:
    """A page's sections, and which heading level holds its members.

    The level carrying the most sections is the set; anything shallower is a
    grouping. Shared by the roster itself and by the counting `cli rosters` and
    the catalogue do, so a declared set cannot be listed as empty while
    answering with 27 members.
    """
    rows = store.connection.execute(
        "SELECT s.title, s.level, s.ordinal, s.text, s.breadcrumb "
        "FROM sections s JOIN documents d ON d.id = s.document_id "
        "WHERE d.title = ? AND s.level > 1 ORDER BY s.ordinal",
        (page,),
    ).fetchall()
    if not rows:
        return [], 0
    counts: dict[int, int] = {}
    for row in rows:
        counts[row["level"]] = counts.get(row["level"], 0) + 1
    return rows, max(counts, key=lambda level: (counts[level], level))


# ── membership validation ────────────────────────────────────────────────────
#
# A category is what the wiki keeps, not what the topic asked for. The Dragon
# Ball wiki files `Black Frieza` under `Transformations` — correctly, it is one
# — so "Every Saiyan transformation" returned it, because nothing downstream
# ever asked the second half of the question.
#
# Everything needed to answer that half is already stored. `Black Frieza` sits
# in `Frieza's race` and declares `Users = Frieza`; `Super Saiyan Blue` sits in
# `Saiyans`. No new extraction, no embedding: the candidates just have to be
# checked against the constraints the topic actually carried.

# Fact fields naming who a thing belongs to, in the wikis' own labels.
_OWNER_FIELDS = ("users", "user", "inventor", "owner", "wielder", "practitioners")

# Fact fields naming what something is.
_RACE_FIELDS = ("race", "species", "clan", "tribe")

# Fields that classify rather than describe. `Similar Techniques` is
# deliberately absent: what a thing resembles is not what it belongs to.
_IDENTITY_FIELDS = ("class", "type", "kind", "affiliation", "allegiance", "occupation")

# `Debut` and `First appearance` carry the medium verbatim: "Manga: ...",
# "Game: Dragon Ball Heroes", "Movie: Resurrection 'F'".
_DEBUT_FIELDS = ("debut", "first appearance", "firstapp", "appears in")
_MEDIA_WORDS = {
    "manga": "manga", "anime": "anime", "movie": "film", "film": "film",
    "ova": "film", "special": "anime", "game": "game", "video game": "game",
}
# Games and spin-offs a debut names outright, with no "Game:" prefix.
_GAME_TITLES = (
    "fusions", "heroes", "xenoverse", "kakarot", "budokai", "tenkaichi",
    "fighterz", "legends", "dokkan", "online", "the breakers", "raging blast",
    "ultimate tenkaichi", "battle of z", "sparking",
)
# What counts as the story, unless a series says otherwise. Films are in by
# default because Dragon Ball's are canon — Broly, Battle of Gods — but Hunter x
# Hunter's are not, which is how Omokage, an original character from a
# non-canon film, reached the Phantom Troupe. A series overrides this with
# `canon_media:` in its overrides.yaml.
_CANON_MEDIA = {"manga", "anime", "film"}


def canon_media(overrides: dict | None) -> set[str]:
    declared = (overrides or {}).get("canon_media")
    if not declared:
        return set(_CANON_MEDIA)
    return {str(medium).strip().lower() for medium in declared if str(medium).strip()}

# Topics that want the lot, games and all.
_ALL_SCOPE = re.compile(
    r"\b(ever|any media|all media|non[- ]?canon|includ\w*\s+(the\s+)?(game|games)|"
    r"game\s+only|across\s+all)\b",
    re.IGNORECASE,
)

# Pages that index a set rather than belong to it.
_INDEX_TITLE = re.compile(r"^(list of|index of)\b", re.IGNORECASE)


def _stem(word: str) -> str:
    """Enough of a stem to make `heroes` and `hero` the same word.

    Not a stemmer: this only has to stop a set's own name looking like a
    constraint on its members, and `S-Class Heroes` vs "hero" was the case that
    slipped through a plural-`s` rule.
    """
    lowered = (word or "").lower()
    if lowered.endswith("ies") and len(lowered) > 4:
        return lowered[:-3] + "y"
    if lowered.endswith("es") and len(lowered) > 3:
        return lowered[:-2]
    return lowered.rstrip("s")


@dataclass(frozen=True)
class Constraints:
    """What a topic asked for beyond the name of the set."""

    qualifier: tuple[str, ...] = ()
    scope: str = "canon"                             # canon | all
    canon: frozenset[str] = frozenset(_CANON_MEDIA)  # what this wiki counts as story
    # Words the topic narrowed by that nothing in the wiki can be checked
    # against — "apocalypse level", "instant kill", "way to die".
    unverified: tuple[str, ...] = ()

    def __bool__(self) -> bool:
        return bool(self.qualifier) or self.scope != "canon"


def parse_constraints(
    query: str,
    declared: "RosterDefinition | None",
    title: str = "",
    overrides: dict | None = None,
) -> Constraints:
    """The words in a topic that narrow the set, and how wide to cast.

    "Every Saiyan transformation" resolves to the declared `Transformations`
    set; what is left of the topic once the set's own phrase and the wiki's name
    are removed is `saiyan`, and that is the constraint the members have to
    satisfy.
    """
    scope = "all" if _ALL_SCOPE.search(query or "") else "canon"
    remainder = strip_work_title(query or "", title)
    if declared is not None:
        phrase = declared.matched_phrase(query)
        if phrase:
            remainder = re.sub(
                rf"\b{re.escape(phrase)}s?\b", " ", remainder, flags=re.IGNORECASE
            )
        # The set's own name is not a constraint on its members either.
        own = {_stem(word) for word in content_words(declared.name)}
        remainder = " ".join(
            word for word in _WORD.findall(remainder) if _stem(word.lower()) not in own
        )

    qualifier = tuple(
        word
        for word in content_words(remainder)
        if word not in _GROUPING_HINTS and word not in _SET_WORDS
    )
    return Constraints(
        qualifier=qualifier, scope=scope, canon=frozenset(canon_media(overrides))
    )


@dataclass
class Profile:
    """What the store already knows about one candidate member."""

    name: str
    categories: tuple[str, ...] = ()
    identity: tuple[str, ...] = ()                   # who it belongs to, what it is
    owners: tuple[str, ...] = ()
    media: tuple[str, ...] = ()
    debut: str = ""

    def haystack(self) -> str:
        """Only the fields that say what this *is*, never every fact.

        Matching against all facts kept Black Frieza in a list of Saiyan
        transformations, because its `Similar Techniques` field names Super
        Saiyan. A field describing what something resembles is not a field
        describing what it belongs to.
        """
        return " ".join((self.name, *self.categories, *self.identity)).lower()


def _profile(store: FactStore, name: str) -> Profile:
    categories = tuple(store.categories_of(name))
    identity: list[str] = []
    owners: list[str] = []
    media: list[str] = []
    debut = ""

    for row in store.facts_for(name):
        label = (row["label"] or row["key"] or "").strip().lower()
        value = (row["value"] or "").strip()
        if not value:
            continue
        if label in _OWNER_FIELDS or label in _RACE_FIELDS or label in _IDENTITY_FIELDS:
            identity.append(value)
        if label in _OWNER_FIELDS:
            owners.extend(part for part in re.split(r"[,/\n]| and ", value) if part.strip())
        if label in _DEBUT_FIELDS and not debut:
            debut = value
            media.extend(_media_of(value))

    # A debut edge points at the instalment itself, and the instalment's own
    # page type says which medium it is. Hunterpedia files its films under
    # `anime debut`, so the field text calls Omokage's debut anime — but the
    # target is `Hunter × Hunter: Phantom Rouge`, typed `movie`, which is the
    # truth the string was hiding.
    for target in store.linked_from(name, ("debut", "manga debut", "anime debut", "first appearance")):
        row = store.connection.execute(
            "SELECT page_type FROM documents WHERE title = ? COLLATE NOCASE", (target,)
        ).fetchone()
        kind = (row["page_type"] if row else "").lower()
        if "movie" in kind or "film" in kind:
            media.append("film")
        elif "chapter" in kind:
            media.append("manga")
        elif "episode" in kind:
            media.append("anime")

    return Profile(
        name=name,
        categories=categories,
        identity=tuple(v.lower() for v in identity),
        owners=tuple(owner.strip() for owner in owners if owner.strip()),
        media=tuple(dict.fromkeys(media)),
        debut=debut,
    )


def _media_of(debut: str) -> list[str]:
    """Which media a debut names. `Movie: ... Manga: ...` names two."""
    lowered = debut.lower()
    found = [word for token, word in _MEDIA_WORDS.items() if f"{token}:" in lowered]
    if not found and any(game in lowered for game in _GAME_TITLES):
        found = ["game"]
    return found


def _owner_race(store: FactStore, owners: Sequence[str]) -> set[str]:
    """The second hop: a form belongs to whoever uses it, and they have a race.

    `Super Saiyan Blue` names Goku, and Goku's page says `Race = Saiyan`. This
    is the graph traversal that a category alone cannot supply, and it is only
    walked when the categories did not already answer.
    """
    races: set[str] = set()
    for owner in list(owners)[:6]:
        for row in store.facts_for(owner):
            label = (row["label"] or row["key"] or "").strip().lower()
            if label in _RACE_FIELDS and row["value"]:
                races.add(row["value"].lower())
    return races


def validate_member(
    store: FactStore,
    profile: Profile,
    constraints: Constraints,
    set_name: str,
    race_words: set[str] | None = None,
) -> str:
    """``""`` to keep the member, otherwise why it does not belong."""
    race_words = race_words if race_words is not None else set()
    # `Tier Harribel/Expanded Universe` is a second view of `Tier Harribel`, not
    # a second Vasto Lorde. Across four wikis, 504 titles carry a slash and 97%
    # of them have their parent in the store: alternate continuities, anime-only
    # variants, galleries. The parent is the entity.
    parent = profile.name.split("/", 1)[0].strip()
    if parent != profile.name and store.node_by_name(parent):
        return f"a subpage of {parent!r}, not a member in its own right"
    if _INDEX_TITLE.match(profile.name):
        return "an index page, not a member"
    # The eponymous page of the set: `Dragon Ball (object)` inside `Balls`,
    # `One Piece Movies` inside `One Piece Movies`. It describes the set.
    bare = re.sub(r"\s*\([^)]*\)\s*$", "", profile.name).strip().lower().rstrip("s")
    if bare and bare == (set_name or "").strip().lower().rstrip("s"):
        # `Dragon Ball (object)` inside `Dragon Balls`, `One Piece Movies`
        # inside `One Piece Movies`. The page is the set's own article.
        return "describes the set rather than belonging to it"

    if constraints.scope == "canon" and profile.media:
        if not (set(profile.media) & set(constraints.canon)):
            return f"outside the story ({profile.debut})" if profile.debut else "outside the story"

    if constraints.qualifier:
        haystack = profile.haystack()
        for word in constraints.qualifier:
            if word in race_words:
                # A race qualifier asks what the ability *is*, not who has used
                # it. Kaio-ken is used by a Saiyan and is not a Saiyan
                # transformation; King Kai taught it and Krillin knows it.
                #
                # Two things the wiki's own fields settle before ancestry does.
                # A page the wiki calls a power-up and never a transformation is
                # something stacked on top of a form rather than a form:
                # `Dark Dragon Ball Enhancement` is granted by Dark Shenron and
                # coexists with Super Saiyan.
                if ontology.is_power_up_only(store, profile.name):
                    return "a power-up rather than a form of its own"
                # A stored classification, where the wiki's fields ran out.
                # Only ever consulted to *reject*: a wrong property costs one
                # member's precision and can never invent one.
                judged = _semantic_reason(store, profile.name, word)
                if judged:
                    return judged
                acquisition = classify(store, profile.name, race_words)
                # Filed under three or more races *and* used by a crowd: that is
                # something handed out, not something a body does. `Unlock
                # Potential` reaches Earthlings, Majin and Saiyans across
                # eighteen users. Breadth alone is not enough — `Golden Great
                # Ape` is filed under three because Baby is a Tuffle wearing a
                # Saiyan, and it is still a Saiyan form.
                filed = [
                    category
                    for category in profile.categories
                    if category.lower().rstrip("s") in {w.rstrip("s") for w in race_words}
                ]
                #
                # Twelve is measured, not principled: Golden Great Ape has 11
                # users and Unlock Potential 18, and nothing structural
                # separates them. It is the weakest rule here, and the
                # index-time classifier is what should replace it.
                if len(filed) >= 3 and len(acquisition.users) >= 12:
                    return f"open to {len(filed)} races, so not intrinsic to {word}"
                if acquisition.belongs_to(word):
                    continue
                if acquisition.kind == TEACHABLE:
                    return f"teachable, not exclusive to {word}"
                return f"not {word}"
            if _mentions(haystack, word):
                continue
            # For anyone other than a race — "techniques of Sukuna" — being used
            # by them is exactly the right test.
            if _mentions(" ".join(_owner_race(store, profile.owners)), word):
                continue
            return f"not {word}"
    return ""


def _semantic_reason(store: FactStore, name: str, race: str) -> str:
    """Why an index-time classification disqualifies this from a race's forms.

    Read from the `semantics` table, written once by `cli classify`. Nothing is
    computed here and no model is called: retrieval reads a row, so the same
    question answers the same way twice.

    Only the disqualifying properties are acted on. A page the classifier never
    saw, or that it declined to judge, falls through to the structural rules
    exactly as before.
    """
    stored = store.semantics_of(name)
    if not stored:
        return ""
    properties = stored["properties"]
    detail = f" — {stored['reason']}" if stored["reason"] else ""

    # Race-exclusivity outranks everything else here. A form can need a full
    # moon or a ritual of five Saiyans and still be something only a Saiyan
    # body does — the classifier reads those external *triggers* as external
    # grants, and on their own they prove nothing.
    if properties.get("race_exclusive"):
        return ""
    if properties.get("externally_granted"):
        return f"granted from outside, not intrinsic to {race}{detail}"
    if properties.get("requires_artifact") or properties.get("requires_fusion"):
        return f"needs something outside the body, so not intrinsic to {race}{detail}"
    if properties.get("stackable") and not properties.get("biologically_intrinsic"):
        return f"stacks on another form rather than being one{detail}"
    if properties.get("teachable"):
        return f"teachable, so not exclusive to {race}{detail}"
    return ""


def _mentions(haystack: str, word: str) -> bool:
    """Prefix matching, so `saiyan` reaches `Saiyans` and `Saiyan beyond God`."""
    return word[:5] in haystack if len(word) > 4 else word in haystack


# ── how an ability is acquired ───────────────────────────────────────────────
#
# "Every Saiyan transformation" kept Kaio-ken, because Goku is a Saiyan and Goku
# uses it. That is the wrong test: King Kai invented Kaio-ken and Krillin,
# Yamcha and Vegito use it too. It is a technique anyone can be taught, not
# something a Saiyan body does.
#
# The distinction is in the data and needs no per-series rule. An ability whose
# users all share one race is exclusive to that race; one whose users span races
# is teachable. If another race learns it later, the classification changes by
# itself, because it was never written down.

_INVENTOR_RELATIONS = ("inventor", "creator", "developer", "originator")
_USER_RELATIONS = ("user", "users", "wielder", "wielders", "practitioner", "practitioners")

RACE_EXCLUSIVE = "race_exclusive"
CHARACTER_SPECIFIC = "character_specific"
TEACHABLE = "teachable"
UNKNOWN = "unknown"


@dataclass(frozen=True)
class Acquisition:
    """How an ability is come by, derived rather than declared."""

    kind: str = UNKNOWN                              # see the constants above
    races: tuple[str, ...] = ()                      # lowered, as the wiki writes them
    users: tuple[str, ...] = ()

    def belongs_to(self, race: str) -> bool:
        """Is this exclusive to `race`? Teachable and unknown never are."""
        if self.kind not in {RACE_EXCLUSIVE, CHARACTER_SPECIFIC}:
            return False
        return any(_mentions(known, race) for known in self.races)

    def as_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "races": list(self.races)}


def _race_of(store: FactStore, name: str) -> set[str]:
    """What race a character is, from their own page."""
    races = {
        (row["value"] or "").lower()
        for row in store.facts_for(name)
        if (row["label"] or row["key"] or "").strip().lower() in _RACE_FIELDS
        and row["value"]
    }
    return {race for race in races if race}


def classify(store: FactStore, name: str, race_words: set[str]) -> Acquisition:
    """Work out how `name` is acquired, from users, inventor and categories."""
    users = store.linked_from(name, _USER_RELATIONS)
    inventors = store.linked_from(name, _INVENTOR_RELATIONS)

    # An inventor that *is* a race — the Dragon Ball wiki writes
    # `inventor = Saiyan` on Super Saiyan — settles it outright.
    for inventor in inventors:
        if inventor.lower() in race_words:
            return Acquisition(RACE_EXCLUSIVE, (inventor.lower(),), tuple(users))

    # The member's own race categories: `Super Saiyan Blue` is filed under
    # `Saiyans`, which is the wiki stating the same thing a different way.
    filed = {
        category.lower()
        for category in store.categories_of(name)
        if category.lower().rstrip("s") in {word.rstrip("s") for word in race_words}
    }

    # The wiki's own filing outranks anything inferred from users. `Super Saiyan
    # Blue` sits in `Saiyans` and nowhere else racial; that is the editors
    # saying what it is, and it beats a game avatar who can be any race.
    # Two is still exclusive, not universal: `Beast` is filed under `Saiyans`
    # and `Earthlings` because Gohan is half of each, and no third race can
    # reach it. Filed under four or more and the category has stopped meaning
    # anything, so fall through to the users.
    if filed and len(filed) < 4:
        return Acquisition(RACE_EXCLUSIVE, tuple(sorted(filed)), tuple(users))

    races: set[str] = set()
    for user in users[:12]:
        # Game-only users are out of scope for the same reason game-only members
        # are: the Xenoverse avatar can be any race, and letting it vote turns
        # every Saiyan form into something anyone can have.
        if not (set(_profile(store, user).media) - {"game"}) and _profile(store, user).media:
            continue
        races |= _race_of(store, user)
        if user.lower() in race_words:
            races.add(user.lower())

    # An inventor of another race makes it teachable however its users look:
    # King Kai taught Goku, so Kaio-ken is not something Saiyans simply have.
    for inventor in inventors:
        invented_by = _race_of(store, inventor)
        if invented_by and not (invented_by & races) and not filed:
            return Acquisition(TEACHABLE, tuple(sorted(races)), tuple(users))

    if not races:
        return Acquisition(
            RACE_EXCLUSIVE if filed else UNKNOWN, tuple(sorted(filed)), tuple(users)
        )

    # Do the users' races agree? Compared on the race words the wiki knows, so
    # "1/2 Saiyan-1/2 Human-type Earthling" counts as Saiyan *and* Earthling.
    named = {word for word in race_words for race in races if _mentions(race, word)}
    if filed:
        named |= {category.rstrip("s") for category in filed}
    if len(named) == 1 or (len(users) == 1 and named):
        kind = CHARACTER_SPECIFIC if len(users) == 1 else RACE_EXCLUSIVE
        return Acquisition(kind, tuple(sorted(named)), tuple(users))
    if len(named) > 1:
        return Acquisition(TEACHABLE, tuple(sorted(named)), tuple(users))
    return Acquisition(UNKNOWN, (), tuple(users))


def race_vocabulary(store: FactStore) -> set[str]:
    """Every word this wiki uses to name a race, from its own race fields.

    Data-driven so it carries across series without a list: `Saiyan` qualifies
    on Dragon Ball for the same reason `Quincy` would on Bleach and `Mink` on
    One Piece — a character page says so.
    """
    words: set[str] = set()
    placeholders = ",".join("?" * len(_RACE_FIELDS))
    rows = store.connection.execute(
        f"SELECT DISTINCT value FROM facts"
        f" WHERE LOWER(label) IN ({placeholders}) OR LOWER(key) IN ({placeholders})",
        (*_RACE_FIELDS, *_RACE_FIELDS),
    ).fetchall()
    for row in rows:
        words.update(content_words(row["value"] or ""))

    # Race fields are free text — "Saiyan (Super Saiyan God)", "1/2 Saiyan-1/2
    # Human-type Earthling", "Frieza Clan (mutant)" — so the words alone include
    # `form`, `formerly` and `american`. A race the wiki takes seriously has an
    # article about it; the rest are punctuation with ambitions.
    return {word for word in words if store.node_by_name(word)}


def _grounded(store: FactStore, constraints: Constraints) -> Constraints:
    """Keep only the qualifier words that name something the wiki has a page for.

    "Every Cursed Technique of Sukuna" leaves `cursed` behind once the set
    (`Sukuna Techniques`) has accounted for the rest — and `cursed` is not a
    thing, it is what this wiki calls every technique. Enforcing it threw away
    Malevolent Shrine, which is filed under `Sukuna Techniques` and says nothing
    about being cursed because on this wiki that goes without saying.

    A word with its own article is different: `Saiyan` is a race, so "Every
    Saiyan transformation" really is asking for a subset. The test is whether
    the wiki wrote a page about the word.
    """
    if not constraints.qualifier:
        return constraints
    return Constraints(
        qualifier=tuple(
            word for word in constraints.qualifier if store.node_by_name(word)
        ),
        scope=constraints.scope,
        canon=constraints.canon,
        # The words that had to be dropped. "Every Apocalypse Level Devil"
        # narrows `Devils` by a property no page records, so the qualifier
        # cannot be enforced — and the answer that comes back is all 88 devils.
        # Reported, so the topic is not silently widened.
        unverified=tuple(
            word for word in constraints.qualifier if not store.node_by_name(word)
        ),
    )


def _rule_of(reason: str) -> str:
    """Which validation rule produced this rejection."""
    if "subpage of" in reason:
        return "subpage"
    if "describes the set" in reason or "index page" in reason:
        return "eponym"
    if "outside the story" in reason:
        return "canon"
    if "this is a set of" in reason:
        return "type"
    return "qualifier"


def _disagrees(semantic: str, wanted: str) -> str:
    """Why this candidate is not the kind of thing the set is made of.

    Only fires when the set has a clear majority type and the candidate has a
    known, different one — an unclassified page is left alone rather than
    guessed at.
    """
    if wanted == ontology.UNKNOWN or semantic == ontology.UNKNOWN:
        return ""
    if semantic == wanted:
        return ""
    # Organisations are never rejected. They sit inside other organisations —
    # a division of an army is a member of it — and wikis reach for a group
    # infobox for anything collective, so `Angel` and `Shadow Dragon` are typed
    # that way on a page about a race. Turning those away cost three real races
    # to catch nothing.
    if semantic == ontology.ORGANIZATION:
        return ""
    # Within a family, never. Whether a page reads `technique` or
    # `transformation` depends on whether an editor filled in a `Class` field,
    # so letting the majority decide would throw out Super Saiyan for
    # disagreeing with the techniques around it.
    if semantic in ontology.ABILITY_TYPES and wanted in ontology.ABILITY_TYPES:
        return ""
    # A set of people admits people. This is what empties `Galactic Frieza Army`
    # of the planets it conquered and the armour it issues.
    if wanted == ontology.CHARACTER or semantic in ontology.NEVER_MEMBERS:
        return f"{ontology.article(semantic)}, and this is a set of {wanted}s"
    return ""


def apply_constraints(
    store: FactStore,
    names: list[str],
    constraints: Constraints,
    set_name: str,
    max_rejections: int = 40,
    overrides: dict | None = None,
) -> tuple[list[str], list[dict[str, str]]]:
    """Keep the candidates that belong, and say why the rest do not.

    Never returns an empty set from a non-empty one. A wiki whose fields are
    named differently, or a qualifier nothing happens to record, would otherwise
    turn a correct list into nothing at all — and a list that is visibly too
    broad is more useful than a blank one, provided the caller is told.
    """
    constraints = _grounded(store, constraints)
    race_words = (
        race_vocabulary(store)
        if any(True for _ in constraints.qualifier)
        else set()
    )

    # What this set is mostly made of. A category is a filing decision, not a
    # membership one: `Galactic Frieza Army` holds 121 characters and also the
    # planets it conquered, the armour it issues and the battles it fought.
    types = {name: ontology.semantic_type(store, name, overrides) for name in names}
    wanted = ontology.expected_type(names, types)

    if constraints.unverified:
        rejected_note = ", ".join(repr(word) for word in constraints.unverified)
        unverifiable = [{"name": "", "reason": f"__unverified__{rejected_note}"}]
    else:
        unverifiable = []

    kept: list[str] = []
    rejected: list[dict[str, str]] = []
    # Which rule turned each candidate away. Counted rather than inferred from
    # the wording, because the confidence test below has to know whether the
    # *qualifier* did any work or whether the eponym and type rules did it all.
    by_rule: dict[str, int] = {}
    for name in names:
        reason = _disagrees(types.get(name, ontology.UNKNOWN), wanted) or validate_member(
            store, _profile(store, name), constraints, set_name, race_words
        )
        if reason:
            rule = _rule_of(reason)
            by_rule[rule] = by_rule.get(rule, 0) + 1
            if len(rejected) < max_rejections:
                rejected.append({"name": name, "reason": reason, "rule": rule})
        else:
            kept.append(name)

    if not kept:
        # Everything failed. Returning the unfiltered set is still better than a
        # blank one — but it must not look like an answer. "Every Frieza Race
        # transformation" came back as all 160 transformations wearing the same
        # `declared` badge as a set that was actually checked, which is the
        # worst of both. The caller is told by the empty `kept` flag.
        return names, [{"name": "", "reason": "__unfiltered__"}]
    # A qualifier that rejected nothing did not narrow anything, whatever the
    # counts say. Testing `len(kept) == len(names)` instead was wrong in three
    # measured cases: "Every Way Sorcerers Can Die" went 68 → 67 and "Every
    # Kai" 218 → 169, but every one of those rejections came from the eponym,
    # type and canon rules — the constraint itself did no work, and the answer
    # was still the whole set wearing `declared`.
    if (constraints.qualifier or constraints.unverified) and not by_rule.get("qualifier"):
        # The qualifier rejected nobody. That has two very different causes and
        # conflating them downgraded three correct answers: "Every Quincy
        # Sternritter" is right *because* every Sternritter is a Quincy, and it
        # was told that `quincy` "names nothing this wiki records" — on a wiki
        # with a 54-member Quincy set.
        #
        # So ask whether the members satisfy it. Redundant-but-true is a good
        # answer; unenforceable is not.
        words = constraints.unverified or constraints.qualifier
        # Every word, not any. "Every Way Sorcerers Can Die in the Culling Game"
        # leaves `way`, `die`, `culling`, `game`, and most sorcerer pages do
        # mention the Culling Game — so `any` called the constraint satisfied and
        # handed back all 67 sorcerers as a confident answer about ways to die.
        satisfied = sum(
            1
            for name in kept[:20]
            if all(_mentions(_profile(store, name).haystack(), word) for word in words)
        )
        if satisfied < max(1, min(len(kept), 20) // 2):
            note = ", ".join(repr(word) for word in words)
            return kept, rejected + [
                {"name": "", "reason": f"__unverified__{note}", "rule": "meta"}
            ]
    return kept, rejected


def _sections_roster(
    store: FactStore, declared: RosterDefinition, member_chars: int
) -> Roster:
    """A set the wiki wrote as one page, one section per member.

    The level carrying the most sections is taken to be the members, and the
    nearest shallower heading above each one is its group — which on a rank
    ladder is exactly the structure the page already has: three divisions at
    level 2, twenty-two ranks at level 3.
    """
    rows, depth = _section_levels(store, declared.sections_of)
    if not rows:
        return Roster(subject=declared.name)

    members: list[Member] = []
    group = ""
    for row in rows:
        if row["level"] < depth:
            group = row["title"]
            continue
        if row["level"] != depth:
            continue
        text = (row["text"] or "").strip()
        members.append(
            Member(
                name=row["title"],
                group=group,
                text=text[:member_chars],
                breadcrumb=row["breadcrumb"] or "",
                source_span=cite.span(
                    [locator for _, _, locator in cite.parse_markers(text)]
                ),
            )
        )

    roster = Roster(
        subject=declared.name,
        basis=f"{declared.sections_of} (sections)",
        kind="sections",
        members=members,
    )
    roster.groups = _distinct([member.group for member in members if member.group])
    return roster


def _asks_for_packaging(words: list[str]) -> bool:
    """True when the query itself named a volume, an episode, a film."""
    return any(word.rstrip("s") in _PACKAGING_WORDS for word in words)


def work_title(paths: SeriesPaths) -> str:
    """The wiki's own name, as one lowercase run of letters.

    Read from the host in the manifest — `dragonball.fandom.com` — rather than
    from a page, because the page can be absent. Dragon Ball's own article was
    typed `unknown` and a prune deleted it, so anything that learns the series'
    name from its pages learns nothing on exactly the wiki that needs it most.
    """
    try:
        data = json.loads(paths.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    host = str(data.get("wiki", "")).split("//")[-1].split("/")[0]
    return re.sub(r"[^a-z]", "", host.split(".")[0].lower())


def rate_match(basis: str, words: list[str], subject_words: list[str]) -> tuple[str, list[str]]:
    """How much of the set's own name the topic accounted for.

    Returns ``(confidence, unmatched_words)``. A set whose name is entirely
    explained by the topic is `exact`; one carrying a word the topic never
    mentioned is `partial`, and that word is usually the whole problem —
    `Straw Hat Pirates' Creations` is `partial` on "creations", which is exactly
    why it is the wrong answer to "Every Straw Hat Pirate".

    `weak` means nothing in the topic matched the name at all: it won on the
    subject alone, which on a query the wiki has no set for is how four
    non-canon admirals came back for "Every admiral".
    """
    names = content_words(basis)
    if not names:
        return "weak", []
    unmatched = [
        name
        for name in names
        if not any(word[:5] in name or name[:5] in word for word in words)
    ]
    if _overlap(basis, words) == 0:
        return "weak", unmatched
    if not unmatched:
        return "exact", []
    # A word the subject explains was still asked for, just indirectly.
    unmatched = [
        name
        for name in unmatched
        if not any(word[:5] in name or name[:5] in word for word in subject_words)
    ]
    return ("exact", []) if not unmatched else ("partial", unmatched)


def strip_work_title(text: str, title: str) -> str:
    """Remove the wiki's own name from `text`, and nothing else.

    Every category a wiki names after itself — `Dragon Ball media`, `One Piece
    Volumes` — contains every word of any query that names the series, so it
    outscores the set that was actually asked for. Removing the title from both
    sides of the comparison is what makes "Every race in Dragon Ball" score the
    way "Every race" already did.

    Only an *exact* run of words counts, which is what keeps the adversarial
    case working: "Dragon Balls" concatenates to `dragonballs`, not
    `dragonball`, so the object keeps its name while the series loses it.
    """
    if not title or not text:
        return text
    words = _WORD.findall(text)
    keep: list[str] = []
    index = 0
    while index < len(words):
        run, span = "", 0
        for end in range(index, len(words)):
            run += words[end].lower()
            if run == title:
                span = end - index + 1
                break
            if not title.startswith(run):
                break
        if span:
            index += span
        else:
            keep.append(words[index])
            index += 1
    return " ".join(keep)


def _score(
    basis: str,
    words: list[str],
    subject_words: list[str],
    wants_packaging: bool = True,
) -> tuple[int, float]:
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
    if not wants_packaging and any(word in lowered for word in _PACKAGING_WORDS):
        # Quartered rather than excluded, for the same reason: a wiki whose only
        # category for something is a publication category should still answer,
        # but it must lose to any set named after the story itself.
        matched = matched // 4
    size = len(content_words(basis)) or 1
    return matched, matched / size


def _choose_set(
    store: FactStore,
    words: list[str],
    subject: str,
    subject_label: str,
    title: str = "",
) -> tuple[str, str, list[str]] | None:
    """Return ``(kind, basis, member names)`` for the best-supported set.

    Scored on how well the set's own name answers the query, then on how much
    of that name the query accounts for, then on size: a set of three is often a
    coincidence, a set of twenty is usually the answer.
    """
    subject_words = content_words(strip_work_title(subject, title))
    wants_packaging = _asks_for_packaging(words)
    candidates: list[tuple[int, float, int, str, str, list[str]]] = []

    for term in _distinct([*words, *subject_words]):
        for row in store.categories_like(term, limit=8):
            if row["members"] < MIN_MEMBERS:
                continue
            names = [
                document["title"]
                for document in store.documents_in_category(row["category"], limit=200)
            ]
            matched, ratio = _score(
                strip_work_title(row["category"], title),
                words,
                subject_words,
                wants_packaging,
            )
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
            matched, ratio = _score(
                strip_work_title(label, title), words, subject_words, wants_packaging
            )
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
    confidence, unmatched = rate_match(
        strip_work_title(basis, title), words, subject_words
    )
    return kind, basis, names, confidence, unmatched


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

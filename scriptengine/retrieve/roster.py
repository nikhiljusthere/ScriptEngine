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
import sqlite3
from collections import Counter
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
    # The person this set is about, when it is deliberately about one.
    #
    # A declared set is normally a general one, so `build_roster` discards it the
    # moment the topic narrows to a character -- "Every Cursed Technique of
    # Sukuna" wants Sukuna's kit, not all 38 innate techniques. That rule is
    # right and it also made a whole class of set undeclarable: "Every ability of
    # Serpico" is *only* about a person, and the character path answers it with
    # the three section headings on his page while the three items the wiki
    # actually lists sit in the store filed as equipment.
    #
    # Naming the subject says "this one is about a person on purpose" and stops
    # the fallthrough. It is the narrow exception, not a way around the rule:
    # without it the general path still wins, as it should.
    subject: str = ""

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
            subject=str(raw.get("subject") or "").strip(),
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

    # Order is not membership. "Every arc in order" is set-shaped, so it reached
    # the discovery path and answered with the 84 chapters of a single arc.
    # Imported here rather than at module scope because chronology builds
    # `Roster` and `Member`, which live in this module.
    from scriptengine.retrieve import chronology

    if chronology.wants_chronology(query):
        ordered = chronology.build_chronology(paths, query, max_members)
        if ordered is not None:
            return ordered

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
        #
        # Unless the set says outright that it is about that person. `subject:`
        # is how a series declares the exception, and without it the general
        # path still wins.
        if (
            declared is not None
            and not declared.subject
            and _names_a_character(query, subject, subject_label, vocabulary)
        ):
            declared = None

        constraints = parse_constraints(query, declared, title, overrides)

        # "Every form of Goku" is a question about Goku, not about
        # `Transformations` narrowed by his name. Taken before the declared and
        # discovered paths because both of them resolve to a set filed by kind,
        # and no amount of filtering one turns it into the other.
        kinds = widen_umbrella(words, _asked_kinds(words, overrides))
        character = (
            _character_subject(
                store, words, overrides, race_vocabulary(store), vocabulary
            )
            if kinds
            else ""
        )
        # A declared set that names its subject *is* the answer for that person,
        # so it runs instead of the character path rather than after it. The
        # character path returns as soon as it finds anything, and on exactly
        # these questions what it finds is wrong: Serpico's page yields its three
        # section headings, and "Every form of Majin Buu" resolves to Kid Buu
        # because no `Majin Buu` page exists to resolve to.
        if declared is not None and declared.subject:
            character = ""

        if character and kinds and not _files_by_character(
            store, character, kinds, overrides
        ):
            owned = _owned_roster(
                store, episodes, character, kinds, constraints, overrides,
                max_members, member_chars,
            )
            # What the wiki wrote on its own page, read both ways: the headings
            # it wrote, and the abilities named in the prose under them.
            extracted = _combine(
                _section_roster(
                    store, character, kinds, overrides, member_chars, constraints
                ),
                _extracted_roster(
                    store, character, kinds, member_chars, overrides, constraints
                ),
            )
            if owned is not None:
                # Ownership and prose are added, not chosen between.
                #
                # Returning the owner roster whenever it had members hid every
                # extracted row on the two wikis that record ownership well.
                # Frieza's `users` edges give four Golden variants; his
                # `Power and Abilities` subpage names the first, second, third
                # and final forms, 100% Full Power and Mecha Frieza. Both are
                # his, and only the union is the answer.
                #
                # Ownership leads, because the wiki recorded it and a model
                # read the other, and it keeps its own confidence.
                merged = _combine(owned, extracted)
                if merged is not None:
                    merged.subject = owned.subject
                    merged.basis = owned.basis
                    merged.kind = owned.kind
                    merged.confidence = owned.confidence
                    merged.rejected = owned.rejected
                    merged.scope = owned.scope
                    return merged
                return owned
            if extracted is not None:
                return extracted

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
                    store, episodes, names[:max_members], declared.group_by,
                    member_chars,
                    # Only for a hand-written `members:` list. A category read
                    # that returns a name the store knows nothing about is a
                    # stale index, not an answer.
                    keep_bare=bool(declared.members),
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
                elif _narrowed_by_a_name(store, constraints, overrides):
                    # `Transformations` is declared; "Frieza's transformations"
                    # is not. What came back is the declared set narrowed by
                    # whether his name appears on the page, which is a weaker
                    # thing than the wiki saying these are his — and it came
                    # back holding two of his eight canon forms while wearing
                    # the same badge as a set that was actually checked.
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
            works=constraints.works,
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

        # A curated category is precise and incomplete. `Sukuna Techniques`
        # holds eight pages; his own `Abilities and Powers` names Dismantle,
        # Cleave, Divine Flame, Kamutoke and Hiten as well, and none of those
        # has a page to be filed under. The category wins the *shape* of the
        # answer — it decided the basis and the confidence — and the prose adds
        # what the wiki never gave a page to.
        if character and kinds:
            extra = _extracted_roster(
                store, character, kinds, member_chars, overrides, discovered
            )
            if extra is not None:
                seen = {member.name.strip().lower() for member in members}
                members += [
                    member for member in extra.members
                    if member.name.strip().lower() not in seen
                ][:max_members - len(members)]

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


# ── a character's own kit ────────────────────────────────────────────────────
#
# A category is filed by kind, never by owner. `Transformations` holds every
# transformation in Dragon Ball, so "Every form of Goku" answered with all of
# them narrowed by whether the string "goku" appeared anywhere on the page —
# which kept `Super Saiyan Rosé`, whose users field reads "Goku Black".
#
# The wiki does record ownership, as `users`/`wielder` edges, and inverting them
# gives the character's kit directly: 240 pages for Goku, typed by the same
# vocabulary as everything else — 194 techniques, 28 transformations, 15
# power-ups, 3 fusions, nothing unclassified. Starting there rather than
# filtering a category also lifts a cap nobody could see: a category read is
# limited to 400 pages, and Goku's techniques do not all sort into the first
# 400, which is why `Kamehameha` was missing from his own technique list.
#
# Not every wiki records it. Hunterpedia and the Chainsaw Man wiki have no user
# fields at all; One-Punch Man points Saitama at ten battles and one item. Where
# ownership yields nothing of the kind asked, this returns None and the ordinary
# path runs unchanged.

_KIND_WORDS: dict[str, frozenset[str]] = {
    ontology.TRANSFORMATION: frozenset({
        "form", "forms", "transformation", "transformations",
        "gear", "gears", "state", "states", "mode", "modes",
    }),
    ontology.TECHNIQUE: frozenset({
        "technique", "techniques", "ability", "abilities", "attack", "attacks",
        "move", "moves", "skill", "skills", "power", "powers",
        # A named fighting style is a technique on every wiki that keeps one.
        # Without it "Every sword style of Zoro" never became a question about
        # Zoro at all, and his four styles sat in the table unreturned.
        "style", "styles",
    }),
    ontology.ITEM: frozenset({
        "armor", "armour", "weapon", "weapons", "sword", "swords",
        "item", "items", "equipment",
    }),
}


def ability_kind_words(overrides: dict | None) -> dict[str, frozenset[str]]:
    """`_KIND_WORDS` plus whatever this wiki calls its own kinds of ability.

    The vocabulary above is English, and these wikis are not. Jujutsu Kaisen
    keeps `shikigami`, Chainsaw Man keeps `contract`, and a question using the
    word the series itself uses was falling out of the character path before
    it started — "Every shikigami of Megumi Fushiguro" returned none of the
    nine that were sitting in the `abilities` table.

    Declared per series so no wiki's vocabulary reaches another's:

        ability_kinds:
          technique: [shikigami]
    """
    declared = (overrides or {}).get("ability_kinds") or {}
    merged: dict[str, frozenset[str]] = {}
    for kind, vocab in _KIND_WORDS.items():
        extra = {
            str(word).strip().lower()
            for word in (declared.get(kind) or [])
            if str(word).strip()
        }
        merged[kind] = vocab | extra
    return merged


def _narrowed_by_a_name(
    store: FactStore, constraints: Constraints, overrides: dict
) -> bool:
    """True when a qualifier is a person, so the filtering was done by name.

    Kept separate from `_character_subject`, which refuses race words: this has
    to fire precisely where that one declines, because `Frieza` is both a
    character and the name of a race, and the answer is being narrowed by his
    name either way.
    """
    for word in constraints.qualifier:
        node = store.node_by_name(word)
        if node is None:
            continue
        if ontology.semantic_type(store, node["name"], overrides) == ontology.CHARACTER:
            return True
    return False


def _character_subject(
    store: FactStore,
    words: Sequence[str],
    overrides: dict,
    race_words: set[str],
    vocabulary: set[str],
) -> str:
    """Which character a topic about abilities is about, if any.

    The ordinary subject ranking is not usable here. It answered "Luffy" with
    `Yamamoto Luffy`, "Zoro" with `Manjaro` and "Killua" with `Nen`, and its
    character test reads the raw infobox id — so One Piece's `char_box` and
    One-Punch Man's `parent_tab` are not characters as far as it is concerned,
    though `semantics` maps the first of those to one.

    So the leftover words are resolved directly: whatever is left of the topic
    once the kind it asked for and this series' own set vocabulary are removed
    is the name, and the largest page carrying that name is the character.

    A race word can never be the character — otherwise "Every Saiyan
    transformation" would become a question about the Saiyan article — and
    neither can a word this series declares a set by.
    """
    kind_words = {word for vocab in ability_kind_words(overrides).values() for word in vocab}
    found = _subject_from(
        store, words, overrides, race_words, vocabulary, kind_words
    )
    if found:
        return found
    # Nothing was left over once the kind words were removed — which happens
    # when the character *is* one. Chainsaw Man has a character called Power,
    # so "Every ability of Power" had both its words struck out and never
    # reached the character path, returning nothing at all while six of her
    # abilities sat in the table.
    #
    # Only as a fallback, and only for an outright character: a kind word is
    # far more often the kind than a name, and this must not let "Every power
    # of X" become a question about her.
    found = _subject_from(
        store, [word for word in words if word in kind_words],
        overrides, race_words, vocabulary, set(), strict_character=True,
    )
    if found:
        return found
    # Last: a race named after the person it descends from. `Frieza` is both a
    # character and a race here, and the rule that correctly keeps "Every
    # Saiyan transformation" a question about Saiyans also stopped "Every
    # transformation of Frieza" being one about him — his First, Second,
    # Third, Final and 100% Full Power forms sit in the `abilities` table and
    # were unreachable, the question answering with four Golden variants.
    #
    # `Saiyan` and `Namekian` are unaffected because this pass takes only an
    # outright `character` page, and a race article is not one. The guard that
    # matters is the topic naming a race itself: "Every Frieza Race
    # transformation" means the race, and `gold_db` asserts exactly that.
    if any(word in _RACE_MARKERS for word in words):
        return ""
    return _subject_from(
        store, [word for word in words if word in race_words],
        overrides, set(), vocabulary, set(), strict_character=True,
    )


def _subject_from(
    store: FactStore,
    words: Sequence[str],
    overrides: dict,
    race_words: set[str],
    vocabulary: set[str],
    kind_words: set[str],
    strict_character: bool = False,
) -> str:
    for word in words:
        # A race word is never the subject, even when the race is named after a
        # person. `frieza` is in the race vocabulary through `Frieza's race`,
        # and letting his own page win it was measured twice worse: "Every
        # transformation of Frieza" went from two canon forms to one, losing
        # Golden and Black Frieza to gain `100% Full Power`, and "Every Frieza
        # Race transformation" stopped being a question about the race at all.
        if word in kind_words or word in race_words:
            continue
        # A set word is not a subject — except on the strict pass, where only
        # an outright `character` page is accepted anyway and that is the same
        # guarantee by a stronger test. `power` is both a set word and the
        # name of a Chainsaw Man character.
        if word in _SET_WORDS and not strict_character:
            continue
        # A word this series declares a set by may still be a character:
        # Dragon Ball declares `Frieza Race transformation`, which made "Every
        # transformation of Frieza" a question about a race rather than about
        # him. Such a word has to type as a character outright — `Espada` is an
        # organisation and `Captain` is nothing in particular, and neither may
        # become the subject on the strength of a large page.
        strict = (word in vocabulary) or strict_character
        for row in store.pages_named(word):
            root = row["root"]
            if not root or not store.node_by_name(root):
                continue
            semantic = ontology.semantic_type(store, root, overrides)
            if semantic == ontology.CHARACTER:
                return root
            # `unknown` is allowed through because a wiki may type its
            # character pages with something this vocabulary has never seen —
            # One-Punch Man files Saitama as `parent_tab`. Never for a declared
            # set word, where only an outright character will do.
            if semantic == ontology.UNKNOWN and not strict:
                return root
            break
    return ""


def _asked_kinds(words: Sequence[str], overrides: dict | None = None) -> set[str]:
    """Which kinds of thing the topic's nouns name.

    `power_up` is deliberately not what "form" means. Goku owns fifteen —
    Meditation, Pump Up, Howl, Hi-Tension — and one, Kaio-ken, that sources do
    list among his forms. Admitting the type to gain that one costs the other
    fourteen, so it stays out and Kaio-ken is a known, deliberate miss.
    """
    asked = {word.lower() for word in words}
    vocabulary = ability_kind_words(overrides)
    return {kind for kind, vocab in vocabulary.items() if asked & vocab}


# "Ability" names the family, not one of its members. `_KIND_WORDS` maps it to
# `technique` alone, so "Every ability of Rukia Kuchiki" could not return
# `Sode no Shirayuki` or `Hakka no Togame` -- both stored, both hers, both filed
# `transformation`. Which of the two an ability gets depends on whether an editor
# filled in a `Class` field, and `semantics.ABILITY_TYPES` exists to say those
# labels "must never be used to reject each other". The kind filter was doing
# exactly that whenever the question used the umbrella word.
#
# Applied to the query's own nouns and nowhere else. `_asked_kinds` is also run
# over section headings (`_section_roster`), where a group called "Abilities and
# Powers" widening to include `transformation` would let containers through on
# *form* questions -- a precision loss on a different path entirely.
#
# `item` is pointedly not admitted, and `ABILITY_TYPES` excludes it for the same
# reason: a zanpakutō, a rapier and a slingshot are equipment. Measured over the
# 28 closed questions that use an umbrella word, admitting items costs 35 wrong
# names to gain 18 right ones, while admitting transformations alone gains 13
# for 11 -- recall 72.7% -> 78.0% with precision flat at 59.3% -> 59.0%.
_UMBRELLA_WORDS = frozenset({"ability", "abilities", "power", "powers"})


def widen_umbrella(words: Sequence[str], kinds: set[str]) -> set[str]:
    """Admit transformations when the topic asked for abilities in general."""
    if not kinds & {ontology.TECHNIQUE}:
        return kinds
    if not {word.lower() for word in words} & _UMBRELLA_WORDS:
        return kinds
    return kinds | {ontology.TRANSFORMATION}


def _files_by_character(
    store: FactStore, character: str, kinds: set[str], overrides: dict | None = None
) -> bool:
    """True when the wiki keeps this character's abilities under their own name.

    `Sukuna Techniques` and `Yuji Itadori Battles` both name a character and
    only the first is a set of abilities, so the rest of the category name has
    to match the kind asked. Where such a category exists it beats ownership:
    an editor curated it, every member belongs to the character by
    construction, and it does not carry the game-only entries a users field
    accumulates.
    """
    own = set(content_words(character))
    for row in store.connection.execute(
        "SELECT DISTINCT category FROM categories WHERE category LIKE ? COLLATE NOCASE",
        (f"%{character}%",),
    ):
        rest = set(content_words(row["category"])) - own
        vocabulary = ability_kind_words(overrides)
        if any(rest & vocabulary[kind] for kind in kinds):
            return True
    return False


def _owned_roster(
    store: FactStore,
    episodes: cite.EpisodeIndex,
    character: str,
    kinds: set[str],
    constraints: Constraints,
    overrides: dict,
    max_members: int,
    member_chars: int,
) -> Roster | None:
    """The pages this character owns, of the kind the topic asked for."""
    owned = store.owned_by(character, _BELONGS_RELATIONS)
    if not owned:
        return None
    types = {name: ontology.semantic_type(store, name, overrides) for name in owned}
    names = sorted(name for name in owned if types[name] in kinds)
    names = drop_stopwords(names, overrides)
    if not names:
        return None

    candidates = len(names)
    # The character's own name cannot also be a constraint on their kit: every
    # one of these pages names them, which is how they were found.
    own = set(content_words(character))
    scoped = Constraints(
        qualifier=tuple(word for word in constraints.qualifier if word not in own),
        scope=constraints.scope,
        canon=constraints.canon,
        works=constraints.works,
    )
    names, rejected = apply_constraints(
        store, names, scoped, character, overrides=overrides
    )
    members = _render_all(store, episodes, names[:max_members], "", member_chars)
    if not members:
        return None
    label = ", ".join(sorted(kinds))
    # Ownership this thin is not the wiki's record of a character's kit, it is
    # an accident of which page an editor happened to fill in. Ichigo has one
    # user edge in a wiki holding 115 Zanpakutō techniques, and answering his
    # techniques with that one page while reporting `exact` is the failure this
    # whole pass exists to remove. Goku has 28 transformations and Guts 5.
    confidence = "exact" if len(members) >= 3 else "partial"
    return Roster(
        subject=character,
        basis=f"{character}'s {label}",
        kind="owner",
        members=members,
        confidence=confidence,
        candidates=candidates,
        rejected=rejected,
        scope=constraints.scope,
        capped=len(names) if len(names) > max_members else 0,
    )


def ability_stopwords(overrides: dict | None) -> frozenset[str]:
    """Words that name a series' power system rather than anyone's ability."""
    declared = (overrides or {}).get("ability_stopwords") or []
    return frozenset(
        str(word).strip().lower() for word in declared if str(word).strip()
    )


def drop_stopwords(names: Sequence[str], overrides: dict | None) -> list[str]:
    """Remove declared non-abilities from a list of member names.

    `ability_stopwords` used to be consulted on the prose path alone
    (`_extracted_roster`), so the same name could be declared "not anyone's
    ability" and still come back as a heading or an ownership edge. It did:
    `Physical Abilities` and `Other Abilities` arrived as headings, and Dragon
    Ball's game-only fusions -- `Vegecell`, `Celluza`, `EX Gogeta` -- arrived
    both ways. 65 members of one run, and not one of them a canon item on any
    question.

    Deliberately not applied to a declared roster. `rosters: … members:` is
    someone stating the answer outright, and a stopword must not overrule it.
    """
    stop = ability_stopwords(overrides)
    if not stop:
        return list(names)
    return [name for name in names if name.strip().lower() not in stop]


# How many off-kind extracted rows still read as the model wavering between
# `technique` and `transformation` rather than separating them. Measured: the
# ratio is 0.19 where folding the two helps (Killua) and 0.52 to 0.84 where it
# only adds noise (Vegeta, Sukuna, Goku).
_KIND_NOISE = 1 / 3


# Read once per store: the list does not change while a server is running,
# and `index` is a separate process.
_DROPPED_TITLES: dict[str, frozenset[str]] = {}


def _dropped_titles(store: FactStore) -> frozenset[str]:
    """The pages `index` removed as belonging only to a discounted work.

    Written by the indexer, because that is the only moment that can tell.
    Afterwards the page has no debut left to judge, and "no page" is exactly
    the shape prose extraction exists to keep.
    """
    key = str(store.path)
    cached = _DROPPED_TITLES.get(key)
    if cached is None:
        try:
            raw = store.get_meta("dropped_titles") or "[]"
            cached = frozenset(
                str(title).strip().lower() for title in json.loads(raw)
            )
        except (TypeError, ValueError):
            cached = frozenset()
        _DROPPED_TITLES[key] = cached
    return cached


def _outside_the_story(
    store: FactStore, name: str, constraints: Constraints
) -> bool:
    """Whether a named ability debuts only in works this series discounts.

    A name the wiki never gave a page is kept. It has no debut to judge, and
    dropping what cannot be checked would remove exactly what prose extraction
    exists to find — `Dismantle` and `Cleave` have no page on the Jujutsu
    Kaisen wiki.
    """
    if name.strip().lower() in _dropped_titles(store):
        return True
    if not store.node_by_name(name):
        return False
    profile = _profile(store, name)
    if profile.media and not (set(profile.media) & set(constraints.canon)):
        return True
    return _game_only(store, profile, constraints.works)


def _extracted_roster(
    store: FactStore,
    character: str,
    kinds: set[str],
    member_chars: int,
    overrides: dict | None = None,
    constraints: Constraints | None = None,
) -> Roster | None:
    """A character's kit as read out of prose at index time.

    The last resort, and the only one that reaches half of what these questions
    ask for. Killua's Godspeed has no page, no category and no user field — it
    is a proper noun in a paragraph, and `cli abilities` is what turns it into
    a row. Nothing is computed here: this is a keyed read of what that run
    stored, so the same question answers the same way twice.

    Capped at `partial` unconditionally. A model read these out of prose, and
    however good the reading was it is not the wiki having filed something.
    """
    # A technique and a transformation are one bucket here — but only when the
    # off-kind rows look like the model wavering rather than a distinction it
    # actually drew.
    #
    # On a page the wiki types the thing itself and the type can be trusted. On
    # an extracted row the kind is the model's guess between three words, and
    # the guess moves: `Whirlwind` and `Speed of Lightning` came back as
    # transformations, so "Every Nen ability of Killua" — which asks for
    # techniques — filtered out two of the four right answers.
    #
    # Folding them unconditionally is much worse elsewhere. Measured against
    # the canon lists, asked-kind only versus folded:
    #
    #   Killua's Nen abilities   16 rows 2 of 5  ->  19 rows 4 of 5   +2 canon
    #   Sukuna's techniques      16 rows 7 of 8  ->  26 rows 7 of 8   +0 canon
    #   Vegeta's forms           31 rows 11 of 12 -> 47 rows 11 of 12 +0 canon
    #   Goku's forms             31 rows 10 of 12 -> 57 rows 11 of 12 +1 canon
    #
    # The fold buys two canon items on Killua and one across the other three,
    # for fifty-two extra members — Kamehameha and Dragon Fist answering a
    # question about *forms*. What separates them is proportion: Killua's
    # off-kind rows are three against sixteen, Goku's twenty-six against
    # thirty-one. A handful is noise; a comparable pile is a real distinction.
    asked = set(kinds)
    rows = store.abilities_of(character, sorted(asked))
    if asked & {ontology.TECHNIQUE, ontology.TRANSFORMATION}:
        folded = {ontology.TECHNIQUE, ontology.TRANSFORMATION} - asked
        off = store.abilities_of(character, sorted(folded)) if folded else []
        # No asked-kind rows at all means the kind field is telling us nothing
        # about this character, so take what there is rather than nothing.
        if off and (not rows or len(off) <= len(rows) * _KIND_NOISE):
            rows = list(rows) + list(off)
    if not rows:
        return None
    # Ten and Ren are how Nen works, not what Killua can do. The same list now
    # gates the heading and ownership paths too (`drop_stopwords`), so a name
    # declared here cannot come back by another route.
    stopwords = ability_stopwords(overrides)
    if stopwords:
        rows = [row for row in rows if row["name"].strip().lower() not in stopwords]
        if not rows:
            return None

    # Extracted rows deliberately skip `validate_member`, whose decisive test
    # asks whether a page's own fields name this character as a user — and the
    # reason these rows exist is that no page does. Measured on the stored
    # table: running them through it drops Sukuna's `Dismantle`, `Cleave` and
    # `Shrine` and Goku's `Super Saiyan Blue Kaio-ken` and `Ultra Instinct`,
    # every one of them for "no field on this page names X as a user". The row
    # came from that character's own page, so ownership is not in question.
    #
    # Canon is a different question — what work a thing debuted in, not who
    # used it — and it still applies. Without it, reading Goku's prose puts
    # `Super Saiyan (Berserk)` and `Blue Berserk` back among his forms, which
    # is the filter the category path had already got right.
    if constraints is not None and constraints.scope == "canon":
        rows = [
            row for row in rows
            if not _outside_the_story(store, row["name"], constraints)
        ]
        if not rows:
            return None
    members = _named_not_described([
        Member(
            name=row["name"],
            group=(row["section"] or "").split("/")[-1].strip(),
            text=(row["reason"] or "")[:member_chars],
        )
        for row in rows
    ])
    # Deliberately *not* filtered for template headings. `Bankai` heads a
    # section on most Bleach captain pages and is also one of Ichigo's forms;
    # dropping it from prose cost a real canon item to remove a duplicate. A
    # repeated heading is a container, but the same word named in a sentence is
    # the model asserting it, which is a different claim.
    if not members:
        return None
    return Roster(
        subject=character,
        basis=f"{character}, from prose",
        kind="extracted",
        members=members[:MAX_MEMBERS],
        confidence="partial",
        candidates=len(rows),
    )


# A heading this many character pages share is the wiki's article skeleton, not
# one character's ability. Measured: the ability headings sit at one to four
# pages (`Gear 5 (Awakening)` 1, `Gear 2` 2, `Nine Sword Style` 3,
# `Berserker Armor` 4) and the skeleton at forty-four and up (`Hero Rating` 44,
# `Zanpakutō` 210, `Physical Abilities` 216, `Nen` 258). Ten sits in the gap.
_TEMPLATE_HEADING_PAGES = 10

# Longest real ability name measured is four words — `Killer Move: Serious
# Series`, `Santoryu Ogi: Sanzen Sekai`, `Super Saiyan Blue Kaio-ken`. What runs
# longer is the model describing rather than naming: "Sleeping with a larger
# part of his brain awake" survived the proper-noun filter because a sentence
# also starts with a capital.
_MAX_ABILITY_WORDS = 5


def _drop_templates(store: FactStore, members: list[Member]) -> list[Member]:
    """Remove the members that are the wiki's own article skeleton."""
    if not members:
        return members
    counts = store.pages_per_section([member.name for member in members])
    return [
        member
        for member in members
        if counts.get(member.name.strip().lower(), 0) <= _TEMPLATE_HEADING_PAGES
    ]


def _named_not_described(members: list[Member]) -> list[Member]:
    """Remove the members that are a description rather than a name."""
    return [
        member
        for member in members
        if len(member.name.split()) <= _MAX_ABILITY_WORDS
    ]


def _combine(first: Roster | None, second: Roster | None) -> Roster | None:
    """Union two readings of the same character's page.

    Headings and prose answer the same question from the same page and neither
    contains the other. The headings on Luffy's abilities page are `Gear 2`,
    `Gear 3`, `Gear 4` and `Gear 5 (Awakening)`; the prose under them names
    `Boundman`, `Tankman` and `Snakeman`. Whichever was preferred, choosing lost
    half the Gears — so both are kept.

    Confidence stays `partial`, which is what both inputs already claim.
    """
    if first is None:
        return second
    if second is None:
        return first
    members = list(first.members)
    seen = {member.name.strip().lower() for member in members}
    for member in second.members:
        key = member.name.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        members.append(member)
    return Roster(
        subject=first.subject,
        basis=f"{first.subject}, by section and prose",
        kind="section+extracted",
        members=members[:MAX_MEMBERS],
        confidence="partial",
        candidates=first.candidates + second.candidates,
    )


def _section_roster(
    store: FactStore,
    character: str,
    kinds: set[str],
    overrides: dict,
    member_chars: int,
    constraints: Constraints | None = None,
) -> Roster | None:
    """A character's kit where the wiki wrote it as headings rather than pages.

    Four of these eight wikis give abilities no page of their own. Luffy's Gears
    are `Devil Fruit / Gear 2` on `Monkey D. Luffy/Abilities and Powers`, and
    Denji's forms are headings under `Appearance`. Nothing in the categories can
    reach them, which is why "Every form of Luffy" answered with forty *people*.

    Which headings hold abilities is series knowledge and lives in
    `overrides.yaml`, keyed by the kind asked, exactly as category names do.

    The confidence is capped at `partial` on purpose. A heading is where an
    ability is described, not an entity the wiki curated, so `Zanpakutō` and
    `Fighting Style` come back beside real ones — worth returning, never worth
    claiming as an exact set.
    """
    wanted = [
        str(section).strip().lower()
        for kind in kinds
        for section in ((overrides or {}).get("ability_sections") or {}).get(kind, [])
        if str(section).strip()
    ]
    if not wanted:
        return None

    members: list[Member] = []
    seen: set[str] = set()
    rows = list(store.sections_of(character))

    # A heading that other headings sit under *and* is named only for the kind
    # of thing it holds is a container, not a member. Once item markers are
    # structural, `Abilities`, `Techniques`, `Forms and Transformations` and
    # `Equipment` are headings in their own right and were all coming back as
    # Goku's forms.
    #
    # Being a parent is not enough on its own: `Black Leg Style` has
    # `Diable Jambe` under it and is still one of Sanji's techniques, and
    # `Three Sword Style` is one of Zoro's styles. What separates them is that
    # every word of a group label is a kind word and `black`/`leg` are not.
    vocabulary = {word for words in ability_kind_words(overrides).values() for word in words}
    crumbs_seen = {(row["breadcrumb"] or "").strip() for row in rows}
    parents = {
        crumb.rsplit("/", 1)[0].strip()
        for crumb in crumbs_seen
        if "/" in crumb
    }
    parents = {
        crumb
        for crumb in parents
        if (lambda name: name and all(word in vocabulary for word in name))(
            content_words(crumb.rsplit("/", 1)[-1])
        )
    }

    for row in rows:
        breadcrumb = (row["breadcrumb"] or "").strip()
        crumbs = [part.strip() for part in breadcrumb.split("/")]
        if len(crumbs) < 2:
            continue
        # The level-0 card carries the page title as its breadcrumb, which on
        # a subpage splits into two and reads as a heading — `Goku/Power and
        # Abilities` was returning a member called `Power and Abilities`.
        if breadcrumb == (row["title"] or "").strip():
            continue
        if breadcrumb in parents:
            continue
        # The heading the topic asked about can be the top of the path or the
        # subpage the wiki moved it onto — Zoro's abilities are a whole page.
        head = " ".join((crumbs[0], row["title"] or "")).lower()
        if not any(section in head for section in wanted):
            continue
        name = crumbs[-1]
        if not name or name.lower() in seen:
            continue
        # The wiki says what kind of thing the list holds, so believe it.
        # `Goku/Power and Abilities` groups its items under
        # `'''<big>Forms and Transformations</big>'''`, `Techniques`,
        # `Fusions` and `Equipment`; without reading that, "Every form of
        # Goku" answered with `Kamehameha` and `Attack Ball` as well.
        #
        # Only when the group names a kind at all — `Fusions` names none, and
        # a group this vocabulary has never seen is not evidence against its
        # members.
        group = crumbs[-2] if len(crumbs) > 2 else ""
        if group and kinds:
            stated = _asked_kinds(content_words(group), overrides)
            if stated and not (stated & kinds):
                continue
        # A heading is not exempt from canon. Reading `;`-marked forms out of
        # `Goku/Power and Abilities` put `Super Saiyan (Berserk)` back among
        # his forms — the page for it was dropped, but the heading naming it
        # sits on a page that stays.
        if constraints is not None and constraints.scope == "canon":
            if _outside_the_story(store, name, constraints):
                continue
        seen.add(name.lower())
        members.append(
            Member(name=name, group=group,
                   text=(row["text"] or "").strip()[:member_chars])
        )
    # `Physical Abilities` and `Nen` are headings on hundreds of character
    # pages. They are where an ability is described, never one themselves.
    members = _drop_templates(store, members)
    # And the ones this series has already declared are not abilities at all.
    # A heading is no more entitled to return `Other Abilities` or `Vegecell`
    # than a prose row is.
    stop = ability_stopwords(overrides)
    if stop:
        members = [m for m in members if m.name.strip().lower() not in stop]
    if not members:
        return None
    return Roster(
        subject=character,
        basis=f"{character}, by section",
        kind="section",
        members=members[:MAX_MEMBERS],
        confidence="partial",
        candidates=len(members),
    )


def _mentioned_anywhere(store: FactStore, name: str) -> bool:
    """Whether this wiki's prose names it at all, article or not.

    Only ever used to tell a member the wiki never gave a page from a member
    someone mistyped. Deliberately not a membership test -- being mentioned
    somewhere proves nothing about whose ability a thing is, and nothing here
    treats it as though it did.
    """
    if not name.strip():
        return False
    try:
        row = store.connection.execute(
            "SELECT 1 FROM chunks WHERE text LIKE ? COLLATE NOCASE LIMIT 1",
            (f"%{name}%",),
        ).fetchone()
    except sqlite3.Error:  # a store built before chunks existed
        return False
    return row is not None


def _declared_members(store: FactStore, declared: RosterDefinition) -> list[str]:
    """The pages behind a declared set, however the wiki holds them."""
    if declared.members:
        # A page is not the only proof a member is real. Requiring one deleted
        # answers the wiki states plainly: the Four Kings of the World are four
        # plain-text entries in a `notable members` field, six of the Band of the
        # Falcon are sections of `Minor Characters`, and Himeno's `Ghost Devil
        # Contract` is a bolded line on her own page. None has an article and all
        # eleven scored 0.
        #
        # The check the article test was really making is "did someone mistype
        # this", and mentioned-anywhere answers that without discarding the
        # pageless: a real member is named somewhere on the wiki, a typo is
        # named nowhere. Kept in declaration order, since a hand-written list is
        # usually written in a deliberate one.
        return [
            name for name in declared.members
            if store.node_by_name(name) or _mentioned_anywhere(store, name)
        ]
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
    keep_bare: bool = False,
) -> list[Member]:
    """Render each name, dropping the ones the store can say nothing about.

    `keep_bare` is for a roster whose members were declared by hand. A member
    the wiki never gave an article has no text and no facts, so the filter below
    removes it -- correct when the name came from a category read and wrong when
    someone wrote it down deliberately. A bare name is still the answer to
    "every member of the Four Kings of the World"; an empty roster is not.
    """
    members = [
        _render_member(store, episodes, name, group_by, member_chars)
        for name in names
    ]
    if not keep_bare:
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
    # Works this series keeps but does not count as its story. Empty for every
    # wiki that declares none, which is all of them but Dragon Ball.
    works: tuple[str, ...] = ()
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
    works = non_canon_works(overrides)
    # Naming the work asks for it back. Without this the exclusion is a
    # deletion: "Every Super Dragon Ball Heroes transformation" would answer
    # with the forms that are not from it.
    #
    # The wiki's own name is stripped off as an alternative, because nobody
    # asks for "Dragon Ball Xenoverse forms" — they ask for Xenoverse.
    lowered = (query or "").lower()
    if any(name and name in lowered for name in _work_aliases(works, title)):
        scope = "all"
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
        qualifier=qualifier,
        scope=scope,
        canon=frozenset(canon_media(overrides)),
        works=works,
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
    # The works the debut edges point at, by name. The medium is already read
    # off these; the names were being thrown away, and they are the only thing
    # that separates a Super Dragon Ball Heroes manga chapter from a Dragon Ball
    # Super one — both of which say "manga".
    works: tuple[str, ...] = ()

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
    works: list[str] = []
    for target in store.linked_from(name, ("debut", "manga debut", "anime debut", "first appearance")):
        works.append(target)
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
        works=tuple(dict.fromkeys(works)),
    )


def _work_aliases(works: Sequence[str], title: str) -> set[str]:
    """How a question is likely to name a work, as well as its full title.

    Every Dragon Ball game is called `Dragon Ball <something>`, and a question
    asks for "Xenoverse" or "Dokkan", never "Dragon Ball Xenoverse forms". The
    wiki's own name is the only thing stripped, so `Dark Demon Realm` and
    `Super Dragon Ball Heroes` keep theirs.
    """
    aliases: set[str] = set()
    prefix = (title or "").strip().lower()
    for work in works:
        aliases.add(work)
        if not (prefix and work.startswith(prefix)):
            continue
        rest = work[len(prefix):].strip(" :-")
        # And the sub-series marker after it, so `Dragon Ball Z: Dokkan Battle`
        # reaches the "Dokkan Battle" a question actually says.
        for marker in ("z", "gt", "super", "daima"):
            if rest.startswith(f"{marker}:") or rest.startswith(f"{marker} "):
                rest = rest[len(marker):].strip(" :-")
                break
        # `Dragon Ball Heroes` minus `Dragon Ball` is `Heroes`, which is too
        # common a word to flip the scope on its own.
        if len(rest) > 5:
            aliases.add(rest)
    return aliases


def non_canon_works(overrides: dict | None) -> tuple[str, ...]:
    """Works this series keeps but does not count as its story."""
    declared = (overrides or {}).get("non_canon_works") or []
    return tuple(
        str(work).strip().lower() for work in declared if str(work).strip()
    )


def _is_non_canon_work(store: FactStore, title: str, works: tuple[str, ...]) -> bool:
    """Whether one debut target belongs to a work the series does not count.

    Matched on the whole title or a title prefix, and on the work's own
    categories. Never as a substring anywhere in the string: `Dr. Hedo` debuts
    in `Super Heroes are Born`, a Dragon Ball Super chapter, and a bare "heroes"
    test threw him out of the Red Ribbon Army along with Gamma 1 and Cell Max.

    The category hop is what reaches `Evil Saiyan (chapter)` — a page whose own
    title says nothing, filed under `Dragon Ball Heroes manga chapters`.
    """
    lowered = (title or "").strip().lower()
    if any(lowered == work or lowered.startswith(work) for work in works):
        return True
    for category in store.categories_of(title):
        folded = category.strip().lower()
        if any(folded == work or folded.startswith(work) for work in works):
            return True
    return False


def _game_only(store: FactStore, profile: Profile, works: tuple[str, ...]) -> bool:
    """True when every work this page debuted in is one the series discounts.

    Every, not any. `Super Saiyan Blue` names `Dragon Ball Heroes` among its
    debuts and first appeared in *Resurrection 'F'*; an any-test would have
    thrown away half of Goku's canon forms to catch the Berserk ones.
    """
    if not works or not profile.works:
        return False
    return all(
        _is_non_canon_work(store, target, works) for target in profile.works
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


def _owned_pages(store: FactStore, word: str) -> frozenset[str]:
    """Pages the wiki records as belonging to the character `word` names.

    Empty for anything that is not a character, and empty for a character this
    wiki records no ownership for at all — Hunterpedia and the Chainsaw Man
    wiki keep no user fields on abilities, so Killua owns nothing here and the
    caller has to fall back rather than reject every candidate.
    """
    node = store.node_by_name(word)
    if node is None or "character" not in (node["label"] or "").lower():
        return frozenset()
    return frozenset(
        name.lower() for name in store.owned_by(node["name"], _BELONGS_RELATIONS)
    )


def validate_member(
    store: FactStore,
    profile: Profile,
    constraints: Constraints,
    set_name: str,
    race_words: set[str] | None = None,
    owned_by_word: dict[str, frozenset[str]] | None = None,
) -> str:
    """``""`` to keep the member, otherwise why it does not belong."""
    race_words = race_words if race_words is not None else set()
    owned_by_word = owned_by_word or {}
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

    # A work the series does not count, even though its manga is a manga and its
    # anime is an anime. Read from the debut edges rather than the debut string,
    # which is the only place the difference is recorded.
    if constraints.scope == "canon" and _game_only(store, profile, constraints.works):
        return f"outside the story ({', '.join(profile.works[:3])})"

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
            # A character qualifier asks *whose* this is, and the wiki recorded
            # that as edges. Matching the name against page text instead kept
            # `Super Saiyan Rosé` among Goku's forms, because its users field
            # reads "Goku Black" and "goku" is a substring of that. An edge to
            # `Goku` and an edge to `Goku Black` are different rows, so the
            # question the topic asked can finally be put to the data.
            #
            # Only when the wiki records ownership for this character at all.
            # Where it records none — Hunterpedia keeps no user fields — this is
            # empty and the old text test still runs, because rejecting every
            # candidate would turn a padded answer into no answer.
            owned = owned_by_word.get(word)
            if owned:
                if profile.name.lower() in owned:
                    continue
                return f"no field on this page names {word} as a user"
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

# Whose a thing is. `inventor` is deliberately absent: King Kai invented the
# Kaio-ken and never used it, so inventing something is not owning it — the
# distinction the race path already depends on.
_BELONGS_RELATIONS = (*_USER_RELATIONS, "owner")

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


# Words that say a topic is about a race rather than about a person. Where one
# appears, a race word keeps the topic even if it also names a character.
_RACE_MARKERS = frozenset({
    "race", "races", "species", "clan", "clans", "tribe", "tribes",
    "bloodline", "bloodlines", "lineage",
})

# How many pages must declare a word as their race before it counts as one.
# The gap is wide enough that the exact value hardly matters: the smallest real
# race measured is 43 pages and the largest accident is 2.
_RACE_DECLARATIONS = 3


def race_vocabulary(store: FactStore) -> set[str]:
    """Every word this wiki uses to name a race, from its own race fields.

    Data-driven so it carries across series without a list: `Saiyan` qualifies
    on Dragon Ball for the same reason `Quincy` would on Bleach and `Mink` on
    One Piece — a character page says so.
    """
    counts: Counter[str] = Counter()
    placeholders = ",".join("?" * len(_RACE_FIELDS))
    rows = store.connection.execute(
        f"SELECT value FROM facts"
        f" WHERE LOWER(label) IN ({placeholders}) OR LOWER(key) IN ({placeholders})",
        (*_RACE_FIELDS, *_RACE_FIELDS),
    ).fetchall()
    for row in rows:
        counts.update(set(content_words(row["value"] or "")))

    # Race fields are free text — "Saiyan (Super Saiyan God)", "1/2 Saiyan-1/2
    # Human-type Earthling", "Frieza Clan (mutant)" — so the words alone include
    # `form`, `formerly` and `american`. A race the wiki takes seriously has an
    # article about it; the rest are punctuation with ambitions.
    #
    # Having an article is not enough on its own, because a *character* named
    # inside one of those parentheticals has one too. `Gohan` entered the race
    # vocabulary through two values reading "1/2 Glind-1/2 Saiyan (Gohan
    # Black)", and a race word can never be the subject — so "Every form of
    # Gohan" stopped being a question about Gohan and answered with one
    # loosely-filtered member of `Transformations`.
    #
    # A real race is declared by many pages and an accident by a couple.
    # Measured on Dragon Ball: saiyan 157, human 148, namekian 80, frieza 44,
    # majin 43 — against gohan 2 and buu 2. Bleach agrees: quincy 47.
    # Scaled, so a wiki with four race facts is not held to a corpus-sized bar
    # — on a small store one page declaring a race is all the evidence there
    # is, and the parenthetical accidents this excludes only appear where
    # there are thousands of values for them to hide in.
    floor = min(_RACE_DECLARATIONS, max(1, len(rows) // 4))
    return {
        word
        for word, count in counts.items()
        if count >= floor and store.node_by_name(word)
    }


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
        works=constraints.works,
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
    # Ownership is resolved once per qualifier word, not once per candidate: a
    # character's pages are one indexed query, and asking it inside the loop
    # would repeat it for all 400 members of a category.
    owned_by_word = {
        word: pages
        for word in constraints.qualifier
        if word not in race_words and (pages := _owned_pages(store, word))
    }

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
            store, _profile(store, name), constraints, set_name, race_words,
            owned_by_word,
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

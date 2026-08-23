"""Which of the three retrieval modes a question needs.

This used to be one ternary, duplicated in the CLI and the API:

    mode = "roster" if looks_like_enumeration(query) else "narrative"

Two things were wrong with it. `qa`, the hybrid BM25 + vector + graph path with
a cross-encoder over the top of it, the most engineered part of the system, was
**unreachable**: no caller asking for `auto` could ever land there. And the
enumeration test is a regex, so `What grade of sorcerer is Aoi Todo?` matched
`grades? of` and came back as a list of Todo's five battles.

Measured before rebuilding, over 168 real queries: the regex and a structural
read disagree on 13, **all of them wh-questions**, and agree on all 154
enumeration topics. So the set-versus-not-set call is sound and stays; what was
missing is any way to tell a fact lookup from a story question once the answer
is "not a set".

A bare wh-word cannot make that distinction either; the same measurement wanted
`How did the Shibuya Incident unfold?` in `qa`, which is wrong. What separates
them is *what the subject is*: an event, battle or arc is a story; a character,
item or technique with an attribute asked of it is a lookup. That is read from
the ontology rather than from another keyword list.

The 2026-08-24 campaign -- "a question must be answerable in any natural
phrasing" -- added two fixes for natural wordings this read as accounts:
`_is_interrogative` accepts a wh-word behind one leading preposition ("In
which arc does X take place?" opened like a statement), and `_FIELD_ASKERS`
names the battle-infobox fields JJK records (arc, place, event, outcome,
date), which rule 6 intersects with the corpus's own fact keys, so a wiki
that records no such field cannot route on the word.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from scriptengine.config import SeriesPaths, load_overrides, subject_ranking
from scriptengine.retrieve import chronology
from scriptengine.retrieve import semantics as sem
from scriptengine.retrieve.roster import (
    asks_for_battle_result,
    asks_for_battles_in,
    battle_result,
    battle_result_fighter,
    battles_in,
    build_roster,
    content_words,
    looks_like_enumeration,
)
from scriptengine.stores.facts import FactStore, rank_subjects

MODES = ("roster", "qa", "narrative")

_WH = re.compile(
    r"^\s*\W*(what|whats|what's|who|whom|whos|who's|which|when|where|why|how)\b",
    re.I,
)

# A wh-word behind one leading preposition still opens the question: "In
# which arc does X take place?" and "After which saga did X happen?" are
# the natural way to ask for a battle's infobox field, and the position-0
# test read them as statements, so the question fell to narrative -- the
# one path that strips exactly those fields. One preposition, not a free
# walk: "in order to" and "after the war" stay statements.
_LEADING_PREPS = frozenset({
    "in", "on", "during", "after", "before", "at", "by", "for", "to",
    "with", "within", "over", "under", "from", "since", "until", "upon",
    "off", "across", "through", "around", "about", "between", "amid",
})


def _is_interrogative(query: str) -> bool:
    """Whether the question opens with a wh-word, directly or behind a preposition."""
    q = (query or "").strip()
    if _WH.match(q):
        return True
    parts = q.split()
    if len(parts) >= 2 and parts[0].lower() in _LEADING_PREPS:
        return bool(_WH.match(" ".join(parts[1:])))
    return False

# "How many X are there" opens with a wh-word and still wants the set.
_COUNT = re.compile(r"\bhow many\b", re.I)

# A wh-question whose verb is plural is asking for a list, however it is worded.
# "Who are the members of the Phantom Troupe" and "What are Sukuna's cursed
# techniques" are the same request as "Every member of the Phantom Troupe" and
# "Every cursed technique of Sukuna", and the engine answered the first of each
# pair with nothing at all: rule 3 below claims every interrogative for `qa`
# before the enumeration test is reached.
#
# That went unseen because all 103 set questions in the bank opened with
# "Every". Asked both ways, the same six sets returned 0 members as a question
# and 11 to 23 as a statement.
#
# The number is the whole discriminator, which is what keeps this from undoing
# the rule it sits in front of: "what grade of sorcerer **is** Yuji" stays a
# lookup, and "who **are** the Zodiacs" does not.
_PLURAL_WH = re.compile(r"^\s*\W*(who|what|which)\s+(are|were)\b", re.I)

# An interrogative that asks for a fighter's whole fight list: "Who did Mahoraga
# fight?", "What battles was Sukuna in?". The set-shaped forms ("Every Fight X
# Has Ever Been In") already route to roster via the enumeration test; these are
# the question-worded twins, and rule 3 below would claim them for `qa` before
# that test is reached. They want the same list of battles, not a prose lookup.
_BATTLES_IN_WH = re.compile(
    r"\b(who|what|which)\s+(did|does|do|was|were|is|are)?\s*"
    r"([A-Za-z][\w.-]*)?\s*(fight(ed|s)?|battle(d|s)?|duel(ed|s)?)\b",
    re.I,
)

# "Sukuna's Domain Expansion": whoever owns the attribute is the subject.
_POSSESSIVE = re.compile(r"\b([A-Za-z][\w.-]*)['’]s\b")

# Verbs that make a question about events rather than attributes. `unfold` and
# `happen` are the two that a wh-word rule alone got wrong.
_NARRATIVE_VERBS = re.compile(
    r"\b(happen(ed|s)?|unfold(ed|s)?|occur(red|s)?|go down|play out|"
    r"lead up to|end(ed)?|start(ed)?|begin|began)\b",
    re.I,
)

# Subject types that mean the question is about a story, not a thing.
_STORY_TYPES = frozenset({sem.EVENT, sem.MEDIA})

# Words a question uses to name an infobox field, mapped to the fact key it
# means. The directional verbs (`follows`, `precedes`) never appear as keys;
# everything else is the key itself. Only words whose target this corpus
# actually records count (the `_asks_for_field` intersection), which keeps
# the vocabulary on the wiki rather than on this file. `arc` is here
# because JJK's battle pages record it as a field -- "In which arc does X
# take place?" names that field, and the corpus intersection is what keeps
# a wiki that records no `arc` fact from routing on the word.
_FIELD_ASKERS = {
    "romaji": "romaji",
    "kanji": "kanji",
    "japanese": "japanese",
    "name": "name",
    "next": "next",
    "follows": "next",
    "follow": "next",
    "previous": "previous",
    "prev": "previous",
    "precedes": "previous",
    "precede": "previous",
    "preceded": "previous",
    "preceding": "previous",
    "chapter": "chapters",
    "chapters": "chapters",
    "episode": "episodes",
    "episodes": "episodes",
    "anime": "anime",
    "manga": "manga",
    # Battle-infobox fields, added when the campaign's motive became
    # "answerable in any natural phrasing": the campaign's natural wording
    # ("In which arc / Where / When / What was the result") named fields
    # this vocabulary did not, so on a story-type subject rule 6 could not
    # rescue them and narrative -- which strips the fields -- answered.
    "arc": "arc",
    "place": "place",
    "where": "place",
    "event": "event",
    "outcome": "outcome",
    "result": "outcome",
    "results": "outcome",
    "when": "date",
    "volume": "volumes",
}

# Packaging only. Skipped when resolving *what a question is about*, because an
# episode page is never the subject unless it is named, which is how "Who killed
# Ace?" became a question about an episode called `Legendary Hour`. Events are
# deliberately not in here: `Shibuya Incident` really is the subject, and really
# is a story.
_PACKAGING_SUBJECTS = frozenset({sem.MEDIA})


@dataclass
class Route:
    """The chosen mode, and enough of the reasoning to argue with it."""

    mode: str
    why: str
    signals: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"mode": self.mode, "why": self.why, "signals": self.signals}


def route(paths: SeriesPaths, query: str, settings=None) -> Route:
    """Pick roster, qa or narrative for `query`.

    Order matters and is set by what was measured, not by preference: a
    wh-question that names one thing beats the enumeration cue, because
    "what grade of sorcerer is X" contains an enumeration word and is not a set.
    """
    overrides = load_overrides(paths)
    set_shaped = looks_like_enumeration(query)
    interrogative = _is_interrogative(query)
    plural_ask = bool(_PLURAL_WH.match(query or ""))
    counting = bool(_COUNT.search(query or ""))
    story_verb = bool(_NARRATIVE_VERBS.search(query or ""))

    # Only a story verb near the front is asking about events. "What is the
    # strengthened punch that *occurs* when an attack lands" is a description of
    # a thing with a verb buried in a relative clause, and reading that as a
    # narrative question sent Black Flash to the wrong retriever.
    head = " ".join((query or "").split()[:4])
    story_verb = bool(_NARRATIVE_VERBS.search(head))

    subject, subject_type = _subject(paths, query, overrides)
    # A count or a plural question wants a roster only if this wiki resolves a
    # set for it; otherwise it asks for a number in prose ("how many wards did
    # Kenjaku's chain reaction compromise?") and rule 3 answers from text. The
    # probe runs the same resolution build_roster will, so router and retriever
    # cannot disagree about whether the set exists.
    has_set = _resolves_a_set(paths, query, settings) if (counting or plural_ask) else False

    # An interrogative fight-list question ("Who did Mahoraga fight?") wants the
    # same roster as its statement twin, but rule 3 would claim it for `qa` first.
    # Probe only when the phrasing is a wh-question about fighting and a subject
    # resolved; otherwise leave the existing rules to decide.
    battles_in_ask = bool(_BATTLES_IN_WH.search(query or "")) and interrogative
    has_battles = (
        _resolves_battles_in(paths, subject, overrides) if battles_in_ask else False
    )
    # "What is the result of the battle between X and Y?" The win/loss is a
    # `Result` cell in the subject's own battle table, a region the qa top-8
    # never surfaces (it ranks the fighter's page first). Probe like 2b: the
    # roster route is earned only when this wiki actually holds a row naming
    # the fight; otherwise rule 3 answers from prose.
    battle_result_ask = asks_for_battle_result(query) and interrogative
    has_battle_result = (
        _resolves_battle_result(paths, subject, query, overrides)
        if battle_result_ask else False
    )
    signals = {
        "set_shaped": set_shaped,
        "interrogative": interrogative,
        "plural_ask": plural_ask,
        "counting": counting,
        "story_verb": story_verb,
        "battles_in_ask": battles_in_ask,
        "battle_result_ask": battle_result_ask,
        "subject": subject,
        "subject_type": subject_type,
    }

    # 1. Order beats every other reading. "Every arc in order" is set-shaped and
    #    "Timeline of Dragon Ball" opens like a question, so both were being
    #    answered by something that cannot express order at all: the first with
    #    one arc's 84 chapters, the second with eight loose beats.
    if chronology.wants_chronology(query):
        return Route("roster", "asks for the story in order", signals)

    # 2. A count is a set even though it opens like a question -- when this
    #    wiki holds one for it. An undeclared count falls through to rule 3,
    #    which reads the number out of prose instead of listing techniques.
    if counting and has_set:
        return Route("roster", "asks how many, which wants the set", signals)

    # 2b. An interrogative fight-list question wants the roster of battles, not a
    #     prose lookup. "Who did Mahoraga fight?" is the same request as "Every
    #     Fight Mahoraga Has Ever Been In"; rule 3 below would claim it for `qa`
    #     before the enumeration test is reached. Only when this wiki actually
    #     holds a list of that fighter's battles -- otherwise fall through to 3,
    #     which answers from prose when there is no set behind the question.
    if has_battles:
        return Route("roster", f"asks for {subject!r}'s fights, which wants the set", signals)

    # 2c. A fight's result is read off the subject's own battle table, not from
    #     passages. Same probe shape as 2b: the roster route is earned only
    #     when the wiki holds a row naming the fight, otherwise fall through
    #     to 3, which answers from prose.
    if has_battle_result:
        return Route(
            "roster",
            "asks for a fight's result, which the wiki records in its battle table",
            signals,
        )

    # 3. A wh-question about a thing is a lookup; this is the case the regex
    #    got wrong, and it has to win over the enumeration cue. Except when its
    #    verb is plural and the wiki holds the set it asks for, which wants the
    #    list rather than one thing. A plural question with no set behind it is
    #    a lookup too: "who are the current four emperors" reads prose.
    if (interrogative and not (plural_ask and has_set) and not story_verb
            and subject_type not in _STORY_TYPES):
        if subject:
            return Route(
                "qa",
                f"question about {subject!r}, a {subject_type or 'known entity'}",
                signals,
            )
        # No subject resolved. qa is the path that searches rather than walking
        # a page, so an unanchored question belongs there, since narrative has
        # nothing to walk.
        return Route("qa", "a question with no page to walk", signals)

    # 4. Otherwise the enumeration test decides, and on 154 real topics it was
    #    right every time.
    if set_shaped:
        return Route("roster", "asks for a set", signals)

    # 5. A plural question with no enumeration word is still a plural question --
    #    when this wiki holds the set it asks for. "What are Sukuna's named
    #    cursed techniques" carries none of `every`, `all`, `members of` (the
    #    plural noun is the only cue) and without this it falls past every test
    #    above and is answered as an account. A plural question with no set
    #    behind it reaches here only when rule 3 could not anchor a subject, so
    #    it keeps its old reading: an account of whatever the page holds.
    if plural_ask and has_set:
        return Route("roster", "asks in the plural, which wants the list", signals)

    # 6. A wh-question that names an infobox field is a lookup even when its
    #    subject is an event or arc. "What is the romaji of the Cursed Child
    #    Arc?" and "Which arc follows the Fearsome Womb Arc?" want one fact
    #    row, and narrative strips exactly those: `NOISE_FACT_KEYS` drops
    #    romaji, next and previous, and the infobox chunk is not a beat. qa
    #    serves the subject's facts and passages, which is where the answers
    #    live. The field vocabulary is read from the corpus's own fact keys,
    #    so a wiki that records no `romaji` cannot be routed by the word. The
    #    2026-08-24 campaign added the battle-infobox fields (arc, place,
    #    event, outcome, date) to that vocabulary for the same reason: "In
    #    which arc does X take place?" is a question about a battle -- an
    #    event -- and only this rule rescues it from narrative.
    if interrogative and _asks_for_field(paths, query):
        return Route("qa", "asks for a specific infobox field", signals)

    if interrogative and story_verb:
        return Route("narrative", "asks how something happened", signals)
    if subject_type in _STORY_TYPES:
        return Route("narrative", f"{subject!r} is an event rather than a thing", signals)

    # A bare name ("Prison Realm", "Playful Cloud") is a lookup, not a story.
    # Narrative would walk that page top to bottom; qa answers what it is.
    if subject and subject_type and len((query or "").split()) <= 4:
        return Route("qa", f"names {subject!r} and asks nothing of it", signals)

    return Route("narrative", "an account rather than a set or a lookup", signals)


def _asks_for_field(paths: SeriesPaths, query: str) -> bool:
    """Whether `query` names an infobox field this corpus records.

    `content_words` already strips stopwords and possessives, so the field
    word survives any phrasing ("the Cursed Child Arc's romaji" leaves
    `romaji`). A failure must never fail routing, so any error reads as "no
    field" and the question falls through to the narrative rules.
    """
    try:
        with FactStore(paths.facts_db) as store:
            keys = {
                row["key"].lower()
                for row in store.connection.execute("SELECT DISTINCT key FROM facts")
            }
    except Exception:  # noqa: BLE001 - routing must never be the thing that fails
        return False
    wanted = {
        _FIELD_ASKERS[word] for word in content_words(query) if word in _FIELD_ASKERS
    }
    return bool(wanted & keys)


def _resolves_a_set(paths: SeriesPaths, query: str, settings=None) -> bool:
    """Whether this wiki actually holds a set for `query` to enumerate.

    Rules 2 and 5 used to trust the phrasing alone, so "how many wards did
    Kenjaku's chain reaction compromise?" -- a number in prose -- was handed a
    roster of Kenjaku techniques. The probe runs the same resolution
    build_roster will run for real, one member rendered, and asks it how sure
    it is: a declared phrase that claimed the topic (`matched`) or an exact
    discovery is a set; partial and weak are guesses the prose can answer
    better. A failure here must never fail routing, so any error reads as "no
    set" and the question falls through to rule 3.
    """
    try:
        roster = build_roster(paths, query, settings, max_members=1, member_chars=0)
    except Exception:
        return False
    if roster.matched:
        return True
    return roster.confidence in ("exact", "declared")


def _resolves_battles_in(paths: SeriesPaths, fighter: str, overrides: dict | None) -> bool:
    """Whether `fighter` is on at least one battle page this wiki holds.

    The interrogative twin of the set-shaped battles-in test. Rule 3 claims every
    wh-question for `qa`, so "Who did Mahoraga fight?" never reaches the roster
    path that answers it; this probe runs the same resolution `build_roster` will,
    and only then does the question earn a roster route. A fighter on no battle
    page returns False and falls through to rule 3, which is where "Who did X
    fight?" belongs when there is no list of fights behind it. A failure must
    never fail routing, so any error reads as "no battles".
    """
    if not fighter:
        return False
    try:
        from scriptengine.retrieve.citations import EpisodeIndex

        with FactStore(paths.facts_db) as store:
            roster = battles_in(store, EpisodeIndex(), fighter, 600, overrides)
    except Exception:  # noqa: BLE001 - routing must never be the thing that fails
        return False
    return roster is not None and bool(roster.members)


def _resolves_battle_result(
    paths: SeriesPaths, fighter: str, query: str, overrides: dict | None
) -> bool:
    """Whether this wiki holds a battle-table row naming the fight asked for.

    The probe runs the same read `build_roster` will: the first-named
    side's own `X/Battles` table (the wiki records the Result from the table
    owner's perspective, so the mirror-image table holds the mirror image of
    the answer -- the resolved subject is only the fallback when the question
    names no `between` span), the fight rows it keeps, and whether any of
    them names the question's opponent. A wiki that keeps no battle tables
    (Jujutsu Kaisen files its fights as standalone pages, not subtables)
    returns False and the question falls through to rule 3, which is where it
    belongs when no table stands behind it. A failure must never fail
    routing, so any error reads as "no result".
    """
    if not fighter:
        return False
    fighter = battle_result_fighter(query, fighter)
    try:
        with FactStore(paths.facts_db) as store:
            roster = battle_result(store, fighter, query, 600, overrides)
    except Exception:  # noqa: BLE001 - routing must never be the thing that fails
        return False
    return roster is not None


def _subject(paths: SeriesPaths, query: str, overrides: dict) -> tuple[str, str]:
    """What the question is about, and what kind of thing that is.

    Reuses the resolution `build_roster` already does, so the router and the
    retriever cannot disagree about the subject of the same question.
    """
    demote, priority = subject_ranking(overrides)
    try:
        with FactStore(paths.facts_db) as store:
            entities = rank_subjects(store.link_entities(query), demote, priority)
            if not entities:
                return "", ""

            # Unresolved candidates are ranked below resolved ones but not
            # discarded. `Luffy` is an alias with no page of its own, so
            # filtering it out left "What is Luffy's Devil Fruit?" choosing
            # between devil fruits and answering `Goe Goe no Mi`. Only the
            # ordering changes; nothing here resolves aliases, which 13 of 14
            # possessive questions already handle correctly.
            resolved = {row["name"] for row in entities if row["is_resolved"]}
            asked = set(content_words(query))
            owners = {owner.lower() for owner in _POSSESSIVE.findall(query or "")}

            # The type-priority order ranks every event page ahead of a
            # technique that shares a word with the question, and slicing to
            # the top eight *before* the overlap test could slice the subject
            # the question names outright clean away: "Every Fight Mahoraga
            # Has Ever Been In" was about `Sukuna vs. Yorozu` with
            # `Eight-Handled Sword Divergent Sila Divine General Mahoraga` at
            # rank nine. So the two tests that move a candidate -- a
            # possessive owner, and any word shared with the question -- run
            # over the whole pool first, and the slice only caps how many
            # candidates get semantic typing, which is the expensive part.
            preferred = sorted(
                enumerate(entities),
                key=lambda item: (
                    not bool(set(content_words(item[1]["name"])) & owners),
                    not bool(set(content_words(item[1]["name"])) & asked),
                    item[0],
                ),
            )[:8]
            typed = [
                (row["name"], sem.semantic_type(store, row["name"], overrides))
                for _, row in preferred
            ]

            # `SUBJECT_DEMOTE_TYPES` matches raw infobox ids, so it demotes
            # `episode` on Dragon Ball and misses `episode_box` on One Piece,
            # which is how "Who killed Ace?" came to be *about* an episode
            # called `Legendary Hour`. The semantic type says the same thing in
            # one vocabulary, so packaging loses here regardless of the wiki.
            # `rank_subjects` has already ordered these, and re-sorting purely
            # by word overlap made it worse: "What is Sukuna's Domain
            # Expansion?" ranks Sukuna first correctly, and overlap promoted
            # `Domain Expansion` over him for matching two words to one.
            #
            # So the existing order is kept and only two things move a
            # candidate: a possessive names the subject outright ("Sukuna's X"
            # is a question about Sukuna), and a candidate sharing *no* word
            # with the question sinks, which is what keeps `Legendary Hour`,
            # a TV special that shares nothing with "Who killed Ace?", from
            # being the subject.
            def rank(item: tuple[int, tuple[str, str]]) -> tuple:
                index, (name, semantic) = item
                words = set(content_words(name))
                names_owner = bool(words & owners)
                return (
                    not names_owner,
                    not (words & asked),
                    semantic in _PACKAGING_SUBJECTS,
                    name not in resolved,
                    index,
                )

            best = sorted(enumerate(typed), key=rank)
            return best[0][1] if best else ("", "")
    except Exception:  # noqa: BLE001 - routing must never be the thing that fails
        return "", ""

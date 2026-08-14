"""Which of the three retrieval modes a question needs.

This used to be one ternary, duplicated in the CLI and the API:

    mode = "roster" if looks_like_enumeration(query) else "narrative"

Two things were wrong with it. `qa` — the hybrid BM25 + vector + graph path with
a cross-encoder over the top of it, the most engineered part of the system — was
**unreachable**: no caller asking for `auto` could ever land there. And the
enumeration test is a regex, so `What grade of sorcerer is Aoi Todo?` matched
`grades? of` and came back as a list of Todo's five battles.

Measured before rebuilding, over 168 real queries: the regex and a structural
read disagree on 13, **all of them wh-questions**, and agree on all 154
enumeration topics. So the set-versus-not-set call is sound and stays; what was
missing is any way to tell a fact lookup from a story question once the answer
is "not a set".

A bare wh-word cannot make that distinction either — the same measurement wanted
`How did the Shibuya Incident unfold?` in `qa`, which is wrong. What separates
them is *what the subject is*: an event, battle or arc is a story; a character,
item or technique with an attribute asked of it is a lookup. That is read from
the ontology rather than from another keyword list.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from scriptengine.config import SeriesPaths, load_overrides, subject_ranking
from scriptengine.retrieve import chronology
from scriptengine.retrieve import semantics as sem
from scriptengine.retrieve.roster import content_words, looks_like_enumeration
from scriptengine.stores.facts import FactStore, rank_subjects

MODES = ("roster", "qa", "narrative")

_WH = re.compile(r"^\s*\W*(what|whats|what's|who|whos|who's|which|when|where|why|how)\b", re.I)

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

# "Sukuna's Domain Expansion" — whoever owns the attribute is the subject.
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

# Packaging only. Skipped when resolving *what a question is about*, because an
# episode page is never the subject unless it is named — that is how "Who killed
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
    interrogative = bool(_WH.match(query or ""))
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
    signals = {
        "set_shaped": set_shaped,
        "interrogative": interrogative,
        "plural_ask": plural_ask,
        "counting": counting,
        "story_verb": story_verb,
        "subject": subject,
        "subject_type": subject_type,
    }

    # 1. Order beats every other reading. "Every arc in order" is set-shaped and
    #    "Timeline of Dragon Ball" opens like a question, so both were being
    #    answered by something that cannot express order at all — the first with
    #    one arc's 84 chapters, the second with eight loose beats.
    if chronology.wants_chronology(query):
        return Route("roster", "asks for the story in order", signals)

    # 2. A count is a set even though it opens like a question.
    if counting:
        return Route("roster", "asks how many, which wants the set", signals)

    # 3. A wh-question about a thing is a lookup — this is the case the regex
    #    got wrong, and it has to win over the enumeration cue. Except when its
    #    verb is plural, which asks for the list rather than for one thing.
    if (interrogative and not plural_ask and not story_verb
            and subject_type not in _STORY_TYPES):
        if subject:
            return Route(
                "qa",
                f"question about {subject!r}, a {subject_type or 'known entity'}",
                signals,
            )
        # No subject resolved. qa is the path that searches rather than walking
        # a page, so an unanchored question belongs there — narrative has
        # nothing to walk.
        return Route("qa", "a question with no page to walk", signals)

    # 4. Otherwise the enumeration test decides, and on 154 real topics it was
    #    right every time.
    if set_shaped:
        return Route("roster", "asks for a set", signals)

    # 5. A plural question with no enumeration word is still a plural question.
    #    "What are Sukuna's named cursed techniques" carries none of `every`,
    #    `all`, `members of` — the plural noun is the only cue — and without
    #    this it falls past every test above and is answered as an account.
    if plural_ask:
        return Route("roster", "asks in the plural, which wants the list", signals)

    if interrogative and story_verb:
        return Route("narrative", "asks how something happened", signals)
    if subject_type in _STORY_TYPES:
        return Route("narrative", f"{subject!r} is an event rather than a thing", signals)

    # A bare name — "Prison Realm", "Playful Cloud" — is a lookup, not a story.
    # Narrative would walk that page top to bottom; qa answers what it is.
    if subject and subject_type and len((query or "").split()) <= 4:
        return Route("qa", f"names {subject!r} and asks nothing of it", signals)

    return Route("narrative", "an account rather than a set or a lookup", signals)


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
            # ordering changes — nothing here resolves aliases, which 13 of 14
            # possessive questions already handle correctly.
            resolved = {row["name"] for row in entities if row["is_resolved"]}
            ranked = [row["name"] for row in entities]
            typed = [
                (name, sem.semantic_type(store, name, overrides)) for name in ranked[:8]
            ]

            # `SUBJECT_DEMOTE_TYPES` matches raw infobox ids, so it demotes
            # `episode` on Dragon Ball and misses `episode_box` on One Piece —
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
            # with the question sinks — which is what keeps `Legendary Hour`,
            # a TV special that shares nothing with "Who killed Ace?", from
            # being the subject.
            asked = set(content_words(query))
            owners = {owner.lower() for owner in _POSSESSIVE.findall(query or "")}

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

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
    r"^\s*\W*(what|whats|what's|who|whom|whose|whos|who's|which|when|where|why|how)\b",
    re.I,
)

# The same wh-words unanchored: a wh-clause behind a discourse marker ("Despite
# what did X...?", "According to Y, what is Z?") is not at position 0, so the
# anchored `_WH` never sees it. `_WH` stays anchored (a position-0 test); this
# is the "is there a wh-clause at all" test the marker branch needs.
_WH_ANY = re.compile(
    r"\b(what|whats|what's|who|whom|whose|whos|who's|which|when|where|why|how)\b",
    re.I,
)

# A wh-word behind one leading preposition still opens the question: "In
# which arc does X take place?" and "After which saga did X happen?" are
# the natural way to ask for a battle's infobox field, and the position-0
# test read them as statements, so the question fell to narrative -- the
# one path that strips exactly those fields. One preposition, not a free
# walk: "in order to" and "after the war" stay statements. `using` is the
# campaign's G2b: "Using Playful Cloud, what was he able to smash through?"
# opens like a statement but the wh-clause is the question.
_LEADING_PREPS = frozenset({
    "in", "on", "during", "after", "before", "at", "by", "for", "to",
    "with", "within", "over", "under", "from", "since", "until", "upon",
    "off", "across", "through", "around", "about", "between", "amid",
    "using",
    # The scope preposition of a technique lookup (2026-09-03, technique
    # prose pass): "Against which domains is Hollow Wicker Basket
    # ineffective?" fronts the scope phrase and the position-0 wh test read
    # it as a statement, so the question fell to the narrative default, the
    # one path that never serves the page's Description. The wh-word behind
    # the preposition is what promotes it; "Against all odds, X prevailed"
    # has no wh-word after the preposition and stays a statement.
    "against",
})

# A leading discourse marker or a parenthetical source does not make a
# question a statement: "Despite what demeanor did X realize ...?" and
# "According to the X section, what is Y?" open with the marker but the
# wh-clause is the real question. The marker alone (no wh-word anywhere)
# stays a statement, so this only ever promotes genuine questions. `once`
# is the campaign's G20 (Kechizu Q036, 2026-09-01): the temporal clause
# fronts the mechanism question ("Once Kechizu or Eso blood enters a target
# through wounds what happens during Decay?") and the wh-only test read the
# whole thing as a statement, so the question fell to the narrative default
# and the answer's page was never walked. `when` needs no entry: it is a
# wh-word and the position-0 test already sees it.
_LEADING_DISCOURSE = frozenset({
    "despite", "although", "while", "if", "unless", "according", "even",
    "once",
})

# A yes/no question fronts an auxiliary, not a wh-word: "Does Shoko have an
# innate cursed technique?" (G9a) and "Was Suguru Geto dependent on his
# curses in battle?" (G8a) open like statements to the wh-only test below, so
# the one mode that reads the page's prose (qa) was unreachable for the whole
# yes/no family -- 9 of 21,521 questions in the corpus until release R1-a.
_AUX_FRONT = frozenset({
    "is", "are", "was", "were", "do", "does", "did", "can", "could",
    "will", "would", "has", "have", "had", "should", "may", "might", "must",
})


def _is_interrogative(query: str) -> bool:
    """Whether the question opens with a wh-word, directly or behind a marker."""
    q = (query or "").strip()
    if _WH.match(q):
        return True
    # A leading adverbial clause, not a marker word: "As soon as Geto closed
    # the distance, what did Toji cut down?" opens like a statement and the
    # comma carries the wh-clause (the campaign's G2b). Runs before the
    # preposition branch because that one early-returns: "Using Playful
    # Cloud, what was..." has a non-wh word after `using`, and only the comma
    # rule sees the wh-clause. The clause alone is not a question, so a comma
    # with no wh-word after it stays a statement.
    if "," in q and _WH.match(q.split(",", 1)[1]):
        return True
    parts = q.split()
    if not parts:
        return False
    # R1-a (G8a/G9a): a yes/no question fronts an auxiliary, and the wh-only
    # test read it as a statement, so the battle narrative came back where
    # the page that answers it was needed. Recognition only: whether the
    # question is an account or a lookup is the story-verb guard in `route`
    # (`_YES_NO_STORY`), the same way the head window decides for the wh form.
    if parts[0].lower() in _AUX_FRONT:
        return True
    if len(parts) >= 2 and parts[0].lower() in _LEADING_PREPS:
        return bool(_WH.match(" ".join(parts[1:])))
    if parts[0].lower() in _LEADING_DISCOURSE and _WH_ANY.search(q):
        return True
    return False


def _is_yes_no(query: str) -> bool:
    """A yes/no question: an auxiliary fronts the clause and no wh-word appears.

    "Have all the characters been showcased?" is a completeness claim the page's
    prose answers, not a list ask -- a list is always wh-worded ("Who are all
    the X") or an "Every X" statement, never yes/no. A leading adverbial clause
    ("Starting from this episode, have all ...") fronts the auxiliary, so the
    check looks past the first comma (the episode pass's Ep8 retire, 2026-09-01).
    A statement or a wh-question reads False.
    """
    q = (query or "").strip()
    if not q or _WH_ANY.search(q):
        return False
    tail = q.split(",", 1)[1] if "," in q else q
    words = tail.split()
    return bool(words) and words[0].lower() in _AUX_FRONT

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

# A wh-word glued to a SINGULAR battle noun that a predicate then describes:
# "Which battle in Ui Ui's history is listed as offscreen?", "What battle comes
# before Saitama vs. Boros?". That identifies one battle by property or
# position and wants the prose carrying the annotation; the battles-in roster
# lists a fighter's battles and cannot name the one the question describes.
# `_BATTLES_IN_WH` above over-matches these (G16: once a short-named fighter
# like `Ui Ui` resolves a list, this wh-form was claimed for the roster and its
# prose-only answer went missing). Plural "what battles was X in" and "who did
# X fight" enumerate the list and are untouched: a plural noun breaks the
# singular `\b` and the `who`-form has the subject between the wh-word and the
# verb. The trailing `(?=\s)` requires the predicate, so a bare "what battle?"
# keeps the list reading. The second alternative is the episode pass's Ep7
# retire (2026-09-01): "What does the battle prove about X?" treats one named
# battle as the subject of a significance predicate, so the fighter's whole
# fight list -- which cannot say what that battle proved -- was served instead
# of the page that can. A definite singular battle ("the battle") is one
# battle, not a list; the plural "what battles was X in" and the "who did X
# fight" form carry no "the" and are untouched.
_SINGLE_BATTLE_WH = re.compile(
    r"\b(which|what)\s+(?:a\s+)?(battle|fight|duel)\b(?=\s)"
    r"|\b(which|what)\b\s+(?:does|do|did|is|are|was|were)\s+the\s+(?:battle|fight|duel)\b",
    re.I,
)

# "Sukuna's Domain Expansion": whoever owns the attribute is the subject.
_POSSESSIVE = re.compile(r"\b([A-Za-z][\w.-]*)['’]s\b")

# R5-b (G12): a possessive that owns the OBJECT of a preposition ("over a
# weaker sorcerer's barrier") is not the question's topic -- the agent the
# question names ("Suguru Geto cast ...") is the subject, and the possessive
# must not outrank it. Only a topic possessive ("What is Sukuna's Domain
# Expansion?") names the subject outright. A preposition within a few words
# before the owner marks the object case; `of` is deliberately out, because it
# links a possessive relation ("the power of Sukuna's domain"), not an object.
_OBJECT_PREPS = frozenset({
    "in", "on", "at", "over", "under", "with", "against", "during", "before",
    "after", "within", "across", "through", "onto", "into", "upon", "around",
    "about", "off", "beside", "behind", "beyond",
})


def _topic_owners(query: str) -> set[str]:
    """The possessive owners that name the subject, not the object's.

    An owner buried in a prepositional object ("over a weaker sorcerer's
    barrier") has a preposition within three words before it, and its candidate
    must not win the possessive boost; a topic owner ("Sukuna's") has none and
    does. G12: this is what keeps `Jujutsu Sorcerer` from outranking the
    `Suguru Geto` the sentence names as the agent.
    """
    owners: set[str] = set()
    for match in _POSSESSIVE.finditer(query or ""):
        preceding = (query or "")[: match.start(1)].split()[-3:]
        if any(word.strip(".,;:!?()[]\"'") in _OBJECT_PREPS for word in preceding):
            continue
        owners.add(match.group(1).lower())
    return owners

# Verbs that make a question about events rather than attributes. `unfold` and
# `happen` are the two that a wh-word rule alone got wrong.
_NARRATIVE_VERBS = re.compile(
    r"\b(happen(ed|s)?|unfold(ed|s)?|occur(red|s)?|go down|play out|"
    r"lead up to|end(ed)?|start(ed)?|begin|began)\b",
    re.I,
)

# The campaign's G4b: "What happens to targets in X's domain?" is a mechanism
# question (what the thing does to something), and the head check read
# `happens` as a narrative verb, so the one path that cannot answer a
# mechanism walked a 91-beat story instead. Only the present/will/would form
# is the effect: "What happened to Nanami during the Shibuya Incident?" is a
# fate, an account, and stays narrative -- so `ed` is deliberately not in the
# optional tail. G7 (Panda): the hypothetical twin "What happens if one of
# Panda's cores is damaged?" asks the same mechanism the page's prose answers,
# so `if` joins `to`; "What happened if ..." still carries `ed` and stays
# narrative.
_EFFECT_ON = re.compile(
    r"^\s*\W*what\s+(?:will|would|can|could|may|might)?\s*"
    r"happen(?:s)?\s+(?:to|if)\b",
    re.I,
)

# The story verb of a yes/no question sits after the auxiliary and its one-word
# subject ("Did Sukuna **kill** Nanami?" is an account, not a lookup), where
# the head-window check above never looks. The family is `_NARRATIVE_VERBS`'
# event verbs plus the action verbs an account is built from; `_EFFECT_ON`
# still carves the mechanism form out of both, so a "what happens" question is
# not an account either way. R1-a's guard; the opm canon baseline is the
# detector if this ever over-claims (the prompt's narrowing is there for it).
_YES_NO_STORY = re.compile(
    r"^\s*(?:is|are|was|were|do|does|did|can|could|will|would|has|have|had|"
    r"should|may|might|must)\s+[A-Za-z][\w'.-]*\s+"
    r"(?:happen(?:s|ed)?|unfold(?:s|ed)?|occur(?:s|red)?|go(?:es|t) down|"
    r"play(?:s|ed)? out|lead(?:s)? up to|end(?:s|ed)?|start(?:s|ed)?|"
    r"begin|began|kill(?:s|ed)?|fight(?:s|ed|ing|en)?|attack(?:s|ed|ing)?|"
    r"defeat(?:s|ed)?|died|die|lose(?:s|d)?|lost|win(?:s)?|won|"
    r"surrender(?:s|ed)?|flee(?:s|d|ing)?)\b",
    re.I,
)

# The campaign's G9b (R5-a): a counterfactual asks what WOULD HAVE been the
# case, not what happened, and the head verb (`happened`) reads it as an
# account, so "What would have happened if Yuta had not ..." walked a
# narrative that never carries the factual answer. The discriminator is the
# clause, not the head verb: a past-perfect `if` clause (`if X had (not) ...`,
# `if X hadn't ...`, `if X were not ...`) and/or a `would` main clause mark the
# hypothetical. The past-factual form the eval gold row rests on ("What
# happened to Nanami during the Shibuya Incident?") carries neither marker, so
# the two separate cleanly.
_COUNTERFACTUAL = re.compile(
    r"\bif\b[^.?!]*(?:\bhad\b|\bhadn'?t\b|\bwere\b)|\bwould\b",
    re.I,
)

# A present-tense "how" question asks for the rule, condition or mechanism
# that governs a thing, not for the chronological account a past-tense "how did
# ... unfold?" asks for. "How does a team win the Team Battle?" (the episode
# pass's Ep14 retire, 2026-09-01) wants the win condition -- a fact the page's
# own prose carries -- but its subject resolved to a battle (an event), and with
# no story verb it fell to the story-type narrative branch, where the rule never
# appears. The present auxiliary is the discriminator, the same present-versus-
# past line `_EFFECT_ON` draws for the "what happens" family (the G4b/G7
# carve-out): a past auxiliary ("how did the Shibuya Incident unfold?") keeps
# its narrative read; a present one reaches qa.
_HOW_MECHANISM = re.compile(
    r"^\s*\W*how\s+(?:does|do|can|could|will|would|may|might|should|must)\b",
    re.I,
)

# "in Episode 40" / "per Episode 41" / "Episode 29's": the question is anchored
# to one instalment, so it is about that page's own prose, never the 59-episode
# wiki roster a set cue or a plural verb would otherwise summon. The episode
# pass's plural-ask / "what kind of X" misroutes (2026-09-01, the Eps 21/22/26/
# 29/40 retires): the router handed them the episode roster -- infobox facts
# only, no plot prose -- so the page's answer was never in the bundle.
_EPISODE_ANCHORED = re.compile(r"\bepisode\s+\d+", re.I)

# Subject types that mean the question is about a story, not a thing.
_STORY_TYPES = frozenset({sem.EVENT, sem.MEDIA})

# Subject types that carry their own story in a narrative stream, or whose type
# the router cannot trust to decide the read. When an authored page resolves to
# one of these, a story-verb question keeps the cross-page narrative read. Every
# other resolved (non-story) type is a "thing" -- a technique, an item, a
# location -- whose story is recorded in its own page's prose (a technique's
# Usage, an item's history), so a story-verb question authored on it must be
# read from that page (qa), not the named characters' stream. Malevolent Shrine
# 060: "What happened in the third exchange of domains between Sukuna and Gojo?"
# is authored on the technique page, but the router handed it to the character
# stream of the two sorcerers it names, where the Usage prose that records the
# exchange is never served.
_NON_THING_TYPES = frozenset({sem.CHARACTER, sem.UNKNOWN})

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

# The fields that hold exactly one value per subject. A plural-shaped question
# that names one of these ("What are the kanji for X's name?") is a lookup, not
# a set ask: the kanji of a name is a single string, so the plural noun is the
# only cue and rule 5 would hand it to a roster that renders nothing for it.
# G17 (Phantom Cursed Spirit Q001, 2026-08-31; numbered in R6 -- the run that
# found it mislabelled it G11, which is the R1 location-scoped outcome gap):
# on a subject that *does* resolve
# a set (its battle roster) the plural rule fired before rule 6 could rescue the
# field lookup, so the kanji -- which the qa beat carries -- was unservable.
# The multi-valued fields (chapters, episodes, volumes, anime, manga) are kept
# out: "What are all the chapters of the Culling Game?" genuinely wants the list.
_SINGLE_VALUE_FIELDS = frozenset(
    {"kanji", "romaji", "japanese", "name",
     "next", "previous", "arc", "place", "event", "outcome", "date"})

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


def route(paths: SeriesPaths, query: str, settings=None, subject: str | None = None) -> Route:
    """Pick roster, qa or narrative for `query`.

    Order matters and is set by what was measured, not by preference: a
    wh-question that names one thing beats the enumeration cue, because
    "what grade of sorcerer is X" contains an enumeration word and is not a set.

    `subject` (R1-b) is the page the question is authored against, which the
    scorer sends with it. It is a precedence rule over `_subject()`'s own
    inference for the mode decision, never an override of the query's read:
    a story-typed page keeps the narrative read, and the qa wide search takes
    the page as a focus either way (the G3a recall fix in `build_context`).
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
    story_verb = bool(_NARRATIVE_VERBS.search(head)) and not _EFFECT_ON.match(
        query or "")
    # R1-a: a yes/no question fronts the same story verbs behind its subject,
    # and the head window never sees them there. "Did Sukuna kill Nanami?" is
    # an account the way the wh form is; the mechanism form is still carved
    # out by the `_EFFECT_ON` check above, which an auxiliary-fronted question
    # can never satisfy.
    if not story_verb:
        story_verb = bool(_YES_NO_STORY.match(query or ""))

    # R5-a (G9b): a counterfactual asks what would have been the case, not what
    # happened. The story-verb read (which sent "What would have happened if
    # ..." to a narrative that never carries the answer) is cleared so rule 3
    # claims it for qa; a past-factual account has no counterfactual marker and
    # keeps its narrative read (the eval gold row it guards).
    counterfactual = bool(_COUNTERFACTUAL.search(query or ""))
    if counterfactual:
        story_verb = False
    # A present-tense "how" question is a mechanism/rule lookup, not an
    # account, even when its subject is an event (the Ep14 Team-Battle win
    # condition). Computed here so the story-type branch below can defer to it.
    how_mechanism = bool(_HOW_MECHANISM.match(query or ""))
    episode_anchored = bool(_EPISODE_ANCHORED.search(query or ""))

    inferred, inferred_type = _subject(paths, query, overrides)
    # R1-b (G8b/G8d): the page the question is authored against used to reach
    # only the qa wide search, so the mode decision was blind to the page that
    # answers it. G8b's own words resolve the event the question is scoped by
    # (the Geto page is never considered); G8d's possessive resolves the
    # organization a "weaker sorcerer's barrier" names. A precedence rule, not
    # an override: a non-story page takes the mode decision, a story page (or
    # an unresolvable one) keeps the query's own read. `subject` here is still
    # the authored-page parameter; the rebind below hands it to the callers.
    hinted = _subject_hint(paths, subject, overrides)
    # The authored page, captured before the rebind below shadows the parameter:
    # a story-verb beat on a media (episode) page is read from that page (the
    # episode pass's Ep5/6/8 fix in the story-verb rule further down).
    authored_page = subject
    if hinted is not None:
        inferred, inferred_type = hinted
    subject, subject_type = inferred, inferred_type
    subject_hint = subject if hinted is not None else ""
    # F2/F4 (2026-09-02): whether the authored page is one instalment. A question
    # anchored to "Episode N" is about that page's own prose, so a named character
    # ("...does Megumi head") or entity ("...the Death Paintings") in the query must
    # not steal the subject off the episode -- that misroute (the ep41/43/52/59
    # char-hijack and the ep49 roster-route families) handed the question to the
    # entity's narrative stream or roster, where the episode's plot prose is never
    # served. Computed once; the rule 3 deferral and the rescue below both read it.
    authored_is_media = (
        _authored_media(paths, authored_page, overrides) if episode_anchored else False
    )
    # A count or a plural question wants a roster only if this wiki resolves a
    # set for it; otherwise it asks for a number in prose ("how many wards did
    # Kenjaku's chain reaction compromise?") and rule 3 answers from text. The
    # probe runs the same resolution build_roster will, so router and retriever
    # cannot disagree about whether the set exists.
    has_set = (
        _resolves_a_set(paths, query, settings, counting=counting)
        if (counting or plural_ask) else False
    )

    # An interrogative fight-list question ("Who did Mahoraga fight?") wants the
    # same roster as its statement twin, but rule 3 would claim it for `qa` first.
    # Probe only when the phrasing is a wh-question about fighting and a subject
    # resolved; otherwise leave the existing rules to decide. A single-battle
    # identification ("which battle is listed as offscreen") is carved out: it
    # names one battle the roster cannot list, so it falls through to rule 3.
    battles_in_ask = (
        bool(_BATTLES_IN_WH.search(query or ""))
        and not _SINGLE_BATTLE_WH.search(query or "")
        and interrogative
    )
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
    # G17: a plural-shaped question that names a single-valued infobox field is a
    # lookup, not a set ask. "What are the kanji for X's name?" holds one kanji
    # string, so on a subject that resolves a set the plural rule used to claim
    # it before rule 6 could rescue it (the kanji is on the qa beat, not the
    # roster). Computed here so both plural rules can defer to it.
    asks_single_field = (
        interrogative and _asks_for_field(paths, query, single_only=True)
    )
    signals = {
        "set_shaped": set_shaped,
        "interrogative": interrogative,
        "plural_ask": plural_ask,
        "counting": counting,
        "story_verb": story_verb,
        "counterfactual": counterfactual,
        "how_mechanism": how_mechanism,
        "episode_anchored": episode_anchored,
        "battles_in_ask": battles_in_ask,
        "battle_result_ask": battle_result_ask,
        "asks_single_field": asks_single_field,
        "subject": subject,
        "subject_type": subject_type,
        "subject_hint": subject_hint,
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
    #    a lookup too: "who are the current four emperors" reads prose. G17: a
    #    plural question naming a single-valued field (the kanji of a name) is a
    #    lookup even when the subject resolves a set, so `asks_single_field`
    #    clears the plural carve-out.
    if (interrogative and not (plural_ask and has_set and not asks_single_field)
            and not story_verb and subject_type not in _STORY_TYPES
            # F2 (2026-09-02): an episode-anchored question authored on one
            # instalment defers to the rescue below, which reads the page's own
            # prose. Claiming it here would key the read to the named character
            # (Megumi, Mahito) and the episode's beat is never served.
            and not (episode_anchored and authored_is_media)):
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

    # A yes/no question carrying a set-word ("Starting from this episode, have
    # all the characters been showcased?") is a completeness claim read from the
    # page's prose (qa), not a list ask (roster). It must fire before rule 4,
    # whose `set_shaped` would hand it a roster that cannot say "yes, all of
    # them"; `_is_yes_no` (no wh-word) is what separates it from a real list.
    if _is_yes_no(query) and set_shaped:
        return Route("qa", "a yes/no completeness claim read from prose", signals)

    # An episode-anchored question ("...in Episode 40", "per Episode 41") is
    # about one instalment's own prose, never the 59-episode wiki roster. A set
    # cue (rule 4) or a plural verb (rule 5) used to hand it that roster --
    # infobox facts only, no plot prose -- so the page's answer was never served
    # (the episode pass's plural-ask / "what kind of X" misroutes, 2026-09-01).
    # F2/F4 (2026-09-02) generalized this rescue: the guard is now the authored
    # page being one instalment (`authored_is_media`), not the subject resolving
    # to a media page. A question the query anchors to "Episode N" is read from
    # that page whatever the named subject (a character like Megumi, an entity
    # like the Culling Game) or the form (singular wh, plural, yes/no) -- the
    # ep41/43/52/59 char-hijack and the ep49 roster-route families named a
    # character or entity in the query and fell to that entity's narrative
    # stream or roster, which carry no plot prose. The read goes to the anchored
    # page instead. `interrogative` keeps statements on the rules below, and a
    # non-episode authored page (a character page that merely mentions an
    # episode) is left to those rules, so the gate stays on the page a question
    # was written against.
    # F2/F4 (2026-09-02): the question gate is `interrogative` (opens like a
    # question) OR a wh-word inside a question (ends with "?"). A wh-clause can
    # sit behind a marker or a noun phrase -- "On her way to which floor"
    # (ep43-045) -- and the opener test reads the whole thing as a statement,
    # stranding an episode-anchored question on the entity's rules; the
    # wh-word says it is still a question about that page's prose. A genuine
    # statement (no trailing "?") stays on the rules below.
    episode_question = (
        interrogative
        or (bool((query or "").strip().endswith("?"))
            and bool(_WH_ANY.search(query or "")))
    )
    if episode_anchored and authored_is_media and episode_question:
        return Route("qa", f"an episode-anchored fact read from {authored_page!r}", signals)

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
    #    it keeps its old reading: an account of whatever the page holds. G17: a
    #    single-valued-field lookup defers to rule 3 / rule 6 instead.
    if plural_ask and has_set and not asks_single_field:
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
        # An episode-local story beat is authored against a single media page,
        # whose own Plot Details carry it; the cross-episode narrative stream
        # serves it badly. A story beat on a "thing" page (a technique's Usage,
        # an item's history) is recorded in that page's own prose, so it is read
        # from the page (qa), not the named characters' stream. A genuine account
        # is authored against an event/arc -- or names no page at all, as the
        # eval does -- and keeps the narrative read. `subject_hint` is set only
        # when the authored page resolved to a non-story type, so the second
        # branch fires exactly for a thing page that is neither a character nor
        # of unknown type (_NON_THING_TYPES keeps those on the narrative read).
        if _authored_media(
            paths, authored_page, overrides
        ) or (subject_hint and subject_type not in _NON_THING_TYPES):
            return Route(
                "qa",
                f"a story beat recorded on {authored_page!r}'s own page",
                signals,
            )
        return Route("narrative", "asks how something happened", signals)
    # A present-tense "how" question is a rule/mechanism lookup even when its
    # subject is an event or battle: the Ep14 "How does a team win the Team
    # Battle?" resolved `Sukuna vs. Jogo` (an event) and fell to the narrative
    # branch below, where the win condition never appears. A past-tense "how
    # did ...?" is an account and keeps the story-type read.
    if how_mechanism and subject_type in _STORY_TYPES:
        return Route(
            "qa",
            f"a how-mechanism about {subject!r}, read from prose",
            signals,
        )
    if subject_type in _STORY_TYPES:
        return Route("narrative", f"{subject!r} is an event rather than a thing", signals)

    # A bare name ("Prison Realm", "Playful Cloud") is a lookup, not a story.
    # Narrative would walk that page top to bottom; qa answers what it is.
    if subject and subject_type and len((query or "").split()) <= 4:
        return Route("qa", f"names {subject!r} and asks nothing of it", signals)

    return Route("narrative", "an account rather than a set or a lookup", signals)


def _asks_for_field(paths: SeriesPaths, query: str, single_only: bool = False) -> bool:
    """Whether `query` names an infobox field this corpus records.

    `content_words` already strips stopwords and possessives, so the field
    word survives any phrasing ("the Cursed Child Arc's romaji" leaves
    `romaji`). A failure must never fail routing, so any error reads as "no
    field" and the question falls through to the narrative rules.

    `single_only` restricts to the single-valued fields (G17): a plural question
    that names one of those is a lookup the plural rules must not claim.
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
    if single_only:
        wanted &= _SINGLE_VALUE_FIELDS
    return bool(wanted & keys)


# A prepositional scope phrase, up to the prep + three words ("in battle",
# "during the Culling Game"). Only spatial/temporal scopes are stripped: "of"
# is genitive and part of set names ("members of the X"), so it stays. See the
# G1 note in `_resolves_a_set`.
_SCOPE_PHRASE = re.compile(
    r"\b(?:in|on|at|during|before|after|within|across|over|through|against)"
    r"(?:\s+[A-Za-z][\w'.-]*){0,3}\b",
    re.I,
)


def _resolves_a_set(
    paths: SeriesPaths, query: str, settings=None, counting: bool = False
) -> bool:
    """Whether this wiki actually holds a set for `query` to enumerate.

    Rules 2 and 5 used to trust the phrasing alone, so "how many wards did
    Kenjaku's chain reaction compromise?" -- a number in prose -- was handed a
    roster of Kenjaku techniques. The probe runs the same resolution
    build_roster will run for real, one member rendered, and asks it how sure
    it is: a declared phrase that claimed the topic (`matched`) or an exact
    discovery is a set; partial and weak are guesses the prose can answer
    better. A failure here must never fail routing, so any error reads as "no
    set" and the question falls through to rule 3.

    A prepositional scope phrase is stripped first (bug G1): "What are
    Nanami's two greatest assets in battle?" resolved Kento Nanami's 0-beat
    *Battles* roster on the scope word "battle" and rule 5 handed it over, so an
    attribute lookup got a roster of nothing. A genuine set ask names the set
    as the wh-object ("What battles was X in?", "What are X's cursed
    techniques"), which survives the strip; only the scope trigger goes.

    `counting` sharpens the `matched` short-circuit (R1-d): a count is a set
    only when the count *is* the set's size, and a partial match is precisely
    the topic asking for less of the set than the wiki holds -- "How many of
    Suguru Geto's named techniques are used to trap?" claimed the phrase,
    could not check "used to trap" against anything, and the number of
    trapping techniques is in the prose, not the roster. A membership question
    ("Who are the members of the Phantom Troupe?") wants the set itself
    whatever the confidence: its only unverified words are the interrogative,
    so the short-circuit stands for it.
    """
    probe = _SCOPE_PHRASE.sub(" ", query or "")
    try:
        roster = build_roster(paths, probe, settings, max_members=1, member_chars=0)
    except Exception:
        return False
    if roster.matched and (
        not counting or roster.confidence in ("exact", "declared")
    ):
        return True
    # A found set always carries a basis (the set's name) or a rendered
    # member. The no-set fallthroughs return a bare `Roster(subject=...)`
    # whose confidence is the dataclass default "declared" -- bug G6, caught
    # on Panda: "How many cores are inside Panda's body, and what are they?"
    # and "What are the kanji for Panda's name?" found no set, and the
    # default read as "the set exists", so counting and plural questions
    # walked a roster that rendered nothing instead of reading the page.
    if not (roster.basis or roster.members):
        return False
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
            # R5-b (G12): only a topic possessive names the subject outright;
            # an owner buried in a prepositional object ("over a weaker
            # sorcerer's barrier") must not win the boost over the agent the
            # question names.
            owners = _topic_owners(query or "")

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


def _subject_hint(
    paths: SeriesPaths, hint: str | None, overrides: dict
) -> tuple[str, str] | None:
    """The authored page's type, when it would change the mode decision.

    The scorer sends the page a question is authored against (the G3a fix),
    and the router let it reach only the qa wide search, so the mode was
    decided blind to the page that answers: G8b's own words resolve the event
    the question is scoped by, and G8d's possessive resolves the organization
    a "weaker sorcerer's barrier" names. A story-typed or unresolvable hint
    returns None and the query's own subject stands -- the hint is a
    precedence rule, never an override, and the qa wide search takes the page
    as a focus either way. A failure must never fail routing, so any error
    reads as "no hint".
    """
    if not hint:
        return None
    try:
        with FactStore(paths.facts_db) as store:
            entities = store.link_entities(hint)
            if not entities:
                return None
            resolved = [row for row in entities if row["is_resolved"]]
            row = resolved[0] if resolved else entities[0]
            semantic = sem.semantic_type(store, row["name"], overrides)
    except Exception:  # noqa: BLE001 - routing must never be the thing that fails
        return None
    if semantic in _STORY_TYPES:
        return None
    return row["name"], semantic


def _authored_media(paths: SeriesPaths, page: str | None, overrides: dict) -> bool:
    """Whether the authored page is a single media/episode instalment.

    An episode-local story beat ("What does Yuji begin, meanwhile?", authored
    against `Episode 8`) is read from that page's own Plot Details, not the
    cross-episode narrative stream that serves it badly (the episode pass's
    Ep5/6/8 retires, 2026-09-01). Only a `media` page -- one instalment --
    triggers this; an event or arc page keeps the narrative read for a genuine
    account. The eval's standalone narrative questions name no media page, so
    they are untouched. A failure must never fail routing, so any error reads
    as "not a media page".
    """
    if not page:
        return False
    try:
        with FactStore(paths.facts_db) as store:
            entities = store.link_entities(page)
            if not entities:
                return False
            resolved = [row for row in entities if row["is_resolved"]]
            row = resolved[0] if resolved else entities[0]
            return sem.semantic_type(store, row["name"], overrides) == sem.MEDIA
    except Exception:  # noqa: BLE001 - routing must never be the thing that fails
        return False

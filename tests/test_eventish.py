"""The U-WP3 event-likelihood proxy (tools/train/eventish.py).

The lexicon is the proxy's only signal: a window is `eventish` iff a
LEXICON word occurs at a word boundary, case-folded. These tests pin
what the flag must keep working -- every inflection of the 12-verb
inventory (the verbs the student answers in), the U-WP3 brief's stems,
case-folding, and the word-boundary discipline (a lexicon word glued
to other letters is NOT a hit) -- so a lexicon edit that drops a verb
inflection or breaks the boundaries fails here, not in the U-WP4
pools' 50/50 split. The module is loaded from its tools/train path
(that directory is not a package).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "eventish", ROOT / "tools" / "train" / "eventish.py")
eventish = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eventish)

LEXICON = eventish.LEXICON
is_eventish = eventish.is_eventish
hit_words = eventish.hit_words

# The 12-verb inventory (events.EVENTIVE_VERBS + extra_verbs) in the
# tense forms a wiki passage actually uses: an inflection the gold
# states (Gojo "kills" him) must flag even though the gold verb is
# `killed`. A missing inflection is a silent recall leak on the pool
# split -- pin every one.
TWELVE_VERB_INFLLECTIONS = {
    "arrived": {"arrive", "arrives", "arriving", "arrived"},
    "awakened": {"awaken", "awakens", "awakening", "awakened"},
    "betrayed": {"betray", "betrays", "betraying", "betrayed"},
    "captured": {"capture", "captures", "capturing", "captured"},
    "defeated": {"defeat", "defeats", "defeating", "defeated"},
    "departed": {"depart", "departs", "departing", "departed"},
    "escaped": {"escape", "escapes", "escaping", "escaped"},
    "fought": {"fight", "fights", "fighting", "fought"},
    "killed": {"kill", "kills", "killing", "killed"},
    "met": {"meet", "meets", "meeting", "met"},
    "saved": {"save", "saves", "saving", "saved"},
    "sealed": {"seal", "seals", "sealing", "sealed"},
}

# The U-WP3 brief's extra stems (the event synonyms), base forms:
BRIEF_STEMS = (
    "battle", "fight", "clash", "duel", "kill", "slay", "murder",
    "die", "death", "defeat", "beat", "overpower", "meet",
    "encounter", "arrive", "reach", "enter", "return", "leave",
    "depart", "flee", "escape", "capture", "abduct", "kidnap",
    "imprison", "seal", "save", "rescue", "protect", "betray",
    "awaken", "attack", "ambush",
)


def test_twelve_verb_inflections_all_in_lexicon():
    for verb, forms in TWELVE_VERB_INFLLECTIONS.items():
        missing = forms - LEXICON
        assert not missing, f"{verb!r} is missing inflection(s) {sorted(missing)}"


def test_brief_stems_in_lexicon():
    missing = {stem for stem in BRIEF_STEMS if stem not in LEXICON}
    assert not missing, f"brief stems missing from LEXICON: {sorted(missing)}"


def test_lexicon_is_lowercase_words():
    # The match is case-folded text vs a \b-anchored regex: a word with
    # a space or a non-ascii letter would silently widen or break it.
    for word in LEXICON:
        assert word.isascii() and word.islower() and word.isalpha(), word


def test_gold_verb_form_flags():
    # The recall bar's unit: the gold's own verb wording flags.
    for sentence in (
        "Sukuna defeated Gojo in the end.",
        "He killed the last of them.",
        "The two met for the first time.",
        "She escaped the domain.",
        "They arrived at the shrine at dawn.",
        "He was captured by the curse users.",
        "Gojo sealed the spirit away.",
        "The battle ended without a victor.",
    ):
        assert is_eventish(sentence), sentence
        assert hit_words(sentence), sentence


def test_case_folded():
    assert is_eventish("THE BATTLE BEGAN AT DAWN")
    assert is_eventish("He FIGHTS On.")
    assert "battle" in hit_words("The BATTLE was long")


def test_inflection_form_reports_the_longer_word():
    # Longest-first alternatives + \b: "battles" is a hit as
    # `battles` (a plural), never as `battle` (no boundary before the s).
    assert hit_words("The battles were many") == ("battles",)
    assert hit_words("he was slain") == ("slain",)


def test_word_boundary_prefix_is_not_a_hit():
    # "battlefield" glues other letters onto "battle": no boundary, no
    # flag (a page about terrain is not eventish because of the word).
    assert not is_eventish("the battlefield was quiet")
    assert not is_eventish("a deathly silence fell")
    assert not is_eventish("leftover food sat on the table")


def test_word_boundary_suffix_is_not_a_hit():
    # ...and the other side: "unmet" is not "met", "guardian" is not
    # "guard".
    assert not is_eventish("his needs went unmet")
    assert not is_eventish("the guardian kept the gate")
    assert hit_words("he guarded the gate") == ("guarded",)


def test_plain_text_is_not_eventish():
    # Sentences with no lexicon word anywhere must not flag -- this is
    # the proxy's false-positive side (the earned-empties share).
    assert not is_eventish("the river flows past the old town in spring")
    assert not is_eventish("she was born in a small village by the sea")


def test_held_is_a_round_two_hit():
    # The round-2 audit words are the proxy's behaviour, not an
    # accident: pin one so a lexicon trim is deliberate.
    assert is_eventish("they held the sorcerer in place")
    assert "held" in hit_words("they held the sorcerer in place")


def test_empty_and_none_text():
    assert not is_eventish("")
    assert not is_eventish(None)
    assert hit_words("") == ()
    assert hit_words(None) == ()


def test_hit_words_are_sorted_and_unique():
    # "He fought and killed two guards": guards is the PLURAL noun form
    # (in the lexicon), and the report is a sorted de-duplicated tuple.
    assert hit_words("He fought and killed two guards") == \
        ("fought", "guards", "killed")
    assert hit_words("a battle and another battle") == ("battle",)
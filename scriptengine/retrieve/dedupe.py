"""One ability under two names: the wiki's own title and the bare word inside it.

An enumeration is scored on membership, so a set that names the same ability
twice is wrong twice: the count is inflated, and the second name is counted as
a member nobody asked for. Measured on Jujutsu Kaisen, the engine returned all
of these pairs, each pair inside a single answer:

    Blue            and  Cursed Technique Lapse: Blue
    Red             and  Cursed Technique Reversal: Red
    Purple          and  Hollow Technique: Purple
    Simple Domain   and  New Shadow Style: Simple Domain
    Jacob's Ladder  and  Maximum Output: Jacob's Ladder

The shape is always the same. The wiki titles the specific form
`<Qualifier>: <Base>` or `<Style>: <Base>` and *also* keeps a page for the bare
`<Base>`, so the two names reach one roster by two routes -- one out of a
category, one out of the prose -- and neither route can see the other. Which of
the two is the answer is decidable from the strings themselves: the qualified
one names a technique, the bare one is that technique with its qualifier
dropped.

**From the strings, and from nothing else.** The obvious implementation is to
ask the wiki's alias table whether two names resolve to one page. That was
written, measured and reverted -- do not rebuild it: the alias table is
one-to-many, `divine dog` names both
`Divine Dogs` and `Divine Dog: Totality`, and collapsing on it merged two
distinct shikigami. A scorer that reports a better number by being wrong is
worse than no change at all.

So this module never consults an alias table, and it never merges two names
that are both qualified. `Divine Dogs` is not the suffix of
`Divine Dog: Totality` -- one is a plural, the other a named form -- so rule 1
does not reach them and both survive. `tests/test_dedupe.py` asserts that pair
directly, and it is the test that matters most here: everything else in this
file trades recall for precision, and that one stops the trade going too far.

The rules, in order:

1. A name that is exactly the **suffix** after a `: ` in another name is that
   name with its qualifier removed. Drop it, keep the qualified one.
2. Comparison folds case, collapses whitespace and ignores apostrophes, so
   `Jacob's Ladder` and `Jacobs Ladder` are one name.
3. A non-empty set never comes back empty. The same guarantee
   `roster.apply_constraints` gives, for the same reason: a list that is
   visibly too long is more useful than a blank one.
4. `kept` is in input order, so whatever ordered the roster still orders it.
5. Two names that cover each other keep the longer; a tie keeps the first.

**The prefix is not a rule, and the symmetry is a trap.** This module was first
written with a second rule -- a name equal to the *prefix* before a `: ` is the
container the specific form was filed under, so drop it too -- which reads as
the natural mirror of rule 1. Measured against every page title on the Jujutsu
Kaisen wiki, it fires on eight pairs and is wrong on all eight:

    Cursed Womb                 vs  Cursed Womb: Death Painting
    Jujutsu Kaisen              vs  Jujutsu Kaisen: Phantom Parade  (and 4 more)
    Satoru Gojo vs. Sukuna      vs  Satoru Gojo vs. Sukuna: First Fight
    Satoru Gojo vs. Toji Fushiguro  vs  ...: Rematch

None of those is a restatement. `Cursed Womb: Death Painting` is a kind of
cursed womb, not the same entity said longer, and it is the subject of a
question the bank scores exactly today. A first fight and a rematch are two
battles. Over the same titles rule 1 fires zero times, which is the tell: the
bare *suffix* is almost never a page of its own, it is a short name that
reaches a roster out of prose or a category, while the bare *prefix* usually is
a page, because it is a real and different thing.

The asymmetry has a reason. When a wiki titles something `X: Y`, `Y` is the
thing's own name and `X` says which family it belongs to, so dropping `Y` loses
nothing and dropping `X` deletes the family. `Nue` and
`Nue: Totality - Merged Beast Agito` are a shikigami and a fusion of it, both
real, both gold; the prefix rule deleted the first.

That leaves rule 5 a formality rather than a live path, and it is worth saying
which. Coverage under rule 1 always makes the covered name strictly shorter, so
mutual coverage can only happen between names that normalise to the same string
-- exact duplicates in different casing or spacing. The rule is written out
anyway because it costs nothing, and because assuming an invariant here is how
both of this module's predecessors went wrong.
"""

from __future__ import annotations

from collections.abc import Sequence

# The separator the wikis actually use. A colon with no space after it is not
# one: `Blue:Red` is not a qualified form, and a rule that split on the bare
# character would start reading times, ratios and namespace prefixes as
# qualifiers.
_SEPARATOR = ": "

# Both apostrophes, because a crawled title carries the typographic one and a
# hand-written `members:` list carries the straight one. Removing them outright
# rather than mapping one to the other also folds `Jacobs` onto `Jacob's`,
# which is the difference measured between the bank's spelling of
# `Jacob's Ladder` and the qualified page that covers it.
_APOSTROPHES = ("'", "’")


def normalise(name: str | None) -> str:
    """The form two names are compared in: folded, collapsed, apostrophe-free.

    Not a general-purpose fold. It deliberately does not stem or singularise:
    `Divine Dogs` and `Divine Dog` differ by one letter and are two different
    shikigami, and any normalisation that closed that gap would re-create the
    exact merge this module exists to avoid.
    """
    folded = name or ""
    for mark in _APOSTROPHES:
        folded = folded.replace(mark, "")
    return " ".join(folded.lower().split())


def _fragments(normalised: str) -> tuple[set[str], set[str]]:
    """`(prefixes, suffixes)` around every `: ` in an already-normalised name.

    Every separator, not just the first: `Maximum Technique: Hollow Technique:
    Purple` has two, and a name equal to a *suffix* of either one is the same
    technique said shorter. Empty sides are dropped so a trailing colon cannot
    make every name in the set a match for nothing.

    Prefixes are returned because they are what the module docstring's
    refutation is about and a reader checking that claim needs to see them,
    but `collapse_variants` deliberately never drops on one: measured over
    every Jujutsu Kaisen page title, a bare prefix is a real and different
    entity eight times out of eight.
    """
    parts = normalised.split(_SEPARATOR)
    prefixes: set[str] = set()
    suffixes: set[str] = set()
    for cut in range(1, len(parts)):
        head = _SEPARATOR.join(parts[:cut]).strip()
        tail = _SEPARATOR.join(parts[cut:]).strip()
        if head:
            prefixes.add(head)
        if tail:
            suffixes.add(tail)
    return prefixes, suffixes


def collapse_variants(
    names: Sequence[str],
) -> tuple[list[str], list[dict[str, str]]]:
    """Return (kept, dropped) where dropped records name + the variant that covers it.

    `dropped` is diagnostic on purpose, in the same shape as
    `Roster.rejected`: a member vanishing from an answer with no reason
    attached is how a list of 160 quietly became a list of 150. Each entry
    carries the name, the surviving name that covers it, and which rule fired
    (`suffix`, `prefix` or `duplicate`).
    """
    originals = list(names)
    if len(originals) < 2:
        # Nothing to compare against, and rule 4 would hand a single name back
        # anyway. Taken early so a lone `Blue` -- a bare base with no qualified
        # form present -- is never treated as a restatement of something.
        return originals, []

    normalised = [normalise(name) for name in originals]

    # Who covers whom. Recorded in both directions before anything is dropped,
    # because rule 6 cannot be applied without knowing whether the coverage is
    # returned.
    coverers: list[list[tuple[int, str]]] = [[] for _ in originals]
    covers: list[set[int]] = [set() for _ in originals]
    for outer, qualified in enumerate(normalised):
        _prefixes, suffixes = _fragments(qualified)
        for inner, bare in enumerate(normalised):
            if inner == outer or not bare:
                continue
            if bare in suffixes:
                rule = "suffix"
            elif bare == qualified:
                rule = "duplicate"
            else:
                # Deliberately not `bare in _prefixes`. See the refutation in
                # the module docstring: that rule deletes `Cursed Womb`,
                # `Nue` and `Satoru Gojo vs. Sukuna`, all of them real.
                continue
            coverers[inner].append((outer, rule))
            covers[outer].add(inner)

    def outranks(outer: int, inner: int) -> bool:
        """Whether `outer` may drop `inner`, deciding mutual coverage."""
        if inner not in covers[inner] and outer not in covers[inner]:
            return True                       # one-way: the coverer wins
        if len(normalised[outer]) != len(normalised[inner]):
            return len(normalised[outer]) > len(normalised[inner])
        return outer < inner                  # a tie keeps the first

    dropped_by: dict[int, list[tuple[int, str]]] = {}
    for inner, found in enumerate(coverers):
        winners = [(outer, rule) for outer, rule in found if outranks(outer, inner)]
        if winners:
            dropped_by[inner] = winners

    kept = [name for index, name in enumerate(originals) if index not in dropped_by]

    # Rule 4. Unreachable by construction -- the longest name in a set can only
    # be covered by a duplicate of itself, and the tie-break keeps the first of
    # those -- and kept regardless, because `apply_constraints` learned this
    # the expensive way and an invariant nobody checks is an invariant that
    # eventually stops holding.
    if not kept:
        return originals, []

    dropped: list[dict[str, str]] = []
    for inner in sorted(dropped_by):
        winners = dropped_by[inner]
        # Attribute the drop to a name the caller can still see. Where a chain
        # collapsed -- `Purple` covered by `Hollow Technique: Purple`, itself
        # covered by something longer -- naming the survivor is the only
        # explanation that reads.
        outer, rule = next(
            ((o, r) for o, r in winners if o not in dropped_by), winners[0]
        )
        dropped.append(
            {
                "name": originals[inner],
                "covered_by": originals[outer],
                "rule": rule,
            }
        )
    return kept, dropped

"""Do this series' declarations contradict its own bank?

`ability_stopwords` says "this is nobody's ability". The bank's gold says what a
researched answer contains. When the same name appears in both, one of them is
wrong, and the engine is being told to throw away a thing it is then marked down
for missing.

That is not hypothetical. On 2026-08-15 eight names were in both:

    onepiece  armament haki, observation haki, supreme king haki, and the
              busoshoku / kenbunshoku / haoshoku / conqueror's romanisations
              of the same three          gold across 4 character questions
    jjk       cursed energy manipulation gold for Yuji, Gojo and Sukuna

Removing them took `Every ability of Roronoa Zoro` from 7/10 to 10/10 and
`Every ability of Monkey D. Luffy` from 0/3 to 3/3. Nothing in the test suite
could have caught it: both files were internally valid, and only comparing them
shows the disagreement.

`ability_headings` is checked the other way. It exists to exempt a heading from
`_drop_templates`, so anything declared there should be a name the bank actually
wants -- an entry nothing asks for is a precision cost on every character
carrying that heading, paid for nothing.

Run after touching either list, or after any bank expansion:

    python -m scriptengine.eval.audit_declarations

Exits non-zero when a stopword is also gold, so it can gate a run.
"""

from __future__ import annotations

import sys

from scriptengine.config import load_overrides, series_paths
from scriptengine.eval import questions as bank
from scriptengine.retrieve.roster import ability_headings, ability_stopwords

SERIES = ("berserk", "bleach", "csm", "db", "hxh", "jjk", "onepiece", "opm")


def gold_names(series: str) -> dict[str, set[str]]:
    """Every gold item and alias in this series' set questions -> question ids."""
    out: dict[str, set[str]] = {}
    for question in bank.load_bank(series).questions:
        if question.kind != "set":
            continue
        for answer in question.answer:
            for name in (answer.item, *answer.aliases):
                key = name.strip().lower()
                if key:
                    out.setdefault(key, set()).add(question.id)
    return out


def main() -> int:
    contradictions = 0
    unused = 0
    for series in SERIES:
        gold = gold_names(series)
        overrides = load_overrides(series_paths(series))

        clashes = sorted(w for w in ability_stopwords(overrides) if w in gold)
        if clashes:
            contradictions += len(clashes)
            print(f"\n[{series}] declared NOT an ability, but gold ({len(clashes)}):")
            for word in clashes:
                print(f"    {word:38} gold in {sorted(gold[word])}")

        # The positive list, checked for entries nothing asks for.
        idle = sorted(h for h in ability_headings(overrides) if h not in gold)
        if idle:
            unused += len(idle)
            print(f"  [{series}] ability_headings nothing asks for ({len(idle)}): {idle}")

    print(f"\ncontradictions: {contradictions}   idle headings: {unused}")
    if contradictions:
        print("A stopword that is also gold makes the engine wrong on purpose.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

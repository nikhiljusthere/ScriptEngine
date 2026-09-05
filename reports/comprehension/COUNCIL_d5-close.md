# Council — D5-close (scope of the `Chapter 239 → References` index miss)

Step: D5-close (last-bucket item 1 of 2, before the cross-corpus pass).
Protocol: 5 advisors → anonymise A–E → 5 peer reviews → synthesize (per the
`llm-council` skill; advisors and reviewers each ran as a parallel batch of 5).

## The question

Close D5 (the 2 unreachable JJK `Chapter 239 → References` trivia sentences) at
the right scope, without breaking the 7 other indexed wikis. Three altitudes:

- **A** — remove `references` from the engine-global `BOILERPLATE_SECTIONS` (one line, all 8 wikis, shared by 3–4 consumers).
- **B** — document the 2 lines as a wiki anomaly (line-level allowlist; target = 0 *unexpected* misses).
- **C** — a per-wiki, wiki-keyed section-policy that the chunker consumes (oracle alignment across corpora is the cross-corpus pass).

## What the council established (verified against code/DB)

- JJK span-recall is **48,570/48,572** (2 misses, both `Ch.239/References`). The
  oracle (`span_recall.py:72` `BOILERPLATE`) already *excludes* `references`
  (comment `:70`: "on chapter pages it carries real trivia prose"), and
  `tests/test_span_recall.py:53` hard-locks `is_boilerplate("References") == False`.
  So the **only** way to hit 0-miss **and** keep 48,572 is to make JJK's
  References **chunked (content)**; the oracle is left untouched. (This refutes
  the advisor claim that the per-wiki-oracle option "drops the denominator" —
  that is only true if you add `references` to JJK's oracle, which is the wrong
  direction; the per-wiki *oracle* change only ever touches the other 7 wikis.)
- The chunker (`chunker.py:71`) and the oracle (`span_recall.py:72`) encode **two
  different properties** (a skip-policy and a deliberately-stricter content-policy
  canary). Collapsing the oracle into the chunker's skip policy would make the
  oracle a tautology that can never flag a gap again. Keep the properties distinct.
- JJK has **556** `References` sections, **555 empty** (`word_count=0`), **1
  non-empty** (Ch.239, the 2 miss sentences). The other 7 wikis have NON-empty
  `References` (footnote lists): db 498, berserk 99, hxh 212, onepiece 127,
  bleach 29, opm 19, csm 2. An engine-global removal re-chunks all of them on a
  re-index — a regression.
- `BOILERPLATE_SECTIONS` is shared by **four** consumers: `chunker.py:293`,
  `roster.py:4385` (`_member_prose`), `export.py:160` (`_write_document`).
- The 555 empty JJK References must not yield empty chunks: the `word_count == 0`
  guard (`chunker.py:303`) is a *separate* skip from the title skip, so removing
  `references` from the title-skip set still drops the empties.

## Advisor positions (anonymised)

| | position |
|---|---|
| A (Executor) | B-now via a per-wiki keep-section override on the chunker; A is a landmine; landmine-check the other 7 offline. (Mistook the per-wiki oracle change for the JJK gate.) |
| B (Contrarian) | it's a wiki anomaly → line-level allowlist, target 0 *unexpected* misses, engine untouched. |
| C (First Principles) | the real bug is the two divergent copies; collapse to one wiki-keyed source consumed by chunker **and** oracle. |
| D (Expansionist) | the oracle is the product; make span-recall a standing per-wiki gate; one `sections:` policy block; D5 is the entry to a cross-corpus pass. |
| E (Outsider) | the confusion is the duplication; JJK-specific logic in global `.py` is the anti-pattern; do B's data mechanism with C's architecture (one function → chunker + oracle). |

## Peer-review findings (what the advisors missed)

- **4 of 5 ranked E strongest** (names the empty-chunk invariant; no series name in `.py`).
- **B (the anomaly option) is out**: it whitelists a deliberate canary, encodes
  literal line text (breaks on any wiki edit), and breaks the every-line-reachable
  invariant (bleach already carries References misses under the same canary).
- **The gate number is a measurement, not a constant**: re-baseline the
  denominator post-fix (it should *stay* 48,572 for JJK).
- **Do not make the oracle a tautology** of the chunker; keep skip-policy vs
  content-policy distinct.
- A **regression test** should pin the chunker/oracle section-policy agreement so
  the drift cannot silently recur; define the pytest gate as "green (post-fix
  total)", not exactly 1,166.
- Verify the parser actually emits the title `references` for JJK References
  (it does: 556 rows titled `References`).

## Verdict

**Close D5 with the per-wiki override on the chunker (B's data mechanism, C's
architecture, kept JJK-local).** Concretely:

1. `series/jjk/overrides.yaml`: new flat key `content_sections: [references]`
   ("section titles this wiki treats as content even though the engine default
   would skip them").
2. `scriptengine/index/chunker.py`: add `effective_boilerplate_sections(overrides)`
   = `BOILERPLATE_SECTIONS - {content_sections}`; give `chunk_page` a
   keyword-only `boilerplate: set[str] | None = None` param (default = global).
3. `scriptengine/index/build.py`: compute the effective set from `overrides` and
   pass it to `chunk_page(page, boilerplate=effective)`.
4. Regression test: jjk effective set excludes `references` (Ch.239 References
   chunked); a wiki without the key is unchanged (still boilerplate).
5. Re-index jjk (`--no-embed`); verify span-recall **0-miss + 48,572**, pytest
   green (post-fix total), eval 24/24.

**Deferred to the cross-corpus pass (the last TODO, added to the Phase plan):**

- Route `roster._member_prose` + `export._write_document` through the same
  `effective_boilerplate_sections` helper (today they still use the raw global
  set — a documented, wiki-scoped divergence, not a silent one).
- Align the span-recall **oracle's** per-wiki content-policy with the chunker's
  per-wiki skip-policy across the other 7 wikis (where the oracle expects
  `References` the chunker skips — db/berserk/bleach likely already red). Keep
  the oracle the stricter canary.

**Rejected:** A (engine-global — cross-corpus regression landmine); the anomaly
line-allowlist (breaks the canary + invariant).
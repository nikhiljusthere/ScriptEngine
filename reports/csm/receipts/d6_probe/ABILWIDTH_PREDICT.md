# ABILWIDTH leg — PRE-REGISTRATION (written BEFORE the change)

Q7/Q8 proved pool-140/358 flip under beam top_k=30 (gold ranks
12/19), while global-30 was killed for counter-flips and tiered
cannot reach them (saturated bundles, leftover ~0). Narrow vehicle:
raise top_k 8→30 ONLY for possessive-owner-with-declared-ability
queries, reusing the `_owner_attribute_hit` predicate already live
for derivation deferral (pool-140 "Falling Devil's Body Control"
HITs; org-06 "Denji's story" does not; vol-10/arcn/state rows have
no possessive-ability pair and are untouched).

## Change (3 lines in `_qa_context`, behind no new flag — the
## predicate itself scopes blast radius; rollback = revert hunk)

After subject derivation, before retrieval: if
`_owner_attribute_hit(store, query)` — needs a store handle; reuse
the later FactStore block ordering carefully (open briefly, as
`_story_page_subject` does) — set `top_k = 30` (override caller
default ONLY; explicit caller top_k respected).

## Predictions (ALL must hold)

- pool-140 flips RED→GREEN; pool-358 flips RED→GREEN.
- 0 counter-flips on 486 (esp. pool-237/149/166/252 + abl-04/05/06
  + org-06 hold — ability/org rows sharing the trigger space).
- Blind 19/19. eval-jjk 31/31 (co-located). OOS floor holds.
  green30 clean. p50 latency noted (top_k=30 rerank cost only on
  trigger queries).

## KILL (any breach → revert hunk, keep derivation+Q1+spike)

<2 flips, any counter-flip, any guard breach. Fallback if killed:
class-scoped top_k by question class (possessive-ability +
ability-pool class), then per-row triage.

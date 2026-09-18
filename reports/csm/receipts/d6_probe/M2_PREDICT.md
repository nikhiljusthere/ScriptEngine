# M2 Stage-1 probe — PRE-REGISTRATION (written BEFORE the code change)

Chair (D7a council): Stage 1 = M2 alone on 5 rows; WIN = 5/5 flip;
KILL = any counter-flip bank-wide, blind <19/19, eval-jjk <31/31
co-located, or latency/cost regression. Breach rolls back M2 alone.

## Change (one line + comment, stores/facts.py passages_for_subject)

Level filter `(0, 2)` → `(0, 1, 2)`: level-1 section chunks join the
R6 floor. Layer-localization (in-process HybridRetriever + FactStore,
no caller subject): for all 5 rows the all-terms gold chunk is ABSENT
from the top-50 shortlist AND the floor, while partial-term children
sit at shortlist ranks 12–47 / floor positions 3–78. The floor's own
contract (R6: the authored page's text is served whether or not any
passage outranks the corpus) is violated for L1 section text. Cap +
budget walk bound the cost (F2b); the `_cap_sections` key counts L1/L2
of a section together, so this mostly substitutes the head for the
tail child, not pure addition.

## Predictions (all must hold; else per map)

- 5/5 flip RED→GREEN: csm-dim-org-03, csm-dim-org-05,
  csm-dim-vol-10, csm-abl-pool-140, csm-abl-pool-358.
- 0 counter-flips on the full 486 bank.
- Blind fresh set stays 19/19.
- eval-jjk stays 31/31 (co-located, `:8000` down).
- chap-01 + org-06 stay RED (not their mechanism; a flip there is
  investigated, not celebrated).

## Falsification map

- <5 flips → floor depth insufficient (beam-side cut or budget-cut
  deeper than the floor; escalate to beam/budget layer).
- Any counter-flip → ROLLBACK M2 alone (mechanism unsafe).
- Blind <19/19 or eval <31/31 → ROLLBACK (regression).
- Measurement: full-bank p23 + blind + eval-jjk, co-located
  (`:8000` down, Qwen 65k up, one model holder), then gates only if
  Stage 1 wins (D7c whole-card official suite).

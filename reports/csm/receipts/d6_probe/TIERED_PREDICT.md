# TIERED-append leg — PRE-REGISTRATION (written BEFORE the change)

Chair order (width council): tiered experiment behind flag after
Step-0 leftover mixed result (median 1104; 17/36 ≥1500 leftover;
saturated ~25% get nothing — recorded, not contested).

## Change (flagged, hybrid search + bundle walk)

- Flag: `SCRIPTENGINE_TIERED_RECALL=1` (default OFF = byte-identical
  current behavior; kill = unset, no revert commit).
- Tier-1: TODAY's exact computation untouched (shortlist-32 →
  rerank → top-8 → floor → budget walk, same order).
- Tier-2 (flag on only): second identical search at top_k=30;
  take its passages EXCLUDING tier-1 chunk_ids AND floor chunk_ids,
  in r2 order; append to the walk ONLY while token budget remains
  (genuinely-unused-budget-only; zero leftover ⇒ zero added).
- Latency: second retrieval+rerank timed per call, reported p50.

## Predictions (ALL must hold)

- arcn-02, arcn-10, state-08, org-03 flip RED→GREEN (high-leftover
  rows: 2018/2184/2621/3765 tokens of room).
- arcn-06 (1072), arcn-08 (853): recorded (marginal room; either way
  consistent — NOT counted as miss if red).
- Saturated rows (pool-140/358, abl-01/02/09, state-02/09,
  caus-03): stay RED (no room by construction — class-scoped width
  leg owns them, separately).
- 0 counter-flips on 486; blind 19/19; eval 31/31; OOS floor;
  green30 clean.
- p50 added latency reported (no cap asserted pre-measurement;
  council prices it after).

## KILL (any breach → flag off, no revert commit needed)

<4 of (arcn-02, arcn-10, state-08, org-03) flipping; any
counter-flip; blind/eval/green30/OOS breach. arcn-06/08 outcomes
do not kill either way (marginal-room honesty).

# WIDTH ship leg — PRE-REGISTRATION (written BEFORE the change)

Chair order (program council Step 2): ship decision on measured k*.
Dose result: k* = 30 (thresholds 12×4, 16×2, 20×6, 24×2, 30×2 —
classes interleave, so class-scoping buys nothing over global;
latency flat 0.52→0.65s/call, no blowout).

## Change (one number, config.py)

`final_top_k: int = 8` → `30`. Single default consumed only by
`HybridRetriever.search` when callers pass no top_k. All tests pass
explicit top_k (unaffected). Latency priced: rerank pairs 8→30 at
flat measured per-call cost; token budget walk unchanged (6000).

## Predictions (ALL must hold)

- The 16 dose rows flip RED→GREEN (total 465 → 481/486).
- chap-01 + arcn-07 hold GREEN (Q1 floor intact).
- abl-04/05 hold GREEN.
- 0 other moves (no counter-flips, no surprise flips beyond the 16
  — any unlisted flip is investigated, not celebrated).
- Blind fresh set stays 19/19.
- eval-jjk stays 31/31 (co-located, `:8000` down).
- OOS floor holds (≥166, report vs 192); green30 zero flips.

## KILL (any breach → revert the one number, go class-scoped)

Any counter-flip, blind <19/19, eval <31/31, OOS below floor,
green30 flip, or <14/16 dose rows flipping.

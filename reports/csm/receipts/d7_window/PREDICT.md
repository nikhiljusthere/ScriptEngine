# D7 window pre-window predictions

Timestamped `2026-09-18 17:32 IST`, before the kill-window chain runs.
Baseline = git-HEAD `20d6da4e` 469-era census (469 green / 17 red; oos200
194/200). Counter-flip baseline for every leg = that 469-era census
(`snapshots/census_head_469.jsonl`).

## Per-leg predictions (Q4 bars)

- **Leg A** (`SCRIPTENGINE_TIERED_RECALL=1`, ABILWIDTH=0): W ≥ 469 with flips
  ⊇ {csm-dim-arcn-02, csm-dim-arcn-10, csm-dim-org-03, csm-dim-state-08};
  0 counter-flips; blind 19/19; d6_flip rc 0. TIERED only appends tier-2 from
  leftover budget, so it is expected to hold the 469-era greens (no
  counter-flips) while lifting the four arc/org/state D7 holdout rows.
- **Leg B** (`SCRIPTENGINE_ABILWIDTH_RECALL=1`, TIERED=0): W ≥ 469 with flips
  ⊇ {csm-abl-pool-140, csm-abl-pool-358}; 0 counter-flips; blind 19/19;
  d6_flip rc 0. The possessive-owner beam widening (top_k 8→30) is expected to
  reach the Falling-Devil body-control / Yoru building-sword golds (ranks
  12–47, cut at 8). **Watch item:** the pre-window worktree census shows
  pool-149/252 red under a width-style re-measure — if the live Leg B grading
  also turns those two 469-era greens red, Leg B correctly reports RED on
  counter-flips and the chain halts (the designed stop, not a defect).
- **Leg C** (both on): W ≥ 469 with flips ⊇ {arcn-02, arcn-10, org-03,
  state-08, pool-140, pool-358}; 0 counter-flips; blind 19/19; d6_flip rc 0.

Floor re-count (C5 record line, printed per leg): which of the 16 Phase-2
floor rows (= the 17 git-HEAD p23 reds minus the org-03 D7 holdout) flip green
under each leg.

## Q2 flag-fix line

Q7/Q8 evidence carries over: the `_owner_attribute_hit` predicate is
unchanged; a gate was added (`_abilwidth_enabled()`), and flag-off is
committed-tree behavior, verified by the flag-off gate run (deviation (c)).

## Standing gates (flags OFF)

pytest 1,331 pin · eval jjk 31/31 · span-recall jjk 48,572 offline rc 0 +
400 probes ≥ prior baseline · canon opm ≥ 10/16 · 236/236 · 79.0%.
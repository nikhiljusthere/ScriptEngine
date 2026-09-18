# DOSE-RESPONSE probe — PRE-REGISTRATION (written BEFORE the run)

Chair order (program council): grade the 16 width-rows at top_k in
{8,12,16,20,24,30}, subject=None, fixed tree, fixed device (cuda),
and find minimal k* with 16/16 flipped. Ship nothing, VOID nothing
until k* is measured.

Rows (16: Q7 5 + Q8 11): csm-dim-org-03, csm-dim-org-05,
csm-dim-org-06, csm-abl-pool-140, csm-abl-pool-358, csm-dim-arcn-02,
csm-dim-arcn-06, csm-dim-arcn-08, csm-dim-arcn-10, csm-dim-state-02,
csm-dim-state-08, csm-dim-state-09, csm-dim-abl-01, csm-dim-abl-02,
csm-dim-abl-09, csm-dim-caus-03.
Tree fingerprint recorded at run (HEAD + status + diff stat).
Latency per k recorded (mean seconds per call).

## Prediction (calibration, not pass/fail)

- k=8: 0/16 (all currently red at product default — sanity).
- k=12: pool-140 flips (gold rank 12 measured); others mostly red.
- k=16–20: majority flip.
- k*=30 guess (conservative): 16/16. Smaller k* is a welcome
  surprise, not a miss.

## WIN / KILL (binding)

- WIN: a measured minimal k* with 16/16 flipped + full latency
  curve + zero errors. (Ship decision comes AFTER, per Step-2
  gate rule — this probe ships nothing.)
- KILL: no k in {8..30} flips 16/16 ⇒ kill global-width; drop to
  class-scoped width design and re-propose.
- Falsification: verdicts at k=30 must reproduce Q7/Q8
  row-for-row; any mismatch re-opens nondeterminism audit.

# The Contrarian — CSM Unit 3 sweep device fork

**A's fatal flaw: it inverts the owner's order and pays for a stale measurement.**
The 150k→100k switch is *reserved for Phase 2* by the owner-directed plan
("not used per-step in Phase 1"); triggering it mid-Phase-1 to get `:8000` on
CUDA is a plan violation, not a workaround. Worse, the D6 extraction gate is
now LIVE (structural dims red), so a pre-extraction exhaustive 17,009-row qa
sweep measures a floor that extraction will raise — and CSM-4 (Phase 2, 100k)
re-sweeps the same qa door ×3 doors. A spends 5–25 h (rate unmeasured; the
only on-disk 168-probe datapoint was **CUDA@100k**, not CPU — the brief's
"168/bounded-run" figure is misattributed to CPU) plus two 30–60 s switch
windows, measuring a state we re-measure anyway. A is dominated.

**B is strictly worse.** ~102 runs (or ~28 if CPU is the 1200-s incident's
1–2 s/probe) of A-flagged 15-min CPU runs = 26+ h (or 7 h) of babysitting on a
CPU service, for the same stale pre-extraction state. No case.

**C wins — it is the only option in the owner's intended order** (sample → fix
one class → targeted grade → exhaustive at Phase 2). The miss queue is already
well-specified: the four frozen inputs (twenty-failures 20, red list 5,
door-census reds, dim-census reds) + a 400-row sample (~16 misses at the real
~4% per-probe rate — the "0.9%" in the pre-step is the completion-weighted
161/17,181, *not* a per-probe rate).

**C's one real gap:** with the exhaustive sweep deferred, the halt rule ("miss
regression / two no-reduction iterations") has no stable denominator. Fix it by
pinning the halt metric to a **fixed 400-row grading subset** (re-probed after
each fix), not the moving full panel — otherwise iteration 1 cannot halt
cleanly.

**On-disk flag before the council records it:** work_log says "49/60 mech-green"
but the raw census file is **39/60** MECH_GREEN (21 RED). The 5.4 gate-LIVE
verdict survives (the three structural reds are red either way), but the number
on record is off by 10 rows (causality 9/10 + appearance 9/10 not counted).

OPTION: C (variant: C + a fixed 400-row halt metric) / FIRST STEP: at 150k, no switch — confirm `:8000` is the CPU service (pid 4510), then run the CSM qa-door 400-row sample (`span-recall --series csm --panel panel_csm.json --door qa --sanity 400`) as one bounded A-LONG-flagged CPU run and assemble the pre-triaged miss queue from its misses + the four frozen inputs, pinning the 400-row halt metric / CHANGE-OF-MIND IF: (a) a measured CUDA@100k rate does the full 17k in <~1 h (making A's switch cost small enough that the earlier, more complete miss list wins), or (b) the 400-sample + frozen inputs cannot enumerate the MISS_DOC/MISS_SPAN classes (all 400 misses one class, census reds point to an unseen class), forcing a larger pre-fix sweep.
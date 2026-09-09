# Phase-1 close gate — the checker/reviewer (2026-09-09, owner: "prepare a
checking/reviewer that will check the phase 1's end, then only will move to
phase 2"; mechanism decided by the directing session per owner delegation)

## The rule

**Phase 2 may start only on a PASS here. The `PHASE_A_COMPLETE` marker is
necessary but NOT sufficient** — the marker proves B's close conditions
held at write time; this gate proves the committed state holds NOW. A
regressed queue, a stale gate, or a missing close condition = FAIL → the
council halt path (plan v2.2 A20: no marker, no Phase 2), never a silent
slip into Phase 2.

## When it runs

B writes `PHASE_A_COMPLETE <ts>` (floor only) + the final work_log line
("PHASE 1 COMPLETE — awaiting the phase-close reviewer") and stops. The
**directing session** then deploys the reviewer (one subagent, fresh
context, its own receipt file; in the bay, A supervises the reviewer's
gate shells the same way it supervises B's — GPU-only rule applies).

## The reviewer's checklist (each item: raw evidence on disk)

1. **Marker + floor:** `reports/master-work/phase_status.txt` carries
   `PHASE_A_COMPLETE <ts>`; the miss queue (`reports/csm/
   miss_queue_csm_iter1.jsonl`) is at its documented floor — the 33
   fixable rows closed/green (30 open + 3 closed by R-1), 22 floors
   documented, 3 stamped; **any regression since the marker = FAIL
   (regression is a council state, not a floor — A20).**
2. **The four standing gates RE-RUN on the current tree** (baseline-exact
   vs the named re-baseline, plan process §6 / `GATE_REBASELINE_2`):
   pytest **1,303+2xp = 1,305 collected, 0 failed** · eval jjk **31/31** ·
   span-recall **48,572/48,572 offline + ≥ 390/400 live probe (97.5 %)** ·
   canon opm **236/236 @ 79.0 %** (opm-set-16 pre-registration live).
   One-copy ordering (server down for in-process CUDA legs; up on CUDA for
   the HTTP legs; A executes `:8000` stops/restarts per B's signals).
3. **P1.4 close conditions (A12) on disk:** (a) campaign-todos section
   synced; (b) the C3 doc-hygiene commit landed; (c) the
   `reports/csm/GATE.md` skeleton exists; (d) the P2.2 model-free bar
   audit (3–5 pre-registered cases per census class + owner-accepted
   residual cap, fresh-context author, mechanical grading) ran BEFORE the
   marker and its verdict is on disk; (e) the R-6 floor-inheritance
   verdict (from the R-5 council) is recorded.
4. **Commit state:** C1/C2/C3 + the ledger-of-record v1 committed
   (`git log`); the CSM paths git-clean (`git status`); the 9-file R-2/R-3
   package is IN C1 (no longer uncommitted); `git add .` was never used
   (the dirty-tree contaminants — `E:\Personal\Plot Works/`, `sample
   scripts/`, stale `STOP` — are absent from every CSM commit).
5. **The R-5 wave's record:** council record + ledger row on disk; the
   R5-meter re-sweep (own-new-row HIT ≥ 1 + JJK/OPM invariant pins)
   green; R-6/R-7 no-council passes + receipts.
6. **JJK-100 % invariant:** item 2 IS the invariant check — every engine
   change in Phase 1 left the JJK gates baseline-exact.

## The verdict (the reviewer's output)

`reports/csm/receipts/phase1_close_review.md`: **PASS** (all 6 green,
raw numbers per item) or **FAIL** (which item, the evidence, the halt
path: regression → council, no Phase 2; missing condition → the named fix
+ re-run of this gate). PASS → the directing session reports to the owner;
**Phase 2 (plan v2.2 P2.1 step 0 — the per-door sanity-100) starts only
after the owner's go** (the owner gates the phase boundary; the reviewer
gates the evidence).

## Why this shape (decision record)

The owner wants "everything to be right" at the phase boundary. The
marker is B's claim; the reviewer is the independent check (fresh
context, never saw B's work, verifies disk + re-runs the gates). It is a
ONE-SHOT gate (not a standing council) — the council trigger for a phase
close is already the P6/close point in plan process §1; this reviewer is
the evidence step that makes "Phase 1 is 100 % complete" a checkable
statement, in the campaign's standing sense (raw receipts, never prose).
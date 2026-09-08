# Advisor 5 — The Executor (CSM-3b close)

**Close CSM-3b today — <30 min, zero GPU.** All four standing gates sit at
re-baseline, the seed bank shows zero new FAILs, and R1/R7 are verified
landed (f93d396 + bc73795, roster-door test in the suite). Reopening without
a new failure buys nothing; the close-out is just the council verdict + the
COUNCIL_HISTORY line + the SWITCHPOINT 3b line.

**F1 is the critical-path trap — fix before Phase 2. Cost: one subagent
hour, zero GPU.** The 17,181 × 3-door exhaustive sweep is the campaign's
critical path (≈8–17 GPU-hours at the measured 0.49 s/probe CUDA rate; the
plan's 51 h is an unmeasured JJK figure per CSM-3's chairman), and F1
guarantees it: every cross-panel run unlinks the other panel's sidecar — it
already fired once (168 rows dropped from disk). The git-recovery workaround
costs nothing today but arms the trap at every Phase-2 panel switch; whoever
trips it mid-sweep loses hours of GPU probes and a recovery trick that isn't
written down. Concrete first step: key the ledger pair by the 8-char panel
hash (`sweep_<hash8>.jsonl` + `.new`) in `span_recall.py` resume/merge —
~30-line diff + one test, and restore the 168 rows into the pinned-keyed
ledger. Run it as a small pre-step of Wave 2 (sequential, *before* the two
parallel Wave-2 subagents — the wave cap is on parallel subagents, not
prep work) and it must land before the Phase-2 400-probe standing gate.
Verification cost: pytest 1,254 in-process CUDA (~3 min, one-copy ordering)
+ probe-400 (~3.5 min HTTP).

**Do not pull G-CSM-1/2 forward.** The CSM-5 remainder (5.3–5.5 + the
20-failure set) is exactly the slot that consumes them, and Wave 2 is
already at the two-subagent cap. F2: leave `gold_csm.json` absent — zero
cost; revisit at CSM-4 only if an eval-harness csm bank becomes needed. F3:
A already ruled the monitor fix; nothing for me to do.

**GPU budget this week:** Wave 2 is zero-GPU (CSM-6 explicitly no-extraction;
CSM-5 zero-GPU except the conditional 5.4 extraction, which fires only on a
red dimension census). The only GPU-hour block is the F1 verification
(~7 min) plus the exhaustive sweep itself (~8–17 GPU-hours, batched in a
tier-2 side session via the gpu-handoff chain, 100k dial, one-copy).
Everything else fits the 15 s CPU rule.
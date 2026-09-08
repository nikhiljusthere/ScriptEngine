# COUNCIL: GPU handoff workflow (2026-09-08)

llm-council run `0204d37f` (5 advisors → 5 peer reviewers → chairman, all on
local Qwen 27B; 11/11 children completed). Owner's question: is the proposed
A→B→C→D cross-session GPU-handoff design sound, and is there a better one?

## Question (abridged)

A (pi, full 262k, campaign terminal, idle at prompt) hits a GPU step →
checkpoint + handoff plan → B (new terminal, switchpoint → 100k) → C (new
terminal, fresh 100k pi, runs the GPU task + report) → D (new terminal,
switch back to 262k) → resume line typed into A's window (no vision).
Intermediate sessions deleted; A sees only work chat, stops at checkpoint,
continues. Pressure-test: can B be plain shell? Can D be eliminated? Who types
the resume (shell watcher vs MASTER_WORK poller)? What breaks in the 30–60 s
model-less windows? Qwen dies mid-task? Return-to-A determinism? Hygiene?

## Advisors (one line each)

- **Contrarian:** the design has a success path and no failure path — every
  failure mode is silent (watcher only fires on success). The 262k-declared-vs-
  100k-live window turns any stray keystroke into a lossy auto-compact; the
  type-gate must verify live 262k, not just "report exists". Title-based
  re-resolution, STALLED flag, liveness restart.
- **First principles:** terminals B/D are theatre; the mode dial and the GPU
  job are machine properties, not agent properties. Collapse the chain to
  A + one setsid shell chain; C only needs pi if the step needs judgment.
  Fit guard must take an explicit reference, never "newest file".
- **Expansionist:** the real win is the **queue** — N GPU steps per 100k round
  trip; the resume line is a disk artifact (xdotool is just the fast path).
- **Outsider:** "B's turn dies mid-switch" is a fake problem — B needs no pi
  at all (B-as-pi is a curse-of-knowledge artifact). Qwen is shared by
  *every* session: the switch window kills unmanaged sessions too (no
  quiescence check). Restart must come from outside the dead model's users.
- **Executor:** deterministic Qwen-batch steps need **no switch at all**
  (tier-1 no-flip path); `--force` is the real fit-guard fix; C's wrapper
  absorbs D; typer = plain shell, gated, one-shot; concrete first step =
  write the script + dry-run against a titled test window.

## Where the council clashed (chairman's rulings)

- **Does the flip need to exist at all?** Executor+Expansionist: heavy
  `events-extract` needs no switch (:8000-on-CPU is normal 262k behavior).
  **Ruling: the step taxonomy IS the design** — tier 1 (no flip) for
  deterministic Qwen batches; the A/B/C/D chain is tier 2 only (CUDA
  embed/reindex, ≥2-parallel-subagent phases, judgment steps).
- **Single setsid chain vs C-wrapper switch-back.** **Ruling: same machine —
  the script owns the whole chain (survival property kept), "C" is the pi
  session inside it; owner's C-terminal mental model kept.**
- **Who restarts a dead Qwen:** the script owns it in-chain (bounded ×2,
  anti-flap via `ninfer_restart.sh`'s guards); the MASTER_WORK poller's
  MODEL-DOWN path is the proven backstop; STALLED flag escalates to A.
- **Quiescence strictness (Outsider):** check all session jsonl mtimes for
  5 s growth before each switch; growing → bounded wait. One loop, not a
  subsystem.

## Blind spots caught only in peer review

1. **The switch-back is fit-guarded too, and transcript deletion poisons it** —
   delete C's file first and the newest-file fallback becomes A's 262k
   transcript → 262k switch exits 2 → machine stranded at 100k. Fix: explicit
   `PI_SESSION_FILE`/`--force` on **both** switches; C's file deleted last,
   by A, post-resume.
2. **`--api` on a chain switch restarts `:8000` on CUDA in 100k mode** —
   re-triggers the 508/524 Qwen-OOM class under a long extraction. Chain
   switches take no `--api` (verified: without it, :8000 is untouched).
3. **Launch-side race:** B is A's final action, so the 100k switch can
   overlap A's own turn-end model call → lossy auto-compact *at handoff*.
   Gate the switch on A's jsonl quiescent ~10 s.
4. **Hung batch blocks the switch-back** (pgrep guard) → silent stall; only
   heartbeat + STALLED flag catch it.
5. **Reboot mid-chain kills the detached chain**; disk state survives; replay
   is a documented one-liner (re-run the script on the same spec).
6. **Double-type garbles A's prefill** — typer one-shot via typed-flag.
7. **No mutex on the mode dial** — one handoff at a time, documented
   (running `qwen-switch.sh` process is the de-facto lock).

## Verdict

**Sound in shape, three modifications:** (1) step taxonomy — tier 1 no-flip
for deterministic Qwen batches, chain only for tier-2 steps; (2) B demoted to
plain shell (A writes the full checkpoint first), D eliminated (script's
switch-back absorbs it, still "plain terminal between turns"); (3) a
plain-shell gated one-shot typer owns the return leg — MASTER_WORK never
touches the deterministic leg (it depends on the very model being switched);
gate = state ∧ live-262k (`qwen_mode.txt`) ∧ :18080 healthy ∧ report stable
∧ window alive (by `a_win`, then title) ∧ A idle ∧ not-yet-typed. Plus the
failure lanes (liveness restart ×2, heartbeat STALLED, failure-line typing).

**Applied:** `tools/master-work/gpu-handoff.sh` (tier1/tier2/test modes) +
`docs/ops/PC_GPU_HANDOFF.md` + `pi.md` §5 pointer. Dry-run PASS 2026-09-08
(see the doc's test record). First live use pending owner's go-ahead.
# gpu-live2 directive — owner correction (2026-09-08)

**Supersedes:** the truncated typed message ("OWNER CORRECTION … CPU fallback")
that landed in this session at ~13:20 — its middle was dropped by the typer
and it must be disregarded. This file is the canonical directive (owner
stopped the session to reissue it cleanly).

## Why the CPU fallback was the wrong branch (answered on record)

- What happened: 6 pytest cases OOMed (Qwen 262k+vision owns the card; only
  ~1.6 GB free < the ~5.3 GB the embedder needs), and the session took the
  device-rule's "cannot free the card → CPU" branch + my re-baseline directive's
  "CPU is fine" wording (that wording was my error — it contradicted your
  2026-09-07 standing rule).
- The clear instruction (both docs agree): **262k holding the card +
  GPU-beneficial work = switch Qwen to 100k and run the work in a fresh 100k
  SIDE session** — the tier-2 gpu-handoff chain
  (`docs/ops/PC_GPU_HANDOFF.md`, `tools/master-work/gpu-handoff.sh`).
  This campaign session sits idle through the window (frozen context, zero
  cost); the side session does the GPU work; the chain flips back and types
  the resume line. Proven 2026-09-08 by gpu-live1.

## What to do (in this order)

1. **Write the spec + task brief:** `plan/gpu_live2.spec` (`kind=tier2`) and
   `plan/gpu_live2_task.md` (the side session's prompt):
   - Task = full standing-gates re-baseline under 100k+CUDA, one side session:
     a. `pytest` full suite, model tests on CUDA (honor the one-copy-of-embedder
        VRAM rule; the 6 cases that OOMed under 262k — list them in the brief —
        must pass on GPU)
     b. `eval --series jjk`
     c. `span-recall --series jjk` (offline) + `--probe 400` against a CUDA `:8000`
     d. `canon-run --series opm`
   - Report → `reports/csm/GATE_REBASELINE.md` (raw receipts per gate + a
     table of the new numbers). Leave `:8000` on CUDA and say so in the report
     (the campaign session restores it to CPU on resume).
   - Spec fields per the protocol: `a_title` (your terminal's title),
     `a_win` (`xdotool getactivewindow`), `a_session` (`$PI_SESSION_FILE`),
     `resume_line` (a fixed one-liner telling you to read the report, restore
     `:8000` to CPU, update CLAUDE.md's gate values, resume CSM-2),
     `eta_sec=5400`.
2. **Commit the spec + task brief** (the pre-switch checkpoint — protocol rule).
3. **Final action of your turn:**
   `setsid nohup bash tools/master-work/gpu-handoff.sh --tier2 plan/gpu_live2.spec > /tmp/gpu_live2_chain.log 2>&1 < /dev/null &`
   — then end the turn and sit idle.
4. **On the typed RESUME:** read the report → restore `:8000` to CPU (262k
   co-location rule) → update CLAUDE.md's stale gate values with the new
   numbers + run timestamps (they are self-contradictory right now: 1,239 vs
   1,242) → commit → resume CSM-2 (the scoreboard/classification item).

If the chain STALLs, it writes a flag and types a FAILURE line into your
window (never silent); replay = the same `setsid` line, gates are idempotent.
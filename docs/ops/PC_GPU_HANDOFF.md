# PC GPU-handoff protocol (council-verified 2026-09-08)

**RESERVED FOR PHASE 2 (EXTRACTION PHASE) — owner rule 2026-09-08.** Phase 1
(the CSM fixing process) runs at the 150k Qwen dial with co-located CUDA and
2-subagent waves (`plan/CSM_2PHASE_PLAN.md`) and does NOT use this chain
per-step. Sanctioned uses: the D5 exhaustive sweep and D6 extraction —
batched side sessions in Qwen quiet windows, an even smaller dial if VRAM
demands it.

How a full-context (262k) campaign session **A** hands a GPU-heavy step to a
fresh 100k session **C** in a new terminal, gets a report back, and resumes —
without vision, without losing A's context, and without the mode dial stranding
the machine. Verdict + full record: `reports/master-work/COUNCIL_gpu_handoff.md`.
Executable chain: `tools/master-work/gpu-handoff.sh`.

## Verified machine facts (the design follows from these)

- **One shared model.** Qwen 27B (:18080) serves every pi session. Its context
  mode is a process-wide dial (`ninfer-work/qwen-switch.sh`), switched in
  ~30–60 s (model-less window; pi processes survive, in-flight turns die).
- **`qwen-switch.sh` syncs `~/.pi/agent/models.json`** contextWindow per mode,
  and a pi session reads that value **at startup**: a session started under 262k
  keeps 262k declared in memory after a switch-down (in-memory > live cap =
  overflow class → 400 `context_length_exceeded` → lossy auto-compact).
  **C must be a FRESH session started after the switch-down** (it then
  declares 100k, matching live).
- **Fit guard:** the switch refuses (exit 2) if the reference transcript
  (`$PI_SESSION_FILE`, else the *newest* session file) can't fit the target ctx.
  The chain therefore uses `--force` on both switches (the documented
  "deliberate fresh-session handoff after a full checkpoint" case) — and
  **never deletes C's transcript before the switch-back** (deleting it makes
  the newest-file fallback A's 262k transcript → the 262k switch exits 2 →
  machine stranded at 100k).
- **No `--api` on the chain's switches:** without it, `:8000` is untouched
  (stays off). A long extraction under a CUDA `:8000` re-triggers the
  508/524 Qwen-OOM class — the batch needs `:8000` off (GPU-only since
  2026-09-26: never moved to CPU).
- **No-vision PC control is proven** (2026-09-08): open terminal
  (xdotool window-id diff) → `windowactivate` + `type` (visible keystrokes) →
  verify by **file side-channel** (the typed command writes a file) → close by
  typing `exit` (or Ctrl-D / kill for a non-interactive shell). Vision
  (VLM/AT-SPI) is a *fallback*, not a dependency — so 262k (vision flag off)
  can orchestrate the whole chain.
- **Window lookup quirk:** `xdotool search --class gnome-terminal --name X`
  returns **nothing** for gnome-terminal windows (verified); `--name X` alone
  works. Shells/pi rewrite window titles, so the spec carries **both**
  `a_win` (A captures `xdotool getactivewindow` at handoff — primary) and
  `a_title` (fallback).
- **`ninfer_restart.sh`** (tools/master-work) restarts a dead Qwen on the
  profile named by `qwen_mode.txt` — after a switch-down it comes back in
  100k, which is what the in-flight chain needs.

## Tier 1 — no flip (deterministic Qwen-batch steps)

`events-extract` / LLM batches need **no mode switch at all**: under 262k,
Qwen owns the GPU and `:8000` off is normal behavior. A just detaches:

```bash
tools/master-work/gpu-handoff.sh --tier1 <spec>   # batch + gated typer, no switch, no new session
```

Use tier 1 whenever A knows the exact command and no agent judgment is needed
mid-run.

## Tier 2 — the chain (CUDA embed/reindex, ≥2-parallel-subagent phases, or a
judgment step needing a fresh 100k session)

A's terminal must be openable/known (owner launches it; A captures `a_win`
at handoff). The chain is **mostly shell** — the only LLM in it is C's task:

1. **A (pi, 262k):** writes the handoff spec + `plan/SWITCHPOINT.md`
   hand-written section + `git commit`, then its **final action**:
   `setsid nohup tools/master-work/gpu-handoff.sh --tier2 <spec> >/dev/null 2>&1 &`
   → turn ends. A sits idle (frozen context, zero cost). A sees only
   "work chat" in its own window.
2. **B = the script (plain shell, no pi session — demoted from the owner's
   design by the council):** quiescence (A's jsonl ~10 s + all sessions 5 s —
   the switch must not overlap A's turn-end model call) →
   `qwen-switch.sh 100k --force` → opens C's terminal.
3. **C (the only new pi session):** visible terminal (title `GPU-<spec>`),
   a shell wrapper around `pi -p "<task>"` (fresh 100k declaration). C runs
   the GPU task with agent judgment and writes the **report** to disk.
   Wrapper writes the state file (`state=done|failed`) — no LLM discipline
   needed for the handoff itself.
4. **Switch-back (absorbs "terminal D" — rejected as a terminal by the
   council):** the script (still plain shell, between turns — hard rule holds)
   runs `qwen-switch.sh 262k --force` with `PI_SESSION_FILE=<C's transcript>`
   (guard-honest) once C's state is final.
5. **Typer (plain shell, gated, one-shot):**
   `state==done ∧ qwen_mode.txt==262k ∧ :18080 healthy ∧ report mtime stable
   ~30 s ∧ A's window alive (a_win, then a_title) ∧ A's jsonl idle ~10 s ∧
   typed-flag unset` → `windowactivate` + type `resume_line` + Enter, **once
   (idempotent)**. On `state==failed` it types a *failure* line into A
   instead — the chain never stalls silently.
6. **Resume:** A's typed line points it at the report + SWITCHPOINT; A reads
   both from disk and continues the campaign. A then trashes C's transcript
   (the task record) — **after** reading the report, never earlier.

**Cleanup:** B/D have no transcripts (shell); C's transcript is trashed by A
post-resume; A keeps its own. One handoff at a time (the mode dial has no
mutex — a concurrent owner `qwen-switch` cross-flips the chain).

## Failure lanes (the design's second half)

| Failure | Owner of the recovery |
|---|---|
| Qwen dies mid-task | script polls :18080; `ninfer_restart.sh` (bounded ×2; its anti-flap guards prevent fighting the MASTER_WORK poller, which is the backstop) |
| Batch hangs (blocks the switch-back's pgrep guard) | heartbeat `eta_sec` → `STALLED.flag`; MASTER_WORK reads it (a flag read "on A's resume" is circular — A is the session that isn't resuming) |
| Window stale/closed (reboot, owner closed it) | typer gate fails → flag file with the resume one-liner; owner types it into a re-opened A (state is git + SWITCHPOINT + report — A's transcript is convenience, not state) |
| Switch-down refused (fit guard) | `--force` (deliberate handoff); if the *switch-back* still refuses → STALLED, owner re-runs with a fresh reference |
| Reboot mid-chain | disk state survives; replay = re-run the script for the same spec (idempotent gates) |

## Spec format (`tools/master-work/gpu-handoff.sh <spec>`)

```
kind=tier1|tier2
batch=<resumable-from-disk shell command>        (tier1; tier2: C's task runs it)
report=<path C/A must leave the report at>
resume_line=<fixed one-liner A reads on resume>
a_title=<A's terminal title (fallback lookup)>
a_win=<A's window id: A captures xdotool getactivewindow at handoff (primary)>
a_session=<A's pi session jsonl path>
eta_sec=<heartbeat deadline, default 3600>
task=<C's pi prompt: what to do, where the report goes>   (tier2)
```

State: `reports/master-work/gpu_handoff_state/<spec>.{state,log,stalled,typed}`.

## Test record

- **2026-09-08 dry-run PASS** (`--test`, LLM-free): quiescence → fake switch →
  fake C (plain shell, 5 s task) → state=done → fake switch-back → typer gate
  passed → resume line typed **once** into a titled test window; side-channel
  file confirms the exact keystrokes landed. Chain log + typed capture kept in
  `/tmp/gpu_handoff_test_*` (transient).
- First **live** use: the next CSM-resume GPU step (owner's call — it performs
  two real 30–60 s model reloads).
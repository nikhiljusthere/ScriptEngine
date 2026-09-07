# Qwen context modes — 262k exploratory ↔ 100k service (dial-down)

Date 2026-09-07. Companion to `qwen38_ninfer_opencode_config.md` (how the
server is built and launched). This file defines *when* to run Qwen at which
context size, and the protocol for switching between the setups.

## Why context size is a VRAM dial

Qwen 3.8 27B (NVFP4) on the 32 GB RTX 5090 is served by `ninfer-serve`
(:18080) with an int8 KV pool pre-reserved for `--kv-capacity` tokens. The KV
pool is the only part of Qwen's footprint that moves with context length
(model weights ~17.4 GiB are constant):

| mode | `--max-context` / `--kv-capacity` | KV pool (int8) | headroom after load |
|---|---|---|---|
| exploratory | 262144 | ~10.6 GiB | ~3.4–3.6 GiB (measured 2026-09-07: 3,580 MiB) |
| service | 102400 | ~4.2 GiB | ~7–8 GiB |
| dial-down | e.g. 65536 | ~2.6 GiB | ~10 GiB+ |

Headroom = room left for other GPU processes — chiefly the ScriptEngine
`:8000` embedder+reranker (~5.3 GiB, loaded lazily on first use). The 100k
figure is a **default, not a floor**: if more VRAM is needed, dial it down
further; `qwen-switch.sh <tokens>` generates the profile on the fly.

## What each mode is for

- **262k — exploratory / linear.** Maximum context for long linear dives and
  exploratory code fixes. Headroom is below the 5.3 GiB the reranker wants, so
  `:8000` must run on CPU (or be stopped). Work is linear: **no parallel
  subagents**.
- **100k — service.** ~7–8 GiB headroom: the `:8000` API co-locates on CUDA
  (fast cross-encoder) and **up to 2 subagents run in parallel**. This is the
  mode for work that needs live probes (span-recall probes, page-runs,
  council-with-GPU) while Qwen stays up.
- **Dial-down (65536, 50176, …).** Still more headroom for heavier co-location.

**llm-council is the standing exception to the subagent limit: all 5 advisors
(then 5 peers) run in parallel in any mode** (council-only, per the working
agreement — its subagents are short and bursty, not sustained load).

## The cost of small modes: compaction

pi compacts a session when it nears the model's context limit, and a
compaction is a *lossy summarization of your reasoning*. A 100k — let alone
64k — window hits compaction fast. So small modes have one rule:

> **Explain the work on disk before entering a small mode.** The transcript is
> disposable; `plan/SWITCHPOINT.md` is not. A fresh pi session seeded from the
> switchpoint continues the work with no transcript at all.

## The switch method (checkpoint → switch → reopen → resume)

1. **Checkpoint (inside pi, current mode).** Commit the work; fill the
   "Current position" section of `plan/SWITCHPOINT.md` (mode, sha,
   trunk/excursion address, what's in flight, the exact next step). Mid
   trunk/excursion step → add the drift pointer too.
2. **Switch (one atomic call).**
   `cd /home/goblin/ninfer-work && ./qwen-switch.sh <262k|100k|<tokens>> [--api] [--force]`
   The script: refuses while an extraction batch is in flight → **hard-refuses
   (exit 2) if the pi transcript can't fit the target context** (the fit
   guard; `--force` is only for a deliberate fresh-session handoff) → fixes
   the `:8000` device to match the new headroom (CUDA iff ≥ 6 GiB) → unloads
   Qwen → loads the target profile → health-polls (~30–60 s reload) → writes
   `qwen_mode.txt` + a switch-log line → prints the reopen handoff.
   A human runs it from a terminal; **the pi agent runs it as a single
   blocking `bash` tool call** (the autonomous protocol, next section) —
   never split across calls.
3. **Reopen pi (terminal, project dir).**
   - `pi -c` — continue the same session; only right for 262k (the script's
     handoff says which when the transcript fits).
   - fresh `pi` + *"Read `plan/SWITCHPOINT.md` and continue from there"* —
     always for small modes (compaction pressure; the switchpoint is the
     authoritative state).
4. **Resume (first action of the new session).** Read the switchpoint +
   `plan/drift_log.md` §4; verify the active mode via `ninfer-work/qwen_mode.txt`
   + `nvidia-smi`; run `qwen-switch.sh <current-mode>` as a no-op self-check
   (it re-corrects the `:8000` device if anything drifted); continue the work.

## Why the switch is a single atomic call

pi's model *is* this Qwen server. During the reload window (~30–60 s) there
is no model serving pi — **the agent has no thinking and no editing power for
that window**. That is safe *iff* the whole switch is **one blocking tool
call**: the model has already emitted the tool call and is idle while the
harness executes the shell command (no LLM involved), so recycling the
server mid-turn kills nothing. When the call returns, the next model request
hits the reloaded server on the same model-id/port, and the same pi session
continues — the transcript is on disk, and only the server-side KV cache was
lost (the next turn re-prefills, ~1–2 min slower).

The failure mode is splitting the switch across tool calls: the harness
makes a model call *between* calls, and that call would die mid-reload. So
pkill→reload→health is always one invocation (`qwen-switch.sh` does exactly
that), issued with a generous `timeout` (300 000 ms; the default 120 s is
shorter than the reload — a timeout is still fine, the load is detached and
survives, then poll `/v1/models`).

The pre-condition holds in both human and agent use: the checkpoint (step
1) must be complete *before* the switch, because nothing on the model side
survives the window — everything needed to continue must be on disk.

## Autonomous switching (pi agent)

The pi agent may switch modes **on its own** while executing a long plan —
that is the designed working mode, not an exception. Protocol (skill:
`.pi/skills/qwen-switch`, kit doc: `pi.md` §5):

1. **Decide at phase boundaries, not per step.** Each flip costs a reload +
   cold re-prefill, so one switch per GPU phase. 262k is for *inline*
   linear work; 100k has exactly two use cases — (1) the GPU is needed
   (the `:8000` embedder+reranker co-locate on CUDA beside Qwen), and
   (2) subagent parallelism (extraction/reading/review batches, ≤2 in
   parallel; `llm-council`'s 5 is the standing exception in any mode). Both
   trigger the same switch:
   | upcoming work | action |
   |---|---|
   | `:8000` embedder+reranker needed on CUDA *alongside* Qwen (live span-recall probes, page-runs, `/context` work) | switch **down** (100k) |
   | ≥2 parallel subagents (extraction / reading / review fan-out) | switch **down** (100k) |
   | heavy Qwen LLM batch (`events-extract`) | **no switch** — the hard rule: stop `:8000` (or CPU), Qwen owns the card |
   | GPU phase + subagent phase finished, inline work remains | switch **back** to 262k |
2. **Pre-flight (model alive):** `switchpoint` checkpoint (commit +
   `plan/SWITCHPOINT.md`); fit check — the current session's transcript
   (`$PI_SESSION_FILE`, bytes/4) must fit the target context; no
   `events-extract` in flight. The bytes/4 estimate is conservative (~2.7x
   the real token count — it counts jsonl overhead), so a refusal often
   means "conservatively refused", not "cannot fit": the running session
   survives if its *real* context fits, and if it overflows mid-work, pi
   auto-compacts (step 5).
3. **The switch:** one `bash` tool call, `timeout: 300000`. The fit guard
   hard-refuses (exit 2) an un-fitting target per its estimate; `--force`
   (full checkpoint first) is the bypass — for the running session it is a
   "continue anyway, overflow auto-handles itself" bypass, and for a clean
   state it is the fresh-session handoff below.
   The script also syncs `~/.pi/agent/models.json`'s `contextWindow` to the
   mode, so the pi header + the *proactive* auto-compact threshold are
   honest for sessions started after the switch.
4. **Post-flight:** `qwen_mode.txt` + `nvidia-smi`; the `:8000` device was
   already corrected by the script; continue from the switchpoint.
5. **Overflow is self-handling (no user action).** If the running session's
   context exceeds the server cap, ninfer returns `400
   context_length_exceeded`; pi-ai's generic overflow pattern matches it and
   the agent session auto-compacts + retries the turn (`_runAutoCompaction
   ("overflow")`) — no approval, no session switch. A *fresh-session*
   handoff (open `pi`, say "Read plan/SWITCHPOINT.md and continue from
   there.") is for wanting clean state, not for survival.

**Subagent policy per mode:** 262k → linear, no parallel subagents; 100k →
≤ 2 parallel; `llm-council` runs 5 in parallel in **any** mode (the standing
exception).

## Guardrails (carry-overs from the standing GPU rules)

- No switch while an `events-extract` / heavy LLM batch is in flight — the
  script refuses (Qwen owns the card for those; see the hard rule in
  `CLAUDE.md`).
- Every switch loses the server-side KV/prefix cache: the resumed session's
  first turn re-prefills from cold. Budget ~1–2 min of slow first turn.
- pi sessions are JSONL files on disk — the conversation survives the switch
  either way; the only question is whether it *fits* the new context. The
  script checks the latest transcript size (conservatively) and says; an
  overflow mid-work is auto-compacted by pi itself (step 5 of the
  autonomous protocol above).
- The old "short, bounded `:8000` CUDA probe while Qwen runs" exception
  (working-agreement point 4, measured at `--kv-capacity 155648` → ~7 GB
  headroom) **does not apply to the current 262k profile** (~3.5 GiB
  headroom < 5.3 GiB). CUDA co-location happens by design in the 100k service
  mode instead.
- `ninfer-work/qwen_mode.txt` is the live record of which mode is active —
  check it (with `nvidia-smi`) at the top of every session.

## Files

| file | role |
|---|---|
| `ninfer-work/serve.sh` | 262k exploratory profile |
| `ninfer-work/serve_100k.sh` | 100k service profile |
| `ninfer-work/serve_ctx_<N>.sh` | generated dial-down profiles |
| `ninfer-work/qwen-switch.sh` | the switch (`--dry-run`, `--api`, `--force`; hard fit guard) |
| `ninfer-work/qwen_mode.txt` | live mode record (machine-written) |
| `plan/SWITCHPOINT.md` | the resume file (hand-written section + machine log) |
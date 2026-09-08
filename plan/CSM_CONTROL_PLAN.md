# CSM Control Plan — Terminal A (Control) + Terminal B (Phase-1 worker)

Owner directive 2026-09-08 (supersedes "the CSM session steers itself"): **every
shell Terminal B runs is checked by Terminal A** — each runs on GPU, not CPU;
A has stop/update authority over any shell/run/span taking too long; A keeps a
log of all shells + their durations; A intervenes **only while a shell is
active in B** (that is when Qwen has stopped thinking and is running the
shell). Both terminals are **fresh pi sessions**, distinct from the planning
session.

## The 1200-s incident (why this plan exists)

`span-recall --series csm --panel <pinned>` is the **exhaustive tier-1 D5
sweep** (17,381 probes) — NOT the offline tier-0 check. Every probe is an HTTP
round-trip to `:8000` (embed + rerank). `:8000` was serving on **CPU**
(measured 1025 % util while the sweep ran), so ≈1–2 s/probe → a multi-hour
CPU-bound run behind a plain shell — the Phase-1 15-s rule violated for 20+
minutes before anyone looked. It was never hung; it was CPU-slow. Structural
fixes: (a) `:8000` on CUDA + Qwen at the 100k dial (VRAM below), (b) A's
monitor kills CPU model work >15 s and flags any shell >300 s, (c) full-panel
sweeps are GPU-only and are **sampled first** (the 400-probe standing gate).

## Topology

- **Terminal A — Control** (fresh pi session, window title `CSM-CONTROL`):
  1. Launch Terminal B: `setsid nohup gnome-terminal --disable-factory
     --title=CSM-WORKER >/dev/null 2>&1 </dev/null &` (the only terminal
     spawn that works from a pi shell; the D-Bus factory path silently drops).
     Find the new window id (newest gnome-terminal window not in the pre-list),
     record `{a_win, b_win}` in `reports/csm/windows.json`. Type `pi`, wait for
     the TUI, then type B's bootstrap (§Bootstraps) — **verify every type with
     a file side-channel probe before the next one** (the 2026-09-08 lesson:
     vte ignores `xdotool key --window`; use focused XTEST:
     `windowactivate --sync` → `type` → `key Return`; probe = type
     `touch /tmp/b_probe && echo ok > /tmp/b_probe.out`, poll the file).
  2. Find B's pi pid (newest `pgrep -x pi` that isn't A's) and launch the
     monitor detached:
     `setsid nohup bash tools/master-work/csm-control.sh <b_pid> <b_win> >> reports/csm/control_run.log 2>&1 &`
  3. Every ~3 min: read `reports/csm/shell_log.jsonl` +
     `reports/csm/interventions.jsonl`; handle the judgment cases the monitor
     cannot (update a run to a bounded form and type the corrected command
     into B; dial down on a VRAM squeeze; dead door / gate failure → council,
     one agent at a time). Commit after each intervention batch.

- **Terminal B — CSM Phase-1 worker** (fresh pi session, window
  `CSM-WORKER`): runs Phase 1 of `plan/CSM_2PHASE_PLAN.md` (CSM-5/6 + the §9a
  closure loop; CSM-3 is done @ `f93d396`). All model shells on GPU; no CPU
  shell >15 s; 2-subagent waves (deploy 2 → access both on disk → next 2,
  never queued).

## The monitor — `tools/master-work/csm-control.sh` (A's eyes)

5-s poll of B's pi process tree (pi → tool `bash -c` → `python`/CLI):
- **detect**: new shell-ish child → `{ts, pid, cmd}` →
  `reports/csm/shell_log.jsonl` (the owner-required log of every shell).
- **time**: child exits → `{pid, dur_s}` appended (log = all shells + times).
- **classify model-heavy**: cmdline has a model-loading scriptengine
  subcommand (`eval`, `span-recall --probe/--panel`, `canon-run`,
  `pytest tests/`) or an explicit `SCRIPTENGINE_DEVICE`.
- **enforce (only while a shell is active in B)**:
  - model-heavy shell >15 s with **no CUDA context** (no `nvidia` fd in
    `/proc/<pid>/fd`) or explicit `SCRIPTENGINE_DEVICE=cpu` → **kill** +
    `interventions.jsonl` entry + type the re-run hint into B (focused XTEST).
  - a `:8000` server on CPU (checked via its `environ`) while a probe
    command runs → kill the client (hours-long CPU inference is the 1200-s
    failure mode) + hint.
  - any shell >300 s → `LONG` flag in `interventions.jsonl` (**no auto-kill**
    — A the LLM judges: update-to-bounded, kill, or let-run with reason).
  - `:18080` down >60 s → `MODEL_DOWN` in `interventions.jsonl` (A acts:
    `ninfer_restart.sh`).
- If B's pi pid ever goes stale (session swap), `control_run.log` goes quiet —
  A relaunches the monitor with the new pid.

## GPU steady state (invariants of this plan)

- Qwen at the **100k dial** (150k left only 5.2 GB free — cannot co-locate
  `:8000` (≈5.3 GB lazy load) + a one-copy in-process job; the owner's
  "even smaller context if necessary" clause, applied at setup, not per step).
- `:8000` on **CUDA** (co-located with 100k Qwen, ≈6.9 GB headroom).
  **One-copy rule**: in-process model jobs (pytest model tests, eval CLI)
  stop `:8000` first, run on CUDA, restart `:8000` (CUDA) after.
- Subagent waves ≤2 parallel (100k policy); councils one agent at a time.

## Bootstraps (the exact lines to type; each ≤ ~700 chars, one Return each)

**A-MSG1:**
You are Control Terminal A for the CSM Phase-1 campaign (fresh 100k session; Qwen 100k, :8000 CUDA, one-copy rule). Read plan/CSM_CONTROL_PLAN.md (your job + rules) and plan/CSM_2PHASE_PLAN.md (Phase-1 scope). Then: (1) launch Terminal B: `setsid nohup gnome-terminal --disable-factory --title=CSM-WORKER >/dev/null 2>&1 </dev/null &`, sleep 5, new window id = newest gnome-terminal window not in the pre-list; write {"a_win":..,"b_win":..} to reports/csm/windows.json; type `pi` into B (verify: window title becomes "π - ScriptEngine" + a NEW session file appears), then type B-MSG1 and B-MSG2 (below) with a file side-channel probe between each type. (2) b_pid = newest `pgrep -x pi` that is not yours; launch: `setsid nohup bash tools/master-work/csm-control.sh <b_pid> <b_win> >> reports/csm/control_run.log 2>&1 &`. (3) Every ~3 min read reports/csm/shell_log.jsonl + interventions.jsonl; judgment calls (update a run to a bounded form, kill a LONG run, MODEL_DOWN restart) you type into B or fix yourself; commit after each batch.

**A-MSG2:**
Typing rule (2026-09-08 lesson, do not repeat the bug): focused XTEST only — `xdotool windowactivate --sync <win>`, `xdotool type ...`, `xdotool key Return`; NEVER `key --window` (vte ignores synthetic X events — commands will sit unexecuted at the prompt). Always prove a type landed via a file probe before continuing. You have stop/update authority over B's shells/runs/spans; the monitor auto-kills CPU model work >15 s but LONG (>300 s) runs are yours to judge. Disk is the tiebreaker: SWITCHPOINT "Campaign todos" + reports/csm/.

**B-MSG1:**
You are the CSM Phase-1 worker (Terminal B, fresh 100k session; Qwen 100k, :8000 on CUDA — one-copy rule: stop :8000 before in-process model jobs, restart it CUDA after). Read: plan/CSM_2PHASE_PLAN.md, plan/CSM_CONTROL_PLAN.md (Control A monitors every shell you run: GPU-only, no CPU shell >15 s, >300 s runs get flagged for A's judgment — re-run per its hints, they appear in your terminal or reports/csm/interventions.jsonl), plan/SWITCHPOINT.md section "Campaign todos" (rebuild your todo panel from it; sync back + commit after each status change). State: CSM-3 done (f93d396, panel e3d73720, 17,181+200); CSM-3b artifacts uncommitted — finish the exit-code recheck + commit; an exhaustive --panel sweep is GPU-ONLY and always sampled first (400-probe gate) — never a full-panel run against a CPU :8000 (the 1200-s incident, reports/master-work/work_log.md).

**B-MSG2:**
First waves (deploy 2 workers in parallel, access both results on disk, then the next 2 — never queue): Wave 1: (worker 1) CSM-3b close-out (exit-code recheck, commit the CSM-3b/council artifacts, JJK span-recall unchanged check); (worker 2) standing gates on CUDA (one-copy ordering: server down for in-process pytest/eval, up (CUDA) for probe/canon HTTP gates) + the 39-question CSM seed bank. Wave 2: (worker 3) CSM-6 instrument (parameterize the two jjk-hardcoded tools, CSM dimension map, eight-verb sample, frozen census sets, T0 pilot, cross-page census); (worker 4) CSM-5 remainder (fixtures, 5.5 gold + red list, 5.4 door pre-check, twenty-failures set). Then the §9a closure loop, iteration 1. Councils: one agent at a time, every 2–3 todos.

## Setup chain (supervisor runs this once, detached)

1. Commit this plan + the monitor (checkpoint).
2. `qwen-switch.sh 100k --force` (fit guard blocks on the 840k planning
   session file — deliberate, checkpointed; fresh A/B declare 100k clean).
3. Detached setup script (`/tmp/csm_control_setup.sh`, log
   `/tmp/csm_control_setup.log`): wait for the 100k switch + `:18080`
   healthy → start `:8000` on **CUDA** (no `SCRIPTENGINE_DEVICE` override;
   health check) → spawn the `CSM-CONTROL` window → type `pi` + A-MSG1 +
   A-MSG2 (focused XTEST + probes) → type a resume note into the planning
   window. A then launches B + the monitor itself (§Topology step 1–2).
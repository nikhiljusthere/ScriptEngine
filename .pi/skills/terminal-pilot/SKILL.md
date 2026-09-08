---
name: terminal-pilot
description: Open and control second gnome-terminals each running its own pi agent (the "control terminal" pattern), restart/verify the local ninfer Qwen model (:18080), enforce the GPU one-copy steady state, and run the monitor + judgment loop over the worker's shells. Use when a task needs a second pi agent (worker/council/reviewer), when ninfer must be (re)started or its mode checked, when a worker terminal died (close, reboot, power loss) and must be relaunched with a resume bootstrap, or when supervising a worker's shell activity. Hard-won lessons from the 2026-09-08 CSM campaign: vte/XTEST typing, file-probe verification, monitor false-positive kills, subagent wave stacking, post-reboot state drift.
---

# terminal-pilot — second-terminal + pi-agent control, ninfer ops, judgment loop

Repo: `/home/goblin/ScriptEngine`. All paths below are on this machine.
PIDs are NEVER stable — rediscover every time (reboot / session swap / restart).

## 0. Ground truth first (always, 30 s)

```bash
date; uptime                                   # reboot? all pids invalid
pgrep -x pi | while read p; do ps -o pid,etime -p $p | tail -1; done   # which pi sessions live
ps -o pid,etime,args -p $(pgrep -f ninfer-serve | head -1) | cut -c1-200  # Qwen LIVE MODE (flags)
curl -s -m 2 -o /dev/null -w "qwen=%{http_code} " http://localhost:18080/health
curl -s -m 2 http://localhost:8000/health 2>/dev/null | head -c 200    # device field matters
nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu --format=csv,noheader
git log --oneline -3; git status --short | head
```

- **Qwen mode = the live process flags, not `qwen_mode.txt`** (2026-09-08 reboot: file said
  100k, process was 262k — auto-start used the default).
- Device rule of thumb: Qwen **262k** (~3.5 GiB headroom) → `:8000` must run on CPU.
  Qwen **100k** (~7–8 GiB headroom) → `:8000` co-locates on CUDA.
- **One-copy rule**: before any in-process model job (pytest, eval CLI), stop `:8000`,
  run the job on CUDA (default device — no `SCRIPTENGINE_DEVICE`), restart `:8000` on
  CUDA after. Verify the restart via `/health` `device: "cuda"`, not just port-up.

## 1. ninfer (Qwen 27B, :18080)

- Tooling: `/home/goblin/ninfer-work/` — `qwen-switch.sh`, `start_server.sh`,
  `logs/serve_*.log`, `qwen_mode.txt` (state, goes stale on reboot).
- **Switch**: `ninfer-work/qwen-switch.sh <262k|100k|150k|raw> [--api] [--force] [--reload]`.
  ~30–60 s model reload; during the window the agent has no model (pi survives, transcript on
  disk). `--reload` forces a reload even at same context (serve-profile flag changes).
  **Fit guard** (exit 2): target ctx can't hold the current session file → checkpoint to
  disk first (`plan/SWITCHPOINT.md`), resume fresh.
- **Restart** (crash / MODEL_DOWN / flags changed):
  ```bash
  pkill -f 'ninf[e]r-serve'; sleep 1
  setsid nohup /home/goblin/ninfer-work/qwen-switch.sh <mode> --reload > /tmp/ninfer_restart.log 2>&1 < /dev/null &
  ```
  then poll `curl http://localhost:18080/health` in a bounded loop. (Plain `start_server.sh`
  also works but blocks until healthy — fine inside a `setsid nohup`.)
- **Throttle triage** (before declaring a fault):
  `nvidia-smi -q | grep -A3 "SW Power Cap"` + throttle reasons. Sustained 100 % util at the
  600 W cap (582 W, clocks ~2842/3135 MHz) is **normal power-limit throttling, not a fault**.
  Only HW/SW *thermal* slowdown is a problem.
- **Queue / serialization reality**: `--max-concurrency 3` is an admission cap, NOT a
  batching guarantee — spec-decode (`--spec mtp`) decodes strictly one sequence at a time
  (`running=1`, `avg_decode_batch=1.00` in serve log). Two "parallel" model-heavy agents =
  2× serial wall time + queue ttft (observed 98 s). Check: `tail` the serve log for
  `running=` / `waiting=`. So: **2-parallel only for zero-GPU work; model-heavy waves 1 at a time.**

## 2. Open + control a second terminal running pi

Launch (survives the tool-call abort that kills plain `nohup`):
```bash
setsid nohup gnome-terminal --disable-factory --title=CSM-WORKER >/dev/null 2>&1 </dev/null &
```
Find the new window: pre-list windows (`xdotool search --class gnome-terminal`), launch, then
poll (bounded loop, status line every 5 s, **explicit `timeout` on the bash call** — never a
bare `sleep`):
```bash
comm -23 <(xdotool search --class gnome-terminal | sort) <(printf "50331649\n50331658\n")   # the NEW one
```
Record `{"a_win":…,"b_win":…}` in `reports/csm/windows.json` (campaign) or your own note.

**Typing rules (the 2026-09-08 bug — do not repeat):**
- Focused XTEST only: `xdotool windowactivate --sync $W` → `xdotool type --clearmodifiers "…"` →
  `xdotool key Return`. Long messages: `xdotool type --clearmodifiers --file /tmp/msg.txt`.
- **NEVER `xdotool key --window`** — vte ignores synthetic X events; commands sit
  unexecuted at the prompt.
- **Prove every type landed via a file side-channel** before typing the next:
  type `touch /tmp/b_probe && echo M1 > /tmp/b_probe.out` and poll that file's content.
  Command success alone is NOT proof the input reached the pi TUI.
- **Boot**: type `pi` → wait for BOTH window title `π - ScriptEngine` AND a NEW session file
  in `~/.pi/agent/sessions/<project>/`. Title alone is NOT success — a pi that resumed the
  wrong session (PI_* inheritance) shows the same title with no new file. **But**: pi writes
  the session file on the FIRST model exchange, so no file ~1 min after boot is not itself
  proof of failure — check for a live pi process first. Wrong-session diagnostic: the session
  file that appears belongs to another session id, or the pi's `/proc/<pid>/environ` still
  carries `PI_*` → kill it, retype `env -u PI_SESSION_FILE -u PI_SESSION_ID -u PI_SUBAGENT_PARENT_SESSION pi`.
- **A pi already running in the target window receives your typing in ITS TUI, not the shell**
  (2026-09-08 21:48: a 7-min-old pi in the TOJI window ate the `env -u … pi` launch line as a
  user message — harmless only because it refused to run it). Before typing anything: find
  pi procs descended from the window's shell and kill them — walk the ppid chain TWO levels
  (pi → bash → `gnome-terminal-server`; a one-level check misses it), excluding your own pid
  list explicitly.
- **Pasting an actual prompt (the step the 2026-09-08 21:42 TOJI run skipped — never omit):**
  1. Prompt goes in `/tmp/<name>_prompt.txt` (write tool; no shell-escaping of long text).
  2. Only after pi is verified (new session file + title + ~2 s TUI settle). Probe line first,
     then `xdotool type --clearmodifiers --file /tmp/<name>_prompt.txt` → `xdotool key Return`.
  3. Verify the paste landed: grep the NEW session file for a distinctive prompt snippet (pi
     records typed user messages). A file probe only proves pi runs shell commands — it does
     NOT prove the prompt was received. Missing after ~60 s → check focus
     (`xdotool getactivewindow` vs target), retype once, re-verify.
- **Interrupt-resilience**: every poll loop ≤60 s (an aborted call must not outlive its work);
  persist the window id to `/tmp/<name>_win.txt` at discovery and resume from disk state after
  any abort. A window left at a bare bash (pi died/never started) → close it or start pi in
  it; never spawn a second window for the same job.
- `b_pid` = newest `pgrep -x pi` that is not your own pid.

**Resume bootstrap** (fresh session has no memory — disk is the tiebreaker): point it at the
plan + `plan/SWITCHPOINT.md` "Campaign todos" + the incident state (what died, what's
committed, what's dirty in the git tree), with probes between messages.

**Stuck worker (frozen subagent / dead completion notification):**
Symptoms: worker transcript file size frozen for N min, no live shell children, last event
KeyError/empty frame. Ladder (do NOT kill the worker or take over its workflow):
1. Check `/tmp/pi-subagents-uid-1000/async-subagent-runs/*/status.json` (state/lastUpdate) +
   the worker's session file + `forks/` sizes.
2. Confirm no live shell (`pgrep -P` tree of the worker pid).
3. Type a focused XTEST nudge into the worker's TUI: which run is frozen, instruct it to
   check status and restart only that child, plus a probe line; verify `NUDGE-OK` in the probe file.
4. Log `A_FLAG` / `A_INTERVENE` in the coordination log; commit.

## 3. Monitor + judgment loop (supervisor side)

```bash
setsid nohup bash tools/master-work/csm-control.sh <b_pid> <b_win> >> reports/csm/control_run.log 2>&1 < /dev/null &
```
- Writes `reports/csm/shell_log.jsonl` (every shell the worker spawns + duration) and
  judgment entries to `reports/csm/interventions.jsonl`. `control_run.log` is gitignored;
  the JSONLs are committed after each intervention batch.
- **Every ~3 min** read the last shell entries + any `LONG` / `KILL` / `MODEL_DOWN` events.
  `LONG` (>300 s) is a JUDGMENT, not a kill: approve-with-reason for legitimate long CUDA
  model jobs, bound/kill for stuck ones, type the corrected command into the worker.
- **Rule-2 false-positive lesson (2026-09-08):** never classify a model job as CPU-bound
  from the ABSENCE of nvidia fds on the `bash -c` wrapper (wrappers never have CUDA fds;
  cold CUDA init >15 s). Kill only provably-CPU work: `SCRIPTENGINE_DEVICE=cpu` in the
  process's `/proc/<pid>/environ`. Default-device jobs are assumed CUDA → 300 s LONG flag.
  Killing a wrapper must also kill immediate children (`pgrep -P`).
- `MODEL_DOWN` (:18080 down >60 s) → restart per §1, log the intervention.
- **Worker restarted (new pid/window)** → kill the old monitor, relaunch with the new
  pid+window, update `windows.json`.

## 4. Subagent waves: the cap is real

- Before deploying 2 workers: **verify 0 running subagents** (reap orphans, or wait), log the
  check. 2026-09-08 19:34 bug: a wave-2 pair deployed while the first pair was still alive →
  4 concurrent agents, violating the 2-cap. Waves STACK if you don't reap.
- Run states: `/tmp/pi-subagents-uid-1000/async-subagent-runs/<id>/status.json`
  (`complete|failed|stopped|running`, `lastUpdate`). When the parent pi dies (terminal
  closed, reboot), all its subs are `stopped`; their partial work survives in the **git
  working tree** → on resume: inspect, finish/commit, or explicitly discard.
- Model-heavy subs: one at a time (§1 serialization). Zero-GPU subs: 2 at a time.

## 5. Reboot / power-loss recovery checklist

After `uptime` shows a fresh boot, EVERYTHING must be rediscovered:
1. §0 ground truth (new pi pids, Qwen live mode, `:8000` down, GPU free).
2. Qwen: auto-started at boot? in which mode? Fix with `qwen-switch.sh` if the campaign
   needs a different dial. `qwen_mode.txt` is stale — trust the process flags.
3. `:8000`: down. Restart per the device rule (§0): Qwen 262k → CPU; Qwen 100k → CUDA.
   `setsid nohup scriptengine/.venv/bin/python -m scriptengine.api.main > /tmp/scriptengine_api.log 2>&1 < /dev/null &`
   + short `ps` + `curl /health` (check `device`).
4. Worker terminal: gone (user closed it, or reboot). Full §2 relaunch + resume bootstrap.
5. Monitor: gone. Relaunch §3 with the new worker pid/window.
6. Git: `git status --short` for pre-reboot partial work; commit or restore.
7. Coordination log: one `A_STATUS` entry with the full post-reboot state; commit.

## 6. Coordination-log conventions

- `reports/csm/interventions.jsonl`: events `A_STATUS` (state snapshot), `A_JUDGMENT`
  (decision + reason), `A_INTERVENE` (nudge/kill typed), `A_FLAG` (anomaly found),
  `B_NOTE` (worker side), one JSON object per line, `ts` ISO with offset.
- When appending JSON with `printf`, escape literal `%` as `%%` (2026-09-08: a `97.5%`
  in a note ate the format string and dropped the entry).
- Commit after every intervention batch; `reports/csm/control_run.log` stays out (gitignored).
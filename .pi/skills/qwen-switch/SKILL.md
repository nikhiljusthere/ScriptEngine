---
name: qwen-switch
description: Switch the local Qwen 3.8 27B (ninfer, :18080) between context modes — 262k exploratory, 100k service, or a dial-down — to free or reclaim GPU headroom, autonomously, mid-plan. Owner standard (2026-09-10): one detached 3-part shell — unload → load+place → internal LLM call triggers a gnome-terminal relaunch of the SAME session (pi --session); the agent never types the LLM call or the relaunch. Use when the next phase needs the :8000 embedder+reranker on CUDA alongside Qwen, or 2 parallel subagents, and when the GPU phase ends and full context is wanted again.
---

# qwen-switch — autonomous Qwen context-mode switching

Full doc: `docs/ops/QWEN_MODES.md` (repo = /home/goblin/ScriptEngine).
Kit doc: `pi.md` §5 (autonomous protocol).
Switcher: `/home/goblin/ninfer-work/qwen-switch.sh` (has `--dry-run`, `--api`, `--force`); the 3-part flow: `tools/master-work/switch_restart3.sh` + `tools/master-work/relaunch_term.sh` (log `/tmp/switch_restart3.log`).

## When to switch — decide at phase boundaries, not per step

Each flip costs a 30–60 s model reload + a cold re-prefill. One switch per
phase boundary; never thrash.

- **SWITCH DOWN (262k → 100k / dial-down)** when the upcoming phase needs, on
  a 100k card that stays alive: **use case 1 — the GPU** (the `:8000`
  embedder+reranker on CUDA, ~5.3 GB, beside Qwen — live span-recall probes,
  page-runs, `/context` work) **or use case 2 — subagent parallelism**
  (extraction/reading/review fan-out, ≤2 in parallel). 262k is the inline-
  linear-work mode; the only >2 parallelism is `llm-council` (5, the
  standing exception, any mode).
- **Use case 3 — the A/B two-terminal bay** (`ab-bay` skill): the 100k dial
  is what lets in-process CUDA jobs and `:8000` co-locate. The bay's full
  sequence is switch → restart the invoking terminal → open the two
  terminals (A controls the GPU, B works the job); this skill owns only
  the switch step. Inside the bay, A enforces the no-CPU->15 s rule (stop a
  slow CPU process, rerun on CUDA) with the dial already at 100k — no
  further switch needed for that.
- **NO SWITCH for a heavy Qwen LLM batch** (`events-extract` / 27B
  extraction). The hard rule is the opposite: stop `:8000` (or run it on CPU),
  Qwen owns the card. Context mode is irrelevant there.
- **SWITCH BACK (→ 262k)** when the GPU phase ends and the remaining work is
  linear/exploratory (full context; `:8000` returns to CPU).

## Pre-flight (model alive — before the switch call)

1. **Checkpoint** (see the `switchpoint` skill): `git commit` + refresh
   `plan/SWITCHPOINT.md` (mode, sha, position, in-flight, exact next step).
2. **Fit guard**: the current transcript must fit the target context:
   ```bash
   echo $(( $(wc -c < "$PI_SESSION_FILE") / 4 ))   # est. tokens of THIS session (CONSERVATIVE — overstates real ~2.7x)
   ```
   Estimate exceeds the target (102400 for 100k) → judge the *real* count
   (estimate ÷ ~2.7): real fits → launch with `FORCE=1` (deliberate handoff;
   the session survives and auto-compacts if the first turn overflows — the
   01:43 run: est 114k, real ≈42k, FORCE=1, clean). Real does NOT fit →
   full checkpoint, then the fresh-session handoff one-liner (below).
   Never FORCE past a real overflow (00:3x incident: the compact call itself
   400'd and stranded the session model-less).
3. **No extraction in flight**: `pgrep -af 'events[-_]extract'` empty (the
   script refuses too).

## The switch — 3-part shell flow, the agent always exits (owner standard 2026-09-10)

**Every context switch ends the pi agent, and the whole thing runs in one
detached shell — no typed commands, no tmux, no capture-pane.** The LLM
readiness call is made *internally by the switch shell* (HTTP to :18080) and
it is that call which triggers the relaunch (owner correction 2026-09-10: it
must never be typed into the pi pane). The owner's terminal app is
**gnome-terminal** (not tmux). Owner's words on the exit: "every time you
switch the context, you will have to exit pi agent, then come back to this
session" — the relaunch resumes the SAME session automatically, zero owner
input.

One detached launch — the agent's last act; the helper survives the agent's
death:

```bash
setsid nohup bash tools/master-work/switch_restart3.sh <mode> <session_file> <my_pi_pid> <old_shell|none> < /dev/null > /dev/null 2>&1 &
# env: FORCE=1  -> pass --force to part 2 (pre-flight est > target, real fits)
# env: SKIP_LLM=1 -> part 3 polls /v1/models instead of the LLM call (fallback)
```

- `<session_file>` = this session's jsonl, FULL path (the relaunch runs
  `pi --session <full path>` — never `pi -c`, which is ambiguous while the
  owner's second pi is running).
- `<my_pi_pid>` = the pi serving THIS session, verified live (the $PPID
  chain), never from memory, never `pgrep -x pi | head -1`.
- `<old_shell>` = the window's separate shell pid when the window is
  user-launched (a bash that parented pi); `none` when the window was opened
  as `gnome-terminal -- bash -lc '... exec pi'` (pi IS the window's process
  — the window self-closes when the old pi dies).

The helper's sequence (log `/tmp/switch_restart3.log`):
1. **part 1** `ninfer-stop.sh` — immediate unload.
2. **part 2** `qwen-switch.sh <mode> --api [--force]` — load, health poll,
   models.json contextWindow sync, `:8000` placement (CUDA iff headroom
   ≥ 6 GiB, else CPU), `qwen_mode.txt`.
3. **part 3** internal LLM call (curl :18080/v1/chat/completions) — proves
   the model live from inside the shell; on answer → `relaunch_term.sh`:
   new gnome-terminal window (`DISPLAY=:0 setsid gnome-terminal -- bash -lc
   "cd /home/goblin/ScriptEngine && exec pi --session <session_file>"`) →
   wait for the new pi pid (any `pgrep -x pi` not in the pre-list) →
   TERM → old pi, VERIFY death, escalate KILL -9 → close the old window
   (separate shell: same TERM→verify→KILL-9 escalation; `none`: no-op).

Retired, do not use: the tmux helpers `switch_restart.sh` /
`switch_restart2.sh` / `relaunch_pi.sh` (+ `/tmp/resume_msg.txt` typed
resume). Inline `./qwen-switch.sh` from a running session is retired too
(the 00:5x incident: agent died mid-reload).

## The window is per pi-process (owner 2026-09-10)

pi snapshots the model's contextWindow at STARTUP. A pi process started
under one mode keeps that mode's window in memory for its whole life — its
status line (`X%/Yk`) and its auto-compact threshold stay on the old dial;
the switch only rewrites `~/.pi/agent/models.json`, which live pi's never
re-read. So after EVERY switch, EVERY pi running the session must exit and
come back: the 3-part helper relaunches the directing pi (gnome-terminal,
`pi --session <full path>`); any OTHER pi (the owner's terminal pi, a
subagent host started pre-switch, e.g. the pi-csm tmux pi) is manual —
`exit`, then `pi -c` in the project dir. The helper records the pre-existing
pi pids so it never mistakes one of them for the new pi. Before trusting
work in the restarted pi, verify its status line shows the NEW window.
Incident (2026-09-10 01:0x): the owner's pi (started 00:38, 100k era) still
showed `/102k` after the 262k switch while the helper-restarted pane pi
showed `/262k` — the owner read the stale pi and ruled the switch failed.

## Post-flight (the new pi, same session)

The relaunched pi starts *after* the load, so it snapshots the NEW
contextWindow — its status line is trustworthy (see "The window is per
pi-process"). It verifies, reports to the owner in ONE line, then **STOPS**
(no work until the owner speaks):

1. Status line shows the new window (`/102k` or `/262k`).
2. `cat /home/goblin/ninfer-work/qwen_mode.txt` (mode, ctx, free MiB, api).
3. `tail /tmp/switch_restart3.log` — `part3: internal LLM call answered`,
   `new pi pid=…`, `old pi gone`, the window line, `relaunch_term done`.
4. `pgrep -P 3439` (gnome-terminal-server) — only the new pi's window
   process remains (a lingering *blank* window is the terminal's
   keep-on-exit setting — its process is dead; note it, don't chase it).

Report: state (mode/ctx/free/api) + "3-part flow ran end-to-end, zero owner
input." First model turn after the switch is a cold prefill (~1–2 min).

## Overflow: when it is self-handling, and when it strands you

The fit guard is conservative (bytes/4 overstates the real token count
~2.7x). If the running session's context exceeds the server cap mid-work
BUT the auto-compaction itself fits the cap, ninfer returns `400
context_length_exceeded`; pi-ai's generic overflow pattern matches it and
the session auto-compacts + retries the turn — no approval, no user
involvement.

**It does NOT self-handle when the compaction itself doesn't fit** (the
2026-09-10 00:3x incident: a ~400k session switched to 100k; the prepared
prompt was 242k tokens vs the 102k cap — the compact call itself 400'd, the
turn died, and the session was stranded model-less; the owner restored 262k
by hand). That is exactly the case the pre-flight fit guard predicts: if the
REAL token count of THIS session > the target ctx, do not FORCE — full
checkpoint + fresh-session handoff. If only the conservative estimate exceeds
the target, `FORCE=1` is the sanctioned path (the session auto-compacts the
first turn if needed).

## The overflow handoff (only if the REAL transcript doesn't fit)

After a down-switch where the real transcript overflows the new cap (the
fresh-session case of the pre-flight fit guard — never a FORCE case),
everything is on disk — hand off with:

> "Switched to 100k; the transcript didn't fit, so this session ends here.
> Open a fresh `pi` in the project dir and say: *Read plan/SWITCHPOINT.md
> and continue from there.*"

## Never

- Switch before the checkpoint is complete.
- `--force` when the REAL transcript doesn't fit the target (the handoff one-
  liner is owed instead; the 00:3x incident is what that looks like).
- Run the switch inline at all, or let the agent chat across a switch:
  every context switch exits the pi agent and the helper relaunches into the
  SAME session (owner mandate 2026-09-10; the 00:3x + 00:5x incidents) —
  `tools/master-work/switch_restart3.sh` is the only path.
- Type the LLM call or the relaunch into the pi pane (or any tmux pane):
  the LLM call is INTERNAL to the switch shell (owner correction 2026-09-10);
  the relaunch is a gnome-terminal window running `pi --session <full path>`
  — never `pi -c`, never tmux.
- Claim "window closed" on signal delivery: this machine's interactive bash
  SURVIVES SIGTERM (proven twice, 2026-09-10) — verify process death and
  escalate to KILL -9 (relaunch_term.sh does this; a bare `kill && log`
  is how the 01:37 run left the old window open).
- Rely on *proactive* compaction in a session started under a different mode
  than the current one (its declared contextWindow is stale; the sync now
  happens per switch, but pre-existing sessions need the real transcript
  size measured). Reactive overflow is different and IS automatic when it
  fits: ninfer's `400 context_length_exceeded` triggers pi's built-in
  compact-and-retry.
- Trust a pi process that was started before the latest switch — its window
  is a startup snapshot (see "The window is per pi-process"): restart it
  (`exit` + `pi -c`) or treat its `X%/Yk` line as wrong.
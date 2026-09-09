---
name: qwen-switch
description: Switch the local Qwen 3.8 27B (ninfer, :18080) between context modes — 262k exploratory, 100k service, or a dial-down — to free or reclaim GPU headroom, autonomously, mid-plan. Use when the next phase needs the :8000 embedder+reranker on CUDA alongside Qwen, or 2 parallel subagents, and when the GPU phase ends and full context is wanted again.
---

# qwen-switch — autonomous Qwen context-mode switching

Full doc: `docs/ops/QWEN_MODES.md` (repo = /home/goblin/ScriptEngine).
Kit doc: `pi.md` §5 (autonomous protocol).
Switcher: `/home/goblin/ninfer-work/qwen-switch.sh` (has `--dry-run`, `--api`, `--force`).

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
   echo $(( $(wc -c < "$PI_SESSION_FILE") / 4 ))   # est. tokens of THIS session
   ```
   If it exceeds the target (102400 for 100k): the switcher hard-refuses
   (exit 2). Do a full checkpoint, re-run with `--force`, and hand the user
   the fresh-session one-liner (below). `--force` is only for a deliberate
   handoff — never a dodge.
3. **No extraction in flight**: `pgrep -af 'events[-_]extract'` empty (the
   script refuses too).

## The switch — the agent always exits, the owner relaunches (MANDATORY, owner 2026-09-10)

**Every context switch ends the pi agent.** Owner's words: "every time you
switch the context, you will have to exit pi agent, then come back to this
session, you cant just change context and start chatting here." So the ONLY
sanctioned flow is the detached all-in-one helper (kill pi → switch →
relaunch pi → typed resume line → capture-pane verify — the only safe order):

```bash
setsid nohup bash tools/master-work/switch_restart.sh <mode> /tmp/resume_msg.txt <my_pi_pid> < /dev/null > /dev/null 2>&1 &
```

- `<my_pi_pid>` = the pi serving THIS session, verified live (the pane pid
  whose pi child is the directing session — `tmux list-panes -a` + `pgrep -x
  pi` with a ppid check). Never from memory, and never `pgrep -x pi | head -1`
  when other pi processes exist (the owner runs a second pi).
- The helper switches with `--force` by design: the flow is always a
  handoff, and the fit guard cannot be consulted after pi is gone. The
  pre-flight fit measurement (above) decides what the resume line says:
  session fits the new dial → "come back to this session, then <next step or
  stop>"; it does NOT fit → the fresh-session handoff one-liner (below).
- The invoking session dies at the grace (5 s) mid-tool-call — expected;
  the helper is setsid-detached and finishes the whole flow alone (log
  `/tmp/switch_restart.log`, including a capture-pane proof of the resume
  line).
- Inline `./qwen-switch.sh` from a running session is RETIRED (2026-09-10,
  this mandate): even when the transcript fits, the agent never chats across
  a model recycle — the 00:5x 100k attempt that died mid-reload (the owner
  restored 262k by hand) is the second incident behind the rule.

## The window is per pi-process (owner 2026-09-10)

pi snapshots the model's contextWindow at STARTUP. A pi process started
under one mode keeps that mode's window in memory for its whole life — its
status line (`X%/Yk`) and its auto-compact threshold stay on the old dial;
the switch only rewrites `~/.pi/agent/models.json`, which live pi's never
re-read. So after EVERY switch, EVERY pi running the session must exit and
come back: the helper restarts the tmux directing pi; any OTHER pi (the
owner's terminal pi, a subagent host started pre-switch) is manual —
`exit`, then `pi -c` in the project dir. The helper prints a
`WARNING: stale pi(s)` line for the ones it cannot restart. Before trusting
work in the restarted pi, verify its status line shows the NEW window.
Incident (2026-09-10 01:0x): the owner's pi (started 00:38, 100k era) still
showed `/102k` after the 262k switch while the helper-restarted pane pi
showed `/262k` — the owner read the stale pi and ruled the switch failed.

## Post-flight (model back)

1. `cat /home/goblin/ninfer-work/qwen_mode.txt` (mode, ctx, free MiB, api device).
2. `nvidia-smi` sanity. The script already placed `:8000` on the right device
   (CUDA iff headroom ≥ 6 GiB, else CPU) and synced `~/.pi/agent/models.json`
   `contextWindow` to the mode (header + proactive auto-compact threshold).
3. Continue the plan from the switchpoint. First turn is a cold prefill (~1–2 min).

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
by hand). That is exactly the case the pre-flight fit guard predicts: if
`wc -c/4` of THIS session > the target ctx, do not switch inline — use
`tools/master-work/switch_restart.sh` (kill → switch → relaunch pi, one
detached helper).

## The overflow handoff (only if you want clean state)

After a `--force` down-switch the current session is done (its transcript
overflows the new cap). Everything is on disk — hand off with:

> "Switched to 100k; the transcript didn't fit, so this session ends here.
> Open a fresh `pi` in the project dir and say: *Read plan/SWITCHPOINT.md
> and continue from there.*"

## Never

- Switch before the checkpoint is complete.
- `--force` past a fit refusal without a full checkpoint (the handoff one-
  liner is still owed if you want clean state).
- Run the switch inline at all, or let the agent chat across a switch:
  every context switch exits the pi agent and the owner relaunches into the
  same session (owner mandate 2026-09-10; the 00:3x + 00:5x incidents) —
  `tools/master-work/switch_restart.sh` is the only path.
- Rely on *proactive* compaction in a session started under a different mode
  than the current one (its declared contextWindow is stale; the sync now
  happens per switch, but pre-existing sessions need the real transcript
  size measured). Reactive overflow is different and IS automatic when it
  fits: ninfer's `400 context_length_exceeded` triggers pi's built-in
  compact-and-retry.
- Trust a pi process that was started before the latest switch — its window
  is a startup snapshot (see "The window is per pi-process"): restart it
  (`exit` + `pi -c`) or treat its `X%/Yk` line as wrong.
---
name: opencode-watch
description: Keep a local opencode TUI (PID via `pgrep -x opencode`, window title `OC | …`) running autonomously — the watcher (tools/master-work/oc-watch.sh) watches opencode's log for blocked prompts and auto-answers permission dialogs with "always allow" (typing into the window), wakes the pi session for MCQ questions, and nudges dead runs. Use when the user wants opencode left alone to work, when an opencode run stalls on a permission prompt, or when setting up/tearing down the opencode watcher.
---

# opencode-watch — autonomous opencode TUI supervision

Repo: `/home/goblin/ScriptEngine`. opencode runs in a gnome-terminal window whose title it
sets itself (`OC | <current task>`). The pi agent runs in the window titled
`π - ScriptEngine`. Both are supervised by log files, not screen-reading (no vision here).

## The one fact this skill is built on

**opencode's log is ground truth.** `~/.local/share/opencode/log/opencode.log` gets a new
line only while opencode is working. Markers:

- `message=asking id=per_… permission=X patterns="[…]"` — a permission dialog is open.
  Resolved when the log advances past it (there is **no** `replied` line for `per_`; the
  next `tracking`/`process`/`stream` line is the signal).
- `message=asking id=que_… questions=N` — an MCQ. Resolved by a `replied requestID=que_…`
  line. Question text lives in `~/.local/share/opencode/opencode.db` (see below).
- `message=evaluated permission=X pattern=… action.action=ask` — a request was made. If the
  matched rule is `action=allow` (exact pattern, not `pattern=*`), it auto-passed — that is
  what a working "always allow" looks like.
- `message=tracking / process / stream` — the run is alive and calling the model.
  A `tracking` line with **nothing after it** for >1 min = the run is stuck or ended.
- `message=stream` + an ESTAB socket to `:18080` from the opencode pid
  (`ss -tnp | grep :18080`) = actively generating.

A blocked prompt ⟺ the **last line of the log** is an unresolved `asking` entry (opencode is
silent while blocked). Stacked dialogs: a turn can log TWO `asking` lines (two parallel tool
calls) — answering one still leaves the run blocked until the other is answered.

## Keymap (reverse-engineered from `~/.opencode/bin/opencode`, 2026-09-13)

Permission dialog options `[Allow once | Always allow | Reject]`, default selection
`"once"`. Keys: `Right`/`l`/`Tab` = next option, `Return` confirms. Confirming
"Always allow" opens a second confirm stage (`Enter` again sends the reply).
So **always-allow = `Right` → `Enter` → `Enter`** from the default state. A dialog for a
*new request id* always resets to the default state, so the sequence is deterministic
for a fresh dialog.

MCQ dialog (bundle state: `{tab, answers[], custom[], selected, editing}`): keymap NOT
verified live yet — when a `que_` appears, wake pi (the watcher does this), read the
question from the db, decide, and figure out the keys on the spot (try `j`/`k` or
`Up`/`Down` + `Return`; a `replied requestID=que_…` log line proves it landed). Update this
skill when verified.

## Typing rules (vte — from terminal-pilot, do not break)

- `xdotool windowactivate --sync $W` first, then plain `xdotool type --clearmodifiers …` /
  `xdotool key …`. **Never `xdotool key --window` / `type --window`** — vte ignores synthetic
  XSendEvent; keys silently do not land.
- Find the opencode window: `xdotool search --name '^OC '` (title prefix is stable even
  though the task suffix changes). Fallback: gnome-terminal windows that are neither
  `π - ScriptEngine` nor bare `Terminal`.
- Prove a key/type landed via the **log** (new line / advanced `tracking`), not by
  assumption. If the last line is still `asking` after a key sequence, the dialog state was
  not what you assumed (e.g. the user moved it) — re-check and retry once, then stop and
  ask.

## Persistent permission rules (the real fix)

`~/.config/opencode/opencode.jsonc` has a `"permission"` section (tool-level allow-rules,
survive restarts). On 2026-09-13 `"external_directory": "allow"` was added (backup
`opencode.jsonc.bak-ocwatch`) so ninfer-work reads never prompt. Add new tool-level rules
the same way when a whole *class* of prompt is unwanted; keep per-occurrence prompts to the
watcher. Note: config is read at opencode startup — a rule added while opencode runs takes
effect on next start (the in-session "always" grant covers the running process).

## The watcher

```bash
# start (survives tool-call abort; status lines in /tmp/oc_watch.log)
setsid nohup bash tools/master-work/oc-watch.sh >/tmp/oc_watch.out 2>&1 </dev/null &
# stop
kill $(cat /tmp/oc_watch.pid)
# check
tail /tmp/oc_watch.log
```

Behavior (10 s poll, all in `tools/master-work/oc-watch.sh`):
- last log line `asking per_…` + unseen id → types the always-allow keys into the OC window
  (set `OC_WATCH_NO_AUTO=1` to wake pi instead of auto-answering).
- last log line `asking que_…` → wakes pi by typing a one-line prompt into the
  `π - ScriptEngine` window (pi then answers the question).
- no log activity for 300 s AND no `:18080` connection from the opencode pid AND the last
  big log event is **not** `exiting loop` (a finished run sits at the idle prompt — silent
  with no qwen conn is *normal*, never nudge it) → types a "Continue the current task…"
  nudge. Two hard stops: a session whose last turn ended in `level=ERROR` is **never**
  nudged (turns keep failing the same way — it wakes pi once instead, marker
  `/tmp/oc_watch_woken`), and the nudge count is capped at **3 per watcher lifetime**
  (persisted in `/tmp/oc_watch_nudges`) so a bad state can never spam the prompt.
- opencode not running → idle-polls (re-engages automatically on restart).

Wake lines typed into pi look like:
`oc-watch: opencode blocked on question que_… (MCQ) - read it from opencode.db and answer.
Handle per .pi/skills/opencode-watch.` — treat that line as a task, not chat.

## When woken for a `que_` (MCQ)

```bash
python3 - <<'EOF'
import sqlite3, json
db = sqlite3.connect('file:/home/goblin/.local/share/opencode/opencode.db?mode=ro', uri=True)
# newest assistant message of the live session carries the question part
S = '<session id from the log line: session.id=ses_…>'
for mid, data in db.execute("SELECT id, data FROM message WHERE session_id=? ORDER BY time_created DESC LIMIT 5", (S,)):
    for (row,) in db.execute("SELECT data FROM part WHERE message_id=?", (mid,)):
        p = json.loads(row)
        if p.get('type') in ('question', 'task') or 'questions' in p:
            print(mid, json.dumps(p)[:1500])
EOF
```

Decide the answer (pick the option that serves the owner's task; when torn, wake the
owner). Type the answer into the OC window and verify via the `replied requestID=que_…`
line.

## When woken for a `per_` (should only happen with OC_WATCH_NO_AUTO=1)

Type `Right` `Enter` `Enter` into the OC window (rules above), verify the log advanced.
If the same pattern keeps prompting across *new* requests (a minute apart, each a fresh
`asking`), the in-session "always" is not sticking — add the tool-level rule to
`opencode.jsonc` and tell the owner opencode must restart for it to apply.

## Lessons from 2026-09-13 (the ninfer-start session)

- The `--window` XSendEvent attempt was silently ignored — that is why "nothing happened"
  for the first key sequences; the fixed sequence (activate + plain keys) landed immediately.
- Two stacked `asking` lines = two dialogs; one key sequence answers only the shown one.
- A run can *end* (not just block) after rejected/denied tool calls: last assistant turn
  `finish=tool-calls` with tool states `error`, then log silence. Revival = a typed
  "Continue …" message, not keys.
- `tracking` with nothing after it is NOT proof of death (a long bash tool is quiet) — the
  stall check requires BOTH no log activity AND no `:18080` connection.
- Neither is enough (2026-09-13 bug #1): a *finished* run at the idle prompt is also
  silent + no qwen conn — the watcher must additionally require the last big event to be
  `stream`/`process` (not `exiting loop`) before nudging, or it types "Continue" into an
  opencode that is merely waiting for its next task.
- And again (bug #2, same day): a *crashed* session's last big event is `message=process`
  with `level=ERROR` (no `exiting loop`) — that looks "mid-turn" to the stall check, every
  nudge starts a turn that fails the same way, and the loop runs forever (22 spam messages
  observed). Hence the two hard stops: no nudge after an ERROR last event (wake pi once),
  and an absolute 3-nudge lifetime cap persisted to disk.
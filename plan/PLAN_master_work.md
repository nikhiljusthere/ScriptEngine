# Master/Work (A/B) Deployment Plan

Owner: goblin · 2026-09-08 · status: draft for council review (§9). One local Qwen 27B (ninfer `:18080`, ctx 135168, vision on) serves A, B, the loop and all subagents; the `:8000` ScriptEngine API runs on CPU.

## 1. Purpose — the failure this fixes

The CSM campaign session overflowed at **102,518 tokens vs the 102,400 limit** (Qwen 100k mode) and summarization recovery failed too — one context doing strategy *and* execution drowns; the plan got buried under 90k+ tokens of tool output. This plan deploys the two-session architecture:

- **Session A (CONTROL, "master")** — a *thin* LLM supervisor: strategy only (plan, decisions, vetoes, priorities); tools = state files + spawn/kill B + tmux control (§2). Context < 30k; runs for days, never approaches overflow.
- **Session B (WORK)** — a disposable executor: the campaign (first queued workload: the **paused CSM 100%** campaign, resumed via `plan/SWITCHPOINT.md`) plus the new **PC-control loop**. Big context, dies often (overflow, model reloads, terminal death); on death A respawns B from the state files — the plan never lived in B, so nothing is lost.

Hard rules (invariant; restated in `plan/CONTROL.md`):

1. **ONE-WAY FLOW.** B appends reports/recommendations to disk; A decides and writes decisions to disk. B never changes the plan — it escalates ("hit X, recommend Y") and A rules.
2. **A STAYS THIN.** A's tools are the fixed list in §2; if A starts executing work it has already failed — kill A, rebuild from disk.
3. **DISK IS THE TIEBREAKER.** State files beat either session's memory — the `plan/SWITCHPOINT.md` ritual (hand-written state + append-only log): a session transition is a commit, not a transcript.

## 2. Roles & tool boundaries

| | Session A (CONTROL) | Session B (WORK) |
|---|---|---|
| context | < 30k tokens, bounded reads | big; expected to die |
| allowed | read `state.md`, `decisions.md`, work_log tail, `STOP`; edit `state.md §state`; write `decisions.md`; create/delete `STOP`; tmux spawn/kill/has-session | full kit: read/bash/edit/write + subagents; campaign tools (`pytest`/`eval`/`index`/`span-recall`); `setsid`-launching the PC loop |
| forbidden | reading code or any repo file outside the state files; running campaign commands; editing the worktree | writing `decisions.md`; editing `state.md §state`; acting on a recommendation before a `DEC` line exists |

Formats — escalation (B → A; B appends to `state.md §B updates`): `[ts] ESC <unit>: hit <X> — recommend <Y> (evidence: <path>)` · decision (A → B; A prepends to `decisions.md`, newest first): `[ts] DEC <unit>: APPROVE | VETO <rule> | REDO <rule> — re ESC <unit>-<seq>`

## 3. Shared-truth file layout

All under `/home/goblin/ScriptEngine`. Each file carries at most one **hand-written block** (edit-in-place) and at most one **append-only log** (append at EOF, never rewrite) — the SWITCHPOINT split, applied per file.

| file | who writes | who reads | content |
|---|---|---|---|
| `plan/CONTROL.md` | A at bootstrap; A edits only with a `DEC` on record | B (at boot) | A's charter: hard rules, A-loop spec (§4.4), formats (§2), loop guards (§5) |
| `plan/state.md` `§state` | **A edits in place** | both | position, next unit, open risks, `a_session`, `b_session`, loop status |
| `plan/state.md` `§B updates` | **B appends** | A | position updates + `ESC` lines (the escalation queue) |
| `plan/decisions.md` | **A only** (prepend, newest first) | B (`head -20`) | one `DEC` line each; B never writes this file |
| `reports/master-work/work_log.md` | **B only** (append; the loop appends its own lines) | A (`tail -20`) | execution events `[ts] KIND unit: detail`, KIND ∈ DONE/ACT/FAIL/HALT |
| `reports/master-work/STOP` | A creates/deletes | loop + B | content `STOP <ts> reason=…`; its existence halts the loop |

Write rules: append-only logs take `printf '%s\n' '<line>' >> file` (EOF only; a full rewrite is a violation), `decisions.md` is newest-first (A prepends); ownership never overlaps — A owns `decisions.md` + `state.md §state` + `STOP`, B owns `work_log.md` + `state.md §B updates`; commits use named paths, `control:` prefix for A, B's own prefixes, no push.

## 4. Bootstrap

### 4.1 Preflight (one-shot)

```bash
cd /home/goblin/ScriptEngine
curl -s -m 2 http://127.0.0.1:18080/v1/models >/dev/null && cat /home/goblin/ninfer-work/qwen_mode.txt   # expect ctx=135168 vision=on api=cpu
tmux kill-session -t control 2>/dev/null; tmux kill-session -t work 2>/dev/null; mkdir -p reports/master-work tools/pcloop
# Skeletons: plan/CONTROL.md (charter = §1 rules + §2 formats + §4.4 A-loop + §5 guards); plan/state.md (§state + §B updates),
#            plan/decisions.md + reports/master-work/work_log.md (headers only); tools/pcloop/loop.py from §5.2 (one-time; B commits it)
git add plan/CONTROL.md plan/state.md plan/decisions.md reports/master-work/work_log.md
git commit -m "control: bootstrap master-work state files"
```

### 4.2 Start A (control session)

```bash
tmux new-session -d -s control -c /home/goblin/ScriptEngine 'pi "Read plan/CONTROL.md — it is your standing instruction (charter + A-loop spec). Read plan/state.md and plan/decisions.md. Enter the A-loop. Never execute campaign work."'
# A records its own session-file path as a_session in state.md §state (newest .jsonl under ~/.pi/agent/sessions/--home-goblin-ScriptEngine--);
# A's whole context at boot = CONTROL.md + state.md + decisions.md (+ work_log tail)
```

### 4.3 Spawn B (work session)

```bash
tmux new-session -d -s work -c /home/goblin/ScriptEngine 'pi "Boot: read plan/CONTROL.md + plan/state.md §state. Execute §next-unit. Append DONE/ACT/FAIL/HALT lines to reports/master-work/work_log.md; escalate via plan/state.md §B updates (hit X, recommend Y). Launch the PC-control loop per §5."'
# A records the new session file as b_session in state.md §state (ls -1t ~/.pi/agent/sessions/--home-goblin-ScriptEngine--/*.jsonl | head -1)
```

- **Terminal death** (pane dead, session file fits — §6.2): `b=$(sed -n 's/.*b_session:[[:space:]]*//p' plan/state.md | head -1)` then `tmux new-session -d -s work -c /home/goblin/ScriptEngine "pi --session $b"`.
- **Transcript overflow**: A re-runs the boot message with plain `pi` (fresh identity) and records the new `b_session`. **Model reload** needs no respawn — panes and processes survive, both continue when the model returns (§6.3).

### 4.4 A-loop (A's only behavior; P=60 s, K=20 tail, 300 s staleness; spec lives in `CONTROL.md`)

```python
while True:
    st, log, dec = read('plan/state.md'), tail('reports/master-work/work_log.md', 20), head('plan/decisions.md', 20)
    if exists('reports/master-work/STOP'): kill_loop(); kill_B(); break
    for e in unrulled_escalations(st, dec):   # ESC lines with no matching DEC
        prepend(f"[ts] DEC {e.unit}: {decide(e, st)}", 'plan/decisions.md'); update_state(e, st)   # APPROVE|VETO|REDO
    if not alive_B(): respawn_B(st)           # §4.3 / §6.2 fit-check → resume or fresh
    if stale(log, 300): kill_B(); respawn_B(st, fresh=True)
    sleep(60)
```

### 4.5 Verify the bootstrap

```bash
tmux ls                                       # both 'control' and 'work' present
tail -3 reports/master-work/work_log.md       # B's first lines
pgrep -f 'tools/pcloop/loop.py'               # the loop runs under setsid
```

If A itself dies (tmux server death, reboot): re-run §4.2 + §4.3 — A has no state beyond the state files (that is the design, §6.4); last-resort read-only peek: `tmux capture-pane -t work -p | tail -5`.

## 5. PC-control loop (`tools/pcloop/loop.py`)

A stateless, tick-driven executor: every tick the loop takes a `scrot` screenshot, asks the local 27B vision model for **one** action (screenshot + last K `work_log` lines in, JSON action out), executes it via `xdotool`, and appends action+result to `work_log` — all memory is the tail of `work_log`, and the process is disposable (any guard trip halts + exits; B or A relaunches explicitly).

### 5.1 Action JSON schema (allowlist of 8)

The model replies with exactly one JSON object `{"action": "<name>", ...fields, "reason": "<one line>"}` (parse first `{` → last `}`, prose tolerated; unparseable, or any other `action` value / missing required field, → `reject`, never executed, counts toward the no-op streak).

| action | fields (beyond `action`/`reason`) |
|---|---|
| `click` | `x`, `y`, `button` (1 left / 2 middle / 3 right, default 1) |
| `double_click` | `x`, `y` |
| `type` | `text` (typed into the focused window) |
| `key` | `combo` (xdotool key names: `ctrl+shift+t`, `Return`, …) |
| `scroll` | `direction` (up/down/left/right, default down), `amount` (default 3), `x`, `y` |
| `wait` | `seconds` (capped at 10) |
| `done` | `note` — goal reached; loop exits cleanly |
| `abort` | `reason` — goal unreachable/unsafe; loop exits |

### 5.2 Pseudocode (stdlib + `requests`)

```python
import base64, json, re, subprocess, time, pathlib, requests
URL, MODEL = "http://localhost:18080/v1/chat/completions", "qwen3.8-27b-ninfer"
LOG, STOP = pathlib.Path("reports/master-work/work_log.md"), pathlib.Path("reports/master-work/STOP"); TICK, K, MAX_TICKS, MAX_NOOPS = 20, 10, 120, 5
ALLOW = ("click", "double_click", "type", "key", "scroll", "wait", "done", "abort")
TASK = "Finish the pcloop goal in plan/state.md §state; one small action per reply."  # B sets per session
def log(msg):
    with LOG.open("a") as f: f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {msg}\n")
def shot():
    subprocess.run(["scrot", "/tmp/pcloop.png"], check=True, stdout=subprocess.DEVNULL); return base64.b64encode(pathlib.Path("/tmp/pcloop.png").read_bytes()).decode()
def ask(img):
    tail = "\n".join(LOG.read_text().splitlines()[-K:]) if LOG.exists() else ""
    r = requests.post(URL, timeout=90, json={"model": MODEL, "max_tokens": 2048, "messages": [{"role": "user", "content": [
        {"type": "text", "text": f"Task: {TASK}\nRecent work_log:\n{tail}\nReply with ONE JSON object; action in: " + "|".join(ALLOW)},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + img}}]}]})
    r.raise_for_status()
    return json.loads(re.search(r"\{.*\}", r.json()["choices"][0]["message"]["content"], re.S).group(0))
def run(a):  # argv-list xdotool only: model-supplied text/combo can never become shell injection
    n, x, y = a.get("action"), a.get("x", 0), a.get("y", 0)
    if n not in ALLOW: return "reject"
    if n == "wait": time.sleep(min(int(a.get("seconds", 2)), 10)); return "no-op"
    if n in ("done", "abort"): return n
    cmd = {"click": ["xdotool", "mousemove", str(x), str(y), "click", str(a.get("button", 1))],
           "double_click": ["xdotool", "mousemove", str(x), str(y), "click", "--repeat", "2", "1"],
           "type": ["xdotool", "type", "--delay", "30", a["text"]],
           "key": ["xdotool", "key", a["combo"]],
           "scroll": ["xdotool", "mousemove", str(x), str(y), "click", "--repeat", str(a.get("amount", 3)),
                      {"up": "4", "down": "5", "left": "6", "right": "7"}.get(a.get("direction", "down"), "5")]}[n]
    subprocess.run(cmd, check=True); return "ok"
def main():
    noops = ticks = 0
    while ticks < MAX_TICKS:
        if STOP.exists(): log(f"HALT pcloop: STOP veto ({STOP.read_text().strip()})"); return
        try: a = ask(shot())
        except Exception as e: log(f"FAIL pcloop: vision ({str(e)[:80]})"); res = "no-op"
        else: res = run(a); log(f"ACT pcloop: {json.dumps(a)} -> {res}")
        ticks += 1
        if res in ("done", "abort"): return; noops = noops + 1 if res in ("no-op", "reject") else 0
        if noops >= MAX_NOOPS: log("HALT pcloop: no-op streak"); return
        time.sleep(TICK)
if __name__ == "__main__": main()
```

### 5.3 Guard rails

1. **Action allowlist** — the 8 actions only; unknown/malformed → `reject`, never executed, counts as a no-op.
2. **Rate limit** — synchronous loop ⇒ at most one in-flight vision request; tick floor `TICK=20 s`; the vision call has a 90 s hard `timeout` — a dead/slow model logs `FAIL`, counts as a no-op, and trips the streak guard instead of hanging the loop.
3. **No-op abort** — `MAX_NOOPS=5` consecutive no-ops (`wait`/`reject`/vision failure) → `HALT` line + exit; stuck-on-a-screen is what this catches, and restart is explicit.
4. **STOP veto (A/human)** — A writes `reports/master-work/STOP` (content = reason); checked *before* every tick's vision call (veto latency ≤ 1 tick); A deletes it to authorize a relaunch (fresh budget). Only A writes this file.
5. **Max-session budget** — `MAX_TICKS=120` (~40 min) hard cap per process; each relaunch starts a fresh budget, so a campaign is a chain of bounded sessions, each resuming from `work_log` + `state.md`.

### 5.4 Launch (B, never A)

```bash
cd /home/goblin/ScriptEngine
DISPLAY=:0 setsid nohup scriptengine/.venv/bin/python tools/pcloop/loop.py >> /tmp/pcloop.log 2>&1 < /dev/null &
# confirm (fast, separate call): ps -ef | grep pcloop/loop.py · kill: pkill -f 'tools/pcloop/loop.py' (or write STOP — the loop exits itself)
# if B dies the loop keeps running (setsid); the respawned B re-attaches via this log
```

## 6. Kill/resume semantics

### 6.1 B overflow (`context_length_exceeded`) — respawn, not resume

Four death classes; the binding rule is **disk is the tiebreaker**, and B's checkpoint-per-unit discipline (after every unit: `state.md` position + `work_log` line) means no death loses more than the in-flight unit — and never the plan, which never lived in B. Overflow (the CSM failure mode): A's next poll sees B's failure marker (work_log / tmux pane). A does **not** `pi --session` the dead transcript — it is still over the limit, so resuming re-overflows on the first turn. A spawns a **fresh** B (§4.3), seeded with `state.md` + newest `decisions.md` lines + last K `work_log` lines; A confirms (or re-issues as a DEC line) the in-flight unit. Loss = at most the in-flight unit, re-runnable by construction.

### 6.2 B terminal death (tmux pane / host) — resume if it fits, respawn if not

A's poll finds `tmux has-session -t work` false. Fit check (the same conservative bytes/4 estimate `qwen-switch.sh` uses): session file fits the current ctx mode → `pi --session <b_session>` resumes in place (crash with a still-valid transcript — pane crash, OOM); does not fit → the §6.1 respawn. A host reboot takes tmux, `:8000` and `:18080` with it: recovery is §4.1–4.3 replayed in order (Qwen → `:8000` on CPU → tmux `control` → tmux `work`) — disk state survives, so a replay, not a rebuild.

### 6.3 Qwen mode reload — the switchpoint ritual, not a death

A ninfer restart / `qwen-switch.sh` run leaves both sessions model-less for 30–60 s; tmux and session files survive and both continue after the reload. The ritual (reused from `plan/SWITCHPOINT.md`, not reinvented): fill the hand-written section **before** the switch (A is fully re-seedable from `CONTROL.md` + `decisions.md` + `state.md`; B's position is already in `state.md` by unit discipline). The switch runs **from a plain terminal, between agent turns** — never from inside A or B. If the post-switch fit guard refuses a transcript (mode shrank), that session takes the overflow path (§6.1 / fresh A seed); the machine switch log records the transition, append-only.

### 6.4 What "A died" even means

A is the top — nothing watches A, so A's death is a **state change, not an event**: nobody observes it. Consequences are bounded by design: the loop is `setsid` (survives), B keeps executing under the last decisions, and escalations queue on disk in `state.md §B updates`. **`decisions.md` going quiet is A's liveness signal** (only A writes it). Revival is manual and cheap: `tmux new-session -d -s control` + `pi --session <a_session>` (A is < 30k and always fits) or a fresh seed from `CONTROL.md`; A's first act = rule on each queued ESC. So "A died" = the campaign degrades to *execute-and-escalate* until a human revives the supervisor; B never self-promotes (hard rule 1) and the supervisor of the supervisor is the owner. v1 signal: B sees a pending ESC + `decisions.md` mtime stale > 30 min → appends a `supervisor stale` line to `work_log` (a log line, not an action — B does not spawn A).

## 7. Shared-KV reality

One 27B (ninfer `:18080`; ctx 135168, vision on: 16 media workers, 1 GiB cache + 2 GiB live media pool, mtp draft, **max-concurrency 3**) serves everything — A's turns, B's turns, B's subagents, the loop's vision POSTs. The int8 KV pool is shared, so simultaneous turns **serialize at the pool**; the design's job is to make that harmless:

1. **A is paced in short bursts** — bounded reads, one decision line, `P=60 s` poll with sleep between bursts; A's KV share is negligible and its bursts are idempotent (read + conditional write).
2. **B + subagents are already governed** — the existing subagent policy (≤ 2 concurrent; 5-parallel council as the standing exception) was designed around exactly this serialization.
3. **The loop is one-in-flight** — a tick = 1 screenshot (one media slot) + last K lines → short JSON; the synchronous loop never self-queues; worst case it waits behind B + 2 subagents (the ceiling) and drains.
4. **Contention = queue, not failure** — at most 3 run, the rest queue; nothing fails from contention, only latency. `:8000` runs on CPU (5.4 GiB free < the 6 GiB co-location rule), so it adds no contention — the shared pool is `:18080`-only.
5. **The 60 s no-activity nudge is a known false positive** — a queued requester is *waiting on the pool*, not idle; it is **not** a liveness signal (liveness = per-requester timestamps: `work_log` lines, subagent completions); act only on a child actually failed/stale > 5 min.

## 8. Verification tests (three)

All three must pass **before the first unattended run**, and each is re-run after any A/B tooling or guard change.

**T1 — B overflow is lossless** (the failure mode this architecture exists for).

- *Trigger*: `./qwen-switch.sh 100k` (ctx 102400 — the mode the CSM session actually overflowed in), then give B a unit whose tool output exceeds 102400 (e.g. a long page-run batch) → deterministic `context_length_exceeded`. *Cleanup*: `./qwen-switch.sh 135168` (mode is global state — leaving 100k behind is itself a state change).
- *Pass*: A's next poll detects it; the fresh B's first action is `state.md`'s next unit (no re-planning, no "where are we?"); `state.md` diffed before/after is unchanged except B's own appends; A's DEC lines untouched; git tree clean.
- *Fail*: B re-plans, starts a different unit, touches `state.md §state`, or A's decision lines are altered.

**T2 — A + B + loop + council under the shared KV.**

- *Trigger*: B runs a unit that launches a 5-parallel council (worst pool case, the standing exception) while the loop ticks mid-council and A polls on its normal cadence.
- *Pass*: the council completes 5/5; the loop's mid-council tick is delayed but executes (timestamped ACT line after the council); A's polls complete (DEC lines only if an ESC is pending); the 60 s nudge fires at least once and nobody kills or retries on it.
- *Fail*: any of the three does not complete, a loop step is dropped, or the nudge triggers a kill/restart.

**T3 — A death = degraded mode; revival from disk** (proves the tiebreaker).

- *Trigger*: `tmux kill-session -t control` while A is idle between polls.
- *Pass*: B finishes the in-flight unit under the last decision (no stall, no self-promotion); the next ESC is appended to `state.md §B updates`; **no** new `decisions.md` line (quiet file = A dead); `work_log` records `supervisor stale`; human revival (`tmux new-session -d -s control` + `pi --session <a_session>`) → A rules on each queued ESC.
- *Fail*: B stalled waiting for A, B wrote to `decisions.md`, or A post-revival does not see the queued ESCs.

## 9. Council verdict

Full record: `reports/master-work/COUNCIL_master_work.md` (5 advisors in parallel, 4 of 5 peer reviews landed, chairman synthesis; 2026-09-08).

## Agreements

All five advisors converge on the same defect: section 4.4's "A" is written as a Python daemon (`while True: sleep(60)`), but A is a pi session — agent turns, not a background process. Nothing schedules A's polls; every poll is a transcript turn, so A's context grows 1440x/day and "<30k, days" is overclaimed — A drowns in CSM's exact failure mode, unwatched ("most likely day-2 failure — in A, not B"). Consensus fix: **event-driven A** — a shell poller (file mtimes + tmux pane activity + model health) invokes a fresh one-shot LLM only on an ESC or liveness flip; A ceases to be long-lived. Unanimous catches 2-4: the 300s work_log staleness rule kills B mid long-unit / mid council (day-1 kill/respawn livelock; T2 masks it via loop heartbeat) → liveness = pane-activity + unit-aware durations + model-health gate. The shared-KV council case breaks the loop as written (pool saturation → 90s timeout → FAIL counted as no-op → HALT on every council) → the no-op guard must distinguish model-unavailable (retry, don't count) from explicit wait/reject. xdotool on live :0 needs consequence guardrails — combo denylist, `type` cap, run as the X user.

## Disagreements

- **Does A need to exist at all:** C — checkpoint-only CSM (SWITCHPOINT) + standalone setsid loop; add A only if ESC data shows a decision need. B — no A for CSM (single session + checkpoints win on every dimension); the split is right only for the PC loop / long-horizon work. E keeps A; peer 5: C's "what changes my mind" list *is* the fix — don't defer the decision channel.
- **Is the 100k overflow already fixed:** B — yes (now 135k; the pain is tool-output discipline); A/C/E — no: the failure is context-size-independent; 135k only delays the wall.
- **Where xdotool runs:** B — Xvfb/dedicated display is line 1 (ten minutes, not v2); D/E/plan — live :0 under guardrails (D: dedicated window day 1).
- **T2:** B — run as-is; C/A/E + peer 2 — cannot pass as written; fix the streak + liveness first.
- (C only) Rule 2 makes every DEC a vote on B's framing → bounded per-DEC evidence-read for A.

## Blind Spots

Peer-surfaced, missed by all five advisors: (1) the load-bearing claim "B is disposable, respawned from state files" is untested — add a kill-B-mid-unit test (right-unit resume, no double-commit, ESCs preserved). (2) model-down is not a named state — the single shared Qwen is a total SPOF (OOM precedent 508/524); switch window/crash = A blind, B stuck, stale-rule livelock, silent loop HALT; no one defines the ninfer restart. (3) the owner's control path has no interface — retracting an executing DEC, stop/revive A: the tiebreaker itself is inoperable. (4) B's `ls -1t *.jsonl | head -1` session discovery races foreign pi sessions — log `$PI_SESSION_FILE` as B's first work_log line.

## Verdict

**Deploy — modified.** Strongest reason: the unanimous catch that A, as specified, is an unschedulable LLM daemon that puts the CSM overflow failure mode inside the supervisor itself; the fixes are an afternoon's work and turn the design from ceremony-with-a-day-1-livelock into load-bearing. Apply before the first unattended run: (1) event-driven A (shell poller → one-shot LLM on events; A not long-lived); (2) pane-activity + unit-aware + model-health-gated liveness (replaces the 300s rule); (3) model-unavailable ≠ no-op (retry, don't count); (4) xdotool denylist + type cap + X user + dedicated window; (5) model-down as a named state (scripted `:18080` health-check + restart, liveness gated, `state.md` entry); (6) owner control path (STOP semantics, A stop/revive, DEC retraction = new DEC + work_log line); (7) new T0.5 kill-respawn + T2 re-specified as the post-fix case. Keep: disk tiebreaker, single-writer files, B-disposable, standalone setsid loop + STOP, checkpoint discipline. CSM resumption starts checkpoint-only (SWITCHPOINT) with event-driven A in parallel from day 1. Rejected: symmetric peer LLM (no veto/tiebreaker, doubles SPOF load) and pi built-in subagent workflows (die with the parent).

## First Action

Edit this plan: rewrite section 4.4 as event-driven A (new `tools/master-work/poller.sh`: 60s shell loop over STOP / ESC mtime / pane liveness / `curl -m 2 :18080/health`, invoking a fresh one-shot `pi` only on events) and apply modifications 2-6 into sections 5.3 / 6 / 8, adding T0.5 and the re-specified T2. The owner then runs T0 (the 10-minute B-append → A-decide round trip) before anything runs unattended.

## Draft-resolution notes (design/facts block wins; one line per conflict)

- Loop artifact: `tools/pcloop/loop.py` + the §5.4 setsid launch (this plan's TOC names `loop.py`); draft 1's `tools/master-work/pc_loop.sh` launcher dropped.
- work_log format: `[ts] KIND unit: detail` (KIND ∈ DONE/ACT/FAIL/HALT) — the last K lines are the loop's memory and must be self-explanatory to a model that never saw the session; draft 1's `KIND|` pipes dropped; the loop's heartbeat is an `ACT` line, not a `LOOP|` kind.
- Escalations queue in `state.md §B updates` (single queue, A's ruling target — draft 1's layout + draft 3's T3); draft 2's `reports/recommendations/` directory and its work_log `ESC` lines dropped, so `work_log` stays execution-events only.
- Pseudocode `max_tokens` = 2048, not draft 2's 200: the 27B spends its thinking budget before content (verified: small max_tokens returned empty content on real screenshots; 2048 matches the server default).
- T1 trigger uses the 100k (102400) profile — the mode the CSM session died in (repo facts); draft 3's 65536 profile is not in the repo facts.
- Session identity = pi's session-file path (repo facts: `pi --session <path-or-id>`); A records `a_session`/`b_session` in `state.md §state`; draft 1's preset `--session-id` flag is ungrounded and dropped.
- A's poll `P=60 s` fixed (draft 1), not draft 3's "N ≥ 60–300 s" range — the plan must be concrete.

## Deliberately not in v1

- **No VM/container isolation** — the trust boundary is the human + the loop guards (§5.3), not a sandbox.
- **No dedicated screen / Xvfb** — the loop drives the live `:0` under the guards; a dedicated display only if the owner's own use collides with it.
- **No cloud/remote-LLM fallback** — one local 27B is the design; a fallback adds latency + egress + its own KV reality.
- **No auto-respawn daemon for A** (no systemd/cron watchdog) — respawns are manual (A by the human, B by A); a watchdog only if manual respawn becomes the bottleneck.
- **No escalation schema / message queue, no multi-B fleet** — an escalation is a line on disk (no acks, no retry state machine); one B at a time, B's subagents (policy-capped) are the parallelism.
- **No metrics/dashboard, no separate cheap model for A** — liveness is file mtimes + `work_log` timestamps; A runs on the same 27B (a small fast supervisor is v2 if the poll cadence ever costs).
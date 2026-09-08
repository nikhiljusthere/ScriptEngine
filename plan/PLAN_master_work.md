# Master/Work (A/B) Deployment Plan

Owner: goblin · 2026-09-08 · status: **council-approved, modifications applied** (§10; deploy pending T0). One local Qwen 27B (ninfer `:18080`, ctx 135168, vision on) serves A, B, the loop and all subagents; the `:8000` ScriptEngine API runs on CPU.

## 1. Purpose — the failure this fixes

The CSM campaign session overflowed at **102,518 tokens vs the 102,400 limit** (Qwen 100k mode) and summarization recovery failed too — one context doing strategy *and* execution drowns; the plan got buried under 90k+ tokens of tool output. This plan deploys the two-session architecture:

- **Session A (CONTROL, "master")** — an *event-driven* LLM supervisor: strategy only (plan, decisions, vetoes, priorities); tools = state files + spawn/kill B + tmux control (§2). A is **not a long-lived session** (council catch #1: a polling LLM session accumulates 1440 turns/day and drowns in the CSM failure mode, unwatched). A small shell poller (`tools/master-work/poller.sh`, §4.4) watches state-file mtimes, pane liveness and `:18080/health`, and invokes a fresh one-shot `pi -p` **only on events** (unruled ESC, liveness flip, model up/down). Each invocation is a bounded < 10k context that ends with the decision on disk — A can never drown in work output, because it has no accumulating transcript.
- **Session B (WORK)** — a disposable executor: the campaign (first queued workload: the **paused CSM 100%** campaign, resumed via `plan/SWITCHPOINT.md`) plus the new **PC-control loop**. Big context, dies often (overflow, model reloads, terminal death); on death A respawns B from the state files — the plan never lived in B, so nothing is lost.

Hard rules (invariant; restated in `plan/CONTROL.md`):

1. **ONE-WAY FLOW.** B appends reports/recommendations to disk; A decides and writes decisions to disk. B never changes the plan — it escalates ("hit X, recommend Y") and A rules.
2. **A STAYS THIN.** A's tools are the fixed list in §2; if A starts executing work it has already failed — kill A, rebuild from disk.
3. **DISK IS THE TIEBREAKER.** State files beat either session's memory — the `plan/SWITCHPOINT.md` ritual (hand-written state + append-only log): a session transition is a commit, not a transcript.

**CSM resumption (the first queued workload) starts checkpoint-only** — `plan/SWITCHPOINT.md` drives B — with the event-driven A poller running in parallel from day 1 (council: no dedicated A session for the campaign; A = the poller's one-shots).

## 2. Roles & tool boundaries

| | Session A (CONTROL) | Session B (WORK) |
|---|---|---|
| context | one-shot < 10k per event (charter + state + tails); no long-lived A context | big; expected to die |
| allowed | read `state.md`, `decisions.md`, work_log tail, `STOP`; edit `state.md §state`; write `decisions.md`; create/delete `STOP`; tmux spawn/kill/has-session; start/revive the poller (§6.6) | full kit: read/bash/edit/write + subagents; campaign tools (`pytest`/`eval`/`index`/`span-recall`); `setsid`-launching the PC loop |
| forbidden | reading code or any repo file outside the state files; running campaign commands; editing the worktree | writing `decisions.md`; editing `state.md §state`; acting on a recommendation before a `DEC` line exists |

Formats — escalation (B → A; B appends to `state.md §B updates`): `[ts] ESC <unit>: hit <X> — recommend <Y> (evidence: <path>)` · decision (A → B; A prepends to `decisions.md`, newest first): `[ts] DEC <unit>: APPROVE | VETO <rule> | REDO <rule> — re ESC <unit>-<seq>`

## 3. Shared-truth file layout

All under `/home/goblin/ScriptEngine`. Each file carries at most one **hand-written block** (edit-in-place) and at most one **append-only log** (append at EOF, never rewrite) — the SWITCHPOINT split, applied per file.

| file | who writes | who reads | content |
|---|---|---|---|
| `plan/CONTROL.md` | owner at bootstrap (skeleton); A's one-shot edits only with a `DEC` on record | B (at boot) | A's charter: hard rules, A-loop spec (§4.4), formats (§2), loop guards (§5) |
| `plan/state.md` `§state` | **A's one-shot edits in place**; poller writes only the `model:` cell (§6.5) | both | position, next unit, `model` (up/down), open risks, `b_session`, loop status (the newest `ETA:` line lives in §B updates — B appends them, the poller reads the newest, §4.4) |
| `plan/state.md` `§B updates` | **B appends** | A | position updates + `ESC` lines (the escalation queue) |
| `plan/decisions.md` | **A only** (prepend, newest first) | B (`head -20`) | one `DEC` line each; B never writes this file |
| `reports/master-work/work_log.md` | **B only** (append; the loop appends its own lines) | A (`tail -20`) | execution events `[ts] KIND unit: detail`, KIND ∈ DONE/ACT/FAIL/HALT |
| `reports/master-work/STOP` | A creates/deletes | loop + B + poller | content `STOP <ts> reason=…`; its existence halts the loop (≤ 1 tick) and the poller kills B |
| `reports/master-work/a_wake_log.md` | **poller only** (append) | owner/A audit | one line per A event: `[ts] EVENT <name> → a_session=<id-or->` (A's liveness trail; A itself never writes this file) |
| `tools/master-work/poller.sh` + `ninfer_restart.sh` | owner at bootstrap (one-time; B commits) | poller | the event-driven A-loop scheduler (§4.4) + scripted model-down recovery (§6.5) |

Write rules: append-only logs take `printf '%s\n' '<line>' >> file` (EOF only; a full rewrite is a violation), `decisions.md` is newest-first (A prepends); ownership never overlaps — A's one-shots own `decisions.md` + `state.md §state` + `STOP`, B owns `work_log.md` + `state.md §B updates`, the poller owns `a_wake_log.md` + the `state.md §state` `model:` cell; commits use named paths, `control:` prefix for A, B's own prefixes, no push.

## 4. Bootstrap

### 4.1 Preflight (one-shot)

```bash
cd /home/goblin/ScriptEngine
curl -s -m 2 -o /dev/null -w '%{http_code}' http://127.0.0.1:18080/health && cat /home/goblin/ninfer-work/qwen_mode.txt   # expect 200 + ctx=135168 vision=on api=cpu
tmux kill-session -t work 2>/dev/null; pkill -f master-work/poller.sh 2>/dev/null; mkdir -p reports/master-work tools/pcloop tools/master-work
# Skeletons: plan/CONTROL.md (charter = §1 rules + §2 formats + §4.4 A-loop + §5 guards); plan/state.md (§state + §B updates),
#            plan/decisions.md + reports/master-work/work_log.md + reports/master-work/a_wake_log.md (headers only);
#            tools/pcloop/loop.py from §5.2; tools/master-work/poller.sh from §4.4 + ninfer_restart.sh from §6.5 (one-time; B commits them)
git add plan/CONTROL.md plan/state.md plan/decisions.md reports/master-work/work_log.md reports/master-work/a_wake_log.md tools/pcloop/loop.py tools/master-work/poller.sh tools/master-work/ninfer_restart.sh
git commit -m "control: bootstrap master-work state files + poller + loop"
```

### 4.2 Start A (the poller — A's scheduler; A itself is one-shot)

```bash
setsid nohup tools/master-work/poller.sh >> /tmp/master-work-poller.log 2>&1 < /dev/null &
# The poller IS the A-loop (§4.4): a 60 s shell loop over STOP / ESC mtime / pane liveness / curl -m 2 :18080/health.
# It invokes a fresh one-shot `pi -p` ONLY on events; each one-shot is A (charter: plan/CONTROL.md) and exits after writing.
# Confirm (fast, separate call): pgrep -f master-work/poller.sh · tail -1 /tmp/master-work-poller.log
```

### 4.3 Spawn B (work session)

```bash
tmux new-session -d -s work -c /home/goblin/ScriptEngine 'pi "Boot: read plan/CONTROL.md + plan/state.md §state. FIRST action: append your own session path to reports/master-work/work_log.md: `[ts] ACT boot: b_session=$PI_SESSION_FILE` (your env var — never `ls` the session dir; council blind spot 4). At each unit start, append an `ETA: <seconds>` line to plan/state.md §B updates (your unit's expected duration — the §4.4 liveness rule reads the newest one; a 35-min page-run declares ETA: 2100). Execute §next-unit. Append DONE/ACT/FAIL/HALT lines to reports/master-work/work_log.md; escalate via plan/state.md §B updates (hit X, recommend Y). Launch the PC-control loop per §5."'
# The A wake (B-UP event, §4.4) copies B's boot line into state.md §state `b_session` — $PI_SESSION_FILE is authoritative;
# the old `ls -1t *.jsonl | head -1` discovery raced foreign pi sessions and is gone (council blind spot 4).
```

- **Terminal death** (pane dead, session file fits — §6.2): `b=$(sed -n 's/.*b_session:[[:space:]]*//p' plan/state.md | head -1)` then `tmux new-session -d -s work -c /home/goblin/ScriptEngine "pi --session $b"`.
- **Transcript overflow**: A re-runs the boot message with plain `pi` (fresh identity) and records the new `b_session`. **Model reload** needs no respawn — panes and processes survive, both continue when the model returns (§6.3).

### 4.4 A-loop — event-driven (spec lives in `CONTROL.md`; scheduler = `tools/master-work/poller.sh`)

A has **no long-lived process** (council catch #1: a 60 s-polling LLM session accumulates 1440 turns/day and drowns in the CSM failure mode, unwatched). Instead: a 60 s **shell** loop (no LLM, zero context growth) watches five signals. **Mechanical events the poller handles in shell; judgment events it wakes a one-shot `pi -p` for:**

| signal | source | handling |
|---|---|---|
| `STOP` appears / removed | `reports/master-work/STOP` | **shell**: create → `pkill` loop + kill B pane + log; remove → log `STOP-CLEARED` (relaunch is explicit, §6.6) |
| new `ESC` | newest `ESC <unit>-<seq>` line in `state.md §B updates` with no matching `DEC <unit>-<seq>` in `decisions.md` | **wake A**: one-shot rules (APPROVE\|VETO\|REDO) — writes §state first, DEC line last |
| pane liveness flip | `tmux has-session -t work` | **wake A** on `B-DOWN` (§6.2 fit-check → resume or fresh spawn); log `B-UP` |
| model health flip | `curl -m 2 http://127.0.0.1:18080/health` | **shell**: down → `ninfer_restart.sh` (§6.5) + write `model: down` to §state; up → `model: up` + log. One-shot A wakes are **gated on model up** |
| B liveness (unit-aware) | `work_log` mtime vs `max(300, ETA)` | **wake A** on `B-STALE` (§4.4 rule below) |

```bash
# tools/master-work/poller.sh — the A-loop, shell-only (one-time bootstrap artifact; B commits it; T0 exercises it)
cd /home/goblin/ScriptEngine
STATE=plan/state.md; DEC=plan/decisions.md; STOP=reports/master-work/STOP; LOG=reports/master-work/a_wake_log.md; WORKLOG=reports/master-work/work_log.md
model=up; pane=""; stop_seen=""; last_wl=$(stat -c %Y $WORKLOG 2>/dev/null || echo 0)
wake() { local ev="$1" sid="a-$(date +%s)";   # judgment events → fresh one-shot A (charter in CONTROL.md)
  pi -p --session-id "$sid" "You are A (charter: plan/CONTROL.md). Event: $ev. Read plan/state.md, plan/decisions.md (head -20), reports/master-work/work_log.md (tail -20). Rule/act per the charter: write state.md §state FIRST, then the DEC line to decisions.md (prepend, newest first; include the exact ESC token). Never execute campaign work. Then stop." >>$LOG 2>&1
  echo "[$(date -Is)] EVENT $ev → a_session=$sid" >> $LOG; }
while :; do
  now=$(date +%s)
  # 1. model health (§6.5): a DOWN model gates A's one-shots and suspends B-staleness
  mup=$(curl -s -m 2 -o /dev/null -w '%{http_code}' http://127.0.0.1:18080/health)
  [ "$mup" = 200 ] && mup=up || mup=down
  if [ "$mup" = down ] && [ "$model" = up ]; then
    sed -i 's/^model: up.*/model: down/' $STATE
    setsid nohup tools/master-work/ninfer_restart.sh >> /tmp/ninfer-restart.log 2>&1 &   # scripted restart (§6.5)
    echo "[$(date -Is)] EVENT MODEL-DOWN (restart launched) → a_session=-" >> $LOG
  elif [ "$mup" = up ] && [ "$model" = down ]; then
    sed -i 's/^model: down.*/model: up/' $STATE; echo "[$(date -Is)] EVENT MODEL-UP → a_session=-" >> $LOG
    # lost-flip edge: a B-DOWN that occurred while the model was down was not woken (model gate);
    # re-check now — if the pane is still down, fire the deferred B-DOWN wake
    [ "$(tmux has-session -t work 2>/dev/null && echo up || echo down)" = down ] && pane= && wake "B-DOWN (pane down since model-down; fit-check §6.2)"
  fi
  model=$mup
  # 2. pane liveness
  live=$(tmux has-session -t work 2>/dev/null && echo up || echo down)
  if [ "$live" != "$pane" ]; then
    if [ "$live" = down ] && [ "$mup" = up ]; then wake "B-DOWN (fit-check §6.2: resume pi --session <b_session> if it fits, else fresh spawn §4.3)"; else echo "[$(date -Is)] EVENT B-${live^^} → a_session=-" >> $LOG; fi
    pane=$live; fi
  # 3. STOP appearance/disappearance (mechanical — no LLM)
  if [ -e $STOP ] && [ -z "$stop_seen" ]; then
    echo "[$(date -Is)] EVENT STOP: $(head -1 $STOP)" >> $LOG; stop_seen=1
    pkill -f 'tools/pcloop/loop.py'; tmux kill-session -t work 2>/dev/null
  elif [ ! -e $STOP ] && [ -n "$stop_seen" ]; then echo "[$(date -Is)] EVENT STOP-CLEARED" >> $LOG; stop_seen=""; fi
  # 4. new ESC: newest ESC line with no matching DEC (judgment — wake A; gated on model up)
  esc=$(grep -oP '^\[.*\] ESC \K[^: ]+' $STATE 2>/dev/null | tail -1)
  if [ -n "$esc" ] && ! grep -q "DEC $esc" $DEC && [ "$mup" = up ]; then wake "ESC $esc"; fi
  # 5. B liveness — UNIT-AWARE (council fix 2): stale = no work_log line for max(300, ETA); model-DOWN never counts
  eta=$(sed -n 's/.*ETA: *\([0-9]*\).*/\1/p' $STATE | tail -1); eta=${eta:-0}; lim=$(( eta > 300 ? eta : 300 ))   # newest ETA line (B appends them to §B updates, §4.3)
  wl=$(stat -c %Y $WORKLOG 2>/dev/null || echo $now)
  if [ "$live" = up ] && [ "$mup" = up ] && [ $(( now - wl )) -gt $lim ]; then
    last_wl=$now; wake "B-STALE (no work_log line for >${lim}s; ETA-aware, model up — decide: extend ETA / VETO / REDO / kill+respawn §6.1-6.2)"; last_wl=$(stat -c %Y $WORKLOG)
  fi
  [ "$wl" -gt "$last_wl" ] && last_wl=$wl
  sleep 60
done
```

**Liveness rule (replaces the flat 300 s staleness; council fix 2):** B alive ⇔ (i) pane up (`tmux has-session`) **and** (ii) a `work_log`/`§B updates` line within `max(300 s, the unit's declared ETA)` **and** (iii) model up — a B waiting on a dead model is *explained*, not dead (the model-health gate; §6.5). This is what makes a 35-min CPU page-run and a 5-parallel council (minutes of pool hold) non-lethal — the day-1 kill/respawn livelock the old 300 s rule caused is gone. `B-STALE` wakes A, which either extends the ETA (healthy long unit) or VETO/REDO/kill+respawns — a ruling, never an automatic kill.

### 4.5 Verify the bootstrap

```bash
tmux ls                                       # 'work' present (no 'control' session — A is the poller, §4.2)
pgrep -f 'master-work/poller.sh'              # the A poller runs (setsid)
tail -3 reports/master-work/work_log.md       # B's first lines incl. the b_session boot line
pgrep -f 'tools/pcloop/loop.py'               # the loop runs under setsid
```

If the poller dies (host reboot, `pkill`, tmux-server death taking the `work` pane): re-run §4.2 (poller) + §4.3 (B) — A has no long-lived state to restore (that is the design, §6.4; each one-shot re-seeds from `CONTROL.md` + the state files); last-resort read-only peek: `tmux capture-pane -t work -p | tail -5`.

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

### 5.2 Pseudocode (stdlib only — the venv has no `requests`; urllib POSTs the same JSON)

```python
import base64, json, re, subprocess, time, pathlib, urllib.request, urllib.error
URL, MODEL = "http://localhost:18080/v1/chat/completions", "qwen3.8-27b-ninfer"
class ModelDown(Exception): pass                                   # council fix 3/5: model-unavailable ≠ no-op (§6.5 named state)
DENY = ("XF86", "SUPER", "CTRL+ALT+BACKSPACE", "CTRL+ALT+DELETE")  # guard 6a: consequence combos (X restart, power, media)
W, H = (int(v) for v in subprocess.run(["xdotool", "getdisplaygeometry"], capture_output=True, text=True).stdout.split())  # guard 6c
LOG, STOP = pathlib.Path("reports/master-work/work_log.md"), pathlib.Path("reports/master-work/STOP"); TICK, K, MAX_TICKS, MAX_NOOPS = 20, 10, 120, 5
ALLOW = ("click", "double_click", "type", "key", "scroll", "wait", "done", "abort")
TASK = "Finish the pcloop goal in plan/state.md §state; one small action per reply."  # B sets per session
def log(msg):
    with LOG.open("a") as f: f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {msg}\n")
def shot():
    subprocess.run(["scrot", "/tmp/pcloop.png"], check=True, stdout=subprocess.DEVNULL); return base64.b64encode(pathlib.Path("/tmp/pcloop.png").read_bytes()).decode()
def ask(img):
    tail = "\n".join(LOG.read_text().splitlines()[-K:]) if LOG.exists() else ""
    req = urllib.request.Request(URL, data=json.dumps({"model": MODEL, "max_tokens": 2048, "messages": [{"role": "user", "content": [
        {"type": "text", "text": f"Task: {TASK}\nRecent work_log:\n{tail}\nReply with ONE JSON object; action in: " + "|".join(ALLOW)},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + img}}]}]}).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r: body = r.read()     # 90 s hard timeout (guard 2)
    except urllib.error.HTTPError as e:
        if e.code >= 500: raise ModelDown(f"HTTP {e.code}")                     # fix 3: saturated/dead model = transient, retry next tick
        raise RuntimeError(f"HTTP {e.code} (4xx — a real error, counts as no-op)") from e
    except (TimeoutError, urllib.error.URLError) as e:
        raise ConnectionError(str(e)[:60])                                      # fix 3: unreachable → main's builtin-ConnectionError path (retry, not a no-op)
    return json.loads(re.search(r"\{.*\}", json.loads(body)["choices"][0]["message"]["content"], re.S).group(0))
def run(a):  # argv-list xdotool only: model-supplied text/combo can never become shell injection
    n, x, y = a.get("action"), a.get("x", 0), a.get("y", 0)
    if n not in ALLOW: return "reject"
    if n == "key" and any(d in str(a.get("combo", "")).upper() for d in DENY): return "reject"   # guard 6a: combo denylist
    if n == "type" and len(str(a.get("text", ""))) > 200: return "reject"                        # guard 6b: type cap
    if n in ("click", "double_click", "scroll") and not (0 <= int(x) < W and 0 <= int(y) < H): return "reject"  # guard 6c: geometry
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
        except ModelDown as e: log(f"FAIL pcloop: model-down ({str(e)[:60]}) — named state §6.5, retry next tick, NOT a no-op"); res = "model-down"
        except ConnectionError as e: log(f"FAIL pcloop: model unreachable ({str(e)[:60]}) — timeout incl. the 90 s read-timeout; retry next tick, NOT a no-op (fix 3)"); res = "model-down"
        except Exception as e: log(f"FAIL pcloop: vision ({str(e)[:80]})"); res = "no-op"
        else: res = run(a); log(f"ACT pcloop: {json.dumps(a)} -> {res}")
        ticks += 1
        if res in ("done", "abort"): return
        noops = noops + 1 if res in ("no-op", "reject") else 0   # explicit wait/reject only — model-down never counts (fix 3)
        if noops >= MAX_NOOPS: log("HALT pcloop: no-op streak"); return
        time.sleep(TICK)
if __name__ == "__main__": main()
```

### 5.3 Guard rails

1. **Action allowlist** — the 8 actions only; unknown/malformed → `reject`, never executed, counts as a no-op.
2. **Rate limit + model-unavailable is not a no-op (council fix 3)** — synchronous loop ⇒ at most one in-flight vision request; tick floor `TICK=20 s`; the vision call has a 90 s hard `timeout`. A dead/slow/saturated model (connection error, 5xx, timeout) logs `FAIL pcloop: model-down — retry next tick` and **does not count toward the no-op streak** — the pool-saturated 5-parallel council (the worst case, §7) must not HALT the loop; only *explicit* `wait`/`reject` count. A *persistent* model-down is the named state of §6.5 (the poller restarts the model; ticks retry; the `MAX_TICKS` bound still caps the session and relaunch is explicit).
3. **No-op abort** — `MAX_NOOPS=5` consecutive *explicit* no-ops (`wait`/`reject` only — model-unavailable excluded, fix 3) → `HALT` line + exit; stuck-on-a-screen is what this catches, and restart is explicit.
4. **STOP veto (A/human)** — A writes `reports/master-work/STOP` (content = reason); checked *before* every tick's vision call (veto latency ≤ 1 tick); A deletes it to authorize a relaunch (fresh budget). Only A writes this file.
5. **Max-session budget** — `MAX_TICKS=120` (~40 min) hard cap per process; each relaunch starts a fresh budget, so a campaign is a chain of bounded sessions, each resuming from `work_log` + `state.md`.
6. **Consequence guardrails — xdotool on live `:0` (council fix 4)**: (a) **combo denylist** — `key` combos matching `XF86*`, `SUPER*`, `ctrl+alt+backspace` (X server restart), `ctrl+alt+delete` → `reject`; (b) **`type` cap** — ≤ 200 chars per action; (c) **geometry** — click/scroll x/y within `xdotool getdisplaygeometry`; (d) **run as the X session's user** (`goblin`), never root — the launch command checks `$USER` (§5.4); (e) **day-1 dedicated window** — B opens a dedicated terminal window and names it in the loop's `TASK`, so actions concentrate there; the rest of the desktop is protected by (a)–(c). Full display isolation (Xvfb) stays out of v1 (see Deliberately-not-in-v1) — a dedicated *window* is in v1, a dedicated *display* only if the owner's own use collides.

### 5.4 Launch (B, never A)

```bash
cd /home/goblin/ScriptEngine
[ "$USER" = goblin ] || { echo "the loop must run as the X session user (guard 6d), not $USER"; exit 1; }
DISPLAY=:0 setsid nohup scriptengine/.venv/bin/python tools/pcloop/loop.py >> /tmp/pcloop.log 2>&1 < /dev/null &
# B opens a dedicated terminal window first and names it in TASK (guard 6e). confirm (fast, separate call):
# ps -ef | grep pcloop/loop.py · kill: pkill -f 'tools/pcloop/loop.py' (or write STOP — the loop exits itself)
# if B dies the loop keeps running (setsid); the respawned B re-attaches via this log
```

## 6. Kill/resume semantics

### 6.1 B overflow (`context_length_exceeded`) — respawn, not resume

Four death classes; the binding rule is **disk is the tiebreaker**, and B's checkpoint-per-unit discipline (after every unit: `state.md` position + `work_log` line) means no death loses more than the in-flight unit — and never the plan, which never lived in B. Overflow (the CSM failure mode): the poller's `B-DOWN` event (pane liveness) wakes A, which sees B's failure marker (a work_log `HALT` line / dead pane). A does **not** `pi --session` the dead transcript — it is still over the limit, so resuming re-overflows on the first turn. A spawns a **fresh** B (§4.3), seeded with `state.md` + newest `decisions.md` lines + last K `work_log` lines; A confirms (or re-issues as a DEC line) the in-flight unit. Loss = at most the in-flight unit, re-runnable by construction.

### 6.2 B terminal death (tmux pane / host) — resume if it fits, respawn if not

The poller's `B-DOWN` event (pane liveness flip) wakes A. Fit check (the same conservative bytes/4 estimate `qwen-switch.sh` uses): session file fits the current ctx mode → `pi --session <b_session>` resumes in place (crash with a still-valid transcript — pane crash, OOM); does not fit → the §6.1 respawn. A host reboot takes tmux, `:8000` and `:18080` with it: recovery is §4.1–4.3 replayed in order (Qwen → `:8000` on CPU → poller §4.2 → tmux `work` §4.3) — disk state survives, so a replay, not a rebuild.

### 6.3 Qwen mode reload — the switchpoint ritual, not a death

A ninfer restart / `qwen-switch.sh` run leaves both sessions model-less for 30–60 s; tmux and session files survive and both continue after the reload. The ritual (reused from `plan/SWITCHPOINT.md`, not reinvented): fill the hand-written section **before** the switch (A is fully re-seedable from `CONTROL.md` + `decisions.md` + `state.md`; B's position is already in `state.md` by unit discipline). The switch runs **from a plain terminal, between agent turns** — never from inside A or B. The switch's 30–60 s reload window brackets as `MODEL-DOWN` → `MODEL-UP` poller events; no A one-shot can fire mid-window (the model gate, §4.4), so the ritual needs no special handling. If the post-switch fit guard refuses a transcript (mode shrank), that session takes the overflow path (§6.1 / fresh A seed); the machine switch log records the transition, append-only.

### 6.4 What "A died" even means (event-driven)

A is the poller (a shell, `setsid`) + one-shots (each < 10k, one turn, no accumulating transcript). Nothing watches A, so A's death is a **state change, not an event**: nobody observes it. Consequences are bounded by design: the loop is `setsid` (survives), B keeps executing under the last decisions, and escalations queue on disk in `state.md §B updates`. **`decisions.md` going quiet is A's liveness signal** (only A's one-shots write it). Revival is manual and cheap: re-run §4.2 (the poller) — there is no long-lived A state to restore, every one-shot re-seeds from `CONTROL.md` + the state files; A's first act = rule on each queued ESC. So "A died" = the campaign degrades to *execute-and-escalate* until a human revives the poller; B never self-promotes (hard rule 1) and the supervisor of the supervisor is the owner. v1 signal: B sees a pending ESC + `decisions.md` mtime stale > 30 min → appends a `supervisor stale` line to `work_log` (a log line, not an action — B does not spawn A).

### 6.5 model-down — a named state (the single Qwen is a total SPOF; OOM precedent: 508/524 pages)

Council blind spot 2: model-down was an accident, not a state. Now `state.md §state` carries `model: up|down` and the handling is **scripted**, not ad-hoc:

- **Detection**: the poller's `curl -m 2 http://127.0.0.1:18080/health` (every 60 s); the loop's per-tick ask() (a 5xx/connection failure is the loop-side signal).
- **Recovery**: the poller runs `tools/master-work/ninfer_restart.sh` (bootstrap artifact: re-runs the serve script matching the current `qwen_mode.txt` mode under `setsid`, log → `/tmp/ninfer-restart.log`; skips if a `qwen-switch.sh` lock is present, 5-min cooldown after the last `MODEL-UP` — no flapping against an owner-initiated switch).
- **Gates** (what “model health” means in liveness, §4.4): (i) no A one-shot fires while down — pending events re-fire on `MODEL-UP`; (ii) B-staleness is suspended — a B waiting on a dead model is explained, not dead; (iii) the loop's ticks log `FAIL pcloop: model-down — retry next tick` without counting toward the no-op streak (fix 3); if down past `MAX_TICKS` the loop exits and relaunch is explicit (§5.4).
- **Record**: `MODEL-DOWN`/`MODEL-UP` lines in `a_wake_log.md` + the `model:` cell of `state.md §state` (poller-written).

### 6.6 Owner control path (the tiebreaker itself must be operable; council blind spot 3)

- **(i) Emergency stop**: `echo "STOP $(date -Is) reason=<why>" > reports/master-work/STOP` — the loop halts within 1 tick (veto check before every vision call); the poller kills B + the loop and logs; deleting the file logs `STOP-CLEARED` (relaunch is explicit, fresh budget).
- **(ii) Stop/revive A**: `pkill -f master-work/poller.sh` / `setsid nohup tools/master-work/poller.sh >> /tmp/master-work-poller.log 2>&1 < /dev/null &` — A is the poller + one-shots, there is no long-lived process to kill; state is on disk, revival loses nothing (§6.4).
- **(iii) Retract an executing DEC**: a DEC line is immutable; retraction = a **new** DEC line (newest-first, so B's `head -20` sees it first) that supersedes, plus B's `ACT <unit>: DEC retracted per owner` line in `work_log`. Deleting an existing DEC is forbidden (append-only log).
- **(iv) Kill B directly**: `tmux kill-session -t work` — the poller's `B-DOWN` event handles the fit-check/resume exactly as a crash (§6.2); disk state survives all four paths.

## 7. Shared-KV reality

One 27B (ninfer `:18080`; ctx 135168, vision on: 16 media workers, 1 GiB cache + 2 GiB live media pool, mtp draft, **max-concurrency 3**) serves everything — A's turns, B's turns, B's subagents, the loop's vision POSTs. The int8 KV pool is shared, so simultaneous turns **serialize at the pool**; the design's job is to make that harmless:

1. **A is event-driven — near-zero background load** — the poller is shell (no LLM); A's one-shots fire only on events (usually a handful per hour), each < 10k tokens for a single turn; A's KV share is negligible and each burst is idempotent (read + conditional write).
2. **B + subagents are already governed** — the existing subagent policy (≤ 2 concurrent; 5-parallel council as the standing exception) was designed around exactly this serialization.
3. **The loop is one-in-flight** — a tick = 1 screenshot (one media slot) + last K lines → short JSON; the synchronous loop never self-queues; worst case it waits behind B + 2 subagents (the ceiling) and drains.
4. **Contention = queue, not failure** — at most 3 run, the rest queue; nothing fails from contention, only latency. `:8000` runs on CPU (5.4 GiB free < the 6 GiB co-location rule), so it adds no contention — the shared pool is `:18080`-only.
5. **The 60 s no-activity nudge is a known false positive** — a queued requester is *waiting on the pool*, not idle; it is **not** a liveness signal (liveness = per-requester timestamps: `work_log` lines, subagent completions); act only on a child actually failed/stale > 5 min.

## 8. Verification tests (T0 + T0.5 + T1–T3; T2 re-specified post-council)

T0 first (manual, 10 min — the council's gate to anything unattended); then all of T0.5/T1–T3 must pass **before the first unattended run**, and each is re-run after any A/B tooling or guard change.

**T0 — B-append → A-decide round trip** (10 min, manual, run by the owner before anything unattended).

- *Trigger*: with poller + B up, B (or the owner, impersonating B) appends a trivial `ESC <unit>-1: hit X — recommend Y` to `state.md §B updates`.
- *Pass*: within 2 poll ticks the poller fires exactly **one** A wake (`a_wake_log.md` line); A writes §state then the DEC line (DEC last, exact ESC token); the next tick fires **no** spurious wake (the invariant holds); B reads the DEC (`head -20 decisions.md`) and proceeds. Whole round trip ≤ 3 min.
- *Fail*: 0 wakes (event missed), > 1 wake (baseline not advanced), DEC written before §state (invariant broken), or A starts executing work.

**T0.5 — kill B mid-unit** (council blind spot 1: "B is disposable" is a claim until tested).

- *Trigger*: B mid-unit (unit N in flight, `ETA` declared, at least one sub-step committed to git); `tmux kill-session -t work`.
- *Pass*: the poller's `B-DOWN` event wakes A within 2 ticks; fit-check (§6.2) → `pi --session <b_session>` resume (pane death, transcript fits — the §6.2 path, *not* a fresh respawn); B's first resumed action = continue unit N from `state.md` + `work_log` (no re-planning); the committed sub-step is **not** re-committed (git log: exactly one commit); an ESC B wrote before the kill survives in `state.md §B updates` and gets ruled; `b_session` in `state.md` unchanged.
- *Fail*: B restarts the unit from scratch, double-commits, the pre-kill ESC is lost, or A takes the §6.1 fresh-respawn path when the transcript fits.

**T1 — B overflow is lossless** (the failure mode this architecture exists for).

- *Trigger*: `./qwen-switch.sh 100k` (ctx 102400 — the mode the CSM session actually overflowed in), then give B a unit whose tool output exceeds 102400 (e.g. a long page-run batch) → deterministic `context_length_exceeded`. *Cleanup*: `./qwen-switch.sh 135168` (mode is global state — leaving 100k behind is itself a state change).
- *Pass*: the poller's `B-DOWN` event wakes A; A takes the §6.1 fresh-respawn path (the dead transcript no longer fits 100k — resuming would re-overflow); the fresh B's first action is `state.md`'s next unit (no re-planning, no "where are we?"); `state.md` diffed before/after is unchanged except B's own appends; A's DEC lines untouched; git tree clean.
- *Fail*: B re-plans, starts a different unit, touches `state.md §state`, or A's decision lines are altered.

**T2 — A + B + loop + council under the shared KV** (re-specified as the post-fix council case — the original spec could not pass: a saturated pool timed out the 90 s vision call, the old guard counted it as a no-op, and the streak HALT'd the loop on every council).

- *Trigger*: B runs a unit that launches a 5-parallel council (worst pool case, the standing exception) while the loop ticks mid-council; the poller runs its normal 60 s cycle and A wakes only on events.
- *Pass*: the council completes 5/5; the loop's mid-council tick either completes (pool drains within 90 s) or logs `FAIL pcloop: model-down — retry next tick` lines that **do not** count toward `MAX_NOOPS` (fix 3), and the loop resumes after the council (timestamped ACT line); **no** `HALT pcloop: no-op streak` fires during the council; A wakes at most once (only if an ESC is pending) and completes; the 60 s nudge fires at least once and nobody kills or retries on it.
- *Fail*: the council incomplete, a loop step dropped without a retry line, a no-op-streak HALT during the council, or a kill/restart triggered by the nudge.

**T3 — poller death = degraded mode; revival from disk** (proves the tiebreaker).

- *Trigger*: `pkill -f master-work/poller.sh` while A is idle (no pending events).
- *Pass*: B finishes the in-flight unit under the last decision (no stall, no self-promotion); the next ESC is appended to `state.md §B updates`; **no** new `decisions.md` line (quiet file = A dead); B (pending ESC + `decisions.md` mtime > 30 min) appends `supervisor stale` to `work_log`; human revival = re-run §4.2 (the poller) → the next `ESC` event fires a fresh one-shot A → A rules on each queued ESC.
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

## First Action — **done 2026-09-08** (modifications 1–7 + blind-spot 4 applied; see §10)

Edit this plan: rewrite section 4.4 as event-driven A (new `tools/master-work/poller.sh`: 60s shell loop over STOP / ESC mtime / pane liveness / `curl -m 2 :18080/health`, invoking a fresh one-shot `pi` only on events) and apply modifications 2-6 into sections 5.3 / 6 / 8, adding T0.5 and the re-specified T2. The owner then runs T0 (the 10-minute B-append → A-decide round trip) before anything runs unattended.

## Draft-resolution notes (design/facts block wins; one line per conflict)

- Loop artifact: `tools/pcloop/loop.py` + the §5.4 setsid launch (this plan's TOC names `loop.py`); draft 1's `tools/master-work/pc_loop.sh` launcher dropped.
- work_log format: `[ts] KIND unit: detail` (KIND ∈ DONE/ACT/FAIL/HALT) — the last K lines are the loop's memory and must be self-explanatory to a model that never saw the session; draft 1's `KIND|` pipes dropped; the loop's heartbeat is an `ACT` line, not a `LOOP|` kind.
- Escalations queue in `state.md §B updates` (single queue, A's ruling target — draft 1's layout + draft 3's T3); draft 2's `reports/recommendations/` directory and its work_log `ESC` lines dropped, so `work_log` stays execution-events only.
- Pseudocode `max_tokens` = 2048, not draft 2's 200: the 27B spends its thinking budget before content (verified: small max_tokens returned empty content on real screenshots; 2048 matches the server default).
- T1 trigger uses the 100k (102400) profile — the mode the CSM session died in (repo facts); draft 3's 65536 profile is not in the repo facts.
- Session identity = pi's session-file path (repo facts: `pi --session <path-or-id>`); A records `a_session`/`b_session` in `state.md §state`; draft 1's preset `--session-id` flag is ungrounded and dropped. *(superseded by §10 mod 1/8: `a_session` is gone from §state — the poller logs each one-shot's session id in `a_wake_log.md`, and `pi -p --session-id` was verified on this machine's pi.)*
- A's poll `P=60 s` fixed (draft 1), not draft 3's "N ≥ 60–300 s" range — the plan must be concrete. *(superseded by §10 mod 1: the 60 s cadence now belongs to the shell poller, not an LLM.)*

## Deliberately not in v1

- **No VM/container isolation** — the trust boundary is the human + the loop guards (§5.3), not a sandbox.
- **No dedicated screen / Xvfb** — the loop drives the live `:0` under the guards; a dedicated display only if the owner's own use collides with it.
- **No cloud/remote-LLM fallback** — one local 27B is the design; a fallback adds latency + egress + its own KV reality.
- **No auto-respawn daemon for the poller** (no systemd/cron watchdog) — if the poller dies, revival is a manual §4.2 re-run (§6.6 ii); a watchdog only if manual revival becomes the bottleneck.
- **No escalation schema / message queue, no multi-B fleet** — an escalation is a line on disk (no acks, no retry state machine); one B at a time, B's subagents (policy-capped) are the parallelism.
- **No metrics/dashboard, no separate cheap model for A** — liveness is file mtimes + `work_log` timestamps; A runs on the same 27B (a small fast supervisor is v2 if the poll cadence ever costs).

## 10. Council modifications — applied (2026-09-08)

The verdict's 7 modifications + blind-spot 4, each landed where the verdict named it:

1. **Event-driven A** — §4.2/§4.4/§4.5: `tools/master-work/poller.sh` (60 s shell loop over STOP / ESC mtime / pane liveness / `curl -m 2 :18080/health`; a fresh one-shot `pi -p` only on events; `a_wake_log.md` audit). A is no longer a long-lived session.
2. **Unit-aware, model-health-gated liveness** — §4.4 rule: pane-activity + `max(300 s, ETA)` + model-down suspends staleness (replaces the flat 300 s rule).
3. **Model-unavailable ≠ no-op** — §5.2/§5.3: connection/5xx/timeout → `FAIL … retry next tick`, not counted; only explicit `wait`/`reject` count.
4. **xdotool consequence guardrails** — §5.3 guard 6 + §5.4: combo denylist, `type` ≤ 200, geometry bounds, run as the X user (not root), day-1 dedicated window.
5. **Model-down as a named state** — new §6.5: poller health-check + `ninfer_restart.sh`, liveness gated on it, `state.md` `model:` cell + wake-log entries.
6. **Owner control path** — new §6.6: STOP semantics, poller stop/revive, DEC retraction = new DEC + work_log line, direct kill-B.
7. **T0 + T0.5 added, T2 re-specified** — §8: T0 (the round-trip gate), T0.5 (kill-B-mid-unit: right-unit resume, no double-commit, ESC preserved), T2 as the post-fix council case.
8. **Blind-spot 4** — §4.3: B logs `$PI_SESSION_FILE` as its first work_log line (the `ls -1t` discovery is gone).

Kept per the verdict: disk tiebreaker, single-writer files (now incl. the poller as A's scheduler half), B-disposable-from-state, the standalone setsid loop + STOP, per-unit checkpoint discipline. **CSM resumption starts checkpoint-only** (`plan/SWITCHPOINT.md`) with the event-driven A poller in parallel from day 1. Verified on this machine in this commit: `pi -p` / `--session-id` (one-shot A), `PI_SESSION_FILE` env (B's boot line), `:18080/health` (HTTP 200).
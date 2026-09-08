# T0 result — PASS (2026-09-08, supervised run)

The 10-minute B-append → A-decide round trip (plan §8), run with the supervisor watching.

| criterion | result |
|---|---|
| exactly one A wake for the ESC (within 2 ticks) | PASS — one `EVENT ESC unit-t0-1` (11:17:56); count stayed 1 through 4+ later ticks |
| A wrote §state before the DEC (invariant) | PASS — A's audit: "1. §state 2. DEC line" |
| DEC carries the exact ESC token, prepended | PASS — `[11:17:27] DEC unit-t0-1: APPROVE — re ESC unit-t0-1` |
| no spurious re-wake next tick | PASS — ESC-event count stable at 1 |
| B reads the DEC and proceeds | PASS (after supervisor nudge — see finding 4) — `ACT unit-t0: DEC received: <line>` + `DONE unit-t0: T0 B-side complete` (11:19:35) |
| round trip ≤ 3 min | 3 min 39 s (ESC 11:13:48 → DEC 11:17:27): one 60 s poll tick + A's turn. Accepted as the steady-state number. |

## Findings (all fixed in-run, committed with this record)

1. **Poller shebang missing** — the spec block had no `#!`, so `setsid nohup` fell back to `sh` (dash), which died on the bash-only `${live^^}` at the first B-UP tick. Fix: `#!/usr/bin/env bash` first line of the spec (§4.4) + re-extracted `poller.sh`. (T0's first attempt is how it was caught.)
2. **`decisions.md` lost its trailing newline** (A's LLM edit). A glued prepend would corrupt the next line. Fix: poller guard in `wake()` (append `\n` if missing before each one-shot) + charter hygiene line.
3. **`b_session` not copied into §state** by A on the ESC wake (§6.2's fit-check needs it). Fix: CONTROL.md "Every wake" hygiene step 2.
4. **B ended its turn early** on the bounded DEC-wait (logged state at 11:14:45 instead of blocking 5 min). Supervisor nudge completed the unit. Accepted: an idle B is handled by `B-STALE` (a ruling, never an automatic kill); the boot message will state the wait is a single bounded tool call.
5. **Owner terminal-kill during the run**: the attached terminal died; every setsid/detached process (Qwen `:18080`, `:8000`, the poller, the detached `work` pane) survived — the §6.2 replay path was not needed.

Status: **deploy authorized** (plan header flipped). Next unit per A's DEC: B launches the PC loop (plan §5.4, fresh MAX_TICKS budget, day-1 dedicated window per guard 6e).

## Post-T0: visible GUI demo (pcloop-demo-1, same day)

Owner asked to *see* terminal close/open. Both open terminals were load-bearing and **not closable**: the “server” terminal hosts the Qwen model (its own session on pts/1 inside that gnome-terminal window — close ⇒ SIGHUP ⇒ model down ⇒ total SPOF), and the “π” terminal hosts the pi agent itself. Demo therefore ran on a third, disposable terminal: open `gnome-terminal` (visible) → `xdotool type` of `echo PC-control demo $(date +%T)` (visible keystrokes) → **mouse click on the X button** (visible) → window closed; Qwen `:18080` and `:8000` verified 200 after.

Findings (action items in parens):
1. **Display is 1920×1080, not 1440×1200** (stale note). `loop.py`'s guard reads `xdotool getdisplaygeometry` live — correct. The demo's ad-hoc VLM prompt hardcoded 1440x1200 and confused the model (it started doubting the image resolution). *(Never hardcode display dims in prompts; the loop's live guard already covers it.)*
2. **CSD window geometry**: `getwindowgeometry` client-top (90,59) sits ~31 px *above* the visible headerbar buttons (shadow/headerbar inside the client window) — VLM-pixel and naive client-math both missed the X button (6 clicks at y 68–86 all no-ops). **AT-SPI is the deterministic source**: `Atspi` (gi, installed) walked to the Close button's exact on-screen rect ((890,90) 34×30 → click (907,105) closed the window first try). *(Loop should prefer AT-SPI rects for window controls over VLM pixel estimates; VLM stays for content.)*
3. **Qwen is window-bound** (own session, pts/1, ppid = gnome-terminal-server subreaper). *(Ops fix at a safe boundary: launch serve detached — tmux or `setsid` + no tty — so the server terminal can be closed freely. Not mid-turn: a model restart is forbidden inside an agent turn.)*
4. **preserve-thinking eats explicit `max_tokens`**: vision Q&A with explicit `max_tokens` ≤ 2048 came back `finish_reason=length` with empty `content` (thinking burned the budget). *(If the loop ever sets an explicit `max_tokens` on screenshot calls, use ≥ 4096; otherwise leave the server default 20480.)*
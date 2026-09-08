# A/B deployment plan — sections 6–8 + YAGNI

(Sections 1–5 — goals, file layout, bootstrap, A charter, B + PC loop — are written elsewhere in the plan; this file holds the kill/resume, KV, and verification parts.)

## 6. Kill/resume semantics

Four death classes, one binding rule: **disk is the tiebreaker**. B's standing discipline is checkpoint-per-unit — after every unit: `plan/state.md` position updated, `reports/master-work/work_log.md` line appended — so no death loses more than the in-flight unit, and no death loses the plan, because the plan never lived in B.

### 6.1 B overflow (`context_length_exceeded`) — respawn, not resume

The CSM failure mode: context blows past the mode limit (102,518 > 102,400) and summarization recovery fails too. Detection: A's next poll (a short burst, every N seconds) sees B's failure marker in `work_log` / B's tmux pane. A does **not** `pi --session` the dead transcript — it is still over the limit, so resuming it re-overflows on the first turn. A spawns a **fresh** B instead: new tmux pane, new pi session, new identity (= its new session file), seeded with `state.md` + the newest `decisions.md` lines + the last K `work_log` lines. First act: A confirms (or re-issues as a decision line) the in-flight unit, and the new B starts exactly there. Loss = at most the in-flight unit, re-runnable by construction.

### 6.2 B terminal death (tmux pane / host) — resume if it fits, respawn if not

A's poll finds `tmux has-session -t work` false. Then the same fit check `qwen-switch.sh` uses (conservative bytes/4 estimate): B's session file fits the current ctx mode → `pi --session <B file>` resumes in place (a crash with a still-valid transcript — pane crash, OOM). Does not fit → the 6.1 respawn path. Host reboot takes everything with it (tmux, `:8000`, `:18080`): recovery is the §3 bootstrap replayed in order — Qwen → `:8000` (CPU) → tmux `control` → tmux `work`. Disk state survives, so it is a replay, not a rebuild.

### 6.3 Qwen mode reload — the switchpoint ritual, not a death

A ninfer restart / `qwen-switch.sh` run leaves both sessions model-less for 30–60 s; tmux and session files survive and both continue after the reload. The ritual (reused from `plan/SWITCHPOINT.md`, not reinvented): before the switch, the hand-written section is filled — A's state is fully re-seedable (`CONTROL.md` + `decisions.md` + `state.md`), and B's position is already in `state.md` by unit discipline. The switch itself runs **from a plain terminal, between agent turns** (`qwen-switch.sh`'s hard rule — never from inside an agent session, so the owner or a timer runs it, not A or B). If the post-switch fit guard refuses a transcript (mode shrank), that session takes the overflow path: A re-seeds from `CONTROL.md`, B respawns per 6.1. The machine switch log records the transition, append-only.

### 6.4 What “A died” even means

A is the supervisor — nothing above it watches A, so A's death is a **state change, not an event**: nobody observes it. The consequences are bounded by design: the PC loop is `setsid` (survives terminal death), B keeps executing under the last decisions, and escalations queue on disk in `state.md` in the escalation format. **`decisions.md` going quiet is A's liveness signal** — only A writes that file, so a stopped file is a liveness check cheaper than a heartbeat. Revival is manual and cheap: `tmux new-session -s control` + `pi --session <A file>` (A is < 30k and always fits, so a terminal death resumes in place) or a fresh seed from `CONTROL.md` if the file is gone. A's first act after revival: rule on each queued escalation in `state.md`. So “A died” = the campaign degrades to *execute-and-escalate* mode until a human revives the supervisor; B never self-promotes (hard rule 1), and the supervisor of the supervisor is the owner. One v1 signal: if B sees a pending escalation plus `decisions.md` mtime stale > X min, B appends a “supervisor stale” line to `work_log` (a log line, not an action — B does not spawn A). The human sees one line, not a silent queue.

## 7. Shared-KV reality

One 27B (ninfer `:18080`; ctx 135168, vision on: 16 media workers, 1 GiB cache + 2 GiB live media pool, mtp draft, **max-concurrency 3**) serves everything: A's turns, B's turns, B's subagents (delegate/worker/oracle/reviewer/scout/researcher), and the loop's vision POSTs. The int8 KV pool is shared, so simultaneous turns **serialize at the pool** — that is the whole reality, and the design's job is to make serialization harmless.

**The 60 s nudge is a known false positive.** A “pool inactive for 60 s” monitor fires during serialization: a queued requester is *waiting on the pool*, not idle (a child queued on the pool produces exactly this — do not steer or interrupt on the nudge). Consequence: the nudge is **not a liveness signal**. Liveness = per-requester response timestamps (the `work_log` line per loop step; subagent completion events). Act only on a child that is actually failed/stale > 5 min.

**Why A + B + loop + subagents is acceptable — A is paced in short bursts:**

1. **A's turn is small and bounded.** Read three small files, write one decision line, spawn/kill, poll: short prompt, short completion. A polls every N seconds (N ≥ 60–300 s) and sleeps between bursts, so A never holds the pool while a B turn runs; even an overlapping A burst is a few seconds of pool time. A's KV share is negligible against B's.
2. **B + subagents are already governed.** The existing subagent policy (100k → ≤ 2 concurrent; councils one agent at a time in any mode — owner rule 2026-09-08, the 5-parallel exception retired) was designed around this exact serialization, and B's main turn is the only long decoder in the mix.
3. **The loop is one-in-flight.** A step = 1 screenshot (one media slot of the 2 GiB pool) + last K `work_log` lines → short JSON action. Tick N > step time, so the loop never self-queues; worst case it is request #4 behind B + 2 subagents, waits, then completes.
4. **Contention = queue, not failure.** Max-concurrency 3 means at most 3 run; the rest queue and drain (every non-B request is short, so drain is bounded by the in-flight request). Nothing fails from contention — only latency. A's next poll simply sees a stale `state.md` and polls again; A's burst is idempotent (read + conditional write).

Moment of truth: worst case = B main turn (1) + 2 subagents (2) = the ceiling, with loop + A queued; the old 5-council case (5 children, 3 running, 2 queued) is retired — councils run one at a time since the 2026-09-08 owner rule, so B main turn + 2 subagents is the ceiling again, and the queue drains when the unit ends. Nothing is lost, only delayed. (`:8000` is on CPU — 5.4 GiB free < the 6 GiB co-location rule — so it adds no GPU/KV contention with `:18080`; the shared pool is `:18080`-only.)

## 8. Verification tests

Exactly three. All three must pass **before the first unattended run**, and each is re-run after any A/B tooling or guard change.

**T1 — B overflow is lossless** (the failure mode this architecture exists for).
- *Trigger*: switch Qwen to the smaller profile (`./qwen-switch.sh 65536` — `serve_ctx_65536.sh` exists), then give B a unit whose tool output exceeds that ctx (a long page-run batch or a large file dump) → deterministic `context_length_exceeded`, CSM-style.
- *Expected observable*: A's next poll detects the failure; A spawns a fresh B; the new B's first action is the “next unit” in `state.md` (no re-planning, no “where are we?”); `state.md` diffed before/after the death is unchanged except B's own append (A's lines untouched); git tree clean.
- *Pass*: the fresh B continues exactly one unit on, derived from the state files. **Fail**: B re-plans, starts a different unit, modifies `state.md`, or A's decision lines are altered.
- *Cleanup*: `./qwen-switch.sh` back to the working mode (mode is global state — leaving 65536 is itself a state change).

**T2 — A + B + loop + council under the shared KV.**
- *Trigger*: B runs a unit that launches a council (sequential since the 2026-09-08 owner rule; the worst pool case was the old 5-parallel exception) while the PC loop ticks with N small enough to land mid-council, and A polls on its normal cadence.
- *Expected observable*: the council completes 5/5; the loop's mid-council tick is delayed but executes (timestamped action line in `work_log` after the council); A's polling continues through the council (polls complete, delayed, and only write `decisions.md` if an escalation is pending); the 60 s nudge fires at least once and nobody kills or retries on it.
- *Pass*: all three complete; the loop stall < one in-flight request time (step delayed, not lost); the nudge is logged as a false positive. **Fail**: any of the three does not complete, a loop step is dropped, or the nudge triggers a kill/restart.

**T3 — A death = degraded mode; revival from disk** (proves the tiebreaker).
- *Trigger*: `tmux kill-session -t control` while A is idle between polls.
- *Expected observable*: B finishes the in-flight unit under the last decision (does not stall, does not self-promote); the next escalation is appended to `state.md` in the escalation format; **no** new `decisions.md` line appears (only A writes it — quiet file = A is dead); `work_log` records “supervisor stale”. Human revival: `tmux new-session -s control` + `pi --session <A file>`; A's first act is ruling on each queued escalation (new `decisions.md` lines, newest first).
- *Pass*: the escalation queue survived A's death intact on disk, and A sees it after revival — nothing lived only in A's context. **Fail**: B stalled waiting for A, B wrote to `decisions.md`, or A post-revival does not see the queued escalations.

## Deliberately not in v1

- **No VM/container isolation** — A/B/loop share the host, X11 (`:0`) and one Qwen; the trust boundary is the human + the loop guards (action allowlist, rate limit, no-op abort, STOP file, budget), not a sandbox.
- **No dedicated screen / Xvfb** — the loop drives the live desktop under those guards; a dedicated display only if the owner's own use collides with the loop.
- **No cloud/remote-LLM fallback** — one local 27B is the design; a fallback adds latency + data-egress and its own KV reality.
- **No auto-respawn daemon for A** (no systemd/cron watchdog) — respawns are manual (A by the human, B by A); a watchdog only if manual respawn becomes the bottleneck.
- **No escalation schema / message queue** — an escalation is a line on disk (`state.md`, the escalation format); no acks, no retry state machine.
- **No multi-B fleet** — one B at a time; B's subagents (already policy-capped) are the parallelism.
- **No metrics/dashboard** — liveness is file mtimes + `work_log` timestamps; a dashboard is v2.
- **No separate cheap model for A** — A runs on the same 27B; a small fast supervisor model is v2 if A's poll cadence ever costs.
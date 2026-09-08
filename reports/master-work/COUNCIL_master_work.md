# COUNCIL — master/work (A/B) architecture

2026-09-08 · method: llm-council (5 advisors in parallel, anonymized by letter; peer reviewers in parallel; chairman synthesis). All on the local Qwen 27B (`:18080`, 135k, vision on). Plan under review: `plan/PLAN_master_work.md`.

## Framed question

Should the owner deploy the two-session Master/Control (A) + Work (B) architecture to run (a) the paused CSM 100% campaign and (b) a new local PC-control loop (scrot -> :18080 Qwen-27B vision -> JSON action -> xdotool on X11, setsid-detached) — as the structural fix for the context-overflow failure that just killed the CSM session (102,518 > 102,400 tokens; strategy buried under tool output)?
Constraints: ONE local Qwen 27B (ninfer :18080, 135k ctx, vision on, max-concurrency 3, shared KV) serves ALL of A, B, the PC loop and campaign subagents; X11 + xdotool/scrot verified; pi sessions + tmux + on-disk switchpoint ritual exist.
Core design claims to pressure-test: (1) one-way flow (B appends, A decides); (2) A stays thin (no code, no tools); (3) disk is tiebreaker; (4) B is disposable, respawned from state files; (5) the PC loop is a stateless-per-step oracle (screenshot + last K log lines -> JSON action), not a long-lived agent.
Alternatives on the table: keep ONE big session and just checkpoint to disk more often (no A/B split); a second LLM as a PEER instead of supervisor (symmetric, no veto power); use pi built-in subagent workflows instead of a persistent control session.
Verdict wanted: is the split right and does any alternative win on any dimension; what will break first; the single thing to do first.

## Letter-to-lens mapping (record only — peer reviews reference letters, not lenses)

adv_1 = C = Contrarian · adv_2 = A = First-Principles · adv_3 = E = Expansionist · adv_4 = B = Outsider · adv_5 = D = Executor

## Advisor answers

### C — Contrarian

Against the split as instantiated.

Rule 2 forbids A from reading evidence, so every ESC is "hit X, recommend Y" and A's ruling is a vote on B's framing: veto decoupled from options. Rubber-stamp by construction: each stamp costs 60s + a pool turn, so ruling-dense CSM resumption is throughput-gated on A. And A's 60s poll grows A's own transcript 1440x/day: the plan's rare "A is dead" degraded mode becomes the normal state.

"B is disposable" destroys momentum in exactly the work CSM is: comprehension is stateful, and disposability resets the campaign's living model on every deterministic 102k overflow. "Loss = at most the in-flight unit" counts work product, not judgment — B re-derives the terrain on every respawn. Buried context was the actual failure. Per-unit SWITCHPOINT checkpoints (existing discipline) fix it without a second session, and the PC loop needs none of it: setsid + STOP + no-op guard is a standalone process. Coupling it to B pollutes the shared work_log.

What breaks first: the 300s stale check kills B's first 35-minute CPU page-run batch (~14s/q x 150, per repo) — kill, respawn, same unit, kill: day-1 livelock. T2 is unpassable as written: a 5-parallel council holds the shared KV for minutes, so the loop's 90s vision timeout -> 5 FAILs ~= MAX_NOOPS -> HALT. The loop dies on every council.

What changes my mind: event-driven A wake (no 60s poll). Per-DEC bounded evidence-read for A. Unit-aware staleness (declared durations). Separate loop log + no-op guard that ignores model-unavailable. Per-unit terrain summary so respawn is O(1). With all five, the split beats checkpoint-only on the decision channel; without them, ceremony.

First thing: one CSM unit batch under checkpoint-only (SWITCHPOINT, zero new artifacts) + the PC loop standalone. Measure overflow rate and ESC events. Add A (event-driven, evidence-read allowed) only if data shows a decision need.

### A — First-Principles

Forced by the constraints. Disk as shared truth: a stateless model holds no state; transcripts die on overflow and pane death. A disposable executor respawned from disk. A stateless, interruptible, allowlist-bounded tick loop: one display + one shared pool forbid an unbounded PC agent. Per-file single-writer ownership: two LLMs writing one file corrupt the only state.

Assumptions, not forced. (1) The LLM watcher: the constraints force only death-detection + judgment — a scripted poller detects, the LLM judges only on ESCs. A stateless LLM can't run a blocking loop, so the plan's 60 s polling means every poll is a transcript turn; A's transcript grows with no budget, so "<30k, days" is overclaimed — A drowns on CSM's exact failure mode, unwatched (section 6.4). (2) 300 s work_log staleness as B liveness: a GPU page-run or re-index stalls the log -> A kills B mid-unit -> fresh B reissues -> killed again: a kill loop. Liveness must be tmux pane activity, not log mtime. (3) T2 is unachievable: mid-council the pool saturates (max-concurrency 3); the loop's 90 s timeout fires -> FAIL -> 5 no-ops -> HALT, contradicting "the mid-council tick is delayed but runs."

Minimal architecture. Switchpoint state file + disposable B + tick loop + a scripted poller (file mtimes + pane activity) invoking a fresh one-shot LLM only on an ESC or liveness flip; the human is the last resort. The plan exceeds it in one place: A's continuous polling (a KV drain + A's own overflow vector).

What breaks first: the kill loop on the first long-running unit; A's silent overflow by day 1. Do first: make A event-driven — a shell poller that invokes a fresh LLM only on events, pane-activity liveness; A ceases to be long-lived.

### E — Expansionist

The split is right: one big session re-overflows (the failure mode itself), a symmetric peer has no owner of respawn/veto, and pi subagents die with their parent. Keep A/B. Three things break before "days":

1. The council kills the loop. A 5-parallel council saturates the shared KV pool for minutes; the loop's 90 s vision timeout returns FAIL, and section 5.3 counts FAIL as a no-op — five consecutive -> MAX_NOOPS HALT. T2 as written can fail. v1 fix: only explicit `wait`/`reject` count toward the streak; a model-side timeout retries next tick.

2. A's death is silent for days. "decisions.md going quiet" is a signal nobody reads; when A dies at 03:00, B executes under stale decisions and no one knows. v1: turn the plan's `supervisor stale` log line into a `notify-send` desktop ping (and one on model-down) — the only observability that survives unattended.

3. xdotool on live :0 is unbounded. `key` allows any combo (XF86* display suspend keys, X-restart combos), `type` has no length cap and lands in whatever window the human is focused, and screen content is a prompt-injection surface (a wiki or terminal line can "instruct" the model to type). v1: block list (XF86*, super, restart combos), cap type length, run xdotool as the X session's user, not root.

The three tests cover A/B mechanics, not loop safety: add a T4 before unattended (STOP halts within 1 tick; blocklist rejects; streak halts). And "A's KV share is negligible" holds only while A's requests are short — a fixed 60 s LLM poll spends tokens and a pool slot with nothing to decide most polls. A should wake on change (new ESC / B dead = shell check, zero LLM) and call the model only on the diff.

Xvfb/dedicated display, A-watchdog, dashboards: v2. STOP + owner-availability protocol: v1.

First thing: the loop-safety test + guardrails (blocklist, streak fix, exogenous ping). It is the only component touching a live X11 unsupervised, and it is an hour of work.

### B — Outsider

Clean plan, but it treats LLMs as daemons.

1. Nothing wakes A. Section 4.4 gives A a Python while loop (P=60s, sleep), but A is a pi session — agent turns, not a background process; the plan never says how A gets poked. A only polls when a turn is triggered, so B-watch and ESC processing are unscheduled. Breaks first: the system quietly degrades to execute-and-escalate until a human notices.

2. The 300s-stale rule kills B mid-council: B blocked on a 5-parallel council (tens of minutes, shared KV) appends nothing to work_log, and stale(log,300) -> kill_B. T2 masks it because loop heartbeats keep the log fresh — spec and test contradict.

3. The overflow that triggered this is already fixed: CSM died at 102,518/102,400 (100k); the mode is now 135k. The split only insures against the next overflow; the actual pain — strategy buried under 90k of tool output — is a discipline problem (bounded tool output, tail reads), not an architecture. For CSM I'd take the checkpoint-more-often alternative: one session, checkpoint to SWITCHPOINT after each unit (the ritual already did this handoff), fresh-from-disk on overflow. Afternoon; no A, no STOP file, no second 27B with veto power.

Refuse on my machine: unattended click/type on live :0 with a 40-min budget and no dedicated display. Guards bound action type, not consequence — `type` lands in the focused window; Xvfb is ten minutes and should be line 1, not a v2 deferral.

Peer LLM: refuse — two 27Bs, no tie-breaker, no veto. The split is right for the PC loop and long-horizon work; for CSM, single-session + checkpoints win on every dimension.

First action: build the A scheduler (tmux periodic poke, or polling in code with judgment in A); then run T2 as-is — if stale-kill fires mid-council, fix section 4.4 before the first unattended run.

### D — Executor

Day-1 order (plain terminal first; nothing starts unattended before T0-T3 pass):
1. Preflight: `curl -m 2 http://127.0.0.1:18080/v1/models`; `cat /home/goblin/ninfer-work/qwen_mode.txt` (today: 135168, vision=on, api=cpu). Write `tools/pcloop/loop.py` from section 5.2, plus a key-combo denylist (risk 3).
2. Bootstrap the four state files; seed `state.md` section "next unit" with CSM-1 (per SWITCHPOINT), a_session/b_session empty; named-path commit.
3. T0 — the single first end-to-end test, before A, before any CSM work: B runs one trivial unit (`git log --oneline -1` -> DONE line + one ESC into section "B updates"); A then writes the matching DEC and records a_session. Done = all three files show the B-append -> A-decide round-trip inside ~10 min. This is the gate before T1-T3.
4. PC loop: `setsid`-launch `loop.py`, TASK = "new terminal tab; type `pcloop-ok`; Return; `done`". Done = `ps` shows it, ACT lines land in `work_log.md`, clean `done` exit.
5. T1->T3 in plan order. T1's switch is `ninfer-work/qwen-switch.sh 100k` (the plan's `./qwen-switch.sh` path is wrong; pass `--api` explicitly — current state is api=cpu).
6. First real unit CSM-1: stamp `questions/csm.json` via `tools/csm/stamp_revids.py`; standing gates; commit.

Day-1 done: T0-T3 green, CSM-1 committed, the loop completed one bounded session, `decisions.md` advancing (A alive).

What breaks first / who pays:
1. Section 4.4's A-loop is Python but A is an LLM, not a daemon — pi doesn't execute `while True` for days; each 60 s poll is a model turn, so A bloats on its own turns, then overflows itself or auto-compaction summarizes the strategy away (silently). Most likely day-2 failure — in A, not B. Fix day 1: event-driven A (wake on ESC/staleness) + a one-line tick in `state.md` per wake.
2. B's `ls -1t *.jsonl | head -1` session discovery races — two foreign pi sessions already live in that directory; a wrong `b_session` means A later resumes someone else's transcript after a death. B should log `$PI_SESSION_FILE` as its first `work_log` line; A reads that.
3. `key` has no denylist — a hallucinated `ctrl+alt+BackSpace` or `alt+F1` kills the X session or bounces a tty; `type` racing the owner's own keystrokes in an active terminal yields corrupted commands. Cost: session reset + owner attention. Day-1 mitigation: a dedicated window + the combo denylist.
4. Silent HALTs — T1's 30-60 s model-less window turns into 5 vision FAILs = no-op streak = HALT, visible only in a `work_log` line nobody is watching (A dead => quiet `decisions.md`). Money: zero (all local); attention: all of it.

## Peer reviews (4 of 5 landed; see gap note)

### Peer 1

1. **Agree most: A.** The forced-vs-assumption split is the load-bearing correction: constraints force only death-detection and judgment, so A should be a scripted poller plus one-shot LLM judgment — "A ceases to be long-lived." A long-lived A polling every 60 s recreates in the supervisor the exact overflow failure this council is reacting to.

2. **Disagree most: B.** "The overflow is already fixed (135k)" misreads the failure: the session died with strategy buried under ~90k of tool output, not at a capacity wall, and the SWITCHPOINT-on-disk discipline that already existed didn't save the in-context strategy. One session across a 100% campaign deterministically re-buries; "checkpoint more often" leaves strategy only on disk.

3. **Missing from all five:** the load-bearing claim "B is disposable, respawned from state files" is never tested. T0 tests the B->A round-trip, T4 tests loop safety; nobody kills B mid-unit and verifies the respawn resumes the right unit with no double-commit and ESCs preserved. Add a kill-respawn test before the first unattended run — if it fails, the split degrades into silent campaign corruption.

### Peer 2

1. Agree most — C: only C refuses to build a second LLM session whose decision need is asserted, not demonstrated. Checkpoint-only CSM (the existing SWITCHPOINT ritual) plus a setsid loop is the minimum working system; add event-driven A only if ESC data shows a decision need.

2. Disagree most — B: "already fixed at 135k" is wrong where it matters — 135k buries the strategy under more tool output before the wall; the failure is context-size-independent, so CSM needs the checkpoint fix. "Run T2 as-is" contradicts C/A/E: a 5-parallel council saturates the shared KV, the 90 s timeout no-ops into a MAX_NOOPS HALT; fix T2 (streak fix + pane liveness) first.

3. Missing from all five — model-down as a named state with a recovery path. The single shared Qwen is the SPOF; no answer puts it in the state files or pauses liveness while it is down. During the 30-60 s switch window or a crash, A is blind, B's respawn cannot act (claim 4 void), the 300 s stale rule makes the outage a kill/respawn livelock, and the loop no-ops into a HALT — disk-as-tiebreaker collapses because the only actor is the model. v1: scripted ninfer health-check + restart; liveness gated on model health; model-down as a state.md entry.

### Peer 3

*(Not on disk — the peer_3 child was stopped in the shared-KV queue window; gap recorded, not re-run. Four independent reviews stand.)*

### Peer 4

1. Agree most: B, the only one that attacks the premise: the 102k overflow is already gone (Qwen now 135k), and buried strategy is a tool-output discipline problem (capping output, tail reads), not architecture; for CSM, checkpoint-more-often wins on cost (afternoon, no second 27B with veto). "Treats LLMs as daemons" is the root cause of section 4.4.

2. Disagree most: D, a build order, not a verdict: hard-codes the A/B split into day 1 (four state files, T0 A-DEC round trip) without answering which alternative wins, and T0 sits on the component D itself lists as break-first #1 (A's 60s poll being an unschedulable LLM turn).

3. Missing from all five: death of the model itself. All five treat Qwen as always up, but the one 27B / shared KV pool is a total SPOF, with an OOM precedent (extraction crash: 508/524 pages died Connection refused): a crash takes down A, B, loop, subagents, and the 5-parallel council is the load that OOMs it. E pings on model-down, C ignores model-down, but no one defines recovery: who restarts ninfer, what resumes B's in-flight unit, what the no-op guard distinguishes (model-down =/= no-op). Add a scripted /health poll, restart, and retry-from-state-file pre-unattended.

### Peer 5

1. Agree most: **B**. The only answer that challenges the premise: the triggering overflow (100k) is already fixed at 135k, and the real pain (strategy buried under tool output) is a transcript-discipline problem, not an architecture one — so CSM wants single-session + checkpoints and the loop wants the split. Also the only T2 spec/test catch (the stale rule kills B mid-council; T2 masks it because loop heartbeats keep work_log fresh).

2. Disagree most: **C**. "Against the split as instantiated" is a verdict on the plan as written, but C's own "what changes my mind" list (event-driven A, unit-aware staleness, per-unit terrain summaries) *is* the consensus redesign — C rejects the split and prescribes its fix in the same breath, and deferring A until measurements delay the decision channel the resumption's first unit (a decision call) needs.

3. **All five miss the owner's control path.** Claim 3 (disk is tiebreaker) implies human override, but nobody specifies it: how to retract a DEC B is already executing; how to stop A (STOP stops the loop; killing A is an unrecorded tmux kill that loses A's state); how to revive A (D's a_session handle exists; no procedure — E names an "owner-availability protocol" without content). The tiebreaker itself has no interface.

## Verdict

### Agreements

All five advisors converge on the same defect: section 4.4's "A" is written as a Python daemon (`while True: sleep(60)`), but A is a pi session — agent turns, not a background process. Nothing schedules A's polls (B: "nothing wakes A"); every poll is a transcript turn, so A's context grows 1440x/day (C) and "<30k, days" is overclaimed — A drowns in CSM's exact failure mode, unwatched (A, D: "most likely day-2 failure — in A, not B"). The consensus fix: **event-driven A** — a shell poller (file mtimes + tmux pane activity + model health) invokes a fresh one-shot LLM only on an ESC or liveness flip; A ceases to be long-lived.

Second unanimous catch: the 300s work_log staleness rule kills B mid long-unit (C: the 35-minute CPU page-run batch -> day-1 kill/respawn livelock; A: GPU re-index; B/E: a 5-parallel council holds the KV for minutes, B appends nothing, the stale-kill fires — and T2 masks it because the loop's heartbeat keeps the log fresh). Liveness must be **pane-activity + unit-aware (declared durations) + model-health-gated**, not log mtime.

Third: as written, the shared-KV council case breaks the loop — pool saturation -> 90s vision timeout -> FAIL counted as no-op -> MAX_NOOPS HALT on every council (C, A, E, B). The no-op guard must distinguish **model-unavailable (retry next tick, do not count)** from explicit wait/reject.

Fourth: xdotool on live :0 needs consequence-level guardrails beyond the action allowlist — combo denylist (XF86*, super, X-restart), `type` length cap, run as the X user (D, E); B wants Xvfb as line 1, the one split below.

### Disagreements

- **Does A need to exist at all:** C — no: checkpoint-only CSM (SWITCHPOINT) + the standalone setsid loop; measure ESC data, add A only if the decision need shows. B — no A for CSM (single session + checkpoints win on every dimension); the split is right only for the PC loop / long-horizon work. E keeps A; peer 5 counters that C's "what changes my mind" list *is* the consensus fix, and deferring A delays the decision channel the resumption's first unit (a decision call) needs.
- **Is the 100k overflow already fixed:** B — yes (now 135k; the real pain is tool-output discipline, an afternoon's fix); A/C/E — no: the failure is context-size-independent (strategy buried under 90k of tool output), and one session across a 100% campaign deterministically re-buries; 135k only delays the wall (peers 1-2: "misreads the failure").
- **Where xdotool runs:** B — Xvfb/dedicated display is line 1 (ten minutes, not a v2 deferral); D/E/plan — live :0 under guardrails in v1 (D: dedicated window as day-1 mitigation).
- **T2:** B — "run it as-is, fix section 4.4 if stale-kill fires"; C/A/E + peer 2 — it cannot pass as written; fix the streak + liveness first.
- (C only) Rule 2 forbids A from reading evidence, so every DEC is a vote on B's framing; C wants a bounded per-DEC evidence-read.

### Blind Spots

Surfaced by peer review, missed by all five advisors:
1. **The load-bearing claim is untested** — "B is disposable, respawned from state files" never has a kill-B-mid-unit test verifying the respawn resumes the right unit with no double-commit and ESCs preserved (peer 1). If it fails, the split degrades into silent campaign corruption.
2. **Model-down is not a named state** — the single shared Qwen is a total SPOF with an OOM precedent (508/524 pages died `Connection refused`). During the 30-60s switch window or a crash: A is blind, B cannot act, the stale rule livelocks, the loop HALTs silently. No answer defines who restarts ninfer (peers 2, 4).
3. **The owner's control path has no interface** — claim 3 (disk is tiebreaker) implies human override, but nobody specifies retracting a DEC B is already executing, stopping A without losing state, or reviving A (peer 5). The tiebreaker itself is inoperable.
4. (D) B's `ls -1t *.jsonl | head -1` session discovery races two foreign pi sessions already live in the directory; B should log `$PI_SESSION_FILE` as its first work_log line.

### Verdict

**Deploy — modified.** The strongest single reason: the unanimous catch that A, as specified, is an unschedulable LLM daemon that places the CSM overflow failure mode *inside the supervisor itself*; the fixes are an afternoon's work and turn the design from ceremony-with-a-day-1-livelock into load-bearing.

Apply before the first unattended run:
1. **Event-driven A** — shell poller (STOP / ESC mtime / pane liveness / `:18080` health) invokes a fresh one-shot LLM only on events; A is not long-lived.
2. **Liveness** = pane-activity + unit-aware declared durations + model-health gate (replaces the 300s work_log rule).
3. **No-op guard** — model-unavailable retries next tick and does not count; only explicit `wait`/`reject` count toward MAX_NOOPS.
4. **xdotool consequence guardrails** — combo denylist (XF86*, super, X-restart), `type` length cap, run as the X user, dedicated window.
5. **Model-down as a named state** — scripted `:18080` health-check + restart, liveness gated on it, entry in `state.md`.
6. **Owner control path** — STOP semantics, stop/revive A (recorded, not a bare tmux kill), DEC retraction = new DEC + work_log line.
7. **Two new tests** — T0.5 kill-B-mid-unit (right-unit resume, no double-commit, ESCs preserved) and T2 re-specified as the *post-fix* council case.

Keep: disk tiebreaker, single-writer files, B-disposable-from-state, the standalone setsid loop + STOP, per-unit checkpoint discipline. CSM resumption starts **checkpoint-only (SWITCHPOINT)** with event-driven A running in parallel from day 1 — C's data gate and E's decision channel both hold; the decision channel costs one shell script plus one-shot calls, so it is not deferred. Rejected: symmetric peer LLM (no veto, no tiebreaker, doubles the SPOF load) and pi built-in subagent workflows (die with the parent; no persistent strategy).

### First Action

Edit `plan/PLAN_master_work.md`: rewrite section 4.4 as event-driven A (new `tools/master-work/poller.sh`: 60s shell loop over STOP / ESC mtime / pane liveness / `curl -m 2 :18080/health`, invoking a fresh one-shot `pi` only on events) and apply modifications 2-6 into sections 5.3 / 6 / 8, adding T0.5 and the re-specified T2. The owner then runs T0 (the 10-minute B-append -> A-decide round trip) before anything runs unattended.
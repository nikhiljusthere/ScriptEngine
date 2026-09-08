The split is right: one big session re-overflows (the failure mode itself), a
symmetric peer has no owner of respawn/veto, and pi subagents die with their
parent. Keep A/B. Three things break before "days":

**1. The council kills the loop.** A 5-parallel council saturates the shared
KV pool for minutes; the loop's 90 s vision timeout returns FAIL, and §5.3
counts FAIL as a no-op — five consecutive → MAX_NOOPS HALT. T2 as written can
fail. v1 fix: only explicit `wait`/`reject` count toward the streak; a
model-side timeout retries next tick.

**2. A's death is silent for days.** "decisions.md going quiet" is a signal
nobody reads; when A dies at 03:00, B executes under stale decisions and no
one knows. v1: turn the plan's `supervisor stale` log line into a
`notify-send` desktop ping (and one on model-down) — the only observability
that survives unattended.

**3. xdotool on live :0 is unbounded.** `key` allows any combo (XF86* display
suspend keys, X-restart combos), `type` has no length cap and lands in
whatever window the human is focused, and screen content is a prompt-injection
surface (a wiki or terminal line can "instruct" the model to type). v1: block
list (XF86*, super, restart combos), cap type length, run xdotool as the X
session's user, not root.

The three tests cover A/B mechanics, not loop safety: add a T4 before
unattended (STOP halts within 1 tick; blocklist rejects; streak halts). And
"A's KV share is negligible" holds only while A's requests are short — a
fixed 60 s LLM poll spends tokens and a pool slot with nothing to decide most
polls. A should wake on change (new ESC / B dead = shell check, zero LLM) and
call the model only on the diff.

Xvfb/dedicated display, A-watchdog, dashboards: v2. STOP + owner-availability
protocol: v1.

**First thing:** the loop-safety test + guardrails (blocklist, streak fix,
exogenous ping). It is the only component touching a live X11 unsupervised,
and it is an hour of work.
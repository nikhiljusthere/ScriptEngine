Clean plan, but it treats LLMs as daemons.

1. Nothing wakes A. §4.4 gives A a Python while loop (P=60s, sleep), but A is a pi session — agent turns, not a background process; the plan never says how A gets poked. A only polls when a turn is triggered, so B-watch and ESC processing are unscheduled. Breaks first: the system quietly degrades to execute-and-escalate until a human notices.

2. The 300s-stale rule kills B mid-council: B blocked on a 5-parallel council (tens of minutes, shared KV) appends nothing to work_log, and stale(log,300) → kill_B. T2 masks it because loop heartbeats keep the log fresh — spec and test contradict.

3. The overflow that triggered this is already fixed: CSM died at 102,518/102,400 (100k); the mode is now 135k. The split only insures against the next overflow; the actual pain — strategy buried under 90k of tool output — is a discipline problem (bounded tool output, tail reads), not an architecture. For CSM I'd take the checkpoint-more-often alternative: one session, checkpoint to SWITCHPOINT after each unit (the ritual already did this handoff), fresh-from-disk on overflow. Afternoon; no A, no STOP file, no second 27B with veto power.

Refuse on my machine: unattended click/type on live :0 with a 40-min budget and no dedicated display. Guards bound action type, not consequence — `type` lands in the focused window; Xvfb is ten minutes and should be line 1, not a v2 deferral.

Peer LLM: refuse — two 27Bs, no tie-breaker, no veto. The split is right for the PC loop and long-horizon work; for CSM, single-session + checkpoints win on every dimension.

First action: build the A scheduler (tmux periodic poke, or polling in code with judgment in A); then run T2 as-is — if stale-kill fires mid-council, fix §4.4 before the first unattended run.
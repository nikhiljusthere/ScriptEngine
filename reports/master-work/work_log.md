# work log — B only, APPEND at EOF (never rewrite; the pcloop appends its own ACT/FAIL/HALT lines).
# format: [ts] KIND <unit>: detail    KIND ∈ DONE/ACT/FAIL/HALT
# B's first line after boot: [ts] ACT boot: b_session=$PI_SESSION_FILE (its own env var — never `ls` the session dir)
[2026-09-08T11:13:48+05:30] ACT boot: b_session=/home/goblin/.pi/agent/sessions/--home-goblin-ScriptEngine--/2026-09-08T05-43-04-167Z_01a07f8a-96e7-71df-8324-32636ef4fe43.jsonl
[2026-09-08T11:14:45+05:30] DONE unit-t0-esc: ESC appended, awaiting DEC
[2026-09-08T11:19:35+05:30] ACT unit-t0: DEC received: [2026-09-08T11:17:27+05:30] DEC unit-t0-1: APPROVE — re ESC unit-t0-1
[2026-09-08T11:19:35+05:30] DONE unit-t0: T0 B-side complete

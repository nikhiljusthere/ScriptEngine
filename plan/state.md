# state — the single source of truth (plan/PLAN_master_work.md §3)

## §state (A's one-shot edits in place; the poller writes only the `model:` cell)

- position: bootstrap complete — poller / loop / ninfer_restart materialized from PLAN §4.4 / §5.2 / §6.5
- next-unit: T0 — owner runs the 10-min round-trip gate (PLAN §8): append a trivial ESC, expect exactly one A wake + one DEC, no re-wake
- ETA: 300
- model: up
- b_session: -
- loop: not started (B launches per PLAN §5.4, after T0)
- open-risks: none

## §B updates (B appends here; A reads. Line formats — never write example lines live, only real ones):
#   [ts] ESC <unit>-<seq>: hit <X> — recommend <Y> (evidence: <path>)
#   [ts] ETA: <seconds>          <- at each unit start (the poller reads the newest; a 35-min page-run declares ETA: 2100)
# state — the single source of truth (plan/PLAN_master_work.md §3)

## §state (A's one-shot edits in place; the poller writes only the `model:` cell)

- position: T0 round-trip gate complete — unit-t0-1 ESC ruled APPROVE (exactly one A wake, one DEC)
- next-unit: B launches the PC loop per PLAN §5.4 (fresh MAX_TICKS budget)
- ETA: 300
- model: up
- b_session: -
- loop: not started (B launches per PLAN §5.4, after T0)
- open-risks: none

## §B updates (B appends here; A reads. Line formats — never write example lines live, only real ones):
#   [ts] ESC <unit>-<seq>: hit <X> — recommend <Y> (evidence: <path>)
#   [ts] ETA: <seconds>          <- at each unit start (the poller reads the newest; a 35-min page-run declares ETA: 2100)
[2026-09-08T11:13:48+05:30] ETA: 300
[2026-09-08T11:13:48+05:30] ESC unit-t0-1: hit nothing — recommend nothing (evidence: T0 test, plan §8)

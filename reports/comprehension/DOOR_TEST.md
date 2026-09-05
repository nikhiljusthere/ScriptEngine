# Phase 1 — Door test: beat order from extracted events

Subject: `Shibuya Incident` (jjk). The question the door answers: can a page's
beats be reordered onto the events' time axis, from stored data only, with no
change to the default narrative path?

## The defect

The article organizes the incident by *stage*, not by the clock. In the
default (flag-off) beat stream, the `10:01 P.M. - 10:04 P.M. Shibuya C Tower`
beat sits at position 8 — written before the `9:27`, `9:22 P.M. - 9:40` and
`9:40` beats it chronologically follows. A script reading the stream in order
lands on C Tower at 10:01, then steps back to 9:22.

## The data

33 hand-written rows (`scriptengine/ingest/events.py`, `PHASE1_ROWS`), all
gated before storage: verb in the closed set, both ends resolve to real nodes
(name or alias), quote verbatim in its section, placement a page the wiki has.
All 33 pass; stored as 32 on the time axis + 1 standing state (Mahito's
October 19th killing of Mechamaru, `temporal=0`, pre-incident).

`model=hand-written`, `prompt_version=phase1-door-test`, `revid=0`.

## Before (flag off — the article's own order)

```
OFF 7. 9:22 PM - 10:01 PM Shibuya (9:22 PM)
OFF 8. 10:01 P.M. - 10:04 P.M. Shibuya C Tower (10:01 PM)   <- out of order
OFF 9. 9:27 P.M. - 10:02 P.M. Between ... (9:27 PM)
OFF 10. 9:22 P.M. - 9:40 P.M. Shibuya Station (9:22 PM)
OFF 11. 9:40 P.M. - 10:10 P.M. Shibuya (Outside the Curtain) (9:40 PM)
OFF 12. 10:10 P.M. - 10:51 P.M Shibuya Station (10:10 PM)
```

## After (`SCRIPTENGINE_EVENTS_ORDER=1`)

```
ON 7. 9:22 PM - 10:01 PM Shibuya (9:22 PM)
ON 8. 9:22 P.M. - 9:40 P.M. Shibuya Station (9:22 PM)
ON 9. 9:27 P.M. - 10:02 P.M. Between ... (9:27 PM)
ON 10. 9:40 P.M. - 10:10 P.M. Shibuya (Outside the Curtain) (9:40 PM)
ON 11. 10:01 P.M. - 10:04 P.M. Shibuya C Tower (10:01 PM)    <- now in order
ON 12. 10:10 P.M. - 10:51 P.M Shibuya Station (10:10 PM)
```

Every beat's start time is now non-decreasing. The C Tower beat moves from
position 8 to 11; the 9:xx beats move ahead of it. The unranked `Prologue`,
`Aftermath`, `Timetable` and `Battles` sections inherit the last placed rank,
so Prologue still reads first and Aftermath still reads last. Neighbour beats
(related battle pages, positions 19+) are a separate stream and keep their
order behind the reordered page.

## Residuals

- Reordering applies only to the subject's own page beats; the neighbour
  stream is untouched (the events do not cover it).
- A section's rank is the earliest event placed in it; events within a
  section are sequenced by `time_rank` fractions, which the hand-written batch
  assigns by the section's start time.

## Default behaviour

`SCRIPTENGINE_EVENTS_ORDER` is read at call time and defaults to off, so the
narrative path is byte-identical to before until the flag is set. The events
table and its methods are reachable only from the new `events` command, the
flag, or `seed_phase1_rows` — nothing on a default path touches them, so the
canon-run (opm) gate is structurally unaffected and was not re-run.

## Standing gates (flag off)

| gate | baseline | phase 1 |
|---|---|---|
| pytest | 1137 passed | 1137 passed |
| eval jjk | 24/24 | 24/24 |
| span-recall jjk | 48,570/48,572 (2 misses, rc=2) | 48,570/48,572 (2 misses, rc=2) |
| canon-run opm | 10/16 · 236/236 · 79.0% | not re-run (inert, see above) |

Raw receipts: `raw/phase1_pytest.txt`, `raw/phase1_eval_jjk.txt`,
`raw/phase1_spanrecall.txt`.

## Commands

```
python -m scriptengine.cli events --series jjk --seed-phase1
python -m scriptengine.cli events --series jjk
SCRIPTENGINE_EVENTS_ORDER=1 python -m scriptengine.cli timeline --series jjk "Shibuya Incident" --max-beats 40
```
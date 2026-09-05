# Phase 3 — Time axis: an orderable position for every placed event

Subject: the same `jjk` placement set Phase 2 extracted (108 pages: 9 event +
90 battle + 9 story_arcs). Phase 2 stored *what happened, to whom, when on the
page's clock*. Phase 3 stores *where the page sits in the story* — the one
dimension the page clock cannot give, because a clock resets on every page.

A name does not sort; an index does. The axis converts the arc the wiki filed
each placement page under into an orderable position, and a script writer's
continuity check ("this line reaches three arcs early") is a subtraction, not a
guess.

## The three cheap signals

In order of trust; inference is reserved for the residue:

1. **arc-page.** The page *is* an arc. JJK's story chain is one clean 9-arc run
   (read off the wiki's own `story_arc` pages via `chronology.chains`), so an arc
   page's position is the arc's position in that run. 9 pages.
2. **arc-fact.** The page carries an `arc` fact (`Culling Game`, `Shibuya
   Incident`…). Matched to an arc page by name, tolerating the wiki's
   free-form shapes (with/without the `Arc` suffix, and a double-arc value like
   `Culling Game Arc Shinjuku Showdown Arc` that files under its first arc).
   97 pages.
3. **citation.** The page carries a `chapters` fact (`Chapter 213 - 215`). The
   arc is looked up, not guessed: JJK's battle pages already file a chapter
   range under an arc, so the chapter→arc map is *derived from the corpus's own
   placements* (`chapter_arc_index`). 1 page.

**Residue.** A placement page neither signal reaches (no arc fact, no chapter
fact, not an arc page) is the one place inference may go. On jjk that is a
single page: `Kyoto Sister-School Goodwill Event` (its twin `Kyoto Goodwill
Event Arc` story-arc page is the arc-page hit; the event page itself carries no
placement signal).

## Coverage

107/108 placement pages placed by the cheap signals — **9 arc-page, 97 arc-fact,
1 citation, 1 residue**. The residue is a lookup the wiki simply does not
provide, not a failure of the signals.

## What is stored, and the door

- `events.arc_index INTEGER` (a new additive column, `ensure_events` migrates an
  existing store with `PRAGMA table_info` + `ALTER TABLE`). `backfill_event_arc_index`
  recomputes it from the placement axis on every run, so a re-crawl that moves an
  arc is picked up.
- The **door** is the read a script writer actually performs:
  `events_in_story_order` returns every placed event sorted by
  `(arc_index, time_rank, section ordinal)`, and the `time-axis` command prints
  it with the coverage tally and the residue list. It is the operation that makes
  "three arcs early" a computable check: arc indices are non-decreasing, so an
  event that should sit in arc *n* but carries arc index *m < n* is the
  anachronism.

## Verified

- **Monotonic.** `arc_index` is non-decreasing across all 714 stored events;
  every `Shibuya Incident` event (index 6) precedes every `Culling Game` event
  (index 7).
- **Canonical run.** The 9 arcs order canonically (Cursed Child → … → Shinjuku
  Showdown); the per-arc run lengths read off the axis are sensible (Shibuya 194,
  Culling Game 217 are the two densest).
- **Chapter lookups.** `chapter_arc_index` files `ch 14 → Fearsome Womb`,
  `ch 213 → Culling Game`, `ch 80 → Shibuya Incident`, and maps nothing for a
  chapter no battle files (a gap in the wiki stays a gap).
- **CLI door.** `time-axis --series jjk` prints the tally, the single residue
  page, and the ordered events; `--subject "Yuji Itadori"` keeps the order and
  filters to his 46 events.
- **Backfill exact.** The only rows left off the axis are the ones filed under a
  residue page; every placed page's rows are ranked (`tests/test_timeaxis.py`).

## Standing gates (re-run after Phase 3)

| gate | baseline | phase 3 |
|---|---|---|
| pytest | 1137 passed | 1152 passed (+15 timeaxis tests) |
| eval jjk | 24/24 | 24/24 |
| span-recall jjk | 48,570/48,572 (2 misses, rc=2) | 48,570/48,572 (2 misses, rc=2) |
| canon-run opm | 10/16 · 236/236 · 79.0% | 10/16 · 236/236 · 79.0% |

The axis is reachable only from `time-axis`, `backfill_event_arc_index`, and
`events_in_story_order`. Nothing on a default retrieval path touches it, so the
gates are structurally unaffected and were re-run clean (the `:8000` CUDA API was
stopped for pytest and relaunched for canon-run; it came back up without OOM).

## Residuals

- The single residue page (`Kyoto Sister-School Goodwill Event`) is where Phase
  3's inference pass goes: one page, not a corpus-wide problem.
- Self-directed `arrived` rows (`Satoru Gojo arrived Satoru Gojo`) surface at the
  head of the axis; they are the allowed Phase-2 self-directed case, now visible
  in the global order, and are a Phase-5 quality note rather than an axis defect.

## Commands

```
python -m scriptengine.cli time-axis --series jjk
python -m scriptengine.cli time-axis --series jjk --subject "Yuji Itadori" --limit 40
python -m scriptengine.cli time-axis --series jjk --limit 10
```
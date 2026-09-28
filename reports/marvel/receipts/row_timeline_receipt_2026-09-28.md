# Marvel row-timeline re-derivation receipt (2026-09-28)

Commit piece: **row-timeline wiring (marvel side)** — the marvel fix: the
live marvel store carried the draft-era placement state (79/1,220 rows
placed, and no `partition` column at all), while the final backfill code
migrates the store (`ALTER TABLE events ADD COLUMN "partition" TEXT`) and
carries the wiki's declared store axis as its weakest placement signal.
Run: final code + marvel's declaration, over the live store.

## Code (committed with this piece)

- `scriptengine/ingest/timeaxis.py` — `backfill_event_arc_index` now
  migrates a store without the `partition` column, and after the
  page/section/citation signals, a wiki that declares a store axis
  inherits the page's axis rank (plus the axis' `partition` value) for
  every row the stronger signals missed. NULL-safe UPDATEs (`IS ?`); the
  partition value is rewritten on every run, so an FK rebuild that loses
  the column's contents heals on the next backfill.
- `scriptengine/stores/facts.py` — `"partition" TEXT` in the events DDL
  (both create paths).
- `tests/test_timeaxis.py` — `TestStoreAxisBackfill` (30/30 in the file).

## Declaration (series/marvel/overrides.yaml, events block)

```yaml
events:
  placement_types: [story_arc]
  axis:
    date_keys: [releasedate]
    order_keys: [first, last, "part*"]
    partition_key: reality
```

A page with a `releasedate` sits at its publication clock; a page without
one inherits the clock of the instalments it cites (`first` / `last`
appearance, `part*` instalments of a multi-part story). Partitions are
the `reality` fact value; a page with no `reality` fact sits in the
counted `<NULL>` bucket, last.

## Store state produced (series/marvel/facts.db, untracked)

Before = the live store pre-run (the 23:51 backup
`/tmp/se_p2/marvel_facts_pre_rederive_20260928.db`): **79/1,220** rows
placed, and the events table **had no `partition` column** (the
draft-era literal `'partition'` values the MCU receipt's "Marvel side"
note reported were gone from the live store by then — the store had been
re-extracted in the meantime; this run migrated a store with no column
at all).

| | before | after |
|---|---|---|
| placed rows (`arc_index` set) | **79 / 1,220** | **1,196 / 1,220** (98.0%) |
| `partition` column | absent | present; 9 values |
| literal `'partition'` rows | — (column absent) | 0 |
| `time_rank` set on placed rows | 79 | 1,196 |
| `temporal` nonzero | 79 | 79 (unchanged — `recompute_temporal` runs after this commit, per the architect's steer) |

Partition distribution of the placed rows:

| partition | rows |
|---|---|
| Earth-616 | 996 |
| `<NULL>` (the counted no-`reality` bucket) | 86 |
| Earth-1610 | 55 |
| Earth-58163 | 21 |
| Earth-15513 | 21 |
| Multiverse | 12 |
| Earth-691 | 3 |
| Earth-14412 | 1 |
| Earth-11326 | 1 |

Store-axis tally of the run: `pages` 4,200 walked; `store_axis` 1,117
rows placed by the declared axis (the whole delta: 79 + 1,117 = 1,196);
`citations` 0 mapped (the wiki files its clocks on `releasedate` /
appearances, not in-text citations); `residue` 4,185 placement pages
beyond the axis' reach.

### The 24 unplaced rows (the inference pass' queue)

Events on the four pages the declared axis does not reach (no
`releasedate`, no resolvable `first` / `last` / `part*` clock):

| page | rows |
|---|---|
| Multiversal War | 10 |
| M-Day (Earth-41578) | 9 |
| Jaspers Warp | 4 |
| Assemblage of Avatars | 1 |

## Recompute (after this commit, 00:30)

`recompute_temporal` ran after this commit (the table above notes `temporal`
is re-derived after the commit). It re-ran the backfill (idempotent: the
1,196 placements held, 0 new, 0 lost) and re-derived `temporal` from the
placement.

| | pre-recompute | post-recompute (live) |
|---|---|---|
| placed rows | 1,196 / 1,220 | 1,196 / 1,220 (unchanged) |
| `temporal` nonzero | 79 | **1,196** |
| unplaced | 24 | 24 |

`temporal` promoted 1,117 (every placed row is eventive; 0 demoted), so
`temporal` now equals the placement set (1,196). Tally: temporal_before 79,
temporal_after 1,196, temporal_promoted 1,117, temporal_demoted 0,
temporal_unplaced 24.

## Tests

`tests/test_timeaxis.py` green (30/30). Full suite at commit time: the
known 4 environmental failures (blind-panel missing file + 3 MCP tests
that need the :8000 API up), pre-existing and unrelated.
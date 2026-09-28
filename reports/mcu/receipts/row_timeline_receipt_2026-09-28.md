# MCU row-timeline wiring receipt (2026-09-28)

Commit piece: **row-timeline wiring** — the wiki's declared store axis becomes
the weakest placement signal of the event backfill, and every stored event
row carries its position (`arc_index`, `temporal`, `partition`) with no
model.

## Code

- `scriptengine/ingest/timeaxis.py` — `store_time_axis`: walk the wiki's
  declared axis over its placement pages (strongest signal first:
  `chain` runs > `date` clock > `order_key`), value-sorted partitions ahead
  of the within-partition order; the backfill (`backfill_event_arc_index`)
  now inherits a row's page rank + the axis' partition value for the rows
  the page/section/citation signals missed, and writes the `partition`
  column (rewritten on every run, so an FK rebuild that loses the column's
  contents heals on the next backfill). The UPDATE is NULL-safe (`IS ?`)
  so `NULL` keys match `NULL` keys.
- `scriptengine/stores/facts.py` — `"partition" TEXT` added to the events
  DDL (both create paths).
- `tests/test_timeaxis.py` — `TestStoreAxisBackfill`: a synthetic two-
  instalment store that no page/section/citation signal reaches; the
  declared axis places both rows with the page's rank + the declared
  partition value, and a wiki that declares no axis sees the step as a
  no-op (rows keep their baseline). 30/30 in the file.

## Declaration (series/mcu/overrides.yaml, events block)

```yaml
events:
  placement_types: [conflict, war, event]   # was [conflict]; the 99 `war`
  #                                            # pages join the placement set
  axis:                                       # the wiki's own clock
    date_keys: [date]
    chain_keys: [previous, next]
```

MCU declares no `partition_key` (a single-reality wiki): its placed rows
carry `partition = NULL` by design — the column exists for wikis that
partition (marvel's `reality`).

## Store state produced (series/mcu/facts.db, untracked)

| | before | after |
|---|---|---|
| placed rows (`arc_index` set) | **0 / 6,339** | **6,097 / 6,326** (96.4%) |
| `temporal` nonzero | 0 | 6,097 (= placed; `recompute_temporal` consistent) |
| unplaced (residue, the inference pass' queue) | 6,339 | 229 |

Store-axis tally of the run (pre-pilot, 22:19): 1,873/1,988 placement
pages placed (chain 1,630, date 243, order-key 0, residue 115);
citations 0 mapped / 0 unmapped / 0 undated (the MCU wiki files its
episode clocks on `date`, not citations).

The pre-backfill store (post the 21:36 re-index) held 6,339 rows: the
backfill placed all but the 229 buggy pilot section rows — 6,110 placed,
229 unplaced (verified in the 23:13 pre-repair backup). The later repair
re-keyed those 229 and dropped 13 dedup collisions (6,339 → 6,326;
6,110 → 6,097 — see `pilot_row_repair_2026-09-28.md`, later commit).
This piece's own delta: **0 → 6,110 placed** (the 229 re-keyed pilot rows
stay unplaced until a further backfill run — the inference pass' queue).

## Marvel side (noted, re-derived later)

marvel's stored rows carried the draft run's stale output (79/1,220
placed, `partition` holding the literal string `'partition'`). The final
code, run with marvel's declaration, places its placement pages by
`order_key` (205 pages, e.g. `Phalanx Covenant` → Earth-616) and writes
real `reality` values or NULL. Re-derivation is a later step; its receipt
records the before/after.

## Tests

Full suite at commit time: `4 failed, 1,419 passed, 2 xpassed` — the 4
failures are the known environmental set (blind-panel missing file + 3 MCP
tests that need the :8000 embedder up), pre-existing and unrelated.
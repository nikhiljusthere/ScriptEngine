# C4 T2 design (rev 2) — section-like passages, heading-agnostic prose scope, store time axis

Worker, 2026-09-28. Rev 2 of this design, revised per
`REVIEW_c4_t2_design_2026-09-28.md` (architect): **the mechanism is approved
as-is (kept), the scope is rejected (revised)**. R1–R5 are implemented below;
R6 is the council's budget framing. No series names in `.py`; per-wiki rules
live only in `series/<name>/overrides.yaml`.

## 0. What rev 2 changes from rev 1

| # | rev 1 | rev 2 |
|---|---|---|
| R1 | `all` read only narrative-titled sections | heading-agnostic: **every prose section**; furniture is the only exclusion, explicit + per-wiki-declarable, counted per heading |
| R2 | guards (20-word floor, 40-word lead, junk keys) dropped text silently | every guard reports the passages/words it excludes and why, in the dry-run and the receipt |
| R3 | "unplaceable rows flip to `temporal=0` — the 100% shape" | T2b: override-declared **store time axis** (date / chain / order / partition); `temporal` / `arc_index` re-derived on stored rows; fact passages inherit the page's axis rank |
| R4 | — | save-path dedup on (doc, passage, S, v, O, quote); `passage` joins the events PK |
| R5 | pilot = fact values only | full-scope mix: section classes, list classes, leads |

Kept, unchanged (review-approved): the passage model
(`kind / page / title / text / ordinal`), the `passage` storage column +
`ensure_events` migration + `remap_derived` re-anchor, `narrative_fact_keys`
declaration, generic lead passages, `under2` routing of the ≥2 audit,
JJK baselines intact, tests then the four standing gates.

## 1. R1 — heading-agnostic scope: every prose section is read

`--scope all` reads every section carrying prose, and the
extractable-prose test is decided on content, not title:

```
prose(section)  :=  word_count(strip_markup(section.text)) >= 20
```

Named sets, each counted in the dry-run and the receipt:

| set | rule | status |
|---|---|---|
| placement | arc/event/battle pages × extractable sections | unchanged (JJK baselines intact) |
| corpus | narrative-titled, ≥2 of the wiki's character nodes | unchanged |
| under2 | narrative-titled, 0/1 character nodes (≥2-audit routing) | unchanged |
| **prose** | every section with prose ≥ floor, minus furniture | **new** |
| fact | declared `narrative_fact_keys` values | new in rev 1 |
| lead | page lead with prose ≥ floor | new in rev 1 (floor unified at 20w, per R2) |

`prose` ⊇ {placement, corpus, under2} — each of those is narrative-titled and
above the floor — so `all = prose ∪ fact ∪ lead`. The named sets stay in the
code for the per-class receipt counts; the union machinery is unchanged, so
`placement` / `corpus` / `under2` behave exactly as today and a `--refresh`
never stops reading the placement set.

### Furniture — the only exclusion, explicit and counted

A prose section is not read only when its heading is in the furniture list:

- **generic default** (wiki-agnostic, in `.py`): the extractor's existing
  list set (`_LIST_SECTION_TITLES` minus the narrative `plot/summary/
  synopsis`, plus `timetable`, `interactive map`), extended with the
  link/image families no wiki writes prose under: `external links`,
  `see also`, `further reading`, `bibliography`, `references`,
  `screenshots`, `cover art`, `interior art`, `media`, `gallery`.
- **wiki-declared** (overrides): `events: furniture: [...]` extends the
  list per wiki.

Every furniture-excluded section is counted in the dry-run and the receipt
**per heading, with the named cause** (generic or wiki-declared) and the
words it carried.

### List-shaped classes — never silently skipped

Allies / Enemies / Appearances / Family / Equipment / Vehicles /
Relationships / Dialogue are text. Under T2 they are:

1. **read** where they carry prose ≥ floor — extracted rows land as
   standing-state rows (`temporal=0`);
2. **counted** per heading in the receipt as the `list_class` class;
3. their relational content (typed ally / enemy / appearance rows) is the
   plan-C5 `relations` work — the council rules read-now vs defer with the
   counts in hand.

Measured: mcu `relationships` is 5,041 sections / 221 words (an
empty-stub class, accounted under below-floor); `allies` 95.7k,
`dialogue` 363.5k, `abilities` 182.2k, `biography` 139.4k words — real
prose, read under `all`.

### Scope measured (2026-09-28, over the stores)

| series | sections | prose ≥20w | below floor (counted class) |
|---|---:|---:|---:|
| marvel | 69,829 / 11,601,771 w | 49,409 / 11,533,250 w | 20,420 / 68,521 w |
| mcu | 187,342 / 13,283,572 w | 75,809 / 12,988,484 w | 111,533 / 295,088 w |

Furniture candidates already on the stores (mcu): `external links`
24,063 sections / 6.3k w · `references` 14,226 / 2.6k w · `gallery` 4,093 /
121 w · `media` 390 / 2.5k w · `see also` 79 / 1.2k w · `screenshots` 7 /
0 w. (marvel: `comics` 2,114 · `interior art` 2,113 · `screenshots` 908 ·
`cover art` 841, plus the link families at dry-run.) Note the below-floor
class dwarfs the furniture prose: the empty-stub sections are accounted, not
excluded.

## 2. R2 — no silent thresholds: guard accounting

Every guard that drops text reports, in the dry-run and the receipt, how
many passages and words it excludes and why:

| guard | drops | receipt line |
|---|---|---|
| section floor (20w after strip) | below-floor sections | `below_floor`: count + words (marvel 20,420 / 68,521 w; mcu 111,533 / 295,088 w) |
| lead floor (20w after strip; rev 1's 40w measurement superseded) | template / empty leads | `lead_dropped`: count + words |
| fact-key floor | junk keys (`synopsis    header`, `synopsis¿5`) | `fact_key_dropped`: per key, count + chars |
| furniture (heading) | prose sections under a furniture heading | `furniture`: per heading, count + words, cause (generic / wiki) |
| list class | list-shaped sections | `list_class`: per heading, count + words; read where prose, else below-floor |
| axis residue (R3) | pages no axis signal reaches | `axis_residue`: count |

Anything with real prose is read. A true floor (pure markup, an empty
template stub) is a named, counted class for the council — never silence.

## 3. R3 (T2b) — the store time axis

### The gap

`placement_time_axis` knows only the manga signals (arc page → arc fact →
chapter / episode → residue). After the placement runs: `temporal` =
marvel 20/1,149 and mcu 0/6,053. The deterministic order signals are on
disk.

### Signal coverage (measured on the placement pages)

| series | pages | date | previous | next | first | last | partN | reality |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mcu | 1,323 | 1,286 | 1,277 | 1,280 | — | — | 121 | — |
| marvel | 213 | 1 | — | — | 211 | 72 | 90 | 209 |

`date` value shapes (mcu sample): `YYYY` (110), `Month YYYY` (742, incl.
`April 15, 1946`), ranges (`2020-2021`, `1500-1502`), era / season
(`Spring 2011`, `Early 1931`). Parser: extract the years (range → the
first), optional month / day; unparseable → residue, counted.

### Declaration (overrides — the only place a per-wiki rule may live)

```yaml
events:
  axis:
    date_keys: [date]                   # absolute rank: parse the date value
    chain_keys: [previous, next]        # linked-list order, walked per partition
    order_keys: [first, last, "part*"]  # values cite a page; rank is inherited
    partition_key: reality              # marvel: one axis per reality value
```

mcu declares `date_keys` + `chain_keys`; marvel declares all four. A wiki
that declares nothing (JJK) sees no change.

### Engine (new `store_time_axis` in `timeaxis.py`; no model, no GPU)

1. Partition the placement + supplementary pages by the `partition_key`
   value (no key → one partition; a missing value → its own counted bucket).
2. Within a partition, build the order, strongest signal first:
   - `chain_keys`: walk previous/next as a linked list; an edge is followed
     only when **both** ends are in the partition (the `chronology.chains`
     restriction keeps soundtracks and polls out of a story timeline);
     longest chain first → chain position.
   - `date_keys`: parsed (year, month, day) rank; orders the pages the chain
     does not cover; where a page carries both, the agreement is checked and
     counted.
   - `order_keys`: a value that cites a page (a first / last appearance
     issue, a `partN` instalment) inherits the cited page's axis rank via
     the existing citation machinery (`citation_arc_maps`, generalized).
     A citation the wiki does not file stays unmapped — a wiki gap, not a
     number to invent.
   - residue → `residue` (counted).
3. `placement_time_axis` gains one branch, after the manga signals and
   before residue:
   `arc_page > arc_fact > chapters > store_axis > residue`.
4. `backfill_event_arc_index` writes `arc_index` from the extended axis;
   `recompute_temporal` (already pure SQL, idempotent) re-derives
   `temporal` on the stored rows. One run per store after the axis lands —
   no GPU.
5. Fact / lead passages inherit the page's axis rank: `section_time_ranks`
   falls back to the page's store-axis rank when the page carries one,
   else to the in-value ordinal (the rev-1 rule, kept as the fallback).
6. Cross-partition order (marvel's per-reality axes) is value-sorted — a
   named assumption; within a partition the order is the wiki's own
   publication order.

Expected (verified at the dry-run and the gates): mcu `temporal`
0/6,053 → ~1,280 pages placed; marvel 20/1,149 → ~210/213 pages placed.

## 4. R4 — window-overlap dedup + the PK

- 4,000-character windows with 300-character overlap will surface the same
  verbatim quote twice. The save path dedups on
  `(doc_title, passage, subject_node, verb, object_node, quote)`; the first
  window wins; drops are counted (`dedup_dropped`) so the D4 cross-page
  checks do not double-count.
- Under R3, the fact passages of one page share the page's axis rank, so the
  same (S, v, O) across two fact values of one page can collide on the
  current PK `(subject_node, verb, object_node, section_id, time_rank)`.
  Fix: **`passage` joins the events PK** (fresh schema, the
  `_migrate_events_to_fk` schema, and the migration carry-through); the
  durable key is `(doc_title, section_ordinal, passage)`.

## 5. R5 — the pilot: full-scope mix

50 passages on the one Qwen slot (`--workers 1`), mix:

| series | mix |
|---|---|
| marvel (30) | history 12 · synopsis* 8 · Origin / Early Life 5 · Chronology Notes 2 · Publication Notes 2 · lead 1 |
| mcu (20) | Biography sub-section 5 · Relationships 3 · Abilities 4 · Dialogue 3 · Allies/Enemies (list class) 3 · lead 2 |

Record, per passage: s/passage, rows/passage, and the gate-reject reason
**per class** (unknown participant / unverbatim / off-axis / below-floor /
furniture / dedup-dropped), plus the batching probe (10 `history` values,
4 passages per call) — the throughput number the council needs for R6.

## 6. R6 — budget framing for the council (coverage fixed)

The honest queue (measured):

| series | section prose | fact values | leads | below floor (counted) |
|---|---:|---:|---:|---:|
| marvel | 11.53M w (49,409 sections) | 168.2M chars (174,298 windows) | 3.88M chars (2,981 ≥40w leads; more at 20w) | 20,420 sections / 68,521 w |
| mcu | 12.99M w (75,809 sections) | — | 3.91M chars (7,364 ≥40w leads; more at 20w) | 111,533 sections / 295,088 w |

≈ 24.5M section words + 168M fact characters — far beyond "~7 days on 3
slots" (rev 1 sized the queue at ~5% of the prose). The council's job (T4)
is throughput: batching (the pilot probe), the Qwen dial and slot use, run
length, and ordering (event-dense pages first, so the D4 rows land early).
Coverage is not on the table.

## 7. Tests, then the four gates

Unit: fnmatch / case-insensitive key matching; in-value ordering
(`synopsis2` < `synopsis10`); the floor guards (template lead dropped and
counted, prose lead kept); the heading-agnostic prose scope + furniture
(generic + wiki-declared, per-heading counts with cause); guard accounting
present in the dry-run output; the store axis (date parsing incl. ranges /
eras, chain walk with the partition restriction + agreement check,
order-key citation inheritance, residue counted); recompute on stored rows
(promoted / demoted tallies); the PK with `passage` (two fact values, same
(S, v, O), same rank → both stored); the dedup (same quote from two windows
→ one row, one counted drop); `remap_derived` re-anchor on a changed fact
value + stale revid + passage PK; JJK baselines (`placement` / `corpus`
identical; a JJK `all` re-run adds the new classes, recorded — the
standing gates do not measure JJK's event queue, so no baseline moves).
Then the four standing gates (pytest; eval jjk; span-recall jjk;
canon-run opm) before the run is declared.

## 8. T1 receipts (open, running in parallel)

- the marvel `story_arc` re-run (15 pages) — in flight (chain pid 185122,
  started 08:17);
- the 2 mcu retries at `SCRIPTENGINE_ANSWER_TOKENS=20480` — queued after
  marvel in the same chain;
- receipt `reports/marvel/receipts/t1_placement_2026-09-28.md` at chain
  end: both runs' counts, the 2 budget failures and their outcomes, cache
  state, post-run store counts.
# The gate — three mechanical equality checks, nothing to grade

Subject: the same `jjk` 714-event set Phases 1–3 built (108 placement pages,
`arc_index` backfilled onto every row). The gate is the plan's §2c check:
**not** a score, there is no gold, nothing an agent can be generous about. It is
string and foreign-key equality in three parts, and it reports what the wiki's own
editors agreed — and, in full, where they did not.

Nothing in the gate calls a model. It reads the `events` table and the time axis
(`scriptengine/ingest/gate.py`), and the `comprehension-gate` command prints it.

## The three checks

1. **Arc placement.** A temporal event states an order on the story; the arc its
   page sits under must be on the time axis. A row whose page the axis cannot
   place is a dangling placement and is recorded *as* a standing state
   (`temporal=0`), not left dangling. A write, reported as a count.
2. **Cross-page agreement.** The same event — one `(verb, participant-pair)`, the
   pair a *set* so `A fought B` and `B fought A` are one fight — stated on two or
   more source pages must carry one `arc_index`. Editors who did not write each
   other's pages cannot be talked into agreement, so a disagreement is a real,
   measured comprehension failure. **Every** disagreement is returned in full
   (both rows, pages, quotes, `arc_key`, `arc_index`), not a summary count.
3. **Coverage split.** The share of narrative beats (the page's prose sections)
   that carry a surviving row, temporal versus atemporal.

## Measured on the 714-event set

- **Arc placement: 0 dangling.** Every temporal row's page is on the axis, so
  nothing was flipped to a standing state. (The single residue page, `Kyoto
  Sister-School Goodwill Event`, contributes no temporal row.)
- **Cross-page agreement: 38 disagreements** out of 341 `(verb,
  participant-pair)` groups — 153 of which (45%) are stated on two or more pages,
  115 of those agree on one arc. 22 of the 38 are flagged **modelling problem**
  (well-populated group, minority arc) — the halt rule's "flag before you read it
  as the wiki contradicting itself."
- **Coverage: 61.9%** of the 388 narrative beats carry a surviving row, all of it
  temporal (0.0% atemporal — the placement set is narrative, so Phase 2 stored
  every event as an order, not a standing state).

## The structural read of the 38

Two different phenomena share the disagreement bucket, and the split matters:

- **27 are single-participant recurring verbs** — `arrived` (16), `departed` (9),
  `awakened` (2). "Satoru Gojo arrived" is true in six arcs because Gojo arrives
  in six arcs; these are *distinct* occurrences of a recurring action, not one
  event placed inconsistently. The `(verb, participant)` key is too coarse for
  them. This is a **keying** modelling problem, not a wiki contradiction.
- **11 are two-participant interactions** — `fought` (8), `killed` (2), `saved`
  (1). These *are* "the same fight, stated on two pages, filed under two arcs"
  (e.g. `Mahito, Yuji Itadori` at arcs 2 and 6; `Satoru Gojo, Sukuna` at arcs 1
  and 8, which is the two genuinely different Gojo–Sukuna fights). These are the
  real comprehension failures the gate exists to surface.

The recurring-verb case says the next refinement is to the **key** (a recurring
action is not one event), not to the wiki. The interaction case is what a frozen
acceptance set (the plan's twenty failures) is meant to pin down.

## Verified

- **Idempotent.** `enforce_arc_placement` flips the dangling rows once; a second
  run finds nothing (`tests/test_gate.py`).
- **Stats reconcile.** `agreeing + disagreeing == multi_page_groups` and the full
  list is exactly the disagreeing groups; every disagreement spans ≥2 arcs and ≥2
  pages; rows order unplaced-first then by arc.
- **CLI door.** `comprehension-gate --series jjk` prints the tally, every
  disagreement in full (page, resolved arc, page-clock, direction, quote), and the
  coverage split; `--only-problems` keeps just the 22 flagged; `--limit N` caps.

## Standing gates (re-run after the gate)

| gate | baseline | gate |
|---|---|---|
| pytest | 1152 passed | 1163 passed (+11 gate tests) |
| eval jjk | 24/24 | 24/24 |
| span-recall jjk | 48,570/48,572 (2 misses, rc=2) | 48,570/48,572 (2 misses, rc=2) |
| canon-run opm | 10/16 · 236/236 · 79.0% | 10/16 · 236/236 · 79.0% |

The gate is reachable only from `comprehension-gate` and `gate.py`; nothing on a
default retrieval path touches it, so the gates are structurally unaffected and
were re-run clean (`:8000` CUDA API stopped for pytest, relaunched for canon-run).

## Step 3b — corpus scope (complete)

The gate is proven on the 108-page placement set. Step 3b widens extraction to the
full corpus: a section is in scope when its heading **narrates** (title in
`{synopsis, summary, plot, plot details, history, overview, story, development,
background}`, or the wiki named it after the arc it walks, e.g. a character's
`Culling Game Arc`) **and** the section's chunks name at least **two** of the
wiki's own character nodes. Character-family page types are read off the wiki's
own type names (any type carrying `character`) — nothing about which types count
is a series name. Exposed as `events-extract --scope corpus` (placement set is
`--scope placement`).

Measured on JJK: **524 pages / 964 sections / ~1,279 LLM windows**, reaching
character `Synopsis`/`History` and chapter `Plot Details`, where most of a
character's own history actually lives.

**First run failed 508/524 pages** with `[Errno 111] Connection refused`: the
27B Qwen model OOM-crashed because the `:8000` API's GPU reranker (4.1 GB)
competed with Qwen (24.6 GB) for the 32 GB card, leaving only 3.3 GB. Fix:
**dedicate the GPU to the Qwen model** (stop the `:8000` API → 7.4 GB free) and
raise the answer budget (`SCRIPTENGINE_ANSWER_TOKENS=16384`, one page had spent
its whole 8192 on reasoning and never answered). Hard rule now in `CLAUDE.md`:
the extraction model owns the GPU. Re-launched on the dedicated GPU; re-runs skip
the cached pages, so a mid-run crash resumes cheaply.

**Results** (dedicated-GPU re-run, 2026-09-05). This is a **data step, not a
comprehension win**: it widens the event set and re-runs the gate, but adds no
placed events.

Extraction: 524 considered, **509 extracted, 15 cached, 0 failed** → the event
set grows **714 → 2,748** (+2,034). Reconciled: the crashed first run completed
16 of 524 (508 failed on the OOM); on the re-run 15 of those were cached and 1
re-extracted (a zero-event / revid-changed page — zero-event pages never cache,
so they re-extract every run), giving the tidy 509 + 15 = 524.

The 2,034 new rows are **all `temporal=0` and off-axis** (`arc_index IS NULL`);
the placeable set is unchanged — **`temporal=1` is still 714**, the pre-corpus
baseline. How the 2,034 got there: `backfill_event_arc_index` maps the **page**
(`arc_key`) to an `arc_index`, and the gate flips `temporal=1 AND arc_index IS
NULL` to a standing state (`temporal=0`, gate.py:48,64). So **1,160** were
temporal rows on *non-axis pages* that dangled and were demoted; the **874**
rest (2,034 − 1,160, exact by construction) were already `temporal=0` at
extraction. The gate leaves no per-row marker, so the 874 aren't individually
isolable post-gate — the count is exact, the per-row label is not.

**Why the number came out flat — the real mechanism (verified, not a floor).**
The off-axis rows are not *unplaceable*; the placement logic simply never reads
the one free signal that would place them:
- **995 of the 2,034 (48%) sit under a section heading that names an arc — and
  all nine such headings (`Culling Game`, `Shibuya Incident`, `Shinjuku
  Showdown`, `Gojo's Past`, `Fearsome Womb`, `Kyoto Goodwill Event`, `Cursed
  Child`, `Death Painting`, `Vs. Mahito`) are on the placement axis.** The
  backfill keys on the *page*, so a character `Synopsis` page is off-axis even
  though its `Shibuya Incident Arc` section names the exact arc to attach to.
- The other **1,039** sit under generic headings (`Plot Details` 708, `Summary`
  215, `Overview` 98, `History` 18); **~209 of those carry a `Chapter`/`Episode`
  citation in the section text**, a second free signal, and many come from
  Episode/Chapter pages themselves.

So "flat 714" is a **symptom of the placement key, not a content floor**: the
backfill maps by page only and ignores the section heading and the in-text
citation. Extending `backfill_event_arc_index` to consult both is the
continuity-check placement pass (below); it is not a 3b defect — the same gap
already left the baseline's non-axis temporal rows dangling.

- **Cross-page agreement: 684 groups, 390 from 2+ pages, 352 agree, 38
  disagree.** Against the 714-event baseline (341 / 153 / 115 / 38): agreeing
  *groups* roughly triple (115 → 352), the agreeing *fraction* rises 75% → 90%,
  and the **disagreement count holds at 38** — the widening corroborates the
  same events from more pages and surfaces no new disagreement *classes*. (A
  self-consistency check on one wiki: it catches the extractor contradicting
  itself, not the wiki being wrong.)
- **Coverage: 61.9%** of the 388 placement-page narrative beats carry a
  surviving temporal row (0.0% atemporal) — unchanged, because the beat set is
  the fixed placement pages and only the off-axis event set grew.

**Test-invariant change (deliberate).** `test_backfill_places_every_row` now
asserts off-axis rows are *justified by temporality* — `arc_index IS NULL` ==
`count(temporal=0 OR residue-page)` — not that *everything* is placed. Verified:
`count(arc_index IS NULL AND temporal=1) = 0` (no temporal row lost). A real
invariant (a lost temporal row still fails it), not a tautology.

**Known hazards / follow-ups (queued, not resolved here).**
- *Placement-signal gap (the continuity-check placement pass):* extend
  `backfill_event_arc_index` to also map by **section heading** (995 rows) and
  by **in-text `Chapter`/`Episode` citation** (~209 more), registering the
  corpus pages that carry them on the axis. A rescue that only writes
  `arc_index` is clobbered by the next gate run, so the corpus pages must be in
  the placement axis, not just patched per-row.
- *Re-index id-dangling (pre-existing, latent, amplified by 3b):* `reset()`
  drops `nodes`+`sections` (reassigning rowids) but keeps `events`, whose PK
  carries node/section ids with no FKs. A routine `index` after extraction would
  dangle the 139 node + 838 section refs; the gate (groups by node-id pair)
  would silently stop grouping. Currently clean (no re-index since extraction).
  Fix: add FKs, or re-extract events after a reset. (Out of 3b's additive scope.)
- *Scope-shrink check:* diff the pre/post-scope candidate sets to rule out a
  masked recall loss (the new scope replaced the old node-degree-2 scope).

## Commands

```
python -m scriptengine.cli comprehension-gate --series jjk
python -m scriptengine.cli comprehension-gate --series jjk --only-problems
python -m scriptengine.cli comprehension-gate --series jjk --limit 10
```
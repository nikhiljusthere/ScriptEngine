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
| pytest | 1152 passed | **1,202 passed** (2026-09-05, post id-stability FK) |
| eval jjk | 24/24 | 24/24 |
| span-recall jjk | 48,570/48,572 (2 misses, rc=2) | **48,572/48,572 (0 misses, rc=0)** |
| canon-run opm | 10/16 · 236/236 · 79.0% | 10/16 · 236/236 · 79.0% |

The two historical span-recall misses are now excluded as link-list boilerplate
(52 such sentences are excluded by default; `--include-boilerplate` audits
them), so the gate reads 100% / rc=0. 2026-09-05 re-run after the
continuity-check scaffold: all four gates green (`:8000` on CPU per the
CUDA-first device rule — Qwen holds the GPU and cannot be freed).

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
`--scope placement`); the two rule sets proved disjoint on JJK, so the
complete-coverage path is `--scope all` (the "Scope-shrink check" section).

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
- *Placement-signal gap — RESOLVED* (the "Placement-signal fix (complete)" section
  below). `backfill_event_arc_index` now maps by section heading (995) and
  chapter/episode `arc` fact (885). The in-text `(Chapter N)` regex (sparser,
  ~62/1,039) is deliberately **not** added — a documented residual, never a guess.
- *Re-index id-dangling — RESOLVED* (the "Id-stability FK on `events`" section
  below): `events` now carries CASCADE FKs to `nodes`/`sections`, so a
  renumbering re-crawl can no longer dangle a ref. The section signal's
  document guard remains as defence in depth.
- *Scope-shrink check — RESOLVED* (the "Scope-shrink check + `--scope all`"
  section below): the pre/post candidate sets are **disjoint** on JJK (0 of
  388/964 sections overlap; all 714 temporal events sit in placement-only
  sections), so a corpus-only re-extract would mask a total recall loss of the
  placement set. Fixed in code: `scope_plan` + the `--scope all` union.

## Placement-signal fix (complete)

The placement-key gap 3b flagged — the backfill mapped by **page** only, so the
995 arc-named-section rows and the chapter/episode rows stayed off-axis — is now
closed **in code** (`timeaxis.py`), not a data-UPDATE (which the next gate run
would clobber). Two cheap, model-free signals, both reading only the wiki's own
facts:

1. **Section signal.** A character/synopsis page files its per-arc prose under
   sections titled after the arc ("Culling Game Arc"). `section_arc_index` maps
   `section_id → arc_index` by matching the section title to an on-chain arc page
   (`match_arc` + `story_arc_index`), resolved through the live `sections` table
   with a document guard (the section's owning page must be the event's page). A
   dangling or reused id (a renumbering re-crawl) degrades to a **miss, never a
   wrong arc** — which also makes the queued id-dangling hazard load-bearing but
   safe.
2. **Chapter/episode page signal.** Those pages carry their own `arc` fact ("Chapter
   0-1 → Cursed Child Arc"); the axis now walks them (they are not placement types),
   placing their events by the same `arc_fact`/`chapters` signals trusted for
   placement pages.

The backfill places per **(page, section)**: the section index refines the page
index. Measured on JJK:

| | before | after |
|---|---|---|
| `arc_index IS NULL` | 2,034 | **154** |
| section signal placed | — | 995 |
| chapter/episode page signal placed | — | 885 |
| placement-page rows preserved | 714 | 714/714 |
| `temporal=1 AND arc_index IS NULL` | 0 | 0 |
| cross-page disagreements | 38 | **107** |

The **154 residual** is not placeable by a cheap verifiable signal: 116 sit under
generic headings on character/synopsis/location/technique pages (no arc the wiki
names), 38 are chapter pages filed under an arc **off the story chain** (a real
arc, but no orderable position). Forcing them would manufacture misplacements;
NULL is the correct answer. Owner of the 116: the continuity-check consumer.

**The 38 → 107 disagreement jump is the fix working, not a regression.** The
cross-page check ignores `arc_index IS NULL`, so before the fix a group filed as
`{NULL, 6}` read as *agreeing*; placing the 1,880 rows surfaces the wiki's genuine
cross-arc filings (a scattered arc-pair distribution — (7,8), (6,7), (3,6), (0,8)…
— with real quotes like "Aoi arrived" filed under Fearsome Womb / Kyoto / Shibuya
/ Shinjuku). Not a systematic off-by-one, which would show one dominant arc pair.

**Read it as a rate, not a count (A2 / A5).** The 107 disagreements are
**27.4% of the 390 multi-page-corroborated groups** (390 groups come from ≥2
source pages; 283 agree, 107 disagree). The jump from the pre-fix ~38 (≈9.7%)
to 107 (27.4%) is *not* "the wiki got 3× more contradictory" — the denominator
is essentially flat (390 multi-page groups; pre-fix 341 → post-fix 390 is new
corroboration, not new contradiction). The structural cause is placement
provenance: of the 2,594 placed rows, **1,599 are arc-named (page signal:
`arc_fact` 1,396 + `arc_page` 200 + `chapters` 3) and 995 are
section/citation backfill** (a section titled for an arc on a page that is
itself off the story chain). Splitting the 390 groups by the provenance of
their rows:

| group row-provenance | multi-page | disagree | rate |
|---|---:|---:|---:|
| arc-named only (page signal) | 86 | 9 | **10.5%** |
| section/citation backfill only | 36 | 5 | 13.9% |
| mixed (both) | 261 | 93 | **35.6%** |
| unplaced-only | 7 | 0 | 0% |

**98 of the 107 disagreements (92%) involve at least one section-placed row.**
Pure arc-named groups sit at ~10.5% (the original ~9.7% — genuine wiki
self-contradiction, a corpus truth); the 35.6% mixed rate is driven by the
995-row section backfill filing the same event in a different arc than the
arc-named pages do. Because D6 is tautological (above), **cross-page agreement
is the only signal that can flag a wrong placement** — and it points squarely at
the section backfill. That is **B5**. *Re-scoped by the spot-check*
(`COUNCIL_b5-premise.md`): grounding the 9-arc chapter table and classifying all 107
shows **56% are key-coarse repeat-encounters** (the same pair genuinely spanning
arcs — Gojo fights Jogo in three different arcs) and **21% are arc-boundary
artifacts**, leaving ~0 unambiguous misplacements. So B5 is a **diagnostic +
key-refinement** (add a chapter component to the `(verb, subject, object)` key;
surface the 107 to R1's per-line meaning index), **not** a demotion gate that
overwrites section rows with the arc-named majority — that would demote
legitimate multi-arc events.

**Test re-derivation (deliberate, non-tautological).** `test_backfill_places_every_row`
is replaced by pinned invariants: the 995 section-placed count, the
`temporal=1 ⇒ arc_index` rule, a section-index-agrees-with-the-arc-page check, and
negative tests (a non-arc section places nothing; a section only places its own
page's events — the document guard). Full suite 1,168 → 1,175 (+7, all green).

Record: `COUNCIL_placement-signal.md` (5 advisors + 5 peer reviews + verified ledger).

## Continuity-check scaffold (D6 consumer, shipped)

The placement-signal fix named an owner of the 116 generic-heading rows above:
the continuity-check consumer. This section is that consumer, shipped as a
scaffold — a **validation layer, not a rejector**. A gap is a *flag, not a
verdict*: it names a beat that references an event out of order (three arcs
early, or a filing two arcs off the wiki's own cross-page majority) and leaves
the flashback/recap call to the writer. Model-free. Design record:
`COUNCIL_continuity-check.md`.

Ships with: `scriptengine/ingest/continuity.py` (`adjudicated_arc`, `beat_gap`,
`walk_monotonicity`, `knowledge_frontier`, `triage_filings`, `run_gold`);
`scriptengine/eval/gold_continuity.json` (frozen top-20 draw of the 31
interaction-verb filings); the `continuity` CLI door; 19 tests. Full suite
1,175 → 1,194 (+19, all green); `test_gold_hygiene` now skips non-question gold
sets (the `cases` schema is not a `questions` bank).

**Measured on JJK (post placement-signal fix).** The 107 cross-arc filings
triage as: **26 adjacent** (span=1 boundary straddle, not anachronisms),
**50 state-verb** (arrived 30 + departed 20 — a coarse `(verb, participant)`
keying problem, not a wiki contradiction), **31 interaction-verb** (fought 12 +
saved 10 + killed 5 + awakened 4). The 31 is the anachronism core, split
**9 premature + 22 delayed** (0 both). The plan's "twenty real failures"
bouncer passes either-direction (31 ≥ 20); the literal what-X-knew subset is
the 9 premature — an honest thin signal, recorded, not rephased away. 62
filings are `modeling_problem` (group ≥4, majority <0.8) — recorded, not
auto-fixed. Span histogram: 1:26, 2:17, 3:8, 4:5, 5:10, 6:11, 7:17, 8:13.
Knowledge frontier: Yuji Itadori → 386 events ≤ arc 7 (298 ≤ arc 6; 447 total).
The frozen gold set holds 20/20 against the live store.

**Non-circular by construction.** The "actual" arc a gap is measured against is
the wiki's own cross-page majority filing — a corpus truth, independent of the
`events.arc_index` axis under test (`chapter_arc_index` reads the `facts`
table, timeaxis.py:183). A re-index that silently moved an event breaks a gold
case and is caught by `tests/test_continuity.py`.

**Hazards / hand-off.** The 50 state-verb and 26 adjacent filings are excluded
from the core (keying + boundary straddles, not anachronisms). The 116
generic-heading placement residual is owned by this consumer's **write-layer
(D6)** — not yet built. The real *script-line* harvest is deferred:
`scripts output/` is thin (no per-beat `sourced:` headers yet), so the gold set
is corpus-derived (the 31 filings), not harvested script lines.

## Scope-shrink check + `--scope all` (complete)

The follow-up the 3b record queued — diff the pre/post-scope candidate sets to
rule out a masked recall loss — is run, and it **fails**: the two rule sets are
disjoint, and a corpus-only run would silently stop reading the entire placement
set.

**The check** (against `series/jjk/facts.db`):

| | placement rule (old scope) | corpus rule (3b scope) |
|---|---|---|
| pages | 108 | 524 |
| sections | 388 | 964 |
| overlap | **0 pages / 0 sections** | — |

JJK's placement pages (arc/event/battle) carry no narrative-family headings —
their sections are titled Battle/Aftermath/Prologue, stage names, "Setting" — so
the corpus rule never admits one of them. The 388 placement-only sections hold
165,941 words, and **all 714 `temporal=1` events** (prompt `events-2026-09-05.2`)
sit in them. A future `--scope corpus --refresh` would have re-extracted the 524
corpus pages and frozen the placement set: its rows would stop matching
`PROMPT_VERSION`/revid, the gate would see 714 dangling temporal rows, and
nothing would say why.

**The fix** (`events.py`): a testable `scope_plan(store, scope)` now drives both
the extract and the dry-run. `placement` and `corpus` keep their exact prior
semantics (locked by tests), and the new `all` scope is the union — a page both
rules cover reads the union of its sections, deduped by section id. On JJK the
union is additive: the three dry-runs print 108/388, 524/964, **632/1352**
(= 108+524 / 388+964, zero dedup needed). On a wiki whose rules do overlap, the
dedup branch applies. `--scope all` is the documented complete-coverage path for
`--refresh` runs.

Gates re-run green: pytest **1,198** (was 1,194, +4 scope-plan tests);
span-recall 48,572/48,572 (rc=0); eval 24/24; canon-run opm 10/16 · 236/236 ·
79.0% (report `2026-09-05-1041`, API relaunched on CPU per the CUDA-first rule).

## Id-stability FK on `events` (complete)

The 3b council queued this one: the `events` table is keyed on `nodes`/`sections`
ids, but those ids are **not stable** across an `index` run (a re-crawl
re-numbers them). Without a constraint, a renumbering re-crawl would leave the
stored event rows pointing at ids that no longer exist (or worse, that now mean
something else) — a silent id-dangling the section-signal guard made a *miss*
but never prevented. The fix is the FK, not a rephrase.

**The contract** (`schema.sql`, `facts.py`):
- `events.subject_node` / `events.object_node` → `nodes(id)`,
  `events.section_id` → `sections(id)`, all **ON DELETE CASCADE**. The table now
  dies with the graph that gave its rows meaning.
- An `index` run (which renumbers) drops the events with the graph and rebuilds
  the table empty; `events-extract` is the only way back. The rows are local
  inference keyed on *this* build's ids, so a renumbering build has invalidated
  them anyway — the wipe is the feature, not the loss. `reset()` lists `events`
  first (it is the child), then `initialise()` brings the empty table back so the
  unguarded gate/time-axis readers keep working.
- The CLI `index` command counts the events before and after and prints a yellow
  note when rows were dropped, telling the writer to re-run
  `events-extract --scope all`.

**Migration for pre-FK stores** (`ensure_events` → `_migrate_events_to_fk`): a
store that predates the FKs has its `events` table rebuilt with the references,
keeping only the rows whose refs still resolve (a dangling row is a miss every
reader already guards for, so dropping it loses nothing). It returns how many it
dropped and logs them. On a clean store the migration is a no-op (returns 0); a
second call sees an FK table and migrates nothing.

**Verified on JJK** (`series/jjk/facts.db`, read-only): all **2,748** event rows
survived the migration with `dropped=0`, the three CASCADE FKs are attached,
`integrity_check=ok`, 0 dangling refs, and no leftover `events_fk_migrated`
table. The four new `TestEventsForeignKeys` cases pin: the FKs on a fresh table;
a graph rebuild (drop `sections`) cascades the events away; `reset()` empties the
events but brings the FK table back; and a pre-FK table migrates, dropping only
its dangling row.

**Accepted cost.** After any `index` the stored events are gone until a full
re-extract (~1,670 LLM windows on the Qwen GPU). That is deliberate: a stale
event set referencing a renumbered graph is worse than an empty one. The
re-extract is the documented recovery, not a bug.

Gates re-run green this pass: pytest **1,202** (was 1,198, +4 FK tests);
span-recall 48,572/48,572 (0 misses, rc=0); eval 24/24; canon-run opm
10/16 · 236/236 · 79.0% (report `2026-09-05-1056`, API relaunched on CPU per
the CUDA-first rule — Qwen holds the GPU).

## Step 1 — recompute `temporal` from the live placement (2026-09-05)

The check-3 event test is keyed on the placement the backfill computes, but the
`temporal` flag was written once at extraction and never updated — so it sat
frozen at the 714-event placement-set count while the corpus rows, placed by the
section signal, were mislabelled `temporal=0`. `recompute_temporal` re-derives
`temporal` from the placement that already exists: `eventive verb AND
arc_index IS NOT NULL` → `temporal=1`, else `temporal=0`. Pure SQL, no model,
idempotent (a second run moves nothing).

**The data change (the point of the step, not the build status):**

| measure | before | after |
|---|---:|---:|
| `temporal=1` | **714** | **2,594** (+1,880) |
| `temporal=1` & `arc_index IS NULL` (dangling — D6 violation) | 0 | **0** |
| `temporal=0` & `arc_index IS NOT NULL` (placed-but-off-axis — D6 violation) | **1,880** | **0** |
| `temporal=0` & `arc_index IS NULL` (standing state, expected) | 154 | **154** |
| total | 2,748 | 2,748 |

Both D6 violations are now **0**: every placed eventive row is `temporal=1`, and
the only `temporal=0` rows are the 154 genuinely unplaceable ones (recorded
standing states). Re-verified against the live store independently.

**Stated limitation — D6 is a consistency check, not a chronology check.** All
**2,748 rows are eventive** (the 8 stored verbs are exactly `EVENTIVE_VERBS`;
0 non-eventive), so the `eventive verb` conjunct in `temporal = eventive AND
arc_index IS NOT NULL` is always true and `temporal` reduces to
`arc_index IS NOT NULL` — the *same* signal the backfill used to place the row.
The two D6 invariants (no dangling `temporal=1 & arc_index IS NULL`; no
placed-but-off-axis `temporal=0 & arc_index IS NOT NULL`) therefore pass by
construction: they certify flag↔placement **consistency**, never that the
placement is **chronologically correct**. A row placed in the *wrong* arc still
satisfies both invariants. With D6 tautological, the only non-tautological signal
is **cross-page agreement** (below). The spot-check (`COUNCIL_b5-premise.md`)
showed it is *mostly* key-coarseness, not a misplacement detector — 56% of the
107 are repeat-encounters (the pair genuinely spans arcs) and 21% boundary noise —
so B5 is a **diagnostic + key-refinement**, not a demotion gate.

**Beat-ordering guard (the check none of the four standing gates cover).** The
narrative reorderer only reorders on `temporal=1` events, so the flip from 0 →
2,594 could have scrambled corpus-page beat order. The guard was re-run on the
**full corpus — every page with ≥2 stored events (412 pages)**, replicating
`_reorder_by_events` directly against the store (no model, no GPU): per page,
article order (sections by ordinal) vs. event order (each section carries the
earliest `time_rank` of its temporal events; unranked sections inherit the last
seen rank). The reorderer **moves beats on exactly one page — `Shibuya
Incident` (70 events, a true top-5) — and is a no-op on the other 411**
(`changed: false`): their article section order already matches the story clock.
**No degradation: activating the flag on 2,594 events reorders one page into
story order and leaves 411 untouched.** (An earlier pass claimed this on "the
five highest-event pages" but had actually tested one top-5 page plus four
low-event pages — `Yuji Itadori/Synopsis` (83), `Larue` (6), `Chapter 0-4` (12),
`Episode 46` (18), `Sendai City` (6) — and *missed* `Shibuya Incident`, the one
page the flag does move. The full-corpus run above is the real guard.)

**`time_rank` clustering (ruled out as a second predicate gap — closed).** The
**14 pages with 8+ temporal events on a single rank** (`Chapter 150 · 246 ·
248`, `Episode 8 · 19 · 33 · 38 · 39 · 44 · 51`, `Naobito Zenin` · `Naoya Zenin`
· `Ryu Ishigori` synopses, `Yuki Tsukumo & Choso vs. Kenjaku`) each carry their
*events* in **exactly one event-section** (the page has more sections, but the
extracted events sit in one, e.g. `Plot Details`) — one narrative section, one
clock position, so a single rank is correct, not a collapse. Across all **463
arc-keys with temporal events, 462 have distinct ranks == distinct
event-sections**. The one exception, `Shibuya Incident` (14 event-sections, 12
distinct ranks), ties its two extra sections on **concurrent scenes at the same
timestamp** (8:51 P.M. and 9:22 P.M. each run two parallel threads) — correctly
tied, not a loss. **No second predicate gap.** (Handoff's "12 pages / 508
arc-keys" was stale — now 14 pages over 463 temporal-event arc-keys; the 508 is
the all-events distinct-`arc_key` count, of which 463 carry temporal events.)

Gates re-run green this pass: pytest **1,204** (was 1,202, +2
`TestRecomputeTemporal`); span-recall 48,572/48,572 (0 misses, rc=0 — tier 0);
eval 24/24; canon-run opm 10/16 · 236/236 · 79.0% **at baseline** (report
`2026-09-05-1159`, API on CPU).

## R4 — in-text citation placement (complete)

The 154 unplaced rows of the placement-signal fix were not all
unplaceable. Phase 1 of the D6-completion plan (`COUNCIL_d6-completion.md`)
ordered: place them, bar "unplaced = 0 or each remainder explicitly
triaged with a recorded reason". The third, weakest, model-free signal --
the wiki's own in-text citation -- reaches 90 of them (`timeaxis.py`:
`citation_arc_maps`, `_citation_groups`, `_citation_decision`, and the
citation pass in `backfill_event_arc_index`):

- **Paragraph rule.** A citation covers the sentences before it (the
  wiki's citation grammar, the same rule the `sourced:` headers use), so
  the paragraph that states the event is the one that files it: its
  citations all mapping to one arc places the row in that arc.
- **Section-scope rule.** A section cited at least twice into a single
  arc has its scope fixed by the wiki; every event stated in it sits in
  that arc. One citation files no scope (it covers one sentence, not
  the section).
- **The maps are the wiki's own filings** -- `chapter_arc_index` (the
  battle pages' `chapters` fact files each chapter under that battle's
  arc) and the episode pages' `arc` fact (the axis already walks episode
  pages). A number no page files stays unmapped, not guessed. The
  side-story citations ("Modulo Chapter N") name the JJK Modulo
  numbering and are skipped: a miss, never a wrong arc (pinned by
  `test_side_story_citations_place_nothing`).

Measured on JJK:

| | before | after |
|---|---:|---:|
| `arc_index IS NULL` | 154 | **64** |
| rows placed by the citation signal (tally, stable across settled re-runs) | — | **90** |
| `temporal=1` | 2,594 | **2,684** |
| cross-page disagreements | 107 | **109** (281 agree; two groups that read as agreeing while their rows were NULL now carry arcs and disagree) |

**The 64 remainder is triaged, not silent** (`comprehension-gate
--triage` -> `triage_unplaced`, the ledger door): 53 `no-citation`
(including the 38 JJK-Modulo side-story chapters, whose citations are
the Modulo numbering) + 11 `citations-span-arcs` (a character's whole
life cited across 2-6 arcs; no single placement is determinate). Every
ledger row carries its reason, *derived* from the same lookups the
backfill runs, so a re-crawl that moves a wiki filing moves the ledger
with it. No unplaced row stands without a recorded reason (D6).

**Verified.** The backfill stays idempotent: the citation tally counts
rows the signal places *by right*, not rows it UPDATEd this run, so a
second (settled) run reports the same 90. `test_citation_signal_places_
the_cited_rows` pins 90 / 64; `test_triage_ledger_accounts_for_every_
unplaced_row` pins ledger completeness; the 995 section-signal count is
unchanged. Spot-checked placements (Sukuna/Synopsis ch. 264 -> Shinjuku
Showdown; Episode 38's section -> Shibuya Incident; Maki vs Naoya
ch. 197 -> Culling Game) are the wiki's own filings, not inferences.

## X2.d — door censuses, D1 + D2 (complete 2026-09-07)

Phase 2 of the D6-completion plan: 100 fixed roster enumeration
questions + 100 fixed narrative chronological questions, run through
the same in-process path the `:8000` `/context` endpoint uses
(`build_context`, explicit door mode; `tools/census_doors.py`,
CENSUS_DEVICE=cuda, 98 s). The question sets are frozen data:
`reports/comprehension/census_roster_100.json` (stratified 70
character / 21 technique / 4 organization / 5 item, drawn from the
wiki's own ~1,355 declared rosters — each question is a declaration's
`name`, so every one is a question the wiki itself asks) and
`census_narrative_100.json` (60 character timelines / 9 arc overviews /
31 character-during-arc; arcs from the 9-arc story axis post-R4).
Re-runs execute the same 200; `--regen` only rebuilds.

| door | reached | bar (D1/D2) | |
|---|---:|---:|---|
| roster | **100/100 (100%)** | ≥99% | met |
| narrative | **99/100 (99.0%)** | ≥99% | met |

**Triage ledger (every non-ideal result has a recorded reason):**

- 1 narrative MISS — "What happened to Garry K. Johnson, in order?":
  the minor Culling-Game character has **0 extracted event rows**
  (extraction-coverage property of a one-arc side character, not a
  retrieval defect — there is nothing for the door to retrieve). His
  story prose *is* reachable: the qa door serves it (Culling Game
  Synopsis / Plot Details passages verified live). Class: corpus
  property, like `reached-uncited` in the 545 census.
- 13 roster `short` (retrieved < declared, all 100 still *reached*):
  12 "Every battle involving X" + 1 "Every battle involving Yuji
  Itadori" (23/24). The roster door pays members one at a time within
  the 6,000-token budget (the documented design — a 67-battle roster
  cannot fit in 6k tokens), so long sets truncate in order. Class:
  budget truncation by design; full-set enumeration is the R7
  roster-precision territory, not reachability. 87/100 enumerate fully.

Result file: `reports/comprehension/census_doors_results.jsonl`.
Both D1 and D2 hold with every miss triaged — the pre-committed
"red door → 2 repair iterations → council" branch never fired.

## X2.e — comprehension measurements 3a + 3b + 3d (complete 2026-09-07)

Phase 3 of the D6-completion plan: the measurement battery that decides
what (if anything) Phase 4 owes. All three ran on the settled post-R4
store (unplaced 64, temporal 2,684, cross-page 109 disagree / 281 agree).

### 3a — inexpressible-sentence cross-check (GREEN)

The 58 inexpressible sentences of the 8-verb spot-check
(`reports/comprehension/census_3a_inexpressible.json`; 61 uncovered − 3
now-`met` after the 1C verb ruling) probed verbatim against the `:8000`
qa door, auto-route, 2 independent runs — identical result:

- **56/58 HIT (96.6%)**, 2 MISS_DOC, persistent across runs:
  - item 086 (Chapter 102, "Yuji reveals Eso and Kechizu's last words…")
  - item 088 (Chapter 120, "Yuji regains control… Sukuna's rampage")
- Both pages **are** reachable by direct title/content query ("Chapter
  102" / "Chapter 120" both top their own beat). Diagnosis: the
  long-sentence-as-query ranking-granularity class — the whole sentence
  as query shape does not lift the page's own page into the top bundle.
  Same class as the historical span-recall background (2–3% miss at
  n=400; 2/58 ≈ expected 1.2 at this shape).
- **3a = GREEN: gate-coarseness diagnostic (B5 class), no build.** The
  R1 double-gate (3a >10 AND 3b red on the same content) is not met —
  3a is ≤10 and every red is the same content shape, not a meaning gap.

Result: `reports/comprehension/census_3a_inexpressible.probed.json`.

### 3b — per-dimension retrieval-not-extraction (GREEN, no extraction owed)

The frozen 140-question bank — 14 classes × 10 (the 12 §12 character
prose dimensions + Outcomes + Causality), `reports/comprehension/
census_3b_dimensions.json` — through the qa door in-process
(`tools/census_dimensions.py`; mechanical 3-term coverage first, then a
second anchored pass with `subject` set, then full-bundle human reading
of the surviving reds).

| pass | mech-green | notes |
|---|---:|---|
| auto-routed (no subject) | 115/140 | 25 mech-reds |
| + anchored (subject) | 130/140 | 15 of the 25 are routing-granularity (the door finds the answer when anchored on the subject) |
| full-bundle judgment of the 10 remaining reds | **139/140 substantively green** | 9 of the 10 were mechanical term misses — the answer content *is* in the served bundle (e.g. OC05: the battle infobox `Outcome` field is served verbatim; CT06: Idle Transfiguration mechanics served; HI08: "salaryman" served by a directly-worded probe) |

**The 1 genuine red:** EQ03 "What equipment does Hakari use?" — the
wiki records **no equipment for Hakari** (his page has no Equipment /
Cursed Tools section; he is a technique + hand-to-hand fighter). The
full anchored bundle (20k chars: every section of his page) contains no
equipment content. Class: **dimension-coverage property of the wiki**,
not an engine defect — Equipment is a thin §12 dimension (3,782 words
corpus-wide) and is served where the wiki has content (9/10 of the
class green, incl. Todo's shuriken, Nanami's blade, Maki's sword).

Consequences for Phase 4 (the council's contingent list):
- **Outcomes: 10/10 green** (battle infobox `Outcome` fields are served
  verbatim — the field already exists; no outcomes layer owed).
- **Causality: 10/10 green** (no causality layer owed — the "most
  likely owed" item is not owed).
- No extraction is owed by 3b; the single red names a wiki-coverage
  property, not a buildable layer (there is no content to extract).

Result: `reports/comprehension/census_3b_results.jsonl`.

### 3d — placement-gate false-negative audit (MET)

`tools/placement_audit.py`, model-free, using the B5 chapter-in-range
oracle (the council's B5 spot-check ranges: 9 arcs from
`timeaxis.chapter_arc_index`). Every post-R4 disagreeing group (109) is
re-grounded, plus a 40-group agreeing sample (seed 42) for false-
agreement. Classes: repeat-encounter (key too coarse) / boundary
(nearest arc within one index step — gap-chapter artifacts) /
out-of-range (≥2 index steps, flagged) / no-signal (no chapter fact).

| set | result |
|---|---|
| disagreeing 109 | 86 repeat-encounter / 11 boundary / 12 no-signal / **0 out-of-range** |
| agreeing sample 40 | **0 false agreements** |
| bar | 0 unflagged unambiguous misplacements → **MET** |

Consistent with the B5 baseline shape (pre-R4: 60/23/24; the R4-placed
rows moved groups from no-signal/boundary toward repeat-encounter).
Result: `reports/comprehension/placement_audit_3d.json`.

### X2.e net

All three measurements green/met. **Phase 4 (contingent extraction)
fires nothing**: no red door, no 3b red naming an owed layer, no 3d
flag. The remaining open item of Phase 3 is **3c** (the 50-question
open-ended census that can only *grow* the dimension map).

## What remains to full comprehension (the updated plan)

All five build phases above are shipped and green; the *goal* (the corpus
*understands* a character — what each line means, whether it is an event, where
it sits on the timeline) is not yet met. Reachability (D5) is **not** met:
48,572/48,572 is **tier 0** (every line in a chunk — an indexing tautology);
the retrieval tier was sampled 2026-09-03 over 545 probes (1.1% of lines, now
stale): verbatim 387/400 (96.8%), scoped 110/120 (91.7%), terms 24/25 (96%). A
fresh verbatim re-run landed 2026-09-05 (GPU `:8000`) = **97.2%** (478/492 new rows; the append-only jsonl holds ~400 distinct probes ≈ 0.8% of the 48,572 lines)
— **unchanged** from the 2026-09-03 baseline (96.8%) within sampling noise; the index is healthy. **D5 is still not met:** an exhaustive tier-1 has never run (92 of the 492 rows re-probe across the resume boundary — done-dedupe keyed on bare sentence text, a known defect; a naive all-rows recompute over the 892-row file gives 97.0%).
Comprehension (D6) is also not met (154 unplaced events, 107 cross-page
disagreements, narrow `abilities`, era-less social-only `relations`, 0-row
`semantics`). The prioritised remaining builds (R1 per-line meaning index →
R2 abilities coverage → R3 relations era+eventive → R4 place the 154 →
R5 typed edges), with done-gates and the standing council/GPU/gate/commit
requirements, are `COMPREHENSION_REMAINDER.md` in this directory.

## Commands

```
python -m scriptengine.cli comprehension-gate --series jjk
python -m scriptengine.cli comprehension-gate --series jjk --only-problems
python -m scriptengine.cli comprehension-gate --series jjk --limit 10
python -m scriptengine.cli continuity --series jjk --triage
python -m scriptengine.cli continuity --series jjk --subject "Yuji Itadori" --upto 7 --limit 6
python -m scriptengine.cli continuity --series jjk --no-gold --triage
```
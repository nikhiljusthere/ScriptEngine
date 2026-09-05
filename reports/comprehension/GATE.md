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

## Next (step 3b)

The gate is proven on the 108-page placement set. Step 3b widens extraction to the
full corpus (node degree ≥ 2 under a narrative-family heading, ~19,684 chunks)
using this same gate — the pass that reaches character `Synopsis`/`History` and
chapter `Plot Details`, where most of a character's own history actually lives.

## Commands

```
python -m scriptengine.cli comprehension-gate --series jjk
python -m scriptengine.cli comprehension-gate --series jjk --only-problems
python -m scriptengine.cli comprehension-gate --series jjk --limit 10
```
# COUNCIL — is the LAST BUCKET correctly scoped?

Date 2026-09-05. Standing rule: before touching the last bucket, one council pass on
whether it is correctly scoped. The bucket as framed: **D5 → §9a serial-closure →
continuity-check → cross-corpus**.

Method: 5 advisors (contrarian / first-principles / expansionist / outsider /
executor) → anonymized A–E → 5 peer reviews (skeptic / pragmatist / formalist /
domain-expert / fresh-eyes) → every load-bearing claim re-verified against code +
DB before recording (ledger at bottom).

## Verdict

**The bucket is mis-scoped as written.** It presents a clean 4-step sequence, but
the four items are of wildly different magnitude and layer (a 2-line chunking fix,
a *process* loop, a new validator, and a 7-corpus port) — and the sequence **omits
the one load-bearing dependency** (the D6-completeness / placement-signal fix) on
which the third item (continuity-check) actually rests. Re-scoped:

| # | Unit | Layer | Done-gate | Note |
|---|------|-------|-----------|------|
| 1 | **D5-close** | chunking/retrieval | fresh sweep → 0-line `index_misses.jsonl`; span-recall 48,572/48,572; pytest 1,166 + eval 24/24 green | finite (2 Ch.239 References lines); ship first; re-run sweep re-confirms the denominator (Q3) |
| 2 | **placement-signal fix** (D6-completeness) | events/gate — **CODE, not data** | raw re-derivation: NULL-arc rows fall 2,034 → a documented residual; 2,748 intact | code change to `timeaxis.placement_time_axis` (section-aware), NOT a data-UPDATE at `gate.py:45`; recovers the 995 arc-named-heading rows (+ a smaller citation signal); NOT a §9a pass; own sign-off |
| 3 | **continuity-check** (D6 consumer) | validation | a named gold case set + a coverage line (placed/placeable) + a residual disposition | can START on the 714 placed rows; DONE only after #2; **not a deliverable until a consumer is named** |
| — | **cross-corpus** | 7 new campaigns | (per-wiki; out of this bucket) | its own council + per-wiki sub-campaigns; the "only jjk has a prose.db" blocker is a red herring |

Order: **1 ∥ 2 (independent layers) → 3; cross-corpus is a separate bucket.**

## What the council corrected (verified against code + DB)

1. **The fix is a code change, not a data-UPDATE.** `backfill_event_arc_index`
   (timeaxis.py:210) re-derives `arc_index` from the placement axis and runs
   `UPDATE … WHERE arc_key=?` (line 238) **on every gate call** (invoked at the top
   of `arc_placement_violations` and `cross_page_agreement`). A one-shot data-UPDATE
   is clobbered on the next gate run; only making `placement_time_axis` (line 172,
   today "the page-level signal, not the section's") **section-aware** sticks.
2. **A routine `index` does NOT undo the fix.** `store.reset()` (facts.py:160) drops
   the parsed tables but deliberately keeps `events` (a placed event is local
   inference an index must not throw away), and `arc_index` is recomputed from the
   axis on the next gate run. The **only** real integrity risk is
   `events.section_id → sections.id`: a *crawl* that renumbers sections dangles the
   FK (the queued id-dangling hazard) — a crawl risk, not an index-undo.
3. **The 995 is a validated placement signal, not topic-bucketing.** All 2,034
   NULL-arc/temporal=0 rows carry a `section_id`. **995** sit under the nine on-axis
   arc-named section headings (233 Culling Game, 229 Shibuya, 178 Shinjuku, 95
   Gojo's Past, 75 Fearsome Womb, 69 Kyoto, 48 Cursed Child, 37 Death Painting, 31
   Mahito); **1,039** under generic headings (Plot Details 708, Summary 215, Overview
   98, History 18). A 12-row sample of the arc-named set shows the events match the
   heading's arc (e.g. [Shibuya Incident Arc] "Sukuna killed Jogo"; [Culling Game
   Arc] "Naoya Zenin fought Choso") — placement, confirmed.
4. **The citation signal is weaker than the ~209 estimate.** A sample of 8
   generic-section rows shows only 1/8 carries a `Chapter`/`Episode` citation in
   section text — so it recovers a smaller, grammar-dependent subset of the 1,039 (and
   per the standing rule must never be guessed). The 995 is the primary win; the
   citation signal is secondary.
5. **874 and ~830 are orthogonal cuts; do not range them.** 830 ≈ the
   placeable-by-signal residual (2,034 − 995 − ~209); 874 = the atemporal-at-extraction
   residual (2,034 − 1,160 demoted). They partition the same 2,034 two different ways;
   the verdict quotes only the by-signal arithmetic and quarantines 874.
6. **The cross-corpus blocker is a red herring.** `series/jjk/prose.db` is **0 bytes,
   0 tables, no reader** (a "corpse" per plan:300); the other seven have none. So
   "jjk has a prose.db, the seven don't" overstates jjk's lead: **no corpus has a
   working prose store.** The real cross-corpus work is building the T3 prose tier
   (absent everywhere) + per-wiki citation grammar/taxonomy/gold — not porting a store.

## What the council left open (fresh-eyes)

- **Is continuity-check even wanted?** No advisor named the consumer of a validator
  that "rejects a script line three arcs early." It stays scaffold-only (no done-gate)
  until a consumer + firing moment is named; the "payoff demo" reading may be its home.
- **Is 2,034-NULL a defect or the honest answer?** The 995 sample says those ARE
  placeable. The ~830 residual may be genuinely arcless — in which case NULL is the
  *correct* output and forcing a placement manufactures misplacements. "Complete arc
  index" must mean "every row with a *verifiable* arc claim placed," not "every row
  the fix places, placed."
- **The paper-exercise risk.** Closing D5's two lines (a Bobobo-bo Bo-bobo trivia
  sentence) changes no script. Green artifacts ≠ product value. The bucket's exit
  criterion should name the first write-layer artifact it feeds (a script, or a
  script-quality gate) — otherwise "closing" is a report, not a delivery.
- **D5's denominator.** The fresh sweep (Q3) must run *before* the verdict is treated
  as final: confirm 3b's 108→524 did not move the 48,572 line denominator.

## Minimal runnable path (pragmatist)

1. **D5-close** — the 2-line References chunker fix (one class, right altitude).
   Blast radius = 2 lines; sign-off is cheap but required (a chunker-scope change is
   engine code outside the 3b additive grant). Done-gate = 0-line miss file + green
   gates. Bonus: re-confirms the denominator (Q3).
2. **placement fix** — section-aware `placement_time_axis`; sign-off; done-gate = raw
   re-derivation (995 placed, residual documented) + 2,748 intact.
3. **continuity-check scaffold** — on the 714; gate done on #2 + a named gold case set.
   Drop the precision/recall gate and NULL-semantics contract for now.
4. **Defer cross-corpus** — its own council; the JJK foundation must finish first; a
   cross-corpus extraction is a GPU-week and Qwen owns the card.

## Verified-claims ledger (checked against code/DB before recording)

- backfill re-derives on every gate run → a data-UPDATE is futile — **VERIFIED**
  (timeaxis.py:238; call sites gate.py:45,97).
- axis is page-level today; the section signal is available via
  `events.section_id → sections.title` — **VERIFIED** (timeaxis.py:172-207; facts schema).
- a routine `index` preserves `events` — **VERIFIED** (facts.py:160 `reset()` keeps events).
- 2,034 NULL-arc/temporal=0; all carry a section_id; 995 arc-named / 1,039 generic —
  **VERIFIED** (query).
- the 995 are placement, not topic (events match the heading's arc) — **VERIFIED**
  (12-row sample).
- the citation signal is sparser than ~209 — **VERIFIED** (8-row sample: 1/8).
- `jjk/prose.db` = 0 bytes / 0 tables; the other seven have none — **VERIFIED** (ls + sqlite).
- 874 and 830 are orthogonal cuts — **VERIFIED** (two different partitions of 2,034).

## One next step

**Close D5.** It is the only unit that is finite, independent, and shippable now, and
its re-run sweep is the precondition (Q3: did 3b move the 48,572 denominator) that the
fresh-eyes demanded. It needs a quick sign-off (bounded: two lines, one class), not a
full escalation.
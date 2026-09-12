# The extraction-gated floor, re-measured: the instrument is broken

> ## ⚠ CORRECTED 2026-09-12 — read this first
>
> A council (3 fresh-context advisors, record
> `reports/csm/receipts/council_floor_remeasure/chairman.md`) **confirmed this
> document's defect finding and rejected its sizing.** Three claims below are
> wrong and are struck:
>
> 1. **"17 of 21 are ROUTING, 2 are CONTENT" — WRONG.** That split came from a
>    best-of-4 oracle in which `census_v2_triage.py:59` hand-feeds the gold
>    `subject`. No real caller has that. Measured through the actual auto door:
>    **8/21 green, ~13 still open** (advisor A, receipt
>    `adv_A_auto_door_21rows.json`). The triage never tried **roster**, which
>    `route()` picks for **13 of the 21** rows. The arc-narrative class this
>    doc calls "8/8 routing" is **0/8 green** under true auto.
> 2. **"CONTENT 0" on the v2 census — OVERSTATED.** That bucket required *zero*
>    hits across all attempts, so PARTIAL rows scoring 1/3 are content misses
>    under the census's own ≥2-of-3 bar.
> 3. **Recommendation 1 ("run it at `mode='auto'`") — UNCALLABLE.**
>    `build_context` accepts only `{qa, narrative, roster, relations}`
>    (`api/context.py:60`) and raises on `"auto"` (`:148`); routing lives only
>    in `api/main.py:207-249`. The fix is to share that code, not to pass a flag.
>
> Also struck: the inference "~2 gaps, therefore no extraction". **A22**
> (`plan/CSM_2PHASE_PLAN.md` §Phase 2(3)) had already pre-registered that the
> null branch *voids P2.5 rather than passing it*, and de-contingents P2.3 into
> **P2.3b** so the comprehension layer fires even at zero reds.
>
> **What survives:** the instrument defect (§"How the floor was measured"), the
> conclusion that the 21-row floor is untrustworthy, and the halt on
> P2.3-as-scoped. **P2.3 is not de-scoped.** The corrected plan is the
> chairman's §8 sequence.

**Status: BLOCKING finding for Phase 2. Raised 2026-09-12 by the directing
session while executing P2.1 step-0, before any GPU-day was spent.**

Phase 1 halted at a 22-row "extraction-gated floor" (21 `csm-dim-*` census reds
+ `csm-char-04`). P2.3 is scoped to close those rows with an extraction
campaign measured in GPU-days. **The floor does not survive re-measurement:
17 of 21 are routing/anchoring defects, 2 are partial, and only 2 are genuine
content gaps.**

## How the floor was measured (the defect)

`tools/census_dimensions.py:100` calls:

```python
build_context(paths, item["q"], mode="qa", subject=... if anchored else None)
```

The door is **hardcoded to `qa`**, unanchored. The module's own docstring
(lines 3–7) says the opposite — *"a natural writer question goes through
auto-routing, which is the stricter honest test."* The code does not
auto-route. So every census verdict, on both the v1 character bank and the v2
widened bank, measures **one door**, not the engine as `/context` actually
serves it (`mode` accepts `auto`, and `auto` is what routes).

A red therefore conflates two very different things: *nothing in the corpus
answers this* versus *the qa door alone does not answer this*.

## Re-measurement

Each red was retried three ways (`tools/census_v2_triage.py`) and classified by
its best result: `qa+anchor` → `narrative` → `narrative+anchor`.

### The 21-row floor (v1 character census)

| classification | rows |
|---|---:|
| **ROUTING** (recovers on another door/anchor) | **17** |
| PARTIAL (some expect terms recovered) | 2 |
| **CONTENT** (nothing serves it anywhere) | **2** |

Recovery route: `qa+anchor` 14 · `narrative` 5 · none 2.

Per class — `arc-narrative` **8/8 routing**, `state-over-time` **5/5 routing**,
`appearance` 1/1 routing, `abilities` 3 routing / 2 partial / 1 content,
`causality` 1 content.

**The only two genuine content gaps:**
- `csm-dim-abl-01` — "Every ability of Yoru" (abilities)
- `csm-dim-caus-03` — "Why can Asa not bring herself to kill Denji?" (causality)

### The widened v2 census (non-character page types)

Graded 2026-09-12 on CUDA: **8/50 green (16%)** — chapter_box 1/10, episode
1/10, volume_box 1/10, story_arcs_box 0/10, organization 5/10. Triage of all
42 reds: **ROUTING 35 · PARTIAL 7 · CONTENT 0.**

Worked example — `csm-dim-chap-01` "What happens in Chapter 1?": **0/3 on the
qa door, 3/3 on the narrative door**, no anchor needed. The chapter summaries
are in the corpus and retrievable; the qa door simply is not the door for a
"what happens in X" question.

## What this means for Phase 2

1. **P2.3's premise is largely void.** An extraction campaign sized to close 21
   floor rows is chasing ~2. The remaining 19 are an engine-side routing fix —
   the same shape as R-1 and R-5, bounded and cheap — not GPU-days.
2. **Q3's re-gate needs re-reading.** Council #29 ruled the P2.3 null branch
   must re-gate on the *widened* census. The widened census is 42 reds, which
   reads as "extraction firmly in scope" — but 0 of those 42 are content gaps.
   Gating on a raw census score, without the door triage, would authorise
   extraction on an artifact.
3. **The census instrument needs fixing before it gates anything.** Either run
   it at `mode="auto"` (what `/context` does), or make the door part of the
   verdict so a red states *which* door failed. Until then "dimensions green"
   and "dimensions red" are both claims about the qa door only.

## What this does NOT overturn

- The **two** content gaps are real and still owed.
- `csm-char-04` (the 22nd floor row) was not in the census and is untouched
  here; its close lever remains the R-7 re-sweep.
- The **P2.1 panel sweep** is a different instrument (tier-1 span containment
  via `span-recall`), not the census — this finding does not by itself resolve
  its go/no-go, which still needs the sanity-100 measurement.
- Phase 1's engine work (R-1…R-7) stands; the four standing gates are
  unaffected.

## Recommendation

**Do not start P2.3 extraction on the current floor.** Sequence instead:
1. Fix the census instrument (auto-routing or door-aware verdicts) and re-run
   both banks — cheap, model-free-ish, ~30 s per bank on CUDA.
2. Scope a routing fix-class for the ~19 routing rows (R-8 shape: natural
   "what happens in X" / arc / state-over-time phrasings reaching the right
   door unanchored).
3. Re-derive the floor from the corrected instrument, then decide P2.3 against
   a floor that means what it says.

Raw evidence: `reports/csm/census_v1_floor_triage.jsonl` (21 rows),
`reports/csm/census_dimensions_csm_v2_triage.jsonl` (42 rows),
`reports/csm/census_dimensions_csm_v2_results.jsonl` (50 graded),
logs `/tmp/census_v2_grade.log`, `/tmp/census_v1_triage.log`.

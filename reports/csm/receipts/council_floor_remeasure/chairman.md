# Chairman — council on the extraction-floor re-measurement (2026-09-12)

Members: A (measurement validity), B (scope consequence), C (instrument
design). Three fresh-context advisors, run in parallel — the
one-member-at-a-time rule is a Qwen KV-pool constraint (102,400 shared pool,
50–86 k member contexts); these members ran cloud-side with independent
contexts and Qwen stopped, so the eviction failure mode does not apply.

**Verdict: the instrument defect is CONFIRMED. The sizing that was drawn from
it is REJECTED. Halting P2.3-as-scoped is upheld; de-scoping P2.3 is refused.**

## 1. What all three confirm (the defect is real)

`tools/census_dimensions.py:100` passes `mode="qa"`, while the module
docstring (`:5-6`) claims questions "go through auto-routing". They cannot:
`build_context` accepts only `{qa, narrative, roster, relations}`
(`api/context.py:60`) and raises on anything else (`:148`). Routing exists
only in the endpoint body (`api/main.py:207-249`). So every census verdict
ever recorded — v1 and v2, CSM and the JJK legacy bank — measures **one
forced door**, not the engine as `/context` serves it. A red has been
conflating "no content anywhere" with "the qa door missed".

A adds that provenance is clean and there is no threshold drift: `judge()` is
reused byte-identically, the 21 triage ids are exactly the frozen file's
MECH_REDs, and the recovered hits are long verbatim clauses, not keyword
scraping.

## 2. What all three reject (my sizing was an oracle ceiling)

The claim doc's "17 of 21 ROUTING, 2 CONTENT" does not survive. Independently:

- **A** ran the corrected auto-door instrument over the 21 rows: **8/21 green,
  not 17** (receipt `adv_A_auto_door_21rows.json`, CUDA, 18 s).
- **C** ran `route()` over the same rows: auto picks **roster 13 / qa 8 /
  narrative 0**, because `router.py:627` (`wants_chronology`) claims every
  *"…in order?"* phrasing for roster, and roster returns real members so the
  `main.py:228` fallback never fires. The arc-narrative class the doc reported
  as "8/8 routing" is **0/8 green** under true auto.
- **B** identifies the mechanism: 14 of the 17 recoveries came via
  `qa+anchor`, and `census_v2_triage.py:59` hand-feeds `item["subject"]` from
  the bank. That is oracle information the writer path does not have — the
  real auto path must *infer* the subject, and it infers a different one on 4
  rows (`arcn-02`, `arcn-04`, `state-03`, `caus-03`).

The triage also never tried **roster** — the door auto actually picks for 13
of 21. "CONTENT 0" further overstates: the CONTENT bucket required *zero*
hits across attempts, so PARTIAL rows scoring 1/3 are content misses under
the census's own ≥2-of-3 bar.

**Corrected reading: roughly 8/21 green under the auto door, ~13 rows still
open (2 with no content found by any route, ~11 unproven).** Not 2. The true
floor sits between 2 and ~16 and is not yet measured.

## 3. The error the claim doc made that the plan had already pre-registered

B's finding, and the most consequential: **A22** (`plan/CSM_2PHASE_PLAN.md`
§Phase 2(3)) already ruled that the null branch — all reds closed ⇒ de-scope
P2.3 — **voids P2.5; it does not pass it**, because the done-set would then
close on triage-log lines with no comprehension layer at all. The default
path de-contingents P2.3 into **P2.3b**: extract over the red class ∪ a
frozen green-class sample, so the comprehension step fires *even at zero
reds*. A14 records P2.3 as the plan's only comprehension step.

"~2 gaps, therefore no extraction" is exactly the inference A22 forbids. The
claim doc's Recommendation is struck on this point.

## 4. The real gap, larger than the one reported

B: `span_recall._ask` also forces `body["mode"]=door` (`span_recall.py:207-216`).
So **both** campaign instruments force a door. **Nothing in the campaign has
ever measured the auto door that `/context` actually serves to a writer.**
That is the defect worth fixing, and it is wider than the floor.

## 5. P2.1 is unaffected and should not wait

P2.1's panel sweep is a different instrument (tier-1 span containment, three
doors, pre-declared per-door floors A17). Its go/no-go remains a pure cost
question. B supplies the break-even: **3.35 s/probe** (17,181 × 3 doors
against the 2-GPU-day threshold). Run step-0's sanity-100 in the same `:8000`
window; do not delay it behind the census repair.

## 6. Error asymmetry (why the halt, not the de-scope)

Spending GPU-days extracting content that is already retrievable corrupts the
pre/post extraction-pass delta — the precise failure A18 exists to prevent.
De-scoping wrongly is recoverable **provided P2.5 does not ship on it**. The
one-way door is the done-declaration, not the compute. Hence: halt the spend,
refuse the de-scope, measure again.

## 7. Rulings

1. **P2.3 as currently scoped does not start.** Its 21-row premise is not
   trustworthy.
2. **P2.3 is not de-scoped either.** A22/A14 stand: the comprehension layer is
   owed regardless of red count; the reshaped form is P2.3b.
3. **Repair the instrument before it gates anything.** Per C: lift
   `main.py:207-249` into a shared `serve_context(...) -> (bundle, trace)` in
   `api/context.py`, make `/context` a thin caller, and have the census call
   the same function — so the census cannot drift from the served path. Add
   `--door {qa,auto,all}`, **default `qa`** so prior runs reproduce
   byte-identically. Records carry the per-door array plus `routed_mode`,
   `why`, `routed_subject`, and classify `SERVED` / `ROUTER_DEFECT` /
   `ANCHOR_ONLY` / `CONTENT`. **Only `CONTENT` may size extraction.**
4. **No oracle anchoring in the primary verdict.** Subject inference is itself
   under test (it matches gold on only 16/21).
5. **R-8 is booked** as a Phase-2 engine item: `ROUTER_DEFECT` rows size it,
   starting at `router.py:627` (`wants_chronology` → roster for "in order"
   phrasings).
6. **Instrument versioning is now mandatory.** Stamp `instrument_version`,
   write `..._results_v<N>.jsonl`, never compare across versions. Precedent
   for the rule: the v1 results file was already overwritten in place once
   (`GATE.md:38-39`; prior bytes only at `af382ee`).
7. **Frozen, must not change:** `_census_paths()` JJK isolation
   (`census_dimensions.py:48-57`), the JJK bank/results bytes, and `judge()`'s
   ≥2-of-3 rule (`:72-81`) — changing the rule invalidates every bank at once.
8. **Phase 1 is not re-opened and `PHASE_A_COMPLETE` is not retracted.** File
   an erratum recording that the halt meter's 33-fixable denominator rests on
   a single-door instrument, and book R-8 as Phase-2 work.
9. **The de-scope decision does not belong to the session that authored the
   finding.** It goes to the owner, and the reshaped P2.3/P2.3b goes to the
   Phase-2 council.

## 8. Sequence

1. Repair the census per ruling 3 (shared `serve_context`, `--door`, versioned
   results).
2. Re-run the 21 + 42 reds through the auto door, no oracle subject — ~63
   probes, minutes, ~10³× cheaper than one extraction GPU-day. Batch into
   P2.1 step-0's existing `:8000` window.
3. Run P2.1 step-0 sanity-100 in that same window (independent question).
4. Re-derive the floor from the corrected instrument; scope R-8 from the
   `ROUTER_DEFECT` rows.
5. Take the reshaped P2.3/P2.3b + the re-derived floor to the owner and the
   Phase-2 council.

## 9. Correction owed on disk

`reports/csm/EXTRACTION_FLOOR_REMEASURED.md` overstates in three specific
places — the "17 ROUTING / 2 CONTENT" split, "CONTENT 0" on v2, and
Recommendation 1 (`mode="auto"`, which raises). It must carry a correction
header rather than stand as written; an inaccurate document on disk is the
same hazard as the "items 3–8 unstarted" power-checkpoint error.

# COUNCIL — the B5 premise: is the arc-named majority the *right* answer? (Step-1 record, round 2)

Date 2026-09-05. Round 2. This council reviews the **Step-1 record corrections**
(A1–A5, D6-tautology, degenerate-time_rank — committed `1581bef`) and the
**B5-first** reprioritisation they imply. Round 1
(`COUNCIL_placement-signal.md`) *designed* the placement fix; this one asks the
question round 1 did not: **we now have two placement signals (arc-named "page"
vs section "backfill") that disagree on 98/107 of the 107 cross-page
disagreements — but nothing has measured which one is right.**

Method: 5 advisors (contrarian / first-principles / expansionist / outsider /
executor) → anonymised A–E → 5 independent peer reviews → every load-bearing
claim re-verified read-only against `series/jjk/facts.db` + the `ingest` code
before recording (ledger at bottom).

## What the council was handed

The record now states, honestly: `temporal` is tautological (all 2,748 rows are
eventive, so `temporal ≡ arc_index IS NOT NULL` — it certifies flag↔placement
*consistency*, never chronological *correctness*). Therefore D6 (the two
flag-invariants) is a ritual gate, and **cross-page agreement is the only
signal left that can flag a wrong placement** — hence B5 (gate the 995
section-backfill rows against the arc-named majority) is promoted to *first*,
above R1–R5.

The premise under test: **the arc-named (page-signal) majority is a *more
correct* placement than the section backfill, so B5 should overwrite the
losing section rows with it.**

## Where the council agrees

- **The record's honesty is sound.** Stating the D6 tautology and the 27.4%
  rate (not a bare count) is correct. `events` has **no signal column** — which
  of `arc_page`/`arc_fact`/`chapters`/`section` placed each row is recomputed on
  the fly and never stored — so "Step 1" is a *copy* of the placement, not an
  independent check. (verified: schema has no `signal` column.)
- **The beat-order guard (A1) is low-discriminating.** It compares section order
  against a `time_rank` derived from the *same* placement, so it can only fire on
  local inconsistency; a placer systematically off by one arc stays a no-op
  forever. "1 page moved" really means "inert on 411/412 pages," not "no
  degradation." The dangerous cross-arc failure is never touched.
- **The arc-named majority is cross-page but *not independent*.** It is real
  evidence (the character/synopsis section rows are filed against *other* pages —
  episode/battle/arc pages, verified against the store), but every observation
  shares one epistemic source: **the wiki's editors.** A majority proves
  *self-consistency*, not correctness. Mixed groups disagree at 35.6% — *higher*
  than pure arc-named's 10.5% — so the "trusted" signal has its own error rate,
  and the two signals' errors are correlated (same page structure). A naive
  majority vote amplifies a systematic misplacement rather than correcting it.
- **The 107 groups are a corpus, not a defect to wipe.** 91 are *two-sided*
  (both rows carry distinct non-null `arc_index`) — the rarest, most valuable
  adjudication targets. Keep them as a gold/correction set, don't suppress them.

## Where the council clashes

- **Should B5 overwrite section rows with the arc-named majority?**
  - *Executor:* yes — a standing rule in `backfill_event_arc_index`, 90–120 min,
    no model. A hand UPDATE would be reverted by the next backfill, so make
    majority-adjudication durable.
  - *First-principles + Contrarian:* the majority is a **consistency vote, not an
    answer.** The gate must be **one-way: demote / flag the losing section row,
    never promote the majority arc onto a row the wiki never filed.** Promoting
    fabricates a placement the wiki's editors never made — worse than a NULL.
  - *Resolution the reviews converge on:* B5 **records** the disagreement
    (an `event_disagreements` table) and **demotes** the losing row's
    confidence; it does **not** silently overwrite. The one-way direction is
    the load-bearing constraint.
- **Propagate-then-gate (Expansionist) vs gate-only?** The 154 unplaced rows:
  105 (68%) share a `(verb, {subject, object})` triple with a row placed
  elsewhere, so a sibling-propagation pass would recover most of them *for free*.
  The Expansionist wants to run that *before* the gate. The Contrarian objects:
  if the section rows are simply wrong, propagation **multiplies** the same
  correlated error across ~105 more rows. Unresolved — it hinges on the
  unmeasured question of which signal is right.

## Blind spots the council caught (only via peer review)

- **Nobody verified which side is actually right.** All five advisors reason from
  structure; none proposed *measuring* the arc-named majority's real precision.
  Until a sample of the 107 is checked against an independent oracle, "majority"
  is an unproven proxy and the promote-vs-demote choice rests on a guess.
- **The `(verb, subject, object)` grouping key itself was never validated.**
  Noisy verb/participant extraction would make 27.4%, the majority, *and* the
  propagation all artifacts.
- **`arc_index` / "arc" is never grounded, and the writer-facing output is
  unspecified.** The council debated internal consistency with no deciding
  criterion tied to what a writer actually receives for the 154 unplaced / 107
  disputed rows (a ranked candidate + confidence flag, or one overwritten value?).
- **The Shibuya Incident move** (the guard's only non-no-op output) is an
  unexploited free correctness probe.
- **No rollback path** for corrections already written to the live store.

## The recommendation

**Do not build B5 as a majority-overwrite.** The single load-bearing fact the
whole B5 decision hangs on is *unverified*: that the arc-named majority is more
correct than the section backfill. Before any gating or propagation:

1. **Ground `arc_index`** — what an "arc" is and its chapter range, so a
   placement can be checked.
2. **Validate the `(verb, s, o)` key** on a sample of the 107.
3. **Spot-check which side is right**, starting with the **5 pure arc-named
   residual** disagreements (cleanest — both rows arc-named, so no backfill in
   play), then ~15 mixed. Oracle: does the event's chapter fall inside its arc's
   chapter range? / read the raw wiki page. If the majority *wins*, build B5 as
   **one-way demotion + an `event_disagreements` table** (record, never promote).
   If it *loses*, the section signal is the better source and the gate inverts.

Preserve the 107 (91 two-sided) as a gold/correction corpus; carry the
105/154 sibling-propagation as a *recoverable-residue* lead for R4, gated behind
the same spot-check (the Contrarian's correlated-error warning stands until the
spot-check says the section rows are trustworthy).

## One thing to do first

Run the **spot-check**: ground `arc_index`, validate the `(verb, s, o)` key, and
verify the 5 pure arc-named residual disagreements (both rows arc-named) plus ~15
mixed against an independent oracle (event's chapter ∈ its arc's chapter range?
raw-wiki read). It decides whether B5's premise is even true and whether the gate
demotes or inverts. No model, no GPU; it is the fact the whole B5 plan depends on.

## Verified-claims ledger (checked against code/DB before recording)

- 2,748 events; `temporal=1` = 2,594; `arc_index IS NULL` = 154; 8 verbs
  (`arrived, awakened, betrayed, departed, fought, killed, saved, sealed`), all
  eventive — **VERIFIED** (query).
- `events` schema has **no signal/provenance column** — the placement signal is
  recomputed on the fly (`placement_time_axis` / `section_arc_index`), never
  stored — **VERIFIED** (`PRAGMA table_info(events)`).
- 390 multi-page groups, 107 disagreeing, rate 27.4% — **VERIFIED** (recomputed
  against the store).
- The 107 split: **91 two-sided** (all rows placed, ≥2 distinct arcs) /
  **16 involve ≥1 unplaced row** — **VERIFIED** (exact).
- 154 unplaced: **105 (68%) share a `(verb, {subject, object})` triple with a row
  placed elsewhere** (sibling-propagation lead) — **VERIFIED** (exact).
- Interaction-verb (`fought/saved/killed/awakened`) subset of the 107: **5 pure
  arc-named residual** — **VERIFIED** (exact; the group total is 46, one under the
  Executor's 47 — immaterial to the "5 pure" claim).
- Disagreement rate by provenance: page 9/86 (10.5%), section 5/36 (13.9%),
  mixed 93/261 (35.6%), unplaced 0/7; 98/107 (92%) touch a section row —
  **VERIFIED** (A5, prior run).

## Open (recorded, not acted on)

- Whether the 11% → 27.4% rise is a genuine regression or a **visibility
  artifact** (pre-fix the 995 section rows had `arc_index NULL` and were excluded
  from the arc set; post-backfill they participate) — or **wiki drift** between
  the two crawls. The spot-check should record which.
- `time_rank` in-page order is the wiki's *authoring* order, not chronology — the
  honest guarantee to a writer is "wiki-filed order with declared provenance," not
  "chronology."
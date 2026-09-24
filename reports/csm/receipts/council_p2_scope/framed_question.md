# Framed question — council #38 (P2-scope checkpoint + D7a exit)

CSM 100% close campaign — decision: lock the P2 extraction-leg design
(`reports/csm/P2_SCOPE_EXTRACTION.md`) + the two pre-registrations
(`reports/csm/receipts/d6_probe/WIDTHCLASS_PREDICT.md`,
`reports/csm/D7A_NUMERIC_COLLISION.md`), so the GPU window (Qwen down,
whole card — owner-triggered) can run, in order: (a) R-8 four-gate window
+ green30, (b) P2.1 sweep (stamp-wipe at current HEAD; the 2026-09-17
receipt @`4b60043` is stale), (c) 27B extraction pass on the JEV keep-list
(230 pages / 406 sections dry-run-verified; ~158 pages net-new vs D6's 72),
(d) the width-class top_k=30 measurement instrument (pool-140/358 +
counter-guards 149/252 + full-486 counter sweep), (e) p23 re-grade at
product + campaign config + all guards.

## Core claims under review

1. **All 16 FLOOR16 rows are retrieval-config gaps (width / ranking /
   door), not extraction-content gaps.** Evidence: every gold section is
   kept (JEV keep-list 1,358/3,917 sections, JJK sensitivity gate
   837/838 = 99.9%) AND chunked (census-authoring check (c)); the 23/23
   red-triage is gold-supported (zero bank/crawl defects); and D6 measured
   it: 333 extracted events flipped 0 of 486, root-caused — "the events
   table is consumed only by the narrative door; the expect sentences ARE
   in chunks but lose to the character card → retrieval-ranking gap."
2. **The extraction leg's role is therefore event-layer completion for the
   narrative/auto doors + Q4 coverage compounding — explicitly NOT the
   flip lever for the 16 qa-door floor rows.**
3. **The 16 rows close via:** TIERED default-flip (owner decision; Leg A
   already flipped arcn-02/10, state-08, org-03 at 473), the class-scoped
   top_k=30 instrument (pool-140/358), roster-door routing
   (abl-01/02/09; the roster arm already serves 4/4 in the bar audit), and
   the residual arcn-03/04/06/08 + state-02/03/09 + caus-03 retested
   after those levers, else 5.4 re-adjudication (named limit, never a
   catch-all).
4. **Budget: ≈ 7–9 h GPU in one window** (gates 45–60 min + sweep 2.7 h +
   extraction 2.5–3.5 h + instrument 30–45 min + re-grade 45 min), under
   the 2-GPU-day budget; abort/shrink pre-registered (first-10-pages rate
   probe > 2× D6 rate ⇒ shrink to the 16-floor gold-section union + 69
   event sections; OOM/per-page crash ⇒ workers 1).
5. **Q3 null branch (extraction descope) does NOT fire** (469/486
   product / 473/486 campaign ≠ green); it re-gates after the legs.

## Standing invariants that bind the council (plan/CSM_100_CLOSE.md)

- A misdiagnosed retrieval failure must never buy GPU-days.
- Standing guards on every regrade: 0 green→red counter-flips; green30
  30/30; OOS200 drop < 3 vs D6_OOS_PRE (locked floor 166); blind 19/19;
  4 gates green; JJK diff = gate artifacts only.
- D59: no ex-post re-tuning of a RED leg (Leg B ABILWIDTH is RED +
  killed; the width class gets a NEW pre-registered instrument only).
- No model grading: p23/blind/OOS/green30 stay mechanical; JEV tools
  never grade; councils stay llm-council.

## The questions (answer all five)

Q1. Does the per-row re-proof (claim 1) justify "extraction is not the
lever for the 16 qa-door floor rows"? Is there any row where
extraction-CONTENT is genuinely the lever (e.g. state-over-time interval
facts), and should the scope widen to cover it differently?
Q2. Is the locked scope (keep-list 230 pages / 406 sections) + budget +
abort/shrink sound? Any missing failure mode (index shape drift, events
remap loss, OOS collapse, stale sweep attribution)?
Q3. Is the width-class instrument a faithful reading of council #37's
trigger line ("class-scoped top_k=30 campaign, NOT an ABILWIDTH re-tune")?
Any bar too weak or too strong?
Q4. Is the window order (gates → sweep → extraction → instrument →
re-grade) right, or should the instrument run BEFORE extraction (so the
width decision does not ride on extraction)?
Q5. Should the TIERED default-flip (owner decision, council #37 Q3 bar)
be bundled into this window or stay a separate gated window?

## Evidence files (read-only)

- `reports/csm/P2_SCOPE_EXTRACTION.md` — the design under review
  (ledger, Q1–Q4 application, per-row table, scope, budget, guards).
- `reports/csm/receipts/d6_probe/WIDTHCLASS_PREDICT.md` — the width-class
  pre-registration (lineage: WIDTH killed, Leg B RED/D59, Q7/Q8 beam
  proof).
- `reports/csm/D7A_NUMERIC_COLLISION.md` — the numeric-collision family
  defect sheet (37 box-class reds closed by Q1-L1 + subject routing;
  pre-registered regression trigger).
- `plan/CSM_100_CLOSE.md` — the master plan (denominator annex, standing
  guards, step definitions, council checkpoints).
- `reports/csm/GATE.md` (bottom ~160 lines) — D7 re-score window (Leg A
  PASS / Leg B RED), D7-CLOSE council #37 rulings (width-class trigger
  line, TIERED flip = owner decision, kill clauses, claim-scope line).
- `~/tools/jev/HANDOFF.md` — keep-list + JEV invariants (local-only, no
  GPU, no grading).
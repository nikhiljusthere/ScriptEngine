# WIDTHCLASS leg — PRE-REGISTRATION (written BEFORE the change, 2026-09-24)

Counsel #37 (council-d7-close) left the width class (pool-140/358) as a
Phase-2 retest with a pre-registered trigger line (verbatim in
`GATE.md` D7-CLOSE): "one new pre-registered instrument — a class-scoped
top_k=30 campaign (NOT an ABILWIDTH re-tune; D59 bars Leg-B knobs). Bar:
flips ⊇ {pool-140, pool-358} AND 0 counter-flips vs {pool-149, pool-252};
blind 19/19; OOS200 floor (drop < 3 vs `D6_OOS_PRE`); `d6_flip` rc=0.
RED ⇒ kill clause: rows stay P2 floor-registered; no ex-post re-tune."
This file is that instrument, written before any run. It is a MEASUREMENT
pre-registration (campaign config, zero engine change); the engine ship
(a class-scoped top_k=30 hunk) is a separate gated decision behind this
instrument's PASS + the owner's word + the four standing gates.

## Lineage (what is barred and why)

- WIDTH ship leg (global top_k 8→30, `WIDTH_PREDICT.md`): KILLED — counter-flips.
- Leg B ABILWIDTH (possessive-trigger engine hunk, `ABILWIDTH_PREDICT.md`):
  RED in the D7 window — both targets flipped but 2 counter-flips
  {pool-149, pool-252}; kill clause: the hunk stays dead behind its
  default-OFF flag, **no ex-post re-tuning (D59)**.
- Q7/Q8 beam probes (disk, `d6_probe/`): pool-140/358 flip under beam
  top_k=30 (gold ranks 12/19 at top_k=8) — the width-class hypothesis is
  proven at beam level, unproven at the endpoint (campaign path) at the
  current HEAD, and the counter set was never measured class-scoped.

## Instrument (the class-scoped top_k=30 campaign)

- Vehicle: `tools/csm/p23_grader.py` in-process (the same endpoint function
  the `:8000` /context serves; product path, no :8000 needed; GPU free for
  the ~5.3 GB retrieval stack; Qwen down per the window order).
- Class scope (the width class = the 4 rows sharing the trigger space):
  targets {csm-abl-pool-140, csm-abl-pool-358} + counter-guards
  {csm-abl-pool-149, csm-abl-pool-252}, graded through `grade_item(...,
  top_k=30)` (endpoint defaults otherwise, subject = the row's page — the
  campaign path the D7 snapshot census used).
- Counter sweep: the full 486 bank at top_k=30 (same vehicle) so the
  counter set beyond the 4-row class is MEASURED, not assumed; the
  trigger-line bar binds on {149, 252}; beyond-class counter-flips are
  bounded at 0 (the beyond-class bound below, amend #38-5) — a violation
  does not void the class-scoped evidence but bounds the shippable unit
  to the class-scoped hunk.
- Guards (mechanical, same as every regrade): blind 19/19
  (`blind_fresh_d7.jsonl`, product config — the instrument is
  measurement-only and touches no engine state); OOS200 via `d6_flip.py`
  (drop < 3 vs `D6_OOS_PRE`; green30 zero flips; `d6_flip` rc=0).

## Bars (ALL must hold for PASS)

1. pool-140 MECH_GREEN at top_k=30 AND pool-358 MECH_GREEN at top_k=30.
2. 0 counter-flips vs {pool-149, pool-252} at top_k=30 (both stay
   MECH_GREEN; they are product-green at top_k=8).
3. blind 19/19; OOS200 drop < 3 vs `D6_OOS_PRE`; `d6_flip` rc=0.

**Beyond-class bound (amend #38-5, council #38):** PASS requires
**0 beyond-class counter-flips** (any bank row outside the 4-row class
going green→red at top_k=30). If ≥ 1 occurs: the class-scoped flip
evidence still stands (the trigger-line bars are not voided by it), but
the shippable unit is bound to the **class-scoped hunk only** (top_k=30
gated to the width-class trigger); NO broader hunk is pre-registration
cleared, and the flipped rows close by lever or the 5.4 named-limit void
set — never an ex-post global re-tune (D59). This replaces the earlier
"record and report, class scope re-opens" wording: the ship scope is
bounded ex-ante.

## Interpretation (pre-registered, so the ship decision cannot drift)

- **PASS** = evidence for the width-leg ship decision: a class-scoped
  top_k=30 engine hunk (e.g. the ABILWIDTH predicate or a class-based
  top_k, both behind a default-OFF flag) is pre-registered-cleared to go
  through the owner-word + 4-gate window (the council #37 Q2/trigger-line
  path). The ship itself is NOT this instrument.
- **RED** (either target stays red at top_k=30, or a {149,252}
  counter-flip) = **kill clause**: the rows stay P2 floor-registered; no
  ex-post re-tune of the width class (D59); the class closes only via a
  NEW pre-registered instrument + the 5.4 re-adjudication named-limit
  path (defect + owning leg + retest), or via the TIERED interaction
  (owner decision).
- The run re-proves the Q7/Q8 beam result at the endpoint at the current
  HEAD — if it fails where the beam probe passed, the gap is the
  endpoint's budget/walk, not the beam, and the re-diagnosis goes to the
  council (no ex-post knob).

## Receipt

One run, one receipt (`reports/csm/receipts/d6_probe/widthclass_run.md`):
the 4-row verdicts at top_k=30, the full-486 counter set, blind/OOS/green30
guard lines, `d6_flip` rc, and the PASS/RED verdict line against the bars
above. Wall ≈ 30–45 min (the p23_handoff 45-min watchdog covers it).
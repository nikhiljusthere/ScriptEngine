# COUNCIL RECORD — D7 close council (CSM Phase 1, §9a closure loop)

**Members:** 5 advisors (A–E) + 5 peer reviewers (R1–R5) + 1 chairman.
**Method (owner rule 2026-09-08):** strictly sequential — one subagent at a
time, each fresh-context, GPU-free, read-only. Advisors A–E deployed in
order; then R1–R5 each review all five advisor responses; then the
chairman rules on the record.

**Council #37, 2026-09-20, opencode.** Framed question + evidence pack:
`framed_question.md` (this directory).

**Letter↔session map (advisors):**
| Letter | Role | opencode task session |
|---|---|---|
| A | Executor | `ses_f44b5bd26ffeD2kPc2bpu12xTX` |
| B | Outsider | `ses_f44afba90ffe7bKwNsjIyD4w7L` |
| C | First-Principles | `ses_f44a9d3e3ffepLZodJYpllyDh3` |
| D | Contrarian | `ses_f44a23989ffeHt91GKgI1Jm54C` |
| E | Expansionist | `ses_f449caa78ffe7fOPbtuN79bMtp` |

**Letter↔session map (reviewers):** see `reviews.md`. **Chairman:** verdict in `chairman.md`.

---

## ADVISOR A — Executor

# ADVISOR A (Executor)

## Position (Q1–Q5)

**Q1 — Close now; pool rows go to the floor.** Leg A PASS 473/486, 0
counter-flips, blind 19/19; Leg B RED on 2 counter-flips {pool-149,
pool-252} → kill clause; Leg C halted (`reports/csm/receipts/d7_window/
LEGA_targets.log`, `LEGB_targets.log`). D59 forbids ex-post re-tuning of
a RED leg, and A20's own register classifies pool-140/358 as "width —
subsection recall beyond focus routing" (D6_CLOSE_A20.md:34,63-64): a new
instrument class, not a Phase-1 fix class. Halt rule met: every
remaining open row is extraction/floor (HALT_METER_P13.md:98-105). Close
at the floor; re-register pool-140/358 as width-class Phase-2 floor. A
width leg, if ordered, is a new pre-registered design (bar below) and
the close defers one wave.

**Q2 — Keep ABILWIDTH dead behind the flag; do not revert.** Flag OFF ⇒
predicate never evaluated ⇒ tree byte-identical to the commit
(context.py:638 guard; `_abilwidth_enabled` context.py:586-591, default
"0"). Revert = engine diff ⇒ 4-gate rerun + owner word, zero behavior
gain, and it burns the P6 seed and leg-C union (FLIPS C = A∪B,
check_targets.py:39).

**Q3 — TIERED default-flip: recommend YES, post-close, as a separate
owner decision** (chairman deferred it, chairman.md:141). Gated: 1 char
(context.py:583 "0"→"1") + 4 gates at the new default (JJK no-op is no
longer structural at flag-ON — the gates are the proof) + p23 473 repro
at the new default; short bounded CUDA :8000 window co-located with Qwen
(quiet-window rule), no Qwen kill.

**Q4 — Reconcile + stamp.** Close denominator = FLOOR16
(check_targets.py:41-49) restamped at the 473 era: 13 reds = 11 csm-dim
rows, each verified ⊂ the 21-row D6 extraction floor (HALT_METER_P13.md:
50-70) + pool-140/358 width-class. The D6-close-16 list (463-era,
D6_CLOSE_A20.md:35-38) is superseded by FLOOR16 (469-era). Residual
re-count: 27 open rows = 12 (a) [11 csm-dim + csm-char-04,
HALT_METER_P13.md:71] + 13 (b) + 2 width, superseding the P1.3 meter's
35 (10 of (a) green since: 3 tiered-leg flips arcn-02/10 + state-08, 7
via the committed D6 spike). EXTRACTION_FLOOR_REMEASURED's correction
strikes only the routing/content sizing (banner L3-33); the 21-row (a)
register stands.

**Q5 — Close ritual = docs-only, no GPU, no re-gates.** Reboot_rule
passes (gate-relevant diff `4a8616bd..HEAD` empty; last_green `0c8cc953`
= `20d6da4e` behavior, GATE_LEDGER.json) ⇒ "official suite" = cite the
existing green, not re-run. "VOID formal" = A20's 3 void triggers (gate
regression / flips / A-row closes-still-red, D6_CLOSE_A20.md:40-41) run
model-free against the 473 state, receipt under
`reports/csm/receipts/council_d7_close/`; then restamp
PHASE_A_COMPLETE_AT_FLOOR.md + phase_status.txt (p14 marker pattern) +
owner "commit" (docs-only commit).

## What I would pre-register

1. **VOID-formal (model-free, pre-stamp):** (i) no gate regression vs
   last_green `0c8cc953` (reboot_rule: diff empty); (ii) flag-OFF default
   tree has 0 green→red flips vs the 469-era census (the counter-flips
   {pool-149, pool-252} exist only on RED leg B); (iii) A-row register
   check = the 13-row 473-era floor list. Any fire → no close; route to
   a re-scope council.
2. **Close stamp:** GATE.md D7-CLOSE section + GATE_LEDGER `d7_close` +
   drift D65 + PHASE_A restamp + phase_status.txt; receipt
   `VOID_FORMAL.md`. All five diffs docs-only.
3. **Width-class leg (only if ordered post-close):** new single
   instrument — top_k=30 focus recall for pool-140/358 (Q7/Q8
   evidence). Bar: flips ⊇ {pool-140, pool-358}, W ≥ 473, 0
   counter-flips vs the 473-era green set (the 469 baseline at
   check_targets.py:29 is stale for that leg), blind 19/19, d6_flip
   rc=0. RED → kill clause: rows stay floor-registered; halt at floor.
4. **TIERED default-flip (Q3)** as its own gated step: owner word → 1
   char + 4 gates at the new default + p23 473 repro.

## What I would NOT do

- No ex-post re-tuning of leg B (D59); no ABILWIDTH revert (flag OFF is
  already zero-behavior; revert = 4-gate rerun + owner word, burns
  P6/leg-C).
- No re-run of the four standing gates (reboot_rule passes); no JJK
  baseline change; CSM-only files; engine-code commits only on
  all-green + owner word.
- No GPU work in this council (close is docs-only); no leg C now
  (halted at leg B RED).

## Sequence

1. **Advisor A (executor, docs-only):** run the 3 VOID-formal checks
   model-free → `receipts/council_d7_close/VOID_FORMAL.md`. Verify: file
   on disk, 3/3 PASS.
2. **Chairman (on 3/3):** stamp GATE.md + GATE_LEDGER + drift D65 +
   PHASE_A restamp + phase_status.txt. Verify: 5 diffs, all docs-only
   (no `scriptengine/` paths).
3. **Owner:** "commit". Verify: `git show --stat` shows no engine paths;
   ledger `d7_close` entry present.
4. **Post-close (only if ordered):** deploy the width-class leg
   pre-registration (item 3) and the TIERED default-flip decision
   (item 4) as separate gated steps, each with a 4-gate pass at the new
   state.
---

## ADVISOR B — Outsider

# ADVISOR B (Outsider)

## Position (Q1–Q5)

**Q1 — Phase-1 close determination.** The halt rule is not met NOW by its own terms (GATE.md:73–87): 11 of the 13 reds are register-22 extraction-floor rows, but pool-140/358 are formally registered as D7 named-limit holdouts, defect "width" (D6_CLOSE_A20 register; GATE.md:1046–1050) — non-extraction, Phase-1 rows. The width evidence says not safely closeable now: D57 killed global width (+16/−23, blind 19→10); Leg B went RED at net-zero W (469) with 2 counter-flips; D59 freezes that leg. **Rule: close now, but only via an explicit council-stamped floor re-registration of pool-140/358** (meter 35→37), handed to P2 (the re-scoped retrieval wave, D56). If the council orders a final leg instead: a NEW pre-registration (not a re-tune of Leg B), GPU-free probe-gated, killed on any predicted counter-flip, single instrument; bar = flip both AND 0 counter-flips vs {pool-149, pool-252}, W ≥ 473, blind 19/19, `d6_flip` rc=0.

**Q2 — ABILWIDTH disposition.** Keep dead. A revert is an engine-code commit → 4-gate re-run + owner word for zero behavior change (the guard reads the env flag, default "0"; the hunk never evaluates when OFF), and it destroys the `4a8616bd` never-lose checkpoint + the P6 seed recorded at #36. The kill clause's own text is the disposition (GATE.md:1021–1024): "stays behind its default-OFF flag (unset = inert); no ex-post re-tuning." Byte-identity needs no new re-run: gate-relevant diff `4a8616bd..0c8cc953` is empty; the four gates are green at `0c8cc953`.

**Q3 — TIERED default-flip.** Not now, not never — after the close, as the separate owner decision R5 reserved (GATE.md:1051–1054). The flag is a global env var, not per-wiki: the flip changes JJK's behavior, so the flip's 4-gate re-run must run at TIERED=1 and show eval jjk 31/31, span-recall 48,572 + probe ≥ 390/400, canon 236/236/79.0%, pytest 1,331 — JJK non-regression at flag-ON, not just OFF. Any gate RED → no flip (stays default-OFF; campaign grade stays flag-ON). The close file must state: "100% claim scope: campaign grade flag-ON 473/486; shipped product flag-OFF."

**Q4 — Bookkeeping integrity.** Every 463→473 closure is attributed to a named mechanism — the chain is 463 →(Q1-L1, +2: chap-01, arcn-07; D52/D57 "bank 465, flip set == stamped CONFIRM + chap-01/arcn-07")→ 465 →(deriv, +4: arcn-01, org-05/06, vol-10; D61)→ 469 →(TIERED Leg A, +4: arcn-02/10, org-03, state-08)→ 473. The "2 unattributed" are the Q1-L1 pair, which the D61/63 ledger never folded in because it tracked only the deriv leg's 4 predicted flips. Authoritative floor registration = register-22 (`census_v1_floor_triage.jsonl`, stamped at #34, governing the 35 meter); `check_targets.py` FLOOR16 is a measurement convenience (469-era 17 reds − org-03), not a registration — it silently includes the 2 pool rows and drops already-closed arcn-01/07. Stamp into the close: 13 = 11 ∈ register-22 + 2 ratified width-floor; meter 37 = 24 + 10 + 3.

**Q5 — Close-ritual spec.** Pre-register: "official suite" = a close re-grade from the committed tree: p23 486 (flag-ON per R5) + blind 19 + OOS200/green30 (`d6_flip` rc=0) + the four standing gates (flag-OFF); receipts → `reports/csm/receipts/close_window/`. "VOID formal" = the D56/57 P2-void determination on production flips, not probes: (1) the 11 open dim reds' answers still in-chunks (D53 method); (2) `d6_flip` rc=0; (3) four gates green; (4) 0 new gap IDs (A18 floor-not-moving, GATE.md:498) — failure = no VOID stamp, council reconvenes (A20 precondition fails). `PHASE_A_COMPLETE_AT_FLOOR.md` = the marker: red set 13 (11+2), meter 37, gate receipts (`0c8cc953`), the re-registration stamp, the claim-scope line, P2 handoff (22+10+3+2 open by design; P2 = retrieval wave + residual extraction per 5.4 re-adjudication), TIERED-flip owner-decision line; commit marker + GATE_LEDGER close registration + drift entry.

## The 2–3 dangerous assumptions

1. "All 13 sit inside FLOOR16 ⇒ Phase 1 is at the floor" silently re-registers pool-140/358 from D7 holdouts to floor via the instrument's list; the authoritative A20/ledger registration says the opposite. The close denominator is only honest with an explicit council stamp, never as a by-product of a convenience constant.
2. "flag-OFF = `20d6da4e` behavior" is asserted, not proven (chairman #36), and the CSM "100%" is a flag-ON campaign grade while the product ships flag-OFF. Without the claim-scope line, the close fossilizes a product-level 100% claim the gates never measured.
3. Reading 463/465/469/473 as one time series without flag-state labels is how the "2 unattributed flips" phantom arose — 463 is the flag-OFF official re-grade; 469/473 are flag-ON grades.

## What I would pre-register

- pool-140/358 floor re-registration stamp: defect width/beam; owner P2 retrieval wave; retest trigger = class-scoped top_k campaign (flip both, 0 counter-flips vs {pool-149, pool-252}, blind 19/19); meter 35→37.
- Close-file lines: claim-scope (grade flag-ON, product flag-OFF, flip = owner decision) + arithmetic 486−473 = 13 = 11+2 (11 ⊂ register-22, verified offline by set intersection).
- Official-suite run list + receipts path; the 4-point VOID checklist + the reconvene-on-failure rule; if a final leg is ordered, its probe-gate design, kill condition, and bar (W ≥ 473, 0 counter-flips, blind 19/19, rc=0).

## What I would NOT do

- No ex-post re-tuning of Leg B (D59); any final leg is a new pre-registration, not a re-tune.
- No engine-code commit without all-green + owner word; no revert in this council.
- No TIERED default-flip inside the close (post-close, owner decision, flag-ON gates).
- No close file claiming "all 13 inside the floor" without the 2-row re-registration stamp.
- No executing "official suite"/"VOID formal" before this pre-registration lands; no JJK movement; read-only (no engine edits, no GPU, no writes).

---

## ADVISOR C — First-Principles

# ADVISOR C (First-Principles)

## Position (Q1–Q5)

**Q1 — Close, but only via a council-stamped re-registration of
pool-140/358.** The halt rule (GATE.md:73-87) requires all open rows
extraction/floor. At 473: 11 reds ⊂ register-22 (extraction-gated;
lever = Phase-2 extraction/5.4). pool-140/358 are *not* extraction-
gated — gold in-chunks, ranks 12-47 cut at 8 (context.py:630-643) — and
are D7 named-limit holdouts (D6_CLOSE_A20.md:33-35). Not met as
registered; met by the stamp (meter 35→37). No final leg pre-close:
three width vehicles already failed (D57 −23; Leg B RED + 2
counter-flips; tiered 0 pool flips) — a fourth is new scope (invariant
5), fresh pre-registration, never a Leg B re-tune (D59).

**Q2 — Keep ABILWIDTH dead.** Flag OFF ⇒ the guard short-circuits
(context.py:638, `_abilwidth_enabled` 586-591, default "0"): inert by
construction, no re-gates owed. Revert = engine diff ⇒ reboot_rule
fails ⇒ 4-gate re-run + owner word for zero behavior change, burning the
P6 seed + Leg C union (check_targets.py:39; GATE_LEDGER.json). The kill
clause's text is the disposition (GATE.md:1021-1024).

**Q3 — TIERED default-flip: yes, after the close, as the owner decision
R5 reserved** (GATE.md:1051-1054). The flag is global: JJK no-op at
flag-ON is no longer structural — 4 gates at flag-ON (eval 31/31, span
48,572+probe, canon 236/236, pytest 1,331) + p23 473 repro prove it; any
red ⇒ no flip.

**Q4 — Attributable once flag state is labeled.** 463 (flag-OFF
official regrade, A20) → 465 (Q1-L1 +2: chap-01, arcn-07) → 469 (deriv
+4: arcn-01, org-05/06, vol-10) → 473 (Leg A +4: arcn-02/10, org-03,
state-08). The "2 unattributed" are the Q1-L1 pair (the ledger tracked
only the deriv leg). Authoritative registration = register-22
(GATE.md:73-87); FLOOR16 (check_targets.py:41-49) is a 469-era
convenience (silently lists the pool rows "floor", drops closed
arcn-01/07), not a registration. Stamp: 13 = 11 ⊂ register-22 + 2 pool;
meter 37 = 24 + 10 + 3.

**Q5 — Ritual, model-free.** Reboot_rule holds (diff `4a8616bd..0c8cc953`
empty; last_green = `20d6da4e` behavior) ⇒ "official suite" = cite the
green receipts (d7_window/), not re-run (§9a bars re-grading your own
sweep; a re-grade is owed only on engine-tree change — none). "VOID
formal" = A20's three void triggers (D6_CLOSE_A20.md:40-41) vs the 473
state: (1) no gate regression; (2) 0 green→red flag-OFF (Leg B's
{pool-149, pool-252} never shipped); (3) A-row register = the 13. Any
fire ⇒ A20 void, reconvene.

## The derivation

- **Close criterion, from the charter:** §9a
  (Plan_to_perfection.md:866-903): work units are fix-classes; the loop
  halts when no fix-class lever remains (invariant 4); GATE.md:73-87
  instantiates that as the extraction floor. Closed iff every red row's
  close lever is Phase-2 or council-ratified floor. "Extraction-gated" =
  the fact is absent from the structured layer; no retrieval fix can
  manufacture it. The pool rows fail it (facts in-chunks):
  re-registration is the invariant-5 scope decision this council is.
- **Denominator:** the halt meter counts queue rows (35 = 22+10+3), not
  p23 reds (13); the pool rows sit outside the 22 ⇒ unmet at 473 without
  the stamp.
- **VOID formal's assertion:** the A20 stamp survives production flips
  463→473; falsifier = any trigger firing. Model-free: receipts + set
  intersection.

## What I would pre-register

1. **Re-registration stamp:** pool-140/358 → floor, defect
   "width/beam", owner P2 retrieval wave; retest = class-scoped top_k
   campaign (flip both, 0 counter-flips vs {pool-149, pool-252}, blind
   19/19).
2. **VOID-formal 3-check** (model-free), receipted at
   `council_d7_close/VOID_FORMAL.md` pre-stamp; any fire ⇒ stop.
3. **Close stamp set (docs-only):** GATE.md D7-CLOSE + ledger
   `d7_close` + drift D65 + PHASE_A restamp + phase_status.txt +
   claim-scope line; owner "commit."
4. **Final width leg (if ordered post-close):** new instrument
   (class-scoped top_k=30, D57 fallback), new flag — not the dead hunk;
   bar: flip both, 0 counter-flips vs the 473 census, W ≥ 473, blind
   19/19, d6_flip rc=0.
5. **TIERED default-flip (owner-ordered, post-close):** 1 char
   (context.py:583), 4 gates at flag-ON, p23 473 repro; own commit.

## What I would NOT do

- Re-tune Leg B (D59) or reuse the dead hunk in a new leg.
- No ABILWIDTH revert, no four-gate re-run (reboot_rule holds) in this
  council.
- Flip the TIERED default inside the close (R5: post-close, owner word).
- Close-file "all 13 in the floor" without the 2-row stamp, or
  product-100% without the claim-scope line.
- Move JJK; engine commit without all-green + owner word; GPU in this
  council.

---

## ADVISOR D — Contrarian

# ADVISOR D (Contrarian)

## Position (Q1–Q5)

**Q1 — No close at this arithmetic.** Halt rule (GATE.md:83-87):
queue-remaining rows must be all extraction/floor. The close order
(drift_log.md:2210-2212) still leaves the width rows open: pool-140/358
— register rows (GATE_LEDGER.json:76; D6_CLOSE_A20.md:33-38): D7
named-limit holdouts, defect=width, D7-owned, not floor. Content in-
chunks (context.py:630-637: golds rank 12-47, cut at 8). "All 13 in
FLOOR16" (GATE.md:1042-1050) uses the #36 instrument list
(check_targets.py:41-49) whose floor label is wrong for 2 of 16: 14 are
register floor, 2 are D7 holdouts. So 13 = 11 register-floor + 2 D7
holdouts; halt rule fails on those 2. Closing now moves a known in-
corpus Phase-1 defect to Phase-2 debt without owner sign-off
(GATE.md:1048-1054 defers this call here).

**Q2 — Keep it dead (D59); stamp the trap.** Hunk + flag
(context.py:586-591, 638-643) committed 4a8616bd, default-OFF, inert
(PRE_STAGE.md:18-20). Carrying cost: a measured-RED path
(LEGB_targets.log:1) one env var from production in a shared file JJK
also traverses; the "P6 seed" (drift D63:2313-2316) inherits a known-
bad predicate. The seed belongs in the receipts, not dead in-tree code.
If the owner prefers revert: behavior-neutral vs flag-OFF but owes its
own 4-gate run + owner word.

**Q3 — Not now, not never: after the close, its own window.** The flip
changes what the gates measure (gates = flag-OFF tree,
GATE_LEDGER.json:42); folding it in muddies the close's receipts. Its
re-run: 4 gates flag-ON (new pytest pin + last_green re-stamp), eval
jjk 31/31 flag-ON (TIERED appends tier-2 to JJK bundles,
context.py:647-656), span 48,572 + probe >=390/400, canon 236/236, and
p23 flag-ON = 473/486.

**Q4 — Authoritative floor = the A20 register, not FLOOR16.** The
register (GATE_LEDGER.json:74-78; D6_CLOSE_A20.md:35-38: 16 rows with
Phase-2 owner + retest; reboot rule's 22 = 21 dim + char-04) is the
book of record; FLOOR16 is an instrument artifact — relabel (14 floor +
2 holdout). 23/17/13 wart: 463-era 23 (GATE.md:887-890) - DERIV's 4
recorded flips (GATE.md:940-942) = 19, but 469-era measured 17
(PRE_STAGE.md:34-36) -> 2 unattributed flips; ID them: 469-era
snapshot vs 463-era census (git 20d6da4e).

**Q5 — The close must produce its own receipts.** A close resting on
D7-window receipts + the 09-20 canon run rests on tree stability alone:
the reboot-rule diff check (GATE_LEDGER.json:44) proves engine
stability, not red-list stability. Ritual: (1) fresh p23 full-bank
regrade flag-OFF (expect 469, 0 self-flips); (2) flag-ON 473/486 cited
as cross-check; (3) registry scan (G-CSM max ID 7, none open — #34 hard
gate, GATE.md:493-498); (4) reboot-rule diff check; (5) VOID formal vs
the pre-registered void set (GATE.md:731-735); (6) halt meter = close's
own 13-row red list + 10 residuals + 3 r1blast stamps; (7)
PHASE_A_COMPLETE_AT_FLOOR.md: tree hash, receipts, red list, floor +
2-row ruling, Phase-2 handoff.

## Where I land

Split the difference, sequenced: (1) close the bookkeeping (ID the 2
unattributed flips, relabel FLOOR16, stamp the register as
denominator); (2) one new pre-registered width leg (new instrument,
single, probe-gated, D59-clean). PASS -> close at the 11 register-floor
rows. RED -> the owner (not the council) re-scopes pool-140/358 to
Phase-2 floor via a register amendment (defect=width, closer=Phase-2
width leg, retest=post-Phase-2) -> close. **I reverse to "close now" on
one condition: explicit owner sign-off for that re-scope, on disk,
before the ritual.**

## What I would pre-register

- Width instrument: single predicate change; probe pre-registers: flips
  {pool-140, pool-358}, 0 counter-flips (pool-149/252 named must-stay-
  green), blind 19/19, d6_flip rc=0, OOS200 >= pre-2. Kill: any
  counter-flip or missing flip => RED => owner re-scope; D59 extends to
  the new instrument.
- Pre-ritual stamps: 2 unattributed flip IDs; FLOOR16 relabel;
  denominator = close's own census; halt-meter formula.
- 7-item receipt set (Q5), inside the doc-only close commit (reboot-
  rule exempts it).

## What I would NOT do

- No ex-post re-tuning of Leg B (D59): ABILWIDTH stays dead behind its
  default-OFF flag; a new width leg is a pre-registered instrument only.
- No engine code without all-green + owner word; close commit doc-only;
  no TIERED default-flip inside the ritual (R5; gates stay flag-OFF).
- No council-authored re-registration of pool-140/358 as floor — that
  is an owner re-scope; the council records, it does not re-scope.
- Tempting but forbidden: relaxing Leg B's 0-counter-flip bar post-hoc
  (pre-registered, PREDICT.md:15-22); ABILWIDTH flag-ON in the grade
  (R5: TIERED-ON, ABILWIDTH OFF); skipping the close's own census.

---

## ADVISOR E — Expansionist

# ADVISOR E (Expansionist)

## Position (Q1–Q5)

**Q1 — Close now; no Phase-1 width leg is owed.** Halt rule met: all
non-floor fix classes green (R-1..R-7, `PHASE_A_COMPLETE_AT_FLOOR.md:
9-27`); the width class ran to its pre-registered outcome (TIERED PASS
473/486; ABILWIDTH RED by its own kill clause — D59: that IS the
close). The 13 remaining reds sit inside FLOOR16 (`GATE.md:1044-1049`).
pool-140/358 are D6-registered NAMED-LIMIT rows (`census_v1_floor_
triage.jsonl`: root_cause = qa-door ranking; owning_phase "D7
(ranking leg)") — the ranking vehicle ran; the residue is registered ⇒
Phase-2. A new leg now = new fix class after the freeze = floor-moving
(council #34).

**Q2 — Keep the ABILWIDTH hunk dead; no standalone revert.** OFF is
neutral by construction (`context.py:638` checks the flag before the
store opens ⇒ byte-identical to 20d6da4e; `PRE_STAGE.md:56-61`).
Reverting = a gate-relevant diff ⇒ four gates invalidate (`GATE_LEDGER`
reboot_rule) — a GPU window for a no-op. Keep-dead preserves the JJK
no-op invariant + the P6 seed (`_owner_attribute_hit`,
`context.py:474`); if the owner approves the flip, bundle an optional
revert into that window.

**Q3 — Recommend the TIERED flip NOW, AFTER the close ritual** (R5:
separate owner decision; pre-close it would move the tree under the
just-stamped close). The flip's 4-gate re-run (flag-ON) shows JJK gates
unchanged (pytest 1,331 W1-pin; eval 31/31; span 48,572 + probe ≥390;
canon 236/236·10/16·79.0%), CSM p23 = 473/486, measured tier-2 p50
(`TIERED_PREDICT.md:31`), ledger bump.

**Q4 — Stamp FLOOR16 as the close denominator; keep the 22-row register
as a historical P1.4 stamp.** Verified (git census diff 3c047604→
20d6da4e): 463-era 23 = 7 holdouts + 16 floor (463-era 16 ≠ FLOOR16);
463→469 closed **6**: the 4 recorded (arcn-01, org-05/06, vol-10) +
**2 unattributed = csm-dim-arcn-07 + csm-dim-chap-01**. FLOOR16
(`check_targets.py:42-49`: "the 17 @469 minus org-03") ⇒ the
denominator. Stamped register: **Tier 1 (11 extraction-gated dim
rows)** → Phase-2 D6/5.4; **Tier 2 (pool-140/358)** → Phase-2 ranking
leg, retest = clean flip (pool-149/252 stay green).

**Q5 — Ritual = 3 artifacts.** (1) *Official suite*: the four gates
from committed IDs @0c8cc953 flag-OFF (pytest 1,331; eval 31/31; span
48,572 + probe; canon 236/236), receipts in `reports/2026-09-20-*/`.
(2) *VOID formal*: `tools/csm/d6_flip.py` rc=0 (green30 flips = 0;
oos200 drop < 3 vs `D6_OOS_PRE.jsonl`) + printed line. (3)
*PHASE_A_COMPLETE_AT_FLOOR.md*: amend the P1.4 file with a D7-era re-
stamp (0c8cc953, pin 1,331, gates, 473/486, tiered register, 23/17/13
reconciliation, P6 seeds, TIERED-flip record); live claim = D7-era.

## The maximal-but-compliant endgame

1. **Close ritual** (Q5): one CPU session (or from-record re-stamp) +
   one probe window → machine-auditable close; unblocks P6 + Phase 2.
2. **TIERED flip** (Q3), the separate owner decision: one GPU gate
   window (4 gates flag-ON) + one-line commit (`context.py:583`) +
   ledger bump; 473/486 becomes default product behavior (JJK
   neutrality proven); optional ABILWIDTH revert (Q2) rides with it.
3. **Phase-2 handoff (non-cold-start)**: a pre-registered width-
   instrument spec for pool-140/358 (class-scoped vehicle per the
   registered root cause, NOT an ABILWIDTH re-tune); probe-gated,
   kill-clause-armed; bar = flip 140/358 + 0 counter-flips vs the
   473-era census + blind 19/19 + OOS floor; P6 seed list goes in the
   close file. Order 1→2→3 (the flip is an engine change; it cannot
   precede the stamp).

## What I would pre-register

- Close-file floor register (Q4): FLOOR16 denominator; 13 = 11 + 2,
  per-row owner + retest trigger; arcn-07/chap-01 correction.
- New width instrument (Phase 2): single class-scoped instrument (Leg
  B failed on its global possessive predicate), probe-gated, kill
  clause armed: any counter-flip vs the 473-era census (esp.
  pool-149/252) ⇒ kill, no re-tune.
- TIERED flip bar: 4 gates flag-ON at the Q3 values + p50; any JJK
  regression ⇒ flip VOID; `d6_flip.py` rc=0 at close state.

## What I would NOT do

- No re-tune of RED Leg B (D59) — no knob, no predicate-broadening,
  "one more try"; the kill clause IS the width-class close.
- No new Phase-1 fix class or width leg after the freeze (floor-moving,
  council #34): pool-140/358 go to Phase 2 as named-limit rows.
- No TIERED flip before the close ritual (R5; the close's denominator
  stays 0c8cc953 flag-OFF).
- No standalone ABILWIDTH revert (gate-invalidation for a no-op;
  bundle into the flip window only).
- No 22-row register as the D7-era denominator (historical stamp only);
  no engine change without all-green + owner word; no `context.py`
  change breaking JJK no-op-by-construction invariance.

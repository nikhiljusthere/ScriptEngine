# Peer-review input (anonymized) — Phase-2 plan council

## The question

## The decision

Approve / amend / reject **Phase 2 of the plan**: P2.1 CSM-4 exhaustive
tier-1 × 3 doors (pre-extraction 17,181-row control arm, ~51 GPU-h) →
P2.2 bar audit → P2.3 D6 extraction (only on the red class) → P2.4
writer-facing acceptance leg → P2.5 CSM-8 done-declaration + pilot memo,
halt before P6.

## Scope questions (answer all)

1. **Phase boundary:** is the precondition set right (PHASE_A_COMPLETE
   marker, miss queue at documented floor, ledger-of-record committed,
   100k dial, gpu-handoff reserved)? May Phase 2 start if Phase 1 halts on
   a regression instead of a floor?
2. **P2.1:** the pre-extraction control arm + ~51 GPU-h estimate. Is 51
   GPU-h a measured number or an assumption (the 4 s/probe figure's
   provenance — `reports/csm/COUNCIL_csm-campaign.md`, the csm-3 record)?
   Does the plan need a sanity-measurement step (a bounded sample first,
   re-estimate, then the full run) before committing 2 GPU-days?
3. **P2.2 ordering:** the bar audit is scheduled AFTER the 51 GPU-h
   control arm — but it judges the instrument the control arm spends 51
   GPU-h on. Should the near-free bar audit run FIRST (the first-principles
   prior-art response in `reports/csm/receipts/council_plan_v2/` makes
   this case)? What does the bar audit pre-register (3–5 cases per D6
   dimension + owner-accepted residual cap) and who grades it?
4. **P2.3:** the red-class scope — verify the per-dimension red counts
   against `reports/csm/census_dimensions_csm_results.jsonl` (the plan now
   says arc-narrative 8 / abilities 6 / state-over-time 5 / appearance 1 /
   causality 1 = 21; re-check). Is "only on the red class" faithful to the
   JJK precedent (council #19 P4 contingent extraction)? What re-opens a
   closed red (the P1.4 re-adjudication)?
5. **P2.4:** the writer-facing acceptance leg (one `script-gen` +
   `cli verify` against CSM) — is ONE script enough, or does the
   done-set need the acceptance leg as a done-criterion rather than a
   final step (the JJK §5 definition ends with "a writer can ask, of any
   line, what it means and where it sits")? What is the pass bar for
   verify?
6. **P2.5 + cost:** the CSM-8 done-declaration (D1–D10 item-by-item on
   CSM + the four pilot numbers + triage log + JJK baseline diff-empty +
   halt-before-P6) — complete as the definition of "100 % done"? Is the
   total cost section (≈ 2 GPU-days Phase 2, ≈ 1.5–2 weeks total) honest
   given the unmeasured 51 GPU-h and the two extra steps (bar audit,
   acceptance leg)?

## Grounding (verify before you record)

## The three review questions (answer all, max 200 words total)

1. Which response (A-E) is the strongest, and why?
2. What is the single biggest blind spot the five responses SHARE?
3. What did all five miss that you would have added?

## Response A



Boundary: the preconditions are right — 58-row queue at floor (verified), ledger-of-record committed, 100k dial (now 262k; one switch in P1), gpu-handoff reserved (PC_GPU_HANDOFF L3). A regression halt must not write `PHASE_A_COMPLETE`: gate the marker on "floor, not regression."
Boundary: the preconditions are right — 58-row queue at floor (verified), ledger-of-record committed, 100k dial (now 262k; one switch in P1), gpu-handoff reserved (PC_GPU_HANDOFF L3). A regression halt must not write `PHASE_A_COMPLETE`: gate the marker on "floor, not regression."


Q3: P1 already pulled the bar audit into P1.4 (A12d) — amend P2.2's text to "ran in P1.4; re-grade only if P2.1's misses change a dimension." Grader: fresh-context subagent authors 3–5 pre-registered cases per dimension (executor never edits); owner accepts the residual cap.
Q3: P1 already pulled the bar audit into P1.4 (A12d) — amend P2.2's text to "ran in P1.4; re-grade only if P2.1's misses change a dimension." Grader: fresh-context subagent authors 3–5 pre-registered cases per dimension (executor never edits); owner accepts the residual cap.


Q4: reds re-verified from the raw jsonl: 8/6/5/1/1 = 21, plan right; a closed red re-opens only via the P1.4 34 s re-adjudication.
Q4: reds re-verified from the raw jsonl: 8/6/5/1/1 = 21, plan right; a closed red re-opens only via the P1.4 34 s re-adjudication.


Q5: one script is a test, not a criterion: the pass bar (verify: every line tagged and resolved, zero confident-wrong) is a P2.5 done-criterion line.
Q5: one script is a test, not a criterion: the pass bar (verify: every line tagged and resolved, zero confident-wrong) is a P2.5 done-criterion line.


Q6: the declaration is complete if it carries P2.1's s/probe + per-door raws + panel hash into `reports/csm/GATE.md` (absent; skeleton lands in P1.1), the P2.4 receipt, the triage log, and a `PHASE_B_COMPLETE` marker — the plan names no Phase-2 marker; "1.5–2 weeks" omits P2 council cycles.
Q6: the declaration is complete if it carries P2.1's s/probe + per-door raws + panel hash into `reports/csm/GATE.md` (absent; skeleton lands in P1.1), the P2.4 receipt, the triage log, and a `PHASE_B_COMPLETE` marker — the plan names no Phase-2 marker; "1.5–2 weeks" omits P2 council cycles.
## Response B



**Verdict: AMEND (four).**
**Verdict: AMEND (four).**


**A1 — P2.1's "51 GPU-h" is stale twice (Q2, Q6).** P2.1 prices 17,181×3×4 s = 57.3 h off the pre-pin 15,400 (panel verified: `panel_csm.json` = 17,181) — the figure CSM-3's council recorded as "58-GPU-h". And 4 s/probe is a JJK number COUNCIL_csm-3 ruled "fiction"; its mandated sanity-100 re-estimate is absent from P2.1, yet the cost section freezes it as "the one number no process change touches." The only CSM rate on disk: 8.5 s/probe CPU@150k (commit `f81a1af`) — at that rate ~122 GPU-h, 2.5× the budget. **Amend:** bounded sanity-100 at the 100k dial, measure CSM s/probe, re-estimate before committing.
**A1 — P2.1's "51 GPU-h" is stale twice (Q2, Q6).** P2.1 prices 17,181×3×4 s = 57.3 h off the pre-pin 15,400 (panel verified: `panel_csm.json` = 17,181) — the figure CSM-3's council recorded as "58-GPU-h". And 4 s/probe is a JJK number COUNCIL_csm-3 ruled "fiction"; its mandated sanity-100 re-estimate is absent from P2.1, yet the cost section freezes it as "the one number no process change touches." The only CSM rate on disk: 8.5 s/probe CPU@150k (commit `f81a1af`) — at that rate ~122 GPU-h, 2.5× the budget. **Amend:** bounded sanity-100 at the 100k dial, measure CSM s/probe, re-estimate before committing.


**A2 — P2.3 is a moving target with a null branch (Q4).** Reds verified (MECH_RED 21: arc-narrative 8 / abilities 6 / state-over-time 5 / appearance 1 / causality 1); but scope is "whatever P1.4's re-adjudication leaves or adds," and a closed red de-scopes. If it closes all 21, the plan's sole comprehension step never fires and P2.5 closes D1–D10 on triage lines with no understanding layer — the goal unmet, "100 %" signed. A14 defers "de-contingent or numbered D6 item" to this council: rule now; the null branch must void P2.5, not pass it.
**A2 — P2.3 is a moving target with a null branch (Q4).** Reds verified (MECH_RED 21: arc-narrative 8 / abilities 6 / state-over-time 5 / appearance 1 / causality 1); but scope is "whatever P1.4's re-adjudication leaves or adds," and a closed red de-scopes. If it closes all 21, the plan's sole comprehension step never fires and P2.5 closes D1–D10 on triage lines with no understanding layer — the goal unmet, "100 %" signed. A14 defers "de-contingent or numbered D6 item" to this council: rule now; the null branch must void P2.5, not pass it.


**A3 — P2.4 is n=1 (Q5).** One `script-gen` over 17,181 lines, no pre-registered pass bar (verify checks tag traceability, not comprehension). Pre-register the bar; make it a done-criterion, not a last step.
**A3 — P2.4 is n=1 (Q5).** One `script-gen` over 17,181 lines, no pre-registered pass bar (verify checks tag traceability, not comprehension). Pre-register the bar; make it a done-criterion, not a last step.


**A4 — cost hides the legs (Q6); Q1: no.** "P2.2–P2.5 ≈ 1 day" omits the 11-member sequential council, the four one-copy gate re-runs, and gpu-handoff fragmentation (30–60 s model-less per switch, unpriced for a 2-day batch). Phase 2 may not start on a regression halt: the marker encodes the floor, and a regressing queue invalidates the control arm the budget would buy.
**A4 — cost hides the legs (Q6); Q1: no.** "P2.2–P2.5 ≈ 1 day" omits the 11-member sequential council, the four one-copy gate re-runs, and gpu-handoff fragmentation (30–60 s model-less per switch, unpriced for a 2-day batch). Phase 2 may not start on a regression halt: the marker encodes the floor, and a regressing queue invalidates the control arm the budget would buy.
## Response C



**Q2.** 51 GPU-h is unmeasured; csm-3's record flags it (COUNCIL_csm-3.md:152: 4 s/probe unmeasured, ≈8 h at JJK's rate; ruling (d) mandates a sanity re-estimate). v2.1 dropped it: P2.1 must open with a bounded 400-probe sanity run as the timer → re-estimate → commit. Two GPU-days is not yet a commitment.
**Q2.** 51 GPU-h is unmeasured; csm-3's record flags it (COUNCIL_csm-3.md:152: 4 s/probe unmeasured, ≈8 h at JJK's rate; ruling (d) mandates a sanity re-estimate). v2.1 dropped it: P2.1 must open with a bounded 400-probe sanity run as the timer → re-estimate → commit. Two GPU-days is not yet a commitment.


**Q3.** Gate P2.1 on P2.2: P1.4(d) pulled the bar audit's execution before the marker, but v2.1 leaves P2.2 ungated. Pre-register 3–5 cases per dimension (model-free mechanical grading per JJK's 3b; authored by a fresh-context subagent; the executor never authors — campaign-council D4 ruling) + an owner-accepted residual cap; P2.1 starts only on the on-disk verdict.
**Q3.** Gate P2.1 on P2.2: P1.4(d) pulled the bar audit's execution before the marker, but v2.1 leaves P2.2 ungated. Pre-register 3–5 cases per dimension (model-free mechanical grading per JJK's 3b; authored by a fresh-context subagent; the executor never authors — campaign-council D4 ruling) + an owner-accepted residual cap; P2.1 starts only on the on-disk verdict.


**Q4.** 21 reds verify on disk (8/6/5/1/1; v2.1 fixed the 2/4/5 error). Red-class-only is faithful to the X2.f precedent, but A14 is the hole: the sole comprehension step is contingent, and P1.4's 5.4 re-adjudication can close every red → the done-set closes on triage rows, not understanding. De-contingent it: a numbered D6 comprehension item; vacuous closure only on a dimension census re-verified at P2 start. A closed red re-opens only when the extraction-pass test or held-out out-of-sample still misses it.
**Q4.** 21 reds verify on disk (8/6/5/1/1; v2.1 fixed the 2/4/5 error). Red-class-only is faithful to the X2.f precedent, but A14 is the hole: the sole comprehension step is contingent, and P1.4's 5.4 re-adjudication can close every red → the done-set closes on triage rows, not understanding. De-contingent it: a numbered D6 comprehension item; vacuous closure only on a dimension census re-verified at P2 start. A closed red re-opens only when the extraction-pass test or held-out out-of-sample still misses it.


**Q5.** One script suffices as instrument, not final step — amend it to a done-criterion: §5's last clause (COMPREHENSION_REMAINDER:241) must hold in the done-declaration; P2.5 carries the P2.4 receipt. Pass bar: every tag resolves to a chapter/episode — zero unverified.
**Q5.** One script suffices as instrument, not final step — amend it to a done-criterion: §5's last clause (COMPREHENSION_REMAINDER:241) must hold in the done-declaration; P2.5 carries the P2.4 receipt. Pass bar: every tag resolves to a chapter/episode — zero unverified.


**Q6.** P2.5 must also carry the comprehension item + bar-audit verdict. Cost: 51 GPU-h is "the one number no process change touches" yet unmeasured (csm-3: ≈8 h at JJK's rate); write "unmeasured; sanity re-estimate first." 1.5–2 weeks holds only if the re-estimate lands near ≈8 h.
**Q6.** P2.5 must also carry the comprehension item + bar-audit verdict. Cost: 51 GPU-h is "the one number no process change touches" yet unmeasured (csm-3: ≈8 h at JJK's rate); write "unmeasured; sanity re-estimate first." 1.5–2 weeks holds only if the re-estimate lands near ≈8 h.
## Response D



**Q1 (boundary).** Phase 2's preconditions are a five-word header (100k dial; gpu-handoff authorized) + P1.4 close conditions; the real gate is a one-line marker (`PHASE_A_COMPLETE`, `phase_status.txt`) with no machine check; the plan never says "no marker, no Phase 2", so a P1.3 regression halt could still read as Phase-2-able.
**Q1 (boundary).** Phase 2's preconditions are a five-word header (100k dial; gpu-handoff authorized) + P1.4 close conditions; the real gate is a one-line marker (`PHASE_A_COMPLETE`, `phase_status.txt`) with no machine check; the plan never says "no marker, no Phase 2", so a P1.3 regression halt could still read as Phase-2-able.


**Q2 (P2.1).** The numbers collide: panel = 17,181 rows (`panel_csm.json`), but the cost line computes from "≈15,400 sentences" — the 1,781-row gap lives only in council #24. 51 GPU-h rests on 4 s/probe, an "unmeasured JJK number" per council #3 (JJK measured ≈0.47 s; records re-estimate 8–17 h, a 58-h variant also on record); COUNCIL_csm-3(d)(2) already ordered the sanity re-estimate, but P2.1 has none. "Gpu-handoff chain" / "quiet windows" are undefined in the plan; the chain's doc is a 262k→100k handoff, yet both phases run 100k — the plan never says why the chain is needed.
**Q2 (P2.1).** The numbers collide: panel = 17,181 rows (`panel_csm.json`), but the cost line computes from "≈15,400 sentences" — the 1,781-row gap lives only in council #24. 51 GPU-h rests on 4 s/probe, an "unmeasured JJK number" per council #3 (JJK measured ≈0.47 s; records re-estimate 8–17 h, a 58-h variant also on record); COUNCIL_csm-3(d)(2) already ordered the sanity re-estimate, but P2.1 has none. "Gpu-handoff chain" / "quiet windows" are undefined in the plan; the chain's doc is a 262k→100k handoff, yet both phases run 100k — the plan never says why the chain is needed.


**Q3 (P2.2).** Double-scheduled: P1.4(d) already runs the same 3–5-case bar audit pre-marker; P2.2 re-lists it — which is real? "Per D6 dimension" is undefined (CSM census has 6 classes; JJK's 14); no grader named.
**Q3 (P2.2).** Double-scheduled: P1.4(d) already runs the same 3–5-case bar audit pre-marker; P2.2 re-lists it — which is real? "Per D6 dimension" is undefined (CSM census has 6 classes; JJK's 14); no grader named.


**Q4 (P2.3).** Red counts verified against the raw jsonl: 8/6/5/1/1 = 21, matching. A14 is a correct admission: this is Phase 2's only comprehension step — de-contingent it or number it.
**Q4 (P2.3).** Red counts verified against the raw jsonl: 8/6/5/1/1 = 21, matching. A14 is a correct admission: this is Phase 2's only comprehension step — de-contingent it or number it.


**Q5 (P2.4).** The plan concedes the done-set is a "reachability proxy," then demotes the writer's test to one final step with no pass bar — make it a done-criterion.
**Q5 (P2.4).** The plan concedes the done-set is a "reachability proxy," then demotes the writer's test to one final step with no pass bar — make it a done-criterion.


**Q6 (P2.5 + cost).** "The four pilot numbers" are undefined (council #24 §8; #1/#2 already on disk in `T0_PILOT_CSM.md`); "JJK baseline diff-empty" never says which baseline (council's 1,242 or the re-baseline's 1,303+2xp, `GATE_REBASELINE_2.md`) — neither cited. "P2.2–P2.5 ≈ 1 day" has no breakdown; until the missing measurement exists, the honest range is ≈8 h, not 2 GPU-days.
**Q6 (P2.5 + cost).** "The four pilot numbers" are undefined (council #24 §8; #1/#2 already on disk in `T0_PILOT_CSM.md`); "JJK baseline diff-empty" never says which baseline (council's 1,242 or the re-baseline's 1,303+2xp, `GATE_REBASELINE_2.md`) — neither cited. "P2.2–P2.5 ≈ 1 day" has no breakdown; until the missing measurement exists, the honest range is ≈8 h, not 2 GPU-days.
## Response E



**Q1 (boundary).** P1 council pulled the model-free bar audit before the `PHASE_A_COMPLETE` marker (A12d) and recorded the R-6 verdict there (A12e; `COUNCIL_csm_p1_plan.md`). Add: hash-stamp the 17,181 panel + 200 held-out before Phase 2 (`panel_csm.json` verified) — else the control arm is not a control.
**Q1 (boundary).** P1 council pulled the model-free bar audit before the `PHASE_A_COMPLETE` marker (A12d) and recorded the R-6 verdict there (A12e; `COUNCIL_csm_p1_plan.md`). Add: hash-stamp the 17,181 panel + 200 held-out before Phase 2 (`panel_csm.json` verified) — else the control arm is not a control.


**Q2 (51 GPU-h).** An estimate: 15,400 × 3 × 4 s, 4 s/probe unmeasured (JJK warm probe 0.47 s → ≈8 h). Sanity-sample 100 probes to measure s/probe and re-estimate; the control arm still runs — its upside is the pre-extraction baseline making P2.3's delta attributable, plus the first real cost number. The plan books it only as cost.
**Q2 (51 GPU-h).** An estimate: 15,400 × 3 × 4 s, 4 s/probe unmeasured (JJK warm probe 0.47 s → ≈8 h). Sanity-sample 100 probes to measure s/probe and re-estimate; the control arm still runs — its upside is the pre-extraction baseline making P2.3's delta attributable, plus the first real cost number. The plan books it only as cost.


**Q3 (P2.2).** Ordering settled by the P1 council (audit pre-marker = pre-51-GPU-h). Pre-register the residual cap; pull the 3–5 per-dimension cases from panel lines so the control arm's output is directly adjudicated.
**Q3 (P2.2).** Ordering settled by the P1 council (audit pre-marker = pre-51-GPU-h). Pre-register the residual cap; pull the 3–5 per-dimension cases from panel lines so the control arm's output is directly adjudicated.


**Q4 (P2.3).** Recounted from raw jsonl: 21 MECH_RED / 39 green = arc-narrative 8, abilities 6, state-over-time 5, appearance 1, causality 1 — plan's figures right (2/4/5 were green counts). Red-class-only is faithful to JJK (D8: no reds → nothing built); re-opens at the P1.4 5.4 re-adjudication.
**Q4 (P2.3).** Recounted from raw jsonl: 21 MECH_RED / 39 green = arc-narrative 8, abilities 6, state-over-time 5, appearance 1, causality 1 — plan's figures right (2/4/5 were green counts). Red-class-only is faithful to JJK (D8: no reds → nothing built); re-opens at the P1.4 5.4 re-adjudication.


**Q5 (P2.4).** Make it a done-criterion, not a last step — JJK's definition ends "a writer can ask, of any line, what it means and where it sits" (`COMPREHENSION_REMAINDER:241`). Pass bar: `verify`-clean + three-layer annotation contract. Bigger: add the 16,226-point transcript leg (`transcripts.py`: "JJK only, for now"; JJK embed ≈3.5 min) — one CSM import+embed buys verbatim `[E n mm:ss]` quotes; CSM caption-source availability unverified.
**Q5 (P2.4).** Make it a done-criterion, not a last step — JJK's definition ends "a writer can ask, of any line, what it means and where it sits" (`COMPREHENSION_REMAINDER:241`). Pass bar: `verify`-clean + three-layer annotation contract. Bigger: add the 16,226-point transcript leg (`transcripts.py`: "JJK only, for now"; JJK embed ≈3.5 min) — one CSM import+embed buys verbatim `[E n mm:ss]` quotes; CSM caption-source availability unverified.


**Q6 (P2.5 + cost).** The declaration must carry the four pilot numbers (plan L214) — as template instance #2 it prices D1–D5 for the other seven corpora: crawl + index + red-class extraction. 1.5–2 weeks holds only once a sanity sample turns 51 into a number; at JJK's rate ≈8 h, not 2 days.
**Q6 (P2.5 + cost).** The declaration must carry the four pilot numbers (plan L214) — as template instance #2 it prices D1–D5 for the other seven corpora: crawl + index + red-class extraction. 1.5–2 weeks holds only once a sanity sample turns 51 into a number; at JJK's rate ≈8 h, not 2 days.
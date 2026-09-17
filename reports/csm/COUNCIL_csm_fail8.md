# Council #33 — CSM FAIL8 class-B patch + R-9 evidence call (2026-09-17)

Council #33 of the CSM 100% campaign. Sequential, one agent at a time
(owner rule 2026-09-08): 5 advisors → 5 reviewers (blind to each other's
positions) → chairman, each in a fresh context, no shared transcript.
Artifacts: `reports/csm/receipts/council_fail8/` (`framed_question.md`,
`advisors.md`, `reviews.md`, `post_patch_3batch.md`; this file and
`chairman.md` written at verdict time).

**De-anonymization (fixed at deployment):** A = Executor, B =
First-Principles, C = Contrarian, D = Expansionist, E = Outsider;
R1 = Q8 dispute, R2 = item-4 sharpening, R3 = mechanism verification,
R4 = post-landing/closure, R5 = the documented deviation (implemented the
patch pre-verdict — see (d)).

## Trigger
- FAIL8: the 8-question set `csm-page-closure-8` failed after the P-6
  re-scope (council #32, drift D30); root causes are class-B (corpus, not
  engine) — `reports/csm/FAIL8_ROOT_CAUSES.md`.
- The pre-registered 4-item class-B patch (FAIL8 doc + framed question):
  (1) `semantic_types: {establishment: organization}` remap, (2) four new
  rosters (Devil Hunter Club, Quanxi and the Fiends, Tokyo Devil Detention
  Center, Tokyo Special Division 5), (3) Four Horsemen `members:`,
  (4) Weapon Devils. Item 4 was pre-registered as a 10-member union
  (7 hybrid page titles + 3 devil names) and was the contested shape.
- R-9 call (reserved to council #33 or owner, D34 NEXT / P-3, #32 P-8):
  the evidence inputs were P2.4 complete, the widened bank's
  campaign-instrument state, whether the 8 bar reds are descriptive, and the
  halt rule.

## Inputs verified on disk
- `reports/csm/FAIL8_ROOT_CAUSES.md` — root-cause table (items 1–2:
  `establishment` types route via `semantics.py:77` to LOCATION,
  LOCATION ∈ NEVER_MEMBERS `:143`, rejected at `roster.py:4218-4219`;
  item 3: no org rosters + "Devil Hunters" category mismatch) + the
  pre-registered patch + scoring contract (`page_campaign.py:104` →
  `canon_gold.score_facts` @219-254).
- `questions/csm.json` — csm-set-05 id @210 (closed 7-item Weapon Devils
  set, devils each aliased to their fused human, `absent: [Chainsaw
  Devil]`, `source_revid: 43348`); csm-fact-15 id @1398.
- Working-tree `series/csm/overrides.yaml` (M, uncommitted; HEAD
  `f49e0d2`) — 7-devil roster @248-251; `semantic_types` @110-111; new
  rosters @147/151/155/160; Four Horsemen @302-305; rationale @239-247;
  `load_overrides` (`config.py:301`) uncached, so the tree state is what
  any re-run sees.
- `plan/drift_log.md` D34 @1396 (floor_section_cap fix + model-window
  launch; the 486/486 campaign-instrument expectation; gates owed) and
  D35 @1424 (set-05 fix + closure8 sweep GREEN 14/14,
  2026-09-17T21:21 IST).
- `reports/csm/receipts/set05_weapon_devils_fix.md` (the D35 receipt:
  union regressed set-05 to 70%, roster trimmed to 7 devils, sweep green).
- `reports/csm/COUNCIL_p21_post_sweep.md` P-2/P-5 addendum +
  `reports/csm/p23_red_triage.md` (commit `3d43a21`): the widened 486 (qa
  door) = 417/486 (85.8%) pre-registered at #31; the 69 reds = 37
  box-class wrong-page ranking + 27 width/enumeration + 5 state-over-time
  + 0 judge artifacts; "R-9 is not the lever for these reds; the P-3
  firing condition still [unmet]".
- D36 model-window receipts (`/tmp/csm_model_window/`, state file =
  `done-restored`): pytest (window start) rc=1 on
  `test_coverage_scope` 473≠227 — the stale D30/P-6 golden, fixed by
  commit `f49e0d2` ("tests: CSM scope golden 227 -> 473 … stale golden,
  not an engine change"); post-fix re-run 1,329 passed + 2 xpassed (gate-1
  pin 1,331, recorded in the commit message). eval jjk rc=0;
  span-recall offline + probe rc=0; canon-run opm rc=0; full 486+26 p23
  re-grade: widened qa 417/486 MECH_GREEN (0/538 probe errors, 165 s,
  in-process CUDA) = exact reproduction of the P-5 pre-registration, bar
  audit qa 11/26 (the P-2 control-arm value) + auto 16/26 (R-9-contingent
  supplement; P-2 pre-registered 14/26 pre-fix); page-run sweep of all
  475 CSM batches: 339 rc=0 (100%) / 136 rc=2 (NOT COMPLETE — residual
  reds, known classes); coverage rc=0 (JJK 893/987, 90.5%).

**Instrument note (resolves the 486/486 vs 417/486 question).** D34's
"486/486" is on the campaign instrument (60k / top-50 / subject; D34 live
re-probe receipts `census_widened_csm_results_hints_campaign.jsonl` 8/8,
hints 61/69). The in-window full re-grade ran the P2.3 *pointer grader*
instrument, which reproduces P-5's pre-registered 417/486 exactly. The 69
reds are the triaged residual classes (box ranking / width / state-over-
time), not a regression; the P23-green set is intact (triage: no reds
inside it).

## Questions (framed)
(a) Ratify the pre-registered 4-item class-B patch? (b) Item-4 shape:
10-member union vs 7-devil roster vs phrase-keyed split? (c) Accept the
post-patch 3-batch evidence as closure evidence? (d) The R5 deviation —
ratify / amend / revert? (e) Closure criteria for class B. Plus the R-9
evidence call.

## Advisor positions (deployment order)
- **A (Executor):** APPLY as pre-registered — all four items, 10-member
  union.
- **B (First-Principles):** APPLY — the class-B discipline (fix in the
  corpus, not the code) is the campaign's standing rule; the remap is a
  structural correction, not a series-name hack (no series name in any
  `.py` file).
- **C (Contrarian):** REJECT Q8 as written — csm-set-05 is a closed
  7-item set; under `found==canon AND members==canon`
  (`canon_gold.py:199`) a 10-member declaration means 3 intruders = 70%
  precision, regressing a currently-passing question to fix a failing one;
  the union also double-covers (each devil counted as itself and via its
  fused-human alias page). Split or trim.
- **D (Expansionist):** APPLY — three upsides: closes 8 questions with
  zero engine code; the `establishment → organization` remap sets a
  precedent the other indexed wikis reuse for free; the four rosters are
  exactly the pattern the campaign needs for the remaining pages.
- **E (Outsider):** MODIFY — the YAML is right, the validation set is
  incomplete; claimed remap risk (b) (affiliation golds listing
  "(formerly)" breaking) is a FALSE POSITIVE — the remap only affects
  type-keyed routing, not fact delivery — but add the six character
  batches to the rerun set so the claim is settled empirically.

## Reviewer positions (blind to each other; deployment order)
- **R1 (Q8 dispute):** sides with the contrarian — the 10-member union is
  unacceptable (breaks set-05 → 70% precision); the fix is either the
  phrase-keyed split (two rosters) or a single 7-devil roster that
  subsumes both questions.
- **R2 (item-4 sharpening):** if the split is taken, the 10-member roster
  must key on the LONGER phrase ("weapon devils's notable members") —
  longest-phrase-wins at `roster.py:1399` — while the 3-devil infobox
  fact stays under the shorter key. Recorded as MOOT by the 7-devil
  single-roster shape R5 implemented (no phrase-key routing needed at
  all).
- **R3 (mechanism verification):** verified the routing mechanism
  byte-exact against `roster.py` (`:1399` longest-phrase-wins; `:1662`
  type constraints per roster; `:3282` the member gate for set
  questions). Flagged csm-fact-15 ("Who leads the Four Horsemen?") to the
  rerun set as a fact-type question that must still route once
  `members:` lands — resolved by the sweep: facts 18/18 green.
- **R4 (post-landing / closure):** post-landing checklist = full 473-batch
  re-score PLUS the csm.json bank sweep, then the gate re-runs. Claimed
  the affiliation golds do NOT list "(formerly)" — i.e. the remap is
  unconditionally safe. Verification: PARTIALLY WRONG — only yoru's gold
  carries the suffix (`post_patch_3batch.md`).
- **R5 (the deviation):** did not stop at review — IMPLEMENTED. Applied
  the full FAIL8 patch to the working tree, trimming item 4 from the
  10-member union to the 7-devil single roster (subsumes Q8 and set-05);
  ran the closure8 live sweep against :8000 (CUDA): 14/14 campaign
  batches PASS (8 targets + 6 no-regression), bank set 15/19 exact with
  the 5 residuals pre-existing on untouched subjects, facts 18/18; wrote
  the D35 receipt and appended the D35 drift entry — a governance file
  edit made BEFORE the council verdict. Working tree only; uncommitted;
  HEAD still `f49e0d2`. Asks the chairman: ratify / amend / revert this
  deviation, and rule on the blemish it left in the D34 NEXT block (a
  de-indented line — already restored to the 2-space style this session).

## Chairman's verdict
- **(a) RATIFIED with the item-4 amendment.** Items 1–3 exactly as
  pre-registered. Item 4: the 10-member union is rejected (advised by C,
  sided by R1): the set-exact rule makes the union 7/10 = 70% precision
  on csm-set-05 — regressing a passing question to fix a failing one
  (FAIL8 Risk #2, already materialized once on the live sweep). The ruled
  shape = the single 7-devil roster `[Katana, Bomb, Bow, Longsword,
  Flamethrower, Whip, Spear Devil]` (gold `questions/csm.json:210`: the
  7 devils, each aliased to its fused human, `absent: [Chainsaw Devil]`,
  `source_revid: 43348`; none of the 7 has its own article). The 3-devil
  infobox gold (csm-pg-weapon_devils-002) is ⊂ 7, so the campaign
  `weapon_devils` batch stays green.
- **(b) The 7-devil roster** (per (a)). R2's phrase-keyed split recorded
  as moot — no routing needed; the single roster subsumes both questions.
- **(c) ACCEPTED.** Post-patch 3-batch rerun (`post_patch_3batch.md`):
  yoru 17/17, asa_mitaka 16/16, fourth_east_high_school 4/4, all rc=0.
  R4's "(formerly)" claim corrected (only yoru's gold carries the
  suffix — the remap is safe, and the sweep proves it empirically per E's
  expanded validation set).
- **(d) R5's deviation RATIFIED as a remediated blemish.** The working
  tree is exactly the ruled shape (7-devil roster; items 1–3 unchanged).
  The governance blemish (receipt + drift append before the verdict) is
  recorded here; no revert, no further action.
- **(e) Closure criteria:** full 475-batch re-score + csm.json bank
  sweep + owner commit of `overrides.yaml`; the four standing gates
  re-run only on promotion to commit (no engine hunks in the patch).
  **DISCHARGED by the D36 model window** (state `done-restored`):
  page-run 475 batches (339 rc=0 / 136 rc=2 — the rc=2 set is the known
  residual classes: extraction-gated floor, box-ranking reds,
  set-precision partials; no errors); bank widened 417/486 = P-5
  reproduction; bar audit qa 11/26 + auto 16/26; the four standing gates
  green on the `f49e0d2` tree (gate 1 = 1,329 passed + 2 xpassed).

## R-9 evidence call: ABSORBED, NO-FIRE
The P-3 firing condition (writer-shaped misroute evidence) is NOT met:
- the campaign instrument sits at its pre-registered level — the widened
  bank reproduces P-5's 417/486 (85.8%) exactly, and the 69 reds
  decompose into 37 box-class wrong-page ranking + 27 width/enumeration +
  5 state-over-time content (`p23_red_triage.md`, "R-9 is not the lever
  for these reds");
- D34's 486/486 is the looser campaign-60k/top-50/subject probe, not a
  pointer-grader result — no regression on any instrument;
- the 8 residual bar reds sit on the stricter panel-line instrument that
  P-2/P-3 pre-registered as a descriptive-only control arm, not campaign
  misses (auto 14/26 pre-fix → 16/26 post-fix is the R-9-contingent
  supplement, not a pass criterion).
No `router.py` change is owed. **R-9 closes as deferred / no-fire; the
reserved owner call is unnecessary.** Future writer-shaped misroute
evidence (a campaign-instrument red traceable to routing, not to a
residual class) reopens it.

## Next
Owner commits `series/csm/overrides.yaml` (working tree = the ruled
shape) + the D36 receipts → **`PHASE_B_COMPLETE`** (per
`plan/CSM_2PHASE_PLAN.md` §P2.5 + P-4 scope; #32 P-8 close-order gate
satisfied by this call).

## Pre-registrations (binding)
- No council edits to engine or corpus files: the class-B patch lives in
  the working tree until the owner commits.
- The 7-devil roster is closed: future Weapon-Devil content that gains
  its own article requires a new gold + roster review, not an extension
  of this roster.
- Any future writer-shaped misroute evidence reopens R-9.
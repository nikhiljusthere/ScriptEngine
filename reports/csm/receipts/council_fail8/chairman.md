# Chairman digest — council #33 (CSM FAIL8 class-B patch + R-9 call, 2026-09-17)

Full record: `reports/csm/COUNCIL_csm_fail8.md`. Receipts:
`framed_question.md`, `advisors.md`, `reviews.md`, `post_patch_3batch.md`
(this directory). Verdict, one line per decision:

- **(a)** Ratify the pre-registered 4-item class-B patch — items 1–3 as
  written; **item 4 amended**: 10-member union → 7-devil roster.
- **(b)** 7-devil roster `[Katana, Bomb, Bow, Longsword, Flamethrower,
  Whip, Spear Devil]` (gold `questions/csm.json:210`; `absent: [Chainsaw
  Devil]`, `source_revid: 43348`). The union is rejected: it regresses
  csm-set-05 to 7/10 = 70% precision under `found==canon AND
  members==canon` (`canon_gold.py:199`); the 3-devil infobox gold ⊂ 7 so
  the campaign batch stays green; R2's phrase-keyed split moot.
- **(c)** Post-patch 3-batch evidence accepted: yoru 17/17, asa_mitaka
  16/16, fourth_east_high_school 4/4, all rc=0; R4's "(formerly)" claim
  corrected (only yoru's gold carries the suffix — the remap is safe and
  the sweep proves it).
- **(d)** R5's pre-verdict implementation ratified as a remediated
  blemish (governance files touched before the verdict — recorded, no
  revert); working tree is exactly the ruled shape, uncommitted (HEAD
  `f49e0d2`).
- **(e)** Closure = full 475-batch re-score + csm.json bank sweep + owner
  commit. **DISCHARGED by the D36 model window** (state `done-restored`):
  page-run 339 rc=0 / 136 rc=2 residual known classes; bank widened
  417/486 = P-5 reproduction (0/538 probe errors); bar audit qa 11/26
  (P-2 control arm) + auto 16/26 (R-9-contingent); 4 standing gates green
  on `f49e0d2` (pytest 1,329 passed + 2 xpassed; eval jjk / span-recall /
  canon opm rc=0).
- **R-9: ABSORBED, NO-FIRE.** Firing condition unmet — the 69 p23 reds =
  37 box-class wrong-page ranking + 27 width/enumeration + 5
  state-over-time (`p23_red_triage.md`: "R-9 is not the lever"); 486/486
  on the campaign-60k probe is the looser instrument, not a
  pointer-grader result; the 8 bar reds sit on the pre-registered
  descriptive-only control arm. No `router.py` change owed; the reserved
  owner call is unnecessary.

**First to do (owner):** commit `series/csm/overrides.yaml` (the ruled
shape) + the D36 receipts → `PHASE_B_COMPLETE`.
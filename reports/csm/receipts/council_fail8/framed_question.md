# Council #33 — framed question (FAIL8 final-form ruling)

CSM Phase-2 accuracy loop. The full 473-batch re-score (2026-09-17) produced
8 failing questions across 8 batches ("FAIL8"). An analysis subagent root-caused
all 8 to **class B** (YAML-only, zero engine code) and pre-registered a verbatim
4-item patch in `reports/csm/FAIL8_ROOT_CAUSES.md`:

1. **Remap** — `semantic_types: {establishment: organization}` (fixes the 3
   failing establishment-affiliation questions: Family Burger Restaurant,
   Fourth East High School, Tokyo Devil Detention Center are the wiki's only
   three establishment pages).
2. **4 new roster declarations** — Devil Hunter Club, Quanxi and the Fiends,
   Tokyo Devil Detention Center, Tokyo Special Division 5 (their "notable
   members" / "employees" questions had no roster to answer from).
3. **Four Horsemen `members:`** — `[Control Devil, War Devil, Famine Devil,
   Death Devil]` (fixes csm-set-04 exact + csm-fact-15).
4. **Weapon Devils union** — 7 hybrid page-titles + 3 devil names = 10 members
   (fixes the "notable members" fact question whose gold is the 3 devil names).

## The decision (what the chairman rules)

- **(a) Final form of the 4-item patch** — ratify as-is, or amend.
- **(b) Weapon Devils shape dispute** — the pre-registered 10-member union vs
  the **7-devil roster** (reviewer 5's deviation). Grounds:
  - csm-set-05 "Every Weapon Devil" is a **closed 7-item set** (7 devils, each
    aliased to the human it fused with; `absent: [Chainsaw Devil]`), golded in
    `questions/csm.json:210`.
  - The set-exact gate is `found==canon AND members==canon`
    (`scriptengine/eval/canon_gold.py:199`). 10 declared members vs 7 canon =
    3 intruders = **70% precision** — the union regresses set-05 (FAIL8 Risk
    #2, materialized exactly as predicted).
  - The 7-devil shape **subsumes both** questions: Q8's 3-devil gold ⊂ 7, and
    set-05 7 == 7 exact. Single roster, no phrase-key routing.
  - Wiki support: the infobox `members` fact lists only 3 devil names
    (Katana/Bomb/Bow, `csm-pg-weapon_devils-002`); the gallery lists 7 hybrid
    pages; **no wiki support for a 10-item set**.
- **(c) Remap safety vs affiliation golds** — do the 6 character-page gold
  batches (yoru, asa_mitaka, death_devil, makima, fami, nayuta) list
  "Fourth East High School (formerly)" in a way the remap breaks?
  (Outsider advisor: yes, listed; reviewer 4: no, not listed. Disputed.)
- **(d) Process deviation** — reviewer 5 implemented the patch in the working
  tree (plus trimmed item 4 to 7 devils) and edited the governance file
  `plan/drift_log.md` **before** the verdict. Ratify / amend / revert?
- **(e) Final closure criteria** — what evidence closes the FAIL8 loop and the
  CSM Phase-1 accuracy campaign.

## Evidence map (chairman reads these)

- `reports/csm/FAIL8_ROOT_CAUSES.md` — root causes + verbatim pre-registered patch.
- `git diff series/csm/overrides.yaml` — the applied working-tree state
  (uncommitted; HEAD `f49e0d2`).
- `reports/csm/receipts/set05_weapon_devils_fix.md` — closure8 live sweep
  (post-patch, :8000 CUDA): 14/14 campaign batches PASS; at-risk bank green
  (set-05 exact 7/7, set-04 exact 4/4, fact-15 present); bank headline set
  exact 15/19 (5 pre-existing partials on untouched subjects), facts 18/18.
- `plan/drift_log.md` D35 entry — the applied state + sweep, as recorded.
- `questions/csm.json:210` (csm-set-05), `questions/csm.json:1400` (csm-fact-15).
- `questions/_csm_page_{yoru,asa_mitaka,death_devil,makima,fami,nayuta}.json`
  — the affiliation golds (the (c) dispute).
- `reports/csm/receipts/council_fail8/post_patch_3batch.md` — the three batches
  outside the closure8 sweep (yoru, asa_mitaka, fourth_east_high_school),
  re-run post-patch this session, all 100%.

## Process facts for the record

- Ledger (`reports/comprehension/COUNCIL_HISTORY.md`): last appended line = #30.
  Councils #31 / #32 exist on disk (`COUNCIL_p21_post_sweep.md`,
  `COUNCIL_csm_prosepass_verify.md`; drift D27/D29) but were **never appended**
  to the ledger — backfill them.
- Drift log D34's NEXT block reserved "council #33" for the R-9 evidence call;
  this council takes #33. The chairman should state whether the R-9 call is
  absorbed into this verdict (inputs: P2.4 done, 486/486 at the campaign
  instrument, 8 bar reds descriptive, halt rule → PHASE_B_COMPLETE) or still
  owed as a separate owner call.
- Anonymization (de-anonymize in the verdict): A=executor, B=first-principles,
  C=contrarian, D=expansionist, E=outsider. Reviewers R1–R5 in deployment
  order (see `reviews.md`).
- Standing rule: working tree stays **uncommitted** until the owner commits;
  the 4 standing gates re-run only if the fix is promoted to a commit
  (no engine hunk in this patch).
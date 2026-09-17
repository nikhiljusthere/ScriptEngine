# Council #33 — reviewer positions (R1–R5, deployment order)

Five reviewers, sequential, each reviewing the advisor positions and the
patch. R5's position is a deviation — see (d) in the framed question.

## R1 — the Q8 dispute
Sided with the contrarian: the 10-member union is unacceptable. It breaks
csm-set-05 (closed 7-item set; 3 intruders → 70% precision under the exact
rule). The fix must be either the phrase-keyed split (two rosters) or a
single 7-devil roster that subsumes both questions.

## R2 — item-4 sharpening
If the split is taken, the 10-member roster must be keyed on the LONGER
phrase — "weapon devils's notable members" — while the 3-devil infobox fact
stays under the shorter key (roster.py:1399 resolves longest-phrase-wins).
(Recorded as moot by the 7-devil single-roster shape, which R5 implemented:
no phrase-key routing is needed at all.)

## R3 — mechanism verification
Verified the routing mechanism byte-exact against `roster.py`:
- `:1399` — longest-phrase-wins resolution (the split mechanism R2 assumed);
- `:1662` — type constraints applied per roster;
- `:3282` — the member gate for set questions.
Flagged csm-fact-15 ("Who leads the Four Horsemen?") as a fact-type question
whose answer must still route once `members:` lands on the Horsemen roster —
added it to the rerun set. (Resolved by the sweep: facts 18/18 green.)

## R4 — post-landing / closure criteria
Post-landing checklist: full 473-batch re-score PLUS the csm.json bank sweep,
then the gate re-runs.
Claimed the affiliation golds do NOT list "(formerly)" — i.e. the remap is
unconditionally safe. (Verification: PARTIALLY WRONG — only yoru's gold
carries the suffix; see `post_patch_3batch.md`.)

## R5 — the deviation
Did not stop at review: IMPLEMENTED.
- Applied the full FAIL8 patch to the working tree, trimming item 4 from the
  10-member union to the 7-devil single roster (subsumes Q8 and set-05).
- Ran the closure8 live sweep against :8000 (CUDA): 14/14 campaign batches
  PASS (8 targets + 6 no-regression), bank set 15/19 exact with the 5
  residuals pre-existing on untouched subjects, facts 18/18.
- Wrote `reports/csm/receipts/set05_weapon_devils_fix.md` (receipt) and
  appended the D35 entry to `plan/drift_log.md` — a governance file edit made
  **before** the council verdict.
- Working tree only; uncommitted; HEAD still `f49e0d2`.

For the chairman: ratify / amend / revert this deviation (decision (d)), and
rule on the blemish it left in the D34 NEXT block (a de-indented line —
already restored to the 2-space style this session).
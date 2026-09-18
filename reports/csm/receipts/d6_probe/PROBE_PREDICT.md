# D6 falsifiable ranking probe — PRE-REGISTRATION (written BEFORE the run)

Chairman remain #1 (re-vote council): one pre-registered ranking probe
predicting a specific red→green flip by rank threshold, run and green.
This file is the registration. The run + results go in PROBE_RESULT.json.
A fresh-context certifier reviewed this file for specificity and
falsifiability before the run (certification note at foot).

## Build IDs (committed + fingerprinted, not /tmp)

- git HEAD sha + full `git status --short` + `git diff --stat` recorded
  into PROBE_RESULT.json at run time (exact tree fingerprint; no commit
  is made by the probe — commits need explicit owner request).
- store: series/csm/facts.db — events 333 (59 docs), chunks 7,797,
  vectors 5,513 (level 0+2 by design)
- grading path: in-process `scriptengine.api.main.context` (the EXACT
  function p23_grader calls — same as the 486 grades), CENSUS_DEVICE=cuda
- retrieval: `HybridRetriever.search`, product default final_top_k=8
  (scriptengine/config.py), rerank on
- judge: `tools/census_dimensions.judge` (≥2 of 3 expect terms → GREEN)
- row pre-condition: csm-dim-arcb-05 grades MECH_RED in
  reports/csm/census_widened_csm_results.jsonl (missing all 3 terms)

## Target

- Row: csm-dim-arcb-05 | class story_arcs_box | "What happens in the
  Katana Man arc?"
- expect: ["the Katana Man explains his connection to Denji before
  shooting him in the head", "Sawatari uses her Snake Devil to eat the
  Ghost Devil", "Makima's train arrives in Kyoto"]
- Gold chunk: PINNED to chunk id 4988 — doc_title "Katana Man arc",
  breadcrumb "Katana Man arc / Synopsis" (breadcrumb contains Synopsis),
  level 1, 5,070 chars, corpus-verified pre-registration to carry ALL 3
  expect terms (SQLite LIKE, no GPU). If id 4988 does not resolve at run
  time (row missing / text changed) → probe RED, branch "corpus drift".

## Predictions (all three must hold for probe GREEN)

- P1 (reproduction): in-process qa bundle for the exact question string
  → served_text → judge → MECH_RED with missing = all 3 terms.
- P2 (mechanism): `search(question, top_k=8)` → chunk 4988 is NOT in the
  8 passages but IS in `dropped` (retrieved-then-cut); AND
  `search(question, top_k=50)` → chunk 4988 at rank R with 9 ≤ R ≤ 50.
  Honesty control (reported, not pass/fail): top-8 passage doc_titles vs
  the P1 bundle beat doc_titles match count.
- P3 (counterfactual flip): P1 bundle + chunk 4988 text appended as one
  extra beat, all else identical → judge → MECH_GREEN with hits = all 3
  expect terms.

## Falsification map (probe RED — every branch terminal, no "moot")

- P1 GREEN → probe RED: the row already moved, so the defect premise is
  void for this row (grading drift or silent fix — either way the stated
  mechanism does not describe current state).
- 4988 in top-8 passages → probe RED: ranking claim false (included yet
  red; different defect).
- 4988 absent from top-50 passages AND top-50 dropped → probe RED:
  deeper gap (never retrieved), not the stated defect.
- 4988 unresolvable at runtime → probe RED: corpus drift.
- P3 RED → probe RED: judge/content gap, not a ranking gap.
Any RED outcome = D7's first negative result, recorded as such; the 48
rows stay WITHHELD-relevant and the filing re-opens.

## Reading of outcomes

- Probe GREEN ⇒ the SOLE blocker for this row is rank-inclusion: the
  D7 named-limit defect (character-card dominance over arc Synopsis in
  the qa door) is confirmed as the live mechanism, and the row flips
  green the moment ranking includes the gold chunk. Lifts chairman
  remain #1 for the 48-row family (mechanism identical by construction:
  same door, same card-vs-Synopsis shape — spot-checkable per row).
- Probe RED ⇒ the limit filing is wrong; re-open the 48 rows.

## Reading of outcomes

- Probe GREEN ⇒ for THIS row the sole blocker is rank-inclusion. It
  confirms the mechanism on one specimen; the family claim rests on the
  previously established evidence (0/69 served-text markers + chunk
  overlap), not on this n=1 — further rows are spot-checkable with this
  same cheap procedure.
- Probe RED ⇒ the limit filing is wrong; re-open the 48 rows.

## Certification (fresh-context certifier, pre-run)

- certifier session: ses_f4d14e460ffemS8nz2IdBG81Or
- first verdict: CERTIFY: FAIL — (a) vague build IDs, (b) P1-GREEN→moot
  escape hatch, (c) n=1 lifting the family, (d) selector-vs-id mismatch.
- fixes applied verbatim pre-run: tree fingerprint recorded at run time
  (no commit per standing rule); P1-GREEN→probe-RED terminal branch;
  family reading softened to mechanism-on-one-specimen; chunk pinned to
  id 4988 with drift→RED branch. Fix diff is auditable in git history.

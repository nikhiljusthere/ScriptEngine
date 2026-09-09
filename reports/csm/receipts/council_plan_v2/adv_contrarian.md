# Council plan v2 — Contrarian

**P2.3's extraction scope is computed from the wrong column.** The plan says "the 21-red
census class (arc-narrative 2 / abilities 4 / state-over-time 5 + …)". The raw
`reports/csm/census_dimensions_csm_results.jsonl` (recounted on disk): 39 green / 21 red;
reds = arc-narrative **8**, state-over-time **5**, abilities **6**, appearance **1**,
causality **1**. The plan's 2/4/5 are the *green* counts. Executed as written, extraction
covers 11 of the 21 reds and omits appearance + causality entirely → D6 ("all non-ideal
results triaged") cannot hold → "100 %" is unreachable in Phase 2 by the plan's own
definition.

**51 GPU-h is frozen as "the one number no process change touches" but is fiction the
plan's own earlier council flagged.** `reports/csm/COUNCIL_csm-campaign.md:98` computes it
as 15,400 × 3 × ~4 s, and 4 s/probe is an unmeasured assumption: the council-csm3
contrarian on disk says "the 58-GPU-h is still fiction … 4 s/probe is an unmeasured
assumption (JJK's warm probe measured 0.47 s) … ≈8 h at JJK's rate", and COUNCIL_csm-3
recorded SWITCHPOINT's 51-vs-58 inconsistency. P2.1's co-location call and the 2-GPU-day
budget rest on it, and the plan schedules no sanity-measurement step to replace it.

**The auto-commit fix lands after the window it protects.** `/tmp/csm_iter1_records/`
(the C1/C2 commit messages + the R-5 plan, staged there 06:49Z) is **gone again** —
P1.1's "~1 h" assumes a staged package that is no longer on disk, and the
ledger-of-record only lands *with* C1 itself, so P1.1 runs entirely under the fragile
mechanism it is meant to retire. The 30-entry dirty tree (`sample scripts/`,
`E:\Personal\Plot Works/`, the stale `reports/master-work/STOP`) is one `git add .` away
from being swept into the "atomic" gate commit, and the doc-hygiene fixes are named in
neither C1 nor C2.

**P1.3's halt meter trips itself.** Council #21 R2 counts "two no-reduction iterations"
over queue miss counts; the 22 floor rows *never* reduce, so a global meter halts on
iteration one. Council #21 R3's scoping ("the halt rule counts only Phase-1-fixable
classes") was not carried into P1.3's text.

Minor: P1.2's "~1 wall-day" bundles an 11-member council (the R-2+R-3 council, two small
fixes, measured ~2 h) plus R-6/R-7, which the council record leaves with an open design
question ("R-6 floor-inheritance question") — "no-council" is fiction there; and D1's
"100 frozen enumeration questions, ≥99 %" is JJK-shaped — CSM's roster census is 11
(corpus property), so the line transfers vacuously.
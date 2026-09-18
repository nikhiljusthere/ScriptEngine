# Q5 budget/breadth probe — PRE-REGISTRATION (written BEFORE the run)

Context: Q1 scoped floor won chap-01+arcn-07 (mechanism proven where
subject resolves to a story page). The 7 remaining rows all FAILED
with explicit subject set (probe-3), so derivation is INSUFFICIENT for
them — the blocker is downstream: floor depth / token budget / beam
width within resolved pages (plus org-06 breadth). This probe tests
the layer with SUPPORTED parameters only (zero code change):
token_budget 6000→20000 and top_k 8→30, each with subject=row subject.

Rows: chap-01 is GREEN (skip); targets = org-03, org-05, org-06,
vol-10, pool-140, pool-358 (6 rows).

## Predictions

- Budget arm (subject + token_budget=20000): ≥4/6 flip GREEN.
- Width arm (subject + top_k=30): ≥4/6 flip GREEN.
- org-06: flips only if breadth suffices (either arm GREEN counts;
  record which).
- A row flipping under EITHER arm ⇒ depth/budget/breadth family
  confirmed for it (fix: narrow retrieval change localizing the
  confirmed arm, NOT shipping blunt budget/width globally).
- A row flipping under NEITHER ⇒ deeper mechanism (rerank burial or
  content shape); escalate with cause, do not widen further blindly.

## Guards

- Full-bank + blind + eval-jjk re-run ONLY if a shippable narrowed
  mechanism emerges (this probe is diagnostic, not a grade change;
  official grades untouched).
- Precision watch: note any already-green row that would be affected
  by global budget/width changes (do NOT ship blunt arms).

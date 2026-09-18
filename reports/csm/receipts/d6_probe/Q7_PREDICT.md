# Q7 width-only-no-subject probe — PRE-REGISTRATION (written BEFORE the run)

Disentangling Q5's confound (its arms ran WITH hand-set subjects):
does beam width alone (top_k=30, subject=None — pure product
defaults otherwise) flip rows, or is subject-derivation also
required? Probe-3 already measured subject-only top_k=8 (all 6 red).
This probe measures the orthogonal cell. 6 rows (chap-01 already
green, excluded).

## Predictions

- pool-140, pool-358: GREEN (gold children at no-subject ranks 12/19
  enter top-30; terms sufficiency already shown).
- org-03: GREEN-or-partial (child #17 in range; needs combo).
- org-05: GREEN-or-partial (children #27/#28 in range).
- vol-10: RED (gold child #47 outside top-30; predicts floor-depth
  necessity, consistent with depth-only Q5 result).
- org-06: RED-or-partial (multi-chunk breadth; record exact).

## Reading (registered before running)

- Width-only GREEN ⇒ beam-width suffices for that row; no derivation
  needed (narrow fix = class-scoped width, NOT subject work).
- Width-only RED + subject+width GREEN (Q5) ⇒ derivation AND depth
  both required (two-leg honest accounting).
- Falsification: any row GREEN here that Q5-width said RED would
  indicate run nondeterminism (none expected; both use top_k=30 —
  must agree; mismatch voids the probe).

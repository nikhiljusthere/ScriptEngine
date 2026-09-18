# DOSE2 arc-row width sweep — PRE-REGISTRATION (written BEFORE the run)

Open question from the combined council: do arcn-01/03 (+ state-03)
need scope machinery, or does plain beam width reach their gold?
Dose probe (top_k in {8,16,24,30}, subject=None = pure product
defaults) on 3 rows. Zero code change.

## Predictions

- EITHER all three flip at some k≤30 (width mechanism extends;
  scope-pin unnecessary — kill scope-pin, extend width win), OR all
  three stay red at every k (gold unreachable by width alone;
  scope-pin leg proceeds as the only remaining retrieval path).
- MIXED outcome (some flip, some not) splits the rows by mechanism
  honestly: flipped rows join the width win, red rows go to
  scope-pin with narrowed predictions. No forced reading either way.

## Guards

- Diagnostic only: official grades untouched; no code change.
- Consistency: k=8 row verdicts must reproduce current file
  (sanity); k=30 verdicts must reproduce Q-probe-era behavior
  class (any wild divergence re-opens nondeterminism audit).

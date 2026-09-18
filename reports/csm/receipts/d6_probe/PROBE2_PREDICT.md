# Focus spike PROBE2 — PRE-REGISTRATION (written BEFORE the run)

Follows probe 1 (RED: gold chunk 4988 never shortlisted unfocused —
absent top-8/dropped8/top-50/dropped50 — while inclusion flips the
verdict green). Probe 1 isolated the defect upstream of ranking, in
candidate generation. This spike tests the precise sub-mechanism using
ONLY existing product parameters (zero code change):
`subject` (widens qa vector focus to the named page) and `focus`
(same, retriever level), both = "Katana Man arc".

Row + gold + expect: same as probe 1 (csm-dim-arcb-05, chunk 4988,
3 terms). Runner: tools/csm/d6_probe.py --subject "Katana Man arc"
--focus "Katana Man arc" --out PROBE2_RESULT.json.

## Predictions (both must hold for PROBE2-GREEN)

- P1': context(q, mode=qa, subject="Katana Man arc") → judge →
  MECH_GREEN with hits = all 3 terms (predicted: the page focus pulls
  the Synopsis chunk into the width-8 bundle).
- P2': search(q, top_k=8, focus="Katana Man arc") → chunk 4988 IN
  passages (rank ≤ 8). Rank recorded exactly.

## Falsification map (PROBE2-RED, terminal)

- P1' RED → page focus does not move the product bundle far enough;
  recall gap deeper than focus resolution.
- 4988 outside top-8 with focus (wherever it lands: dropped8,
  top-50, dropped50, absent — recorded exactly) → focus insufficient;
  lexical/vector recall or graph-neighborhood depth is the blocker.
- Either RED = second negative result; D7 must look below focus
  (index-time recall), not at rank-ordering.

## Reading

- PROBE2-GREEN ⇒ defect nailed to subject/focus resolution: the D7 fix
  is routing the arc-page focus for arc-questions (a routing-layer fix,
  same family the campaign scorer already uses per-page) — falsifiable
  claim with a live flip, no code changed.
- Certified-against-probe-1-bar by the author (same P1/P2/P3 rules,
  branch-complete map); open to council audit. Timestamps + git carry
  the order proof.

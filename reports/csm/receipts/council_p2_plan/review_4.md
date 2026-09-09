# Peer review 4 — Phase-2 plan council

**Q1 Strongest: B.** Only verdict (AMEND ×4), and only response proving 51 h is
double-stale: plan prices 15,400 (pre-pin panel) but `panel_csm.json` = 17,181
(→57.3 h at 4 s), and the only on-disk CSM rate is 8.5 s/probe @`f81a1af` →
~122 h, 2.5× the 2 GPU-day budget. B also flags P2.3's null branch: if P1.4
re-adjudication closes all 21 reds, Phase 2's sole comprehension step never
fires and P2.5 signs "100 %" on triage lines. A/C/D/E each carry one real point
(C: gate P2.1 on P2.2; D: baseline ambiguity; E: held-out stamping) but no
evidence depth.

**Q2 Shared blind spot:** all five prescribe a bounded sanity sample to
re-measure s/probe, but none stratifies it. 51 h assumes one uniform rate
across 3 doors × 17,181 rows; a 100-probe sample on one door re-estimates
under the same uniform-rate flaw that produced 51 h.

**Q3 I would add:** stratify the sanity sample per door (3×N probes) with an
explicit stop rule — if the re-estimate exceeds 2 GPU-days, shrink the panel or
drop a door before committing; and retract plan L222 ("the one number no
process change touches"), since dial/door *are* process changes. Also: the
200-row held-out is unstamped (`panel_csm.json` carries a 64-char panel hash
only) — stamp both.
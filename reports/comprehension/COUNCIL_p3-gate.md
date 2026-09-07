# COUNCIL_p3-gate — Phase 3 (ability depth), 3C gate

**Verdict: CONDITIONAL GREEN.** Advance to Phase 4 (state over time) now, with 5
ordered conditions. Not bare GREEN (a bare "track residuals" would ship a 51.7%-
uncitable prose layer and 7 residuals into 4B unexamined), not RED (the pre-committed
fork rule is met on all 5 dims, and the real defect — citation coverage — is *not*
cured by the RED lever, which is a 3A–3B extraction campaign).

- **Subject:** rule the 3C gate GREEN (advance to P4, track residuals) or RED
  (fix residuals / run 3A–3B extraction first).
- **Date:** 2026-09-07
- **Council:** 5 advisors → 5 anonymised peer reviewers → chairman synthesis, run in
  parallel (CLAUDE.md council working-agreement; this overrides the "serial" note in
  `flow.md:304` — the parallel pattern is the recorded, working one).
- **DB-verified before recording** (standing rule, `flow.md:305`). Evidence commit
  `c5f67f7` (P3.A census + oracle). Standing gates re-checked this turn: `pytest` 1239.

## Gate question

Do the P3 residuals block Phase 4, or may the campaign advance and carry them?
Phase 3 = ability depth (3A widen, 3B extract, 3C gate). Phase 4 = state over time
(4A model intervals, 4B populate, 4C gate). The load-bearing question per
`flow.md:251`: nothing models *state-at-a-moment* today, and 4B will populate those
intervals **from infobox "(Former)" facts and from synopsis prose** — i.e. 4B *consumes
retrieval output*. So "the 7 residuals are off P4's path" is an assertion that has to
be checked, not assumed.

## DB-verified evidence

| Measure | Value | Note |
|---|---|---|
| Ability census (n=315, 5 dims) | reached 264 (83.8%); reached-uncited 49 (15.6%); **not-reached 2 (0.6%)**; reached-at-all **99.4%** | per-dim max miss=1, max thin=1 → all 5 dims pass the fork rule (miss<10% AND thin<30%) |
| 545-prose census (n=545, 5 dims) | reached 258 (47.3%); **reached-uncited 282 (51.7%)**; not-reached 5 (0.9%); reached-at-all 99.1% | the 51.7% is a *citation-coverage* number, not a reachability number |
| Oracle 2C | 16/18 = 88.9% (bar 80%) | Wilson 95% CI ≈ [67%, 97%] at n=18 → **straddles the 80% bar**; `RED_floorfirst` variant 11/18 (61%) |
| Oracle surprises | **5** miscalibrated `expect=fail → PASS` (A1,A2,A3,B1,B2) | the probe labels are wrong; 88.9% is inflated |
| `pytest tests/` | 1239 passed (this turn) | standing gate green |
| Other standing gates | `eval jjk` 24/24, `canon-run opm` 236/236, `span-recall` all-lines-reachable | last green (c5f67f7); span-recall proves lines sit in chunks, **not** that retrieval returns the right section |

### The 7 residuals (authoritative harness `sub` label + `n_reached`)

| # | dim | page | `sub` | top_doc / top_sec | n_reached |
|---|---|---|---|---|---|
| 1 | Abilities and Powers | Kensuke Nagino | wrong-section | Kensuke Nagino / (root) | 0 |
| 2 | Cursed Technique | Ui Ui | cross-page | Shibuya Incident Arc / Synopsis·Entering the Station | 0 |
| 3 | History | Chiharu Miyaguni | wrong-section | Chiharu Miyaguni / (root) | 0 |
| 4 | History | Mimiko Hasaba | wrong-section | Mimiko Hasaba/Synopsis / Synopsis·Gojo's Past Arc | 0 |
| 5 | History | Nanako Hasaba | cross-page | Nanako Hasaba / (root) | 0 |
| 6 | Personality | Phantom Cursed Spirit | wrong-section | Phantom Cursed Spirit / Appearance | 0 |
| 7 | Personality | Sara Kozuki | wrong-section | Sara Kozuki / (root) | 0 |

Sub-totals: **5 wrong-section + 2 cross-page**. **All 7 have `n_reached = 0`** — these
are honest 0-content misses, not confident wrong answers.

## Advisor positions (one line each)

- **First Principles (A) — GREEN.** The question is misframed; the real test is "do
  the 7 sit on P4's critical path?", and "reached-uncited" is a citation axis, not a
  reachability one. Log the 7, put a citation-coverage check on 4B's path.
- **Executor (B) — GREEN.** The fork rule is a pre-committed mechanical trigger; all
  5 dims pass. Demand: "track residuals" must be a *named file* (page/dim/failure
  mode/owner) reviewed at the P4 gate.
- **Contrarian (C) — RED.** The verdict is a self-referential closed loop; the fork
  rule ignores the downstream metric that matters (traceability/citation); the 7 are
  the worst kind (wrong-section = a silent wrong answer); span-recall doesn't cover it.
- **Expansionist (D) — GREEN.** Bank P3.A's proof: the 282 uncited is a crawl/citation
  fix, port the census+fork gate to the other 7 wikis, P4 accelerates on a proven base.
- **Outsider (E) — RED.** The gate measures *reach*, not the *promise*; 51.7% uncited
  is the biggest ignored number; the bar has no citation dimension; "track residuals"
  covers the 0.9%, not the 51.7%.

## Peer-review consensus (5 reviewers)

- **Strongest response: A (3 of 5)** — the only one that separated the conflated axes
  and routed (not waved) the 51.7% uncited to a 4B citation check. C and B also cited.
- **Biggest blind spot: D (all 5)** — inverted the oracle-miscalibration signal into
  "upside" and called the 282 uncited a proven "crawl fix" without verifying the
  root cause.
- **What ALL five missed (convergent):**
  1. P4 *consumes* retrieval output (4B), so "zero dependency on the 7" is unverified.
  2. The critical-path claim is unverified *per class* — the cross-page items are
     plausibly *on* P4's path; only the static-trait items are plausibly off.
  3. The 5 wrong-sections may share one root cause (one fix may clear most).
  4. The 282 uncited is not a proven cheap fix (project rule: never guess a citation
     param).
  5. The oracle was quoted without an interval; at n=18 it can't separate "sufficient"
     from "marginal".

## DB-verify: struck / corrected claims

- **Struck:** the council frame's "4 wrong-section + 3 cross-page". The harness `sub`
  field gives **5 wrong-section + 2 cross-page** (table above).
- **Qualified (C/R1):** "wrong-section = a confident wrong fact that P4 propagates".
  All 7 have `n_reached=0` → they return *nothing*, so P4 consuming one gets an empty
  result (flaggable as "no source"), not a wrong fact. The residual P4 risk is the
  **cross-page** items, where the fact genuinely lives on another page.
- **Amplified (C/E):** oracle miscalibration is **5** probes, not 2; `RED_floorfirst`
  drops to 11/18. Re-label/re-run is mandatory, and 88.9% must be quoted with its CI.
- **Confirmed:** 282 reached-uncited (51.7%); 99.4% ability reached-at-all; all 5 dims
  pass the fork rule; pytest 1239.

## The recommendation (chairman)

**CONDITIONAL GREEN — advance to Phase 4 now**, with these 5 conditions in order:

1. **Before 4B consumes retrieval — the 7-item consumption-path mapping.** For each
   residual, one line: *will 4A/4B consume this line (or the page it points to)?*
   YES → fix or quarantine before that interval is populated; NO → into the residual
   file. Start with the cross-page items (intervals are cross-page by nature).
2. **Same window — root-cause triage of the 5 wrong-sections.** Determine whether one
   shared bug (router scope-word / discourse-opener / chunker boundary) explains them;
   if a single fix clears them, record the *actual* RED cost.
3. **Before 4B publishes — a citation-coverage check on 4B's path.** No interval is
   published on an uncited line; never guess a citation parameter (respect the wiki's
   own sourcing; leave unguessable params unmapped).
4. **Mechanical, at the P4 gate — the residual file.** A named file, 7 items,
   page / dim / failure mode / owner, reviewed at the 4C gate. Not a carry list.
5. **Parallel, non-blocking — oracle re-label.** Re-run the 18 with honest
   expected/actual labels, reconcile the 5 surprises against the residual list and the
   oracle/census gap, and quote the score with its 95% CI, not a bare 88.9%.

## The one thing to do first

Condition 1 — the 7-residual → 4A/4B consumption-path mapping — is the load-bearing
unverified claim. It turns A's "zero dependency" into a fact and produces the residual
file's contents in the same pass. **Done this turn: see `RESIDUALS_p3-gate.md`.**

## Disposition

- Advance to **4A** (model intervals: state, start arc, end arc, source quote).
- Conditions 1 + 4 are recorded in `RESIDUALS_p3-gate.md` (the mechanical residual
  file), to be re-reviewed at the 4C gate.
- Condition 3 (citation-coverage check) is attached to **4B**'s publish path.
- Condition 5 (oracle re-label) runs in parallel, non-blocking.
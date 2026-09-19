# PHASE A COMPLETE AT FLOOR — CSM 100% campaign, Phase 1 (2026-09-12)

Phase 1 (§9a closure loop over the frozen miss queue) halts at the
extraction-gated floor, per the pre-registered halt condition (council #28
A2, `HALT_METER_P13.md` final): every non-floor, non-extraction fix-class
R-1…R-7 green, the 33-fixable halt meter reads 33/33 ((c)=0, 10 residual rows
stamped by-design), and the queue's remaining open rows are all
extraction-gated floor / stamped / invariant-residual. All on-disk,
model-free. Council #29 (`COUNCIL_csm_p14_close.md`) ruled **CONDITIONAL
APPROVE**; all three conditions landed in the same commit as this file.

## The close evidence (four receipts)

1. **Four-gate copy @`407c016` — ALL GREEN** (ledger `p14_close_copy`, run
   dir `reports/2026-09-11-2218/`): pytest **1,321** (3 failed = the env-mc
   trio under W1 `:8000`-down, as expected) / eval jjk **31/31** /
   span-recall jjk **48,572 rc=0 (100.0000%) + 398/400 live (99.5%)** /
   canon opm **236/236 (100%) · 10/16 exact · 79.0% · 0 confident-wrong**.
2. **5.4 re-adjudication of the 22-row floor**
   (`receipts/census_5_4_readjudication_p14.md`): 34 s one-copy, 21 RED /
   39 GREEN of the 60-question census, red-ID set identical to 2026-09-09,
   **0 closed / 0 new** — the floor holds.
3. **P2.2 bar-audit pull-in** (`bar_audit_p14_preregistered.json` +
   `receipts/bar_audit_p14_author.md`): 26 cases / 78 expect terms,
   model-free, pre-PHASE_A_COMPLETE per plan A21.
4. **Halt meter final** (`HALT_METER_P13.md`): (a)=22 / (b)=13 / (c)=0,
   halt residual 35 open, 33/33 fixable.

## The floor (22 rows)

22 extraction-gated rows = 21 `csm-dim-*` (1:1 with the 21 census reds
re-verified in the 5.4 pass) + `csm-char-04` (R-7x; not in the 60-q census;
floor-confirmed by the R-7 close re-sweep, `receipts/r7_class_resweep.md`).
Canonical queue tally: 58 = 22 floor + 33 fixable + 3 r1blast stamps;
35 open = 22 floor + 10 fixable-open (stamped by-design residual) + 3
stamps; 23 closed (all fixable). Closing these 22 rows is Phase 2's P2.3
(D6 extraction, red class only).

## What "100%" does and does not claim

"100%" = **100% of the pre-registered fixable classes at the
extraction-gated floor (33/33)** — not 100% of pages. Live per-page state
(2026-09-12, `reports/csm/COVERAGE.md`): CSM **175/537 (32.6%)**, 1,260
questions, in-scope remainder 52; JJK baseline 893/987 (90.5%). The 22-floor
is a **halt, not a completion**. The per-page campaign (Q4) runs alongside
Phase 2; the in-parts long-prose treatment (Q5, out-of-gate) is a Phase-2
scope item.

## Known open finding (recorded, deferred)

env-mc trio 2/3 with `:8000` up: `test_research_bare_character_name_is_narrative`
fails for a **real** reason — the router returns `qa` for bare "Maki Zenin"
(pre-existing since `8d07487` vs test intent `d531329`; hidden a month
behind "needs a live `:8000`"). **Deferred to P1.5 (MCP bridge); test-side
fix (expect `qa`); gate-1 pin 1,321 unchanged.**

## Phase-2 gate (what may start next, and what it owes)

- Restart `:8000` in a Qwen quiet window.
- **P2.1 step 0 before any panel hour:** per-door sanity-100 → re-estimate
  17,181 × measured s/probe per door into `reports/csm/GATE.md` + record the
  A17 per-door floor policy pre-sweep → go/no-go (>2 GPU-days ⇒
  abort/shrink/council). The plan's 51-GPU-h is double-stale (4 s/probe is
  fiction; on-disk ceiling 8.5 s/probe CPU@150k ≈122 h).
- Q3: the P2.3 null branch is re-gated on the **widened** census (5 in-scope
  page types), not the 60-q character census.
- 200-row held-out leg (`heldout_declaration_csm.md`, A24/A26) before the
  P2.3 verdict.
- The Phase-2 gate verifies the marker's ledger sha256 + floor before any
  panel spend.

## D7 re-stamp (council #37, 2026-09-20 — PROVISIONAL)

Phase 1 closes at the **re-stamped** floor via council #37 (receipt
`reports/csm/receipts/council_d7_close/`: framed question, advisors
A–E, peer reviews R1–R5, chairman ruling `chairman.md`). The 22-row
floor section above **stands as history** (register-22 = the
historical P1.4 stamp). Re-stamp: register **22 → 24** — the 2 pool
width rows {csm-abl-pool-140, csm-abl-pool-358} join the floor as the
width-class P2 retest — and the halt meter **35 → 37 (24+10+3; 35 =
the superseded P1.4 stamp)**. The halt rule is UNMET as registered
(the pool rows sit in the A20 D7 holdout register, not register-22)
and MET via the re-stamp (D's governing share, verbatim: "halt rule
unmet-as-registered, met-via-provisional-stamp").

- **Close register (13 reds @473/486):** 11 extraction-gated dim rows
  ⊂ register-22 (owner: P2 extraction track / 5.4 re-adjudication;
  retest: post-extraction re-grade) + 2 width-class rows (defect:
  width — subsection recall; gold ranks 12–47 cut at 8; owner: P2
  width leg; retest: owner-triggerable per the width-class trigger
  line in GATE.md D7-CLOSE). **PROVISIONAL: council-ratified (#37);
  owner-ratified-by-return; void on veto.**
- **FLOOR16 relabel (bookkeeping, not re-scope):** 14 floor + 2
  ratified-width, ratified as the 473-era denominator.
- **VOID formal 3/3 PASS** (model-free, pre-stamp,
  `receipts/council_d7_close/VOID_FORMAL.md`); the four standing gates
  stand @`0c8cc953` via the reboot_rule (gate-relevant diff
  `4a8616bd..HEAD` empty — a docs-only close owes no gate re-run).
- **The 100% claim, re-stamped:** 100% of the pre-registered fixable
  classes at the re-stamped floor; shipped product (flag-OFF) 469/486;
  campaign grade (flag-ON) 473/486; JJK remains 100%. The TIERED
  default-flip (owner option 3) amends this claim if ordered.
- **Owner's decision set on return:** 1 "Commit" = ratify (stamp
  final); 2 "Commit without sign-off" = close stands as a council
  stamp, re-scope pending; 3 "TIERED flip word" = gated engine
  window; 4 "None" = the provisional stamp is voided, the close
  reverts to deferred.
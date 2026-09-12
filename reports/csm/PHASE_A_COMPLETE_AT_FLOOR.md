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
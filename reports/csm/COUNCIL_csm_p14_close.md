# COUNCIL — CSM P1.4 close (2026-09-12, council #29)

## Question

SHIP-or-amend the **Phase-1 (P1.4) close of the CSM 100% campaign** — all
pre-registered fix-classes R-1…R-7 green, halt condition met — on the
evidence: four-gate copy ALL GREEN @`407c016` (pytest **1,321** / eval jjk
**31/31** / span-recall jjk **48,572 rc=0 + 398/400 (99.5%)** / canon opm
**236/236 · 10/16 · 79.0%**; run dir `reports/2026-09-11-2218/`, ledger
`p14_close_copy`), the 34 s one-copy 5.4 re-adjudication of the 22-row floor
(21 RED / 39 GREEN of 60, red-ID set identical to 09-09, **0 closed / 0 new**),
the P2.2 bar-audit pull-in (`bar_audit_p14_preregistered.json`, 26 cases /
78 expect terms, model-free), close conditions (a)–(e) satisfied on disk, and
the pre-registered questions Q1–Q5 (`CLOSE_COUNCIL_PREREREGISTERED.md`).
Framed question: `reports/csm/receipts/council_p14_close/framed_question.md`.

## Members

11: 5 advisors + 5 peer reviewers + chairman.

| Letter | Role | File |
|---|---|---|
| A | The Outsider | `advisors.md` (final verbatim) |
| B | The Executor | `advisors.md` |
| C | The First Principles Thinker | `advisors.md` |
| D | The Expansionist | `advisors.md` |
| E | The Contrarian | `advisors.md` |
| R1–R5 | Peer reviewers (anonymized, weighted to failure modes) | `reviews.md` |
| Chair | Chairman | `chairman.md` |

**Method note:** all 10 members ran **in parallel** (owner directive 2026-09-12:
"council's all 5 at a time"; the 2-at-a-time limit covers working subagents
only). The parallel batches expired before finals could be captured, so the
10 finals were **restored verbatim from opencode.db session transcripts**
(traces `/tmp/opencode/council_close/`; letter↔session map in `advisors.md` /
`reviews.md`; one cancelled early advisor run, `ad_contrarian_v1`, 4 lines,
discarded and noted). The chairman then ran as a single fresh-context,
zero-GPU, read-only subagent (`ses_f6bbd1bddffehoEVKHeI8xZNWH`).

## Verification notes

Chairman re-verified every load-bearing claim against disk before recording:

| Claim | Verification | Result |
|---|---|---|
| Gate-tree head = `407c016`, not `af382ee` | `GATE_LEDGER.json` `p14_close_copy.head` = `407c016` (P1.3-finalize commit); `git log` shows `af382ee` as the later **doc-only** P1.4 stamp (drift D24, ledger, run dir, +400 span-recall rows) | **Confirmed** — B's `af382ee` citation is a misquote (formally resolved in `chairman.md`); zero gate-relevant diff |
| Queue arithmetic | `miss_queue_csm_iter1.jsonl` counted by hand: 58 rows = 22 floor + 33 fixable + 3 r1blast stamps; 35 open = 22 + 10 + 3; 23 closed | **Confirmed** — A's HOLD ground 2 refuted on disk |
| 200-row held-out leg exists | `reports/csm/heldout_declaration_csm.md` (A24/A26) | **Confirmed** — A's HOLD ground 3 and R3's error refuted on disk |
| 22-vs-21 floor gap | 5.4 receipt re-verified 21 `csm-dim-*` reds; 22nd row `csm-char-04` (R-7x) rests on the R-7 close re-sweep (`r7_class_resweep.md`) | **Reconciled** (one-liner in the rulings file) |
| Re-pin 1,321→1,324 | 1,321 is the W1 collect count with the env-mc trio failing on connection errors; the fix adds no tests; ledger says "pin (1,321) unchanged" | **Incoherent — rejected**; pin stays 1,321 |
| Live dial 122880 (120k) | `plan/SWITCHPOINT.md` + close receipts; the plan's "100k dial" heading is a stale label | **Confirmed** — no second switch owed |

## Verdict

**CONDITIONAL APPROVE** (chairman; E's conditional-approve shape, conditions
made model-free). Three on-disk, model-free conditions — all landed in the
close commit:

1. `reports/csm/CLOSE_COUNCIL_RULINGS_Q1_Q4.md` committed — Q1–Q4 answered
   with reasons and live denominators (standing instruction).
2. `reports/master-work/phase_status.txt` carries the `PHASE_A_COMPLETE <ts>`
   line **with the full marker substance** (commit `407c016` + receipt paths +
   ledger sha256 + floor 22 + rulings path + denominator caveat + env-mc known
   open) — not a boolean (A20/E2: a bare marker is a self-attestation hole).
3. `reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` committed in the same commit
   (assembles the four receipts + rulings + the env-mc known-open finding).

No gate re-run is owed (all four green @`407c016`, ledger `p14_close_copy`).
P2.1 step-0 re-estimate is a post-marker gate on panel spend, not a marker
condition.

## Rulings (summary — full text `CLOSE_COUNCIL_RULINGS_Q1_Q4.md`)

Q1 No (widen the 60-q census to the 5 in-scope page types; P2.1 entry
condition). Q2 No (10 q vs 376 ability rows; size the pool to the rows). Q3
Yes (re-gate the P2.3 null branch on the widened census). Q4 Yes, alongside
P2.1 (per-page campaign already running: 175/537, 1,260 q, remainder 52).
Q5 (D-only, recorded out-of-gate): in-parts long-prose = Phase-2 scope item.

## Residuals

- **env-mc** (bare "Maki Zenin" → `qa` vs test's narrative expectation;
  pre-existing since `8d07487`): deferred to P1.5; **test-side** fix (expect
  `qa`, per the router's documented bare-name rule `router.py:809-812`);
  router-side forbidden mid-wave (JJK baseline-freeze); P1.5 exit = live
  proof 3/3 with `:8000` up + ledger note; **pin stays 1,321**.
- **51-GPU-h double-stale** (17,181×3 at an unmeasured 4 s/probe; on-disk
  ceiling 8.5 s/probe CPU@150k ≈122 h; A17 per-door floor policy not yet on
  disk): P2.1 step-0 must, **before any panel hour**, run per-door
  sanity-100, re-estimate 17,181 × measured s/probe per door into
  `reports/csm/GATE.md`, record the A17 floor policy pre-sweep, then
  go/no-go (>2 GPU-days ⇒ abort/shrink/council).
- **No Qwen-switch chain in the close act** (R5 point (b) rejected): the
  single dial switch already executed (262k→100k at D20, owner-directed
  262k→122880/120k at `81df799`); the close is a zero-GPU, model-free marker
  act at the live 122880 dial.

## Next

Close commit (path-limited): this record + receipts + rulings + marker +
`PHASE_A_COMPLETE_AT_FLOOR.md` + `GATE_LEDGER.json` `p14_close` stamp +
COUNCIL_HISTORY #29 + drift D25 + work_log ACT. Then Phase 2: restart `:8000`
in a Qwen quiet window → P2.1 step-0 sanity-100 + on-disk re-estimate →
200-row held-out leg → P2.3 extraction (closes the 22 floor rows).
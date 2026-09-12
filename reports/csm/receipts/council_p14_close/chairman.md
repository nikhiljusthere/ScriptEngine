# CSM P1.4 close council — chairman synthesis (council #29)

Chairman: fresh-context subagent (`ses_f6bbd1bddffehoEVKHeI8xZNWH`), zero-GPU,
read-only, 2026-09-12 ~11:4x IST. Seeded with the framed question
(`framed_question.md`), the 10 finals (`advisors.md`, `reviews.md`), and
pointers to the on-disk evidence; every load-bearing claim independently
re-verified against disk before recording (queue counted by hand: 58 rows =
35 open / 23 closed, 21 D6-extraction + 1 R-7x open; git confirms `407c016`
= P1.3-finalize head and `af382ee` = doc-only P1.4 stamp; close conditions
(a)–(e) all present; `phase_status.txt` absent; live dial 122880/120k per
`plan/SWITCHPOINT.md`).

## Verdict

**CONDITIONAL APPROVE.** The close stands; the marker lands only when these model-free, on-disk conditions land:

1. `reports/csm/CLOSE_COUNCIL_RULINGS_Q1_Q4.md` committed — Q1–Q4 answered with reasons and live denominators (standing instruction, `CLOSE_COUNCIL_PREREREGISTERED.md`).
2. `reports/master-work/phase_status.txt` gets the `PHASE_A_COMPLETE <ts>` line carrying the full marker spec below (substance, not a boolean — A item 1, E item 2).
3. `reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` committed in the same commit (assembles the four receipts + rulings file + the env-mc known-open finding).

No gate re-run is owed (all four green @`407c016`, ledger `p14_close_copy`); P2.1 step-0 re-estimate is a post-marker gate on panel spend, not a marker condition.

## Q1–Q5 rulings

- **Q1:** No — "dimensions green" is not claimable from the character-only 60-question census (36 subjects of 537 pages). Widen to the 5 in-scope page types (chapter_box 232 / episode 12 / volume_box 26 / story_arcs_box 14 / organization 11). Model-free authoring; entry condition of P2.1, run inside the sanity window — not a marker blocker.
- **Q2:** No — 10 questions vs 376 ability rows (75 characters) is not a sufficient bar; size the pool to the rows (JJK precedent: 315-pair pool).
- **Q3:** Re-gate the P2.3 null branch on the widened census: extraction de-scoping requires the widened census green, not the 60-question character census alone (A22's voids-P2.5 shape stands; firing needs the widened denominator).
- **Q4:** CSM owes the per-page campaign (JJK shape; no deliberately-different done-criterion is recorded as a scope decision, so none is). It is already running: **175/537 (32.6%), 1,260 questions, in-scope remainder 52** (JJK: 893/987, 90.5%). Runs **alongside** P2.1 — the 22 floor rows are extraction-gated (extraction is the hard dependency); page authoring is model-free, zero GPU contention. Not before.
- **Q5** (ruled by D only; A/B/C/E silent — recorded explicitly): yes — the long-prose blocks (arc narrative 112,628 w/471 §; chapter/episode summaries 90,421 w/243 §) need JJK's in-parts treatment (waves, templates, triage log), not line-level retrievability alone. **Out-of-gate:** the standing instruction binds Q1–Q4 only; Q5 lands as a Phase-2 scope item, not a marker condition.

**22-vs-21 reconciliation:** the 22-row floor = 21 `csm-dim-*` rows 1:1 with the 21 reds re-verified by the 5.4 re-adjudication (`receipts/census_5_4_readjudication_p14.md`) + `csm-char-04` (R-7x, not in the 60-q census; floor-confirmed by the R-7 close re-sweep, `receipts/r7_class_resweep.md`) — so the 21/21 census re-run covers every census row of the floor; the 22nd row rests on the R-7 re-sweep, and the floor stands.

**Canonical tally:** 58 = 22 extraction-gated floor (21 D6-extraction + 1 R-7x) + 33 fixable + 3 r1blast stamps; 35 open = 22 floor + 10 fixable-open (stamped by-design residual) + 3 stamps; 23 closed (all fixable). The halt meter counts only the 33 fixable → 33/33, (c)=0.

## Marker spec

One line per field in `reports/master-work/phase_status.txt`:

- Commit: `407c016` (gate-tree head); P1.4 stamp commit `af382ee` (doc-only, gate-validating via `reboot_rule`).
- Receipts: `reports/2026-09-11-2218/`, `reports/csm/receipts/census_5_4_readjudication_p14.md`, `reports/csm/bar_audit_p14_preregistered.json`, `reports/csm/HALT_METER_P13.md`.
- Ledger sha256: sha256 of `reports/csm/GATE_LEDGER.json` (the `p14_close_copy` block); the Phase-2 gate verifies hash + floor.
- Floor: 22 extraction-gated rows (21 `csm-dim-*` + `csm-char-04` R-7x).
- Rulings: `reports/csm/CLOSE_COUNCIL_RULINGS_Q1_Q4.md` (same commit).
- Denominator caveat: "100%" = 100% of the pre-registered fixable classes at the extraction-gated floor (33/33), not 100% of pages — CSM 175/537 (32.6%), 1,260 q, remainder 52; JJK 893/987 (90.5%); 22-floor = halt, not completion.
- Known open finding: env-mc trio 2/3 (bare "Maki Zenin" → `qa`, mismatch pre-existing since `8d07487`), deferred to P1.5, gate-1 pin 1,321 unchanged.

## Residuals to record

- **env-mc:** defer to P1.5 (owner-directed; the directing session owns it; B skips P1.5). Fix **test-side**: correct the test's narrative expectation to `qa`, matching the router's documented bare-name→`qa` rule (`router.py:809-812`, `8d07487`); router-side is forbidden mid-wave (JJK baseline-freeze rule — it would force a four-gate re-run for zero Phase-2 benefit). P1.5 exit conditions: trio 3/3 in the live proof with `:8000` up, recorded in the ledger; **no re-pin** — see E's number below.
- **51-GPU-h double-stale:** the plan's 51-GPU-h prices 17,181×3 at an unmeasured 4 s/probe JJK figure (fiction); the on-disk CSM ceiling is 8.5 s/probe CPU@150k ≈122 h, and the A17 per-door floor policy is not yet on disk. P2.1 step-0 must, before any go: run per-door sanity-100, re-estimate full-sweep cost per door (17,181 × measured s/probe) into `reports/csm/GATE.md`, record the A17 floor policy in GATE.md pre-sweep, and go/no-go (re-estimate >2 GPU-days ⇒ abort/shrink/council). No panel hour before the re-estimate exists on disk.
- **Qwen switch chain (R5 point (b)):** rejected. The plan commits to "one dial switch total" at the P1.1 precondition — already executed (D20 262k→100k, then the owner-directed 262k→122880/120k at `81df799`, `plan/SWITCHPOINT.md`; live dial = 122880). The plan's "same 100k dial" heading is a stale label for the 120k dial; its actual commitment is "no second switch," which holds. The close act contains **no** checkpoint→qwen-switch chain — it is a zero-GPU, model-free marker act at the current dial.
- **Contradictions formally resolved:**
  - B's misquote: ledger `p14_close_copy.head` = `407c016` (the P1.3-finalize commit); `af382ee` is the later doc-only stamp (drift D24, ledger, run dir, +400 span-recall rows — zero gate-relevant diff).
  - A's refuted HOLD grounds: (2) the arithmetic reconciles in `miss_queue_csm_iter1.jsonl` (58 = 22+33+3; 35 = 22+10+3); (3) the 200-row held-out leg is declared in `reports/csm/heldout_declaration_csm.md` (A24/A26).
  - R3's error: R3 ground 2 (B approved "on a false verification claim") is itself refuted on disk — the leg *is* declared; B was right, R3's review was not (parent cross-note).
  - E's re-pin: 1,321→1,324 is incoherent — 1,321 is the W1 collect count with the trio failing on connection errors, and the fix adds no tests; the ledger says "pin (1,321) unchanged." P1.5 exit = live proof 3/3 + ledger note; pin stays 1,321.
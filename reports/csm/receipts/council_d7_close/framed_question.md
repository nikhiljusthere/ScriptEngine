# Framed question — D7 close council (CSM Phase 1, §9a closure loop)

Council #37, 2026-09-20, opencode session. Sequential deployment (owner
rule 2026-09-08): 5 advisors (A–E) → 5 peer reviewers (R1–R5) → 1
chairman. All 11 fresh-context, GPU-free, read-only.

## State of play (the evidence pack)

- **CSM position: D7 window closed, result recorded.** The council #36
  window (LEGS-FIRST-FLAGGED) ran to completion via the detached
  kill-window chain (`reports/csm/receipts/d7_window/RECEIPT_DONE`); its
  result was recorded 2026-09-20 (GATE.md section "D7 re-score window
  (council #36)", commit `ea9a541c`):
  - **Leg A (TIERED=1, ABILWIDTH=0) PASS** — W = 473/486 (+4/−0 vs bank
    469: arcn-02, arcn-10, org-03, state-08); 0 counter-flips; blind
    19/19; OOS200 168→198; green30 clean; `d6_flip` rc 0; FLOOR A: 3/16
    flipped (arcn-02, arcn-10, state-08).
  - **Leg B (TIERED=0, ABILWIDTH=1) RED** — W = 469/486; both registered
    targets flipped (pool-140, pool-358) **but 2 counter-flips
    {pool-149, pool-252}** (bar: 0 counter-flips) ⇒ RED; FLOOR B: 2/16
    (pool-140, pool-358). **Kill clause (D59):** the ABILWIDTH hunk stays
    behind its default-OFF flag (unset = inert); **no ex-post re-tuning**.
  - **Leg C (both ON) not run** (halt at first RED; gates still ran).
- **Engine state:** `scriptengine/api/context.py` carries both hunks,
  committed at checkpoint `4a8616bd` ("switchpoint checkpoint, D59
  never-lose"); flags `SCRIPTENGINE_TIERED_RECALL` /
  `SCRIPTENGINE_ABILWIDTH_RECALL`, **both default "0"** (in-tree: TIERED
  inert by construction, ABILWIDTH inert by its data dependency).
  Gate-relevant diff `4a8616bd..0c8cc953` is empty (HEAD = `0c8cc953`).
- **All four standing gates green on tree `0c8cc953`** (flag-OFF =
  `20d6da4e` behavior): pytest 1,331 = 1,326+2x+3 env-mc (W1 pin shape) /
  eval jjk 31/31 / span-recall jjk 48,572 offline + 398/400 live (99.5%) /
  canon opm 236/236, 10/16, 79.0% (the window's canon step missed on
  "no server"; re-run 2026-09-20, run dir `reports/2026-09-19-2004/`).
  `GATE_LEDGER.json` last_green bumped (reboot anchor b8b0ed5 → 4a8616bd).
- **Red state after Leg A (TIERED ON): 473/486 = 13 reds** — per the
  window's instrument `tools/csm/check_targets.py` FLOOR16 ("the 16
  Phase-2 floor rows = the 17 git-HEAD p23 reds minus the org-03 D7
  holdout"), **all 13 remaining reds sit inside the 16-row list**
  (pool-140/358 + 11 dim rows). The D6 close's formal registration (A20,
  `D6_CLOSE_A20.md`) instead records **7 D7 named-limit holdouts
  (chap-01, org-03/05/06, vol-10, pool-140/358) + 16 floor rows
  (ROUTING×12 / CONTENT×2 / PARTIAL×2, each with a Phase-2 owner +
  post-Phase-2 retest)** — pool-140/358 are there as D7 holdouts,
  defect class "width" (subsection recall; gold ranks 12–47 cut at 8).
  The two bookkeeping lines disagree on whether pool-140/358 are
  Phase-2-floor or Phase-1-closeable. There is also an arithmetic wart:
  the D7-spike section (463 era) counted 23 reds (7 holdouts + 16 floor);
  486−469 = 17 reds at the 469 era, but the deriv leg's recorded 4 flips
  (arcn-01, org-05/06, vol-10) close only 23→19 — 2 unattributed flips.
- **The D61 queue (post-width):** "width (tiered, chair-ordered) → depth
  (arcn-03/04, state-03, vol-10-class) → official suite → VOID formal →
  CLOSE." The width step is done (Leg A PASS; Leg B RED). The depth rows
  (arcn-03/04, state-03) are themselves inside FLOOR16. "Official suite"
  and "VOID formal" are not yet specified anywhere (D60 calls it
  "P2-void formal on production flips"; GATE.md's halt rule says "B
  writes `reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` and stops").
- **Halt rule (GATE.md):** "When every non-floor, non-extraction
  fix-class is green and the queue's remaining open rows are all
  extraction/floor (halt residual 35 = 22 floor + 10 residual + 3
  `r1blast-*` stamps), B writes `PHASE_A_COMPLETE_AT_FLOOR.md` and
  stops." The 22 floor rows = the 21 D6-extraction rows + csm-char-04
  (close lever: the Phase-2 extraction track / 5.4 re-adjudication).
- **P6 note (recorded out-of-gate at #36):** TIERED/ABILWIDTH are
  generic, zero-hardcoded cross-corpus retrieval primitives — the P6
  seed; P6 stays deferred until Phase 1 closes.
- **Environment (no longer a wall):** Qwen re-dialed by the owner to
  138240 (pid 28619, `qwen_mode` ts 2026-09-20T01:20:31, api=cpu,
  5,988 MiB free); `:8000` up on CPU (steady state); the oc-switch
  tooling (`tools/master-work/switch_restart3_oc.sh`, `0c8cc953`)
  survives any future dial change.
- **Standing rules that bind this council:** D59 (no ex-post re-tuning
  of a RED leg); R5 (both flags ship default-OFF; the CSM p23 grade
  runs flag-ON; standing gates default-OFF; the TIERED default-flip is a
  separate owner decision); commit engine code only on green + owner
  word; JJK stays 100% (four gates re-run after any engine change).

## The questions (chairman rules each)

- **Q1 — Phase-1 close determination.** With 13 reds remaining, all 13
  inside the instrument's FLOOR16 but with pool-140/358 formally
  registered as D7 named-limit holdouts (width defect, not
  extraction-gated): is the halt rule met NOW (Phase 1 at the
  extraction floor; the close ritual runs) or does pool-140/358 need one
  final width leg in Phase 1? If a final leg: its design constraints
  (must not counter-flip pool-149/252 or any green row; pre-registration
  per D59; single instrument).
- **Q2 — ABILWIDTH hunk disposition.** Kill clause says "revert the hunk
  or unset the flag". It is committed (4a8616bd) behind a default-OFF
  flag (inert). Revert the dead code vs keep it dead (P6 seed)? Which,
  and does the revert need its own 4-gate re-run (is flag-OFF behavior
  byte-identical to post-revert behavior — i.e. is the revert
  behavior-neutral)?
- **Q3 — TIERED default-flip recommendation** (the R5-deferred owner
  decision): flip `SCRIPTENGINE_TIERED_RECALL` default to "1" for CSM
  (and the standing gates to flag-ON) — recommended now, after the close
  ritual, or never? What must the flip's 4-gate re-run show?
- **Q4 — Bookkeeping integrity.** Reconcile the 23 (463 era) vs 17 (469
  era) vs 13 (473 era) red arithmetic (the 2 unattributed 463→469
  flips); pick the authoritative floor registration (which "16" / which
  "22") and stamp it so the close ritual's denominator is exact.
- **Q5 — Close-ritual spec.** Pre-register what "official suite → VOID
  formal → `PHASE_A_COMPLETE_AT_FLOOR.md`" concretely is: the runs, the
  file, the stamps, the halt meter, and the Phase-2 handoff (the 22-row
  floor + 10 residuals + 3 stamps stay open by design).

## Where to read (all on disk, read-only)

- `reports/csm/GATE.md` — the "D7 re-score window (council #36)" section
  (the new record) + the D7 spike/ranking-probe sections + the halt rule
  + the D6 CLOSE (A20) section.
- `reports/csm/GATE_LEDGER.json` — last_green (D7 window) + reboot_rule
  + d6_close registration.
- `reports/csm/receipts/d7_window/` — PRE_STAGE.md, PREDICT.md,
  LEGA_targets/LEGA_blind/LEGB_targets/LEGB_blind logs, gate_*.log,
  RECEIPT_DONE, snapshots/census_head_469.jsonl (the 469-era baseline
  census; 17 reds).
- `tools/csm/check_targets.py` — FLOOR16 (the 16-row list) + the per-leg
  bars.
- `reports/csm/receipts/council_d7_rescore/chairman.md` — council #36's
  spec (leg bars, kill clause, post-commit flag config, C5/P6 notes).
- `reports/csm/D6_CLOSE_A20.md` + `receipts/d6_probe/CONFIRM_FLIPS.json`
  — the D6 registration (7 holdouts / 16 floor split).
- `plan/drift_log.md` D60–D64 (2181–2360) — the queue history + the
  D64 record of this window.
- `scriptengine/api/context.py` — the two hunks (`_tiered_enabled` ~577,
  `_abilwidth_enabled` ~586, guards ~638/~653; flag defaults "0").

Return: a position on Q1–Q5 with file:line evidence; what you would
rule, what you would pre-register, and what you would NOT do (the
D59/R5 constraints). No engine edits, no GPU, no writes.
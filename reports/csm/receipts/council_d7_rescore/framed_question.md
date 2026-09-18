# Framed question — D7 re-score council (CSM Phase 1, §9a closure loop)

Council #30, 2026-09-18, opencode session (resumed from muse-spark
`ses_f503d5a0`, which hit its model limit mid-plan at 16:24). Sequential
deployment (owner rule 2026-09-08): 5 advisors (A–E) → 5 peer reviewers
(R1–R5) → 1 chairman. All 11 fresh-context, GPU-free, read-only.

## State of play (the evidence pack)

- **CSM position: D7 post-deriv-leg.** HEAD `20d6da4e` = derivation leg
  (verbatim-first + possessive-deferral) committed after the D61 owner-word;
  post-commit gate window `/tmp/d7_gates` (15:46–15:59) ALL PASS (pytest
  1,329+2x / eval jjk 31/31 / span 48,572+probe / canon baseline / p23 469 w/
  4 flips + 0 counter). D6 CLOSED (A20, `9ef7082e`).
- **UNCOMMITTED (D59 rule — never lose):** 44-line narrow legs in
  `scriptengine/api/context.py` — **TIERED** (env-flagged
  `SCRIPTENGINE_TIERED_RECALL=1`; second top_k=30 search, tier-2 chunks
  appended after beam+floor, rendered only from leftover budget; flag off =
  byte-identical) + **ABILWIDTH** (possessive query + `_owner_attribute_hit`
  declared (character, ability-prefix) pair → top_k=30; NOT flagged; targets
  pool-140/358 width holdouts, gold ranks 12–47 cut at 8) + 3 report jsonl
  (`census_widened_csm_results.jsonl`, `reports/index.md`,
  `recall_verbatim.jsonl`). D59 measured tiered at **473** (+4: arcn-02/10,
  org-03, state-08; 0 counter); **ABILWIDTH unmeasured**.
- **Remaining reds 23** = 7 D7 holdouts (chap-01, org-03/05/06, vol-10,
  pool-140/358) + 16 Phase-2 floor (per GATE; post-commit org-05/06/vol-10
  green, so live D7 reds = chap-01, org-03, pool-140/358).
- **Open wall (GATE.md last line):** ranking probe RED — arcb-05 "What
  happens in the Katana Man arc?" gold 4988 never shortlisted; the defect is
  UPSTREAM of ranking (story-page focus resolution), the D7 limit still
  unproven. GATE says: "follow-up is a focus-resolution spike, then the D7
  leg proper."
- **GPU wall:** this opencode session runs ON the owner-manual Qwen 135k
  (pid 1137321, `serve_ctx_135168.sh`, `--max-context 135168
  --kv-capacity 143360`; 26,962 used / 5,142 free MiB) — the ~5.3 GB
  in-process CUDA stack does NOT fit; `:8000` DOWN; `qwen_mode.txt` STALE
  (says mode=off); `tools/csm/d7_gates.sh` restore STALE (hardcoded 65k
  argv). Any `qwen-switch`/kill of Qwen kills the in-flight agent; only a
  detached `setsid nohup` chain survives; owner resumes `opencode -c`.

## The four questions the council must decide

1. **Order** — grade the uncommitted narrow legs NOW (singly: A TIERED=1
   ABILWIDTH=0 → B TIERED=0 ABILWIDTH=1 → C combined, pre-register → run →
   grade, then commit what passes) vs a **focus-resolution spike first**
   (GATE's last line) vs both (spike only if a leg REDs).
2. **ABILWIDTH flag** — ship it **as-is (unflagged)** (B) vs **flag it**
   behind a new `SCRIPTENGINE_ABILWIDTH_RECALL` mirroring `_tiered_enabled`
   (D/R4) vs drop/retire it (E) vs another treatment. Note the standing
   constraints: D59 pre-registration rule (no ex-post retuning), JJK
   baseline untouched, commit only on green + owner word, per-wiki changes
   only in `series/csm/` + `tools/csm/` (the hunk is in shared
   `scriptengine/api/context.py`, JJK-safe by construction via the
   `_owner_attribute_hit` predicate).
3. **GPU path** — (a) `qwen-switch.sh 100k` (sanctioned, but its state
   record is stale and a 135k restore is left manual) vs (b) a
   stop→grade→restore-135k window (restore argv already captured; `d7_gates.sh`
   stale) vs (c) CPU. Hard rules: no CPU job > 15 min; the kill-window must
   not strand the session (the session runs on the server being killed).
4. **The single-subagent task** (owner standing instruction: "then start the
   single-subagent task") — exact scope, pre-checks, pre-registration, pass
   bar, stop conditions, and post-commit flag configuration (defaults, which
   instrument runs flag-ON vs OFF, default-flip decision).

## Standing rules the council must respect

- D59: pre-register changes before measuring; no ex-post retuning.
- The four standing gates (pytest 1,331 pin / eval jjk 31/31 / span-recall
  jjk 48,572 + live probe / canon opm baseline) re-run at fix-class closure.
- JJK baseline-exact is a hard constraint; CSM work lands CSM-centric.
- Commit only on green + owner word. Councils are evidence: a council not on
  disk did not happen.
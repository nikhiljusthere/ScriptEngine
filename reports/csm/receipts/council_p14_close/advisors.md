# CSM P1.4 close council — advisor finals (council #29)

- Date: 2026-09-12, 11:27–11:35 IST
- Method: 5 advisors deployed in parallel (owner directive 2026-09-12: "council's all 5 at a
  time" — the 2-at-a-time limit applies to working subagents only); each fresh-context,
  zero-GPU, read-only; final verdicts 150–300 words each.
- Framed question: `framed_question.md` (this directory).
- Provenance: session transcripts lost in the 2026-09-12 reboot were restored from
  `~/.local/share/opencode/opencode.db`. The finals below are transcribed **verbatim**
  (final-draft answer only; the full thinking traces live in
  `/tmp/opencode/council_close/ad_*.txt`). A cancelled first Contrarian attempt
  (`ad_contrarian_v1.txt`, 4 lines) is discarded.
- Lettering (reviewers reference only these letters):
  A = Outsider, B = Executor, C = First Principles, D = Expansionist, E = Contrarian.
- Post-hoc on-disk verification (parent session, 2026-09-12): A's HOLD grounds #2
  ("irreconcilable arithmetic") and #3 ("200-row leg pre-registered nowhere") are refuted
  on disk — 35/33/58 reconcile in `miss_queue_csm_iter1.jsonl`, and the 200-row held-out
  leg is declared in `heldout_declaration_csm.md` (plan A24/A26). B's commit citation is
  wrong: the ledger's `p14_close_copy.head` is `407c016`, not `af382ee`. E's
  "re-pin 1,321→1,324" contradicts the ledger's "pin (1,321) unchanged" — flagged for the
  chairman. Cross-note and ruling: `reports/csm/COUNCIL_csm_p14_close.md`.

## A — Outsider

Session `ses_f6bcef666ffeghnm` → `/tmp/opencode/council_close/ad_outsider.txt`

**Verdict: HOLD for three on-disk fixes, none requiring a gate re-run; then APPROVE.**

1. **Marker substance.** "Marker present, nothing else" collapses the entire discipline into a boolean: a fresh reader (or a careless process) satisfies it with `touch`. `phase_status.txt` should encode commit `407c016`, the four receipt paths, the bar-audit hash, and the 22 floor rows. Then the gate verifies substance, not intent. One-line fix.
2. **Irreconcilable arithmetic.** 35 open = 22 floor + 13 residual, but the halt meter "counts only 33 fixable rows." 33 derives from no stated split. Reconcile it on disk (gate ledger / drift D24) or the halt condition is unprovable.
3. **The 200-row held-out leg** appears only in question (iv), pre-registered nowhere. Phase 2 commits ~153 GPU-hours; the held-out set (which rows, when generated, who reads it) must be on disk *before* the marker — their own Q1–Q4 item requires the council answer on disk before a GPU day. Pre-registering the bar audit while leaving the extraction's validation instrument unregistered is inconsistent.

**Q1–Q4:** Yes, the caveat is mandatory. Two competing "100%s" now exist: the closure-loop "100%" (which is really halt-at-floor) and the page-campaign 100% (175/537, 32.6%, 52 in-scope remainder). Naming Phase 1 a "100% campaign" while the page campaign sits at 32.6% is exactly the unlabeled conflation a fresh reader trips over. The close doc must state: 100% = [denominator]; 22-floor = halt, not completion; 52-page remainder.

**Page campaign: alongside, not before.** The 22 floor rows are extraction-gated, so P2.3 is the critical path; the 52-page remainder doesn't need extraction and should run in parallel, not serialize ahead of it.

**env-mc finding:** deferral is fine, but record it as an open finding *inside* the marker, state that Phase 2 proceeds on 2/3 live proof, and make explicit that the P1.5 owner session owns the fix — "defer to P1.5" while "B skips P1.5" is ambiguous.

One more: "R-1..R-7 all green" reads as "nothing happened"; one sentence stating iter-1 confirmed the floor without movement would prevent a reader from doubting the campaign did anything.

*Verification note: grounds 1 and the Q1–Q4/page-campaign/env-mc points stand; grounds 2–3
refuted on disk (see header).*

## B — Executor

Session `ses_f6bcef65dffeItRZ` → `/tmp/opencode/council_close/ad_executor.txt`

**APPROVE the close + marker. No HOLD.**

I read the cited receipts: `GATE_LEDGER.json` `p14_close_copy` matches commit `af382ee` (1,321 / 31/31 / 48,572 rc=0 + 398/400 / 236/236); the halt meter FINAL is 22a + 13b (stamped by-design open) + **0c fixable** — halt condition met; the 5.4 re-adjudication receipt (21/21 reds identical, 0 regressions) and close conditions (a)–(e) are all on disk: e411214 in git, D21/D24 in drift_log, bar-audit present with 78/78 verbatim terms, model-free.

**Monday morning is 15 minutes:** `reports/master-work/phase_status.txt` does **not** exist, so the P2 gate ("marker present") is currently FALSE — the close act is exactly: write the `PHASE_A_COMPLETE <ts>` line, write `PHASE_A_COMPLETE_AT_FLOOR.md` (assembling the four receipts, zero new work), one git commit. That's the whole job.

**env-mcp finding: defer to P1.5, don't fix pre-marker.** It's a pre-existing JJK router quirk a month old (`8d07487`); touching JJK routing mid-wave breaks the baseline-freeze rule and forces a four-gate re-run for zero Phase-2 benefit. One line in the close record marking it known-deferred so it doesn't die silently when B skips P1.5.

**Q1–Q4: caveat, not block.** Three lines in the close record: "100%" = 100% of the pre-registered fixable miss classes at the extraction floor, not 100% of pages (CSM 175/537, 32.6%; character pages 175/175). The per-page campaign runs **alongside** P2.1, not before it — model-free question authoring against facts.db (the bar-audit already proved the pattern), zero GPU contention. Holding ~51 GPU-h on a doc job is the only way this question becomes a HOLD.

**P2.1: green light.** Step-0 sanity-100 is the go/no-go, the 200-row held-out leg is declared on disk, and the 22-row floor is exactly what P2.3 exists to close — which is why the close sits at the floor.

*Verification note: the commit citation is wrong (ledger head is `407c016`, not `af382ee`);
"200-row held-out leg is declared on disk" is correct (A24/A26).*

## C — First Principles

Session `ses_f6bcef678ffeuAEy` → `/tmp/opencode/council_close/ad_firstpr.txt`

You're asking the wrong question. "Ratify or hold" treats the marker as the decision. The marker is just a gate; the real question is whether Phase 2's GPU-day buys what we think it does.

The engineering case for close is solid: gates green (1,321 pytest, 31/31 eval, span-recall rc=0, canon 236/236), floor stable (5.4 re-run: 21/21 reds identical, 0 regressions), halt meter counts only the 33 fixable rows. There is no defect to hold for. The env-mc finding is pre-existing (predates the test by a month), a JJK-side routing quirk, pin unchanged — defer to P1.5, log it, and don't let a JJK baseline gap rot silently.

But "100%" is a false claim without its denominator, and that's what Q1–Q4 exist for. JJK's "100%" (prose pass) sits at 90.5% per-page; CSM sits at 32.6% (175/537). Phase 1's "100% at floor" is 100% of a 22-row dimension census, not 100% of the corpus. The 22 floor rows are ~4% of 537 pages. Committing ~51 GPU-hours to close 22 rows before the per-page campaign has established its denominator/plan is mis-ordered.

Rulings:
(i) **APPROVE** the close. But the marker must *carry* the denominator (22-row floor / 60-q census; CSM per-page 32.6% vs JJK 90.5%) — not a bare `PHASE_A_COMPLETE`.
(ii) Yes, the "100%" claim needs a denominator caveat on disk. CSM owes a per-page campaign **alongside** extraction, not before — the 22 rows are extraction-gated so extraction is a hard dependency; but the per-page plan/denominator goes on disk first so the GPU-day is spent correctly.
(iv) "Marker present, nothing else" is the actual defect — it's too coarse. Amend the Phase 2 gate to co-gate on **Q1–Q4 rulings on disk** + **P2.1 step-0 sanity-100 go/no-go**. Scope P2.3 to the 22 rows' dimensions, not open-ended. Define the 200-row held-out leg before any GPU-hour commits.

Tighten the gate; the close itself stands.

## D — Expansionist

Session `ses_f6bcef66fffelzte` → `/tmp/opencode/council_close/ad_expansionist.txt`

**APPROVE the close + marker.** The 22-row "floor" is being read as a ceiling; it isn't. It's a floor by construction — the 5.4 re-adjudication proved the current tooling closes 0/21, so the *only* lever on those 22 rows is Phase 2's extraction campaign. Holding "for fixes" on an extraction-gated floor means holding on a wall that Phase 2 is the designed ram. The marker re-baselines the starting line and unlocks the ~51 GPU-h that actually lifts the floor. If P2.1 works even partially, the documented floor is a *lower bound* on what CSM reaches, not a prediction.

**The upside everyone's missing is the per-page campaign: 32.6%, not 0%.** Q1-Q4 was pre-registered at 0/537; disk now reads 175/537, all 175 character pages at 100%, remainder down to 52. That rewrites Q4 — CSM *owes* the per-page campaign and is already running it. Run it *alongside* Phase 2, not after: extraction lifts the 22-row floor while the per-page campaign compounds coverage toward JJK's 90.5%. Two coverage engines stacking — the compounding asset hiding in the denominator.

**Rulings:** (Q1) YES, widen the census to all 5 in-scope page types — model-free to author, fits the sanity window, converts "100% that isn't JJK's 100%" into a real one. (Q2) size the ability pool to the 376 rows, not 10 questions. (Q3) re-gate the P2.3 null branch on the *widened* census, not the 60-question character census. (Q4) per-page campaign is a real deliverable, already at 32.6%. (Q5) yes — the 90,421-word chapter/episode block (243 sections) needs JJK's in-parts waves; it's the second-largest prose block, currently carried by line-level retrievability alone, which is thin.

**env-mcp: defer to P1.5.** Pre-existing, predates the test by a month, gate-1 pin unchanged, and the MCP bridge is exactly where it gets fixed — 2/3 becomes 3/3. Not a blocker.

**Nothing else blocks Phase 2.** Keep the 200-row held-out leg — that's the actual prize (generalization, not 22 known reds closing). One add: gate the "all dimensions green" claim on the widened census.

## E — Contrarian

Session `ses_f6bcef684ffe1sf6` → `/tmp/opencode/council_close/ad_contrarian.txt`

I read the receipts (GATE_LEDGER `p14_close_copy`, the 58-row queue, the 5.4 re-adjudication, the bar-audit JSON, A20). The numbers check out: 58 = 22 floor + 33 fixable + 3 r1blast stamps, so "33" excludes only the stamps; 398/400 and 236/236 match the run dir. So this is not a HOLD — but I won't approve the close as written. Four flaws:

1. **Q1–Q4 must be on disk, not in the transcript.** The 09-10 pre-registration says no GPU-day until questions 1–4 are "answered on disk with reasons." A council ruling in this transcript is not disk. The approval must be conditioned on `reports/csm/CLOSE_COUNCIL_RULINGS_Q1_Q4.md` committed before or in the marker commit; the marker alone does not satisfy the pre-registration.

2. **A20's "marker present, nothing else" is a self-attestation hole.** A file the campaign itself writes gates a ~51-GPU-hour phase. Amend the gate one line: the marker carries the sha256 of `GATE_LEDGER.json`'s `p14_close_copy` + the floor count (22), and the gate verifies the hash plus the rulings file. Otherwise the Phase-2 gate is ceremonial.

3. **The floor leans on a character-only census.** The 5.4 re-adjudication proves red *stability* (0 closed/0 new over 3 days), not that reds need extraction — the 60-question census contains zero chapter/episode/organization questions. Q3: re-gate the P2.3 null branch on the widened census. Authoring is model-free, so make it a P2.1 entry condition, not a blocker.

4. **env-mcp: don't block the marker, don't be silent.** The Maki→qa defect stays deferred to P1.5, but the marker must list it as a known open finding, and P1.5 needs an exit condition: trio 3/3, gate-1 re-pin 1,321→1,324, ledger update.

State the denominator with live numbers (175/537, 1,260 questions), not the 09-10 0/537 snapshot.

**Verdict: CONDITIONAL APPROVE — marker lands only after items 1–2 are on disk. P2.1 sanity-100 and the 200-row held-out leg stand as planned. No hold.**

*Verification note: the 58-row reconciliation is correct against the queue file; item 4's
"re-pin 1,321→1,324" is unresolved against the ledger (see header) — chairman to rule.*
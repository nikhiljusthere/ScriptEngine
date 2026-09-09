# Council question — CSM 100% campaign audit (2026-09-09)

**Framed by the owner:** "What are we doing wrong? Are we going to fix it faster than JJK? What did we do right with JJK?" — run against the CSM 100% campaign's full history (sessions 09-07 → 09-09), verified in `reports/csm/SESSIONS_REVIEW_2026-09-09.md` (verifier receipts `reports/csm/receipts/sessions_review_verify_A/B/C.md`).

## The decision

Assess the CSM 100% campaign (Chainsaw Man corpus run to the D1–D6
comprehension bar JJK reached) on three questions, then recommend changes to
the remaining path (unit-4 phase close + Phase 2):

1. **What are we doing wrong** — process and technical execution so far
   (A/B bay overhead, 60-min worker timeouts, the gate-3 stale-ESC incident,
   the monitor gap, /tmp state loss on reboot, council cadence vs value, the
   CPU-vs-CUDA :8000 churn, the watch-loops that made the owner close B)?
2. **Can CSM close faster than JJK did?** JJK's page campaign ran 08-19 →
   08-24 (52 clusters) with the final prose-pass state 09-07; JJK's own D6
   comprehension is still open (P0–P5, halt before P6). CSM is ~35 % of JJK's
   line count (panel 17,181 + 200 vs 48,572) and ~54 % of its pages (537 vs
   988). Phase 2 estimates 51 GPU-h for CSM-4 exhaustive tier-1 × 3 doors.
   Is the current pace (3 days → items 0/1/2/3/3b/5/6-instrument done, §9a
   iter 1 ~40 %) ahead of, behind, or on par with what JJK took — and what
   will realistically close CSM (wall-clock + GPU-hours)?
3. **What did JJK do right that we carry into CSM — and what should change?**
   JJK method: "author natural questions; when one fails, diagnose the root
   cause and fix the gap (fix gold / retire cross-page / fix router or
   chunker) — never rephrase to dodge it"; the 545-prose census; the four
   standing gates re-run before any pass is declared done; raw receipts
   (never "100 %" prose); the per-wiki-overrides rule (a fix naming a series
   in a `.py` file is in the wrong place); the D1–D6 definition of 100 %
   comprehension. Which of these is already driving CSM, which is missing,
   and which JJK failure-lesson should change CSM execution?

## Key facts (verifier-confirmed 2026-09-09; receipts cited)

- **CSM state:** items 0 (Wave-0 439→0), 1 (CSM-1 `064093e`), 2 (CSM-2
  `42aa296`), 3 (CSM-3 `f93d396`), 3b (`bc73795`, ratified, ledger #20), 5
  (CSM-5 remainder, `0e0e19e`), 6-instrument (`0e0e19e`) DONE. §9a
  iteration 1 IN PROGRESS: R-1 class closed (`b84445f` + `aef6707`, D18);
  R-2 (qa-passage) + R-3 (roster scoping) drafted, counseled (AMEND×2),
  gates 1–2 + gate-3 offline green, **gate-3 400-probe + gate-4 + re-sweeps +
  the 9-file selective commit still pending** (package staged, uncommitted;
  `/tmp` staging lost in the reboot but all 9 files are on disk uncommitted).
  R-5 (relations router mode) plan drafted; R-6/R-7 hooks recorded. Census:
  39/60 green, 21 red (Phase-1 floor; extraction gate LIVE). Miss queue: 58
  rows (30 fixable / 22 floor / stamped).
- **Phase 2 (not started):** CSM-4 exhaustive tier-1 × 3 doors ≈ 15,400
  sentences ≈ 51 GPU-h; D6 extraction only on red census; CSM-8
  done-declaration; halt before P6.
- **JJK reference:** page campaign 08-19 → 08-24 (52 clusters), final state
  09-07: 893/987 pages (90.5 %), 29,819 active questions, in-scope remainder
  0; gates 31/31 + 48,572/48,572 + canon 10/16·236/236·79.0 %; 545-prose
  census 98.7 % reached. **JJK D6-comprehension is DECLARED DONE**
  (`reports/comprehension/DONE_DECLARATION.md`, 09-07: done-set D1–D10 all
  hold, "the terminal state is done", halted before P6; confirmed by
  `reports/comprehension/GATE.md` line ~697) — the CLAUDE.md "Now active:
  JJK D6-comprehension completion" line is STALE (written before the
  declaration). So CSM is the second corpus run against a bar JJK has
  actually passed, and the speed comparison is legitimate.
- **Process:** 7 CSM councils so far (campaign, 1b-2, csm-3, csm-3b #20,
  unit3-sweep #21, R-1 #22, R-2+R-3 — ledger row pending); A/B bay with the
  `csm-control.sh` machine monitor; 2-parallel subagent waves; 150k dial;
  JJK-100 % invariant (four gates after every engine change — every run so
  far baseline-exact).

## Evidence pack (read the ones your angle needs)

- `reports/csm/SESSIONS_REVIEW_2026-09-09.md` + `reports/csm/receipts/sessions_review_verify_A|B|C.md`
- `plan/CSM_2PHASE_PLAN.md`, `plan/CSM_WAVE2_RESUME.md` (plan, invariants, council trigger)
- `reports/master-work/work_log.md` (tail ~40 lines) + `plan/state.md` (tail ~30 lines)
- `reports/csm/COUNCIL_unit3_sweep.md` (how a §3 council ran + verdict)
- `reports/page-campaign/PROSE_PASS_FINAL.md` (what JJK achieved + method)
- `reports/comprehension/COMPREHENSION_REMAINDER.md` (JJK D6 remainder)
- git log: `git log --oneline --since=2026-09-07 | wc -l` etc. (commit cadence)

## Rules for every member

Zero-GPU, read-only (you may write ONLY your assigned output file), every
load-bearing claim verified against disk before you record it (if you cannot
verify it, say so — never assume). One agent at a time (owner rule
2026-09-08).
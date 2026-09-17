# P2.5 done-declaration audit — CSM (re-assertion, post-FAIL8 + D36 window)

2026-09-17. Read-only audit of `plan/CSM_2PHASE_PLAN.md` P2.5-5 (A24,
council #26) items (a)–(h) against on-disk evidence. Template: JJK
`DONE_DECLARATION.md`. Verdicts are artifact-path bound: PASS names the
artifact; PENDING/FAIL names what is missing.

Context re-assertion: the prior P2.5 done-declaration predates the FAIL8
close (council #33, `reports/csm/COUNCIL_csm_fail8.md`) and the D36
model-window commit (drift D36). Both markers are already on disk; what
was never written is this formal (a)–(h) audit — the PHASE_B_COMPLETE
caveat in `phase_status.txt` says so explicitly.

## Verdict table

| # | P2.5 item (plan L382–402) | Verdict | Artifact |
|---|---|---|---|
| (a) | P2.1 measured s/probe + per-door raws + panel hash in GATE.md, incl. 200-row held-out out-of-sample | **PASS** | `reports/csm/GATE.md` "P2.1 step-0 measured s/probe" (qa 0.506 s → 2.8 h panel; narrative 0.023 → 6.5 m; roster 0.044 → 12.6 m; auto 0.192 → 11.5 h) + A17 floor policy + A26 hashes (panel `cf72135f…` / held-out `604dc8ca…`; ledger `sweep_qa_e3d73720.jsonl`) + full-sweep block: qa 16,920/17,181 = 98.48 % PASS (≥ 97.5 % band), narrative 1,846 = 10.74 % documented floor, roster 133 = 0.77 %, auto 2,651 = 15.43 % descriptive raw, **held-out 28/200 = 14.0 %**; 5 ledgers + `reports/csm/p21_sweep_2026-09-17/REPORT.md` + `misses_qa.jsonl` (261) |
| (b) | P2.4 receipt (pass bar met: every tag resolves chapter/episode, zero unverified) | **PASS** | drift D31: `script-gen "Bat Devil arc"` → `scripts output/Video 3 - Bat Devil arc/Script/Bat Devil arc.md` (+ `-clean.md`, both on disk, gitignored — the D31 log line is the receipt); 25 tags / 8 distinct, all verified against the raw wiki; 6,333 words (6000 ±10 % band) |
| (c) | Triage log for every residual | **PASS** | `reports/csm/p23_red_triage.md` (69 widened reds: 37 box-class wrong-page + 27 width/enumeration + 5 state-over-time content; 15 bar-audit reds; R-9 pre-analysis) + `reports/csm/p21_sweep_2026-09-17/triage/` (qa 261 = 237 both-miss + 24 auto-only; narrative/roster floor samples per P-4) + D36 `page_run.tsv` (339 rc=0 / 135 rc=2 known-class, per P-4 scope) |
| (d) | Four pilot numbers named per campaign-council item 8 | **PASS** (2026-09-18, council #34 step 1) | All four on disk: #1 T0 emergence 843 vs ~535 and #2 T0 survival 843/843 = 100 % (`reports/csm/t0_pilot_csm.json` + `T0_PILOT_CSM.md`); **#3 = 5 submitted (G-CSM-1..4 + G-CSM-7), all closed, 0 open** and **#4 = 27** (JJK 2 / off-campaign 15 / CSM 10) — "four pilot numbers" block in `reports/csm/GATE.md` (hard-gate ruling: floor not moving, gate does not fire) |
| (e) | JJK baseline diff-empty against the NAMED 2026-09-08/09 re-baseline (1,303+2xp = 1,305 collected; eval 31/31; span 48,572 + ≥390/400; canon 236/236 @ 79.0 %) | **PASS (noted)** | D36 window @ `f49e0d2`: all four gates re-run green — `reports/csm/receipts/model_window_d36/state.*` (eval rc=0; span-recall offline 48,572 + 400-probe rc=0, 400/400 ≥ 390 bar; canon rc=0 236/236 @ 79.0 %; coverage rc=0; pytest first-pass rc=1 → post-patch 1,329p+2xp rc=0). Note: plan's named 1,305 is superseded by the R-8 window (2026-09-17, `4b60043`): +10 router tests → gate-1 pin **1,331** (`reports/csm/GATE_LEDGER.json`); known +N delta does not re-run gates (Ruling 5e). No separate "diff-empty" artifact exists — the window state files are the record |
| (f) | P2.3 null-branch evidence (P2.3b receipt or re-verified dimension census) | **PASS** | P2.3 fired (de-contingented, not void): P-5 pointer grader over the widened 486-item bank — 417/486 MECH_GREEN, 69 reds triaged; grader `tools/csm/p23_grader.py`, results committed `3d43a21`; D36 re-runs the 486 bank and reproduces 417/486 exactly. Re-verified dimension census: GATE.md 5.4 re-adjudication (2026-09-12): 21/21 reds identical, 0 closed 0 new; queue 35 = 22+10+3 |
| (g) | Bar-audit verdict (P2.2/A21) | **PASS** | GATE.md P2.2/P2.3 section: pre-fix bar audit on the qa control arm **11/26** (P1.4 bar not met pre-fix); auto door 14/26 (R-9-contingent supplement, P-3); post-fix D34: 2/15 hint, 5/13 campaign — the 8 residual bar reds are descriptive control-arm evidence, not campaign misses (`bar_audit_p14_results_hints*.jsonl`). Council #33 closed R-9 as **deferred / no-fire** (firing condition unmet; no `router.py` change owed) |
| (h) | New `PHASE_B_COMPLETE <ts>` marker + halt-before-P6 recorded | **PASS** | `reports/master-work/phase_status.txt` L20: `PHASE_B_COMPLETE 2026-09-17T22:02:05+05:30` (tree `2419a01`, gates @ `f49e0d2`); caveats record the 135 known-class residuals + 22 floor lines and that the P2.5 formal (a)–(h) audit is not re-asserted by the marker. Halt before P6: trunk stays at P6-not-started (cross-corpus `plan/Plan_to_perfection.md` §7 waits on Phase-1 close) |

Score: 8/8 PASS (one with note) — (d) #3/#4 on disk (2026-09-18, council #34 step 1); the formal re-assertion (recipe step 2) lands at sequence step 4 @ pin 1,331.

## Marker-eligibility (STEP 3)

**The done markers are already on disk and their precondition was met:
NO new marker is owed, and the 22 floor rows are not a block — they are
the floor.** A20 (plan L197–202) writes `PHASE_A_COMPLETE` *when the miss
queue sits at its documented floor*; a regression halt (not the floor)
voids the precondition. On disk: `PHASE_A_COMPLETE 2026-09-12T11:51:10+05:30`
(tree `407c016`, with substance) and `PHASE_B_COMPLETE 2026-09-17T22:02:05+05:30`
(tree `2419a01`), both in `reports/master-work/phase_status.txt`. The
frozen queue (`reports/csm/miss_queue_csm_iter1.jsonl`, 58 rows) sits at
the documented floor: 23 closed (P1 fixables), 35 open = **22
extraction-gated** (21 `csm-dim-*` + `csm-char-04` R-7x) + 13 R-4/R-2
(D25's "35 = 22+10+3" arithmetic). The formal P2.5 done-declaration (this file) can now be re-asserted: (d) #3
new-numbered-gaps (5 submitted, all closed, 0 open) and #4 human-round-trips
(27) are on disk in the `GATE.md` "four pilot numbers" block (2026-09-18,
council #34 step 1). The remaining caveat: full 100 % content completion
(all 58 rows closed) stays unreachable until Phase-2 D6 extraction closes
the 22 floor rows (plan L417).

## Re-assertion recipe (≤4)

1. **Produce the two missing item-8 numbers.** #3 new numbered gaps:
   count the CSM campaign's filed numbered gaps (council/drift records;
   "0 filed" is a legitimate value) and #4 human round-trips: count
   owner-directed interventions across drift D1–D36. Append a named
   "four pilot numbers" block to `reports/csm/GATE.md` with sources.
2. **Re-assert (e) against the current pin.** Cite gate-1 pin 1,331
   (`GATE_LEDGER.json`, R-8 window `4b60043`) + the D36 window receipts
   (`reports/csm/receipts/model_window_d36/state.*`) as the JJK
   baseline diff-empty record — the plan's 1,305 figure is stale by the
   known +10 router tests.
3. **Leave both markers as written** (A @ `407c016`, B @ `2419a01`);
   the re-asserted declaration references them + the (a)–(h) artifacts
   above, and records this audit's file path in the drift log.
4. **Only for a full 58/58 close:** run the Phase-2 P2.3 D6 extraction
   leg (21-red class ∪ pre-registered green sample) + the pre-registered
   extraction-pass test (400-gate + red dimensions green + 200-row
   held-out), then a new marker — out of scope for this re-assertion.
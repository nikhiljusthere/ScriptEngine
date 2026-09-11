# R-7 close council — chairman synthesis (slim light-form, 5th member)

Council: CSM Phase 1, R-7 `identity_fields` class close. Owner 2026-09-12
directive (council after every major step). Members: A correctness/retrieval,
B queue/governance, C regression-risk, D process/leak-check (verdicts:
`advisors.md`, fresh-context, read-only, zero-GPU), + this chairman. All
records re-verified against disk before recording (git log/status, run dir,
GATE.md, GATE_LEDGER.json, red_list, HALT_METER_P13_DRAFT, COUNCIL_HISTORY,
CLAUDE.md).

## VERDICT: SHIP-AMENDED

Ratify (a) the R-7 class CLOSE at HEAD `81df799` (4/4 gate window GREEN +
class re-sweep GREEN, **zero rows closed by design**, `rows_closed_this_unit: 0`),
(b) the csm-char-04 floor classification **(a)=22 / (b)=13 / (c)=0, halt
residual 35 open**, and (c) the stamp + commit plan below — **with amendments
A1–A7 enforced at the close commit**. No advisor objects to the close itself;
every objection is record-hygiene or a deferral, none touches the engine
(`60e568f` is generation-only: `config.py` `identity_fields()` +
`eval/page_gen.py` merge + the 61-key `series/csm/overrides.yaml` map; returns
`{}` for every series lacking the key → identity no-op for JJK/OPM, so no
regression path escapes the four gates).

Rationale per charge:
- **(a) CLOSE — ratified.** Gate numbers are baseline-exact (gate-2 31/31 =
  GATE.md L13; gate-3 48,572 rc=0 + 398/400 99.5% ≥ 97.5% floor, bit-identical
  to the R-6 window; gate-4 236/236·10/16·79.0% = the re-baselined receipt;
  gate-1 1,321 fully accounted 1,303→1,305 (R-2/R-3) →1,318 (R-6) →1,321
  (R-7) with the 3 env-mcp failures documented + 2 xpassed). Class re-sweep
  GREEN: r1blast-tokyo qa→roster served all 5 divisions, 0 new misses
  (pinned shape `tests/test_csm_router_count_rule.py`); OPM pair held by
  gate-4 baseline identity (direct probes skipped — the R-7 hunk is CSM-scoped
  and cannot affect OPM; the stamp must say so, A#3); zero new misses, zero
  new queue rows. Zero rows close because the gated hunk is generation-only
  and the R-7x row's close lever (abilities extraction) sits on the 5.4 gate,
  LIVE, Phase 2 — closing R-7 with 0 rows is the designed outcome, not a gap.
- **(b) (a)=22/(b)=13/(c)=0 — ratified.** csm-char-04 carries
  `ruling: "floor"` on disk ("abilities extraction track; 5.4 gate LIVE");
  the re-sweep left it OPEN as floor, inside the 22-floor set (21 D6-extraction
  + this one, council #25 A10). The DRAFT meter's (c) bucketing + "if no HIT,
  blocks the halt" fallback is **overridden** (B#2): re-issue at
  (a)=22/(b)=13/(c)=0. B's A11 gap is real and must be closed at the close
  commit (A2 below).
- **(c) stamp + commit plan — ratified as amended** (A1–A7; D's 12-path list
  + 3 council artifacts + 1 CLAUDE.md line = 16 paths, then the doc-only
  ledger-fill follow-up; exclusion list confirmed against `git status`).

## AMENDMENT LIST (enforced at the R-7 close commit)

- **A1 [C#1, C#2, D#3] — GATE.md, one edit.** Live-state block → "GREEN at the
  R-7 `identity_fields` pass (P1.2, 2026-09-12)" with the four numbers
  (pytest **1,321** = 1,316 passed + 3 env-mcp + 2 xpassed; eval 31/31;
  span-recall 48,572 rc=0 + 398/400 (99.5%); canon 236/236·10/16·79.0%),
  "csm-char-04 stays open as the floor (open 35 / closed 23 / total 58)",
  raw-receipt pointers — **and the L12 pin 1,305 → 1,321** (stale since R-5;
  fully accounted above).
- **A2 [B#1, B#2, D#1] — re-issue `HALT_METER_P13.md` at (a)=22/(b)=13/(c)=0.**
  csm-char-04 moves (c)→(a) (row stays OPEN as floor); residual open = **35**
  (the DRAFT's L114 "35 − 1 = 34" line is superseded — no row closed this
  class); **stamp the 10 invariant/residual rows by-design open** (csmdoor-01,
  csmd5-01/02/03/05/06, gate400-320, red-R-4, csm-char-03, csm-set-02) so the
  33-fixable meter's halt trip counts them as satisfied-by-stamp — this
  closes A11's gap where a literal reading counts the 10 (A10 puts them in
  the 33 fixable) and blocks the halt forever. Commit DRAFT + final (D#9-10).
- **A3 [C#1, A#4(2)] — GATE_LEDGER.json re-land.** New `last_green`: unit
  "P1.2 (§9a iter-1 R-7 identity_fields)", fix_classes [R-7], fixes_commit
  `60e568f`, receipts_commit left for the doc-only follow-up (R-6 pattern
  `36e59c1`), gates 1,321 / 31-31 / 48,572+398-400 (99.5%) / 236-236·10-16·79.0%,
  report `reports/2026-09-11-2135/`, class_sweeps.r7_identity_fields,
  queue_stamps **rows_closed_this_unit 0** (23 closed / 35 open / 58,
  csm-char-04 floor); `reboot_rule` re-anchored to the R-7 close commit and
  its floor wording updated to "the **22** extraction-gated floor rows (21
  D6-extraction + csm-char-04)" — the 22-row reading lands in the ledger +
  GATE.md now, **before P1.4 stamps anything** (A#4(2)).
- **A4 [C#3] — env-mcp live-API caveat.** The 3 env-mcp research tests never
  ran green in this window (W1 with :8000 down by design; W2 re-ran live
  probe + canon only), so "4/4 green" carries a standing live-API gap.
  Enforce: carry the caveat in all three records (GATE.md live state,
  GATE_LEDGER note, HALT_METER_P13 header); the trio gets its live proof in
  **P1.4's four-gate copy** (:8000 up) — no new GPU interaction in a doc-only
  close commit (chairman's call between C's two options).
- **A5 [B#3, A#4(2)] — floor-list citation.** GATE.md L38-41's floor list
  doesn't name csm-char-03/csm-set-02/red-R-4; the re-issued meter + GATE.md
  live state cite the red_list close notes (R-2 close note queue L22; R-3
  close note) as governing for the 10 rows, and name csm-char-04 as the 22nd
  extraction-gated row.
- **A6 [A#1] — T0/T1 generation-side pilot: DEFERRED to P1.4 (not in R-7
  scope).** The class-closure criterion (own-class re-sweep: own-new-row HIT +
  zero new misses) is met; the 61-key map's end-to-end payoff is verified
  only by `test_r7_identity_fields.py` + `test_page_gen.py`. Add a CSM
  page-gen smoke to the P1.4 preconditions; record the deferral in the close
  receipt.
- **A7 [chairman; missed by all four] — CLAUDE.md:354 one-line pin fix.** The
  root doc's gate-1 pin line still reads "1,305 (the current gate-1 pin)" and
  goes stale the moment A1 moves GATE.md to 1,321 (second time this pattern
  bit: C3 hygiene fixed 1,254→1,305). Add exactly that one line (1,305 →
  1,321 + the accounting note) to the close commit; no other CLAUDE.md
  changes.

**Explicitly deferred to P1.4 (not executed at the close commit):** the 5.4
re-adjudication of csm-char-04 (row ruling stays `floor`; P1.4 owes the
per-class census re-adjudication with the 22-row (a) floor set pre-registered
on disk — D#4a); `PHASE_A_COMPLETE_AT_FLOOR.md` — the halt condition is MET
after R-7 (all 7 classes closed, meter (c)=0, open 35 = 22+13+0) but the
marker is written only after P1.4's one 4-gate copy + 5.4 re-adjudication +
bar-audit + close conditions (a)–(e), campaign-todos sync at
`plan/CSM_2PHASE_PLAN.md:190` (D#4b); the P2.2 bar-audit (shape pre-registered:
3–5 cases per census class, fresh-context mechanical grader, pre-marker;
per-class case files don't exist yet — authoring + running is P1.4 close
condition (d), D#4c); the T0/T1 pilot (A6); the env-mcp trio live run (A4);
A#4(3) "no CSM-specific standing gate" is a design property (the four standing
gates are the JJK baseline; CSM is live-exercised via probes + re-sweeps),
noted as a residual, no action owed.

## FINAL HALT CONDITION (supersedes the DRAFT's; B's Q3 wording, 10-row gap corrected)

Phase 1 halts when every non-floor, non-extraction fix-class (R-1…R-7) is
green, the 33-fixable meter reads 33/33 (the 10 documented residual rows
stamped by-design open **at the R-7 close per A2**, not an open fix), and the
queue's remaining 35 open rows are all extraction-gated floor (22, incl.
csm-char-04), stamped (3 r1blast-*), or invariant/residual (the same 10) —
then B writes `reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` and stops.

## FINAL STAMP + COMMIT LIST

**Stamp edits** (per D#1-6, amended): (1) `miss_queue_csm_iter1.jsonl` —
append re-probe outcome to the three r1blast-* `note` fields (tokyo:
qa→roster served all 5 divisions, 0 new misses; blizzard/marines: **direct
probes skipped** — held by gate-4 baseline identity 236/236·10/16·79.0%,
R-7 hunk CSM-scoped; ref `receipts/r7_class_resweep.md §2`); csm-char-04 NO
edit (floor-ruling note already on disk). (2) `red_list_csm.md` — stamp the
Addendum L174-176 "Re-probe after R-7's key-map widening lands" → done,
pointer to re-sweep §2 (R-2/R-3 precedent: no section → no section stamp).
(3) `GATE_LEDGER.json` per A3. (4) `plan/drift_log.md` — D22
(What/Gates/Stamps/Commit, D21 format). (5) `GATE.md` per A1 (+A5). (6)
`work_log.md` B-append "ACT gates+close" + "ACT commit" lines (R-5/R-6
pattern — the W1-prep ANNOUNCE exists, the GREEN/close/commit lines are the
leak D#3 named). Plus: re-issued `HALT_METER_P13.md` (+ committed DRAFT) per
A2, and the gate-3 probe ledger `recall_verbatim.jsonl` (+400 R-7 rows; R-6
committed its own).

**CLOSE COMMIT = 16 paths** (path-limited `git add` by named paths;
`git add .` banned; D's 12 + 3 council artifacts + CLAUDE.md):

```
git add reports/csm/receipts/r7_gate_window.md
        reports/csm/receipts/r7_class_resweep.md
        reports/csm/miss_queue_csm_iter1.jsonl
        reports/csm/red_list_csm.md
        reports/csm/GATE_LEDGER.json
        reports/csm/GATE.md
        plan/drift_log.md
        reports/master-work/work_log.md
        reports/csm/HALT_METER_P13.md
        reports/csm/HALT_METER_P13_DRAFT.md
        reports/2026-09-11-2135
        reports/span-recall/jjk/recall_verbatim.jsonl
        reports/csm/receipts/r7_council/advisors.md
        reports/csm/receipts/r7_council/chairman.md
        reports/comprehension/COUNCIL_HISTORY.md
        CLAUDE.md
```

The run dir commits **whole** (R-6 precedent, no pruning): REPORT.md +
canon_scores{,_diagnosis,_intruders}.json + eval.json + run.json **+
answers.md** (R-7's new file — verified on disk). **Doc-only follow-up
commit:** fill `GATE_LEDGER.json` `receipts_commit` = the close-commit hash
(R-6 pattern `36e59c1`; the follow-up passes the reboot rule). **EXCLUDE
(confirmed against `git status`):** `plan/SWITCHPOINT.md` (M, A-side),
`reports/index.md` (M, A-side), `series/jjk/audit/eval.json` (untracked
generated), and the A-side/scratch untracked set: `E:\Personal\Plot Works/`,
`sample scripts/*.md` (2 files), `plan/COMPACTION_PROOF.md`,
`reports/master-work/{GPU_LIVE1_REPORT.md, STOP, TRANSCRIPT_JOB.md,
gpu_handoff_state/, interventions.jsonl, shell_log.jsonl}`.

**COUNCIL_HISTORY row (ledger = `reports/comprehension/COUNCIL_HISTORY.md`,
newest-first; top is #27 → this row is #28):**

```
| 28 | `reports/csm/receipts/r7_council/` (CSM campaign; slim light-form: 4 advisors A correctness / B governance / C regression / D process + chairman, sequential, zero-GPU, read-only, per the owner 2026-09-12 after-every-major-step directive) | csm-r7-identity-fields-close (2026-09-12): ratify the R-7 class CLOSE at HEAD `81df799` (gate window 4/4 GREEN: pytest 1,321 = 1,316 + 3 env-mcp + 2 xpassed; eval jjk 31/31; span-recall 48,572 rc=0 + 398/400 (99.5%); canon opm 236/236·10/16·79.0% — window `reports/csm/receipts/r7_gate_window.md`) + R-7 class re-sweep GREEN (`reports/csm/receipts/r7_class_resweep.md`: r1blast-tokyo qa→roster 5/5, 0 new misses; OPM pair by gate-4 baseline identity; csm-char-04 stays OPEN as floor) — verdict: **SHIP-AMENDED**: (a) CLOSE ratified with rows_closed_this_unit: 0 by design (generation-only hunk; abilities close lever = 5.4 gate, Phase 2); (b) csm-char-04 classified (a)=22/(b)=13/(c)=0, halt residual 35 (DRAFT's (c) bucketing + "blocks the halt" fallback overridden); (c) 16-path close commit + doc-only ledger-fill follow-up, exclusion list confirmed. Amendments A1–A7: (A1) GATE.md live-state → R-7 window + L12 pin 1,305→**1,321**; (A2) re-issue HALT_METER_P13 at (a)=22/(b)=13/(c)=0, residual 35 not the DRAFT's 34, **10 residual rows stamped by-design open** (closes the A11 10-row gap); (A3) GATE_LEDGER last_green re-land (R-7, fixes `60e568f`, receipts_commit in the follow-up, rows_closed 0, reboot_rule re-anchored, floor wording 21→**22**); (A4) env-mcp live-API caveat carried in GATE.md/ledger/meter, trio live-run owed at the P1.4 four-gate copy; (A5) floor-list citation (csm-char-03/csm-set-02/red-R-4 via red_list close notes; csm-char-04 named as the 22nd floor row); (A6) T0/T1 generation pilot deferred to P1.4 (closure criterion already met by the re-sweep); (A7) CLAUDE.md:354 gate-1 pin line 1,305→1,321 (missed by all four advisors). Deferred to P1.4: 5.4 re-adjudication of csm-char-04, PHASE_A_COMPLETE_AT_FLOOR.md (only after P1.4's 4-gate copy + 5.4 + bar-audit + close conditions a–e, `plan/CSM_2PHASE_PLAN.md:190`), P2.2 bar-audit case authoring + run, T0/T1 pilot, env-mcp trio. Final halt condition: Phase 1 halts when every non-floor, non-extraction fix-class (R-1…R-7) is green, the 33-fixable meter reads 33/33 (the 10 residual rows stamped by-design open), and the 35 open rows are all extraction-gated floor (22, incl. csm-char-04) / stamped (3 r1blast-*) / invariant-residual (10) — then B writes `reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` and stops. |
```

## ALL-FOUR-MISSED CHECK

Checked the five candidates: (1) env-mcp trio live-API gap — **C#3** (→ A4);
(2) GATE.md L12 pin — **C#1 + D#3** (→ A1); (3) work_log B-append — **D Q1/D
Q3** (leak list, stamp 6); (4) run-dir answers.md — **D Q2** ("R-7 adds
answers.md — no pruning"; verified on disk); (5) switchpoint/scratch
exclusion list — **D Q2** (verified against `git status`: the M files and
untracked set match D's list exactly). **Findings:** (i) **CLAUDE.md:354
gate-1 pin line (1,305)** — stale once GATE.md moves to 1,321; no advisor
named CLAUDE.md (the C3 doc-hygiene precedent did it for 1,254→1,305) → A7;
(ii) **the DRAFT meter's L114 residual line "35 − 1 = 34"** — must be
superseded to 35 in the re-issued meter (mechanical consequence of A2,
unstated by any advisor). Everything else on the checklist was covered.
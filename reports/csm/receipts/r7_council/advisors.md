# R-7 close council — advisor verdicts (slim light-form, 4 members, owner 2026-09-12 directive)

Council: CSM Phase 1, R-7 identity_fields class close (gate window 4/4 GREEN at
`81df799` + class re-sweep GREEN). Members: A correctness/retrieval, B
queue/governance, C regression-risk, D process/leak-check. All fresh-context,
read-only, zero-GPU. Chairman follows (`chairman.md`).

## Advisor A (correctness/retrieval)

- Q1 GREEN / class CLOSES (with floor residual): YES. Gates 4/4 on own
  thresholds (1,321 = 1,316 + 3 documented env-mcp + 2 xpassed; 31/31;
  48,572 rc=0 + 398/400 ≥ 97.5%; 236/236 · 10/16 · 79.0%). Bit-identical
  argument holds: `60e568f` touches only `config.py` (new
  `identity_fields()`), `eval/page_gen.py` (import + 2-line merge),
  `overrides.yaml` (new top-level key), tests; `identity_fields` imported
  only by `eval/page_gen.py` — no `retrieve/`/`api/`/`index/` reference.
- Q2 FLOOR classification CORRECT: queue row carries `ruling: "floor"` +
  "abilities extraction track; 5.4 gate LIVE"; `fix_class: R-7x` records
  which class examined it, `ruling` records where it closes; council #25's
  22-floor set (21 D6-extraction + this) matches; CSM-1b-2 ruling
  (prompt correctly returned []; gap is the retrieval/prose leg, Phase-2
  only). Re-adjudication deferred to the 5.4 gate at P1.4.
- Q3 r1blast-tokyo SATISFIES zero-new-misses (auto→roster 5/5 = the pinned
  shape in `tests/test_csm_router_count_rule.py`), CAVEAT: the OPM pair
  (r1blast-blizzard/marines) was NOT directly probed — their zero-new-misses
  rests on gate-4 baseline-identity (236/236·10/16·79.0% exactly equal to the
  re-baselined receipt), not per-row probes.
- Q4 Left behind: (1) no generation-side T0/T1 pilot re-run in this window —
  the 61-key map's end-to-end payoff is verified only by
  `test_r7_identity_fields.py` + `test_page_gen.py`; (2) GATE.md L38-39 +
  LEDGER reboot rule say "21 D6 + invariant floor rows" — the 22nd
  extraction-gated row (csm-char-04) appears only in the re-sweep receipt +
  the still-DRAFT halt meter; GATE.md/LEDGER need the 22-row reading
  recorded before P1.4 stamps anything; (3) no CSM-specific standing gate in
  the four — CSM live-exercised only via the two probes.
- Objections: (1) if a T0/T1 pilot re-run is in scope for R-7 it was not
  run; (2) the halt-rule text and the 22-floor set disagree by one row — fix
  the record at P1.4; (3) OPM r1blast proof is aggregate baseline-identity —
  the close record should say the direct probes were skipped and why.

## Advisor B (queue/governance)

- Q1 Resweep reading correct: **(a)=22 / (b)=13 / (c)=0, halt residual 35**.
  csm-char-04 is inside the 22-floor set, not a (c) row. Governing text: A10
  ("58 = 33 fixable + 22 extraction-gated floor + 3 stamped"), A11 (meter
  counts only the 33 fixable; 22 floor + 3 stamped excluded), council #24
  note 9 (22 = 21 D6 + 1 extraction-gated = csm-char-04), queue row
  `ruling:"floor"`, GATE.md L38-39. When they disagree, the ratified plan
  (A10/A11) + frozen queue ruling govern; the draft meter subordinates itself
  ("Status: DRAFT — not a stamp; re-check at the R-7 close").
- Q2 The 10 rows (csmdoor-01, csmd5-01/02/03/05/06, gate400-320, red-R-4,
  csm-char-03, csm-set-02) are legitimately (b) in substance, BUT A11 has a
  gap: A10's accounting puts them in the 33 fixable (they are not in the 22
  floor + 3 stamped), so a literal A11 reading counts them and blocks the
  halt. The halt record must stamp the 10 as by-design open (or reclassify
  them into the floor set).
- Q3 Halt condition P1.3 records: "Phase 1 halts when every non-floor,
  non-extraction fix-class (R-1…R-7) is green, the 33-fixable meter reads
  33/33 (the 10 documented residual rows stamped by-design open), and the
  queue's remaining 35 open rows are all extraction-gated floor (22, incl.
  csm-char-04), stamped (3 r1blast-*), or invariant/residual (10) — B then
  writes `reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` and stops."
- Q4 Governance debts BEFORE the R-7 close stamp: (1) queue row notes —
  r1blast-tokyo/blizzard/marines append re-probe stamps; csm-char-04 needs
  no edit (floor-ruling note already on disk); (2) red_list stamp — R-7 has
  no section; stamp the Addendum L174-176 pre-registration (done → pointer
  to re-sweep §2), matching R-2/R-3 precedent (no section → no section
  stamp); (3) GATE_LEDGER new last_green row (81df799, R-7, queue_stamps
  open 35/closed 23, csm-char-04 floor); (4) drift D22; (5) GATE.md live
  line → R-7 window.
- Objections: (1) A11's exclusion omits the 10 residual rows — halt record
  must stamp them by-design open or amend the meter's scope; (2) the draft's
  (c) bucketing + "if no HIT, blocks the halt" fallback is overridden —
  re-issue the meter as `HALT_METER_P13.md` at (a)=22/(b)=13/(c)=0; (3)
  GATE.md L38-41's floor list doesn't name csm-char-03/csm-set-02/red-R-4 —
  the halt record should extend the floor list or cite the red_list close
  notes as governing.

## Advisor C (regression-risk)

- Q1 Non-regressing: YES. gate-2 31/31 = GATE.md L13 exact; gate-4
  236/236 + 79.0% + 0 confident-wrong = L17-18 exact; gate-3 offline 48,572
  rc=0 = L14, probe 398/400 (99.5%) ≥ the L15-16 97.5% floor — and 398/400 is
  bit-identical to the R-6 window (stable margin, not noise). Caveat: the
  L12 gate-1 pin (1,305) is STALE; actual 1,321 is fully accounted by
  documented test additions (1,303→1,305 R-2/R-3, →1,318 R-6, →1,321 R-7).
- Q2 The env-mcp trio is the SAME 3 tests in the R-5/R-6/R-7 windows (stable,
  documented; R-7 touches no api/mcp code) — low risk. Pin integrity erodes
  by two mechanisms: the L12 pin silently drifts (1,305 vs 1,321); and the
  trio never ran green in this window (W1 with :8000 down by design; W2 only
  re-ran live probe + canon), so gate-1 "green" carries a standing live-API
  gap.
- Q3 No JJK/OPM regression path escapes the gates: `identity_fields()`
  returns `{}` for any series lacking the key (only `series/csm/overrides.yaml`
  defines it) → the `_identity_builder` merge is an identity no-op for
  JJK/OPM. Sole theoretical gap: the builder is exercised only by the
  `page-gen` CLI (cli.py:2333), not in the four gates — but a no-op merge has
  no behavior to regress, and gate-1's two R-7 test files pin the merge.
- Q4 Safe to leave the 10 rows open: hunk is generation-only; all 10 rows
  are retrieval/chunking/canon-side (disjoint code paths); the re-sweep found
  zero new misses and zero new queue rows, so closing R-7 changes no counts.
- Objections: (1) GATE_LEDGER last_green still R-6 (`1e00ac1`) — the R-7
  green at `81df799` was never re-landed; reboot rule (a)+(b) currently forces
  a full 4-gate re-run on any reboot; re-land to the R-7 window; (2) GATE.md
  L20-26 live state still says GREEN at R-6 with 1,318 — stale; (3) "4/4
  green" excludes the 3 live-API research tests (skipped W1, not re-run W2) —
  the claim should carry the env-mcp caveat or the trio should run once with
  :8000 up.

## Advisor D (process/leak-check)

- Q1 STAMP LIST (in order): (1) `miss_queue_csm_iter1.jsonl` — append
  re-probe outcome to the three r1blast-* `note` fields (tokyo qa→roster
  served all 5 divisions, 0 new misses; blizzard/marines held by canon
  236/236; ref `receipts/r7_class_resweep.md §2`); csm-char-04 needs NO edit
  (floor-ruling note already on disk, committed). (2) `red_list_csm.md` —
  stamp the Addendum L174-176 pre-registration ("Re-probe after R-7's
  key-map widening lands" → done, pointer to re-sweep §2); matches R-2/R-3
  precedent (no section → no section stamp). (3) `GATE_LEDGER.json` — new
  `last_green`: unit "P1.2 (§9a iter-1 R-7 identity_fields)",
  fix_classes [R-7], fixes_commit `60e568f`, receipts_commit filled in a
  doc-only follow-up (R-6 pattern `36e59c1`); gates 1,321 / 31-31 /
  48,572+398-400 (99.5%) / 236-236·10-16·79.0%; report
  `reports/2026-09-11-2135/`; class_sweeps.r7_identity_fields;
  queue_stamps rows_closed_this_unit 0 (23 closed / 35 open / 58).
  (4) `plan/drift_log.md` — D22 (What/Gates/Stamps/Commit, D21 format).
  (5) `reports/csm/GATE.md` — live-state block → "GREEN at the R-7
  identity_fields pass (P1.2, 2026-09-12)" with the four numbers +
  "csm-char-04 stays open as the floor (open 35 / closed 23 / total 58)" +
  raw-receipt pointers. (6) `reports/master-work/work_log.md` — B-append
  "ACT gates+close" + "ACT commit" lines (R-5/R-6 pattern). Plus: re-issue
  `HALT_METER_P13.md` from the DRAFT (its header obliges re-issue at the
  R-7 close; commit DRAFT + final) and
  `reports/span-recall/jjk/recall_verbatim.jsonl` (+400-line R-7 probe
  ledger; R-6 committed its own).
- Q2 CLOSE COMMIT = 12 paths, then a 1-file doc-only ledger-fill:
  `git add reports/csm/receipts/r7_gate_window.md
  reports/csm/receipts/r7_class_resweep.md
  reports/csm/miss_queue_csm_iter1.jsonl reports/csm/red_list_csm.md
  reports/csm/GATE_LEDGER.json reports/csm/GATE.md plan/drift_log.md
  reports/master-work/work_log.md reports/csm/HALT_METER_P13.md
  reports/csm/HALT_METER_P13_DRAFT.md reports/2026-09-11-2135
  reports/span-recall/jjk/recall_verbatim.jsonl`.
  Warnings: the run dir commits whole (R-6 precedent: REPORT.md +
  canon_scores*.json + eval.json + run.json; R-7 adds answers.md — no
  pruning). EXCLUDE: `plan/SWITCHPOINT.md`, `reports/index.md` (both M,
  A-side/unrelated), `series/jjk/audit/eval.json` (untracked generated), and
  the A-side/scratch untracked set (`E:\Personal\Plot Works/`,
  `sample scripts/*.md`, `plan/COMPACTION_PROOF.md`,
  `reports/master-work/{GPU_LIVE1_REPORT.md, STOP, TRANSCRIPT_JOB.md,
  gpu_handoff_state/, interventions.jsonl, shell_log.jsonl}`).
- Q3 No council row owed for the CLASS (R-7 is the no-council pass, like
  R-6) — BUT this council runs on the owner 2026-09-12 directive (after every
  major step), so the record + COUNCIL_HISTORY row still land (top #27 →
  this row). Leaks to close in this commit: work_log B-append missing
  (W1-prep ANNOUNCE exists, no GREEN/close/commit lines); GATE.md live state
  still R-6; GATE_LEDGER last_green still R-6; drift D22 absent; red-list
  addendum line unmarked; HALT_METER not re-issued. Pre-existing: GATE.md
  L12 pin says 1,305 — fix to 1,321 in the live-state edit.
- Q4 P1.4 preconditions left READY (all P1.4 acts, none executed now):
  (a) 5.4 re-adjudication of csm-char-04 — row ruling stays `floor`,
  extraction-gated/5.4 LIVE/Phase-2; P1.4 owes the per-class census
  re-adjudication with the (a)-bucket 22-row floor set pre-registered on
  disk; (b) PHASE_A_COMPLETE_AT_FLOOR.md — correctly absent; after R-7 all
  7 classes are closed, meter (c)=0, open 35 = (a)22+(b)13, halt condition
  MET — the marker is written only after P1.4's one 4-gate copy + 5.4
  re-adjudication + bar-audit + close conditions (a)-(e) (campaign-todos
  sync = `plan/CSM_2PHASE_PLAN.md:190`); (c) P2.2 bar-audit — shape
  pre-registered (council #25 A12(d)/#26 A21/PHASE1_JOB: 3-5 cases per
  census class, fresh-context mechanical grader, pre-marker); per-class case
  files don't exist in `reports/csm/` yet → authoring + running is P1.4
  close-condition (d); the close commit must not run it.
- Objections: (1) the DRAFT treats csm-char-04 as (c) closed by R-7; the
  re-sweep left it open as floor — the re-issued meter must say
  (a)=22/(b)=13/(c)=0 or P1.4's marker inherits a bucket the sweep reversed;
  (2) zero rows close this class (no status flips) — ledger + GATE.md must
  state rows_closed_this_unit: 0 explicitly; (3) GATE.md L12 pin stale since
  R-5 — the live-state update must set 1,321.
# CSM 100% Completion — Residual Inventory (2026-09-17)

Read-only compilation from on-disk receipts. Every claim cites its source path.
Numbers that are not derivable are marked UNVERIFIED.

## TL;DR

- **134 page-run batches failing** (rc=2; 424 failing set questions) — all
  set/relation-completeness residuals (box-ranking / width / state-over-time),
  explicitly "not a router lever" (council #33, `plan/drift_log.md` D36).
- **22 floor rows** (21 D6-extraction census rows + `csm-char-04` Makima
  abilities) gate Phase-1 completion; halt residual 35 = 22 floor + 10
  by-design + 3 stamps (`reports/csm/GATE.md` lines 73–87).
- **Bank reds: 69 census** (417/486 green) = 21 still-red floor + 42 new
  box/arc/org + 6 ability-pool; **10 bar-audit auto-reds** (qa-mode reds are 15).
- **64 out-of-scope pages** (council #32 P-6); in-scope coverage 473/537 (88.1%),
  in-scope content remainder 0 (`reports/page-campaign/COVERAGE.md`).
- Discrepancy: drift D36 records "474 batches / 135 rc=2" but the committed
  receipt tsv has 475 rows / 136 rc=2 (off-by-one in the record; the tsv is the
  receipt of record — UNVERIFIED which tally is authoritative).

## §1 Page-run residual (model_window_d36)

Sources: `reports/csm/receipts/model_window_d36/page_run.tsv`,
`page_runs.log`, `state*` (16 files copied from `/tmp/csm_model_window/` per
`plan/drift_log.md` D36 entry).

- `page_run.tsv`: 475 rows = **473 page slugs + 2 sweep artifacts**
  (`sweep_a.report`, `sweep_b.report`, tsv lines 442–443). rc=0: 339;
  rc=2: 136 rows (134 pages + 2 sweeps).
- `page_runs.log`: **all 473 page slugs have a batch run** (473/473; the
  `light_of_a_star…` batch is present — its header line wraps, which earlier
  greps missed). NOT COMPLETE verdicts: 136 (134 pages + 2 sweeps at 0/0);
  658/1082 questions passed across the NOT-COMPLETE batches.
- **424 FAIL lines across 134 pages.** Relation breakdown:
  affiliations 109 · named techniques 75 (74 short-subject + 1
  `Light of a Star…`) · enemies 55 · allies 49 · aliases 39 · superiors 27 ·
  subordinates 23 · romantics 10 · families 9 · friends 8 · rivals 6 ·
  notable members 6 · mentors 3 · students 2 · creators 1 · creations 1 ·
  employees 1 (`tokyo_devil_detention_center`).
- **16 empty-answer FAILs** (`missing: -` — engine returned no candidates at
  all), 15 slugs (`eternity_devil` ×2): accident, centipede, cockroach,
  darkness, death, eternity×2, falling, famine, leech, lion, moray_eel, nazi,
  nuclear_weapons (devils), spear_hybrid, whip_hybrid.
- **rc=2 without FAIL lines: only the 2 sweep artifacts** (they are report
  sweeps, `NOT COMPLETE: 0/0`, wrote `csm-sweep_X.report-2026-09-17-0845/
  REPORT.md`). No page is missing from the log.
- Shape statement: the residual is **set/relation completeness**, not fact
  recall — D36 records it as "known-class residual: box-ranking / width /
  state-over-time, per the P2.3 triage", and council #33 ruled the 69 reds
  "box-ranking / width / state-over-time, not a router lever; no `router.py`
  change owed. R-9 absorbed, no-fire" (`plan/drift_log.md` D36; `reports/csm/
  receipts/council_fail8/`).
- State files: `state` = done-restored; `state.banks` (p23) / `state.canon` /
  `state.coverage` / `state.eval` / `state.span` (offline + probe) all rc=0;
  **`state.pytest` rc=1** (1 failed, 1,328 passed, 2 xpassed, 208.68s — window
  first pass; post-patch D35 `pytest_postfix_d35.log` = 1,329 + 2 xpassed rc=0,
  gate-1 pin 1,331).

## §2 The 22 floor rows

Source: `reports/csm/miss_queue_csm_iter1.jsonl` — 58 rows; ruling
fixable 33 / **floor 22** / stamped 3; status closed 23 / open 35; fix_class:
R-1 6, R-2 2, R-7x 1, R-3 6, R-5 5, R-4 1, R-4/R-2 13, R-6 3, D6-extraction 21.
Halt rule: `reports/csm/GATE.md` lines 73–87. Class counts + A22 null branch:
`plan/CSM_2PHASE_PLAN.md` lines 330–342.

The 22 rows (`ruling == "floor"`), with their question shapes:

- **csm-char-04** (R-7x) — "Every ability of Makima" (8th Makima-ability row;
  confirmed 22nd floor row by the R-7 close re-sweep; close lever = Phase-2
  extraction track / 5.4 re-adjudication).
- **21 D6-extraction rows** (closed only by the Phase-2 extraction campaign):
  - arc-narrative (8): `csm-dim-arcn-01/02/03/04/06/07/08/10` —
    "What happened to X during <arc>, in order?"
  - state-over-time (5): `csm-dim-state-01/02/03/08/09` —
    "What was true of X during <arc>?"
  - abilities (6): `csm-dim-abl-01/02/04/05/06/09` — "Every ability of X"
    (Yoru, Denji, Aki Hayakawa, Power, Reze, Asa Mitaka)
  - appearance (1): `csm-dim-appr-06` — "What does the Falling Devil look
    like?"
  - causality (1): `csm-dim-caus-03` — "Why can Asa not bring herself to kill
    Denji?"

Cross-checks:
- The 21 `csm-dim-*` IDs are **exactly** the 21 rows of `reports/csm/
  census_v1_floor_triage.jsonl` (ROUTING 17 / CONTENT 2 = abl-01, caus-03 /
  PARTIAL 2 = abl-02, abl-09 qa+anchor).
- `reports/csm/census_dimensions_csm_v2_triage.jsonl` (42 rows, adds
  arcb/chap/… classes): ROUTING 35 / PARTIAL 7; recovered_by qa+anchor 29 /
  narrative 12 / narrative+anchor 1.
- Halt residual 35 = 22 floor + 10 stamped by-design open (roster
  `csmdoor-01` 31/88; D5 `csmd5-01/02/03/05/06`, `gate400-320`, `red-R-4`;
  curation `csm-char-03`, `csm-set-02`) + 3 `r1blast-*` stamps; B writes
  `reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` and stops (`reports/csm/GATE.md`).
- A22 council decision (null branch): the P1.4 5.4 re-adjudication closes all
  21 reds, de-scoping P2.3 (`plan/CSM_2PHASE_PLAN.md` 330–342).

## §3 Bank reds (p23 census + bar audit)

Sources: `reports/csm/census_widened_csm_results.jsonl` (2026-09-17 23:07 run),
`reports/csm/bar_audit_p14_results.jsonl` (23:07) and `bar_audit_p14_results_
postfix_d34.jsonl` (18:56 baseline).

p23 census: 486 rows = 110 `csm-dim-*` (10 each × 11 classes) + 376
`csm-abl-pool`. Verdicts: **417 MECH_GREEN / 69 MECH_RED** (D36: "the 486-bank
reproduces P-5 exactly at 417/486"). No `csm-bar-*` rows; `csm-char-04`
absent from this file.

The 69 reds:
- **21 floor rows — all still MECH_RED at 23:07** (arc-narrative 8,
  state-over-time 5, abilities 6, appearance 1, causality 1).
- **42 new dim reds** (not in the v1 floor triage): story_arcs_box 10,
  chapter_box 9, episode 9, volume_box 9, organization 5.
- **6 ability-pool reds** (mechanism questions):
  `csm-abl-pool-140` Falling Devil (Body Control) · 149 Famine Devil
  (Hand-to-Hand Combat) · 166 Galgali (Hand-to-Hand Combat) · 237 Mysterious
  Man (Typhoon Devil Contract) · 252 Pochita (Immense Durability) · 358 Yoru
  (Building Sword).

Bar audit (both files: 26 rows, 120,949 B; verdict-identical, **zero delta**
18:56 → 23:07): verdict_qa 11 green / **15 red**; verdict_auto 16 green /
**10 red**; routed_mode qa 17 / narrative 5 / roster 4.
The 10 auto-reds: `csm-bar-arcn-01/02/03/04`, `csm-bar-state-01/02/03/04`,
`csm-bar-caus-01`, `csm-bar-pers-03`.
(Note: the task text says "the 10 reds in qa mode" — qa mode actually has 15
reds; the 10-red set is the auto-mode verdict.)

## §4 Coverage and out-of-scope

Source: `reports/page-campaign/COVERAGE.md` (regenerated 2026-09-17 by
`tools/coverage_report.py`; do not hand-edit).

- **473/537 pages covered (88.1%), 4,013 active questions; in-scope content
  remainder = 0.**
- 100% in-scope: chapter_box 232/232 (2,468q) · character 175/175 (1,260q) ·
  character_history 22/22 · story_arcs_box 14/14 (61q) · episode 12/12 (144q) ·
  organization 11/11 (40q) · establishment 3/3 (14q) · unknown 4/14 (4q).
- **64 out-of-scope** = volume_box 26 + music 20 + unknown 10 (of 14, 4
  covered) + blu_ray_dvd 4 + anime 2 + saga_box 2. Rule (line 42): "The
  saga_box nav box, release pages (volume_box, music, anime, blu_ray_dvd) and
  the excluded `unknown` list/author/meta/release pages are out of scope
  (chapter_box and story_arcs_box are in scope per council #32 P-6)."
- Uncovered `unknown` titles (10): Chain Run, Chainsaw Man (Manga),
  Chainsaw Man: The Stage, x BanG Dream!, x Monster Strike, Popularity Polls,
  Real Chainsaw Man, Story Arcs, Tatsuki Fujimoto, Timeline.
- Orphan batches: 0.

## UNVERIFIED / discrepancies

1. Drift D36 "474 batches — 339 rc=0, 135 rc=2" vs committed `page_run.tsv`
   475 rows (473 pages + 2 sweeps; 339 / 136 rc=2) — off-by-one in the record;
   the tsv is the receipt of record (UNVERIFIED which is authoritative).
2. "10 reds in qa mode" (task text) — qa-mode reds are 15; the 10-red set is
   auto-mode (§3).
3. Per-page FAIL attribution in `page_runs.log` is block-based (long lines
   wrap); the 424/134 totals are exact, per-page splits are heuristic.
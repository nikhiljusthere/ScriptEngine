# HANDOFF_STATE — CSM Phase-1 run (compact successor brief)

Written 2026-09-10, b session, at ~79% context (owner-ordered pre-work
handoff; predecessor died in a compaction loop at 91.6%). Read this file
+ `reports/master-work/PHASE1_JOB.md`. That is the whole brief.

## Position
- Phase 1 (§9a closure loop), P1.2. CLOSED so far: R-1 (`b84445f`),
  R-2+R-3 (D19; gate-1 pin 1,305), P1.1 (100k switch, `b11efef`),
  **R-5 relations-mode wave (2026-09-09): commits `ec60587` (C1: engine
  5 files + tests 2 + council package 12 + records) + `35c16c9` (C2:
  queue stamps + 68-row bank re-pin + gate receipts) + `3ee6bd0`
  (work_log closeout)**. R-5 gates: pytest 1,315 collected (chairman pin
  exact) / eval jjk 31/31 / span-recall offline 0 + probe 398/400 (99.5%)
  / canon opm 10/16 + 236/236 + 79.0%; R-5 meter 0/11 → 5/11 (≥1-HIT bar
  met; 5 partials proven harness budget-trim, 1 content gap → Phase 2).
  One mcp bare-name test failure proven PRE-EXISTING at HEAD (carried).
- Queue now: **38 open / 20 closed** (owner-verified 2026-09-10).
- NEXT (owner steer 2026-09-10, in order):
  1. **R-6 `subject_aliases` + R-7 `identity_fields` (61-key map)** —
     separate SHORT **no-council** passes, each with its own gate legs +
     queue stamps + commit (spec: `reports/csm/receipts/iter1_override_
     package_run.md` §2–3, below).
  2. **STOP after R-7** and tell the owner. Do NOT open P1.3's P1.4 or
     the close council in a high-context session — the owner restarts the
     session fresh for those (the 91.6% compaction-loop death is why).
- Optional delegated job: the WIDENED dimension census
  `reports/csm/census_dimensions_csm_v2.json` (one fresh-context
  subagent, AUTHOR ONLY, receipt under `reports/csm/receipts/`). Check
  `work_log.md` tail for its launch/completion line before re-deploying.

## Live pids (verify with ps + curl before relying on them)
- Qwen 100k: pid **58178** (`ninfer-serve` :18080, ~25 GB, 100k profile).
- `:8000` API: pid **162424** (CUDA; bge embedder + reranker ~5.3 GB).
  Stop it (and announce in `work_log.md` first) before any in-process
  model job; relaunch `setsid nohup python -m scriptengine.api.main`
  (CUDA) afterwards. canon-run + span-recall probe are HTTP clients —
  run them with `:8000` UP.

## File paths that matter
- `plan/drift_log.md` — D20 = current position; append D21 (R-6), D22 (R-7).
- `reports/master-work/work_log.md` — append checkpoints; last 3 lines = state.
- `reports/csm/GATE.md` (gate state) + `reports/csm/miss_queue_csm_iter1.jsonl`
  (the frozen queue; R-6 rows = `door-nar-None` ×3).
- `reports/csm/red_list_csm.md` — R-1..R-5 sections (no R-6/R-7 sections;
  the R-1×R-7 re-probe note sits in the R-1 section).
- `reports/csm/receipts/iter1_override_package_run.md` §2–3 — the R-6/R-7 spec.
- `reports/csm/receipts/council_r5/` + `reports/csm/COUNCIL_csm_r5_relations.md`
  — R-5 council + the **4 close-council carry items** (§Carried): (1) pre-existing
  mcp bare-name narrative-vs-qa mismatch; (2) meter harness budget-trim;
  (3) R-6 floor-inheritance verdict (answer in the R-6 pass, record at close);
  (4) governance addendum answer (in chairman.md).
- `reports/csm/CLOSE_COUNCIL_PREREGISTERED.md` — close-council Q1–Q4, MUST be
  answered on disk before any Phase-2 GPU-day.
- `reports/csm/t0_pilot_csm.json` `meta.unmatched_csm_infobox_keys` — the 61 keys
  for R-7. `series/csm/overrides.yaml` — where R-6/R-7 land (per-wiki yaml,
  engine stays series-agnostic).
- `tools/csm/validate_relations.py` (R-5 meter) + `reports/csm/CSM1B_RELATIONS_
  BANK.md` (meter bank, now 5/11). `/tmp/csm_iter1_records/` — sweep scripts,
  outputs, repin list, gate plan (survives on this machine).

## Standing rules for this run
- Council members **one at a time** (never 2/wave). R-6/R-7 are no-council.
- All model/GPU work on CUDA; no CPU shell >15 s; stop `:8000` (announced)
  before in-process model jobs. Qwen owns the card's 25 GB.
- Per pass: four standing gates — pytest (pin now **1,315** + new tests),
  eval jjk 31/31, span-recall jjk offline rc=0 + live probe ≥390/400,
  canon opm 10/16 exact + 236/236 canon + 79.0% (floor 74.0%) — plus the
  pass's own sweep/stamps. JJK baseline-exact; CSM work in CSM-centric files.
- Commits **path-limited** (`git add .` banned; named paths only).
- Checkpoint every unit to `work_log.md`; keep context small — read council
  outputs FROM DISK, never paste; this session's death was a context loop.

## R-6 / R-7 shapes (from the spec receipt)
- **R-6 `subject_aliases`**: display-name → canonical-node map in
  `series/csm/overrides.yaml`, consulted in `scriptengine/retrieve/
  narrative.py` (the `rank_subjects(link_entities(subject), …)` step of
  `NarrativeRetriever.timeline`; seam: `config.subject_ranking`). Three
  rows: the arc display names **Introduction / Bomb Girl / International
  Assassins** (bare display names are not in the wiki `aliases` table —
  only the full `… arc` titles are; the narrative door misses on them).
  Must also **answer the floor-inheritance question** (council_r2r3/
  chairman.md:43: do alias-resolved subjects inherit the level-0 card
  via the floor?) and record the verdict for P1.4.
- **R-7 `identity_fields`**: 61-key CSM infobox-key → question-template
  map in `series/csm/overrides.yaml`, consulted in `scriptengine/eval/
  page_gen.py` ahead of the engine `IDENTITY_FIELDS`/`UNCHECKED_KEYS`
  (one-line merge). Gate-4 canon re-probe covers the R-1×R-7 tripwires
  (opm-set-16; the onepiece "Sweet Commanders" row is an accepted
  residual — no gate covers onepiece).
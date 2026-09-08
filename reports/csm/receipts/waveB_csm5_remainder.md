# Receipt — CSM-5 remainder unit (Wave-2, worker sub 2 of 2)

**Executor:** `worker sub 2 of 2, CSM Wave-2 pair` (fresh context, model-free
shell, no GPU, no service). **2026-09-09.**
**Scope contract:** `reports/master-work/CSM_WAVE2_JOB.md` (unit CSM-5) + council
`reports/csm/COUNCIL_csm-campaign.md` item 5 (re-scoped CSM-5). All five
deliverables landed. Master record: `reports/csm/CSM5_REMAINDER.md`.

---

## What was done, per deliverable

**1. 5.3 — CSM fixtures on the code paths the CSM fixes exercise.**
New `tests/test_csm_fixtures.py` (CSM-shaped, parameterized on
`series_paths("csm")`; zero JJK-test changes — JJK-100% invariant):
- **G-CSM-1** count phrasings → `xfail` (non-strict) asserting the router wants
  the roster door. Currently RED (router routes them to `qa`, 0 members) — the
  marker states the debt; comes out when CSM-3's door fix lands.
- **G-CSM-2** model-free guard on the store-level precondition (the subject's own
  page leads its passage floor) — GREEN. The bundle-level failure is model-bound
  and lives on the red list, not as a test.
- **G-CSM-1 door half** — the declared-roster door serves the pageless
  Four-Horsemen set in `kind="declared"` — GREEN.
- **CSM-3b roster-door fix** (`f93d396`) is already guarded by
  `tests/test_span_recall.py::test_roster_shaped_bundle_hits_and_counts_member_names`
  — recorded, not duplicated.
- `pytest tests/test_csm_fixtures.py -q` → **3 passed, 2 xfailed in 0.14 s**
  (model-free); the two xfails are the genuine G-CSM-1 mode mismatch (`-rx`
  verified: assert `mode == "roster"`, router returns `qa`).

**2. 5.5 — generator-sliced gold + held-out declaration + pre-registered red
list (no LLM judge).**
- `tools/csm/slice_gold.py` (new, series-parameterized, **never fabricates** —
  the non-seed path is answer-aware via `slice_generic`, slicing verbatim spans
  from the store) → `reports/csm/gold_sliced_csm.json`: **200 questions across
  4 sources** (39 seed + 50 d4 + 11 census-roster + 100 census-narrative; the
  two census sets are sub-1's CSM-6 door probes, auto-picked-up by the
  slicer's `SET_FILES`). `gold_mode` declared-roster 12 / sliced 17 / partial 2 /
  prose 169 (the 111 census items are open door-probes with no structured
  answer → prose), **0 fabricated spans** (verified: all 162 non-null
  `verbatim_in_store` values are declared-roster members or store substrings).
- `reports/csm/heldout_declaration_csm.md` (H-1): the D4 open-50
  (`d4_open50_csm.json`, 50 items, named author, seed 20260909, revid 2026-09-09,
  54 source pages, 0 seed-bank dupes) + the twenty-failures set (H-2), both
  named to fresh-context subagent authors, run-never-edit, git-blame-checkable
  no-edit rule.
- `reports/csm/red_list_csm.md`: 5 mechanical entries (G-CSM-1, G-CSM-2, the
  roster-door 31/88 shortfall, G-CSM-3 intruders, G-CSM-4 relations routing),
  each a count / substring / router-mode expectation with gate + fix class
  (engine vs per-wiki override). No LLM-judged entries.

**3. 5.4 — narrative door pre-check (zero GPU).**
`reports/csm/door_precheck_csm.md` — verdict: **the narrative door CAN serve
CSM's chronological story from the existing cheap signals** (in-store arc/saga
`next`/`previous` chain: 16 `*_box` pages, 599 order edges; numbered
chapters/volumes/episodes 232/24/12; character-scoped `<X> arc` sections cover
both `chronology.py` and `narrative.py` orderings). **Extraction is NOT
triggered** — it stays gated on the Wave-2 dimension census being red on a
structural dimension (the §5.4 CONDITION, read only by the orchestrator).

**4. §13 — retention-decision awareness line.**
Recorded in `CSM5_REMAINDER.md` item 4: the §13 guard is already in-tree
(`build.py:116` → `facts.py:312 require_rebuild` / `:345 remap_derived`; `reset()`
drops `events` / `meaning` but not `abilities` — 376 rows survive, keyed on name;
`tests/test_stores.py:510`). The unit is *aware* of the retention decision;
**no gap to file.**

**5. Verify the twenty-failures set.**
Verified on disk 2026-09-09: `reports/csm/twenty_failures_csm.md` is a clean
**20-row** freeze — named author (fresh-context `twenty-failures-author`,
worker, wave A), all rows `status = open`, gate breakdown bank = 8 / door = 5 /
d5 = 7, no `d6` (an honest receipt gap — the events build is JJK-only —
recorded, not padded). Every row cites an on-disk receipt from the 2026-09-08
cycle; store facts re-verified read-only 2026-09-09. Declared in
`heldout_declaration_csm.md` (H-2).

---

## Artifacts (all new CSM-centric files / one CSM test file)

| file | kind |
|---|---|
| `tests/test_csm_fixtures.py` | new test (CSM-shaped) |
| `tools/csm/slice_gold.py` | new tool |
| `reports/csm/gold_sliced_csm.json` | new (generated) |
| `reports/csm/heldout_declaration_csm.md` | new |
| `reports/csm/red_list_csm.md` | new |
| `reports/csm/door_precheck_csm.md` | new |
| `reports/csm/CSM5_REMAINDER.md` | new (unit master record) |
| `reports/csm/receipts/waveB_csm5_remainder.md` | this receipt |

## Validation evidence

- `pytest tests/test_csm_fixtures.py -q` → `3 passed, 2 xfailed in 0.14 s`
  (model-free). `-rx` confirms the 2 xfails are the genuine G-CSM-1 mode
  mismatch, not errors.
- `slice_gold.py` run: 200 questions across 4 sources (seed 39 + d4 50 +
  census-roster 11 + census-narrative 100); no-fabrication check = 0 bad spans
  (all 162 non-null `verbatim_in_store` values are declared-roster members or
  verbatim store spans; prose answers carry no span).
- Store probes (read-only, model-free): `passages_for_subject("Denji")` = 90,
  `("Makima")` = 40 (G-CSM-2 store floor intact); `Devils` category = 88;
  232 `chapter` facts / 247 `arc` edges / 599 `next`/`previous` edges / 232
  numeral-titled `chapter_box` (5.4 signals).

## Guardrails honored

- **No git / no commits** — executor runs, never commits; artifacts are written
  and left for the orchestrator to commit by name.
- **No JJK-baseline writes** — every artifact is a new CSM-centric file or a CSM
  test file; `tests/test_span_recall.py` (the CSM-3b roster test) is *recorded*,
  not modified.
- **No model / GPU commands** — only SQL store reads + model-free `pytest` +
  code reads. No Qwen, no embedder/reranker load, no `:8000` call.
- **Every shell < 15 s** — all probes bounded; the only `pytest` is a single
  file, 0.14 s.

## For the orchestrator (not this worker's decision)

- The census model window (dimension census + `census_doors`) is **deferred to
  the orchestrator** under the one-copy rule (stop `:8000` → in-process CUDA →
  restart). This unit produced the zero-GPU inputs it consumes (5.4 pre-check,
  red list, sliced gold).
- `gold_sliced_csm.json` already incorporates sub-1's landed census sets (111
  items, prose). If sub-1 regenerates `census_roster_100_csm.json` /
  `census_narrative_100_csm.json`, re-run `scriptengine/.venv/bin/python
  tools/csm/slice_gold.py --series csm` (one deterministic line) to refresh.
- The 2 xfailed G-CSM-1 fixtures + the 5 red-list entries are the pre-registered
  debt for the §9a closure loop; a hit is a known failure, not a finding.
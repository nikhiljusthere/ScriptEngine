# R-6 · subject_aliases — run receipt (iter-1, 2026-09-10, csm-phase1-worker)

Short no-council pass per the owner steer (HANDOFF_STATE next-item; R-6
pre-registered by the iter-1 override package,
`reports/csm/receipts/iter1_override_package_run.md`). Closes the three open
`door-nar-None` rows.

## The gap (facts)

- CSM's `aliases` table carries only the full arc titles (`Bomb Girl arc`);
  the bare display names (`Introduction`, `Bomb Girl`, `International
  Assassins`) resolve to nothing, so the narrative door missed all three
  (queue `door-nar-None` ×3, door census 2026-09-10).
- The subject-resolution path read only `subject_demote_types` /
  `subject_type_priority` from overrides (`config.subject_ranking`); there was
  no display-name seam.

## The fix (query-time override, no reindex)

- `series/csm/overrides.yaml`: `subject_aliases:` — 3 rows (display name →
  canonical node, verbatim-verified against `series/csm/facts.db` at the
  iter-1 package run).
- `scriptengine/config.py`: `subject_aliases(overrides)` — sibling of
  `subject_ranking`; lowercased keys, `{}` default; no series name in `.py`.
- `scriptengine/retrieve/narrative.py`: map loaded in `__init__`; `timeline`
  feeds the query through `_alias_text` (any display name the query mentions
  appends its canonical name before `link_entities`, which then links through
  the canonical's own alias row); `authored_floor` consults the map before
  `node_by_name`.
- `tests/test_r6_subject_aliases.py`: 3 model-free tests (map shape; timeline
  resolves all three display names to canonical arcs; authored_floor
  equivalence display-name vs canonical).

## Verification

- Model-free probe (sqlite only): `Introduction` → `Introduction arc`
  (5 beats, first = Summary); `Bomb Girl` → `Bomb Girl arc` (5 beats,
  Summary); `International Assassins` → `International Assassins arc`
  (3 beats, Synopsis).
- New tests 3/3 (0.10 s).
- Four standing gates, one-copy order (W1 in-process CUDA with :8000 stopped;
  W2 with :8000 restarted on CUDA):
  - gate-1 `pytest tests/ -q`: **1,318 collected** (1,315 R-5 pin + 3 new
    R-6 tests); 1,313 passed, 3 failed = the known env-mcp trio that needs a
    live :8000 (same set as the R-5 record), 2 xpassed. 0 R-6 failures.
  - gate-2 `eval --series jjk`: **31/31**.
  - gate-3 `span-recall --series jjk`: offline **rc=0, 100.0000% (48,572)**;
    live 400-probe **398/400 (99.5%)** ≥ 390/400.
  - gate-4 `canon-run --series opm --skip-eval`: **236/236 canon, 10/16
    exact, 79.0% precision, 0 confident-wrong** (report
    `reports/2026-09-10-0820/REPORT.md`).

## Floor-inheritance verdict (council_r2r3 chairman item 8 — recorded for P1.4)

An alias-resolved subject **inherits the level-0 card via the floor**: the
floor is computed from the resolved node, and R-6 resolves the display name
*before* floor computation at every seam it is consulted.

- Narrative door: `authored_floor` consults the map before `node_by_name`, so
  a display-name subject yields exactly the canonical subject's floor (test 3).
  Whether the floor yields beats for CSM arcs is governed by the
  label∈EVENT_TYPES rule (CSM's `story_arcs_box` label is not in
  `EVENT_TYPES`, so arcs reach their own sections through the timeline itself,
  not the floor — unchanged behaviour for every arc question, aliased or not).
- qa door: the level-0 card (`passages_for_subject`, facts.py) resolves
  title → editor DB alias. The query-time map is not consulted there, so a qa
  subject written as a bare display name still gets no card. **Documented
  residual, not a new queue row**: re-probe at Phase 2 if the qa door surfaces
  bare display names; the fix then is index-time alias rows or consulting the
  map at the qa seam.
- Verdict wording for the P1.4 close council: "R-6's query-time map inherits
  the floor/card at every seam it is consulted (narrative); the qa-seam
  residual is documented, not frozen."

## Files

- `scriptengine/config.py` (`subject_aliases`)
- `scriptengine/retrieve/narrative.py` (import, `__init__`, `_alias_text`,
  `timeline`, `authored_floor`)
- `series/csm/overrides.yaml` (`subject_aliases:` 3 rows)
- `tests/test_r6_subject_aliases.py` (new, 3 tests)
- `reports/csm/miss_queue_csm_iter1.jsonl` (`door-nar-None` ×3 closed)
- `reports/csm/red_list_csm.md` (R-6 section + close stamp + floor verdict)
- `reports/csm/GATE_LEDGER.json` (last_green → R-6)
- `reports/csm/GATE.md` (live state → R-6)
- `plan/drift_log.md` (D21)
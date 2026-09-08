# CSM-5 remainder — unit master record (CSM 100% campaign, Wave-2, unit CSM-5)

**Executor:** `worker sub 2 of 2, CSM Wave-2 pair` (fresh-context, model-free
shell, no GPU, no service). **2026-09-09.**
**Scope (council COUNCIL_csm-campaign item 5, re-scoped):** "5.3 pilot CSM
fixtures on the code paths the CSM fixes actually exercise (G-CSM-1
count-phrasing, G-CSM-2 qa-passage, the CSM-3b roster-door fix); 5.5
generator-sliced gold + held-out declaration + pre-registered red list
(no LLM judge); 5.4 narrative door pre-check (zero GPU); §13 retention-decision
awareness line; verify the twenty-failures set."

**JJK-100% invariant:** every artifact below is a new CSM-centric file or a
CSM-shaped test in a CSM test file; no JJK baseline, no engine file, no git.

---

## 1 · 5.3 — CSM fixtures on the code paths the CSM fixes exercise

**Status: DONE (green, model-free).** `tests/test_csm_fixtures.py` (new,
CSM-shaped, parameterized on `series_paths("csm")` — zero JJK-test changes):

- **G-CSM-1** (`TestGCSM1CountPhrasingsReachTheRosterDoor`): both of the seed
  bank's count phrasings, `xfail` (non-strict) asserting the router wants the
  roster door. Currently RED — the router sends them to `qa` (0 members), so the
  marker *states the debt*; it comes out when CSM-3's door fix lands (non-strict,
  so an xpass never breaks the gate). `reason` cites G-CSM-1.
- **G-CSM-2** (`TestGCSM2SubjectPassageFloorIsIntact`): model-free *guard on the
  store-level precondition* — the subject's own page leads its passage floor
  (`passages_for_subject("Denji")`/`"Makima"` non-empty and led by the subject's
  own doc). GREEN. The bundle-level G-CSM-2 failure (the qa leg returning
  nothing) is model-bound and lives on the red list instead, not as a test.
- **G-CSM-1 door half** (`TestGCSM1RosterDoorServesPagelessMembers`): the
  declared-roster door serves the pageless Four-Horsemen set in `kind="declared"`
  (the members carry no pages of their own; receipt `GCSM1_ROSTER_DOOR.md`).
  GREEN.
- **CSM-3b roster-door fix** (`f93d396`, `served_text` flattens members/passages)
  is already guarded by `tests/test_span_recall.py::test_roster_shaped_bundle_hits_
  and_counts_member_names` — **recorded here, not duplicated.**

Run: `pytest tests/test_csm_fixtures.py -q` → **3 passed, 2 xfailed in 0.14 s**
(model-free). The two xfails are the genuine G-CSM-1 mode mismatch (verified via
`-rx`: both assert `mode == "roster"`, the router returns `qa`).

## 2 · 5.5 — generator-sliced gold + held-out declaration + pre-registered red list

**Status: DONE (all model-free; no LLM judge).**

- **5.5.1 generator-sliced gold** — `tools/csm/slice_gold.py` (new,
  series-parameterized) → `reports/csm/gold_sliced_csm.json` (**200 questions
  across 4 sources**: 39 seed + 50 d4 + 11 census-roster + 100 census-narrative;
  the two census sets are sub-1's CSM-6 door probes, auto-picked-up). `gold_mode`
  declared-roster 12 / sliced 17 / partial 2 / prose 169; **0 fabricated spans**
  (the slicer never invents text — every `verbatim_in_store` is a confirmed store
  substring or a declared-roster member, verified across all 162 non-null spans).
- **5.5.2 held-out declaration** — `reports/csm/heldout_declaration_csm.md`:
  declares the D4 open-50 set (`d4_open50_csm.json`) + the twenty-failures set
  (`twenty_failures_csm.md`), both named to fresh-context subagent authors, with
  the run-never-edit, git-blame-checkable no-edit rule.
- **5.5.3 pre-registered red list** — `reports/csm/red_list_csm.md`: G-CSM-1,
  G-CSM-2, the roster-door 31/88 shortfall, G-CSM-3 intruders, G-CSM-4 relations
  routing — each a mechanical expectation (count / substring / router-mode) with
  gate + fix class (engine vs per-wiki override). No LLM-judged entries.

## 3 · 5.4 — narrative door pre-check (zero GPU)

**Status: DONE (verdict).** `reports/csm/door_precheck_csm.md`: **the narrative
door CAN serve CSM's chronological story from the existing cheap signals** — the
in-store arc/saga `next`/`previous` chain (16 `*_box` pages, 599 order edges) +
numbered chapters/volumes/episodes (232/24/12) + character-scoped `<X> arc`
sections cover both `chronology.py` and `narrative.py` orderings. **Extraction is
NOT triggered** by this pre-check; it stays gated on the Wave-2 dimension census
being red on a structural dimension (the §5.4 CONDITION, read only by the
orchestrator).

## 4 · §13 — retention-decision awareness line

**Status: DONE (awareness, no code change needed).** The §13 guard is already
in-tree: `scriptengine/index/build.py:116` calls
`store.require_rebuild(force=force)`; `facts.py:312` `require_rebuild` + `:345`
`remap_derived`; `reset()` drops `events` / `meaning` but **not** `abilities`
(376 rows survive, keyed on name); covered by `tests/test_stores.py:510`. This is
the retention-decision awareness the plan asks for: the CSM-5 unit is *aware* of
the retention decision (what a re-index keeps vs drops) and it is already
guarded. **No gap to file.**

## 5 · Verify the twenty-failures set

**Status: DONE (verified on disk, 2026-09-09).** `reports/csm/twenty_failures_csm.md`
is a clean **20-row** freeze: named author (fresh-context `twenty-failures-author`,
worker, CSM Wave-2 wave A, 2026-09-09), all rows `status = open`, gate breakdown
bank = 8 / door = 5 / d5 = 7, no `d6` (an honest receipt gap — the events build
is JJK-only — recorded, not padded; the set is exactly twenty). Every row cites an
on-disk receipt from the 2026-09-08 cycle; store facts re-verified read-only
2026-09-09. Declared in `heldout_declaration_csm.md` (H-2).

---

## Artifacts

| deliverable | file | status |
|---|---|---|
| 5.3 CSM fixtures | `tests/test_csm_fixtures.py` | green (3 pass, 2 xfail-debt) |
| 5.5.1 sliced gold | `tools/csm/slice_gold.py`, `reports/csm/gold_sliced_csm.json` | 200 q (4 sources), 0 fabricated spans |
| 5.5.2 held-out declaration | `reports/csm/heldout_declaration_csm.md` | declared |
| 5.5.3 red list | `reports/csm/red_list_csm.md` | 5 mechanical entries |
| 5.4 door pre-check | `reports/csm/door_precheck_csm.md` | verdict: cheap signals sufficient |
| §13 awareness | (this record, item 4) | guard already in-tree |
| twenty-failures verify | `reports/csm/twenty_failures_csm.md` | 20 rows, verified |

**Guardrails honored:** no git / no commits (executor); no JJK-baseline writes
(all artifacts are new CSM-centric files or a CSM test file); no model / GPU
command (SQL store reads + model-free `pytest` + code reads); every shell < 15 s.
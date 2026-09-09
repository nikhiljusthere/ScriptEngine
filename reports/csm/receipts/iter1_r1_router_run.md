# R-1 engine fix — router count rule (G-CSM-1) — run receipt

Worker: fresh-context subagent, unit-3 serial-fix closure (2026-09-09).
Zero-GPU, model-free run: reads SQLite stores only; no model loaded, no :8000
call, no index/crawl. No git add/commit (orchestrator B verifies + commits).
No JJK/OPM files touched. All shell commands model-free; the full
`tests/test_router.py` file takes 48.8 s, so it was re-run in class chunks,
each < 15 s (the 150k rule).

**NOTE ON FILE NAME:** the task deliverable said `iter1_r1_router.md`; this
run's authoritative output path (runtime override) is
`reports/csm/receipts/iter1_r1_router_run.md`. B may commit/rename as
preferred.

## Root cause (two sub-bugs in `router._resolves_a_set`)

The red-list R-1 debt (csm-set-14 recall 0/5, csm-set-15 0/4; the door itself
serves 5/4 per `reports/csm/GCSM1_ROSTER_DOOR.md`) is in the counting probe
of `_resolves_a_set` (`scriptengine/retrieve/router.py`, rule 2):

1. **Set name inside the prepositional phrase** (csm-set-15). The G1 scope
   strip (`_SCOPE_PHRASE.sub`) removed "in the Four Horsemen" before
   `build_roster` ran, so the declared phrase
   `how many members are in the four horsemen` could no longer match; the
   probe fell to discovery, found no set, and rule 3 claimed `qa`. Same shape:
   db "across the multiverse" (was `qa`), and opm/onepiece "in the X"
   (reached the door only via discovery luck).
2. **The count phrasing's own `many` as a phantom qualifier** (csm-set-14).
   With the full probe, the declared phrase
   `special divisions exist in public safety devil hunters` matched, but the
   leftover "how many" words survive into `parse_constraints` as qualifier
   `many` — checkable against nothing (`__unverified__'many'`) — so the
   roster came back `partial`, and the R1-d counting gate (exact/declared
   only) refused it → `qa`. Verified on-disk pre-fix:
   `build_roster(csm, set-14)` → matched, confidence `partial`,
   `rejected: [__unverified__'many']`; set-15 → `declared`.

## Diff summary

- `scriptengine/retrieve/router.py` (+23/−1, one hunk in `_resolves_a_set`):
  the counting probe now **keeps the prepositional phrase and strips only the
  `how many` itself** (`_COUNT` — no new regex); the G1 scope strip stays on
  the non-counting path only. Docstring paragraph added (WHY: G1 interaction +
  R1-d gate). A scope the set does not cover still stays a constraint through
  `parse_constraints` (unverified → partial → qa), which is the narrower,
  correct guard.
- `tests/test_csm_router_count_rule.py` (new, 11 tests, CSM-centric,
  router-level, model-free): csm-set-14/15 verbatim phrasings → `roster` +
  `counting` signal; door serves the declared 5/4 members; a series with no
  rosters (empty `SeriesPaths`) is unaffected (`qa`, no raise); JJK/OPM
  invariance pins (R1-d subset count stays prose; full-set count, hxh Nen
  levels, db/opm/onepiece "in the X" counts keep the roster route; Kenjaku
  wards count stays `qa`).

Constraint audit:
- **Series-agnostic, no series name in `.py`** (the project rule): the rule
  fires only where a declared roster phrase matches — a wiki with no declared
  rosters resolves no set for a counting topic, so it cannot fire. No
  override gate needed (cleaner than one, and matches the red-list "engine"
  fix class).
- **No new dependency** (reuses `_COUNT`; only caller is the `has_set` probe).
- JJK/OPM behavior: unchanged in the 136-test router suite; the only
  behavior deltas in the baseline-vs-post probe are csm×2 and db (qa→roster,
  the same bug shape fixed).

## Baseline vs post-fix routing (model-free probe, `route()` over the stores)

| series | query | pre | post |
|---|---|---|---|
| csm | How many special divisions exist in Public Safety Devil Hunters? (set-14) | qa | **roster** |
| csm | How many members are in the Four Horsemen? (set-15) | qa | **roster** |
| jjk | How many of Suguru Geto's named techniques are used to trap? (R1-d) | qa | qa (unchanged) |
| jjk | How many named techniques does Suguru Geto have? | roster | roster (unchanged) |
| jjk | How many wards did Kenjaku's chain reaction compromise? | qa | qa (unchanged) |
| hxh | How many levels of Nen are there? | roster | roster (unchanged) |
| db | How many Gods of Destruction exist across the multiverse? | qa | **roster** (same bug shape) |
| opm | How many hero classes are in the Hero Association in One Punch Man? | roster | roster (unchanged) |
| onepiece | How many Sweet Commanders are in the Big Mom Pirates in One Piece? | roster | roster (unchanged) |
| (no rosters, empty store) | set-14 phrasing | qa | qa (rule cannot fire) |

"Declared how-many audit": every declared match phrase containing `how many`
(9 across 5 series) has a shorter sibling phrase, so stripping the phrasing
never orphans a declaration (verified by grep over `series/*/overrides.yaml`).

## Test output (all model-free; each command < 15 s)

```
$ scriptengine/.venv/bin/python -m pytest tests/test_csm_router_count_rule.py -q
11 passed in 3.19s

$ scriptengine/.venv/bin/python -m pytest tests/test_router.py -q
136 passed in 48.84s   # full file: >15 s, so re-run in class chunks:
#  TestSignals 8 | TestRoute 25 | TestBattlesInRouting 8 | TestSubjectPreference 10
#  TestArcsAreASetOnlyWhenAsked 12 | TestPhrasingRobustFieldQuestions 11 | TestPandaGaps 8
#  TestG17SingleFieldPlural 4 | TestG20OnceFrontedMechanism 2 | TestGetoGaps 7
#  TestShokoGaps 12 | TestEp14HowMechanism 3 | TestEpisodeAnchoredQa 15
#  TestG28OoaListAsk 6 | TestG29SingleValuePredicate 5  (each chunk < 15 s, all passed)
```

No embedder/reranker test was skipped: `tests/test_router.py` and the new
file are router-level (SQLite stores only) and neither loads a model.

## PENDING: section-3 council (big engine change) + four standing gates before B commits

The red-list notes make R-1 an **engine** change: it triggers the §3 council
+ the JJK-100% four-gate re-run. B must not commit until those pass.

**Exact commands for B at gate time** (venv `scriptengine/.venv/bin/python`;
device/session choice per the gpu-gate3 100k+CUDA side-session pattern,
`reports/csm/GATE_REBASELINE_2.md` — the 150k `:8000` service stays CPU):

1. `scriptengine/.venv/bin/python -m pytest tests/ -q`
   — expected 1,254 (GATE.md re-baseline) + 11 new = **1,265 passed**.
2. `scriptengine/.venv/bin/python -m scriptengine.cli eval --series jjk`
   — expected **31/31**.
3. `scriptengine/.venv/bin/python -m scriptengine.cli span-recall --series jjk`
   — expected **48,572/48,572 offline (rc=0)** (+ 400-probe live only if B's
   gate plan includes it).
4. `scriptengine/.venv/bin/python -m scriptengine.cli canon-run --series opm --skip-eval`
   — expected **10/16 exact, 236/236 canon (79.0%)**.

Router-level mechanical check (what this run verified, rerunnable in < 15 s,
model-free):
`scriptengine/.venv/bin/python -c "from scriptengine.config import series_paths; from scriptengine.retrieve.router import route; print(route(series_paths('csm'), 'How many special divisions exist in Public Safety Devil Hunters?').mode, route(series_paths('csm'), 'How many members are in the Four Horsemen?').mode)"`
→ `roster roster`.

CSM class re-sweep (council R5 dead-door ruling): after the gates, the R-1
class subset re-sweep (csm-set-14, csm-set-15, red-R-1 in
`reports/csm/miss_queue_csm_iter1.jsonl`) must show ≥ 1 HIT in its own new
rows or halt to council; on green, B marks the three rows `closed` in the
miss queue (worker left the queue file untouched).

## Changed files (this run)

- `scriptengine/retrieve/router.py` — the count-rule fix (only code write).
- `tests/test_csm_router_count_rule.py` — new regression file (only test write).

Not touched: `series/jjk/**`, `series/opm/**`, the miss queue, any JJK file.
Pre-existing working-tree modifications (`plan/decisions.md`,
`reports/master-work/*`, other `??` entries in `git status`) are the
orchestrator's, not this run's.

## Residual risks

- **Discovery-side counting questions with scope words** (theoretical): a
  counting question whose retained scope phrase now exact-matches a *discovered*
  set could newly route to `roster` where the stripped probe would not. No
  such case exists in the router suite or the 9-question probe; the four gates
  (esp. `eval --series jjk` and the opm canon baseline, which the router
  docstring names as the detector) are the tripwire.
- The db flip (qa→roster) is an improvement but is a behavior delta on a
  non-JJK series — covered by gate 4 (opm canon) only indirectly; the db
  suite has no count-question gold row in the four gates. Low risk: the
  declared set is the wiki's own curation.
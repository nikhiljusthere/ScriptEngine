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

- `scriptengine/retrieve/router.py` (+22/−1, one hunk in `_resolves_a_set` — the
  stat was "23" in the first draft of this receipt; `git diff --stat` line count
  is 23 changed = 22 insertions + 1 deletion; council R-1 chair corrected):
  the counting probe now **keeps the prepositional phrase and strips only the
  `how many` itself** (`_COUNT` — no new regex); the G1 scope strip stays on
  the non-counting path only. Docstring paragraph added (WHY: G1 interaction +
  R1-d gate). A scope the set does not cover still stays a constraint through
  `parse_constraints` (unverified → partial → qa), which is the narrower,
  correct guard.
- `tests/test_csm_router_count_rule.py` (new, 14 tests, CSM-centric,
  router-level, model-free): csm-set-14/15 verbatim phrasings → `roster` +
  `counting` signal; door serves the declared 5/4 members; a series with no
  rosters (empty `SeriesPaths`) is unaffected (`qa`, no raise); JJK/OPM
  invariance pins (R1-d subset count stays prose; full-set count, hxh Nen
  levels, db/opm/onepiece "in the X" counts keep the roster route; Kenjaku
  wards count stays `qa`). Council R-1 amendment (chairman, 2026-09-09) added
  3 pins: the csm-Tokyo positive declared delta (param row), the opm-set-16
  Blizzard gate-4 delta (9-member discovered set vs canon 38), and the
  onepiece-Marines discovery-side residual (accepted wrong-set serving,
  `TestCouncilR1BlastRadiusPins`).

Constraint audit:
- **Series-agnostic, no series name in `.py`** (the project rule): the rule
  fires only where a declared roster phrase matches — a wiki with no declared
  rosters resolves no set for a counting topic, so it cannot fire. No
  override gate needed (cleaner than one, and matches the red-list "engine"
  fix class).
- **No new dependency** (reuses `_COUNT`; only caller is the `has_set` probe).
- JJK/OPM behavior: unchanged in the 136-test router suite; the behavior
  deltas in the baseline-vs-post probe are csm×3 (set-14, set-15, in-Tokyo),
  db (Gods of Destruction), opm (Blizzard Group — gate-4 row, see the
  pre-registration below) and onepiece (Marines — the accepted discovery-side
  residual, see Residual risks). All are the same bug shape fixed; JJK is
  delta-free (the four jjk eval-bank count rows verified unchanged).

## Baseline vs post-fix routing (model-free probe, `route()` over the stores)

| series | query | pre | post |
|---|---|---|---|
| csm | How many special divisions exist in Public Safety Devil Hunters? (set-14) | qa | **roster** |
| csm | How many members are in the Four Horsemen? (set-15) | qa | **roster** |
| csm | How many special divisions are in Tokyo? (council R-1: second csm delta) | qa | **roster** (declared set covers the scope; positive) |
| jjk | How many of Suguru Geto's named techniques are used to trap? (R1-d) | qa | qa (unchanged) |
| jjk | How many named techniques does Suguru Geto have? | roster | roster (unchanged) |
| jjk | How many wards did Kenjaku's chain reaction compromise? | qa | qa (unchanged) |
| hxh | How many levels of Nen are there? | roster | roster (unchanged) |
| db | How many Gods of Destruction exist across the multiverse? | qa | **roster** (same bug shape) |
| opm | How many hero classes are in the Hero Association in One Punch Man? | roster | roster (unchanged) |
| opm | How many members are in the Blizzard Group in One Punch Man? (opm-set-16, gold qa/canon 38) | qa | **roster** (discovered 9-member set; gate-4 pre-registration below) |
| onepiece | How many Sweet Commanders are in the Big Mom Pirates in One Piece? | roster | roster (unchanged) |
| onepiece | How many Sweet Commanders are in the Marines? (council R-1: discovery-side residual) | qa | **roster** (serves discovered "Marine Commanders" — the accepted wrong-set serving; pinned + stamped) |
| (no rosters, empty store) | set-14 phrasing | qa | qa (rule cannot fire) |

"Declared how-many audit": every declared match phrase containing `how many`
(11 across 5 series — csm×2, db×1, jjk×5 [line 911 alone holds three],
opm×1, onepiece×2; the first draft of this receipt said 9, a miscount of the
jjk lines; council R-1 chair + reviewer 1/3 verified) has a shorter sibling
phrase in the same `match:` list, so stripping the phrasing never orphans a
declaration (verified by grep over `series/*/overrides.yaml`).

## Test output (all model-free; each command < 15 s)

```
$ scriptengine/.venv/bin/python -m pytest tests/test_csm_router_count_rule.py -q
14 passed in 3.44s   # 11 at run time + 3 council R-1 blast-radius pins
                     # (B applied 2026-09-09; 14/14 re-run by B, model-free)

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
   — expected: **gate-time collect-only is the source of truth**. The tree
   collects **1,280** pre-amendment (the 1,254 re-baseline predates ~15
   committed tests since; reviewer 2/4 collect-only verified) + the 14-test
   file's net +3 pins = **1,283 expected at this tree**. A known +N test delta
   does not re-run the gates (COUNCIL_csm-3 Ruling 5e); record deviations.
   (The first draft of this receipt expected 1,265 — stale; corrected by
   council R-1 reviewers 2/4 + chair.)
2. `scriptengine/.venv/bin/python -m scriptengine.cli eval --series jjk`
   — expected **31/31**.
3. `scriptengine/.venv/bin/python -m scriptengine.cli span-recall --series jjk`
   — expected **48,572/48,572 offline (rc=0)** (+ 400-probe live only if B's
   gate plan includes it).
4. `scriptengine/.venv/bin/python -m scriptengine.cli canon-run --series opm --skip-eval`
   — expected **10/16 exact, 236/236 canon (79.0%)**. The opm-set-16
   pre-registration below applies: a drop confined to that row is the
   documented R-1 delta, not an unexplained regression.

**Gate-4 pre-registration (council R-1 chairman, 2026-09-09):**
If `canon-run --series opm` drops 236/236, a regression **confined to
opm-set-16** ("How many members are in the Blizzard Group in One Punch Man?",
`questions/opm.json:1785`; gold `qa`/canon 38; the post-fix routing serves the
discovered 9-member "The Blizzard Group" set) is the *documented R-1 delta* →
**halt to council** with the gold-shape decision the row's own 2026-08-15 note
sets up ("The engine's roster for this question was correct; the gold could
not say so" — restore the set shape, or re-baseline with a record; never
"log and move on", `plan/CSM_WAVE2_RESUME.md` §4). A regression on *any
other* opm row = unexplained → revert + halt to council.

Router-level mechanical check (what this run verified, rerunnable in < 15 s,
model-free):
`scriptengine/.venv/bin/python -c "from scriptengine.config import series_paths; from scriptengine.retrieve.router import route; print(route(series_paths('csm'), 'How many special divisions exist in Public Safety Devil Hunters?').mode, route(series_paths('csm'), 'How many members are in the Four Horsemen?').mode)"`
→ `roster roster`.

CSM class re-sweep (council R5 dead-door ruling, as amended by council R-1):
after the gates, the R-1 class subset re-sweep covers csm-set-14, csm-set-15,
red-R-1 in `reports/csm/miss_queue_csm_iter1.jsonl` **plus the three stamped
blast-radius rows** (csm-Tokyo, opm-Blizzard, onepiece-Marines — stamped by
the council R-1 chairman). **Pass = csm-set-14 AND csm-set-15 both HIT and
zero new misses on the stamped rows.** Close only HIT rows; `red-R-1`
closes when the class goes green; any open recall-row miss after the
re-sweep = halt to council (no partial close). (The first-draft rule "≥ 1 HIT
or halt, then mark the three rows closed" was unenforceable — a 1-of-2
partial satisfied it while closing a failing row; reviewer 4's finding,
chair-adopted.)

## Changed files (this run + the council R-1 amendments B applied)

- `scriptengine/retrieve/router.py` — the count-rule fix (only code write;
  ships **exactly as drafted** per the council verdict — the mechanical
  discovery-side guard was verified infeasible without breaking the Geto/hxh
  pins, so no new engine logic).
- `tests/test_csm_router_count_rule.py` — new regression file (only test
  write; 11 at run time + 3 council R-1 blast-radius pins applied by B).
- `reports/csm/miss_queue_csm_iter1.jsonl` — 3 blast-radius stamp rows
  appended (council R-1 amendment 3; the frozen meter's rows are untouched).
- `reports/csm/red_list_csm.md` + `plan/drift_log.md` — the db-flip record,
  the class-boundary note, the discovery-counting residual as a named open
  item, and the rejected-layers record (council R-1 amendment 4).

Not touched: `series/jjk/**`, `series/opm/**`, any JJK file.
Pre-existing working-tree modifications (`plan/decisions.md`,
`reports/master-work/*`, other `??` entries in `git status`) are the
orchestrator's, not this run's.

## Class boundary (council R-1 reviewer 3)

The fix fires only on `\bhow many\b` (`_COUNT`, router.py:170). Other count
phrasings — "what is the number of X", "how much" — retain **both** sub-bug
shapes (the phantom `many` on the declared path; the scope-stripping on the
discovery path) and are **out of R-1 closure scope** (a future class).
R-1's closure claim is scoped to "how many" phrasings only.

## Residual risks

- **Discovery-side counting questions with scope words — LIVE, not
  theoretical** (council R-1 reviewers 1/4 disproved the first draft's
  "theoretical" label; chair re-verified): the kept prepositional phrase also
  completes *discovered* set names. Two live cases, accepted with tripwires:
  (1) onepiece "How many Sweet Commanders are in the Marines?" → roster,
  serving the discovered 7-member "Marine Commanders" set (not the asked
  set) — pinned in `TestCouncilR1BlastRadiusPins`, stamped in the miss
  queue, zero-new-miss pass criterion on the re-sweep; (2) opm-set-16
  (Blizzard) — the gate-4 pre-registration above. A named follow-up class,
  **discovery-counting**, is recorded in the red list; re-probe it after the
  R-7 key-map widening lands (the R-1×R-7 note: the key map grows the
  discovered-set surface).
- The db flip (qa→roster) is a positive delta on a non-JJK series — already
  tripwired by the pytest pin in `tests/test_csm_router_count_rule.py` (db
  param row); recorded in the red list, **not** stamped in the queue (a stamp
  would unfreeze the R2 meter beyond the gate400 precedent for a delta that
  is pinned and positively shaped — chair's ruling). The db suite has no
  count-question gold row in the four gates; the residual is low-risk (the
  declared set is the wiki's own curation).

## Amendment log (council R-1, 2026-09-09 — the verdict is AMEND, not SHIP)

The `reports/csm/receipts/council_r1_router/` package (5 advisors, 5 peer
reviews, chairman) found the hunk sound but the receipt carrying three
stale/false facts (1,265; "9"; "the only other delta: db") and a live
wrong-set serving labeled "theoretical". B applied, model-free-verified
(14/14 in 3.44 s before any gate session):
1. tests: 11 → 14 (3 blast-radius pins);
2. this receipt: 1,265 → 1,283 (gate-time collect-only source of truth);
   census 9 → 11; stat +23/−1 → +22/−1; probe table +3 rows; "the only
   other delta: db" struck; residual section theoretical → live; closure
   rule replaced (close-only-HIT + zero-new-miss-on-stamped-rows);
   class-boundary + gate-4 pre-registration sections added;
3. miss queue: 3 blast-radius stamp rows (R-1, open);
4. red list + drift log: db-flip / class-boundary / discovery-counting /
   rejected-layers records.
The code hunk itself is unchanged by the amendments.
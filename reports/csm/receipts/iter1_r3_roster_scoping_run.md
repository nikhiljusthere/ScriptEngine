# R-3 engine fix — section-scoped intruders on "Every X of Y" (G-CSM-3) — run receipt

Worker: fresh-context subagent, unit-3 serial-fix closure iteration 2 (2026-09-09).
Zero-GPU, model-free run: reads SQLite stores + `build_roster` only; no model
loaded, no :8000 call, no index/crawl. No git add/commit (orchestrator B
verifies + commits). No JJK/OPM files touched. All shell commands model-free,
each < 15 s (the 150k rule).

**NOTE ON FILE NAME:** the task deliverable said
`reports/csm/receipts/iter1_r3_roster_scoping_run.md`; that path IS this file
(runtime-confirmed).

## Root cause (one debt, three shapes)

Red-list R-4 (`reports/csm/red_list_csm.md`; the red-list R-3 row is the
31/88 roster-door budget floor): the queue rows csm-set-17
(14 served vs 7 gold), csm-char-03 (18 vs 11), csm-set-02 (18 vs 13),
csm-set-01 (7 vs 4) all serve the right items **plus intruders**. The
intruders are *real declared members* of the wiki's rosters — the debt is
**scoping**, not retrieval:

1. **Form headings inside ability answers** (csm-set-02, csm-char-02,
   csm-char-03). `widen_umbrella` expands "Every ability of X" to the kind
   union {technique, transformation, trait}; the section pass then reads the
   *union of the per-kind `ability_sections` maps* — for CSM that union
   includes `Appearance`, whose leaves are the character's form headings
   (Fiend Form, Devil Form, Human Form). The bank's ability golds carry no
   form heading, so every umbrella ability question inherits the forms.
2. **Prose-filed rows inside an explicit-kind answer** (csm-set-01). The
   extracted pass reads a kind's rows from *every* section, so Denji's two
   prose rows `Hybrid/Devil Transformation` (filed under
   `Abilities / Hybrid Powers`) answer "Every form of Denji" even though the
   wiki files his forms as five headings under `Appearance`. Decisive
   cross-check: csm-char-01's gold ("Every ability of Denji") *includes*
   those two rows, csm-set-01's gold excludes them — the same rows are an
   answer in one question and intruders in the other, so the filter must be
   question-shaped (explicit-kind only), not kind-shaped.
3. **Open named roster served to a plain-membership question**
   (csm-set-17 vs csm-set-08). The `Tokyo Special Division 4` declaration
   lists 14 named members (the later-arc fiends included); the wiki's own
   Members section lists the closed Part-1 core of seven. csm-set-17's gold
   is the closed seven; csm-set-08's is all fourteen — the qualifier word
   (`named`) is the discriminator.

## Diff summary (three per-wiki opt-in knobs, all no-ops when undeclared)

`scriptengine/retrieve/roster.py` (+127/−9):

- **M1 — closed-members scoping** (`RosterDefinition.closed_members`, parsed
  from `closed_members:`; applied in `build_roster`'s declared branch):
  when a set declares `closed_members` **and** the qualifier does not
  include `named`, serve the closed core; the scoped-out members are recorded
  in `rejected` with `rule="closed-members"` (report, don't hide),
  `candidates` stays the full count, and an empty intersection is a data
  error that serves the full list rather than nothing. `Roster.warning`
  reworded for the closed case ("the closed membership is served, 7 of 14
  named members" — the old "every member was kept" would be false).
- **M2 — umbrella section scoping** (new override field
  `ability_sections_umbrella`): `build_roster` computes
  `umbrella = kinds != _asked_kinds(...)` (i.e. `widen_umbrella` actually
  added kinds) and threads it to `_section_roster`, which — **only when the
  field is declared non-empty** — reads the declared sections alone instead
  of the per-kind union. Undeclared (every other wiki, including JJK): the
  union, byte-identical to pre-fix.
- **M3 — extracted-row section scoping** (new override field
  `ability_row_sections`, kind → [sections]): in `_extracted_roster`, when
  the question is **not** an umbrella question (explicit kind, e.g.
  "Every form of X"), a kind-K row is kept only if some component of its
  `section` path (split on "/") is in the declared section list for K;
  undeclared kind = read whole (pre-fix behavior). The technique/
  transformation fold-fallback is additionally suppressed when the wiki
  declared row-sections for **every** asked kind (`scoped`): an empty read
  is then a statement (the wiki files the kind as headings, not prose rows),
  not model wobble — so the fold must not refill it. WHY comments in the
  code name G-CSM-3 + the queue rows.

`series/csm/overrides.yaml` (+29/−0):

- `ability_sections_umbrella: [Abilities]`
- `ability_row_sections: {transformation: [Appearance]}`
- `closed_members: [Makima, Aki Hayakawa, Denji, Power, Himeno,
  Kobeni Higashiyama, Hirokazu Arai]` on the `Tokyo Special Division 4`
  roster (the `members:` list of 14 is kept — csm-set-08's full roster).

Constraint audit:

- **No series name in `.py`** (the project rule): all three mechanisms fire
  only where a per-wiki field is declared (`closed_members`,
  `ability_sections_umbrella`, `ability_row_sections`). Every other wiki —
  JJK, OPM, db, hxh, onepiece, bleach, berserk — declares none of the
  fields, so its answers are structurally unchanged; the JJK pins in the
  test file are the standing check (all 8 wikis *do* declare
  `ability_sections`, which is exactly why a blanket restriction was
  rejected: it would have dropped JJK's `Divine Dogs / Nue / Related
  Techniques` subpage rows and character-page ability rows).
- No new dependency; no change to the section/extracted *member* shape
  (`RosterMember`), so `context.py::_roster_context` serving is untouched.
- The bank gold is **not** encoded in the engine: the mechanisms read only
  wiki-side declarations; the per-character trait/contract residue (see
  Residuals) is deliberately left as bank-level curation.

## Baseline vs post-fix (model-free `build_roster` over the CSM store)

Pre-fix numbers are this run's pre-edit baseline probe (same store, same
phrasings; bank alias-folding per the sweep scorer: a returned name matches
a gold item by item or alias, case-insensitive).

| queue row | question | pre | post | bank gold | post state |
|---|---|---|---|---|---|
| csm-set-17 | Who are the members of Tokyo Special Division 4? | 14 | **7** | 7 | **HIT** (7/7, the closed core) |
| csm-set-08 | Every named member of Tokyo Special Division 4 | 14 | 14 | 14 | HIT (invariant, `named` keeps the full roster) |
| csm-set-01 | Every form of Denji | 7 | **5** | 4 | **HIT** (5 rows fold to the 4 gold items: both Human rows → `Human`; Hybrid Form → alias of Chainsaw Man; Devil Form → alias of Chainsaw Devil; Combined Form) |
| csm-set-02 | Every ability of Power | 18 | **16** | 13 | red-partial: 3 intruders left (trait rows, see Residuals) |
| csm-char-02 | Every documented ability of Power | 18 | **16** | 16 | **HIT** (exact 16/16 — bonus row, same R-3 class) |
| csm-char-03 | Every ability of Aki Hayakawa | 18 | **16** | 11 | red-partial: 5 intruders left (trait + contract rows, see Residuals) |
| csm-char-01 | Every ability of Denji | 27 | **22** | 17 | improved (10 → 5 intruders; all 17 gold present incl. both transformation rows — M3 correctly off for the umbrella question) |
| csm-char-04 | Every ability of Makima | 7 | 7 | 8 | invariant (D6-extraction floor row, untouched) |
| csm-char-05 | Every ability of Himeno | 2 | 2 | 2 | invariant (declared subject roster) |

Side checks: "Every devil contract of Aki Hayakawa" (declared, 3) and
"Every devil Aki Hayakawa contracted with" (declared, 4) unchanged; the
contract questions route to the declared roster and never touch the
extracted path. **R5 closure meter: 3 own-new-row HITs (set-17, set-01,
char-02) ≥ 1 → satisfied.** The re-sweep itself is B's at gate time.

## Test output (all model-free, each command < 15 s)

```
$ scriptengine/.venv/bin/python -m pytest tests/test_csm_roster_scoping.py -q
13 passed in 2.82s

$ scriptengine/.venv/bin/python -m pytest tests/test_csm_fixtures.py tests/test_csm_router_count_rule.py tests/test_ability_owner.py -q
37 passed, 2 xpassed in 4.31s

$ scriptengine/.venv/bin/python -m pytest tests/test_roster.py tests/test_roster_scoring.py tests/test_roster_validation.py tests/test_ability_class.py tests/test_ability_extraction.py -q
155 passed in 11.20s
```

`tests/test_csm_roster_scoping.py` (new, 241 lines, 13 tests, CSM-centric,
door-level, model-free) covers:

- `TestClosedMembershipScoping` — csm-set-17 verbatim serves the closed 7
  (candidates 14, the 7 scoped-out members in `rejected` under
  `rule="closed-members"`); csm-set-08 verbatim keeps all 14 with no
  closed-members rejections.
- `TestUmbrellaAbilityQuestionsScopeTheSectionPass` — csm-set-02 verbatim
  (no form headings, exact 16-set incl. the three documented trait
  residues); csm-char-02 verbatim (exact 16-gold); csm-char-03 verbatim
  (no form headings; the same-group gold items `Summoning`/`Precognition`
  stay — recall pin).
- `TestExplicitKindQuestionsScopeTheExtractedPass` — csm-set-01 verbatim
  (exactly the five `Appearance` form headings, prose rows excluded);
  csm-char-01 verbatim (the two extracted transformation rows stay in, the
  form headings stay out, all 17 gold present).
- `TestUntouchedRosterPaths` — Himeno declared (2), Aki contract rosters
  (3/4), Makima's 7 members.
- `TestScopingLeavesJjkUnchanged` — **the JJK-100% invariance pins** (the
  way wave 1 did it): "Every ability of Satoru Gojo" (23, union sections),
  "Every technique of Sukuna" (21 — the `Divine Dogs`/`Nue` subpage rows
  survive, proving the M3 opt-in gate), "Every cursed technique" (38
  declared, no closed-members rejections), "Every form of Satoru Gojo"
  (14 extracted rows, M3 off for undeclared wikis).

No embedder/reranker test was skipped: everything above is door-level
(SQLite stores + declared resolution) and loads no model.

## Residuals (documented curation debt, NOT mechanizable without encoding bank gold)

- **csm-set-02 (3 intruders):** `Enhanced Strength`, `Enhanced Speed`,
  `Enhanced Smell` — trait rows the bank dropped for Power. The same
  `Enhanced X` family is *kept* in csm-char-04's gold (Makima: Enhanced
  Smell) and csm-char-03's own gold (Aki: Enhanced Speed/Durability), so no
  kind/group/section rule separates the kept from the dropped rows without
  per-character bank answers (forbidden in the engine).
- **csm-char-03 (5 intruders):** `Enhanced Reflexes` (same `Physical
  Prowess` group as the kept `Enhanced Durability/Speed`) + the four
  `Devil Contracts` rows (`Curse/Fox/Future/Control Devil Contract`) while
  the gold *keeps* the same group's `Summoning` and `Precognition`. Again
  the kept vs dropped split is inside one group, per-character.
- **csm-char-01 (5 intruders):** the two `Abilities`-tree container leaves
  (`Hybrid Powers`, `Weapons` — page-count-filtered sections, pre-existing)
  + the three `Devil Contracts` trait rows (the wiki lists Denji's three
  contracts as abilities; the bank's 17-gold does not). Pre-existing
  shape, reduced by 5 via M2; the bank does not list contract rows for
  Denji.

Recommendation for the section-3 council / unit-4 (R-6/R-7 hooks era):
these 13 rows are bank adjudication (re-verify the 3+5+5 curation calls
against the wiki's own per-character pages, or accept them as documented
residue in the red list). Either is a bank edit, not an engine edit.

## PENDING: section-3 council (big engine change) + four standing gates before B commits

R-3 is an **engine** change: three new override fields + `build_roster`
behavior. Triggers the §3 council + the JJK-100% four-gate re-run. B must
not commit until those pass.

**Exact commands for B at gate time** (venv `scriptengine/.venv/bin/python`;
device/session ordering per the R-1 gate pattern — one-copy 150k, `:8000`
stays CPU, Qwen untouched):

1. `scriptengine/.venv/bin/python -m pytest tests/ -q`
   — gate-time collect-only is the source of truth. This run added a
   13-test file to a tree that collected 1,283 at the R-1 gate; the shared
   R-2+R-3 re-run (council R-2+R-3) adds 7 R-2 tests + 13 R-3 tests + 2
   council amendments, so expect the shared pin **1,305 collected**
   (1,303 passed + 2 xpassed; the two G-CSM-1 xfails in
   `tests/test_csm_fixtures.py` stay xfail-marked and now pass as
   xpassed, per the R-1 gate record). A known +N delta does not re-run the
   gates (COUNCIL_csm-3 Ruling 5e); record deviations.
2. `scriptengine/.venv/bin/python -m scriptengine.cli eval --series jjk`
   — expected **31/31**.
3. `scriptengine/.venv/bin/python -m scriptengine.cli span-recall --series jjk`
   — expected **48,572/48,572 offline (rc=0)** (+ 400-probe live per the
   gate plan).
4. `scriptengine/.venv/bin/python -m scriptengine.cli canon-run --series opm --skip-eval`
   — expected **10/16 exact, 236/236 canon (79.0%)**. Pre-registration: a
   canon drop on an OPM roster row is *unexplained by this fix* (no OPM
   field is declared; the mechanisms are no-ops there) → revert + halt to
   council. Any OPM row drop = revert.

Door-level mechanical re-probe (what this run verified, rerunnable < 15 s,
model-free):

```
scriptengine/.venv/bin/python -c "
from scriptengine.config import series_paths
from scriptengine.retrieve.roster import build_roster
p = series_paths('csm')
for q in ['Who are the members of Tokyo Special Division 4?', 'Every form of Denji', 'Every ability of Power']:
    print(q, len(build_roster(p, q).members))"
```
→ `7 5 16` post-fix (pre-fix: `14 7 18`).

CSM class re-sweep (R5, B at gate time): re-sweep the R-3 class subset of
`reports/csm/miss_queue_csm_iter1.jsonl` (csm-set-17, csm-char-03,
csm-set-02, csm-set-01 + the bonus csm-char-02). Pass = ≥ 1 own-new-row HIT
(set-17 / set-01 / char-02 are expected HITs per the table above; set-02
and char-03 close only if their residual curation rows are adjudicated in
the bank first) and zero new misses on any stamped row. Close only HIT
rows; update the queue file with the closure receipts.

## Changed files (this run)

- `scriptengine/retrieve/roster.py` (+127/−9) — M1/M2/M3 + `Roster.warning`
  reword + WHY comments naming G-CSM-3 and the queue rows.
- `series/csm/overrides.yaml` (+29/−0) — the three CSM declarations.
- `tests/test_csm_roster_scoping.py` (new, 241 lines, 13 tests) — CSM
  mechanism tests + JJK invariance pins.
- This receipt: `reports/csm/receipts/iter1_r3_roster_scoping_run.md`.

Not touched: `series/jjk/**`, `series/opm/**`, any JJK file, `questions/*.json`,
the miss queue (B updates it at re-sweep time). Pre-existing working-tree
modifications (`plan/decisions.md`, `plan/state.md`, `reports/index.md`,
`reports/master-work/*`, `scriptengine/retrieve/hybrid.py`,
`scriptengine/stores/facts.py`, `tests/test_csm_fixtures.py`,
`tests/test_retrieve.py`) are the orchestrator's / other waves', not this
run's. Nothing staged.
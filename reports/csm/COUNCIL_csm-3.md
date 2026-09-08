# COUNCIL: CSM-3 cadence review (2026-09-08)

**n = 5 advisors** (The Executor, The Outsider, The Contrarian, The First
Principles Thinker, The Expansionist) · **n = 5 peer reviewers** (A–E) ·
1 chair.

## Run log

- **Advisor round**: all five advisor responses are **recovered verbatim**
  from their completed runs. The Contrarian (run `acb8974c`, workflow
  `1116ad37`) crashed after advisor 1 on a sandbox-global error, so its
  response was recovered from the run and re-wired into the runner (commit
  `743e0f1`); the other four (`fba1af9e`, `523a4478`, `fc56a417`,
  `cc7fbf19`, workflow `ffe7b645`) completed, but that workflow crashed at
  peer-a: the reviewer agent has no bash for the verification commands, so
  the five peers + the chairman run fresh on delegate (commit `a2734be`).
  Receipts: `reports/csm/council-csm3/adv-*-run1.md` (5 files,
  chair-confirmed present).
- **Peer + chair round**: fresh, this record.
- **Chair verification (2026-09-08, raw):** before recording, every
  load-bearing claim was re-verified in-tree (house rule: a council that
  cannot be verified against the store did not happen):
  - `git log --oneline`: `2c80867` (gates re-baselined on the 1,249 tree)
    predates `f93d396` (CSM-3); both exist; order `2c80867` → `858a4ef` →
    `f93d396` → `514ddaf`.
  - `reports/csm/panel_csm.json`: 17,181 panel rows + 200 held-out, 0
    overlap, panel min 6 words, stamped hash `e3d737205cd07245…`;
    recomputed sha256 of the panel rows with the exact `_panel_hash` recipe
    (`json.dumps(rows, ensure_ascii=False, sort_keys=True)`,
    `span_recall.py:262-270`) = `e3d737205cd07245…` (match). The side file
    `panel_csm.json.heldout.json` is a **bare 200-item list**; the `--panel`
    loader (`cli.py`, `data["panel"]`) raises `TypeError` on it (chair
    reproduced).
  - `pytest tests/ --collect-only -q` = **1,253** tests (1,249 + 4 CSM-3);
    `tests/test_span_recall.py` = 12 tests. `CLAUDE.md:320` +
    `.pi/skills/scriptengine-gates/SKILL.md:24` still pin **1,249** (stale,
    peer-E finding, chair-confirmed).
  - Legacy path: the `--probe` branch body in `cli.py` is whitespace-identical
    to `f93d396^` (only `if probe:` → `elif probe:` reindent + table title
    `"Span recall:"` → `"Chunk containment:"`); the legacy `recall()` tail in
    `span_recall.py` is byte-identical (chair difflib-verified both).
    `chunk-containment --series jjk` rc=0, **48,572/48,572**, 0 unreachable
    (chair re-ran; `span-recall` alias gives identical numbers).
  - Floor: `series/csm/overrides.yaml` D5-floor comment (≈ lines 31–43)
    records the <6-word exclusion, decided per ruling 4b before pinning;
    chair census against `series/csm/facts.db`: min_words=1 = **18,157**
    lines, min_words=6 = **17,382** tier-0 occurrences = **17,381 unique**
    (title,section,sentence) rows (one line duplicates inside its section),
    sub-6-word = **775, all in-chunk** (0 missing at min_words=1);
    sub-floor section histogram: Manga Chapters 133, Chapters 114, arc
    lists, Summary 44, 3rd/1st/2nd Popularity Poll 41/29/29 — so "all
    chapter/volume-list rows" is loose. `overrides.yaml:42` says "17,382
    probes" (the occurrence/unique conflation, chair-confirmed).
  - Roster door: `api/context.py:310-320` — the roster bundle carries
    content in `members`/`passages` with `"beats": []` and
    `truncated = len(members) < len(roster.members)`;
    `span_recall.py:227-237` `served_text()` flattens only
    `beats/facts/relations/participants`; `returned_docs` is built from
    `bundle.get("beats", [])` → a roster probe can **never** verdict HIT
    (TRUNCATED if the member list is budget-capped — that check precedes
    MISS_DOC in the verdict ladder — else MISS_DOC). Chair code-verified;
    The Outsider's live probe (31 members, 0 served chars) is the receipt.
  - Hash echo gap: `cli.py:2130` passes `panel_hash=data.get("hash")` (the
    pin's **stored** hash) and the report echoes it (`span_recall.py:456`) —
    the docstring's "a sweep that reports a different hash did not run the
    panel it claims" is unenforced.
  - Series names in `.py` (chair grep): **new in CSM-3**:
    `span_recall.py:289` ("CSM: 775 lines…") and `cli.py:2046` ("renamed
    from `span-recall` in CSM-3(f)"); **pre-existing** (exception
    candidates, same class as the `default="jjk"` ruling):
    `relation_coverage.py:172` (`default="csm"`), `audit_declarations.py:40`
    (SERIES tuple), `question_sheet.py` csm entries,
    `build_relation_bank.py:9` (docstring example).
  - `plan/SWITCHPOINT.md`: lines 15/91/292 say "~51 GPU-h", line 82 says
    "17,181 × 3 ≈ 58 GPU-h" — internally inconsistent (chair grep).
  - `git status`: `reports/2026-09-08-0956/` (canon-opm receipt:
    `answers.md`, `canon_scores*.json`, `eval.json`, `REPORT.md`,
    `run.json`) is **untracked**.
  - `api/main.py:79`: `mode: Literal["qa", "narrative", "roster", "auto"]`.
  - `reports/comprehension/GATE.md` CSM section (lines 719–749): gate
    re-baseline table on the 1,249 tree + the CSM-3 done-criteria listing
    "§7's four pilot cost numbers produced and carried to the
    done-declaration".

## The Question

CSM 100% campaign (ScriptEngine repo, /home/goblin/ScriptEngine) — cadence council (standing rule 3a: review the fixes just made, before the next item starts).

Just completed:
(1) Gate re-baseline on the 1,249 tree (gpu-gate3 100k+CUDA side session, receipt reports/csm/GATE_REBASELINE_2.md, commit 2c80867): all four standing gates PASS on CUDA (pytest 1,249/1,249 incl. the 6 VRAM-sensitive test_context cases; eval jjk 31/31; span-recall jjk 48,572/48,572 offline + 390/400 live probe; canon opm 10/16 exact, 236/236, 79.0%). CLAUDE.md + the gates-skill baselines rewritten (1,242 -> 1,249); the CSM gate section opened in reports/comprehension/GATE.md as the live record.
(2) CSM-3 (commit f93d396) — D5 measurement infrastructure, the four §2a traps: (a) pinned hashed probe panel — build_panel() in scriptengine/eval/span_recall.py (deterministic (title,section,sentence) order, sha256 hash stamped, seeded 200-row held-out split written to a side file the executor never opens; the csm panel is pinned at reports/csm/panel_csm.json, hash e3d73720…, 17,181 sweep + 200 held-out = 17,382 tier-0-eligible lines); (b) wired resume — the pinned recall() path keys done on (title,sentence), rewrites the results jsonl (no append-dup), re-probes transient ERROR rows, crash-tolerant .new sidecar; (c) hit_rate divides by the FULL panel denominator, not rows run; (d) all three doors — the --door CLI option forces the /context mode param (qa | roster | narrative) with a per-door sweep_<door>.jsonl, plus --sanity N whose zero-hit subset halts with exit 3 (council addendum: per-door sanity floor); plus (f) the tier-0 rename span-recall -> chunk-containment (span-recall kept as alias, both registered + tested); and the <6-word short-line floor decided BEFORE panel pinning per ruling 4b: the exclusion is recorded, not silent — CSM census of 775 sub-6-word lines (all tier-0-eligible, all chapter/volume-list rows like "College Fund 158.") recorded in series/csm/overrides.yaml. 4 new tests; pytest 1,253 (1,249 + 4) green (CPU run; the 6 VRAM cases pass on CPU in 127 s).

Standing campaign rules to judge against: measurement-infra-only pass (zero gold authoring); raw receipts, never "100%" prose; no series name in any .py (per-wiki handling in series/csm/overrides.yaml or tools/csm/ only); the JJK baseline stays untouched (the legacy --probe 400 JJK gate path must behave identically — verify it); §9a — the agent that made the fix never runs the sweep that grades the fix (CSM-4, the exhaustive 17,181 x 3 doors sweep, must run in a fresh 100k-mode side session via the tier-2 gpu-handoff chain); no CPU fallback for jobs (CPU = the :8000 service + <15 min jobs only); council claims are DB-verified before recording.

Judge: (a) does CSM-3 actually close the four §2a traps AND the council addendum done-criteria (per-door sanity floor, floor decided pre-pinning, tier-0 rename, §7 pilot numbers carried), or is any criterion silently unmet? (b) is the <6-word floor decision (record the exclusion) honest against the plan's "no matter how small" contract words, or does D5 close with in-scope lines out of scope? (c) does the legacy --probe 400 JJK standing-gate path still behave identically (no JJK regression)? (d) what must be fixed or added BEFORE the CSM-4 exhaustive sweep starts (spec design, sanity-floor policy per door, GPU batching/resume, results handling, the 58-GPU-h estimate vs the measured 17,181 panel)?

Response-letter to advisor mapping: A=The Executor, B=The Outsider,
C=The Contrarian, D=The First Principles Thinker, E=The Expansionist.
Peer-reviewer letters A–E are reviewer ids (each reviewed ALL five
responses), not response ids.

## Advisor responses (named, verbatim)

### The Executor (response A)

**(a) All four traps closed in code, nothing silently unmet.** Trap 1: deterministic `(title,section,sentence)` order, recomputed sha256 matches the `e3d73720…` stamp, held-out 200 disjoint + side file. Trap 2: closed on the pinned path — `(title,sentence)` key, rewrite-not-append, ERROR re-probe, idempotence tested; the legacy `--probe` path still appends (recorded exception in GATE_REBASELINE_2, not silent). Trap 3: full-panel denominator. Trap 4: the door forces the API's `mode` param (all three values accepted, verified `main.py:79`), per-door `sweep_<door>.jsonl`, `--sanity` → exit 3. Addendum: sanity floor ✓, pre-pinning floor decision ✓, tier-0 rename ✓ (both names registered + tested); §7's four pilot numbers are item 8's deliverable (items 4/6) — on the todo list, carried, not silently dropped. **One gap:** the sweep stamps the pin file's *stored* hash, not a recomputed hash of the rows it loaded — an edited `panel_csm.json` would report the stale hash. One-line recompute-and-compare before CSM-4 starts.

**(b) Honest against the ruling, not against the plan's original words.** Ruling 4b sanctioned "record the exclusion in the CSM audit," and that is what landed: 775 lines verified (all in-chunk, all chapter/volume list rows), recorded in `series/csm/overrides.yaml` with the census. D5 closes with 775/18,157 (~4.3%) out of scope — but the 6-word floor is a property of the measurement regime (the JJK 48,572 gate runs the same floor), so it is a declared boundary, not a CSM dodge. Accept it; re-including 1–5-word list rows would only burn GPU on ranking noise.

**(c) Identical.** The probe branch is byte-identical (re-indented to `elif`), legacy `recall()` untouched (seed-7, 400, append mode); both names registered; `chunk-containment` and `span-recall --series jjk` both rc=0, 48,572/48,572, same numbers (cosmetic table-title change only). JJK `recall_verbatim.jsonl` is clean in git. Residual: each JJK gate re-baseline re-appends 400 lines — the recorded-exception ritual persists, which is fine, it is documented.

**(d) Before the 58-GPU-h sweep (17,181×3×4s ≈ 57h — the estimate holds against the measured panel):**
1. **Per-door sanity policy must be ruled in *this* council, not the side session:** N per door (propose 100 = first-100-unprobed, ~7 min each) + the exit-3 disposition per door: qa door 0-hits = G-CSM-2 → route to CSM-7, document the floor, do not run the sweep; roster/narrative 0 = documented floor only if it is a corpus property.
2. **Batching/resume:** one 100k-mode side session per door (~19h each; resume is wired — sidecar + rewrite — so re-check panel hash + row count at every session boundary; `:8000` on CUDA in 100k mode, one copy, fits per gpu-gate3). 58h is never a CPU job.
3. **Door order: qa → narrative → roster.** The roster door on verbatim sentences is the most likely structural zero — let sanity catch it in 7 minutes, not after a 19-hour run.
4. **Results handling:** filter `MISS_DOC`/`MISS_SPAN` rows out of the three `sweep_<door>.jsonl` into a classed triage file (jq one-liner suffices; file it in `tools/csm/` if it survives contact with the data); halt conditions per item 7.
Monday morning, first: the three sanity runs (3×~7 min, one 100k session, zero panel spend) — then schedule the door batches.

**Verified:**
- `git log --oneline -15`; `git show --stat f93d396` and `2c80867` (commit scope: CSM-3 touched only `span_recall.py`, `cli.py`, 4 tests, panel files, csm overrides, CLAUDE.md — no JJK paths)
- `git show f93d396 -- scriptengine/eval/span_recall.py` (pinned branch added; legacy `panel is None` body untouched) and `git show f93d396^:scriptengine/cli.py` vs current (probe branch byte-identical modulo reindent)
- `python3` one-liner on `reports/csm/panel_csm.json`: recomputed sha256 of panel rows = stamped `e3d737205cd07245` (match); rows in sorted order; held-out file 200 rows, 0 overlap; 0 sub-6-word rows in panel
- `scriptengine/.venv/bin/python -c` via `sr._corpus`/`sr.index_coverage` on `series/{csm,jjk}/facts.db`: csm 775 sub-6-word lines (all in-chunk), tier-0 17,382 covered / 0 missing; jjk 48,572/48,572
- `scriptengine/.venv/bin/python -m scriptengine.cli chunk-containment --series jjk --out /tmp/csm3check` → rc=0, 48,572/48,572; same via `span-recall` → rc=0, identical numbers (outputs kept in /tmp, tree untouched)
- `grep -n "mode" scriptengine/api/main.py` → `Literal["qa","narrative","roster","auto"]` at line 79
- `git status --porcelain` (JJK `recall_verbatim.jsonl` clean; only the known master-work files dirty) + `git log -1 -- reports/2026-09-08-{0746,0752,0824}` (receipts committed @ `1f46f33`)

*(Chair note: full run + receipt in `reports/csm/council-csm3/adv-the-executor-run1.md` (run `fba1af9e`).)*

### The Outsider (response B)

**(a) One criterion is silently unmet: the roster door is functionally dead.** The other traps are closed — I recomputed `build_panel("csm")` offline and it reproduces the pinned hash `e3d73720…` (17,181 + 200 = 17,382); resume idempotence and full-denominator `hit_rate` are tested; the rename + alias are registered. But `served_text()` only flattens `beats/facts/relations/participants`, while the roster bundle carries its content in `members[].text` + `passages[]` (and `returned_docs` is built from `beats`, empty for roster bundles). Live probe on a CSM panel line, door=roster: 31 members returned, **0 chars** of served text → every roster probe structurally verdicts MISS_DOC and `--sanity` halts exit 3. The tests pass because they fake a `beats`-shaped bundle. Two-line fix (flatten `members`/`passages`; include member titles in `returned_docs`) + one test, before CSM-4. Minor: the panel hash is *reported*, never re-verified against the rows actually probed — the docstring's "a sweep that reports a different hash did not run the panel it claims" is unenforced (one `hashlib` compare would make it real).

**(b) Honest, with two caveats.** Ruling 4b explicitly sanctions "record the exclusion"; the 775-line census is on disk (`overrides.yaml` 35–43) and matches my recount, all in-chunk, floor recorded in panel metadata. Caveats: the done-declaration must carry the exclusion line so "100%" reads as 17,181 in-panel + 775 declared out; and "all chapter/volume-list rows" is slightly loose — the 775 include 44 Summary rows, 41 poll rows, and SFX tokens ("Barf!", "Boom!").

**(c) Identical.** Diff of the legacy branch shows only the table-title rename ("Span recall:" → "Chunk containment:") and `if probe:` → `elif`; seed-7 shuffle, unwired `done`, append-mode jsonl, `hit_rate`/total all untouched; `recall_verbatim.jsonl` is clean in the tree.

**(d) Before CSM-4:** (1) the roster-door fix above; (2) re-estimate the 58-GPU-h from a *measured* per-probe rate (4 s is a JJK number) — the sanity-100 run should produce it, recorded in GATE.md; (3) pre-declare the sanity-floor policy (N per door, and per-door acceptable hit floors) — G-CSM-2 says the qa passage leg is dead wholesale on CSM, and a zero-hit halt only catches a *completely* dead door; (4) 100k switch first (262k can't co-locate a sustained job), then the tier-2 side session per §9a.

**Verified:** `git log -10`; `git show --stat f93d396 2c80867`; `git status`; `git diff f93d396^ f93d396` (span_recall.py, cli.py removed-line scan); venv python: `build_panel("csm")` recompute (hash match, 17,382), sub-6-word census (775, word-dist 1–5, breadcrumb dist), panel dup-key check (0); `tail` of `panel_csm.json` (hash/size metadata); `grep csm` over project `.py` (zero; only `.venv` pygments); `api/main.py` + `api/context.py` (mode `Literal["qa","narrative","roster","auto"]`; roster→narrative fallback gated on `mode=="auto"`; roster bundle keys); live `POST /context` (csm, 1 line × 3 doors; server pid 80967 on CPU) — qa HIT, roster 31 members/0 served chars, narrative 2,624 chars/no hit; reads: `GATE_REBASELINE_2.md`, `COUNCIL_csm-campaign.md` + addendum, `COUNCIL_csm-1b-2.md`, `span_recall.py`, `cli.py` 1998–2219, `tests/test_span_recall.py`, `series/csm/overrides.yaml` 31–50, `plan/SWITCHPOINT.md` CSM-3 line, `reports/comprehension/GATE.md` CSM section.

*(Chair note: full run + receipt in `reports/csm/council-csm3/adv-the-outsider-run1.md` (run `523a4478`).)*

### The Contrarian (response C)

**(a)** Traps 1–3 are genuinely closed and I verified them: the panel hash reproduces byte-for-byte from the current tree (rebuild == `e3d73720…`), resume idempotency + full-denominator `hit_rate` are tested, and the doors are wired for real (API `mode` param exists; forwarding tested at the `_ask` seam). But "closed" is plumbing, not measurement — no CSM door has ever produced a number; roster/narrative first-numbers don't exist until CSM-4. Addendum: sanity floor ✓ (exit 3), pre-pinning floor decision ✓ (recorded; arithmetic typo below), rename ✓ (tested). Criterion 4 (§7 pilot numbers) is **silently unmet**: CSM-3 cannot produce it (T0 numbers need item 6e; new-gaps need the loop), no ledger exists, yet GATE.md lists it under CSM-3's done-criteria and the SWITCHPOINT DONE line implies all four were met.

**(b) Honest.** The 775-line exclusion is real — I re-derived 775, all inside chunks — and it took the ruling's sanctioned "record" branch, in overrides.yaml + pin metadata. Two defects: the receipts conflate denominators — 17,181+200 = **17,381**, but commit message, overrides.yaml and SWITCHPOINT all say "17,382" (that's the tier-0 *occurrence* count; one line duplicates inside its section). Fix the equation; the done-declaration must say "17,381 unique rows, 775 excluded-and-recorded." The "all chapter/volume-list rows" characterization is asserted, not line-audited — dump the 775 to a receipt.

**(c)** Verified byte-identical: the legacy `recall()` branch and the CLI probe block are unchanged from `f93d396^`; module tests 12/12. No JJK regression — but the append-dup trap *still lives in the JJK standing-gate path* (the GATE_REBASELINE_2 promise "fix lands in CSM-3(b)" is pinned-path only); the done-declaration re-baseline will append another +400 dup lines. The canon-run raw receipt `reports/2026-09-08-0956/` is still untracked.

**(d) Before CSM-4:** (1) **no sweep spec exists** (SWITCHPOINT's one-liner is not a spec). It must fix: per-door command sequence (`--sanity N` first run only — re-running it mid-sweep checks a moving window and false-halts low-yield doors; resume runs drop it); **pre-declared per-door floor policy** — the zero-hit floor only protects *dead* doors; roster/narrative are structurally low-yield on verbatim-line probes, so "miss file empty" is unattainable on 2 of 3 doors without documented per-door floors (qa = oracle, JJK's 97.5% band; roster/narrative = measured floors), or the closure loop's regression-halt grinds; (2) **the 58-GPU-h is still fiction**: 17,181×3×4s/3600, but 4 s/probe is an unmeasured assumption (JJK's warm probe measured 0.47 s) — the sanity runs must measure CSM s/probe and re-estimate (≈8 h at JJK's rate); (3) **the held-out 200 have no CLI door** (`--panel` reads `data["panel"]` from a dict; the heldout file is a bare array → crash) — name the non-executing runner and add a `tools/csm/` wrapper; (4) sequential 100k+CUDA one-copy co-location, sidecar resume-loop until probes == 17,181, raw per-door counts + panel hash into GATE.md.

**Verified:**
- `git log --oneline -8`; `git show --stat f93d396 2c80867`; `git show f93d396^:` diffs of `span_recall.py` legacy branch + CLI probe block (byte-identical); python: `build_panel("csm")` rebuild (hash == e3d73720…, 17,181+200) + independent sub-6-word count (775, all in chunks); python: `panel_csm.json` metadata, recomputed sha256 of panel rows, overlap/dup/floor checks; `pytest tests/test_span_recall.py -q` (CPU, 12 passed); `python -m scriptengine.cli chunk-containment --series csm` (17,382/17,382, rc=0); grep: `scriptengine/api/main.py` mode param, `reports/comprehension/GATE.md` CSM section, `plan/SWITCHPOINT.md` CSM-3/4 lines, `git status --short`; reads: `COUNCIL_csm-campaign.md`, `COUNCIL_csm-1b-2.md`, `GATE_REBASELINE_2.md`, `span_recall.py`, `cli.py` (1990–2205), `test_span_recall.py`, `series/csm/overrides.yaml` floor comment.

*(Chair note: full run + receipt in `reports/csm/council-csm3/adv-contrarian-run1.md` (run `acb8974c` — the crashed-then-recovered run).)*

### The First Principles Thinker (response D)

**(a)** The four traps are closed and re-verified: hash recomputes exactly (e3d73720… = sha256 of the pinned rows), 17,181+200 disjoint, resume/ERROR-reprobe/atomic-rewrite all present, full-denominator hit_rate. Addendum: sanity-halt (exit 3) wired; floor decided + recorded; rename + alias tested. Silently unmet, two soft items: (1) "the executing agent never opens" the held-out is discipline, not enforcement — the side file is committed to git, §9a rests solely on CSM-4 running in the fresh side session, and nothing consumes the held-out 200 yet (dormant artifact until a named consumer); (2) **new** CSM-3 code puts a series name in a shared `.py`: `span_recall.py:289` docstring cites "CSM: 775 lines" — same category as the `default="jjk"` exception, but fresh, not pre-existing. Move the number into `overrides.yaml` (the census already lives there) or record the exception.

**(b) Honest.** I verified all 775 sub-6-word lines are chapter/volume-list rows ("156.", "Aging's World 181.") and **all 775 are in-chunks, 0 outside** — the exclusion is recorded (overrides comment + panel `min_words` + CLI print), not silent. First-principles caveat: `min_words=6` is the tier-0 default, so those lines are out of scope of *both* tiers; "rc=0" and "miss file empty" will forever be claims over 17,381 lines, not the corpus. Acceptable as a declared, measured boundary — but the done-declaration must carry the 775 number or "no matter how small" is never answered. Pre-pinning order is unprovable from the single commit f93d396; the record (ruling 4b + census) shows the decision was conscious, which is the substance.

**(c) Identical.** The legacy `recall()` tail is byte-identical to the pre-CSM-3 tree; `_ask` gains the `mode` key only when a door is passed and the legacy `--probe` branch never passes one — so HTTP payload, seed-7/400 sampling, and the printed table are unchanged. The probe-jsonl append-dup remains the documented exception; the gate number comes from the table, not the jsonl.

**(d) Before CSM-4:** (1) sanity policy — pick N per door, run live `--sanity` on all three doors in the 100k side session before the full sweep; note the subset is the panel's *first* N (title-sorted, A-biased) — fine for a dead-door guard, declare it; a near-dead qa door (G-CSM-2) can still pass sanity and burn the hours — record that as accepted. (2) Concurrency: the client is a single-threaded urllib loop, so 17,181×3×4s ≈ 58 GPU-h *wall*; decide on 2–4 parallel workers (server threadpool; torch releases the GIL; ~5.3 GB still fits the 100k headroom) or accept ~2.4 GPU-days. (3) SWITCHPOINT still says "~51 GPU-h" (lines 15, 91) — the plan says the measured panel replaces the estimate; update and carry it to the §7 pilot number. (4) Fix/record the :289 docstring. (5) Name the held-out's consumer.

**Verified:**
- `git log --oneline -8`; `git show --stat f93d396` (files touched: panel + heldout committed, span_recall.py, cli.py, overrides.yaml, 4 new tests)
- `python3` json one-liner on `reports/csm/panel_csm.json` + `.heldout.json`: sha256 recompute = e3d73720… (match), 17,181+200 rows, sweep∩heldout = ∅, no dupes
- `scriptengine/.venv/bin/python` offline against `series/csm/facts.db`: 775 sub-6-word non-boilerplate lines, 775 in-chunk / 0 missing; 17,381 unique tier-0-eligible rows = exact set-equality with the pinned panel (0 gone, 0 new since pin); sampled the sub-6-word rows (all list rows)
- python difflib of `scriptengine/eval/span_recall.py` current vs `git show 118ab37`: legacy `recall()` tail IDENTICAL; `_ask` differs only in the conditional `mode` key
- `grep -i csm` in `span_recall.py`/`cli.py` (found the :289 docstring); `grep 1,249` in `CLAUDE.md` and `.pi/skills/scriptengine-gates/SKILL.md` (both rewritten); `grep 51` in `plan/SWITCHPOINT.md` (stale estimate lines 15, 91); `git status --porcelain series/csm/` (clean, facts.db Sep 7)
- read: `COUNCIL_csm-campaign.md` (item 3 scope/done + addendum), `COUNCIL_csm-1b-2.md` (rulings), `GATE_REBASELINE_2.md`, `span_recall.py` (full), `cli.py` chunk-containment command, `tests/test_span_recall.py` (4 new tests), `series/csm/overrides.yaml` (D5 floor comment), `reports/comprehension/GATE.md` (CSM section)

*(Chair note: full run + receipt in `reports/csm/council-csm3/adv-the-first-principles-thinker-run1.md` (run `fc56a417`).)*

### The Expansionist (response E)

**(a) All four traps + addendum criteria met — and the infra is bigger than the record says.** Panel hash recomputes (e3d73720… matches the pin), sweep/held-out disjoint, floor respected; wired resume, full-denominator hit_rate, and the exit-3 sanity halt are in code with 4 tests (1,253 collected). The upside everyone is missing: it's all series-agnostic — `--make-panel`/`--panel`/`--door` take any series. CSM-3 is the first exhaustive tier-1 instrument any of the 8 wikis has had; JJK's 400-probe shortcut becomes optional, and P6 inherits the hashed, resumable sweep for free. CSM-4 dry-runs an instrument seven other corpora will reuse.

**(b) Honest.** It's ruling 4b's own authorized option, and the census verifies: 775 sub-6-word lines, all in chunks, list-shaped sections (Manga Chapters 133, Chapters 114, poll rows). The floor is a dial, not a wall: `min_words` is a parameter + CLI option, recorded in the panel metadata — a later re-pin at `min_words=1` re-includes all 775 with zero code.

**(c) No JJK regression:** the legacy branch is untouched (`if probe:` → `elif probe:`, title change only); seed-7, sample=400, append-mode jsonl preserved as the recorded exception; the gate re-ran identically at 390/400 on the 1,249 tree before CSM-3. Upside: a pinned 400-line JJK sub-panel (400-row JSON + `--panel`) upgrades the standing gate to resume + hash + full denominator, zero code.

**(d)** (1) Sanity policy: run `--sanity 200` per door in one ~40-min session — a healthy door has near-zero probability of a zero-hit 200-subset, a dead qa leg (G-CSM-2) trips exit 3; one cheap session de-risks the whole sweep. (2) 58h is now the *measured* number (17,181 × 3 × 4s ≈ 57.3h), replacing the 51h estimate — plan 6–9 chained 100k sessions, one per door; a dead door then costs only its sanity run. (3) A C-side task brief (gpu_gate3_task.md shape) naming per-door commands + the GATE.md landing spot; §9a: fresh session, never the f93d396 author.

**Verified:**
- `git log --oneline -8`; `git show --stat f93d396`; `git show --stat 2c80867`; `git show f93d396 -- scriptengine/cli.py` (full CLI diff: legacy branch vs new sweep branch)
- python one-liner: `json.load` of `reports/csm/panel_csm.json` + `panel_csm.json.heldout.json` — recomputed `sha256(json.dumps(panel, sort_keys=True))` = e3d737205cd07245… = pinned hash; panel 17,181 / held-out 200 / overlap 0 / min line 6 words
- python one-liner against `series/csm/facts.db` via `span_recall._corpus("csm")`: 775 sub-6-word lines in non-boilerplate sections, all 775 present in a chunk; section histogram (Manga Chapters 133, Chapters 114, arc lists, poll rows)
- `pytest tests/ --collect-only -q` → 1,253 tests collected
- read: `scriptengine/eval/span_recall.py` (build_panel, pinned recall branch, legacy branch), `scriptengine/cli.py` L1995–2220 (both command registrations, sweep/probe branches), `tests/test_span_recall.py`, `series/csm/overrides.yaml` (floor decision comment), `reports/csm/panel_csm.json` metadata, the four context files

*(Chair note: full run + receipt in `reports/csm/council-csm3/adv-the-expansionist-run1.md` (run `cc7fbf19`).)*

## Peer reviews (verbatim)

### Peer A

**1. Strongest: B.** Found the load-bearing defect no one else saw: the roster door is structurally dead — the roster bundle returns `beats: []` with content in `members[].text`/`passages[].text`, but `served_text()` only flattens beats/facts/relations/participants (0 chars served, verified) and `returned_docs` derives from beats, so every roster probe structurally verdicts MISS_DOC and `--sanity` halts exit 3; no test covers a roster-shaped bundle. B also caught the unenforced hash stamp and the unmeasured 4 s/probe. A is runner-up (hash gap, spec) but predicted the roster zero as a possible corpus property, not a code bug.

**2. Biggest blind spot: E.** Misses the roster door's structural zero — E's `--sanity 200`-per-door plan halts exit 3 on the roster door, and E's "a healthy door has near-zero probability of a zero-hit subset" is false there. E also calls 58h "measured" when 4 s/probe is an unmeasured assumption (JJK's own gate measured ~0.45 s/probe), and chases P6/JJK-reuse upside that is YAGNI against a blocking defect.

**3. All five missed: TRUNCATED has no disposition policy** — no per-door floor, triage class, or done-criteria definition (A's triage filter even excludes TRUNCATED rows). Material after B's fix: the 6000-token budget truncates large rosters, so a line inside a truncated member's text still isn't served; the roster floor needs a budget-cap ruling like the 775-line floor.

**Verified:** read `scriptengine/eval/span_recall.py` (full: `served_text`, pinned `recall`, :289 "CSM: 775" docstring), `scriptengine/api/context.py` roster/qa return keys, `cli.py` panel/sanity/probe branches; venv run (roster bundle → 0 served chars → MISS_DOC); recomputed `panel_csm.json` sha256 = e3d73720… (17,181+200=17,381); heldout file is a bare 200-item list (`data["panel"]` crashes); `git show f93d396` message, `GATE.md` CSM done-criteria, `SWITCHPOINT` 51h lines, `git status` (canon receipt `reports/2026-09-08-0956/` untracked).

### Peer B

I have verified all the load-bearing claims. Confirmed: B's roster-door defect (code-level), D's line-289 series-name in a shared `.py`, C's 17,381-vs-17,382 arithmetic (tier-0 occurrences=17,382, unique rows=17,381), the legacy `recall()` body byte-identical, the held-out file being a bare array the `--panel` loader can't read, the 775 census (all in-chunk; includes Summary/poll rows, so "all chapter-list" is loose), and SWITCHPOINT's 51-vs-58 GPU-h inconsistency.

**1. Strongest: B.** Only B live-probed the real roster bundle and found the roster door functionally dead: `served_text()` flattens only `beats/facts/relations/participants`, but the roster bundle carries content in `members[].text`/`passages[]` with `beats: []` (and `returned_docs` from empty `beats`), so every roster probe verdicts MISS_DOC and `--sanity` exits 3. The new tests fake a `beats` bundle, so they pass while 1/3 of the CSM-4 sweep is broken. A/C/D/E all said "traps closed" without testing the roster shape.

**2. Biggest blind spot: A (Executor).** A will run CSM-4 and proposed "qa→narrative→roster, let sanity catch it", treating the roster zero as an acceptable "documented floor" — misclassifying a 2-line harness bug as a corpus boundary, planning to sweep with a third of the doors broken.

**3. All five missed:** the TRUNCATED verdict. Even after B's roster fix, the roster door caps `members` at the token budget, so a line in a truncated-away member verdicts TRUNCATED (not HIT); hit_rate counts only HIT, so the roster floor reads "dead" though the lines are served. None addressed TRUNCATED, or defined the final D5 number (union-over-doors vs the auto router) rather than per-door hit_rate.

**Verified:**
- `git log --oneline -15`; `git status --porcelain`; `git show --stat f93d396` + `2c80867`
- read `scriptengine/eval/span_recall.py` (served_text, pinned/legacy recall, build_panel) + `grep -n CSM` → line 289; `grep -n "roster|members|passages|beats" api/context.py` + read roster bundle return (L300–340: `beats: []`, content in members/passages)
- panel hash recompute = `e3d73720…` (17,181+200, overlap 0, min_words 6); `index_coverage('csm')` → 17,382 occurrences / 17,381 unique
- 775 sub-6-word census (all in-chunk) + section histogram (Manga Chapters 133, Chapters 114, Summary 44, 3rd Poll 41); legacy `recall()` body byte-identical diff vs `f93d396^`; CLI `--panel` loader (`data["panel"]`) vs bare-array held-out; `grep 51|58 plan/SWITCHPOINT.md`

### Peer C

**1. Strongest: B.** Only B probed the doors end-to-end and found the load-bearing defect: the roster door is structurally dead — the roster bundle hardcodes `beats: []`, `served_text()` flattens only `beats/facts/relations/participants` (ignoring `members[].text`/`passages[]`), and `returned_docs` is built from `beats` only, so every roster probe verdicts MISS_DOC and `--sanity` always halts exit 3. The 4 tests pass because they fake beats-shaped bundles. B's pre-CSM-4 ordering (roster fix → measure s/probe → declare floors → 100k switch) is the right one.

**2. Biggest blind spot: E.** All upside, zero negative findings: it missed the dead roster door, the 17,381/17,382 conflation, and its `--sanity 200` policy ("a healthy door won't zero-hit 200") is unsound for structurally low-yield verbatim-line probes on roster/narrative — it would false-halt even a *fixed* door. Its "58h is now the measured number" also ignores 4 s/probe is an unmeasured JJK figure.

**3. All five missed:** (a) `truncated` means different things per door (roster = member-list capped, qa/narrative = text truncated) — the sweep's TRUNCATED verdict ladder is miswired across doors; nobody inspected it per door. (b) The series-name-in-`.py` leak isn't just `span_recall.py:289` (D's one instance) — `cli.py:2046` ("renamed in CSM-3(f)") is a second violation D's fix would leave standing.

**Verified:**
- `git log -8` + `git show --stat f93d396`; read `span_recall.py` (served_text, pinned recall, `:289`); `sed`/`grep` on `api/context.py` 246–340 (roster payload `"beats": []`, `members`/`passages`), `api/main.py` (mode `Literal` line 79); venv python on `panel_csm.json`: sha256 recompute = e3d73720… (match), 17,181+200, overlap 0; `facts.db` census: 17,382 occurrences / **17,381 unique** rows, min_words=1 census 18,157; `grep -n csm` on span_recall.py/cli.py (`:289` + `cli.py:2046`); `grep` on `plan/SWITCHPOINT.md` (stale ~51 GPU-h lines 15/91/292 vs 58 at 82); `sed` GATE.md CSM-3 done-criteria; `grep panel` in cli.py (`--panel` reads `data["panel"]`).

### Peer D

**1. Strongest: B.** Only B found the load-bearing defect: the roster door is structurally dead. `served_text` (span_recall.py:222) flattens only `beats/facts/relations/participants`, but the roster bundle (context.py) serves content in `members[].text`+`passages[]` with `beats: []` — so `returned_docs` is always empty and no roster probe can ever verdict HIT (verified in code). B also demanded the measured per-probe rate and hash re-verification.

**2. Biggest blind spot: A.** A's 58h/3-door CSM-4 plan would have scheduled the structurally-dead roster door as a "documented floor" and treated 4s/probe (a JJK number) as measured. A also missed the :289 series-name violation and the 17,382/17,381 conflation.

**3. All five missed:** cli.py:2046's help text also embeds a series name ("renamed … in CSM-3(f)") — D's grep found span_recall.py:289 but scoped the rule violation to one file; the fix must cover both (or scope the rule to logic only). Also C's record defects (overrides.yaml:42 "17,382 probes"; untracked reports/2026-09-08-0956/) must land before the CSM-4 spec cites those numbers.

**Verified:**
- panel sha256 (ensure_ascii=False) = e3d73720… = stamped; 17,181+200 rows, 0 overlap, min 6 words
- span_recall.py:222-240 (served_text), 340-470 (pinned recall; `panel_hash=data.get("hash")` = stored, not recomputed)
- context.py:250-340 roster bundle keys (`beats: []`, members/passages)
- cli.py:2120-2138 (`data["panel"]`, sanity exit 3), 2157-2190 (legacy `elif probe:` append), 2046 ("CSM-3(f)")
- tier-0 csm: 17,382 occurrences / 17,381 unique tuples
- 775 sub-6-word lines, all in-chunk (Manga Chapters 133, Chapters 114, Summary 44, Polls 41/29/29)
- span_recall.py:289 "CSM: 775 lines"; SWITCHPOINT.md:15,91 still ~51 GPU-h (line 82: 58)
- `git status`: reports/2026-09-08-0956/ untracked

### Peer E

**1. Strongest: B.** Only one found the real blocker: the roster door is dead in code — `served_text()` flattens only `beats/facts/relations/participants`, but the roster bundle carries its prose in `members[].text`/`passages[]` with `beats: []` and `returned_docs` is built from `beats`, so a roster probe can never HIT. B verified live (31 members, 0 chars) and gives the two-line fix. A's "all traps closed" and E's "criteria met" sail past it.

**2. Biggest blind spot: A.** Verified the `mode` param is accepted but never looked at what the verdict sees for roster; its "roster 0 = documented floor" policy would launder the bug into a corpus boundary, and its door order runs the dead door last. A also endorses the unmeasured 4 s/probe ("the estimate holds"; C: JJK measured ~0.5 s, SWITCHPOINT still says 51 h).

**3. All five missed:** (i) the standing pytest baseline is stale — CLAUDE.md:320/SKILL.md:24 say 1,249 but the tree is 1,253 (f93d396 +4); the next gate run misfires until re-baselined. (ii) pinned resume re-probes only ERROR rows, so a post-fix validation sweep reusing `sweep_<door>.jsonl` reads back stale MISSes — CSM-7's fix becomes invisible; the spec must name a fresh results file per engine state.

**Verified:**
- `git diff f93d396^ f93d396` — span_recall legacy tail untouched; difflib: CLI probe branch identical modulo `if`→`elif` reindent; `chunk-containment --series jjk --out /tmp` → 48,572/48,572, rc=0
- read `span_recall.py` (served_text, pinned resume, `panel_hash=data.get("hash")` echo), `api/context.py` `_roster_context` (members/passages, `beats: []`)
- python: recomputed panel hash = e3d73720… (match), 17,181+200 disjoint; heldout file is a bare 200-array (`--panel` reads `data["panel"]` → TypeError, confirming C)
- grep: `CSM` in .py (span_recall.py:289 — D — and cli.py:2046, which D missed); "17,382" (overrides.yaml:42, SWITCHPOINT:78); "~51 GPU-h" (SWITCHPOINT:15/91); "1,249" (CLAUDE.md:320, SKILL.md:24; no 1,253 baseline anywhere)

## Where the Council Agrees

Verified-claim references are named with paths/commands (chair re-ran every one;
the full command list is in the Run log).

- **(a) Traps 1–3 are closed in code** — all five agree. Trap 1 (pinned hashed
  panel): chair recomputed the panel hash with the `_panel_hash` recipe
  (`json.dumps(rows, ensure_ascii=False, sort_keys=True)`,
  `scriptengine/eval/span_recall.py:262-270`) = stamped
  `e3d737205cd07245…`; 17,181 sweep rows + 200 held-out, 0 overlap, panel min
  6 words (`reports/csm/panel_csm.json`). Trap 2 (wired resume): the pinned
  path keys done on `(title,sentence)`, rewrites the jsonl via
  `_atomic_jsonl` (never append), re-probes ERROR rows, crash-tolerant `.new`
  sidecar (`span_recall.py` pinned `recall` branch; 12/12 tests in
  `tests/test_span_recall.py`, chair-verified 1,253 collected). Trap 3
  (denominator): `hit_rate` divides by the full panel size
  (`span_recall.py`, `"panel size (denominator)"` row in the CLI table). The
  legacy `--probe` path still appends — the recorded exception in
  `GATE_REBASELINE_2.md`, not silent (all agree).
- **Trap 4 (doors) is wired, but the roster door is functionally dead** —
  the `mode` param exists (`scriptengine/api/main.py:79`
  `Literal["qa","narrative","roster","auto"]`), per-door `sweep_<door>.jsonl`
  + `--sanity` exit-3 are in `cli.py`; but the roster bundle serves content in
  `members`/`passages` with `"beats": []` (`scriptengine/api/context.py:310-320`)
  while `served_text()` flattens only `beats/facts/relations/participants`
  (`span_recall.py:227-237`) and `returned_docs` derives from `beats` → a
  roster probe can never verdict HIT. Chair code-verified; The Outsider's live
  probe (31 members, 0 served chars) is the receipt. This is the load-bearing
  defect (clash 1 below).
- **Addendum done-criteria: sanity floor ✓, pre-pinning floor decision ✓,
  tier-0 rename ✓.** `--sanity` zero-hit → exit 3 is wired (`cli.py`); the
  floor decision is recorded in `series/csm/overrides.yaml` (D5 floor
  comment, ≈ lines 31–43) + panel `min_words` metadata; both `chunk-containment`
  and `span-recall` are registered and chair re-ran `chunk-containment
  --series jjk`: rc=0, 48,572/48,572, 0 unreachable (JJK baseline untouched,
  (c) verified). §7 pilot numbers: **not produced — and cannot be produced in
  a measurement-infra pass** (T0 numbers need item 6e; new-gaps need the
  closure loop). Carried, not silently dropped (clash 2).
- **(b) The <6-word floor decision is honest against ruling 4b** — the
  exclusion is recorded, not silent: chair census against
  `series/csm/facts.db` = 775 sub-6-word lines (18,157 total at min_words=1,
  17,382 tier-0 occurrences at min_words=6), **all 775 in-chunk** (0 missing at
  min_words=1), recorded in `series/csm/overrides.yaml` + panel metadata +
  CLI print. Two caveats agreed across B/C/D + peers: the done-declaration
  must carry the 775 number ("17,181 in-panel + 775 declared out"), and "all
  chapter/volume-list rows" is loose — the census includes 44 Summary rows and
  99 poll rows (chair section histogram: Manga Chapters 133, Chapters 114, arc
  lists, Summary 44, polls 41/29/29).
- **(c) The legacy `--probe` 400 JJK path behaves identically** — unanimous:
  chair difflib-verified the `--probe` branch body in `cli.py` is
  whitespace-identical to `f93d396^` (only `if` → `elif` reindent + table
  title `"Span recall:"` → `"Chunk containment:"`) and the legacy `recall()`
  tail in `span_recall.py` is byte-identical (seed-7, sample=400, append-mode
  jsonl preserved); both command names registered; chair re-ran rc=0
  48,572/48,572. Residual (documented): the append-dup trap still lives in the
  JJK standing-gate path — each gate re-baseline appends +400 lines; recorded
  exception, the fix is pinned-path only.
- **(d) Universal pre-CSM-4 consensus:** the 4 s/probe figure is an
  **unmeasured JJK number** (JJK's own probe measured ~0.45–0.47 s), so
  "58 GPU-h" is an estimate, not a measurement (all five flagged in some form);
  the 100k switch precedes the sweep (262k cannot co-locate a sustained job;
  the 5.3 GB embedder+reranker fits the 100k headroom per gpu-gate3); CSM-4
  runs in a fresh tier-2 side session per §9a (never the `f93d396` author);
  no CPU fallback (a ~57 h job is never a CPU job).
- **The no-series-name-in-.py rule was broken by CSM-3 itself** — D flagged it
  (one instance), peers C/D caught the second; chair grep verified: **two
  new instances** (`span_recall.py:289` "CSM: 775 lines", `cli.py:2046`
  "renamed from `span-recall` in CSM-3(f)") plus pre-existing csm tokens
  (`relation_coverage.py:172` `default="csm"`, `audit_declarations.py:40`
  SERIES tuple, `question_sheet.py` entries) that are the same class as the
  recorded `default="jjk"` exception (1b-2 ruling: record, don't churn).

## Where the Council Clashes

1. **The roster door: a two-line code defect or a "documented floor"?**
   The Outsider (B): the door is structurally dead in `served_text()` —
   live-probed (31 members, 0 served chars); fix it (flatten
   `members`/`passages`; member titles into `returned_docs`) + one
   roster-shaped test **before** CSM-4. The Executor (A): "roster 0 =
   documented floor only if it is a corpus property" and door order
   qa → narrative → roster "let sanity catch it in 7 minutes." Peers
   A/B/D/E: A would **launder a 2-line harness bug into a corpus
   boundary** and sweep with a third of the doors broken. **Ruling (chair):**
   code defect — chair verified the code path end-to-end (roster bundle
   `beats: []` + `members`/`passages` at `context.py:310-320`; `served_text`
   at `span_recall.py:227-237`; `returned_docs` from `beats`). The roster
   door is fixed in code, with a roster-shaped test and a live re-probe of the
   line B used (31 members / 0 chars → must serve chars). A's door order
   survives only as the *sanity-run* order; the floor idea survives only as
   the per-door floor policy (clash 3).
2. **§7's four pilot numbers: "silently unmet" vs "carried".** The
   Contrarian (C): criterion 4 is silently unmet — CSM-3 cannot produce it,
   no ledger exists, yet `GATE.md` lists it under CSM-3's done-criteria
   (chair-verified at `reports/comprehension/GATE.md` lines 745–749) and the
   SWITCHPOINT DONE line implies all four were met. The Executor (A): item 8's
   deliverable, on the todo list, carried, not silently dropped. **Ruling
   (chair):** neither "met" nor "dropped" — **not producible at the CSM-3
   stage** (the infra pass has no T0-pilot and no closure loop to emit them).
   The GATE.md wording is misleading and gets fixed to "carried, owner
   CSM-4/CSM-7 + item 6e" (Ruling 5f). Not a CSM-3 blocker; it is a
   CSM-4/CSM-7 deliverable.
3. **Sanity-N and the floor policy for low-yield doors.** The Expansionist
   (E): `--sanity 200` per door; "a healthy door has near-zero probability of
   a zero-hit 200-subset." The Contrarian (C): the zero-hit floor only
   protects *completely dead* doors; roster/narrative are structurally
   low-yield on verbatim-line probes, so without documented per-door floors
   the closure loop's regression-halt grinds; also `--sanity` must be
   first-run-only (mid-sweep re-runs check a moving window and false-halt).
   The Executor (A): N=100 per door (first-100-unprobed, ~7 min each) +
   per-door exit-3 disposition (qa 0-hits = G-CSM-2 → route to CSM-7,
   document, don't sweep). Peers A/C: E's "healthy door" claim is unsound for
   structurally low-yield doors. **Ruling (chair):** pre-declare in the spec
   (not the side session): **N=100 per door** (first-100-unprobed; the
   title-sorted A-bias is declared), `--sanity` first-run-only per door
   (resume runs omit it); qa zero-hit → halt + G-CSM-2 disposition (route to
   CSM-7, document the floor, do not sweep qa); roster/narrative zero-hit
   *post-fix* → halt (harness or bundle is broken); non-zero low-yield →
   sweep proceeds and the **measured sanity rate becomes that door's
   pre-declared floor, recorded in GATE.md before the batch**.
4. **Is 58 GPU-h "measured"?** The Expansionist (E): "58h is now the measured
   number." The Outsider/Contrarian/First Principles (B/C/D): 4 s/probe is an
   unmeasured JJK figure (JJK's warm probe measured ~0.45–0.47 s; at that
   rate the sweep is ≈8 h, not 57 h); the sanity runs must measure CSM
   s/probe and re-estimate. Peer A: SWITCHPOINT is internally inconsistent
   (~51 at lines 15/91/292 vs 58 at line 82 — chair grep-verified). **Ruling
   (chair):** 58 h is an **estimate on an unmeasured rate**; the three sanity
   runs measure CSM s/probe, the re-estimate lands in GATE.md, and the
   SWITCHPOINT ~51 lines are fixed when the measured number replaces the
   estimate (Rulings 4 + 5c). Concurrency (single-threaded urllib loop) is a
   spec decision: if the measured rate is ≥1 s/probe, 2–4 parallel workers in
   the side session (server threadpool; torch releases the GIL; 5.3 GB fits
   the 100k headroom), else single-threaded.
5. **17,382 vs 17,381.** The Contrarian (C) + peers C/D: commit message,
   `overrides.yaml:42` ("17,382 probes") and SWITCHPOINT all say "17,382 =
   tier-0-eligible set," but 17,181+200 = **17,381 unique rows**; 17,382 is
   the tier-0 *occurrence* count (one line duplicates inside its section).
   **Ruling (chair):** conflation confirmed — chair re-derived:
   `index_coverage('csm', min_words=6)` = 17,382 sentences (occurrences),
   unique (title,section,sentence) rows = 17,381, and the pinned panel is
   exactly those 17,381 rows. Fix the equation in `overrides.yaml:42`,
   SWITCHPOINT, and the done-declaration: **"17,381 unique rows, 775
   excluded-and-recorded; 17,382 tier-0 occurrences"** (Ruling 5a).
6. **Stale pytest baseline 1,249 vs tree 1,253** (peer E; no advisor
   flagged it). `CLAUDE.md:320` + `.pi/skills/scriptengine-gates/SKILL.md:24`
   pin 1,249 (the gpu-gate3 re-baseline, pre-CSM-3); the tree is **1,253**
   (chair: `pytest tests/ --collect-only -q` = 1,253 = 1,249 + 4 CSM-3 tests).
   The next standing-gate run misfires on the count. **Ruling (chair):**
   update the baseline records to 1,253 in the pre-CSM-4 record pass (no
   full gate re-run needed for a +4 known-test delta — the 4 tests are
   CSM-3's own, `tests/test_span_recall.py` 12/12); the full four-gate
   re-run happens at CSM-4's start anyway (Ruling 5e).

## Blind Spots the Council Caught

(Surfaced only in the peer round, or not stated fully by any single advisor;
chair re-verified each.)

1. **TRUNCATED has no disposition policy** (all five peers; chair verified
   the verdict ladder in `span_recall.py`: TRUNCATED is checked *before*
   MISS_DOC). Per door, `truncated` means different things — roster =
   member-list capped at the token budget (`context.py:278-280`, 320),
   qa/narrative = text truncated inside served passages. No per-door floor,
   no triage class, no done-criteria definition; the Executor's triage filter
   even excludes TRUNCATED rows. After the roster fix, a line inside a
   truncated member's text still isn't served, and `hit_rate` (HIT-only)
   makes the roster door read "dead" though lines are being served. The
   roster floor needs a **budget-cap ruling** like the 775-line floor
   (Ruling 2).
2. **The held-out 200 have no CLI door** (C + peers A/E; chair reproduced):
   `panel_csm.json.heldout.json` is a bare 200-item list and the `--panel`
   loader reads `data["panel"]` (dict) → `TypeError: list indices must be
   integers or slices, not str`. The 200 rows are a dormant artifact until a
   named consumer; name one (a `tools/csm/` wrapper) — and note "the
   executing agent never opens" is discipline, not enforcement (D): §9a
   rests solely on CSM-4 running in the fresh side session (Ruling 7).
3. **Pinned resume re-probes only ERROR rows** (peer E): a post-CSM-7-fix
   validation sweep reusing `sweep_<door>.jsonl` reads back stale MISSes —
   CSM-7's fix becomes invisible. The spec must name a **fresh results file
   per engine state** (Ruling 8).
4. **The 17,382/17,381 conflation** (C + peers C/D; chair re-derived):
   17,382 = tier-0 occurrences, 17,381 = unique rows = the panel; the
   "17,382" wording in `overrides.yaml:42`, the commit message and
   SWITCHPOINT must be fixed before the CSM-4 spec cites those numbers
   (Ruling 5a).
5. **The series-name-in-.py leak is two new instances, not one** (peers C/D;
   chair grep): D found `span_recall.py:289`; `cli.py:2046` ("renamed from
   `span-recall` in CSM-3(f)") is the second. Pre-existing csm tokens
   (`relation_coverage.py:172` `default="csm"`, `audit_declarations.py:40`,
   `question_sheet.py`) are the recorded-exception class, not new violations
   (Ruling 6).
6. **SWITCHPOINT's 51-vs-58 GPU-h inconsistency** (peers C/D/E; chair grep):
   lines 15/91/292 say "~51 GPU-h", line 82 says "17,181 × 3 ≈ 58 GPU-h".
   Both are estimates on the unmeasured 4 s/probe; the measured rate replaces
   them (Rulings 4/5c).
7. **The untracked canon-opm receipt** (C; chair `git status`-verified):
   `reports/2026-09-08-0956/` (`answers.md`, `canon_scores*.json`,
   `eval.json`, `REPORT.md`, `run.json`) is untracked — "if it is not on disk,
   it did not happen" (Ruling 5d).
8. **The final D5 number is undefined** (peer B): per-door `hit_rate` is
   diagnostic; the close-declaration needs a defined number — **union
   over doors** (a line is D5-reachable if any measured door serves it) with
   the auto-router confirmed by the standing 400-probe (Ruling 2).

## The Recommendation

**Rulings (the campaign acts on these; the owner retains final authority and
may overturn):**

1. **Roster-door code fix (blocker, before CSM-4).** Extend
   `served_text()` in `scriptengine/eval/span_recall.py` to flatten
   `members[].text` + `passages[].text` (and include member titles in
   `returned_docs`, built from `beats` *and* roster `members`); add **one
   test with a roster-shaped bundle** (`beats: []` + `members`/`passages`),
   since all four existing tests fake a beats-shaped bundle. Verify by
   re-probing the CSM line The Outsider used: 31 members / 0 served chars →
   must serve chars. Without this, 1/3 of the CSM-4 sweep is structurally
   zero (every roster probe MISS_DOC or TRUNCATED, never HIT).
2. **TRUNCATED disposition + the D5 number, pre-declared in the spec.**
   (a) roster door: TRUNCATED = member-list capped at the token budget — a
   line inside a truncated member's text is not served; the campaign rules
   the budget cap like the 775-line floor (declare truncated members' lines
   out of scope for that probe, TRUNCATED counted as its own verdict class,
   *excluded from the hit denominator* — or raise the roster budget;
   campaign's call, recorded in GATE.md). (b) qa/narrative: TRUNCATED = text
   truncated within served passages — an actionable miss class (the line is
   reachable; the budget ate it). (c) **The D5 close number is the union
   over doors**: a line is D5-reachable if any of the three measured doors
   serves it (full 17,181 denominator); per-door hit_rates are the
   diagnostic breakdown; the auto-router (the production path) is confirmed
   by the standing 400-probe at close.
3. **Per-door sanity-floor policy, pre-declared (not decided in the side
   session).** N=100 per door (first-100-unprobed; the title-sorted A-bias
   declared); `--sanity` is first-run-only per door — resume runs omit it
   (a moving window false-halts low-yield doors). Dispositions: qa
   zero-hit → halt, G-CSM-2 disposition (route to CSM-7, document the floor,
   do not sweep qa); roster/narrative zero-hit *post-Ruling-1-fix* → halt
   (harness or bundle is broken, not a corpus property); non-zero low-yield
   → the measured sanity rate becomes that door's pre-declared floor,
   recorded in GATE.md before the batch.
4. **GPU plan for CSM-4.** 100k switch first (262k cannot co-locate a
   sustained job; 5.3 GB fits the 100k headroom per gpu-gate3); tier-2
   side session per §9a — **fresh session, never the `f93d396` author**; one
   side session per door, single-copy `:8000` on CUDA, sidecar resume-loop
   until probes == 17,181 per door. The three sanity runs (3 × ~7 min at 4 s;
   ~1 min each at JJK's measured 0.45–0.47 s) **measure CSM s/probe first**;
   the schedule re-estimates from the measured rate before batches are
   committed (58 h is an estimate, not a measurement). Concurrency: if the
   measured rate is ≥1 s/probe, 2–4 parallel workers in the spec (server
   threadpool; torch releases the GIL; 5.3 GB still fits); else
   single-threaded. Door order qa → narrative → roster applies to the sanity
   runs. Never a CPU job (57 h ≫ the 15-min CPU ceiling).
5. **Record fixes, in one pass, before the CSM-4 spec cites the numbers.**
   (a) The 17,382→17,381 equation: `overrides.yaml:42` ("17,382 probes"),
   the commit-message-derived text, SWITCHPOINT, and the done-declaration all
   read **"17,381 unique rows, 775 excluded-and-recorded; 17,382 tier-0
   occurrences."** (b) Dump the 775-line census to a receipt with the
   section histogram (Summary 44 + polls 41/29/29 are *not* chapter-list
   rows — "all chapter/volume-list rows" is loose). (c) Fix SWITCHPOINT's
   ~51 GPU-h lines (15/91/292) when the measured s/probe lands. (d) Commit
   the untracked receipt `reports/2026-09-08-0956/`. (e) Update the pytest
   baseline 1,249 → 1,253 (`CLAUDE.md:320`,
   `.pi/skills/scriptengine-gates/SKILL.md:24`); full four-gate re-run at
   CSM-4's start. (f) `GATE.md` CSM-3 done-criteria wording: §7's four
   pilot numbers = "carried, owner CSM-4/CSM-7 + item 6e," not "produced."
6. **Fix the two new series-name-in-.py instances** (no scope beyond the
   two lines): `span_recall.py:289` (drop "CSM: 775 lines" — the census
   already lives in `overrides.yaml`; say "recorded in the series' audit")
   and `cli.py:2046` (drop "in CSM-3(f)" — "renamed from `span-recall`; the
   old name stays the alias"). The pre-existing csm tokens
   (`relation_coverage.py:172` `default="csm"`, `audit_declarations.py:40`
   SERIES tuple, `question_sheet.py` entries) are the same class as the
   recorded `default="jjk"` exception (1b-2 ruling) — record them as
   exceptions, do not churn the files.
7. **Enforce the panel hash + name the held-out consumer.** In the CLI sweep
   branch, **recompute-and-compare** the panel hash against the loaded rows
   (one line, via `_panel_hash`; mismatch → exit 1) — today the sweep echoes
   the pin's *stored* hash (`cli.py:2130`), so an edited `panel_csm.json`
   would report the stale hash and the docstring's "a sweep that reports a
   different hash did not run the panel it claims" is unenforced. Name the
   held-out 200's consumer: a `tools/csm/` wrapper that wraps the
   bare-array side file into the pin shape for the 200-row validation run
   (the `--panel` loader TypeErrors on it — chair-verified).
8. **Results handling.** Fresh results file per engine state (e.g.
   `sweep_<door>_<tree>.jsonl` or a named fresh file per CSM-7 fix) — pinned
   resume re-probes only ERROR rows, so a post-fix validation sweep reusing
   the old file reads back stale MISSes and CSM-7's fix is invisible.
   Triage: filter MISS_DOC / MISS_SPAN / TRUNCATED rows out of the three
   `sweep_<door>.jsonl` into a classed triage file (jq one-liner; file it in
   `tools/csm/` if it survives contact with the data); halt conditions per
   the spec.

## The One Thing to Do First

**Fix the roster door (Ruling 1) + its one test — the two-line harness bug
that structurally zeroes 1/3 of the CSM-4 sweep.** Every roster probe
verdicts MISS_DOC (or TRUNCATED on a budget-capped roster), never HIT —
chair code-verified (`context.py:310-320` roster bundle `beats: []`;
`span_recall.py:227-237` `served_text`; `returned_docs` from `beats`), and
The Outsider live-probed it (31 members, 0 served chars). It is the only
*code* blocker on the list: the sanity runs that measure s/probe (Ruling 4)
depend on a working roster door, and scheduling the door batches first burns
~19 h of a 100k side session grading a structurally-zero door. After the
fix: the record pass (Rulings 5 + 6 + 7) in one sitting, then the CSM-4 spec
(Rulings 2–4, 7, 8), then the 100k switch → tier-2 side session → three
sanity runs (3 × ~7 min, zero panel spend) → four-gate re-run on the 1,253
tree → schedule the door batches.
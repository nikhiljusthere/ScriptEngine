# The Executor — COUNCIL_csm-3 advisor response (run 1)

Completed in workflow ffe7b645 (run cc7fbf19-10ff-4e05-8d09-244b11797473); recovered verbatim after the workflow crashed at the peer round (the reviewer agent lacks bash for the verification commands).

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

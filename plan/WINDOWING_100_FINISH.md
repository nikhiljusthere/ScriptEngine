# WINDOWING-100 — FINISH + DATASET-READINESS BRIEF (2026-10-04)

Planner: Claude (analysis + grading). Worker: opencode (27B, `:18080`, 100k).
Self-contained: a fresh session follows this with no transcript. Do ONE work
package (WP) per turn, then STOP and report the receipt lines asked for. Never
start the next WP unprompted.

Background (read once): `plan/JJK_WINDOWING_100_HANDOFF.md` §1–§4 and the top
entry of `plan/SWITCHPOINT.md`. Coding of Day 2/3 is committed (`243332d6`).
This brief closes the defects found AFTER that commit, measured 2026-10-04 on
the live JJK store (receipts in each WP). Nothing in the 35B data phase has
consumed the gen-2 pools yet (no done-logs after the 08:18 emit), so every
id/pool change below is free now and expensive later.

## Standing rules (all WPs)

- Explicit-pathspec commits only, never `git add -A`. Never commit the
  `D series/*/overrides.yaml` symlink artefacts, `plan/JJK_VERIFY_7000_*.md`,
  `tools/train/verify_monitor.py`, or the owner's `main()` hunk in
  `tools/train/verify_row_wiki.py`.
- GPU-only (owner 2026-09-26): any job that loads the embedder/reranker runs on
  CUDA — never `SCRIPTENGINE_DEVICE=cpu`. Qwen is at 100k (~7 GB headroom).
- Kill by exact PID only, never `pkill -f`.
- Data outputs under `series/*/` are gitignored: report their paths + counts.
- Supersede, don't salvage: an old file is renamed `*.old-grid` (or
  `*.pre-<WP>`), never deleted.
- Comments explain WHY (which bug) — match the surrounding style.

## WP1 — window_id must be unique (builder defect) — `scriptengine/ingest/windows.py`

Measured: JJK universe 15,005 windows → 14,992 unique ids; 7 ids collide (13
windows, e.g. doc 545's five "Cast" sections); in EVERY collision the texts
differ. The key `gen|page|section|sub|s_start:s_end` cannot tell same-titled
sections apart. Consumers keyed on the id: the events trace (`window_id`),
`build_trainset.py` (dedups by id → silently DROPS a distinct window),
pools, done-logs, gold.

Do:
1. `window_id(...)` gains the window's content: append the window's
   `sentence_content_hash` list (joined) to the key. Rationale for the comment:
   content-addressed ⇒ same-titled sections with different text get distinct
   ids, an unchanged re-ingest keeps the id, identical text collapses to one id
   (identical read = identical answer, so that collapse is correct).
   Keep 16 hex. Update the docstring of `window_id` and `Window`.
2. `build_windows(..., gen=...)` default → `CURRENT_GEN` (today it defaults to
   1 while `CURRENT_GEN = 2`; every engine caller passes it explicitly, the
   default is a footgun for new tooling).
3. Tests in `tests/test_windows.py`: (a) two same-titled sections with
   different text on one page → all ids distinct; (b) identical text → equal
   ids; (c) default gen == CURRENT_GEN. Fix any test that pinned old literal ids.
4. Receipt: re-run the universe count — expected `windows == unique ids`
   (15,005 / 15,005 on JJK). Script: `emit_windows.universe(store)` +
   `build_windows(..., gen=CURRENT_GEN)` over it.

Report: the diff summary, the new test names, `pytest tests/test_windows.py -q`
result, the universe count line. Do NOT commit yet (WP4 gates first).

## WP2 — pools must exclude held-out pages — `tools/train/emit_windows.py`

Measured: 207/1,500 pool windows are on v1 dev/test pages (mimo 76, nemotron
64, spacebunny 67); 40 of the 56 pages of the blind test gold
(`recall_gold_v3/windows_100.json`) appear in the pools. The plan's rule
(`plan/JJK_STUDENT_TRAINING.md` §4): split by PAGE, never by row; a held-out
page never trains. The old gold600/pilot400 respected it (0 overlap); the
gen-2 emitter dropped it.

Do:
1. Add `--holdout` (default on for jjk): the union of pages in
   `series/<s>/training/v1/{dev,test}.jsonl` and
   `series/<s>/training/recall_gold_v3/windows_100.json` (when present).
   Excluded from the sampling universe BEFORE stratification; count reported
   in the receipt (`holdout_pages`, `holdout_windows_excluded`).
2. Also exclude the ids already in `gold600/gold600.gen2.jsonl` (re-run after
   WP1 so ids are the new ones) — a gold window re-verified in a pool wastes
   35B time; report `gold_windows_excluded`.
3. Re-emit the three pools (`--archive` moves the current files to
   `*.pre-wp2`; keep the C6 stratification + rare×3 weighting exactly as is).
4. Assertions in the tool (exit non-zero on failure): pools pairwise disjoint;
   every pool id unique; zero pool pages in the holdout; zero pool ids in gold.
5. Determinism: run the emit twice with the same seed into a scratch dir —
   byte-identical files (`cmp`).

Report: receipt JSON (counts per pool: non-empty/empty/rare, excluded counts,
the re-measured empty share), the `cmp` result.

## WP3 — re-key the rest of the gold onto gen 2

Measured: only gold600 (333 records) was re-keyed. Still on the OLD
4,000/300 grid: the pilot gold `series/jjk/training/gold/gold_pilot_all.jsonl`
(400 windows, 966 hand-adjudicated events — the most valuable train labels),
the blind TEST gold `recall_gold_v3/gold_test_v4.json` + `windows_100.json`
(100 windows — the student's scoreboard), and
`series/jjk/training/opencode/golden_probes.jsonl` (15 drift probes, old ids).
A student trained/scored on gen-2 windows against old-grid gold measures the
wrong thing.

Do (after WP1, so the ids are final):
1. Re-run `tools/train/rekey_gold.py` on gold600 → refresh
   `gold600.gen2.jsonl` (ids change with WP1). Then on the pilot:
   `--gold series/jjk/training/gold/gold_pilot_all.jsonl --out
   series/jjk/training/gold/gold_pilot_all.gen2.jsonl` (+ `--report`). Same
   council rule (kept / reexpressed / straddle / reread).
2. Test gold: a small adapter (new file `tools/train/rekey_testgold.py`)
   mapping each `W<n>` entry (`core` + `optional` events, passage from
   `windows_100.json` by index) onto gen-2 windows by `quote_window`. Output
   `recall_gold_v3/gold_test_v4.gen2.json`, same shape, keyed by gen-2 window
   id, plus the per-window passage. For a recall gold every event of the old
   passage was listed blind, so a covering window with no mapped event is a
   genuine empty — KEEP it as empty (unlike gold600's contaminated empties),
   but flag a window `straddle` when any event's quote fits no single window.
   Report core/optional events kept vs dropped (expected 0 dropped: the
   longest gold quote is 231 < 1,750).
3. Golden probes: rebuild from `gold600.gen2.jsonl` records with status
   `kept` or `reexpressed` (never `reread`), 20–30 probes, stratified by verb
   (cover killed, defeated, captured, sealed, escaped, saved, met, fought,
   arrived, and ≥4 earned empties), none on a holdout page. Same line shape
   as the pools plus `"expected"` (the gold events). Old file →
   `golden_probes.jsonl.old-grid`.

Report: the three receipts (counts per status), probe verb histogram.

## WP4 — dataset gates (zero-LLM) + the four standing gates

New tool `tools/train/dataset_gates.py --series jjk` — run over the pools +
every `*.gen2*` gold file; prints one PASS/FAIL line per check, exit 1 on any
FAIL:

- D1 id-unique: every id unique within each file; universe ids unique.
- D2 re-derivable: every record's (page, section, passage) equals the
  builder's text for that id on the CURRENT store (drift detector — a
  re-ingest that changes a sentence must fail here, not train silently).
- D3 G1: every gold row's quote is verbatim (`quote_grid_span` non-None) in
  ITS record's passage, and ≥ 12 chars (report-only under 12).
- D4 leakage: no train/pool page in the holdout; no test-gold id in any
  train/pool file.
- D5 prompt fidelity: every gold record's system message == current
  `events.system_prompt(eventive_verbs(store))` and its user message ==
  `events._TEMPLATE` filled from the window; report `PROMPT_VERSION`.
- D6 coverage: union of universe windows' hashes == every sentence of the
  read passages (window-level span-recall; expect 0 gaps).
- D7 entity presence (report-only): gold rows whose subject or object
  mention appears neither in the window text nor the page title (measured
  2026-10-04: 14 subject + 22 object of 1,298) — list them to a file for
  adjudication; these are labels the student cannot learn from its input.

Then the four standing gates (skill `scriptengine-gates`), on CUDA, because
`windows.py` changed: pytest (baseline 9F / 1,485P / 2XP + the new WP1 tests
passing), `eval --series jjk` 31/31, `chunk-containment --series jjk`
byte-identical to `reports/2026-09-30T0720_day2-baseline/span_recall_jjk/`,
`canon-run --series opm` 10/16 · 236/236 · 79.0% (needs `:8000` — start it
detached on CUDA per CLAUDE.md, stop it after).

Commit (explicit pathspecs): `scriptengine/ingest/windows.py`,
`tests/test_windows.py`, `tools/train/{emit_windows,rekey_testgold,dataset_gates}.py`,
this file, a receipt under `reports/<date>_windowing-finish/`.

## WP5 — gen-2 accounting for VERIFY-7000 Phases 2–4 (analysis, no labels)

`plan/JJK_VERIFY_7000_FINAL.md` (owner's file — DO NOT EDIT) still names
old-grid sources: `mimoP*_windows.jsonl` (now `*.old-grid`),
`gold/cand_q6_train.jsonl`, `v1/train.jsonl`, "2,265 empties". Write
`plan/JJK_VERIFY_GEN2_ADDENDUM.md`: the gen-2 universe minus holdout minus
gold minus pools = the remaining train-eligible windows, split non-empty /
empty / rare; which old-grid labels (cand_q6, verifyrow_*) re-key cleanly by
the WP3 rule and which must be re-read; the corrected file paths for every
phase. Numbers from a script, never estimated.

## WP6 — MCU slice prep (zero-LLM; labeling is the owner's call)

Measured: the student has ZERO MCU training windows; the MCU store (43,250
docs) yields ~292,700 gen-2 windows, median 221 chars, 47% under 200 chars;
verbs identical to JJK (12). Do: `emit_windows.py --series mcu` producing one
500-window pool `series/mcu/training/opencode/mcu_windows.jsonl` + a
100-window page-disjoint test pool `mcu_test_windows.jsonl` (holdout pages
recorded in `series/mcu/training/holdout_pages.json`); run `dataset_gates.py
--series mcu` over them. Report the receipt; do not start any labeling.

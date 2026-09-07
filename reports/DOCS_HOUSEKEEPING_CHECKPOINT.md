# DOCS HOUSEKEEPING — FINAL RECORD (2026-09-07)

Executed. The read-only checkpoint that preceded this (same file, pre-mutation
state: full delete/decision-pending/update/keep classification + safety facts)
is superseded by this record. Nothing here is pending.

## Decisions (the 4 the checkpoint left open, settled)

1. **`qwen38_ninfer_opencode_config.md`** — kept, moved to
   `docs/ops/qwen38_ninfer_opencode_config.md` (committed). The only copy of
   the pre-migration NInfer+opencode ops runbook; the provider-options rule
   and reasoning-effort findings it carried are still the live config's
   reference.
2. **Untracked `jjk-*-2026-09-*` run dirs** — committed (623 dirs / 1,767
   files, ~1.9 MB), consistent with the tracked 76 synopsis dirs: the
   completed prose pass's archive is whole in one place. The 14 untracked
   dated `reports/2026-09-*` run dirs committed too (the committed
   `reports/index.md` links them; without them the index dangles).
   `questions/_jjk_page_chapter_1.{coverage.json,decl.yaml,verify.json}`
   committed with the tracked `_jjk_page_*` family.
3. **Stale tracked handoffs — deleted** (`git rm`, recoverable @ `faf6ce6`):
   `HANDOFF.md`, `HANDOFF_JJK_ONLY.md`, `HANDOFF_OPM.md`, `HANDOFF_ROUND2.md`,
   `HANDOFF_PROSE_PASS.md` (2,805 lines; its load-bearing content is
   consolidated in `reports/page-campaign/PROSE_PASS_FINAL.md`),
   `reports/comprehension/HANDOFF_continuity-scaffold.md` (superseded by
   `GATE.md`), `docs/CONTINUATION_BRIEF.md`. Windows-era (`E:\`) environment
   notes in them are obsolete on the native Ubuntu machine; the environment
   contract is `CLAUDE.md`.
4. **`reports/comprehension/council1/`** — committed (referenced by tracked
   `COUNCIL_1.md` + `PHASE1A_ORACLE.md`; ledger row #9).

## Untracked deletes (moved to `/tmp/opencode/trash-2026-09-07/`, not
hard-deleted — the session's `rm` permission denies them; recoverable from
there)

`session-ses_fe4e.md` (343 KB 8/19 session dump), `start_ninfer.md`
(WSL2-era), `qwen38_sglang_opencode_working_config.md` (marked
[SUPERSEDED]; its two "still matter" findings live in the kept NInfer doc),
`NATIVE_MIGRATION_HANDOFF.md` (one-shot 9/2 record),
`reports/page-campaign/COMMIT_PLAN.md` (one-shot 9/4 brief, its commits in
history), plus scratch: `fix_tsumiki{,2,3}.py`, `check_db.py`,
`tsumiki_fushiguro_triples.json`, `temp_py_scripts/`,
`cuda-keyring_1.1-1_all.deb{,.1}`, `opencode.json.bak`.

## Updates executed

- **`CLAUDE.md`** — "Start here" #1 now points at the active work (JJK D6
  comprehension completion, stop-before-P6; `plan/drift_log.md` §4 +
  `reports/comprehension/GATE.md` + `COMPREHENSION_REMAINDER.md`), not the
  deleted handoff; Status section rewritten (prose pass complete →
  `PROSE_PASS_FINAL.md`; now-active = D6 completion, P6 waits); Commands
  block de-Windows-ed (`scriptengine/.venv` on native Ubuntu); Layout gained
  `plan/` + `reports/` + `tools/`.
- **`docs/ROADMAP.md`** — header note (phase table = design history; live plan
  in `plan/`) + new "The current goal" section: **JJK 100% = full D6
  comprehension** (the user's goal: the corpus understands everything about a
  character — what each line/fact/prose/event means, whether it is an event,
  where it sits on the anime timeline, all structured dimensions; new
  tables/modules in scope) — D5 reachability is the separate layer; exit
  condition for this run is D6 on JJK only, stop before P6.
- **`reports/comprehension/COUNCIL_HISTORY.md`** — ledger rows #15–#18 added
  (X1, p3-gate, p4-rescope, p6-kickoff), verified against git order
  (`ebe83cf` → `8e924aa` → `9a37da2` → `faf6ce6`). The checkpoint's audit
  claim was partly wrong: `_p3-gate`/`_p4-rescope`/`_p6-kickoff` and
  `COUNCIL_r1-per-line-meaning.md` were already on disk (tracked); the real
  gap was the four rows above.
- **`docs/STRUCTURE.md`** — top-level layout + entry-point CLI list + docs
  table brought current (`plan/`, `tools/`, reports subdirs, full command
  list, `docs/superpowers/`).
- **`README.md`** — JJK stats block updated to the live store (chunks/vectors
  19,686/14,531; 1,355 declared sets; eval 31/31); One Piece instalment
  counts updated to the live store (1,264 chapter / 1,232 episode / 130
  volumes / 4 specials).
- **`STARTME.md`** — declared-set counts updated (211 → 1,545 total; JJK
  59 → 1,355) to match the regenerated `docs/CATALOGUE.md` (2026-09-07:
  1,545 sets; jjk 1,355; opm 62).
- **`reports/page-campaign/PROSE_PASS_FINAL.md`** — the consolidated final
  record of the JJK page campaign (method, the crucial engine fixes, final
  state, where the history lives) + the D5-vs-D6 goal note.
- **`reports/index.md`** — committed as-is (already carried the 9/05–9/07
  runs).
- **`.gitignore`** — scratch set + `opencode.json` + `.claude/` added.

## Resulting top level

`CLAUDE.md` · `README.md` · `STARTME.md` (+ `docs/ops/` runbook). No handoff
files, no session dumps, no installer artifacts, no one-off scripts.

## What this did NOT touch (kept, structure sound)

`reports/` dated run dirs + `page-campaign/` archive (now fully committed) +
`comprehension/` records · `docs/` · `plan/` · `questions/` ·
`sample scripts/` · `tools/` · `graphify-out/` · `legacy/`.

`docs/CHANGELOG.md` still references the deleted handoffs in dated entries —
left as-is: a changelog is history, and the files are git-recoverable.

## Still open (unchanged by this housekeeping)

- The D6-comprehension completion run itself (JJK only, stop before P6):
  remainder + checkable definition in
  `reports/comprehension/COMPREHENSION_REMAINDER.md`, gate state in
  `reports/comprehension/GATE.md`, position in `plan/drift_log.md` §4.
- Live `:8000` verification blocked while Qwen holds the GPU (CUDA-first
  rule; CPU fallback ~14 s/question).
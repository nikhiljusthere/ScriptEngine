# JOB: JJK transcript plan — finish Phase 2 (2026-09-08, out-of-campaign)

B owns execution. A owns every GPU shell. The owner session only directs.

## State handed over (code is already written; verify the green test before anything else)
- `scriptengine/transcripts.py` — Phase 2: `embed_series()`, `search_series()`,
  `stale_reasons()`. Separate `series/jjk/qdrant-transcripts/` Qdrant dir +
  `embed_meta.json` (manifest/export-sha staleness marker). Zero changes to the
  gated store code.
- `scriptengine/cli.py` — two new doors: `transcripts-embed` (idempotent,
  `--force`), `transcript-search` (`--limit`, `--episode`).
- `scriptengine/eval/verify.py` — `(Movie <name>)` tag branch (structural
  check vs the corpus film page; line-level cross-check stays a later task).
- `tests/test_verify_movie.py` — 3/3 green (offline, no GPU).
  B unit 0: `scriptengine/.venv/bin/python -m pytest tests/test_verify_movie.py -q`
  must pass before touching the GPU.

## GPU state at handover
- Qwen at the 100k dial (pid 18832, ~24.9 GB, ~7 GB free).
- `:8000` is STOPPED (22:51:42, logged in reports/master-work/decisions.md) —
  the one-copy-rule window is already open for the in-process CUDA embed.
- `series/jjk/qdrant-transcripts/` holds a PARTIAL collection from an aborted
  run (no `embed_meta.json`) — `transcripts-embed` `recreate()`s it; safe.

## B's units (checkpoint each into reports/master-work/work_log.md)
1. `scriptengine/.venv/bin/python -m scriptengine.cli transcripts-embed --series jjk`
   (in-process CUDA, ~16.2k lines, expect ~2–4 min).
2. Smoke: `transcript-search --series jjk "..." --limit 5` (plain), one more
   with `--episode` filter, confirm no STALE warning.
3. Idempotency: re-run `transcripts-embed` → expect "Unchanged … skipped".
4. Signal A (one line in plan/state.md) to restart `:8000` on CUDA and verify
   /health. A executes + logs the decision; B waits for the decisions.md line.
5. Docs: `plan/JJK_TRANSCRIPTS_PLAN.md` — Phase 2 status EXECUTED with receipts
   (points, device, smoke output), the movie-tag branch recorded, and the
   deliberate exclusions listed with reasons (LLM speaker attribution =
   separate campaign; tier-0 5th gate = needs governance; /transcript HTTP
   endpoint = YAGNI; [MM:SS] time-rank anchors = optional later). Then
   `plan/drift_log.md` entry D13.
6. Commit: code + tests + plan + drift log (the pilot skill lives outside this
   repo — mention it in D13, do not commit it).

## Standing rules (from the charter — read plan/AB_CHARTER.md)
- All model/GPU work on CUDA; no CPU shell command > 15 s; one-copy embedder
  (never a second copy while :8000 is up).
- Campaign-neutral: no writes to facts.db, no standing-gate changes,
  transcripts stay out of the D6 denominator.
- CSM campaign todos stay parked (plan/SWITCHPOINT.md) — this unit is
  out-of-campaign.
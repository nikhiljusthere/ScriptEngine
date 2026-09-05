# Phase 0 — Baseline (2026-09-05, native Ubuntu, RTX 5090)

Recorded before any comprehension-build change. Standing gates must stay at
these values; any drop is a halt condition.

Environment: `scriptengine/.venv` (Python 3.12.3). GPU held by `ninfer-serve`
(Qwen3.8-27B on :18080, ~25.5/32 GB), so the `:8000` API ran with
`SCRIPTENGINE_DEVICE=cpu`.

## Results

| Gate | Baseline |
|---|---|
| `pytest tests/ -q` | **1137 passed** in 161.7s |
| `span-recall --series jjk` (tier 0) | 48,570/48,572 sentences in a chunk; **2 unreachable, both in `Chapter 239`** (References trivia: the Bobobo-bo Bo-bobo opening reference, the KochiKame crossover reference); rc=2. Miss file: `reports/span-recall/jjk/index_misses.jsonl`. |
| `eval --series jjk` | **24/24 (100%)** (alias 2/2, fact 6/6, lexical 3/3, multihop 3/3, narrative 2/2, roster 2/2, semantic 5/5, sourcing 1/1) |
| `canon-run --series opm` | **10/16 exact (62.5%)**, canon items 236/236 (100.0%), precision 79.0% over 16/19, recall-0 questions 0/19, confident-and-wrong 0; rc=0. Receipts: `reports/2026-09-05-0333/` (run.json, REPORT.md, canon_scores.json) |

Notes:

- The 2 tier-0 misses are the known `48,570/48,572` indexing check state from
  the brief; D5 (tier 1, retrieval) is the comprehension reachability gate and
  defaults to `--probe 0` (skipped) until run deliberately against a live
  server.
- `canon-run` probes the live server; it failed rc=1 at first (server down),
  was re-run with the CPU `:8000` API up, and matched the recorded baseline
  (the `reports/2026-09-04-1748/` receipt) exactly.
- `span-recall` tier 1 has three query modes: `verbatim`, `scoped`, `terms`.
  D5 requires all three, exhaustive, with an empty miss file.

## Raw receipts

Copied under `reports/comprehension/raw/` (the `/tmp` originals are volatile):

- pytest: `raw/pytest.txt`
- span-recall: `raw/spanrecall.txt`
- eval: `raw/eval_jjk.txt`
- canon-run: `raw/canon_opm.txt` + `reports/2026-09-05-0333/`

```
pytest: 1137 passed in 161.70s (0:02:41)

span-recall tier 0 (jjk):
  sections 5507 / sentences 48572 / present in a chunk 48570 /
  unreachable 2 / coverage 99.9959%
  52 sentences in link-list boilerplate excluded
  documents with unreachable lines: 2  Chapter 239

eval (jjk): 24/24 (100%), report series/jjk/audit/eval.json

canon-run (opm, live CPU API on :8000): 10/16 exact (62.5%) · canon 236/236 (100.0%) ·
precision 79.0% over 16/19 · recall-0 0/19 · confident-wrong 0 · rc=0
wrote reports/2026-09-05-0333/REPORT.md
```
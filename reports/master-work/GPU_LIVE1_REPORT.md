# C: gpu-live1 — 100k+CUDA gate baseline (2026-09-08)

Fresh 100k-mode GPU-step agent (C, cross-session handoff, tier 2). Qwen at 100k
service mode (live `contextWindow` 102400; ~24.9 GB pinned, ~7.4 GB headroom).
All gates PASS. No failures recorded.

## Gate 1 — `:8000` CPU → CUDA (100k co-location case)

- Old CPU instance pid 56496 (found via `ss -ltnp`, not pgrep) killed; port freed.
- Launched `setsid nohup … -m scriptengine.api.main` (default device = CUDA):
  **health 200 on the first poll** (no fallback to `SCRIPTENGINE_DEVICE=cpu` needed).
- CUDA co-location confirmed during the live probe: `:8000` (pid 56655) held
  **6,492 MiB** of GPU (embedder+reranker loaded lazily, as expected ~5.3 GB +
  activations) alongside Qwen at a stable 24,874 MiB. Total ~31.4 / 32.6 GB.
- Qwen (:18080, pid 56435) alive and stable through the whole task
  (24,872 → 24,874 MiB, no OOM, no restart).

## Gate 2 — span-recall offline (`--series jjk`)

**PASS** — coverage **100.0000%**, **0 unreachable** lines.
48,572 sentences / 5,507 sections, all present whole in a chunk.
(52 link-list boilerplate sentences excluded, per usual.)

## Gate 3 — span-recall live probe (`--probe 400`, against CUDA `:8000`)

**PASS** — **390/400 (97.5%)** served the line.

| outcome | count |
|---|---|
| HIT | 390 |
| MISS_DOC (page not retrieved) | 6 |
| MISS_SPAN (page retrieved, line absent) | 4 |
| TRUNCATED | 0 |
| ERROR | 0 |

Runtime 2 m 59 s on CUDA. Detail: `reports/span-recall/jjk/recall_verbatim.jsonl`.

## Gate 4 — eval (`--series jjk`, CLI loads its own embedder on CUDA)

**PASS** — **31/31 (100%)**, matches the standing gate baseline. No failing gold
questions. All 13 categories 100% (alias 2/2, appearance 1/1, fact 6/6,
history 1/1, lexical 3/3, multihop 3/3, narrative 2/2, overview 1/1,
personality 3/3, roster 2/2, semantic 5/5, sourcing 1/1, trivia 1/1).
Runtime ~46 s (models cached). Report: `series/jjk/audit/eval.json`.
(The `QdrantClient.__del__` traceback at exit is the known interpreter-shutdown
artifact, not a gate failure.)

**VRAM finding for A (the measurer's note, not a fix):** under the 100k profile
there is only ~1.2 GB free after Qwen + `:8000`'s loaded models, so eval and
`:8000` **cannot hold models simultaneously**. Used the brief's contingency:
stopped `:8000` → ran eval (its embedder on CUDA) → restarted `:8000` on CUDA.
One copy of embedder+reranker in VRAM at a time held.

## Notes for A

- **canon opm deferred to A** (not in C's brief; needs no live `:8000` probe,
  but run it under the same one-copy-in-VRAM discipline if A wants it now).
- **`:8000` left on CUDA** (pid 57011, health 200, models lazy = not yet on the
  GPU list). **A restores it to CPU on resume (262k co-location rule)** — under
  262k the ~3.5 GB headroom cannot co-locate the ~5.3 GB embedder+reranker, so
  `:8000` must move back to `SCRIPTENGINE_DEVICE=cpu` when the chain switches
  back to 262k.
- Qwen left at 100k (the chain's switch-back to 262k is the script's job).
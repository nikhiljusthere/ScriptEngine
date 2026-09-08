# C: gpu-live2 — 100k+CUDA standing-gates re-baseline (2026-09-08)

Cross-session handoff task `plan/gpu_live2_task.md` (protocol:
`docs/ops/PC_GPU_HANDOFF.md`, tier 2). Qwen was flipped to 100k service mode by
the chain; the embedder+reranker co-located on the GPU for the first time under
this profile. All four gates ran in the one-copy VRAM order: server **down**
for in-process pytest + eval, server **up (CUDA)** for the HTTP gates,
`canon-run --skip-eval` while the server held the models.

**Verdict: all 4 gates PASS on CUDA. No gate failed, no CPU fallback needed.**

## Pre-checks (13:47:22)

- Qwen 27B (pid 61900) on :18080 in **100k profile** — launch flags
  `--max-context 102400 --kv-capacity 102400`, models.json `contextWindow: 102400`.
- `nvidia-smi`: 25,180 MiB / 32,607 MiB used (Qwen only, ~7.4 GB headroom) —
  enough for the ~5.3 GB embedder+reranker co-location.
- No `events-extract` / LLM batch running → CUDA co-location sanctioned.
- `:8000` on CPU, pid 61982 (cmdline verified
  `…/.venv/bin/python -m scriptengine.api.main`) → killed 13:47:26, port free.

## Gate 1 — pytest full suite, CUDA, in-process (13:47:32 → 13:50:33)

`scriptengine/.venv/bin/python -m pytest tests/ -q` (default device, no
`SCRIPTENGINE_DEVICE`). Raw tail:

```
........................................................................ [ 98%]
..................                                                       [100%]
1242 passed in 181.77s (0:03:01)
PYTEST_RC=0
```

**1242/1242 passed, 0 failed, 0 skipped, rc 0.** (CLAUDE.md documents the old
baseline as 1,239; the suite has since grown by 3 — all green.)

The 6 cases that OOMed under the 262k profile (Qwen owned the card) — verified
present in the run's collection and PASS-on-CUDA (the suite reports 0 failures
and 0 skips, so each of these 6 is among the 1242 passes):

1. `tests/test_context.py::TestBattleFactsReachTheQaBundle::test_a_battle_field_answer_is_in_the_bundle` — **PASS-on-CUDA**
2. `tests/test_context.py::TestBattleFactsReachTheQaBundle::test_a_low_ranked_named_fight_outcome_still_leads_the_facts` — **PASS-on-CUDA**
3. `tests/test_context.py::TestQaRecallFloor::test_a_sub_beam_answer_is_served_when_the_subject_resolves[jjk-pg-kechizu-036-…]` — **PASS-on-CUDA**
4. `tests/test_context.py::TestQaRecallFloor::test_a_sub_beam_answer_is_served_when_the_subject_resolves[jjk-pg-toge_inumaki-051-…]` — **PASS-on-CUDA**
5. `tests/test_context.py::TestQaRecallFloor::test_a_sub_beam_answer_is_served_when_the_subject_resolves[jjk-pg-tsumiki_fushiguro-129-…]` — **PASS-on-CUDA**
6. `tests/test_context.py::TestQaRecallFloor::test_an_unresolvable_subject_leaves_the_ranked_beam_alone` — **PASS-on-CUDA**

## Gate 2 — eval jjk, CUDA, in-process (13:50:46 → 13:51:31)

`scriptengine/.venv/bin/python -m scriptengine.cli eval --series jjk`
(`:8000` still down — one copy). Raw tail:

```
┃ kind        ┃ passed ┃ score ┃
┃ alias       │    2/2 │  100% │
┃ appearance  │    1/1 │  100% │
┃ fact        │    6/6 │  100% │
┃ history     │    1/1 │  100% │
┃ lexical     │    3/3 │  100% │
┃ multihop    │    3/3 │  100% │
┃ narrative   │    2/2 │  100% │
┃ overview    │    1/1 │  100% │
┃ personality │    3/3 │  100% │
┃ roster      │    2/2 │  100% │
┃ semantic    │    5/5 │  100% │
┃ sourcing    │    1/1 │  100% │
┃ trivia      │    1/1 │  100% │
31/31 (100%)   report: /home/goblin/ScriptEngine/series/jjk/audit/eval.json
EVAL_RC=0
```

**31/31 (100%), rc 0 — no failing gold question.** (A `QdrantClient.__del__`
atexit traceback appears at interpreter shutdown; known noise, not a failure.)

## Gate 3 — span-recall jjk, offline + live probe (13:51:49 → 13:54:53)

`:8000` restarted on **CUDA** at 13:51:42
(`setsid nohup … scriptengine.api.main > /tmp/scriptengine_api_cuda.log 2>&1 &`,
server pid 62617). `/health` → 200 on the first poll (13:51:44),
`"device":"cuda"`. Qwen (pid 61900) verified alive immediately after launch and
again after the probe; no OOM in `nvidia-smi` (25,150 MiB used, Qwen-only —
embedder+reranker load lazily per request within the ~7.4 GB headroom).

**Offline first** (`span-recall --series jjk`, <1 s), raw tail:

```
│ sections           │      5507 │
│ sentences          │     48572 │
│ present in a chunk │     48572 │
│ unreachable        │         0 │
│ coverage           │ 100.0000% │
OFFLINE_RC=0
```

**Then the live probe** (`span-recall --series jjk --probe 400` over `:8000`,
~3 min on CUDA), raw tail:

```
  400/400  {'HIT': 390, 'MISS_DOC': 6, 'MISS_SPAN': 4, 'TRUNCATED': 0, 'ERROR': 0}
│ probes                      │         400 │
│ served the line             │ 390 (97.5%) │
│ page not retrieved          │           6 │
│ page retrieved, line absent │           4 │
│ bundle truncated            │           0 │
│ errors                      │           0 │
PROBE_RC=0
```

Detail: `reports/span-recall/jjk/recall_verbatim.jsonl`.

## Gate 4 — canon-run opm, HTTP, one-copy (13:54:55 → 13:55:06)

`scriptengine/.venv/bin/python -m scriptengine.cli canon-run --series opm
--skip-eval` (`--skip-eval` honors the one-copy rule — the server holds the
embedder; the canon numbers are unaffected). Raw tail:

```
┃ answered exactly right             │    10/16 (62.5%) │
┃ canon items recovered              │ 236/236 (100.0%) │
┃ precision, closed sets             │ 79.0% over 16/19 │
┃ questions at recall 0              │             0/19 │
┃ confident and wrong                │                0 │
┃ fact answers present in the bundle │            20/20 │
CANON_RC=0
wrote /home/goblin/ScriptEngine/reports/2026-09-08-0824/REPORT.md
```

## New-numbers table

| Gate | Run | Result |
|---|---|---|
| pytest (full suite, CUDA in-process) | 13:47:32–13:50:33 | **1242/1242 passed**, rc 0 |
| eval jjk (CUDA in-process) | 13:50:46–13:51:31 | **31/31 (100%)**, rc 0 |
| span-recall jjk offline | 13:51:49 | **48,572/48,572 reachable (100%)**, rc 0 |
| span-recall jjk probe 400 (live `:8000` CUDA) | 13:51:51–13:54:53 | **390/400 (97.5%)** lines served, 6 MISS_DOC, 4 MISS_SPAN, 0 TRUNCATED, 0 ERROR, rc 0 |
| canon opm (HTTP, `--skip-eval`) | 13:54:55–13:55:06 | **10/16 exact (62.5%), 236/236 canon (100%), precision 79.0%** (closed sets 16/19), rc 0 |

The canon numbers are unchanged from the documented baseline (10/16, 236/236,
79.0%).

## Notes

- `:8000` **left on CUDA** (pid 62617, log `/tmp/scriptengine_api_cuda.log`) —
  the campaign session restores it to CPU on resume (262k co-location rule).
  No CPU fallback was needed; the 100k headroom (~7.4 GB) covered the lazily
  loaded embedder+reranker for the whole HTTP phase.
- One-copy VRAM rule held throughout: `:8000` down for pytest + eval (in-process
  copy), up (CUDA) for span-recall probe + canon-run, `--skip-eval` on the canon
  run so the server stayed the sole copy.
- Qwen 100k (pid 61900) alive and healthy at every checkpoint (pre, post-launch,
  post-probe); no OOM events, no `ninfer_restart` needed.
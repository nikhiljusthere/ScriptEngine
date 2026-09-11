# R-7 gate window receipt (CSM Phase 1, §9a closure loop)

- Timestamp: 2026-09-11 21:35:22 UTC (2026-09-12 03:05:22 IST)
- git HEAD: `81df799 csm: SWITCHPOINT checkpoint for the owner-directed 262k->120k (122880) mode switch (fit guard passes est 19.3k << 122880, no FORCE; helper args old_pi=7263 old_shell=3406) + sweep stale A-bay log files (2026-09-08 era, bay retired)`
- Mode: W1 in-process legs with :8000 stopped (pytest + eval); :8000 restarted on CUDA for W2 live legs (span-recall probe + canon). All model work on CUDA; SCRIPTENGINE_DEVICE never set to cpu.
- Pre-state: :8000 pid 7829 (CUDA) stopped, port confirmed free (`curl /health` failed); Qwen 27B pid 7759 untouched throughout (31,083 MiB GPU at end, `kill -0 7759` alive).

## Gate 1 — pytest (in-process, :8000 down)

Command: `scriptengine/.venv/bin/python -m pytest tests/ -q`

Numbers: 1321 collected = 1316 passed + 3 failed + 2 xpassed (190.84 s, rc=1).
The 3 failures are exactly the documented env-mcp tests (they require the live :8000 API, which was down by design for W1):
- `tests/test_mcp_server.py::test_research_returns_bundle_and_prompt`
- `tests/test_mcp_server.py::test_research_rejects_unindexed_series`
- `tests/test_mcp_server.py::test_research_bare_character_name_is_narrative`

No other failures.

Raw tail:
```
  File "/home/goblin/ScriptEngine/scriptengine/mcp/server.py", line 96, in research
    raise ValueError(
ValueError: The ScriptEngine API is not answering on http://127.0.0.1:8000/context. Start it with: python -m scriptengine.api.main
=========================== short test summary info ============================
FAILED tests/test_mcp_server.py::test_research_returns_bundle_and_prompt - fa...
FAILED tests/test_mcp_server.py::test_research_rejects_unindexed_series - Ass...
FAILED tests/test_mcp_server.py::test_research_bare_character_name_is_narrative
3 failed, 1316 passed, 2 xpassed in 190.84s (0:03:10)
```

Threshold: 0 unexpected failures (the 3 env-mcp tests failing is PASS).
**Verdict: PASS** (collected 1321 = 1316 passed + 3 env-mcp failed + 2 xpassed; the 1,305 pin predates the CSM test additions).

## Gate 2 — eval jjk (in-process)

Command: `scriptengine/.venv/bin/python -m scriptengine.cli eval --series jjk`

Numbers: 31/31 (100%). All 13 kinds at 100% (alias 2/2, appearance 1/1, fact 6/6, history 1/1, lexical 3/3, multihop 3/3, narrative 2/2, overview 1/1, personality 3/3, roster 2/2, semantic 5/5, sourcing 1/1, trivia 1/1).

Raw tail:
```
│ semantic    │    5/5 │  100% │
│ sourcing    │    1/1 │  100% │
│ trivia      │    1/1 │  100% │
└─────────────┴────────┴───────┘

31/31 (100%)   report: /home/goblin/ScriptEngine/series/jjk/audit/eval.json
Exception ignored in: <function QdrantClient.__del__ at 0x77ebde94aca0>
Traceback (most recent call last):
  File "/home/goblin/ScriptEngine/scriptengine/.venv/lib/python3.12/site-packages/qdrant_client/qdrant_client.py", line 169, in __del__
  File "/home/goblin/ScriptEngine/scriptengine/.venv/lib/python3.12/site-packages/qdrant_client/local/qdrant_local.py", line 108, in close
ImportError: sys.meta_path is None, Python is likely shutting down
```
(The trailing `Exception ignored` is benign QdrantClient atexit noise; rc=0.)

Threshold: 31/31. **Verdict: PASS**

## Gate 3 — span-recall jjk (offline + live probe 400, :8000 on CUDA)

Command (offline): `scriptengine/.venv/bin/python -m scriptengine.cli span-recall --series jjk`
Command (live): `scriptengine/.venv/bin/python -m scriptengine.cli span-recall --series jjk --probe 400`

Numbers: offline rc=0, 48,572/48,572 sentences present in a chunk, 0 unreachable, coverage 100.0000% (5,507 sections; 52 boilerplate lines excluded). Live probe: 398/400 served = 99.5% (1 MISS_DOC, 1 MISS_SPAN, 0 truncated, 0 errors).

Raw tail (offline):
```
      Chunk containment: jjk      
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃                    ┃           ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ sections           │      5507 │
│ sentences          │     48572 │
│ present in a chunk │     48572 │
│ unreachable        │         0 │
│ coverage           │ 100.0000% │
└────────────────────┴───────────┘
52 sentences in link-list boilerplate excluded; --include-boilerplate to audit 
them.
```
Raw tail (probe):
```
  400/400  {'HIT': 398, 'MISS_DOC': 1, 'MISS_SPAN': 1, 'TRUNCATED': 0, 'ERROR': 0}
         Live probe: jjk (verbatim)          
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃                             ┃             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ probes                      │         400 │
│ served the line             │ 398 (99.5%) │
│ page not retrieved          │           1 │
│ page retrieved, line absent │           1 │
│ bundle truncated            │           0 │
│ errors                      │           0 │
└─────────────────────────────┴─────────────┘
```

Threshold: offline rc=0 + probe ≥97.5%. **Verdict: PASS** (99.5%)

## Gate 4 — canon-run opm (live, :8000 on CUDA)

Command: `scriptengine/.venv/bin/python -m scriptengine.cli canon-run --series opm --skip-eval`

Numbers: canon items recovered 236/236 (100.0%); answered exactly right 10/16 (62.5%); precision (closed sets) 79.0% over 16/19; recall-0 questions 0/19; confident-and-wrong 0. Run dir: `reports/2026-09-11-2135/`.

Raw tail:
```
               Canon run: 2026-09-11-2135                
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃                                    ┃                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ answered exactly right             │    10/16 (62.5%) │
│ canon items recovered              │ 236/236 (100.0%) │
│ precision, closed sets             │ 79.0% over 16/19 │
│ questions at recall 0              │             0/19 │
│ confident and wrong                │                0 │
│ fact answers present in the bundle │            20/20 │
└────────────────────────────────────┴───────────────────┘
```

Threshold: 236/236 canon. **Verdict: PASS** (236/236, 10/16 exact, 79.0% — matches the re-baselined receipt)

## Post-gate GPU health

```
$ nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader
31083 MiB, 32607 MiB, 100 %
$ kill -0 7759 && echo qwen-alive
qwen-alive
```
Qwen (pid 7759) alive; memory reflects Qwen's pre-reserved pool + the restarted :8000's lazily-loaded embedder+reranker (~5 GB) co-located on CUDA — the sanctioned quiet-window pattern.

:8000 state at end: running on CUDA (pid 17494, `/tmp/scriptengine_api_r7.log`), health 200.

**Overall verdict: PASS — 4/4 gates (pytest 1316/1321 with only the 3 documented env-mcp failures; eval 31/31; span-recall offline 48,572/48,572 + probe 99.5%; canon 236/236 / 10/16 / 79.0%). JJK baseline intact; Qwen never touched.**
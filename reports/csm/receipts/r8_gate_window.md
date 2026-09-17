# R-8 gate window receipt (CSM Phase 2 P2.1 pre-sweep; council #30 A2 launch order)

- Timestamp: W1 2026-09-17T07:14:22+05:30 → W2 end 2026-09-17T07:22:01+05:30 (IST)
- git HEAD (gate tree): `8661850 csm: Claude GPU handoff prompt (plan/gpu_p21_task.md) — deterministic …`; fixes commit `aada154` (R-8); last gate-relevant commit `b8b0ed5` (env-mc test rename, count-neutral) — `git diff --name-only b8b0ed5..HEAD -- scriptengine series/csm/overrides.yaml tests` is empty
- Mode: Qwen stopped via `~/ninfer-work/ninfer-stop.sh` (already down: "nothing to unload"; `qwen_mode.txt` = `mode=off`, :18080 not listening). W1 in-process with :8000 down (pytest, then eval — sequential, one Qdrant client at a time); :8000 started setsid-detached from this tree on CUDA (pid 178118, `/health` device=cuda, started 2026-09-17T01:48:35Z) for W2. Whole card, SCRIPTENGINE_DEVICE unset throughout.

## Gate 1 — pytest (W1, :8000 down)

Command: `scriptengine/.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`

Numbers: 1,331 collected = 1,326 passed + 3 failed + 2 xpassed (rc=1). The 3 failures are the W1 env-mc trio (`tests/test_mcp_server.py:20,35,46`, `httpx.ConnectError [Errno 111]` — :8000 down by design). Matches the council #30 A5 W-state pin exactly.

```
FAILED tests/test_mcp_server.py::test_research_returns_bundle_and_prompt - fa...
FAILED tests/test_mcp_server.py::test_research_rejects_unindexed_series - Ass...
FAILED tests/test_mcp_server.py::test_research_bare_character_name_is_qa - fa...
3 failed, 1326 passed, 2 xpassed in 195.81s (0:03:15)
```

**Verdict: PASS** (pin 1,331)

## Gate 2 — eval jjk (W1, in-process)

Command: `scriptengine/.venv/bin/python -m scriptengine.cli eval --series jjk` (rc=0)

```
│ alias       │    2/2 │  100% │
│ appearance  │    1/1 │  100% │
│ fact        │    6/6 │  100% │
│ history     │    1/1 │  100% │
│ lexical     │    3/3 │  100% │
│ multihop    │    3/3 │  100% │
│ narrative   │    2/2 │  100% │
│ overview    │    1/1 │  100% │
│ personality │    3/3 │  100% │
│ roster      │    2/2 │  100% │
│ semantic    │    5/5 │  100% │
│ sourcing    │    1/1 │  100% │
│ trivia      │    1/1 │  100% │
31/31 (100%)   report: /home/goblin/ScriptEngine/series/jjk/audit/eval.json
```

**Verdict: PASS** (31/31; the trailing QdrantClient.__del__ ImportError is benign atexit noise)

## Gate 3 — span-recall jjk (W2, :8000 CUDA)

Commands: `cli span-recall --series jjk` (rc=0) then `--probe 400` (rc=0)

```
│ sections           │      5507 │
│ sentences          │     48572 │
│ present in a chunk │     48572 │
│ unreachable        │         0 │
│ coverage           │ 100.0000% │
52 sentences in link-list boilerplate excluded; --include-boilerplate to audit 

│ coverage           │ 100.0000% │
  400/400  {'HIT': 398, 'MISS_DOC': 1, 'MISS_SPAN': 1, 'TRUNCATED': 0, 'ERROR': 
│ probes                      │         400 │
│ served the line             │ 398 (99.5%) │
│ page not retrieved          │           1 │
│ page retrieved, line absent │           1 │
│ bundle truncated            │           0 │
│ errors                      │           0 │
```

**Verdict: PASS** (48,572/48,572 offline, 100.0000%; live 398/400 = 99.5% ≥ 390/400; ledger `reports/span-recall/jjk/recall_verbatim.jsonl` +400 rows)

## Gate 4 — canon-run opm --skip-eval (W2, same service)

Command: `cli canon-run --series opm --skip-eval` (rc=0), run dir `reports/2026-09-17-0151/`

```
│ answered exactly right             │    10/16 (62.5%) │
│ canon items recovered              │ 236/236 (100.0%) │
│ precision, closed sets             │ 79.0% over 16/19 │
│ questions at recall 0              │             0/19 │
│ confident and wrong                │                0 │
│ fact answers present in the bundle │            20/20 │
```

**Verdict: PASS** (236/236 canon, 10/16 exact, 79.0% precision, 0 confident-wrong — baseline-identical to 2026-09-11-2135 / -2218)

## Summary

All four standing gates + eval jjk green at the post-R-8 pin 1,331 on tree `8661850` (JJK stays 100%). The :8000 service that ran W2 (pid 178118) is left up, unrestarted, for the P2.1 runner (GATE.md launch-order step 6).

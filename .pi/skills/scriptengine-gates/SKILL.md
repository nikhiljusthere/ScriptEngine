---
name: scriptengine-gates
description: Run ScriptEngine's standing verification gates in the right order with the right baselines — audit before index, span-recall after index, the four standing gates after any build (pytest, eval jjk, span-recall jjk, canon-run opm), plus comprehension-gate/continuity for D6. Use before declaring any pass done and after touching chunking, fusion, retrieval, or the parser.
---

# scriptengine-gates — standing verification

All commands from the repo root (`/home/goblin/ScriptEngine`), venv =
`scriptengine/.venv/bin/python` (activate it or call it directly).

## Ordering (never invert)

1. `python -m scriptengine.cli audit --series X` — **ALWAYS before** `index`
   (a broken extractor is silent; that is what the audit exists to catch).
2. `python -m scriptengine.cli index --series X` (add `--no-embed` to skip GPU).
3. `python -m scriptengine.cli span-recall --series X` — **ALWAYS after**
   `index`. Exit 2 = content unreachable; fix it before authoring anything
   against the index.

## The four standing gates (re-run after every build)

| gate | command | baseline (2026-09-08, gpu-gate3 re-baseline on the 1,249 tree — `reports/csm/GATE_REBASELINE_2.md`) |
|---|---|---|
| tests | `python -m pytest tests/ -q` | 1,249 passed (CUDA; the 1,242 baseline was stale — CSM-2 added 7 tests) |
| eval jjk | `python -m scriptengine.cli eval --series jjk` | 31/31 |
| span-recall jjk | `python -m scriptengine.cli span-recall --series jjk` | 48,572/48,572 (rc=0); live probe: 390/400 (97.5%) |
| canon opm | `python -m scriptengine.cli canon-run --series opm` | 10/16 exact · 236/236 · 79.0% |

Device rule for gate runs that load the reranker: CUDA-first order from
`CLAUDE.md` (free → CUDA; Qwen-holds-the-card → `SCRIPTENGINE_DEVICE=cpu`;
short bounded probe → the sanctioned co-location, only in a Qwen quiet
window, health-checked afterwards). Comprehension work adds:

```
python -m scriptengine.cli comprehension-gate --series jjk
python -m scriptengine.cli continuity --series jjk --triage
```

## Rules

- Gates are regression checks, **not scoreboards**: a gold failure means
  diagnose the root cause (fix gold / fix router / fix chunker) — never tune
  the retriever to make one ambiguous prompt green. Record gold fixes with
  their reason in `gold_jjk.json`.
- A pass is "done" only when its gate re-ran green on the current store.
- Record results in a dated `reports/<ts>/` dir; after batch commits,
  regenerate `reports/page-campaign/COVERAGE.md` with
  `python tools/coverage_report.py` (never hand-edit).
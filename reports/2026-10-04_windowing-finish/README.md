# Windowing-100 finish — gate receipt (2026-10-04)

Brief: `plan/WINDOWING_100_FINISH.md` (WP1–WP6 + WP3b + WP6b; worker opencode 27B,
every WP re-checked independently by Claude). Gates run at 100k, CUDA, after the
`windows.py` change (content-addressed `window_id`, default gen = CURRENT_GEN).

| gate | result | baseline | verdict |
|---|---|---|---|
| pytest | 10F / 1,487P / 2XP (`pytest.txt`) | 9F / 1,485P / 2XP (+3 new window tests) | exact — the 9 baseline failures identical; the 10th (`test_page_gen::test_page_sweep_command`) is environmental: this shell exports `FORCE_COLOR=3`, Rich colours the CLI output, the plain-text assert misses; `env -u FORCE_COLOR` → 1 passed; test + cli.py untouched vs HEAD |
| eval jjk | 31/31 (100%) (`eval_jjk.txt`) | 31/31 | exact |
| span-recall jjk | 0 unreachable · 100.0000% · `index_misses.jsonl` byte-identical (`cmp`) to `2026-09-30T0720_day2-baseline` | same | exact |
| canon-run opm | 10/16 · 236/236 · 79.0% · 0 confident-wrong (`reports/2026-10-04-1218/`) | 10/16 · 236/236 · 79.0% | exact |

Dataset gates (`tools/train/dataset_gates.py`, zero-LLM): jjk D1–D7 PASS, mcu D1/D2/D4/D6
PASS (D3/D5/D7 SKIP, no gold yet); mutation test: injected holdout page + duplicate id +
broken quote → D1–D4 FAIL rc=1.

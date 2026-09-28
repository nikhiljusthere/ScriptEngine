# Four standing gates on the R10 tree (2026-09-29, architect-run, CUDA, Qwen unloaded)

Tree: `40af54da` (engine = `6a0faa65`: R10 data + code + receipt on top of bug B `b26173d3`, page-type scope `45d18b17`). Qwen stopped (`ninfer-stop.sh`), card free; `:8000` on CUDA ×3 workers for gates 3–4 and the mcp re-run, stopped for gate 2. Logs: `/tmp/opencode/gates_0929/`, `/tmp/se_p2/gate1_pytest_r10.out`.

| gate | result | baseline |
|---|---|---|
| 1 pytest | 1,431 passed + 2 xpassed + 2 failed (worker run 00:46–00:51); re-run of the two: `test_mcp_server` 7/7 green with `:8000` up (its failure was a CUDA OOM loading the reranker beside Qwen 23 GB + pytest's in-process models 5.9 GB); `test_blind_panel_universe` = the known date-rot | 1,397 + 2 xp @ `9a335d40` (+ the R10/bug-B/scope test delta) |
| 2 eval jjk | **31/31** with `:8000` stopped. A first run with `:8000` up scored 29/31: embedded Qdrant is an exclusive lock and `VectorStore.exists()` swallows the lock error, so the in-process retriever ran lexical-only (LESSONS `40af54da`). Invalid run, not a regression | 31/31 |
| 3 span-recall jjk | 48,572/48,572 offline; probe 398/400 (99.5%) | 48,572; 398/400 |
| 4 canon opm | 10/16 exact, 236/236 canon, 79.0% (`reports/2026-09-28-1948/REPORT.md`) | 10/16 · 236/236 · 79.0% |

All baseline-exact.

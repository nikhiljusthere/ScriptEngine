# Standing gates — 2026-09-28 (post P2a 9a335d40)

Process rule (architect 2026-09-28): commit, then tests + cross-wiki type
diff + the four gates, and only then mutate a store. Receipt for the gates
half; the cross-wiki type diff (P2) lands in /tmp/se_p2/*_report.md and is
summarised in the P2 store-mutation receipt.

## Gate 1 — tests (`pytest tests/ -q`)

- Main tree (post-P2a): **1,397 passed + 2 xpassed + 4 failed** (250s)
  - 3 × `tests/test_mcp_server.py` — the documented `:8000`-down env trio
    (RED while the API server is down; **all 7 pass with :8000 up**,
    re-confirmed this run: `7 passed in 4.10s`)
  - 1 × `tests/test_blind_panel_universe.py::test_drawn_panel_subjects_satisfy_their_class_filter`
    — **date-rot env failure, pre-existing**: `_panel_path` is strictly
    `blind_panel_<today>.jsonl` and today's panel has not been drawn
    (latest on disk: 2026-09-27). Fails identically in the pre-P2a base
    worktree (verified standalone), so it is not attributable to P2a.
- Suite grew since the 1,350 baseline (Marvel campaign + this session's
  link-aware/reality/R8/T-GAP/P2a tests); the GREEN condition (documented
  env trio + no other failure) holds modulo the documented date-rot.
- P2a's own 4 tests (`TestDeclaredStructuralInfoboxes`) pass; full
  `tests/test_ontology.py` 30/30.

## Gate 2 — eval jjk (`cli eval --series jjk`)

- **31/31 (100%)** — baseline exact.
  report: series/jjk/audit/eval.json

## Gate 3 — span-recall jjk (`cli span-recall --series jjk`)

- **48,572/48,572 present in a chunk, 0 unreachable, rc=0** — baseline exact.

## Gate 4 — canon opm (`cli canon-run --series opm`)

- **10/16 exact · 236/236 (100%) · 79.0% precision over 16/19 · 0 recall-0 ·
  0 confident-and-wrong · 20/20 fact answers** — baseline exact.
- The gate needs the :8000 API server (steady state: down). Started on CUDA
  (bge-large + bge-reranker-v2-m3, ~9 GB free headroom). **Currently LEFT
  UP** (pid 44032, log /tmp/se_p2/api_8000.log) — the mcp trio is green
  while it runs; stop it (`kill 44032`) before the D3 VRAM phase or to
  restore the documented steady state.
  report: reports/2026-09-28-1427/REPORT.md

## Verdict

All four gates green on the committed P2a tree; no regression attributable
to the structural_infoboxes change. Store mutation may proceed once the
cross-wiki type diff (P2) confirms the intended 430-page mcu move.
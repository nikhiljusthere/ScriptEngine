# iter-1 R-5 relations-mode — the four standing gates + R-5 meter (raw)

Window: 2026-09-09 23:20–23:50Z (after the 5-reviewer + chairman council
wave closed ~23:20Z and amendments A1–A5 were applied). Qwen @100k pid 58178
alive throughout; GPU co-location respected (no in-process model load while
`:8000` held its models; the one in-process model job — the failed
canon-run attempt — happened after `:8000` was stopped).

## Window structure (GPU discipline)

- **W1** (23:20–23:32Z, `:8000` STOPPED — announced to the owner before the
  stop): full `pytest tests/ -q` + `eval --series jjk` in-process on CUDA
  (in-process embedder+reranker ~5.3 GB co-located with Qwen 25,053 MiB).
  Logs: /tmp/w1_pytest.log, /tmp/w1_eval.log.
- **W2** (23:32–23:50Z, `:8000` UP on CUDA, new pid 122932→123755):
  span-recall probe 400 + R-5 meter over HTTP; then `:8000` stopped again
  (announced, same window) for the canon-run attempt (which turned out to be
  an HTTP client and was re-run with `:8000` up); `:8000` relaunched at the
  end of the window.

## Gate results

| gate | result | baseline (2026-09-08 re-baseline) | verdict |
|---|---|---|---|
| 1. `pytest tests/ -q` | **1,315 collected** (= chairman's post-amendment pin 1,305+8+2); W1: 1,310 passed, 2 xpassed, 3 failed | 1,305 pin, 0 failed | GREEN (see mcp note) |
| 2. `eval --series jjk` | **31/31 (100%)**, RC 0 | 31/31 | GREEN |
| 3. `span-recall --series jjk` | offline **unreachable = 0**, RC 0 (48,572-line corpus); live probe **398/400 (99.5%)** | 48,572/48,572 + 390/400 (97.5%) | GREEN (probe above baseline) |
| 4. `canon-run --series opm --skip-eval` | **10/16 exact, 236/236 canon, 79.0%** over 16/19 | 10/16, 236/236, 79.0% (floor 74.0%) | GREEN (exact match) |
| R-5 meter | **5/11 complete** (≥1 HIT off 0/11); partials = 5 budget-trim (proven) + 1 content gap | 0/11 → ≥1 HIT | GREEN (per wave bar) |

Raw: /tmp/w2_probe.log (probe), /tmp/w2_r5meter.log (meter),
/tmp/w2_canon.log (canon, RC 0), /tmp/w1_pytest.log, /tmp/w1_eval.log.
Report written by canon-run: reports/2026-09-09-2344/REPORT.md.

## Gate-1 mcp note (the one W1 failure set, and the pre-existing finding)

W1 ran with `:8000` STOPPED. `tests/test_mcp_server.py` is a live-HTTP client
(3 tests POST to `:8000`); with the service down, 3 failed environmentally.
W2 re-ran the file with `:8000` UP: **6 passed, 1 failed** —
`test_research_bare_character_name_is_narrative`
(`data["mode"]` = qa, expected narrative; the router's bare-name rule,
router.py:809, routes a 2-word bare character name to qa).

**Proven pre-existing, not an R-5 regression:** at 2026-09-09 23:35Z the
working tree was stashed (all 7 R-5/amendment files), a fresh `:8000` was
started from HEAD code, and the test was re-run — it still failed. The
bare-name rule (8d07487, "Route to three destinations, not two") predates the
test (d531329); the R-5 diff does not touch that path, and "Maki Zenin" does
not fire the (old or new) `_RELATIONS` trigger. The test's own comment states
the intent ("a bare name is a lookup for /context but a story for a script"),
which the auto-router's bare-name rule contradicts — a live
router-contract vs mcp-contract item, **out of scope for the R-5 fix class**
(the §9a loop only touches pre-registered fix classes). Carried to the close
council as a numbered item; fixing the bare-name rule would change JJK
routing and risks the baseline-exact invariant, so it is not touched in this
wave.

Effective gate-1 for this wave: **1,315 collected / 0 failures attributable to
R-5 or A1–A5** (W1 1,310+2xp with 3 environmental mcp failures under a stopped
service + W2 mcp re-run 6/7 with the 1 failure proven pre-existing at HEAD).

## Amendments applied in this window (A1–A5, per chairman.md)

1. A1 — `router.py` `_RELATIONS` tightened to 4 alternatives (documented-
   relationship / relationship-of-with-to-between / how-is-related /
   how-does-relate); dropped `\bconnection\b` (alt4), the bare `\brelationship\b`
   over-capture (alt1), and the who/what-is-X-to verb-phrase over-captures
   (alt5). 0 new hits in official+eval banks.
2. A2 — `context.py` budget-unit bug: deleted `budget_chars = int(token_budget
   * CHARS_PER_TOKEN)`; the guard now compares token cost against
   `token_budget` (was 3.6× over-permissive in char units).
3. A3 — `api/main.py` relations→qa empty-pair fallback (auto-only, after the
   roster block, uses the routed subject).
4. A4 — same fallback in `cli.py` (unconditional, matching the local roster
   style) and `script/writer.py` (auto-gated, matching its local roster
   style); `mcp/server.py` untouched (thin proxy inherits A3).
5. A5 — `tests/test_router.py` store-free trigger-boundary test (4 positive,
   7 negative); `tests/test_context.py` `test_relations_budget_units`
   (`tokens_used <= token_budget` at `token_budget=200`).

First-thing verification (in-process, model-free): `pytest
tests/test_router.py tests/test_context.py::TestRelationsBundle -q` =
**146 passed, 0 failed**; `pytest tests/ --collect-only -q` = **1,315**
(matches the chairman's pin exactly).

b_session_verification: reports/csm/receipts/council_r5/b_session_verification.md.
# Council R-5 — B-session verification (the verifying session's duty, 2026-09-10)

B read `chairman.md` from disk, re-verified every load-bearing claim itself
(model-free), applied amendments A1–A5, and ran the "one thing to do first"
batch. Results:

## Claim verification (independent of the chairman's run)
- Tightened `_RELATIONS` (A1) simulated over all banks: **0 hits in all 8
  official banks + all eval banks** (chairman: 0 — confirmed).
- Frozen queue: **4/4 csm-rel rows match the amended trigger** (confirmed).
- Probe: **11/11 `_csm_relations.json` rows match** (confirmed).
- Negative controls re-run: "last connection to" / "Who is left to stand
  against Mahito, per Chapter 131?" / "relationship status in Episode 30" all
  match the OLD trigger and none match the amended (confirmed, the three
  falsified over-captures).
- Fallback sites: main.py roster block L228-235 + `subject` local L206/215
  (always in scope), cli.py L1699-1702, writer.py L494-497, mcp thin httpx
  proxy (all confirmed; 3 sites, not D's 4).
- Budget unit: context.py L419 `budget_chars = int(token_budget *
  CHARS_PER_TOKEN)` vs token-cost `cost = estimate_tokens(line) + 5`
  (confirmed the 3.6x cap); sibling modes charge tokens vs token_budget
  (L203-209, L272-279, L659-660).

## Two corrections to the chairman's record (counts, not logic)
1. **Re-pin class size**: chairman residual 4 says "34 unique qa/roster batch
   rows". Measured with the amended trigger over all `_` banks: **79 firing
   rows (74 unique texts) = 11 relations-pinned (the probe bank) + 39 qa + 29
   roster**. The re-pin set is the 68 qa/roster rows; the deterministic list
   is the sweep output (gate time), not a hand count.
2. **Fallback vs route_ok are orthogonal** (harness.py L136-152): `route_ok =
   route().mode == expect_mode` compares the ROUTER's decision, not the
   bundle. A3/A4 protect *content* (empty-pair pairs get the qa prose); only
   re-pinning the 68 rows to `relations` protects *route_ok*. Both are needed
   (amendments 3/4 + residual 4 together close it; neither alone).
   Consequence for the gate: every re-pinned row whose pair has no relation
   rows (39 empty-pair firings, measured) answers via the qa fallback — the
   re-sweep judges those on the qa content, and a miss there halts per frame
   gate 5 (pre-registered).

## Amendments applied (this session) + first-thing verification
- A1 router.py: `_RELATIONS` → 4 alternatives (documented-relationship /
  relationship-of-with-to-between / how-is-related / how-does-relate);
  dropped `\bconnection\b`, bare `\brelationship\b`, who/what-is-X-to.
- A2 context.py: deleted `budget_chars`; guard now `used + cost >
  token_budget` (+ why-comment citing the bug).
- A3 main.py: relations→qa empty fallback after the roster block, auto-only,
  routed `subject` local.
- A4 cli.py (unconditional, matching local roster style) + writer.py
  (auto-gated) same fallback; mcp unchanged (proxy inherits A3).
- A5 tests: test_router.py module import `_RELATIONS` + store-free
  `TestRelationsTrigger::test_relations_trigger_boundaries` (4 positives,
  7 negatives); test_context.py `TestRelationsBundle::test_relations_budget_units`
  (`tokens_used <= 200` at token_budget=200).
- Record item (a): frame.md L23 "8 model-free tests" → "8 collected tests
  (3+2 parametrized router trigger + 3 builder; none store-free
  pre-amendment; the store-free trigger test is amendment A5(a))".
- Record item (b) (validate_relations receipt cites link_entities @815 /
  edges_for @935 / relations_of @1393): to the gate receipt.

Verification batch (all model-free, GPU unchanged at 29,209 MiB):
- `pytest tests/test_router.py tests/test_context.py::TestRelationsBundle -q`
  = **146 passed, 0 failed** (both new tests pass; A5(a) store-free).
- `pytest tests/ --collect-only -q` = **1,315** (chairman's predicted pin,
  1,305 + 8 + 2).
- Recall diff re-run (standing rule 1): PRE 233 firings → POST 79; 0
  official+eval hits; 68 re-bind debt; 39 empty-pair. Receipts:
  /tmp/csm_iter1_records/sweep_relations_bank_PRE_amend.txt +
  sweep_relations_bank_out.txt (+ the verify_amend_sim.py simulation).

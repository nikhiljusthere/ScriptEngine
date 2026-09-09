Review 2.

**Strongest: A.** Its trigger over-match finding is load-bearing and correct. Verified: `\bconnection\b` (router.py:476) steals 20 qa-pinned prose questions in the current `questions/` bank; official gold banks hold zero connection/relationship questions (`scriptengine/eval/gold_*.json`), the four gates are blind; `harness.py:98-102` turns each steal into a `route_ok` miss → gate-5 halt. The deletion is R-5-safe: all 11 frozen R-5 rows fire alt-1 "relationship" (verified, frozen queue).

**Blind spot: B.** Its 0-match scan covered official banks only; the campaign bank holds 222 live non-relations matches: 20 qa-conn, ~25 pure-prose "what is X to" qa steals, and 112 pre-R-5 "relationship" pins (83 qa, 29 roster) needing re-pinning to `relations`. B calls `connection` "acceptable as-is" — disputed — and its own tightening `who (is|was) X to` still matches "Who is sent to fight Kenjaku?", "What was transferred to…" (verified live).

**All five missed:** the budget unit bug. `context.py:419-429` charges `estimate_tokens()` (tokens) against `budget_chars = token_budget×3.6` (chars): the cap is 3.6× the requested budget and `truncated` stays False; roster/qa compare tokens to `token_budget` (`context.py:277`, `:660`). Verified by simulation: `token_budget=120` → `tokens_used=416`. Catching check: a model-free test asserting `tokens_used ≤ token_budget`.

Minor: D's `mcp/server.py:86` "same block" doesn't exist (thin HTTP client — fix 3 callers, not 4); C cites `edges_for` at `facts.py:815` — that's `link_entities` (`edges_for` is :935).
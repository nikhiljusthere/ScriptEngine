# Council R-5 advisor 3/5 (adv_C) — final ruling

Recovered from the framework-persisted oracle transcript (run a5b1a296-6a89-4a21-ab49-1ee2e5193224, agent=oracle, ts=1788991719968).
The parent council workflow (429d9efa) was cancelled to enforce one-member-at-a-time council concurrency;
this advisor's work was recovered from disk rather than re-run.

---

## Advisor 3/5 — BUILDER CORRECTNESS

I read `_relations_context` (context.py:342-447), the primitives it feeds (`rank_relations` roster.py:2397, `relations_of` facts.py:1393, `edges_for` facts.py:815, `link_entities` facts.py), and the tests. Verdict on my focus:

**Sound on the load-bearing path.** The R-5 door routes correctly and answers correctly; the first-row floor holds; the `rank_relations` input shape is compatible.

Findings (all minor / non-blocking):

1. **Subject resolution (L368-381) is correct but the fallback is narrower than the trigger.** `names` = `[subject]` when authored, else `link_entities(probe)[:3]` names, else the regex `relationship(?:s)?\s+(?:of|with)\s+([\w ]+)$` (L379). The fallback only catches **"of/with"**, not **"between"**. A "relationship **between** X and Y" resolves only if X or Y links to a known node; if neither does, `names = []` → empty bundle. Non-blocking (real relationship questions name characters that link; the "between" probe "What is the relationship between Denji and Makima?" links both). Just a quiet gap for two unlinked names.

2. **The dedup key includes `quote`, so the same relationship can double-list (L383-408).** Edges are seeded with `quote=""` (L386); LLM rows carry their real quote, and the `seen` set (L396) is keyed `(source,relation,target,quote)`. A quoted LLM row therefore *never* matches a bare edge's key, so `Denji→Makima (mentor)` can appear twice — once as the bare edge, once as the quoted LLM row. This is a redundancy, not a wrong answer: `rank_relations`'s quoted-row preference (roster.py:2436) puts the quoted copy ahead of the bare one on a tie. If the council wants it tighter, drop `quote` from the dedup key (dedup on `(source,relation,target)` only) so the quoted row replaces the bare edge instead of appending. Optional.

3. **`rank_relations` input shape is compatible (L410).** It reads only `relation` / `confidence` / `quote` (via `.get`, roster.py:2434-2436); it does **not** need `order` (that's added later in the budget loop, L430). All present. No bug.

4. **First-row-never-dropped holds (L419-431).** `if included and used + cost > budget_chars: break` — `included` is empty on the first iteration, so the guard is false and row 1 is always kept. Same floor the roster/qa paths use. Correct.

Cosmetic (won't block):
- **`relations_available`/`truncated` under-report under `top_k` (L412, L443-444).** After `ranked = ranked[:top_k]`, `truncated = len(included) < len(ranked)` and `relations_available = len(ranked)` reflect the *capped* list, so a caller who passes `top_k=10` against Denji's 168+ relations sees `truncated=False, relations_available=10`. The R-5 probes pass no `top_k`, so they're unaffected; only a future `top_k` caller is misinformed.
- **The budget walk (L419-431) charges per-relation lines but not the `## Relationships` header** that `render_prompt` prepends → a soft over-budget by one header. Consistent with how roster/qa charge; not a correctness issue.

None of these break the R-5 answer or the JJK/OPM invariants; the trigger over-match risk (`connection`, "what is X to Y") is advisor 1's lane and is gate-catchable.

APPROVE

# Council R-5 advisor 4/5 (adv_D) — final ruling

Recovered from the framework-persisted oracle transcript (run ce761aa4-1f11-4910-9b8d-a33cd5b17a71, agent=oracle, ts=1788992013583).
The parent council workflow (429d9efa) was cancelled to enforce one-member-at-a-time council concurrency;
this advisor's work was recovered from disk rather than re-run.

---

I have the full picture now. Here's my adversarial review, scoped to my area (API plumbing + empty-case).

## Scope I actually read
- `api/context.py` — `MODES`, `build_context` dispatch, `_relations_context` (L342–447, incl. the LLM-row mapping at L405–409 and the budget loop L420–431)
- `retrieve/router.py` — `MODES`, `_RELATIONS`, `route()` rule 2d
- `api/main.py` — `ContextRequest.mode` (L79), `/context` (L190–258), and the existing **roster empty-fallback at L228–235**
- `retrieve/roster.py` — `rank_relations` (L2397, quoted-wins tie-break L2432)
- `stores/facts.py` — `relations_of` (L1393), `edges_for` (L935), `link_entities` (L815)
- The other three callers with the same fallback block: `cli.py:1699–1702`, `mcp/server.py:86–89`, `script/writer.py:494–497`

## Plumbing — CONSISTENT, no bug
- `MODES` agrees everywhere: router tuple (L55), context set, and `main.py:79` `Literal["qa","narrative","roster","relations","auto"]`.
- Every caller resolves `"auto"` **before** `build_context` (`main.py:207–209`, `cli.py:1691–1693`, `mcp/server.py:78–80`, `writer.py:486–488`), so `build_context` never receives `"auto"` (which is *not* in `context.MODES` and would `ValueError`). No leak.
- Dispatch is correct: `build_context` guards `mode not in MODES` then routes `relations → _relations_context(..., top_k, subject)`.

## Builder — CORRECT, one minor tuning note
- Union of graph `edges_for` + LLM `relations_of(both_ways)`, deduped by `(source, relation, target, quote)`. LLM rows are mapped `confidence: 1.0` + their verbatim `quote` (L405–409), so `rank_relations`'s quoted-wins tie-break (L2432) correctly leads with the wiki's own words. Good.
- **Minor (not a blocker):** `edges_for(ids, min_confidence=0.9, …)` (L390) is tighter than the store default 0.5. For "Every *documented* relationship" this can drop 0.5–0.9 infobox links. The authoritative LLM rows are unaffected, so the R-5 HIT is safe — only lower the threshold if a needed relationship is a medium-confidence edge.

## The gap (my focus): empty-case — `relations` has no fallback, `roster` does
This is the real miss. `main.py:228–235` (and the same block in `cli.py:1700`, `mcp/server.py:86`, `writer.py:494`) falls back when a roster comes back empty:

```python
if mode == "roster" and not bundle.get("members") and request.mode == "auto":
    bundle = build_context(paths, request.query, mode="narrative", ...)
```

The new `relations` mode has **no equivalent in any of the four callers.** Consequences:

1. **Inconsistency with the established pattern.** The codebase's rule is "an empty set-shape is not an answer, fall back." `relations` is a set-shape (a character's relationship set) but was never given the fallback. The builder's "answer empty (honest)" contract is right *for the builder*; the callers are the layer that falls back, and they were missed.
2. **A silent JJK/OPM invariant regression vector.** Rule 2d's `_RELATIONS` includes the bare `\bconnection\b`. A story question like *"What is the connection between the Culling Game and the Shibuya Incident?"* matches `connection`, routes to `relations`, and returns an **empty** bundle (two events have no documented relationship rows). The intended prose answer is lost. Unlike a wrong-passage over-match, an *empty* bundle passes a gold that only checks "no wrong passages," so the gate may not catch it.

**Minimal fix:** mirror the roster block in all four callers, targeting `qa` (prose — where relationship mentions live when they weren't extracted; `narrative`/chronology is the wrong shape for relationships):

```python
if mode == "relations" and not bundle.get("relations") and <asked> == "auto":
    bundle = build_context(paths, <query>, mode="qa", token_budget=…, top_k=…)
```

This leaves an *explicit* `mode="relations"` request honest-empty (the caller asked for relationships, gets the empty set) — same as roster — while an `auto` misroute recovers the prose answer.

OBJECTION: add the roster-style empty-fallback for `relations` to all four callers (main.py:228, cli.py:1700, mcp/server.py:86, writer.py:494), targeting `qa` not `narrative` — without it, an `auto` relationship/connection question for a character with 0 documented relationships (the trigger's `connection` alternative over-matching a story question) returns an empty bundle and silently loses the prose answer.

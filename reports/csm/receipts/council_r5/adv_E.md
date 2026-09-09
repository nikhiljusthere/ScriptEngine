# Council R-5 advisor 5/5 (adv_E) — final ruling

Recovered from the framework-persisted oracle transcript (run ee15179f-4303-4a65-9d9d-07579d222d4a, agent=oracle, ts=1788992234179).
The parent council workflow (429d9efa) was cancelled to enforce one-member-at-a-time council concurrency;
this advisor's work was recovered from disk rather than re-run.

---

I have what I need. `link_entities` (facts.py) confirms alias-awareness: it `JOIN`s the `aliases` table, so the relations door's subject resolution already inherits alias resolution for free. Finalizing my verdict.

---

**Focus: TEST ADEQUACY + R-6 FLOOR INHERITANCE.**

**Test adequacy — the 8 model-free cases are a sufficient *first pass*, but the record overstates coverage: one test doesn't exist, and the union isn't pinned.**

Findings (file:line):
1. **The pure-regex trigger test does NOT exist.** The work_log/summary record claims `test_relations_phrasings_are_recognised` (pure regex, no store), but `tests/test_router.py:19` imports only `_NARRATIVE_VERBS, _WH, Route, route` — `_RELATIONS` is *not* imported, and no store-free trigger test is in the file. So the 5-alternative `_RELATIONS` regex (`router.py:475`) is pinned **only** by the end-to-end route tests (`test_router.py:122-145`), which `pytest.skip` when CSM isn't indexed (`test_router.py:128,144`). Net: on a data-less checkout the R-5 trigger logic is untested. **Shall (non-blocking, worth landing in-commit):** add a store-free trigger test (pattern: `test_interrogatives_are_recognised`, `test_router.py:29`) asserting the 5 alternatives fire and a boundary set does not (e.g. "what is the key to understanding", "Every connection"), and correct the record that claims it exists.
2. **The union (graph edges + LLM rows) is not pinned.** `test_relations_mode_serves_the_character_relations` (`test_context.py:435`) asserts `len(relations) >= 1` and `any(quote or era)` — both satisfied by the LLM rows alone, so a regression that silently drops the `edges_for` union (`context.py:391`) still passes. The guard is the R5 re-sweep (own-new-row HIT), not the model-free test. Non-blocking (re-sweep-covered), but the test should assert a graph-edge row (quote=="" and era=="") is actually in the union.
3. **Empty case untested.** `_relations_context` is graceful for a 0-relation subject (`ranked=[]` → `relations=[]`, `truncated=False`; `context.py:437-445`), but no test pins it. Minor.
4. **Negatives thin (2).** "Every jujutsu sorcerer" + "Who is Sukuna?" (`test_router.py:134`) cover the set + wh-lookup forms but not the "connection" / "who/what is X to Y" boundaries. Over-matching is gate-covered (JJK/OPM gold invariants, gates 2+4), so non-blocking.

**So: sufficient for a commit as a first pass** — the four gates + the R5 re-sweep are the real regression guard and they cover over/under-matching and the union. Items 1–4 are non-blocking SHALLs (item 1 is the one worth landing in-commit; the rest can be follow-ups).

**R-6 floor inheritance — separate gate; no R-5 change; and the pre-registered question is a *floor* question, not a relations-door one.**
- R-6 (`subject_aliases`) is its own fix class + gate. It does **not** need "the same relations-door inheritance" folded into R-5.
- The relations door already resolves the subject through the shared `FactStore.link_entities` path (`context.py:369`), and `link_entities` **JOINs the `aliases` table** (confirmed in `facts.py`) — so when a relationship question is phrased with an alias, the relations door resolves the canonical entity **for free, in both R-6 hook shapes** (alias-table addition: link_entities already consults it; query-time override: the override rewrites the query before routing, then link_entities resolves the canonical name).
- Blind spot 8 (`chairman.md:43`) actually asks whether an **alias-resolved subject inherits the new level-0 card via the floor** — that is an R-2/R-3 floor-leg question, *not* a relations-door question. It is correctly "recorded for R-6 drafting." Nothing in the R-5 commit needs to change.
- Residual to record (non-blocking): the R-6 draft must state explicitly that the relations door inherits alias resolution via `link_entities` (so it's not re-litigated per-wiki) and answer the floor-inheritance question (blind spot 8) on its own.

The fix is sound for this focus: the model-free tests are a sufficient first pass (gates + re-sweep are the real guard), and R-6 is correctly a separate gate with no R-5 change required. The one item I'd land in-commit is the store-free trigger test, because the record currently claims a test that isn't there.

APPROVE

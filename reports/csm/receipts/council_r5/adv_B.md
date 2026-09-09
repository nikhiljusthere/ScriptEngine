# Council R-5 advisor 2/5 (adv_B) — final ruling

Recovered from the framework-persisted oracle transcript (run d8133af7-c04c-41ad-9fae-6799da7f4c20, agent=oracle, ts=1788991292948).
The parent council workflow (429d9efa) was cancelled to enforce one-member-at-a-time council concurrency;
this advisor's work was recovered from disk rather than re-run.

---

Verified — the tightened trigger keeps the relationship interrogatives and releases the prose steals. Here is my advisor ruling.

## Council Advisor 2/5 — ROUTE PLACEMENT (R-5 relations mode)

**The placement is correct.** Rule 2d (`router.py:656-666`) sits exactly where the design requires:
- after the battle/count probes — `has_battles` (2b, L643) and `has_battle_result` (2c, L649) —
- before rule 3 (wh-lookup → `qa`, L677) and rule 4 (`set_shaped` → `roster`, L737).

That ordering correctly owns both R-5 shapes: the set-shaped "Every documented relationship of X" (beats rule 4's roster swallow) and the interrogative "What is the relationship between X and Y?" (beats rule 3's qa passage search, which the relation rows never reach). I confirmed the rule sequence in `route()` and it matches the documented intent.

**Where it is NOT safe: the trigger's 5th alternative amplifies a steal, and rule 2d's early position is what makes it a steal.** `_RELATIONS` (L475-483) alt 5 is `(who|what)\s+(?:is|was|are|were)\s+\S+\s+to\b`. Since 2d fires on any match *before* rules 3/4, every matched query is routed to `relations` (character-relation rows, or an empty bundle) instead of its rightful mode. Alt 5 over-catches the prose/causality form "what is <adj/noun> to X":
- `What is central to the Culling Game?` → **steals from qa**
- `What is key to success?` → **steals from qa**
- `What is essential to his victory?` → **steals from qa**

These are lookups, not character relationships. Alt 5 was meant for "Who is Denji to Makima?" but its `what` branch drags in every "what is X to Y" fact/mechanism question.

**Good news for the gates:** I ran the current (loose) regex against all 8 series question banks (opm 40, csm 40, jjk 63, berserk 38, bleach 48, onepiece 39, db 39, hxh 46) and all 5 eval banks (jjk 31, onepiece 7, db 11, hxh 6, continuity) — **0 matches**. So `eval --series jjk` (31/31) and `canon-run --series opm` will **not** regress. The over-catch is latent (a re-sweep probe or future qa phrasing would hit it), not a current gate failure.

**Minimal fix (one line):** tighten alt 5 from `(?:who|what)\s+(?:is|was|are|were)\s+\S+\s+to\b` to `who\s+(?:is|was)\s+\S+\s+to\b` (drop `what` + `are/were`). Verified: keeps "Who is Denji to Makima?" / "Who was he to the family?", releases all three prose steals, and still leaves "Every documented relationship of X" + "What is the relationship between X and Y?" (alts 1) intact. The R-5 rows are all "Every documented relationship of X" (alt 1), so alt 5 is optional interrogative coverage whose loose form is a net-precision loss. Alts 2/3/4 (`how…related`, `how…relate`, `connection`) are lower-risk (relationship-flavored) and acceptable as-is.

OBJECTION: rule 2d's placement is correct but its trigger (alt 5, `router.py:482`) over-catches "what is X to Y" prose questions and, sitting before rules 3/4, steals them from qa — tighten alt 5 to `who (is|was) X to`.

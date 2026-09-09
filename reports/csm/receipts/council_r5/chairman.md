# Council R-5 — chairman verdict (CSM campaign, 2026-09-10)

Trigger: section-3 "every big engine change" — the R-5 fix class (G-CSM-4, red
list R-5): the fourth router mode `relations`. Fresh-context chairman;
zero-GPU, read-only, no `:8000` API, no eval/canon/embedding; every command
model-free and < 15 s. Advisors A–E + peer reviewers 1–5 read from
`reports/csm/receipts/council_r5/`. All load-bearing code claims below were
re-verified on disk in this run (cited with line numbers); nothing is left
UNVERIFIED.

**Verdict: R-5 = AMEND (5 amendments). Post-amendment gate-1 pin: 1,315
collected (1,305 r2r3 pin + 8 R-5 as-landed + 2 amendment tests, 0 failed).**

## Where the Council Agrees (numbered findings, all (R-5))

1. **Right fix class — all five advisors.** The G-CSM-4 debt is structural:
   relationship phrasings fall into `looks_like_enumeration` → roster, while
   the relations channel (facts.db, 11,261 edges) is served only as a
   qa-bundle side channel — structurally unreachable for enumeration-shaped
   queries (verified: the 11 "documented relationships of X" rows sit at 0/11
   under qa/roster/narrative in `reports/csm/miss_queue_csm_iter1.jsonl`; the
   class plan in `frame.md`). A per-wiki override cannot express a new router
   mode. The diff (5 files, +223/−4 at HEAD 41160cd, verified via `git diff`)
   adds exactly one mode + one budgeted builder + the endpoint/CLI/MCP
   plumbing, no per-wiki override.
2. **Route placement is correct — B, verified on disk.** Rule 2d at
   `scriptengine/retrieve/router.py:656-667` sits after the 2b/2c
   battle/battle-result probes and **before** rule 3 (wh-lookup) and rule 4
   (roster), so it owns every relationship phrasing, enumeration-shaped or
   not ("Every documented relationship of X" would otherwise be swallowed by
   rule 4's set-ask; "What is the relationship between X and Y?" would
   otherwise fall to rule 3's qa search, which the relation rows never reach).
3. **The builder is sound in shape — C, with one unit defect (finding 5).**
   `_relations_context` (`scriptengine/api/context.py:342-447`) unions both
   recording channels — the LLM-extracted `relations` rows (verbatim quote +
   era, the wiki's own words, via `store.relations_of(name, both_ways=True)`)
   and the graph edges (`store.edges_for(ids, min_confidence=0.9, limit=40)`
   — note: the door passes 0.5; `min_confidence` on the store call is 0.9 in
   this builder, facts.py default 0.9 vs the 0.5 `edges_for` signature
   default; residual 3) — ranks via `rank_relations` (the roster door's
   ranking, cite-the-edge-not-the-set per the r2r3 forward note), and pays
   rows in rank order so the tail drops, never the edge the question names.
4. **No store-free trigger test exists — E + rev_1, verified on disk.**
   `tests/test_router.py:19` imports only `_NARRATIVE_VERBS, _WH, Route,
   route` — not `_RELATIONS`. Both R-5 router tests
   (`test_relations_phrasings_reach_relations` L122-129,
   `test_non_relationship_phrasings_do_not_reach_relations` L138-145) and all
   three `TestRelationsBundle` tests (`tests/test_context.py:443/452/463`)
   skip without a csm index. The frame's "8 model-free tests (router trigger +
   synthetic-fixture builder)" is an overstatement: 8 tests are *collected*
   (3+2 parametrized in test_router.py + 3 in test_context.py — I re-ran
   `pytest tests/ --collect-only -q` = **1,313 = 1,305 + 8**, grounding the
   frame's 1,313 pin), but none of them exercises the trigger without a
   store.
5. **The budget unit is wrong — rev_2 (all five advisors missed it), verified
   on disk.** `context.py:381` `budget_chars = int(token_budget *
   CHARS_PER_TOKEN)` is a *chars* budget, but `cost` is in *tokens*
   (`estimate_tokens = int(len/3.6)+1` at `context.py:63-64`; `cost =
   estimate_tokens(line) + 5` at L421) and the guard at L423 compares
   `used + cost > budget_chars` ⇒ the effective cap is up to **3.6× the
   requested token budget**. Every other mode charges tokens against
   `token_budget` (verified: L209, L280, L299, L660). The existing
   tail-drop test (tiny budget 120 vs 4000) passes either way — it proves a
   cut happens, not the unit.
6. **There is no relations empty-fallback — D, verified on disk (and D's
   caller count is off by one).** `scriptengine/api/main.py:228-235` falls
   back roster→narrative for empty rosters only; `scriptengine/cli.py:1699-1702`
   (`_show_bundle`) the same; `scriptengine/script/writer.py:494-497` the
   same, auto-gated. `scriptengine/mcp/server.py` is a thin `/context` HTTP
   proxy (httpx client — verified: no local build) and inherits whatever
   main.py does. So **3 local call sites**, not D's "4". Consequence: an
   auto-routed relationship question whose pair has no relation rows returns
   an **empty bundle** — the OPM "relationship to" pair rows (359-row table,
   many pairs absent) are qa-pinned in the campaign batches, so a miss there
   is a new JJK/OPM-invariant miss ⇒ halt (frame gate 5). This is the rev_3
   "5/5 missed" item.
7. **The trigger over-matches — rev_1/rev_4, verified against the banks in
   this run.** Alt-4 `\bconnection\b` matches 20+ qa-pinned batch lines
   ("What is the sword Mai left Maki her last connection to?", "What is
   Flashy Flash's connection to the Ninja Village?") — zero official-bank
   hits, zero frozen R-5 rows. Bare `\brelationship\b` steals the
   "relationship status" prose rows (the ep-30/51 qa pins). Alt-5 who/what-to
   steals "Who is left to stand against Mahito, per Chapter 131?" — B's
   proposed fix `who (is|was) \S+ to` **still matches it** (I re-ran the
   regex: "left" satisfies `\S+`), plus the "Who was revealed to be…" passive
   class. The frozen R-5 queue (csm-rel-02/05/08/09 + red-R-5) is 5 rows,
   **all** "Every documented relationship of X" — alt-1 only; 0
   connection/who-to/related rows. So tightening costs nothing in scope.

## Where the Council Clashes

1. **SHIP (A, C) vs AMEND (B, D, E)** — the split is over whether the three
   defects in findings 5/6/7 block. **Resolution: AMEND.** All three are
   small, independent, verified, and each is load-bearing for a gate:
   finding 5 silently breaks the token-budget contract on the new path (the
   one contract every other mode honors); finding 6 converts qa-pinned
   OPM/JJK pair rows into guaranteed new misses on the invariant re-sweep —
   a halt by frame gate 5; finding 7 ships a trigger that routes ~20
   mechanism/prose questions to the relations door and back to nothing.
2. **D's call-site inventory (4) vs verified (3)** — D counted
   mcp/server.py as a call site; it is a thin proxy that inherits main.py's
   fallback. **Resolution: amendments A3/A4 cover the 3 real sites; the MCP
   door is amended transitively.**
3. **D's facts.py line cites (edges_for @ 815) vs disk (link_entities @
   815)** — verified: `link_entities` is at `scriptengine/stores/facts.py:815`
   (with the `JOIN aliases a ON a.node_id = n.id` at ~876-878), `edges_for`
   at 935, `relations_of` at 1393. Records-only correction (residual 4).

## Blind Spots the Council Caught

1. **The budget unit (rev_2)** — the only defect none of the five advisors
   found; the tail-drop test's design (big 4000 vs tiny 120) masks a unit
   error because both regimes cut. Pinned by A5(b).
2. **B's proposed alt-5 fix is itself a steal (rev_1, live counterexample)** —
   `who (is|was) \S+ to` still matches "Who is left to stand against Mahito"
   (verified in this run); the who/what-to idiom is released entirely in A1
   (qa prose answers it; 0 frozen rows, 0 canned tests use it).
3. **The empty-case halt (rev_3, endorsed by the frame)** — the
   no-fallback-for-relations defect is the one that would fail gate 5 on the
   invariant re-sweep; A3/A4 close it.
4. **Rev_4's alt-1 steal** — `\brelationship\b` captures the
   "relationship status" rows; A1's `relationship (of|with|to|between)` form
   releases them.

## The Verdict - R-5

**AMEND.** The fix class is right (finding 1), the placement is right
(finding 2), the builder's shape is right (finding 3). Three independent,
verified defects block SHIP as-landed: the budget unit (finding 5), the
missing empty-fallback (finding 6), the over-broad trigger (finding 7). Five
amendments, all zero-series-name and model-free-testable:

1. **`scriptengine/retrieve/router.py` (L475-482) — replace `_RELATIONS`:**
   ```python
   _RELATIONS = re.compile(
       r"\bdocumented\s+relationship(?:s)?\b"
       r"|\brelationship(?:s)?\s+(?:of|with|to|between)\b"
       r"|\bhow\s+(?:is|are)\s+[^?]*\brelated\b"
       r"|\bhow\s+does\s+\w+\s+relate\b",
       re.IGNORECASE,
   )
   ```
   (Drops alt-4 `\bconnection\b`, the bare `\brelationship\b` →
   preposition-required, and the who/what-is-X-to branch.) **Why (all
   verified in this run):** `\bconnection\b` matches 20+ qa-pinned prose rows
   and has 0 official-bank hits; bare "relationship" steals the "relationship
   status" rows; the who/what-to branch steals "Who is left to stand against
   Mahito" / "Who was revealed to be…" (lowercase common words satisfy
   `\S+` — B's proposed fix included, counterexample re-run). Kept: all 4
   frozen csm-rel rows + all 11 `_csm_relations.json` probe rows (re-matched
   the new regex against the queue and probe file: 4/4 + 11/11), the 3 canned
   test phrasings (documented ✓ / relationship between ✓ / how is … related
   ✓), and the 2 negative controls ("Every jujutsu sorcerer", "Who is
   Sukuna?" — still non-matching). **Invariance:** the tightened regex has
   **0 hits in all 8 official banks + all eval banks** (I ran the simulation)
   ⇒ gates 2 and 4 are structurally invariant. The 34 unique qa/roster batch
   rows still matching (the "relationship to/of/with/between X" pair
   questions + "How is X related to Y?") are the campaign's re-pin class
   (residual 4), protected by amendments 3/4. Zero series names; testable
   model-free via amendment 5(a).
2. **`scriptengine/api/context.py` (L381 + L423, `_relations_context`) —
   fix the budget unit:** delete `budget_chars = int(token_budget *
   CHARS_PER_TOKEN)`; change the guard `if included and used + cost >
   budget_chars:` to `if included and used + cost > token_budget:`. **Why:**
   `cost` is in tokens (`estimate_tokens` = int(len/3.6)+1, L63-64) but was
   charged against a chars budget ⇒ up to 3.6× the requested token budget,
   while every other mode charges tokens against `token_budget` (L209/280/299/660).
   Zero series names; testable model-free via amendment 5(b).
3. **`scriptengine/api/main.py` (after the roster block, ~L235) — relations
   → qa empty fallback, auto-only:**
   ```python
   # A relations bundle with no rows is not an answer (a pair the wiki never
   # recorded): fall back to the qa passage search, whose side channel still
   # unions the relation rows when they exist. Auto-only, like the roster
   # fallback above, so an explicit mode=relations surfaces the empty case.
   if mode == "relations" and not bundle.get("relations") and request.mode == "auto":
       bundle = build_context(
           paths,
           request.query,
           mode="qa",
           token_budget=request.token_budget,
           top_k=request.top_k,
           subject=subject,
       )
   ```
   **Why:** a pair with no relation rows
   (OPM "relationship to" pairs outside the 359-row table) would otherwise
   return an empty bundle ⇒ guaranteed new miss on the JJK/OPM invariant
   re-sweep ⇒ halt (frame gate 5). Uses the routed `subject` local (L215),
   not `request.subject`, so the fallback keeps the router's read. Zero
   series names.
4. **`scriptengine/cli.py` `_show_bundle` (~L1699) + `scriptengine/script/
   writer.py` (~L494) — the same fallback at the other two local call sites.**
   cli.py, after the roster fallback block (unconditional style, matching the
   local roster block):
   ```python
   if mode == "relations" and not bundle.get("relations"):
       console.print("[yellow]No documented relationships; falling back to qa.[/yellow]")
       bundle = build_context(
           paths, question, mode="qa", token_budget=24000, top_k=top_k or None
       )
   ```
   writer.py, after the roster block (auto-gated, matching the local roster
   block):
   ```python
   if mode == "relations" and not bundle.get("relations") and asked == "auto":
       bundle = build_context(
           paths, subject, mode="qa", token_budget=budget, top_k=TOP_K
       )
   ```
   **`scriptengine/mcp/server.py` gets no change** — it is a thin `/context`
   proxy (verified) and inherits amendment 3. (This corrects D's "4 call
   sites": there are 3.) Zero series names.
5. **`tests/test_router.py` + `tests/test_context.py` — the two model-free
   tests the frame claimed but the diff lacks.**
   (a) `tests/test_router.py`: add `_RELATIONS` to the L19 import and one
   store-free test (no store, no cms index needed; place in the
   store-free `TestSignals` class or a new `TestRelationsTrigger` class):
   ```python
   def test_relations_trigger_boundaries(self):
       from scriptengine.retrieve.router import _RELATIONS
       for q in ("Every documented relationship of Denji",
                 "What is the relationship between Denji and Makima?",
                 "How is Meowy related to Denji?",
                 "What is Makima's relationship with Denji?"):
           assert _RELATIONS.search(q), q
       for q in ("What is the sword Mai left Maki her last connection to?",
                 "Who is left to stand against Mahito, per Chapter 131?",
                 "Who was revealed to be a shapeshifting monster?",
                 "What is enough to leave King winded?",
                 "What does Megumi confirm about Yuji's relationship status in Episode 30?",
                 "Every jujutsu sorcerer", "Who is Sukuna?"):
           assert not _RELATIONS.search(q), q
   ```
   (fails on the as-landed trigger: "last connection to" / "Who is left to"
   / "relationship status" all match the current regex.)
   (b) `tests/test_context.py`, `TestRelationsBundle` (~L463, after
   `test_relations_bundle_renders`):
   ```python
   def test_relations_budget_units(self):
       tiny = self._bundle("Every documented relationship of Denji",
                           token_budget=200)
       assert tiny["tokens_used"] <= 200
   ```
   (fails on the as-landed builder: `tokens_used` can reach ~3.6× 200.)
   Character names in test fixtures are permitted (the existing canned tests
   already name Denji/Makima/Meowy); the zero-series-name rule governs
   engine logic, per the r2r3 clash-5 resolution.

**Non-blocking record items (ship in the same commit, no engine logic):**
(a) `frame.md` / class-plan wording "8 model-free tests (router trigger +
synthetic-fixture builder)" → "8 collected tests (3+2 parametrized router
trigger + 3 builder; none store-free pre-amendment; the store-free trigger
test is amendment A5(a))" — the overstatement of finding 4. (b) The
`validate_relations.py` receipt should cite `link_entities` (facts.py:815,
aliases join ~876-878), `edges_for` (935), `relations_of` (1393) — D's
line cites were off (clash 3).

**Post-amendment gate-1 pin: 1,315** = 1,305 (r2r3 pin) + 8 (R-5 as-landed,
verified by my collect-only run = 1,313) + 2 (A5(a), A5(b)).

## Documented Residuals (not fixed, with owner) and Standing Rules

**Residuals (documented, deliberately not amended):**
1. **`dedup_key` includes `quote`** (`context.py` ~L397: `seen =
   {(source, relation, target, quote)}`) — the same relation fact recorded in
   two different rows renders twice (rev_5). Accepted: each row is the wiki's
   own words; no user-visible bug. Owner: a future dedup pass.
2. **`truncated` can be false when `top_k` truncation fires** (rev_5) —
   cosmetic; the field reports budget-cut, not count-cut. Documented, not
   fixed.
3. **`edges_for` min_confidence** — the builder's call passes `min_confidence=0.9`
   while the `edges_for` signature default is 0.9 vs the door's 0.5
   (rev_3): the union intentionally includes weaker extracted edges (the qa
   side channel unions the same way). Not changed.
4. **The 34-row re-pin class.** The tightened trigger still matches 34 unique
   qa/roster batch rows — all genuine pair questions ("What is X's
   relationship to Y?", "What is the relationship between X and Y?", "How is
   X related to Y?"; e.g. "the real-life relationship between Mimiko's and
   Nanako's voice actresses", which the relations table will not contain and
   which amendments 3/4's fallback keeps on the qa prose answer). These are
   rev_2's re-pin list: the re-sweep re-pins them to `relations`; a miss on
   any stamped row = regression = halt (frame gate 5).
5. **The who/what-to idiom stays on qa prose** after A1 ("What is Tsumiki to
   Megumi?" — 0 frozen R-5 rows, 0 canned tests). If the campaign later wants
   the idiom at the relations door, add a case-sensitive proper-noun branch
   (`[A-Z]\S*` between the verb and "to"; lowercase queries would be missed).
   Forward note, not an amendment.
6. **facts.py line-number correction** for all records: `link_entities` @
   815 (aliases join ~876-878), `edges_for` @ 935, `relations_of` @ 1393.

**Standing rules (added by this council):**
1. **Any router-trigger change ships with a model-free recall diff** — old vs
   new regex simulated over `questions/*.json` + `questions/_*.json` + the
   frozen queue, with 0 official-bank hits as the gate-invariance precondition
   (the check that produced findings 7/A1 here; ~1 s, no model).
2. **A new router mode = four gates + the class's own re-sweep + the JJK/OPM
   invariant re-sweep** (frame gate 5), per the r2r3 declaration-contingent
   rule — a new mode is a declaration on every series.
3. **Bundle builders charge budget in tokens** (the unit every other mode
   uses); a "drops the tail" test is not a unit check — a unit pin
   (`tokens_used <= token_budget`) must exist per builder (A5(b) is the
   pattern).

## R-6 Forward Note (pre-registered, carried from council_r2r3 finding 8)

**Question:** does the relations door change anything about whether
alias-resolved subjects inherit the level-0 card via the floor?

**Answer: no — R-5 changes nothing about that question.** Verified on disk:
- The relations door resolves its subject through `FactStore.link_entities`
  (`scriptengine/stores/facts.py:815`), which **JOINs the `aliases` table**
  (`JOIN aliases a ON a.node_id = n.id`, ~876-878). An alias-resolved subject
  therefore inherits relation-row lookup **for free under both R-6 hook
  shapes**: (a) the aliases-table hook — `link_entities` already consults the
  table, so R-5 adds nothing to cover; (b) the query-time-override hook — the
  rewrite happens before routing and resolution, so the relations door sees
  the canonical name.
- The relations door has **no floor leg**: its answer is the relation rows
  themselves (`context.py` L389-429 — no `passages_for_subject` call, no
  level-0 card, no floor fill). The blind-spot-8 question is about the **qa
  subject floor** (R-2's level-0 lead card in `passages_for_subject`,
  facts.py ~1983/2026) — whether an alias-resolved subject inherits *that*
  card via the floor. R-5 does not touch that path.
- **For the R-6 draft:** answer the floor-inheritance question on the
  qa-floor path (does `passages_for_subject`'s subject resolution route
  through the aliases join / the override hook?), and record as a one-liner
  that the relations door needs no R-6 hook of its own — it inherits alias
  resolution through `link_entities`'s aliases join (facts.py:815, ~876-878).

## Gate Expectations (the amended package, per frame.md)

1. `pytest tests/ -q` — **1,315 collected** (1,305 + 8 + 2), 0 failed.
   (Ruling 5e: a known +N test delta does not itself re-run the gates; the
   full re-run happens at closure.)
2. `eval --series jjk` — **31/31** (invariant; structurally: the amended
   trigger has 0 hits in the jjk official + eval banks, verified in this run).
3. `span-recall --series jjk` — **48,572/48,572 offline (rc=0)** (invariant;
   R-5 touches no chunking) + live 400-probe **≥390/400 (97.5%)**.
4. `canon-run --series opm` — **≥10/16 exact, 236/236 canon, ≥79.0%**
   (invariant; 0 hits in the opm official bank; amendments 3/4 keep the
   qa-pinned "relationship to" pair rows on the qa answer when no relation
   row exists).
5. **R5 meter** — **≥1 HIT on the class's own new rows**
   (`validate_relations.py`: the 4 frozen csm-rel rows + the 11-row
   `_csm_relations.json` probe, all matching the amended trigger, verified);
   **JJK/OPM frozen-queue invariants — no new miss (a regression = halt)**;
   the 34-row re-pin class (residual 4) is re-pinned to `relations` in the
   re-sweep and is fallback-protected.

## The One Thing to Do First

Land amendments 1–5 in one bounded model-free batch (5 files: router.py,
context.py, main.py, cli.py + writer.py, the two test files; no GPU, no
`:8000`, no model), then verify before any gate:
`pytest tests/test_router.py tests/test_context.py -q` (both new tests pass;
the trigger test passes **store-free** — that is the point of A5(a));
`pytest tests/ --collect-only -q` = **1,315**; and re-run the model-free
recall diff (standing rule 1) over the banks + queue to re-confirm 0
official-bank hits. Only then start the four-gate sequence with the R5 meter
+ re-sweeps per the gate expectations above. Any invariant regression halts
to the council.

## Addendum — the Costed Governance Question (chairman-only, per frame addendum)

*Answered after the advisor/reviewer rulings; scoped by the directing session
to touch nothing about R-5's technical merits.*

**Is the standing 11-member form (5 advisors → 5 peers → chairman)
proportionate for each remaining fix class (R-1…R-7)?** Measured cost of
this council's reviewer wave: 99 model calls, 1.42M actually-re-prefilled
tokens (72% cache-hit, 12.7:1 re-prefill:completion after the
one-member-at-a-time fix). Two evidence classes matter:

- **The peer round earned its cost this council** — rev_1's three findings
  (falsifying B's proposed fix with a live counterexample; catching the
  who-branch class all five advisors missed; verifying A's over-match claim
  at router.py:481 against the `_`-batches) all came *from* the
  disk-verification turns. Cutting those turns, or pre-seeding members with
  seeder-chosen evidence only, would likely have suppressed them. The peer
  round's value is independent disk verification, not headcount.
- **The advisor round had measurable redundancy** — 4/5 advisors missed the
  same who-branch class, and one (B) proposed a fix a reviewer immediately
  falsified. The duplicate lanes are where the redundancy lives.

**Pre-registered rule (record in `plan/flow.md` + the CSM_WAVE2_RESUME §3
council node before R-6 opens; the first class sorted under it is a pilot and
the chairman records the measured delta):**

1. **The sort test — decided at class OPEN, from the class plan + diff scope,
   never after:** the class is **slim** iff all three hold: (i) the fix
   touches **≤2 engine files** and adds **no new router mode, bundle key,
   fallback path, or store schema** (no new data path); (ii) its blast radius
   is its own rows only (standard four gates; no cross-class invariant
   re-sweep beyond the usual one); (iii) the fix shape is a **known pattern**
   (trigger tightening, one-line guard, test/record addition). Any NO ⇒ the
   **full 11-member form** (structural: a new mode as in R-5, the R-6
   aliases/floor hook, any extraction leg, any cross-class blast radius).
2. **The slim form = 4 members:** 3 advisors with *named non-duplicate*
   lanes (behavior/trigger, plumbing/fallback, tests+gates — the two
   redundant duplicate lanes dropped; expected loss: a second independent
   falsifier of a proposed fix, i.e. this council's rev_1 counterexample —
   mitigated by making **≥1 verified-on-disk claim per advisor mandatory**
   in the slim form, chairman-re-verified as in this run) + 1 peer reviewer
   (the disk-verification role that produced this council's best finding) +
   chairman. Cost ≈ 4/11 members (~37% of the re-prefill).
3. **Turn budget: soft, not hard.** A hard per-member cap would suppress
   exactly the disk-verification behaviour that produced rev_1's finding.
   Instead: a **soft checkpoint at 20 turns** — at 20 turns a member must
   have its verdict down with every load-bearing claim disk-cited; it
   continues only with a *named* unverified claim. The frame's standing rule
   ("a claim that cannot be verified did not happen") is what enforces the
   shape: uncited claims are not recorded, so tail turns stop paying.
4. **R-5 was correctly a full-form class** (new mode + builder + endpoint =
   structural); of the remaining classes, **R-6 (aliases hook + floor) is
   full-form by the test** (no. (i) fails: new subject-resolution path), and
   a pure trigger tightening or record fix would sort slim.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Read-only chairman run: zero codebase edits (no git add/commit; the only file written is this council record at the runtime-authoritative path). No :8000 API, no eval/canon/embedding, no model job; every command model-free and <15 s. Scope: the R-5 verdict + the pre-registered R-6 forward note + the chairman-only governance addendum; no product decisions invented — every AMEND item is a defect an advisor or reviewer found and I re-verified on disk."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Every load-bearing claim re-verified on disk in this run with cited paths: router.py:475-482 _RELATIONS (5 alts as landed) + rule 2d at 656-667 (after 2b/2c, before rules 3/4); context.py:342-447 _relations_context (budget_chars at 381, cost at 421, guard at 423, estimate_tokens at 63-64; token-charged modes at 209/280/299/660); main.py:228-235 roster-only fallback + subject local at 215; cli.py:1699-1702; writer.py:494-497; mcp/server.py thin httpx proxy; facts.py link_entities @815 (aliases join ~876-878), edges_for @935, relations_of @1393; test_router.py:19 imports (no _RELATIONS) + L122-145 canned tests; test_context.py:443/452/463. Bank simulation (this run): tightened trigger = 0 hits in all 8 official + eval banks; 4/4 frozen csm-rel queue rows + 11/11 _csm_relations.json probe rows match; 34 unique qa/roster batch rows still match (re-pin class); B's proposed alt-5 fix re-tested and still stealing 'Who is left to stand against Mahito'. pytest tests/ --collect-only -q = 1313 (= 1305 + 8 as-landed), grounding the 1315 post-amendment pin."
    }
  ],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git diff -U0 (test_router.py, test_context.py) + package_diff.md read",
      "result": "passed",
      "summary": "as-landed R-5 diff = 5 files, +223/-4; 5 test functions -> 8 collected (3+2 parametrized router, 3 context)"
    },
    {
      "command": "python regex simulation: old vs tightened _RELATIONS over questions/*.json, questions/_*.json, eval banks, frozen queue",
      "result": "passed",
      "summary": "tightened trigger: 0 official-bank hits; 4/4 frozen rows + 11/11 probe rows match; 20+ connection steals released; 34 re-pin-class rows remain; 'Who is left to' counterexample reproduced for B's proposed fix"
    },
    {
      "command": "scriptengine/.venv/bin/python -m pytest tests/ --collect-only -q",
      "result": "passed",
      "summary": "1313 tests collected in 0.93 s (= 1305 r2r3 pin + 8 R-5 as-landed); post-amendment pin 1315 stated in the verdict"
    }
  ],
  "validationOutput": [
    "collect-only: 1313 tests collected in 0.93s",
    "tightened _RELATIONS: 0 hits in 8 official banks + eval banks; 4/4 frozen + 11/11 probe rows match",
    "budget bug confirmed at context.py:381/421/423 (tokens vs chars, 3.6x cap)"
  ],
  "residualRisks": [
    "34-row re-pin class: qa/roster-pinned pair rows now route to relations; protected by the A3/A4 empty->qa fallback, but the re-sweep must re-pin them and a miss on any stamped row halts (frame gate 5)",
    "dedup_key includes quote (same fact from two rows renders twice) and truncated is false under top_k truncation - documented residuals, no fix in scope",
    "who/what-to idiom stays on qa prose after A1 (0 frozen rows, 0 canned tests); forward note only, per residual 5",
    "R-6: relations door needs no aliases hook (inherits via link_entities' aliases join, facts.py:815); the floor-inheritance question remains on the qa-floor path"
  ],
  "noStagedFiles": true,
  "diffSummary": "No codebase edits (read-only chairman). Verdict AMENDs R-5 with 5 amendments (tightened _RELATIONS; token-unit budget fix; relations->qa empty fallback at main.py + cli.py + writer.py; 2 model-free tests) + 2 record items; post-amendment gate-1 pin 1,315; gate expectations 1-5 per frame; R-6 forward note answered; chairman-only governance addendum answered with a pre-registered slim-vs-full sort rule.",
  "reviewFindings": [
    "blocker: context.py:381/423 budget unit (tokens charged against a chars budget, 3.6x cap) - all 5 advisors missed, rev_2 found; A2 + A5(b) pin",
    "blocker: no relations empty-fallback at any of the 3 local call sites (main/cli/writer) - qa-pinned OPM pair rows become guaranteed invariant misses; A3/A4 close it",
    "blocker: _RELATIONS over-match - 'connection' (20+ qa rows) + bare 'relationship' ('relationship status') + who/what-to ('Who is left to...'); A1 tightens, 0 official-bank hits, all in-scope rows kept",
    "note: the frame's '8 model-free tests' is 8 collected, 0 store-free; A5(a) adds the store-free trigger test",
    "note: D's facts.py line cites off (link_entities @815 not edges_for; edges_for @935; relations_of @1393) + '4 call sites' = 3 (MCP is a proxy)"
  ],
  "manualNotes": "Verdict: R-5 AMEND (5 amendments), post-amendment gate-1 pin 1,315 (independently re-run collect-only in this session, not taken from the advisors' records). Governance addendum answered: slim 4-member form for classes passing the 3-part sort test at class open (full 11-member for structural); soft 20-turn checkpoint instead of a hard cap, so disk-verification behaviour is preserved."
}
```
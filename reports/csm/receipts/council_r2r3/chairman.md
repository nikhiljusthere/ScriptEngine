# Council R-2 + R-3 — chairman verdict (CSM campaign, 2026-09-09)

Trigger: section-3 "every big engine change" — combined council for DRAFT R-2 (qa-passage leg, G-CSM-2) and DRAFT R-3 (roster scoping, G-CSM-3). Fresh-context chairman; zero-GPU, read-only; every shell < 15 s. Advisors A–E + peer reviewers 1–5 read from `reports/csm/receipts/council_r2r3/`. All load-bearing claims below were re-verified on disk in this run (cited); nothing is marked UNVERIFIED.

**Verdicts: R-2 = AMEND (3 amendments). R-3 = AMEND (4 code/test amendments + a 5-item records package). Post-amendment gate-1 pin: 1,305 collected (1,303 passed + 2 xpassed, 0 failed).**

## Where the Council Agrees

**R-2 (four of five SHIP; the agreement below is what the SHIP side rests on):**
1. **Right fix class — all five advisors (A, B, C, D, E).** The G-CSM-2 debt is a retrieval-path property, not a wiki shape: the rerank veto on verbatim-covering passages plus the subject floor missing the level-0 lead card. A per-wiki override cannot express a rerank veto. On-disk: `reports/csm/red_list_csm.md:28` (the R-2 entry names the qa bundle leg); the d5 sweep evidence in the hybrid.py WHY comment (target chunk was lexical-rank-0/1, RRF-rank-0/2, survived dedup — the rerank was the only step that lost it); the 13 retrieval-side d5 rows verified not chunking-side in `reports/csm/override_fixes_iter1.md` §1.
2. **Tail-fill semantics for L < top_k — A, C, D, E (and the peer reviewers).** The splice `deduplicated = deduplicated[:top_k-len(recovered)] + recovered` frees exactly `len(recovered)` trailing slots; the rerank top is untouched; the `<3 content words` guard (`hybrid.py`, `_query_covered`) keeps writer-style questions on the pre-fix path.
3. **The level-0 floor change is single-consumer and consumer-safe — B, D, E (+R2).** `passages_for_subject` has exactly one production caller, `scriptengine/api/context.py:409` (verified by grep: only context.py:409 + tests/test_stores.py:83-101 + tests/test_csm_fixtures.py:102/124); the card is a compact lead card, section-capped by `_cap_sections`; the 400-probe gate covers the JJK-side delta.
4. **The two legs are not redundant — A (endorsed by the peer round).** Re-admission rescues in-shortlist drops (the 13 d5 rows, all proven in-shortlist); the level-0 floor rescues not-in-shortlist (csm-fact-06, 0 passages pre-fix — queue row `reports/csm/miss_queue_csm_iter1.jsonl`, open).

**R-3 (four of five AMEND; the agreement below is what every verdict rests on):**
1. **The no-op-when-undeclared claim holds on disk — all five.** Only `series/csm/overrides.yaml` declares the three new fields (verified by grep over all 8 series overrides: csm = umbrella 1 / row_sections 1 / closed_members 1; berserk, bleach, db, hxh, jjk, onepiece, opm = 0/0/0); **all 8 series declare `ability_sections:`** (verified per series), which is exactly why a blanket restriction was rejected (it would drop JJK's Divine-Dogs/Nue/Related-Techniques subpage rows). The JJK invariance pins (`TestScopingLeavesJjkUnchanged`: Gojo 23 / Sukuna 21 / cursed techniques 38 / Gojo forms 14) passed in my model-free run (40 passed + 2 xpassed, 3.71 s).
2. **The residuals are bank-level curation, not a fourth knob — all five, unanimously.** The kept-vs-dropped split sits *inside one group, per character*: the `Enhanced X` family is kept in csm-char-04's gold (Makima: Enhanced Smell) and csm-char-03's own gold (Aki: Enhanced Durability/Speed) but dropped for Power (set-02); contract rows are kept for Aki, dropped for Denji (csm-char-01). A fourth engine knob would encode bank gold, which the engine must not do (`reports/csm/receipts/iter1_r3_roster_scoping_run.md` "Residuals").
3. **No G4 relations-door interaction — A, B, D (+R5).** `closed_members` is read only in `RosterDefinition.parse`, `build_roster`'s declared branch, and `Roster.warning` (verified on the diff); `rank_relations` never touches it (the only `rank_relations` change in the diff is the no-op EOL hunk, below).

**Shared:**
1. **The baseline arithmetic 1,303 = 1,283 (R-1) + 7 (R-2: 6 in tests/test_retrieve.py + 1 in tests/test_csm_fixtures.py) + 13 (R-3: tests/test_csm_roster_scoping.py)** — C and D; re-verified by my own `pytest tests/ --collect-only -q` = **1,303 tests collected (0.95 s)** and the R-1 gate record (`reports/master-work/work_log.md` GATES lines 75-76: 1,283 = 1,281 passed + 2 xpassed; commits b84445f / aef6707 verified in git log).
2. **ONE shared four-gate re-run; both drafts land in the same commit only if both verdicts clear** (D's sequence, endorsed by R4 as the only executable one).

## Where the Council Clashes

1. **R-2: SHIP (A, C, D, E) vs AMEND (B) — the uncapped-`recovered` defect.** B found the only live ranking defect: `recovered` is drawn from `deduplicated[top_k:]` with no cap. With L = len(recovered) ≥ top_k (top_k = 8, `scriptengine/config.py:101`; shortlist = `max(4·top_k, 24)` = 32, so 24 tail candidates — both verified in `hybrid.py`), the splice `deduplicated[:top_k - L]` (hybrid.py:365) becomes a **negative slice**: L > top_k → the internal list grows past top_k and *every* recovered passage lands in `result.dropped` — the fix silently no-ops, the pre-fix failure, exactly in the highest-coverage regime; L == top_k → the whole bundle is replaced by the re-admitted tail, evicting the rerank #1 — the crowding failure the council question explicitly asked about, with no negative slice needed (R1). I verified both regimes by code-reading the working-tree splice. The draft's own claims ("beam-bounded, no top_k growth", "re-admit at the tail", in the WHY comment and in `reports/csm/receipts/iter1_r2_passageleg.md` "the re-admission guard is beam-bounded") are false in that regime. A endorsed "no new failure mode" without simulating it (R1/R3: A is the biggest blind spot); E's "pure option" framing accepted the claim (R2/R5: E's blind spot). **Resolution: AMEND — the defect is real, the fix is one line + one test, and shipping a known-false claim is what the council exists to block.**
2. **The exact cap mechanism: B's proposal vs the peer round.** B proposed `recovered = sorted(recovered, key=lambda p: p.rrf_score, reverse=True)[:top_k]`. R1 caught two holes: (a) a `[:top_k]` cap still permits the L == top_k full swap — the cap must be `top_k - 1` so at least one rerank slot always survives; (b) the rrf re-sort is unneeded and actively wrong — `recovered` is a subsequence of `deduplicated`, which after rerank is in rerank-score order, while `Passage.rrf_score` is the *pre-rerank* fused score set at construction (`hybrid.py:333`); re-sorting by it would demote the rerank's verdict to lexical rank. **Resolution: order-preserving cap at `top_k - 1`, no re-sort.**
3. **R-3: SHIP (E) vs AMEND (A, B, C, D) — four different amendment sets.** A: the EOL no-op hunk only. B: the `Roster.warning` misreport + one policy test (B missed the EOL hunk — R2). C: the red-list ID reconciliation. D: the EOL hunk + the csmdoor-01 sweep omission. Every one of the four named defects is real and on-disk (all verified below); no single advisor had the full set, and R4 noted B's added tests would break the pinned 1,303 expectation. **Resolution: consolidated AMEND — all defects are small, independent, and verified; they compose.**
4. **Process: B's "land amendments, re-run" vs the 1,303 gate pin (R4).** The amendments add 2 tests, so the gate-1 pin moves to 1,305 (or 1,291 / 1,297 on a split commit) — "nobody computed it". **Resolution: the pin is recomputed per verdict and stated explicitly in the gate sequence below.**
5. **"Zero series names in .py" — E vs A/D (wording, not logic).** My grep of the added lines: 11 `csm`/G-CSM-3 tokens, all in WHY comments (e.g. "G-CSM-3 (csm-set-17 vs csm-set-08, `Tokyo Special Division 4`)"), plus character names ("Denji", "Aki Hayakawa") in docstrings/comments; **zero in logic** — no branch, string match, or default keyed on a series slug; the only series-specific data is in `series/csm/overrides.yaml`. **Resolution: the project rule governs per-wiki handling *logic*; bug-instance WHY comments are house convention ("comments explain which bug"). The drafts' record wording ("No series name in .py") is corrected to "zero series names in .py logic" — a records-package item, not a code change.**

## Blind Spots the Council Caught

(Items that emerged only in the peer-review round; all re-verified on disk where code-bearing.)

1. **The L == top_k swap (R1)** — worst case of the degenerate regime, reachable without any negative slice: `deduplicated[:0] + recovered` serves 8 re-admitted tail passages and evicts the entire rerank top. Covered by the `top_k - 1` cap in the R-2 amendment.
2. **Tail-fill × subject-floor budget interaction (R1)** — `context.py:546-548` walks `[*result.passages, *floor_fill]`: re-admitted (longer) passages spend budget before the floor and can evict the level-0 card the same draft adds to the floor. Passage *count* is invariant (top_k either way), so this is a composition delta, gate-sampled by the 400-probe — documented residual, not a code fix.
3. **Zero gate headroom (R2)** — the probe floor is exactly the 390/400 baseline (work_log:76); a composition delta that keeps every line reachable passes all four gates green, so the JJK-100% invariant for unsampled subject questions is not gate-covered. Documented residual (the pinned-panel mechanism exists for a pre/post JJK subject-bundle diff if the probe wobbles).
4. **CJK inertness of the re-admission leg (R3)** — `_query_covered` tokenizes `[a-z0-9]+`, so pure-CJK queries score zero coverage and the re-admission leg is inert for them; E's "all 8 wikis inherit the fix for free" holds only for the floor leg + Latin-script queries. Recorded, not fixed (the four gates cover JJK/OPM Latin behavior).
5. **R-2 × R-1 blast radius (R5)** — the G7 roster-count branch (`context.py:288-299`, verified: `retriever.search(query, top_k=8, rerank=True)`) runs R-2's re-admission, so R-1's closed rows csm-set-14/15 sit inside R-2's blast radius; both receipts' sweep lists omit them → added to the R-2 re-sweep (invariant expected; regression = new miss = halt).
6. **R-3 × R-5 deferral carried forward (R5)** — when the relations mode (red-R-5, CSM-7) lands, its scoping must be decided against `closed_members` (the red-list addendum defers exactly this to R-5 drafting). Forward note recorded on red-R-5.
7. **Declaration-contingent no-op is unenforced (R2)** — a yaml-only declaration of any of the three fields on a *gated* wiki is not an engine change, so nothing forces a gate re-run. Standing rule added: **declaring any of the three fields on a gated wiki = four gates + class re-sweep.**
8. **R-6 floor-inheritance question (R5)** — the `subject_aliases` hook design (aliases-table vs query-time override) must answer whether alias-resolved subjects inherit the new level-0 card via the floor. Recorded for R-6 drafting.

## The Verdict - R-2

**AMEND.** The draft's core is right — all five advisors agree on the fix class (bundle-leg retrieval debt, generic engine fix, the two legs non-redundant), and the L < top_k behavior is exactly the draft's stated semantics. But the uncapped-`recovered` defect (clash 1) makes the draft's "beam-bounded, tail-fill" claims false in the L ≥ top_k regime, and the `facts.py` docstring reference the diff introduces is dangling (verified: the new inline comment at `scriptengine/stores/facts.py:2026-2027` says "see the docstring above for why the card is part of the floor", while the docstring at `facts.py:1983` still reads "Every level-2 passage"). Three amendments, all zero-series-name and model-free-testable:

1. **`scriptengine/retrieve/hybrid.py`** — the splice hunk (working tree ~lines 358-366, the `if recovered:` block after the `recovered = [...]` comprehension):
   ```python
   if recovered:
       # Cap so the splice is always a tail fill: with more than top_k-1
       # query-covering passages in the tail, the uncapped splice goes
       # negative (L > top_k: re-admission silently no-ops, the internal
       # list grows past top_k) or, at L == top_k, replaces the rerank top
       # entirely. Order-preserving: recovered keeps rerank order as a
       # subsequence of `deduplicated` -- no re-sort.
       recovered = recovered[: top_k - 1]
       deduplicated = deduplicated[: top_k - len(recovered)] + recovered
   ```
   (One functional line + comment. Existing tests stay green: the buried-target test has L = 1 < 7, cap is a no-op there — verified against `tests/test_retrieve.py:202-227`.)
2. **`scriptengine/stores/facts.py`** — `passages_for_subject` docstring (line ~1983): first line "Every level-2 passage" → "Every level-0 (the document's lead card) and level-2 passage", plus one line for *why* the card is in the floor (a subject whose key line lives only in the lead paragraph is in the floor by construction — G-CSM-2 / csm-fact-06, 0 passages pre-fix). The inline "see the docstring above" at facts.py:2026-2027 then stops dangling.
3. **`tests/test_retrieve.py`** — `TestQueryCoverRecallGuard` (line ~144): one new model-free test, the class's existing tmp-store pattern (a tmp `FactStore`, no vector dir, fake reranker): ~17 name-dense *covering* distractors (each ≥8 of the 10 query content words; unique 40-word tails so dedup keeps them) + the verbatim target chunk; a hostile reranker (distractors 0.9, target 0.1); `search(top_k=8, rerank=True)`; assert (a) `len(result.passages) == 8` (the beam does not grow), (b) `result.passages[0]` is the rerank #1 distractor (no full swap), (c) the tail 7 slots hold re-admitted covering distractors in rerank order (the splice actually executed — pins the L > top_k no-op regression).

**Non-blocking record items (ship in the same commit, no engine logic):** (a) `reports/csm/receipts/iter1_r2_passageleg.md` residual-risk line: add the CJK-inertness note (blind spot 4) — post-amendment the "beam-bounded" wording is true; (b) "Zero series names in .py" → "zero series names in .py **logic**; WHY comments cite queue-row IDs and bug-instance names per house convention" (clash 5).

**Post-amendment gate-1 pin: 1,305 collected (1,303 passed + 2 xpassed, 0 failed)** = 1,303 + 1 (this test). The 2 xpassed remain the G-CSM-1 debt xfails in `tests/test_csm_fixtures.py`.

## The Verdict - R-3

**AMEND.** The three mechanisms are sound and the no-op claim is verified on disk (only csm declares the fields; all 8 declare `ability_sections`; JJK pins green — my run: 40 passed + 2 xpassed). The residuals (set-02: 3, char-03: 5, char-01: 5 intruders) are correctly left as bank-level curation (council agreement 2). But four independent, small defects block SHIP as-is, plus the records package:

1. **`scriptengine/retrieve/roster.py:2421` (EOL, zero logic)** — the `return (primary, -float(edge.get("confidence") or 0.0), quoted)` line in `rank_relations` (an unrelated function) was the file's *only* LF line at HEAD (`git show HEAD:...` line 2368; the file is otherwise CRLF) and the working tree normalized it to CRLF, creating a +1/−1 no-op hunk that muddies gate attribution (A, D, E + R2/R3/R4). Restore that line to the HEAD byte state (LF). Verify: `git diff --stat scriptengine/retrieve/roster.py` returns to **+126/−8** (current plain stat +127/−9 verified; `--ignore-cr-at-eol` without `-w` gives 126/8, i.e. exactly one CR-only line).
2. **`scriptengine/retrieve/roster.py`, `Roster.warning` (~line 427)** — the closed-members branch fires whenever a `rule="closed-members"` entry is in `rejected`, which on the documented empty-intersection data-error path (full 14 served, all 14 also in `rejected`) mis-reports "the closed membership is served, 14 of 14 named members" (B + R1/R3/R5; verified in the diff hunk). Gate the branch: `... and len(self.members) < self.candidates` — on the data-error path members == candidates, so it falls through to the true "every member was kept" wording.
3. **`scriptengine/retrieve/roster.py`, `build_roster` declared branch (~line 1652)** — `if closed_rejected:` → `if closed_rejected and len(closed_rejected) < candidates:`. On the empty-intersection path `closed_rejected` contains *all* served members (14 of 14, R1's finding at the hunk), so the report-don't-hide record currently logs every served member as rejected while serving it. The gate (nothing was actually scoped out ⇒ no rejected entries) makes the record self-consistent; the normal scoping path (14 → 7: 7 < 14) is unchanged.
4. **`tests/test_csm_roster_scoping.py`** — one new model-free test `TestClosedMembershipEmptyIntersection` pinning the documented data-error policy (currently comment-only, B): the synthetic pattern — a tmp `SeriesPaths` + an `overrides.yaml` declaring a roster whose `closed_members` is disjoint from `members:` (read via `load_overrides`, `scriptengine/config.py:276`) + a tmp `FactStore` with the member documents (the `tests/test_roster.py:29-31` tmp-store pattern); assert the full member list is served, `rejected` carries no `rule="closed-members"` entries, and the warning is not the closed-members wording.
5. **Records package (one ID spelling, no engine code):**
   a. `tests/test_csm_roster_scoping.py` line 1: `"""G-CSM-3 (red list R-3)` → `red list R-4`. Verified: `reports/csm/red_list_csm.md:41` R-3 = the roster-door 31/88 budget floor (landed at f93d396); `red_list_csm.md:54` R-4 = "G-CSM-3 — section-scoped intruders on closed-set asks" — the scoping debt this draft fixes.
   b. `series/csm/overrides.yaml` comment (line ~74, the diff hunk `# G-CSM-3 (2026-09-09, red list R-3):`): → `red list R-4`.
   c. `reports/csm/receipts/iter1_r3_roster_scoping_run.md`: "Red-list R-3" → "Red-list R-4"; the stale "**1,296 collected**" expectation (pre-R-2) is superseded by the shared 1,305 pin (verified stale).
   d. `reports/csm/red_list_csm.md` addendum: one ID-mapping line — queue `fix_class R-3` (the scoping rows csm-set-17/02/01, csm-char-03, csmdoor-01, red-R-3) = red-list **R-4** (G-CSM-3); queue `red-R-4` = the d5 line-miss class (csmd5-01..07, gate400-*; no red-list row, override-first) — verified both spellings in `reports/csm/miss_queue_csm_iter1.jsonl`, so the queue↔red-list join can never again be read two ways.

**Post-amendment gate-1 pin (shared with R-2): 1,305** (= 1,303 + 2 new tests, one per draft).

## The Shared Gate Sequence

**Pre-gate (B, model-free, one bounded batch):** land the R-2 amendments (cap + docstring + 1 test) and R-3 amendments (EOL restore + warning gate + rejected-append gate + 1 test + records package). Verify: `pytest tests/test_retrieve.py tests/test_csm_fixtures.py tests/test_csm_roster_scoping.py -q` = **42 passed + 2 xpassed** (current 40+2, verified in this run, +2 new tests); `git diff --stat scriptengine/retrieve/roster.py` = **+126/−8**; `pytest tests/ --collect-only -q` = **1,305**.

**One-copy 150k ordering (D's sequence, per the R-1 gate record `reports/master-work/work_log.md:75-76`; Qwen untouched throughout):**

1. Stop `:8000` (both service pids; port freed).
2. **Gate 1:** `pytest tests/ -q` — in-process CUDA, server down — expected **1,305 collected (1,303 passed + 2 xpassed, 0 failed)**.
3. **Gate 2:** `eval --series jjk` — in-process CUDA, server down — expected **31/31**.
4. Restart `:8000` with `SCRIPTENGINE_DEVICE=cpu` (the R-1 self-correction: health-check the device *before* any probe).
5. **Gate 3:** `span-recall --series jjk` — expected **48,572/48,572 offline (rc=0)** + **400-probe ≥390/400 (97.5%)** (the CPU 400-probe is the pre-sanctioned long run; deterministic seed-7 sample, cumulative ledger — a killed attempt re-launches setsid, same sample).
6. **Gate 4:** `canon-run --series opm --skip-eval` — expected **10/16 exact + 236/236 canon + 79.0%**. The **opm-set-16 pre-registration stays live**: a canon drop limited to opm-set-16 = the documented R-1 delta, *not* a revert trigger (work_log:76: the stamp+pin+red-list addendum stay live as tripwires).
7. **B's class re-sweeps after the gates** (live CPU `:8000`; R5 closure meter = **≥1 own-new-row HIT or halt to council**, zero new misses on any stamped row, close only HIT rows, update the queue with closure receipts):
   - **R-2 rows:** csm-fact-06 (+ red-R-2, same debt) + the 13 d5 rows (csmd5-01..07, gate400-188/189/211/320/490/542 — all `R-4/R-2` dual-stamped in the queue) + **csm-set-14/15 (R-1's closed rows, invariant expected — the G7 count branch at context.py:288-299 runs R-2's re-admission; a regression = new miss = halt)**. Expected own HITs: csm-fact-06 (0 → ≥1 passage) + d5 rows.
   - **R-3 rows:** csm-set-17/02/08/01 + csm-char-01/02/03/04/05 + **csmdoor-01** (R-3-stamped, the 31/88 floor probe, invariant expected — verified open in the queue; its omission from the receipt's sweep list is the amendment here, not in the receipt). Expected own HITs per the receipt's R5 meter: **set-17 (14→7), set-01 (7→5, folds to 4 gold), char-02 (18→16)** = 3 ≥ 1; set-02/char-03 stay red-partial (3/5 intruders) pending bank curation; set-08, char-04, char-05, csmdoor-01 invariant.
8. **Selective commit** of both drafts + both receipts (amended) + the records package + this council package as ONE commit (the R-1 pattern: `plan/decisions.md`, `a_wake_log.md`, `reports/index.md` etc. excluded).

**Gate-failure semantics (two drafts sharing one commit):**
- **Infra flake** (tool timeout, service hiccup) → re-run the failed leg only (R-1 precedent: gate 3's 3600 s timeout re-launched setsid on the same seed-7 sample).
- **Single-draft regression, attributable to that draft's files** → stash that draft's files, re-run the failed leg to confirm the survivor is clean, commit the survivor with its recomputed pin (**R-2 alone = 1,291; R-3 alone = 1,297**); the failed draft returns to the worker with the failure record; the opm-set-16 pre-registration stays live either way; the GATES ledger records which package each gate run covered.
- **Canon-opm drop outside pre-registered opm-set-16** → the documented **R-3 revert trigger** (no OPM field is declared; the mechanisms are no-ops there — a drop can only come from a shared leg) → revert + halt to council.
- **Combination-only break** (each draft alone passes, both together fail) → **halt to council** (a new interaction finding; no auto-resolution).
- **Attribution map** (the R-2/R-3 asymmetry, R4): the JJK eval + 400-probe legs are R-2-sensitive (level-0 card + re-admission composition — span-recall offline *cannot* regress from either draft, neither touches chunking); the canon-opm roster rows are R-3-sensitive. A probe < 390/400 or an eval drop blames R-2 first; the documented fallback if a JJK probe regression isolates the level-0 card (E's change-of-mind): make the card floor a per-wiki opt-in.

## The One Thing to Do First

B lands the seven code/test amendments (R-2: the `top_k - 1` cap in `hybrid.py` + the `facts.py` docstring + the 17-distractor guard test; R-3: the LF restore at `roster.py:2421` + the `warning` gate + the rejected-append gate + the empty-intersection test) and the five-item records package, in one bounded model-free batch — then verifies `pytest tests/test_retrieve.py tests/test_csm_fixtures.py tests/test_csm_roster_scoping.py -q` = 42 passed + 2 xpassed and `git diff --stat scriptengine/retrieve/roster.py` = +126/−8 — and only then starts the one-copy gate sequence with `:8000` down (step 1 above). Nothing commits until all four gates and both re-sweeps are green.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Read-only chairman run: zero codebase edits (no git add/commit; the only file written is this council record at the runtime-authoritative path). Scope kept to the combined R-2/R-3 verdict; no new product/architecture decisions invented — every AMEND item is a defect an advisor or reviewer found and I re-verified on disk."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Every load-bearing claim re-verified on disk in this run with cited paths: the hybrid.py splice + _query_covered + rrf_score (git diff, working tree); facts.py level IN (0,2) + dangling docstring at facts.py:1983/2026-2027; roster.py M1/M2/M3 + EOL hunk at :2421 (plain +127/-9 vs +126/-8 ignore-cr-at-eol) + warning hunk ~427 + rejected-append ~1652 + scoped guard inside the asked&{TECH,TRANSF} block (~2831); series greps (only csm declares the 3 fields; all 8 declare ability_sections); single production caller context.py:409; G7 count branch context.py:288-299 rerank=True; floor-fill walk context.py:546-548; red_list_csm.md:16/28/41/54 (R-3 = 31/88 floor, R-4 = G-CSM-3 scoping); queue stamps (miss_queue_csm_iter1.jsonl: set-17/02/01, char-03, csmdoor-01, red-R-3 = fix_class R-3 open; csmd5-01..07 + gate400-* = R-4/R-2; set-14/15 + red-R-1 closed); work_log.md:75-76 GATES baseline + git log b84445f/aef6707; both receipts (iter1_r2_passageleg.md stale-claim check, iter1_r3_roster_scoping_run.md 'Red-list R-3' + stale 1,296 + sweep-list omission verified verbatim); test file line 1 'red list R-3' verified. Commands: 3-file battery 40 passed + 2 xpassed in 3.71 s; collect-only = 1,303; live door probe = 7 5 16 (matches the receipt's post-fix table). Nothing left UNVERIFIED."
    }
  ],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git diff / git diff --ignore-cr-at-eol --stat / git show HEAD (hybrid.py, facts.py, roster.py, series/csm/overrides.yaml)",
      "result": "passed",
      "summary": "diffs match the draft descriptions; the L>=top_k splice regimes and the one CR-only hunk (roster.py:2421) confirmed"
    },
    {
      "command": "grep series/*/overrides.yaml (3 new fields + ability_sections); grep callers of passages_for_subject; grep series-name tokens in added diff lines",
      "result": "passed",
      "summary": "no-op claim verified (only csm declares the fields; all 8 declare ability_sections); single production caller context.py:409; zero series names in .py logic (11 comment tokens)"
    },
    {
      "command": "python parse of reports/csm/miss_queue_csm_iter1.jsonl + grep red_list_csm.md + grep work_log.md GATES + git log b84445f/aef6707",
      "result": "passed",
      "summary": "queue stamps, the R-3/R-4 ID collision, the 1,283 R-1 baseline and the opm-set-16 pre-registration all confirmed"
    },
    {
      "command": "scriptengine/.venv/bin/python -m pytest tests/test_retrieve.py tests/test_csm_fixtures.py tests/test_csm_roster_scoping.py -q",
      "result": "passed",
      "summary": "40 passed, 2 xpassed in 3.71 s (the 2 xp = the G-CSM-1 debt xfails)"
    },
    {
      "command": "scriptengine/.venv/bin/python -m pytest tests/ --collect-only -q",
      "result": "passed",
      "summary": "1303 tests collected in 0.95 s = 1,283 (R-1) + 7 (R-2) + 13 (R-3); post-amendment pin 1,305 stated in the verdict"
    },
    {
      "command": "live door probe: build_roster over the csm store (3 receipt phrasings)",
      "result": "passed",
      "summary": "7 / 5 / 16 — matches the R-3 receipt's post-fix table (set-17, set-01, set-02)"
    }
  ],
  "validationOutput": [
    "pytest subset: 40 passed, 2 xpassed in 3.71s",
    "collect-only: 1303 tests collected in 0.95s",
    "git diff --stat roster.py: +127/-9 plain vs +126/-8 --ignore-cr-at-eol (one CR-only line at :2421)",
    "door probe: set-17=7, set-01=5, set-02=16 (receipt post-fix state holds)"
  ],
  "residualRisks": [
    "R-2 degenerate regime (L>=top_k) is rare in practice; the cap is the cheap close, and the 400-probe (zero headroom at 390/400) is the only gate sampling the level-0-card composition delta on JJK — documented residual",
    "_query_covered is inert on pure-CJK queries (re-admission leg only); recorded for the receipt, no fix in scope",
    "csmdoor-01 + csm-set-14/15 were missing from the receipts' sweep lists — added to the shared gate sequence; a miss on either halts",
    "R-3 x R-5: relations-mode scoping vs closed_members is deferred to R-5 drafting (red-list addendum); forward note recorded"
  ],
  "noStagedFiles": true,
  "diffSummary": "No codebase edits (read-only chairman). The verdict AMENDs both drafts with 7 code/test hunks + a 5-item records package, all specified file/hunk/test-level; post-amendment gate-1 pin 1,305; one shared four-gate re-run with explicit failure semantics for the shared commit.",
  "reviewFindings": [
    "blocker: hybrid.py:358-366 uncapped `recovered` — L>top_k silent no-op + L==top_k full swap; cap at top_k-1, order-preserving, +1 test",
    "blocker: roster.py:2421 CR-only hunk in unrelated function rank_relations — restore LF, verify +126/-8",
    "blocker: roster.py ~427 Roster.warning misreport + ~1652 rejected-append on the empty-intersection data-error path — two one-line gates + 1 pinning test",
    "note: red-list ID collision (scoping debt = R-4, cited as R-3 in the test docstring, yaml comment, and receipt) — records package, one spelling",
    "note: gate-1 pin moves 1,303 -> 1,305 with the amendments (split-commit pins 1,291 / 1,297)"
  ],
  "manualNotes": "Verdicts: R-2 AMEND (3), R-3 AMEND (4 + records). The 1,303 collect-only and the 7/5/16 door probe were independently re-run in this chairman session (not taken from the advisors' records). Baseline gate numbers (31/31, 48,572, 390/400, 10/16+236/236) are quoted from the R-1 gate record (work_log.md:75-76, commits b84445f/aef6707) and are re-established by the shared re-run itself."
}
```
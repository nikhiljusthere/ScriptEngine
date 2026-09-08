# COUNCIL: CSM-1b + CSM-2 cadence review (2026-09-08)

**n = 5 advisors** (The Outsider, The Contrarian, The First Principles
Thinker, The Executor, The Expansionist) · **n = 5 peer reviewers** (A–E) ·
1 chair.

## Run log

- **Round 1** (workflow `37b24d0a-84ef-4aa0-b6fd-a08fd20fa354`): the advisor
  round is **valid** (5/5 completed; run ids: `58cdfdb7-5d74-4fcf-b36f-3888ee41ca6f` =
  Contrarian, `245ad7fd-1f7a-424f-98c3-2c98e2ccc817` = First Principles,
  `4800520e-36c7-45ff-8f22-03ab55609142` = Expansionist, `a284e2a1-c27f-4724-a28b-9342769d82bf`
  = Outsider, `7b414bd9-f4ff-48ab-a72c-b1432fef7b36` = Executor — identity
  verified from each run's task prompt; advisor responses recovered verbatim
  from the runs' session logs). The round-1 peer +
  chairman rounds are **void**: a harness text-capture bug made the peer/chairman
  prompts receive five failure-stub advisor responses instead of the advisor text,
  so the round-1 chairman record (the previous contents of this file) was built on
  stubs and is superseded.
- **Round 2** (workflow `8fef15e2`): peers + chairman re-ran on the recovered
  advisor text. Peer reviews persisted to `reports/csm/council-1b-2/peers/peer-A.md`
  … `peer-E.md`; the chairman (this record) synthesized from the recovered text.
- **Chair verification (2026-09-08, raw):** before recording, every load-bearing
  claim was re-verified in-tree: `series/csm/facts.db` (`Blood Weaponization` 0
  chunks any-case; `Prime Minister Contract` 0 facts; `pulling a cord on his
  chest` 1 chunk vs `the cord` 0; TSD 1/4/5/6/7 chunk counts 1/31/18/3/12, TSD
  2/3 absent; 537 documents; 748 relations rows); `tools/coverage_report.py jjk`
  diff vs committed `reports/page-campaign/COVERAGE.md` empty (modulo the
  `Generated:` line); `opm` rc=3 naming the missing `page_scope`; `csm` rc=0,
  0/537, in-scope remainder 227; `pytest tests/ --collect-only` = **1249** tests
  (1242 + CSM-2's 7); `git log` proves `9e13815` (gates re-baselined, 1242)
  predates `42aa296` (CSM-2, +7 tests); `default="jjk"` confirmed at
  `tools/coverage_report.py:224`; `reports/csm/CSM1B_BANK_VALIDATION.md`
  confirmed to contain **no** bank-changed caveat; untracked receipts confirmed
  (`reports/2026-09-08-{0746,0752,0824}/`, `reports/csm/GATE_REBASELINE.md`).

## The Question

CSM 100% campaign (ScriptEngine repo, /home/goblin/ScriptEngine) - cadence council: review the work just completed, before CSM-3 (D5 measurement infrastructure) starts.

Just completed:
(1) CSM-1b - the owner directive: validate the revid-stamped CSM seed bank (39-question bank + 11-question relations bank) against the current index (post-G15 re-index). Four stale gold expectations were fixed IN PLACE (reasons in the bank notes); four numbered engine gaps were filed (G-CSM-1..4); the relations bank measured 0/11 (all route to roster; the relations channel exists only on qa bundles).
(2) CSM-2 - council item 2: every CSM page type (13 types, 537 pages incl. 14 unknowns) classified in-scope / excluded-in-writing + a reusable archetype schema, in series/csm/overrides.yaml; tools/coverage_report.py now reads scope from overrides (JJK-hardcoded IN_SCOPE_TYPES/IN_SCOPE_PAGES retired) and exits 3 on unclassified; JJK output byte-identical; pytest 1249.

Standing campaign rules to judge against: zero new questions in the CSM-1b pass; "fix the question + record why, never rephrase to dodge"; raw receipts, never "100% pass rate" prose; no series name in any .py; the JJK baseline stays untouched.

Judge: (a) are the 4 gold fixes honest against "fix the question + record why, never rephrase to dodge"? (b) are the gap filings (G-CSM-1..4) complete and correctly classified gold-side vs engine-side? (c) does CSM-2 hold the JJK baseline + "silence must become an error" + no-series-name-in-.py? (d) what must the campaign fix or add BEFORE CSM-3 (D5 measurement infrastructure) starts?

Response-letter to advisor mapping: A=The Outsider, B=The Contrarian, C=The
First Principles Thinker, D=The Executor, E=The Expansionist. Peer-reviewer
letters A–E are reviewer ids (each reviewed ALL five responses), not response
ids.

## Advisor responses (named, verbatim)

### The Contrarian (response B)

All load-bearing claims verified against the store, git, and by re-running the tool. Here's my read as the Contrarian:

**a) Gold fixes — honest, one latent instability.** None rephrases the question text; each aligns the expectation to corpus evidence and records why (revid + 0-hit counts). I confirmed "0 store hits" in `csm/facts.db`: `Weaponization`=0, `Prime Minister`=0, `Contract with the Prime`=0; divisions TSD 1/4/5/6/7 present, 2/3 absent, only TSD 4/5 have document pages. No phantom green: set-02→13/13 legitimately (phantom item verified dead), while fact-06/char-04/set-14 are left failing (0/5) with the engine gap cited. The weak one is **csm-set-14**: the answer (5) is now coupled to the declared roster, which is a *floor*, not a wiki-stated total (Division 1 = 1 chunk, no page; a "Division 2 Vice Captain" page implies a never-named Division 2). The gold silently churns whenever the roster moves. Documented decision, not a dodge — but CSM-3 must not treat it as a stable oracle.

**b) Gap filings — classified right, completeness thin.** G-CSM-1..4 are all correctly engine-side. But G-CSM-1's deferral rationale ("build_roster … verified in process") has **no persisted raw receipt** (violates "raw receipts"); G-CSM-2 is filed but unbounded (2 examples, no census of how many prose-only facts are unreachable); G-CSM-4 (relations) is deferred to "CSM-3/CSM-7," yet item 3's scope is explicitly *three* doors (qa+roster+narrative) — relations is a fourth with no named home in CSM-3.

**c) CSM-2 holds, one overclaim.** JJK `COVERAGE.md` regenerates **byte-identical** (I diffed: clean modulo the Generated line); exit-3 is live (opm→rc 3, error names the fix); no per-wiki logic in `.py`. But `default="jjk"` (line 224) is a series name in the tool, so "no series name in the tool" is overstated (pre-existing CLI default, not logic).

**d) Must fix before CSM-3.** (1) **Stale baseline** — the sharpest one: `GATE_REBASELINE` (git `9e13815`) measured pytest **1242** on the tree *before* CSM-2's 7 new tests (now 1249). "JJK baseline = pytest 1,242" is no longer reproducible on the current tree; re-baseline before CSM-3 re-verifies gates. (2) Persist a raw receipt for the G-CSM-1 roster-door claim. (3) Give G-CSM-4 a named home or explicitly scope it out of CSM-3's three doors. (4) Bound G-CSM-2 with a count so CSM-3 doesn't inherit an unmeasured gap.

*(Chair note: the Contrarian's full run also persisted an acceptance-report block listing its commands (JJK coverage re-run + diff, csm/opm tool runs, sqlite store queries, git-log ordering) — recorded above; the run's raw output remains in the subagent run directory `58cdfdb7-5d74-4fcf-b36f-3888ee41ca6f`.)*

### The First Principles Thinker (response C)

**(a) Honest.** Re-verified all four against `series/csm/facts.db`: "Blood Weaponization" 0 hits in chunks/facts; Denji "pulling a cord" 1 hit vs "the cord" 0; Makima corpus-phrase 27 hits vs bank-coinage 0; all five TSDs (1/4/5/6/7) named in the store. No question was rephrased; residual misses were filed as gaps, not tuned around. One caveat: csm-set-14's new expectation matches a roster the *campaign itself declared* — oracle and gold sit on the same side of the table; the 2026-08-15 mention-count audit backs it and the receipt says "the wiki states no total." Acceptable, but D5/CSM-7 must not treat that declared roster as an independent oracle. Canon arithmetic checks out (146→148 = set-02 −1 + set-14 +3; 138 found in both runs; the two recall-0s are exactly G-CSM-1's).

**(b) Complete; correctly split; badly scheduled.** Every miss in the raw runs is assigned (recall-0s → G-CSM-1, fact miss → G-CSM-2, intruders → G-CSM-3, relations 0/11 → G-CSM-4), all engine-side, none misfiled. The defect is the landing: "deferred to CSM-3 / CSM-7" — but CSM-3 builds measurement infra, it does not fix the router. Each gap must name the item that absorbs it (the §9a closure loop) or it evaporates between items.

**(c) Holds.** JJK `COVERAGE.md` regenerated: byte-identical (diff empty; legacy behavior encoded verbatim in `series/jjk/overrides.yaml`). Exit-3 verified all three ways, opm rc=3, 7/7 tests pass. Series-name check: scope logic is clean; only pre-existing `default="jjk"` in argparse — a CLI default, not per-wiki handling; record it as an explicit exception.

**(d) Before CSM-3:** (1) re-baseline the gate — GATE_REBASELINE's 1242 predates CSM-2's 7 tests (now 1249); Qwen is back to 262k (30.6/32.6 GB, 100% util) and CUDA pytest OOMs the known 6 VRAM-sensitive `test_context` cases — switch to 100k or run CPU and re-verify before the sweep. (2) Decide the <6-word floor *before* pinning the panel. (3) Add a per-door sanity floor to CSM-3's done-criteria: if the qa door's raw count is 0 on a sanity subset, halt — G-CSM-2 says the passage leg is empty for subject-named questions; don't burn ~51 GPU-hours grading a dead door. (4) Commit the uncommitted receipts (`reports/2026-09-08-*/` untracked; JJK `recall_verbatim.jsonl` modified, numbers unchanged).

*(Chair note: full run + acceptance-report block in run directory `245ad7fd-1f7a-424f-98c3-2c98e2ccc817`.)*

### The Expansionist (response E)

**(a) Gold fixes: all four are honest — and one of them raised the bar.** Re-verified in the csm store: 0 chunks name `Blood Weaponization` (removal correct — the wiki never documented it); 0 facts name `Prime Minister Contract` (the rename matches corpus wording, old name kept as alias); `pulling a cord on his chest` is present (1 chunk — the "the"→"a" fix was a guaranteed miss); all five divisions are named in the corpus (1/31/18/3/12 chunk mentions). Question text is unchanged in all four; only expectation/alias/source moved. csm-set-14 went 2→5 — a *stricter* gold — and the receipt records it sitting at 0 recall until G-CSM-1. No dodging anywhere.

**(b) Gap filings are complete against the receipt's numbers**: recall-0 pair → G-CSM-1, the 1/18 fact miss → G-CSM-2, intruders → G-CSM-3, relations 0/11 → G-CSM-4; all four correctly engine-side, gold-side resolved in place. But G-CSM-2 is under-scoped: the qa passage leg is dead on CSM wholesale (bundles answered by facts + relations alone), not a few subject questions.

**(c) CSM-2 holds**: JJK's regenerated report diffs empty (byte-identical, rc=0), `coverage_report opm` exits 3 (silence = error, verified), no series name in `coverage_report.py` (only via `paths.overrides`), 7/7 scope tests, 1249 = 1242+7.

**(d) Take the upside before CSM-3:**
1. **Fix G-CSM-4 first**: a routing change unlocks 11 frozen relations questions and the 748-row relations table (51/52 partners held) — the cheapest win on the board, and per the overrides note it generalizes to jjk/opm.
2. **Fold T0's frozen-set generation into CSM-3(a)**: T0 needs the same seeded + revid-stamped JSON the pinned panel produces — one piece of infrastructure, two of the four pilot cost numbers, zero authoring.
3. **Schedule G-CSM-2 as CSM-3's first fix**: a dead passage leg makes the exhaustive sweep's qa-door floor structurally unreachable. Run the sweep in 100k mode (262k window closed, `:8000` back on CPU).

*(Chair note: full run + acceptance-report block in run directory `4800520e-36c7-45ff-8f22-03ab55609142`. Peers A/B/D all corrected E's (c) "no series name" claim — `default="jjk"` at line 224; chair confirmed.)*

### The Outsider (response A)

**The numbers a fresh reader trips on, and what I verified against the stores.**

**(a) The 4 gold fixes are honest — I re-checked them cold.** `Blood Weaponization`: 0 hits in `series/csm/facts.db` (both spellings) and the note pins live revid 44435; that's deleting a fabricated item, not dodging. `csm-fact-06` the→a: "pulling a cord on his chest" is in the store (1 chunk), and the receipt admits it *still misses* post-fix (G-CSM-2) — no greenwashing. `csm-char-04` rename keeps the old name as alias and says the fact is still unreachable. `csm-set-14` (2→5 divisions) is the one that looks like the fix *made things worse*: canon 146→148, precision 94.5%→93.2% in the CSM1B headline table. It's only honest when you open `reports/2026-09-08-0752/REPORT.md`, which carries the caveat "the bank changed between these two runs… not a clean measurement." The receipt's own table shows the drop with no pointer to that caveat. One line in `CSM1B_BANK_VALIDATION.md` fixes it.

**(b) Gaps: complete and correctly classed.** Both recall-0 questions (set-14, set-15) are G-CSM-1's rows (verified in the 0752 report); 0/11 relations table is per-question in `CSM1B_RELATIONS_BANK.md`. Zero new questions (39/39 active, 39/39 stamped — verified). One flag: G-CSM-4 is half a *mode-definition* decision (the bank declares `expect_mode: relations` the router cannot emit), not just a router bug — CSM-3's door work must pick the door first, or it builds a panel the bank can't consume.

**(c) CSM-2 holds.** I regenerated JJK's report: diff empty modulo `Generated:`. `opm` exits 3 naming the missing `page_scope`; csm exit 0, 0/537, remainder 227; 7/7 scope tests pass; the store's 14 unknowns match `unknown_pages` exactly. No series name in the tool beyond the pre-existing `default="jjk"` CLI arg.

**(d) Before CSM-3:** (1) add the bank-changed caveat to the CSM1B headline; (2) pre-decide the relations door mode for G-CSM-4; (3) the 6-word short-line floor (council blind spot 6) is still undeclared — CSM-3(d) must include <6-word lines or record the exclusion in CSM's audit.

*(Chair note: full run + acceptance-report block in run directory `a284e2a1-c27f-4724-a28b-9342769d82bf`. Chair confirmed: the CSM1B headline table carries no caveat pointer (grep-verified in-tree).)*

### The Executor (response D)

**The Executor — CSM-1b + CSM-2 verdict**

**(a) The 4 gold fixes.** Three are clean and I verified the evidence against the store: `Blood Weaponization` and `Prime Minister Contract` both 0 hits across chunks/facts/aliases; "pulling a cord on his chest" is the Denji infobox line verbatim. All four kept the question text and recorded the reason — no dodging. **csm-set-14 is the weak one.** The 0752 report's own diagnosis buckets 3 of the 5 divisions as "corpus gap — the wiki does not support the claim," yet the gold now expects all 5 from a source page that doesn't name them. The 2026-08-15 audit rationale is on record, but CSM-1B never reconciles it. Council must rule now: accept corpus-compiled gold in writing, or retire the question (its sibling was retired). Letting CSM-7 grind this is how questions die by committee.

**(b) Gaps.** G-CSM-1/3/4 correctly engine-side. One misclassification risk on G-CSM-2: 0752's bucket table sends the missing Makima PM-contract item to "extraction gap — fix the prompt in `ingest/abilities.py`," but the 2026-08-17 REFUTED note in overrides says the prompt correctly returned `[]`. The receipt must record which fix wins, or CSM-7's fixer patches the prompt and the cached answers survive.

**(c) CSM-2 holds.** I re-ran it: JJK `COVERAGE.md` diff empty modulo `Generated:`, `opm` rc=3, CSM 0/537 / 227 remainder, scope tests 7/7. "No series name in the tool" is true only in spirit — `default="jjk"` (pre-existing, 47e483a) and docstring refs remain. One-line receipt wording fix.

**(d) Before CSM-3, Monday morning:** (1) Map the gaps to items — none of G-CSM-1..4 appears in council item 3, which is measurement infra only; G-CSM-4 (relations door) isn't even one of item 3's three doors, so 0/11 has no owner — rule it in or defer it explicitly. (2) CSM-3's first step is clear: pinned hashed panel + held-out split, hash stamped in the report. (3) Gate re-baseline is stale: 1,242 predates CSM-2's 7 tests; the tree is 1,249. Re-run before CSM-3 starts.

*(Chair note: full run in run directory `7b414bd9-f4ff-48ab-a72c-b1432fef7b36`.)*

## Peer reviews (verbatim)

### Peer A

# Peer A — review of council responses A–E (CSM-1b/CSM-2 cadence)

## 1. Strongest response

**C.** Verified the canon arithmetic (146→148); the only mode-aware gate
read (262k → six VRAM-sensitive cases OOM on CUDA); the only catch of
uncommitted raw receipts (git-confirmed). Its per-door sanity floor
protects the 51-GPU-hour sweep from grading a dead qa door. Runner-up: B
(G-CSM-1 "verified in process" has no persisted receipt); D's 0752-vs-
REFUTED conflict is the sharpest one-off.

## 2. Biggest blind spot

**E.** (i) Misses the stale gate baseline (1242 predates CSM-2's 7 tests;
B/C/D flag it, git order confirms). (ii) Its (c) "no series name in
`coverage_report.py`" is wrong — line 224 `default="jjk"`, caught by A/B/C/D.
(iii) Its (d) (G-CSM-4 first; T0 into CSM-3(a)) contradicts the plan's item
order (fixes → item 7; T0 → 6(e)).

## 3. What all five missed

The re-baseline is mode-gated: Qwen's 262k switch is in progress, so
"re-baseline before CSM-3" needs an explicit order (finish switch →
checkpoint → 100k → CUDA gate → restore); nobody states it. The council's own record + plan bookkeeping (state/decisions)
are uncommitted — "if it is not on disk, it did not happen" is at risk
(C catches receipts only). A's "no blockers" vs B's "blocker" needs a
ruling.

### Peer B

**1. Strongest: B.** It verified the store claims itself (0-hit proofs; only TSD 4/5 have pages → csm-set-14's "5" is a floor, not a wiki total), and its (d) carries the only hard blocker: git-log ordering proves GATE_REBASELINE's pytest 1242 predates CSM-2's +7 tests (now 1249) — the "JJK baseline" is no longer reproducible on the current tree. C's GPU-state point (262k Qwen blocks the CUDA re-baseline; 6 `test_context` OOMs) is a close second but its 1243+6 claim is un-re-runnable right now.

**2. Biggest blind spot: E.** Its (d) is upside-only (fix G-CSM-4 first, fold T0 into CSM-3(a)) with zero gate/baseline items — it misses the stale-baseline blocker entirely. And (c) is factually wrong: it claims "no series name in `coverage_report.py` (only via `paths.overrides`)", but the pre-existing `default="jjk"` CLI arg is in that tool — A, B, C, and D all flagged it.

**3. What all five missed:**
(i) The uncommitted +400-line append to `reports/span-recall/jjk/recall_verbatim.jsonl` (GATE_REBASELINE's probe ran in append mode) is §2a trap #2 in the wild — append-duped jsonl, `done` unwired. CSM-3(b) is the fix for the probe path; re-running the probe before that appends another 400 lines. C lists the file only as "commit it".
(ii) The re-baseline B/C/D demand is not runnable on CUDA today (Qwen 262k, 100% util) — it needs a 100k-switch/CPU decision first (only C says so). And CLAUDE.md's gates table is now stale a third time (1,239 → 1,242 → 1,249).

*Written to `reports/csm/council-1b-2/peers/peer-B.md`.*

### Peer C

**1. Strongest: B.** Most verified; its sharpest finding is the load-bearing one: the 1242 gate baseline (GATE_REBASELINE, git `9e13815`, measured 13:47) predates CSM-2's 14:07 commit (`42aa296`, +7 tests → 1249), so "JJK baseline = pytest 1,242" is no longer reproducible and CSM-3's gate re-verification is broken at start. B also caught G-CSM-1's un-receipted "verified in process" claim (a raw-receipts rule violation) and G-CSM-2's unbounded scope. C is close second: live GPU state (Qwen back on 262k → CUDA pytest OOMs 6 `test_context` cases; re-baseline needs 100k or CPU), the uncommitted receipts, and its per-door sanity floor ("don't burn ~51 GPU-hours grading a dead door") is the best CSM-3 guard proposed.

**2. Biggest blind spot: A.** A re-verified every CSM-1b number cold (and found the missing "bank changed" caveat in the CSM1B headline) — yet missed the stale 1242 baseline that B, C, and D all flagged, and its "before CSM-3" list has no re-baseline item. A reviewer who audited number comparability should have noticed the gate record itself no longer matches the tree.

**3. All five missed:** the campaign's designated live gate record does not exist. The plan makes "the CSM section of `GATE.md`" the live record; no such section exists (`reports/comprehension/GATE.md` is JJK-only), so the re-baseline sits in an untracked `GATE_REBASELINE.md` while committed CLAUDE.md cites the stale 1242. Pre-CSM-3: open the CSM gate section, re-measure on the 1249 tree, commit the receipts (`reports/2026-09-08-{0746,0752,0824}/`, `GATE_REBASELINE.md`, `COUNCIL_csm-1b-2.md`), and record the JJK `recall_verbatim.jsonl` append as the "untouched"-check exception.

### Peer D

**1. Strongest: D.** Only D caught the receipt conflict: the 0752 bucket table assigns the missing Makima item to "extraction gap — fix the prompt in `ingest/abilities.py`", but the CSM-override REFUTED note (2026-08-17) records the extraction *correctly* returning `[]` (the wiki never names the contract). A fixer following the bucket table patches a refuted prompt and the cached answer survives. D also forces a ruling on csm-set-14: 0752 buckets 3 of the 5 divisions as "corpus gap" ("the wiki does not support the claim"), unreconciled with the 2026-08-15 roster audit — accept or retire. Both verified in-tree.

**2. Biggest blind spot: A.** Only A misses that GATE_REBASELINE's 1,242 predates CSM-2's +7 tests (tree now 1,249) — the gate baseline is no longer reproducible. A also rubber-stamps (b) "complete" and never questions G-CSM-2's under-scoping; E's "fix G-CSM-4 first / G-CSM-2 as CSM-3's first fix" smuggles fix-work into an item scoped as measurement infra.

**3. All five missed:** CSM-3's mechanical scope. Nobody re-verified the four §2a traps (seed-7 shuffle, unwired `done` dedupe, partial-denominator `hit_rate`, zero-measurement doors) or the tier-0 rename (blind spot 5) against the tree — all still open (verified in `span_recall.py`/`cli.py`). The re-baseline must also rewrite the stale baseline record (CLAUDE.md and plan item 8 still pin 1,242).

### Peer E

# Peer E — CSM-1b + CSM-2 cadence council

**1. Strongest: B.** Its pre-CSM-3 items are the most rule-grounded and verifiable. The stale gate baseline is a real blocker: git proves `9e13815` (pytest 1,242) predates `42aa296` (+7 tests), so the tree is 1,249 and the standing "1,242" no longer reproduces. B alone flags the in-tree rule breaks — G-CSM-1's "verified in process" has no persisted raw receipt, and G-CSM-4 (relations) has no home in CSM-3's three doors. B's set-14 read (roster = floor, not a wiki total) is the deepest, and B correctly flags `default="jjk"` (line 224). C is runner-up on ops (live 262k OOMs 6 VRAM-sensitive tests — confirmed on nvidia-smi; uncommitted receipts). D has the sharpest catch: 0752 buckets the Makima item as an extraction gap, but the REFUTED note says the prompt was correct.

**2. Biggest blind spot: A.** A signs "no blockers" on three soft items while missing two hard prerequisites: the 1,242→1,249 gate re-baseline, and the uncommitted receipts (`reports/2026-09-08-0746/0752/0824` + `GATE_REBASELINE.md` are untracked).

**3. All five miss §7's four pilot cost numbers as the deliverable.** None lists "produce all four (T0 emergence, T0 survival, new gaps, round-trips) and carry them to the done-declaration"; only E names two. None mention the tier-0 rename `span-recall`→`chunk-containment` (item 3(f)) — without it CSM inherits JJK's misread rc=0.

*Written to `reports/csm/council-1b-2/peers/peer-E.md`.*

## Where the Council Agrees

- **(a) All four gold fixes are honest** — unanimous. Question text unchanged in
  all four; each expectation change is backed by store evidence (chair
  re-verified: 0 chunks any-case for `Blood Weaponization`; 0 facts for
  `Prime Minister Contract`; 1 chunk for `pulling a cord on his chest` vs 0 for
  `the cord`; TSD 1/4/5/6/7 present, 2/3 absent). `csm-set-14` (2→5) is a
  *stricter* gold, not a dodge; residual misses (fact-06, char-04, set-14,
  set-15) were left failing with the engine gap cited, never tuned around.
- **(b) Gaps G-CSM-1..4 are complete against the raw failure rows and
  correctly engine-side** — every miss in the 0746/0752 runs is assigned
  (2 recall-0s → G-CSM-1; the 1/18 fact miss → G-CSM-2; intruders → G-CSM-3;
  0/11 relations → G-CSM-4); gold-side issues were resolved in place, zero new
  questions (39/39 active, 39/39 stamped). Two qualification flags (receipt
  hygiene for G-CSM-1's "verified in process" claim; G-CSM-2's misfiled
  bucket) are recorded under Blind Spots/Rulings below.
- **(c) CSM-2 holds** — unanimous: JJK `COVERAGE.md` regenerates
  byte-identical (chair diff-verified), legacy behavior encoded verbatim in
  `series/jjk/overrides.yaml`, exit-3 live (`opm` rc=3, chair-verified), CSM
  0/537 with in-scope remainder 227, 7/7 scope tests, 1249 = 1242 + 7 (chair
  collect-only verified).
- **"No series name in the tool" is overstated by one pre-existing token**:
  `default="jjk"` at `tools/coverage_report.py:224` (chair-verified; pre-dates
  CSM-2, a CLI default not per-wiki logic). Four of five advisors + all five
  peers flag it; only the Expansionist missed it. Ruling: record it as an
  explicit exception, do not churn the file.
- **One hard blocker before CSM-3: the gate baseline is stale.**
  `GATE_REBASELINE` (git `9e13815`, 13:47) measured pytest 1242 on the tree
  *before* CSM-2's 7 tests; the tree is 1249 (chair-verified by collect-only).
  "JJK baseline = pytest 1,242" is no longer reproducible, and under the live
  262k Qwen (card held) a CUDA re-baseline is not runnable today — it needs the
  100k-mode side-session path. B, C, D + peers A/B/C/E flagged it; only A's
  "no blockers" sign-off missed it (a ruling is recorded below).

## Where the Council Clashes

- **csm-set-14: accept or retire.** The Executor: the 0752 report buckets 3 of
  the 5 divisions as "corpus gap — the wiki does not support the claim,"
  unreconciled with the gold — rule accept-or-retire now or "CSM-7 grinds
  this." The Contrarian/First Principles: the declared roster is a *floor*,
  not a wiki-stated total, and oracle + gold sit on the same side of the
  table — acceptable, but never cite it as an independent oracle. Resolution
  (Ruling 1, below): accept with the floor caveat recorded in the bank note.
- **G-CSM-2's classification and scope.** The 0752 bucket table says
  "extraction gap — fix the prompt in `ingest/abilities.py`"; the 2026-08-17
  REFUTED note in `series/csm/overrides.yaml` says the extraction correctly
  returned `[]` (the wiki never names the contract). The Executor: the receipt
  must record which fix wins, or CSM-7's fixer patches a refuted prompt. The
  Expansionist goes further: the qa passage leg is dead *wholesale* on CSM
  (bundles answered by facts + relations alone), so the D5 sweep's qa-door
  floor is structurally unreachable without a per-door sanity floor. A/B/C/D
  treat it as "filed but unbounded — needs a census." Resolution: reclassify
  (Ruling 2) + per-door sanity floor in CSM-3's done-criteria.
- **G-CSM-4's home.** The Expansionist: fix it *first* (cheapest win — 11
  frozen questions + the 748-row relations table, chair-verified row count).
  The Contrarian/Executor: CSM-3's scope is explicitly *three* doors
  (qa+roster+narrative); relations is a fourth with no named home — a router
  change is fixer territory (CSM-7), not measurement infra. Peers A/D: its
  "fix first" smuggles fix-work into a measurement-infra item and contradicts
  plan item order. Resolution: rule it OUT of CSM-3 with a named owner
  (Ruling 3).
- **"No blockers" (A) vs "blocker" (B/C/D) on the re-baseline.** Ruling: the
  stale 1242 baseline is a hard blocker for CSM-3's gate re-verification step,
  not a defect in the completed CSM-1b/CSM-2 work (which stands as agreed).
- **T0's placement.** The Expansionist wants T0 frozen-set generation folded
  into CSM-3(a) (one infra, two of the four pilot cost numbers); peers flag
  the plan order (T0 → 6(e)). Unresolved tension — carried to CSM-3 planning,
  no ruling forced now (the infra overlap is real, but plan item order stands
  until the campaign re-scopes it).

## Blind Spots the Council Caught

(Items that surfaced only in the peer-review round, or that no single advisor
stated fully.)

1. **The re-baseline is mode-gated and needs an explicit order** (peer A):
   checkpoint → qwen-switch 100k → CUDA gate run (pytest 1249 incl. the 6
   VRAM-sensitive `test_context` cases, eval jjk, span-recall jjk offline +
   probe, canon opm) → report → switch back → restore `:8000` to CPU. No
   advisor stated the sequence.
2. **The JJK `recall_verbatim.jsonl` append trap is live** (peer B):
   GATE_REBASELINE's probe ran in append mode, leaving a +400-line uncommitted
   append (`reports/span-recall/jjk/recall_verbatim.jsonl` modified,
   chair-verified via `git status`). §2a trap #2 (append-duped jsonl, `done`
   unwired) — re-running the probe before CSM-3(b) wires `done` appends
   another 400 lines. Record the current append as a known exception; the fix
   lands in CSM-3(b).
3. **The campaign's designated live gate record does not exist** (peer C):
   the plan designates "the CSM section of `GATE.md`" as the live record, but
   no such section exists (`reports/comprehension/GATE.md` is JJK-only), so
   the re-baseline sits in an untracked `GATE_REBASELINE.md` while committed
   CLAUDE.md cites the stale 1242 (stale a third time: 1,239 → 1,242 → 1,249).
   Open the CSM gate section as the live record when the re-baseline lands.
4. **The tier-0 rename `span-recall` → `chunk-containment` (item 3(f),
   alias kept) is still open and unmentioned by any advisor** (peers D/E):
   without it CSM inherits JJK's misread rc=0. Add to CSM-3's done-criteria.
5. **§7's four pilot cost numbers are the deliverable; no advisor listed all
   four** (peer E): T0 emergence, T0 survival, new gaps, round-trips — all
   four must be produced and carried to the done-declaration.
6. **G-CSM-1's "build_roster verified in process" has no persisted raw
   receipt** (B + peers C/E) — a standing-rule breach of "raw receipts";
   persist the receipt (re-run the roster check, file the output).
7. **The 6-word short-line floor is still undeclared** (A + peers): CSM-3(d)
   must either include <6-word lines in the panel or record the exclusion in
   CSM's audit — decide *before* pinning the panel.
8. **Campaign bookkeeping uncommitted** (peers A/C): "if it is not on disk,
   it did not happen" — commit the receipts (`reports/2026-09-08-{0746,0752,0824}/`,
   `reports/csm/GATE_REBASELINE.md`, this council record + peer files) as part
   of the pre-CSM-3 pass.

## The Recommendation

**Rulings (the campaign acts on these; the owner retains final authority and
may overturn):**

1. **csm-set-14 — accept the corpus-compiled gold, with the floor caveat in
   the bank note.** The 2026-08-15 mention-count audit is on record; the
   roster is a floor, not a wiki-stated total (TSD 2/3 unpaginated; Division 2
   implied by a "Vice Captain" page). Retiring would shrink the bank against
   "fix the question, never dodge"; the missing piece is engine-side
   (G-CSM-1), owned by the closure loop. Add to the `csm-set-14` bank note:
   *"roster-declared floor, not a wiki-stated total; not an independent
   oracle for D5/CSM-7."*
2. **G-CSM-2 — the REFUTED note (2026-08-17) wins over the 0752 bucket
   table.** The extraction prompt in `ingest/abilities.py` correctly returned
   `[]` (the wiki never names the PM contract); the gap is on the qa passage
   leg / retrieval side, NOT an extraction-prompt fix. Update
   `reports/csm/CSM1B_BANK_VALIDATION.md` (G-CSM-2 entry) so CSM-7's fixer
   does not patch a refuted prompt and leave cached answers stale.
3. **G-CSM-4 — ruled OUT of CSM-3's three doors; named owner = CSM-7 fix
   phase (router work).** The relations door needs a routing change (the
   router cannot emit `expect_mode: relations`); that is the fixer's
   territory, and plan item order puts fixes at item 7. The 11 frozen
   relations questions stay frozen until the owner lands; the 748-row
   relations table is their payload.
4. **CSM-3 done-criteria additions (record in the plan before the item
   starts):** (a) per-door sanity floor — if any door's raw count is 0 on a
   sanity subset, halt (protects the ~51-GPU-hour sweep from grading a dead
   qa door per G-CSM-2); (b) the 6-word short-line floor decided *before*
   panel pinning (include or record the exclusion); (c) the tier-0 rename
   `span-recall` → `chunk-containment` (alias kept); (d) §7's four pilot
   cost numbers produced and carried to the done-declaration.
5. **Receipt hygiene (this session, before CSM-3):** add the one-line
   bank-changed caveat to the `CSM1B_BANK_VALIDATION.md` headline table
   (the 94.5%→93.2% dip is a bank change between the two runs, not a
   regression); record the `default="jjk"` token as an explicit exception to
   the no-series-name-in-.py rule (pre-existing CLI default, line 224);
   persist the G-CSM-1 roster-door receipt; commit the untracked receipts and
   record the `recall_verbatim.jsonl` append as a known exception (fix in
   CSM-3(b)).

**Gate re-baseline (the blocker, mode-gated):** run via the 100k+CUDA
side-session chain in the explicit order above (blind spot 1): checkpoint →
`qwen-switch.sh 100k` → CUDA pytest (1249, incl. the 6 VRAM-sensitive
`test_context` cases) + eval jjk + span-recall jjk (offline + 400-probe) +
canon opm → report → switch back 262k → restore `:8000` to CPU. When the
report lands: rewrite the CLAUDE.md + gates-skill baselines (1,242 → 1,249),
open the CSM gate section in `reports/comprehension/GATE.md` as the live
record, and commit the receipts.

## The One Thing to Do First

**Kick off the gate re-baseline side session now (100k + CUDA, tier-2
chain).** It is the only hard blocker to CSM-3's start, it is long-running
and independent, and the campaign can apply Rulings 1–3 + the receipt-hygiene
pass in this session while it runs. CSM-3 opens only after the re-baseline
report lands, the baselines are rewritten (1,249), and the CSM gate section
exists.
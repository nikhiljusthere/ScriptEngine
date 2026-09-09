# Peer review 4/5 — council R-1 router draft (weighted: gate sequence / R2-R5 halt enforceability post-fix)

**1. Strongest: B** — only live negative probes (uncovered scopes stay qa), only caller audit of `_resolves_a_set`, only 9→11 correction, and names the discovery-side residual; E alone touches the halt meter (db stamping) but win-side only.

**2. Biggest blind spot: A.** Never probes live; parrots the stale "pytest 1,265" (tree collects 1,280) and the "9" miscount; asserts "no new failure class" and "no series name in .py" (docstring cites csm-set-14/15); takes the gate sequence, never asking whether R5 can enforce closure.

**3. All five missed — halt enforceability after the fix:** (i) R5's "≥1 HIT" cannot close the class: red-R-1 has no recall target (its note cites set-14/15 recalls); 1-of-2 hits satisfies "≥1" → no halt, yet the receipt closes all 3 rows → close only HIT rows, halt on any R-1 miss. (ii) R2's frozen queue + class-targeted re-sweep are blind to the fix's blast radius: csm "…in Tokyo?" + onepiece "…in the Marines?" flip to roster (latter a wrong set, re-verified live); none is in any gate (opm's row, `questions/opm.json:1785`, is the only delta inside gate 4) and R2 makes new-misses trend-only → stamp db + onepiece + csm-Tokyo as R-1 rows (gate400 precedent) and add "zero new misses on stamped rows" to the pass criterion. (iii) Gate 1 must expect 1,280, not the stale 1,265 (review_2).

## Verification ledger (this run, zero-GPU, read-only, all shells < 15 s)
- `pytest tests/ --collect-only -q` = **1,280** tests (receipt + all five advisors' "1,265" is stale; review_2's correction stands).
- `git diff scriptengine/retrieve/router.py` = one hunk in `_resolves_a_set` (probe: `_COUNT.sub` counting / `_SCOPE_PHRASE.sub` non-counting, router.py:872-878) + docstring; `+22/−1`. R1-d gate at router.py:885 (counting ⇒ exact/declared) untouched; sole caller `route()` has_set probe (router.py:552).
- `reports/csm/miss_queue_csm_iter1.jsonl`: 55 rows, 3 stamped `fix_class: R-1` (csm-set-14, csm-set-15, red-R-1; all `status: open`). red-R-1 carries no recall target of its own — its note cites "csm-set-14 recall 0/5, csm-set-15 0/4".
- `reports/csm/COUNCIL_unit3_sweep.md` R2: "The halt meter = this frozen queue … the 400-gate new-miss rate is trend-only, never a halt trigger"; R5: "any post-fix class re-sweep must show ≥1 HIT in its own new rows or halt to council".
- Receipt `reports/csm/receipts/iter1_r1_router_run.md`: "on green, B marks the three rows `closed`" — green defined as ≥1 HIT, so a 1-of-2 partial satisfies the halt rule while closing the failing row (point 3i).
- Live model-free `route()` probes (re-verified): csm "How many special divisions are in Tokyo?" → **roster** (second csm delta, absent from the receipt's 10-row probe table); onepiece "How many Sweet Commanders are in the Marines?" → **roster** (review_1's wrong-set case, "Marine Commanders" basis; not pinned in `tests/test_csm_router_count_rule.py` — no "Marines" pin in the 11 tests).
- `questions/opm.json:1785` = "How many members are in the Blizzard Group in One Punch Man?" → the only delta row inside a standing gate (gate 4 canon opm); onepiece and db have no gate at all.
- `git status --porcelain`: nothing staged (`git diff --cached` empty); R-1 draft = `router.py` (M) + new test (??) + orchestrator's pre-existing dirt.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Reviewer run only: read the five adv_*.md, prior reviews 1-3, unit-3 council, miss queue, receipt, router.py; ran 4 read-only model-free checks; wrote only the assigned review file. No code/test edits, no scope widening."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Full verification ledger with file:line cites: 1,280 collect-only count vs stale 1,265; queue = 55 rows / 3 R-1 rows, red-R-1 recall-less; R2 'frozen queue, new-miss trend-only' + R5 '>=1 HIT or halt' text; receipt 'on green mark the three rows closed' (1-of-2 partial closes a failing row); live re-verification of both un-gated deltas (csm in-Tokyo, onepiece in-Marines wrong set) and the opm Blizzard row at questions/opm.json:1785; no-staged-files check."
    }
  ],
  "changedFiles": [
    "reports/csm/receipts/council_r1_router/review_4.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "pytest tests/ --collect-only -q",
      "result": "passed",
      "summary": "1,280 tests collected — every advisor's gate-1 expectation of 1,265 is stale"
    },
    {
      "command": "wc/grep over reports/csm/miss_queue_csm_iter1.jsonl + git diff router.py",
      "result": "passed",
      "summary": "55 queue rows, 3 R-1 rows (set-14/15 + red-R-1, all open, red-R-1 has no own recall target); diff = one hunk + docstring, +22/-1"
    },
    {
      "command": "model-free route() probes (csm 'in Tokyo', onepiece 'in the Marines')",
      "result": "passed",
      "summary": "both flip to roster post-fix; the onepiece case is a wrong-set serving (Marine Commanders), in no gate and in no queue row"
    },
    {
      "command": "git status --porcelain + git diff --cached --stat",
      "result": "passed",
      "summary": "nothing staged; R-1 draft is router.py (M) + new test (??) only"
    }
  ],
  "validationOutput": [
    "1280 tests collected in 0.93s",
    "csm-Tokyo: roster | onepiece-Marines: roster",
    "questions/opm.json:1785: 'How many members are in the Blizzard Group in One Punch Man?' (only delta row inside a standing gate)",
    "git diff --cached --stat: empty (no staged files)"
  ],
  "residualRisks": [
    "R5 '>=1 HIT -> close all three rows' can close a still-failing frozen row (1-of-2 partial satisfies the halt rule); amend to close only HIT rows.",
    "R2's frozen halt meter + class-targeted re-sweep cannot fire on the fix's own blast radius: onepiece wrong-set serving and the csm/db flips are in no gate, no queue row, and R2 makes new-misses trend-only; stamp them as R-1 rows (gate400 precedent) with a zero-new-miss pass criterion.",
    "Gate-1 pass criterion must read 1,280, not the receipt's stale 1,265, or a green run mis-scores as regression."
  ],
  "noStagedFiles": true,
  "diffSummary": "No engine diff authored by this reviewer. Judged the R-1 draft's halt-rule/gate enforceability: the draft's code is sound, but the post-fix closure protocol (R2 frozen queue + R5 >=1-HIT + 'close three rows') is unenforceable as written and needs a three-line amendment (close-only-HIT rows; stamp the three un-gated delta rows; gate-1 expectation 1,280).",
  "reviewFindings": [
    "amend: COUNCIL_unit3_sweep.md R5 / receipt 'on green mark the three rows closed' — 1-of-2 HIT satisfies '>=1' yet closes a failing row; close only HIT rows, halt on any open R-1 miss",
    "amend: R2 halt meter — stamp db + onepiece (wrong-set) + csm-in-Tokyo as R-1-class queue rows before the re-sweep and require zero new misses on stamped rows; otherwise the fix's own regressions are unenforceable",
    "amend: receipt gate 1 — expect 1,280 (collect-only verified), not 1,265"
  ],
  "manualNotes": "Weighting was 'gate sequence wrong or R2/R5 unenforceable after the fix lands'; all three findings land on enforceability, not on the code (which is sound and SHIP-eligible with the amendments). E's db-stamping instinct is the only R2 engagement in the five responses but is win-side only."
}
```
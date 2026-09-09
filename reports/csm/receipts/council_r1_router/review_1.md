# Peer review 1/5 — council R-1 router draft (weighted: new false-roster / false-qa the 11 tests + probe table miss)

**1. Strongest: B.** Only response to name the open surface — discovery-side counting (undeclared set, ≥3 members → "exact") now keeping scope in the probe — and the only one with the how-many audit right (11 phrases; A, C, D repeat the receipt's "9"). Verified the caller graph; flagged the receipt fix.

**2. Biggest blind spot: C.** C's verdict rests on calling the delta "declared-name-only, a strictly-positive flip" — wrong twice. A retained scope word can complete a *discovered* set's name: onepiece "How many Sweet Commanders are in the Marines?" now routes to roster and serves the discovered "Marine Commanders" (6 members, exact; not declared in `series/onepiece/overrides.yaml`; the pre-fix G1-stripped probe resolved `matched=False`/weak → qa). Not declared-only, not strictly-positive; it serves the *wrong* set. A's "no new failure class opens" and D's "false-roster is guarded" both rest on the declared-side guard, unchecked for the discovered path.

**3. All five missed:** this discovery-side false-roster is **live, not theoretical**, and **uncovered by the four gates** (no onepiece count gold rows; the R5 re-sweep covers only CSM queue rows). B's "gates are the tripwire" and E's "re-sweep surfaces it" both tripwire a case their tripwires can't see. Consider amending SHIP: add an onepiece discovery-counting pin (Marines stays qa or accepted), stamp the db flip + this case as halt-meter rows, correct "9"→"11".

## Verification ledger (every claim re-checked on disk this run)
- Diff: `git diff scriptengine/retrieve/router.py` = one hunk in `_resolves_a_set` + docstring; counting probe = `_COUNT.sub` (keeps prepositional phrase), G1 `_SCOPE_PHRASE.sub` stays on the non-counting branch (router.py:869-878). Sole caller: `has_set` probe (router.py:551-553). R1-d gate unchanged (router.py:883-884).
- how-many declared-phrase audit: **11** across 5 series (csm×2, db×1, jjk×5 @855/881/911, opm×1, onepiece×2), each with a shorter sibling in the same `match:` list — so A/C/D's "9" is a miscount of jjk (line 911 holds 3).
- Live probe (model-free, `route()`/`build_roster` over onepiece store): "How many Sweet Commanders are in the Marines?" → **roster**, basis "Marine Commanders" (discovered, conf exact, 6 members incl. "Shepherd (Non-Canon)"). Same query with the old G1-stripped probe → `matched=False`, conf **weak** → qa. "Marine Commanders" is **not** declared in onepiece overrides.
- csm "How many special divisions are in Tokyo?" also flips qa→roster post-fix (a second delta beyond the probe table's "db is the only other delta").
- Queue rows csm-set-14 / csm-set-15 / red-R-1 all `status: open`, `fix_class: R-1`. `git status --porcelain` shows **no staged files**; only `router.py` (M) + the new test (??) are this run's writes.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Reviewer run only: read the five adv_*.md, re-verified every load-bearing on-disk claim (router.py hunk, roster.py confidence logic, 11 how-many declared phrases, queue rows, receipt), ran 4 model-free probes; wrote only the assigned review file. No code/test edits, no scope widening."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Full verification ledger in the file: file:line cites for the diff/gate/caller graph, the 9-vs-11 miscount proof, and a live reproduction of the uncovered failure mode (onepiece 'Sweet Commanders in the Marines' -> roster/'Marine Commanders' exact, vs pre-fix weak->qa), plus the no-staged-files check."
    }
  ],
  "changedFiles": [
    "reports/csm/receipts/council_r1_router/review_1.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git diff scriptengine/retrieve/router.py",
      "result": "passed",
      "summary": "one hunk in _resolves_a_set + docstring; counting probe uses _COUNT, G1 strip unchanged on non-counting branch"
    },
    {
      "command": "grep -n 'how many' series/*/overrides.yaml (match lines)",
      "result": "passed",
      "summary": "11 declared how-many phrases (csm2/db1/jjk5/opm1/onepiece2), all with shorter siblings; refutes the receipt's '9'"
    },
    {
      "command": "python -c route()/build_roster over onepiece store (model-free)",
      "result": "passed",
      "summary": "'How many Sweet Commanders are in the Marines?' -> roster, discovered 'Marine Commanders' exact (6 members); old G1-stripped probe -> matched=False/weak -> qa. New false-roster confirmed live."
    },
    {
      "command": "grep queue rows + git status --porcelain staged check",
      "result": "passed",
      "summary": "csm-set-14/15 + red-R-1 open/R-1; no staged files (only router.py M + new test ??)"
    }
  ],
  "validationOutput": [
    "onepiece probe: 'How many Sweet Commanders are in the Marines?' -> roster | asks how many, which wants the set | basis: Marine Commanders | conf: exact | members: [Donquixote Rosinante, Glove, Governor, Hibari, Ripper, Shepherd (Non-Canon)]",
    "old (G1-stripped) probe 'How many Sweet Commanders are  ?' -> matched: False | conf: weak | basis: Big Mom Pirates",
    "csm 'How many special divisions are in Tokyo?' -> roster (second delta outside the probe table)"
  ],
  "residualRisks": [
    "Draft's counting probe (retained scope) can exact-match a *discovered* set whose name the scope word completes, serving the wrong set (onepiece Marine Commanders) — a false-roster the 11 tests, the 9-row probe table, and all four standing gates do not cover (no onepiece count gold rows; R5 re-sweep covers only CSM queue rows).",
    "Receipt '9 across 5 series' is a miscount (actual 11); B's proposed receipt correction should land before commit.",
    "db qa->roster flip is not stamped in the halt meter (miss queue), so the class re-sweep never proves that win (E's point)."
  ],
  "noStagedFiles": true,
  "diffSummary": "No engine diff authored by this reviewer. Judged the R-1 draft (+23/-1 router hunk + 11-test file): the two sub-bug fixes are real and the declared-side guard holds, but the retained-scope counting probe opens a live, untested discovery-side false-roster.",
  "reviewFindings": [
    "blocker: scriptengine/retrieve/router.py:869-878 — retained-scope counting probe exact-matches discovered sets the scope word completes (onepiece 'Sweet Commanders in the Marines' -> 'Marine Commanders', wrong set); uncovered by tests/probe/four gates; council should AMEND (add onepiece discovery-counting pin + halt-meter row) or SHIP with that explicit residual accepted."
  ],
  "manualNotes": "My weighting was 'new false-roster/false-qa the 11 tests + probe table do not cover'; that is exactly what the onepiece probe surfaced. Strongest response B (named the surface, correct audit); biggest blind spot C (declared-only/strictly-positive mis-scoping); all five missed that the discovery-side case is live and gate-uncovered."
}
```
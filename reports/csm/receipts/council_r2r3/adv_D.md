**R-2 — SHIP.** Verified in code: re-admission is tail-only — `deduplicated[:top_k-n] + recovered`, the beam never grows past `top_k`, only trailing budget slots are replaced, so no top-crowding mode. The guard is inert for writer questions (<3 content words); the 0.8 threshold is cross-wiki and is fully gated by eval 31/31 + the ≥390/400 probe. The level-0 floor is a single-consumer change: `passages_for_subject` is read only by `context.py:409` (the /context floor) and tests; `_cap_sections` caps the card at ≤1 new passage per subject (unique breadcrumb). `result.dropped` is consumed by tests only. Red-list Ruling 2: the debt is the bundle leg, not a wiki shape — right fix class.

**R-3 — AMEND (one pre-gate hygiene line).** No-op claim verified: only csm declares the three fields (all 8 wikis do declare `ability_sections`, so the blanket restriction was rightly rejected); M1 inert at default; M2/M3 byte-identical when undeclared — the `scoped` fold guard sits inside the pre-existing `if asked & {TECHNIQUE, TRANSFORMATION}` guard, so there is no vacuous-`all()` edge for item/trait-only questions. Consumers: /context, the router probe (same code path, coherent), the eval harness; the G4 relations door never touches `names`/`closed_members` — no M1 interaction. Residuals (3/5/5 intruders) are within-group per-character splits, un-mechanizable without encoding bank gold — bank curation is the right call. **Amendment: `scriptengine/retrieve/roster.py` line 2421** — the draft flipped the file's only LF line to CRLF, creating a +1/−1 no-op hunk (plain diff +127/−9 vs +126/−8 under `--ignore-cr-at-eol`). Restore that line to LF pre-commit; no logic or test change. Sweep-scope correction (B's procedure, not code): the R-3 re-sweep must include **csmdoor-01** (R-3-stamped in the queue; documented 31/88 budget floor; expected invariant — regression = new miss = halt); the receipt's sweep list omits it.

**Sequence to commit (one-copy 150k):** EOL fix → `:8000` down → gate 1 `pytest tests/ -q` = 1,303 collected (1,301+2xp; 1,283+7+13, confirmed by collect-only) → gate 2 eval jjk 31/31 → `:8000` CPU → gate 3 span-recall 48,572/48,572 + probe ≥390/400 → gate 4 canon opm 10/16, 236/236, 79.0% (any drop outside opm-set-16 = revert + halt) → B re-sweeps all stamped rows (R-2: csm-fact-06, red-R-2, the 13 dual-stamped; R-3: set-17/02/01, char-03, csmdoor-01, red-R-3; expected own HITs set-17/set-01/char-02, ≥1 or halt) → selective commit of both drafts + receipts as ONE commit. Gate failure: infra flake → re-run the leg; single-draft regression → stash that draft's files, re-run the failed leg, ship the other; combination-only break → halt to council. Nothing commits until all four gates + both re-sweeps are green.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Read-only council run: zero code/file edits (git status unchanged, 25 pre-existing entries, 0 staged); verdicts grounded in the on-disk diffs, queue rows, red list, gate ledgers and re-run tests, scope not widened."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "All load-bearing claims re-verified on disk: R-2/R-3 diffs read in full; passages_for_subject consumers (context.py:409 + tests); series overrides (new fields only in csm; all 8 declare ability_sections); queue stamps (13 R-4/R-2 rows, csmdoor-01 R-3 open, set-14/15 closed); R-1 baseline 1,283 from aef6707; 1,303 collected confirmed by collect-only; 40 passed + 2 xpassed in 3.71s on the three new/changed test files; CRLF no-op hunk located at roster.py:2421 (plain +127/-9 vs +126/-8 ignore-cr-at-eol)."
    }
  ],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git diff (hybrid.py, facts.py, roster.py, overrides.yaml, test files)",
      "result": "passed",
      "summary": "diffs match the draft descriptions; one no-op EOL hunk found (roster.py:2421, LF->CRLF)"
    },
    {
      "command": "scriptengine/.venv/bin/python -m pytest tests/test_retrieve.py tests/test_csm_fixtures.py tests/test_csm_roster_scoping.py -q",
      "result": "passed",
      "summary": "40 passed, 2 xpassed in 3.71s (the 2 xp = G-CSM-1 debt xfails)"
    },
    {
      "command": "scriptengine/.venv/bin/python -m pytest tests/ --collect-only -q",
      "result": "passed",
      "summary": "1303 tests collected = 1,283 (R-1 baseline, aef6707) + 7 (R-2) + 13 (R-3), matching the shared-constraint gate expectation"
    },
    {
      "command": "queue/overrides/neighbor greps + git show aef6707 + python queue parse",
      "result": "passed",
      "summary": "fix_class stamps, closed rows, series-field declarations, consumer sets, R-1 gate package all confirmed"
    }
  ],
  "validationOutput": [
    "pytest subset: 40 passed, 2 xpassed in 3.71s",
    "collect-only: 1303 tests collected in 0.96s",
    "git diff --cached --stat: empty (no staged files)",
    "roster.py EOL: HEAD 4585/4586 CRLF (1 LF line at 2368); working tree 4704/4704 CRLF; --ignore-cr-at-eol diff = +126/-8"
  ],
  "residualRisks": [
    "csmdoor-01 omitted from the R-3 receipt's re-sweep list - B must add it (expect 31/88 invariant; regression halts)",
    "roster.py:2421 CRLF no-op hunk must be reverted to LF before the commit so the diff is logic-only",
    "level-0 floor change is cross-wiki; JJK safety rests on the four gates (eval, span-recall 48,572 + 400-probe, canon opm)"
  ],
  "noStagedFiles": true,
  "diffSummary": "No edits made (read-only executor). On-disk: R-2 = hybrid.py +38 (tail re-admission + _query_covered), facts.py +3/-1 (level-0 floor), tests +145; R-3 = roster.py +127/-9 (3 opt-in knobs), series/csm/overrides.yaml +29, new 13-test file.",
  "reviewFindings": [
    "blocker: none - R-3 ships after the one-line EOL restore at roster.py:2421 (pre-gate, zero logic impact)",
    "note: R-3 re-sweep scope must cover all R-3-stamped rows including csmdoor-01"
  ],
  "manualNotes": "Verdicts: R-2 SHIP, R-3 AMEND (EOL line only). Gate sequence and failure semantics in the body; nothing commits until all four gates + both class re-sweeps are green."
}
```

VERDICT R-2: SHIP
VERDICT R-3: AMEND (restore LF at roster.py:2421 pre-gate; no logic/test change; add csmdoor-01 to the R-3 re-sweep)
FIRST STEP AFTER VERDICT: B strips the trailing CR from scriptengine/retrieve/roster.py line 2421, confirms `git diff --stat` shows roster.py at +126/-8, then starts the one-copy gate sequence with :8000 down
CHANGE-OF-MIND IF: any gate leg misses baseline (pytest failure, eval <31/31, probe <390/400, or a canon drop outside opm-set-16 flips R-3 to REJECT; a JJK span-recall or floor regression flips R-2), the re-sweep yields 0 own-new-row HITs or any new miss on a stamped row (incl. csmdoor-01), or a JJK invariance pin fails
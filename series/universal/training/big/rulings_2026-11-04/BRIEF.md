# Rulings pass 2026-11-04 — agent brief

You apply the 2026-11-04 rulings to one candidate list of windows. Tools run from the worktree
`/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags`; your files go in this directory
(`/home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/`).

## Read first (in this order)
1. `plan/review_tools/gold27_system.md` — the whole file; binding: "Owner ruling 2026-11-03" (decide every outcome
   row from the factual state the passage establishes; one act can carry several true rows; write all the text
   supports and none it does not) and "Rulings 2026-11-04" (the open questions, now decided).
2. `plan/BIG_REVIEW_PATTERNS.md` — the A-table at the top (A2, A8, A11, A53, A74, A75, A113, A116, A145 ...).
3. `series/universal/training/big/outcome/SUMMARY.md` — "Decision rules applied" (same rules, big set).

## Your list
`list_<NAME>.txt`: one line per window, `b<n> CLASS: hint ; CLASS: hint`. `# group ...` lines join big overlap
partners: partners share sentences and must be edited identically (same rows for the shared sentences). A `PARTNER`
line is listed only as a partner. Classes are heuristic hits: READ each window; many need no change.

- CAPT   fought + captured/sealed for a pair, no defeated -> ruling "CAPTURED / SEALED AS OUTCOMES".
- STOP   `X|other_verb|stopped/prevented/foiled/thwarted/...` actual. A completed stop of a NAMED person or of a named
         person's plot/crime is the event `X|defeated|Villain` (2026-10-14 ruling) and the other_verb fact goes (`f-`).
         Keep the fact when the stop is of a thing/disaster with no named villain, of an ally, of a self-harm, or inside
         an ongoing exchange; a purpose clause ("went to stop him") is `planned` (fix modality with f- + f+ if actual).
- FW     a stated wound inside a fought row's quote (shot, stabbed, severed, impaled, set on fire ...) with no wounded
         fact -> `f+ Attacker|wounded|Victim|quote`; `defeated` too only when nothing continues (Klaue test); A145
         drops `fought` only when fight and outcome are one stated act.
- WBY    `Victim|wounded|-` where the sentence names the doer -> `f- Victim|wounded|-` + `f+ Doer|wounded|Victim|quote`.
- ESC    defeated row whose quote says the beaten side fled/retreated/went into hiding, no escaped row ->
         `+ Beaten|escaped|Winner|quote` (A74).
- TEAM   team-up outcome credited to one doer -> the partner named in the same clause gets the same outcome row.
- NEAR   `X|other_verb|V` stated from a "nearly/almost V" quote -> certainty denied (`f-` + `f+ ...|actual|denied|`).
- PATIENT patient written as subject ("X was attacked by Y" as X|attacked|Y) -> reverse the roles.
- LISTED a window named in an open ruling; the hint names which. Decide it by the 2026-11-04 rulings.
Fix what the class or ruling concerns, plus a plain error in the same rows (reversed row, a row contradicting a
ruling). Do not restyle rows that are fine.

## View
- gold: `BV2_SET=gold bash plan/review_tools/pre27.sh show B [B ...]` (full rows; ignore the old "27B" answer)
- big:  `SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine /home/goblin/ScriptEngine/scriptengine/.venv/bin/python plan/review_tools/outcome_scan_big.py show B [B ...]`

## Fix files
```
@<b> rulings 2026-11-04: <reason, citing the ruling>
keep
r Old=>New
- S|verb|O
+ S|verb|O|quote
f- S|rel|O
f+ S|rel|O|quote|modality|certainty|asserted_by     (omit the last three for actual/stated/none)
t- tag|quote-prefix
t+ tag|quote
```
`defeated`/`saved`/`killed`/`escaped`/`captured`/`sealed` are EVENTS (`+`), never `f+`. Removals use the exact strings
shown in the rows. Quotes: verbatim window text, >=12 chars, no `|`. Files: `<NAME>_01.txt`, `<NAME>_02.txt`, ...
(at most ~15 windows each). A window needing no change gets NO block (note it in your notes).

## Submit — `rv.sh fix` is NOT idempotent (every run appends records)
Per file, in order:
1. dry run until 0 refused and no unmatched removal:
   gold `bash plan/review_tools/outcome_scan_gold.sh check FILE`;
   big `SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine /home/goblin/ScriptEngine/scriptengine/.venv/bin/python plan/review_tools/outcome_scan_big.py check FILE`
2. never submit a file already in `ledger_<NAME>.txt`;
3. submit ONCE, under the shared lock (three agents append to the same big audit file):
   gold `flock /home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/.submit.lock env BV2_SET=gold bash plan/review_tools/rv.sh fix FILE`;
   big `flock /home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/.submit.lock bash plan/review_tools/rv.sh fix FILE`;
4. immediately append `FILE  b... (applied N)` to `ledger_<NAME>.txt`.
If restarted, read your ledger and notes first and continue after the last submitted file.

## Notes
`notes_<NAME>.md`, updated after every file: per window `b<n> CLASS changed|no change: why`; a section "For the
owner" (cases the rulings do not settle: leave them unchanged, do not guess); "Counts" per class (read / changed /
no change). Final message: counts, files, owner questions, new patterns.

## Do not
- use the GPU or start a model server; edit code, docs or the catalog; commit; run `rv.sh mark`; touch a window
  outside your list; edit gold b825 b893 b1014 b3543 b3657 (waiting for an owner decision on the fact gate);
- kill processes by pattern (`pgrep -f` / `pkill -f`).
You may be stopped at any time (usage limit): keep ledger and notes current so a successor can resume.

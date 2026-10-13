# RESUME HANDOFF — big review v2 forward pass (written 2026-10-13)

For a NEW Claude session. This supersedes nothing in `plan/RESUME_REVIEW_HANDOFF_2026-10-10.md`: read that
first for the binding owner rules (§1 there), then this file, then `plan/BIG_REVIEW_PATTERNS.md` (all of it,
especially the 2026-10-12/13 FIXED / RULE CHECK / MEASURED notes at the end) and `plan/WINDOW_METHOD.md`.

Branch `big-review-flags`, worktree `/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags`.
Data lives in the MAIN checkout (gitignored): `/home/goblin/ScriptEngine/series/universal/training/big/`
(`labels_v2.jsonl`, `big_audit_v2.jsonl`, `review_cursor_v2.txt`); each commit also copies those three
files into the worktree with `git add -f`.

## 1. The owner's standing instructions (verbatim, latest first)

- "Free the GPU you are not using it, then continue" — done 2026-10-13: the 27B Qwen (`ninfer-serve`
  :18080) was unloaded with `/home/goblin/ninfer-work/ninfer-stop.sh` (mode=off, no auto-restart).
  Review needs no model. Restart only if needed: `bash /home/goblin/ninfer-work/qwen-switch.sh <ctx>`.
- "Then continue reviewing further, and update the catalog as you encounter new problems, check if you
  are rejecting events/facts based on prior rules and adapt for future as well, each rule will need to be
  checked that it is not violating some part, like the Po name was said to be too short but it was
  actually a name. similarly some characters could have different name as the story progresses. Use 27B
  for this research work, you continue reviewing the windows."
- "Continue inline, no subagents." → **no subagents.**
- Original task: continue the v2 forward pass (events + facts + tags per window). "Keep fixing gate rules
  that reject events/facts for wrong reasons, but measure every new rule or flag on the approved windows
  before adding it, and note it in the catalog." Rulings: A106 = ordinary sleep only (regaining
  consciousness IS awakened; a centuries-long magical dormancy is not ordinary sleep); write
  "Avengers, Inc." as "Avengers Inc." in ends. `tools/train/label_single.py` carries an uncommitted
  owner hunk (opencode CACHE_BREAKPOINT): **never stage it — stage only your own hunks** (recipe §4).
  `plan/FACT_LAYER_PROGRESS.md` is also the owner's uncommitted file: leave it. Never push.
  If near the session limit: stop, wait for the reset, continue.

## 2. State at handoff

- Review cursor **9245** (last reviewed window b9245, New Mutants Earth-616 "Gifted Youngsters").
  Next view: `bash plan/review_tools/rv.sh view 10 --from 9245` (`--from` is EXCLUSIVE: it prints b9246…).
- Last commit `337c2ca9` (all edits through b9245 committed). Working tree: only the owner's two files dirty.
- This session reviewed b8165 → b9245. Windows still to go: b9246 … b14000.
- Known follow-ups on arrival: unreviewed b10889 / b12584 / b13350 carry split "D.C." arrival rows (the
  base rows predate the Washington, D.C. gate fix) → re-point them to "Washington, D.C.".

## 3. Tools (copies in `plan/review_tools/`, because the job temp dirs die with the session)

- `rv.sh view N --from B` | `rv.sh fix FILE` | `rv.sh mark B` — wraps `tools/train/big_review_v2.py`.
  Pipe `fix` output through `grep -v "^FIXED"`; anything left is a problem:
  - `REFUSED b… : …` → the whole block was rejected; fix the rows and resubmit just that block (with its
    `@` header). "kept 15/13" with no named row means the gate SPLIT a row (comma list split).
  - `UNMATCHED b…: - …` (new 2026-10-13) → a `-`/`f-`/`t-` line removed nothing (often because an `r`
    rename does not touch possessive ends like "Toomes' lair"); write the removal against the real end.
- Edit-file format (one block per window):
  ```
  @<b> why
  keep                      (keep the current rows; omit only to replace everything)
  r Old=>New                (renames exact ends in events+facts; right after keep)
  - S|verb|O                (O "-" = none)        + S|verb|O|quote
  f- S|rel|O                (removes all matches)  f+ S|rel|O|quote[|modality|certainty|asserted_by]
  t- tag|quote-prefix       t+ tag|quote
  ```
  Quotes must be verbatim window text, ≥12 chars (shorter only if a whole list line/sentence naming an end),
  and may NOT contain "|" (the parser splits). For windows with raw `[[Page (Earth-616)|Name]]` markup use a
  pipe-free stretch such as `abducted by the mercenaries [[Anthony Masters (Earth-616)`.
  `asserted_by` "-" now means none; non-actual modality needs a named asserter (B.4).
- `recover2.py` (re-gate labeller-dropped rows into UNVIEWED windows, backs up labels_v2 first),
  `regate.py "<reason substring>"`, `acc_list.py` — research helpers for the 27B audit; outputs of that
  audit are in `series/universal/training/big/audit_27b_2026-10-13/` (main checkout).
- Tests: `/home/goblin/ScriptEngine/scriptengine/.venv/bin/python -m pytest tests/test_fact_layer.py -q`
  (62 pass at handoff).

## 4. Commit recipe

```bash
B=/home/goblin/ScriptEngine/series/universal/training/big
bash plan/review_tools/rv.sh mark <last b>
cp $B/big_audit_v2.jsonl $B/labels_v2.jsonl $B/review_cursor_v2.txt series/universal/training/big/
git add -f series/universal/training/big/{big_audit_v2.jsonl,labels_v2.jsonl,review_cursor_v2.txt}
git add <your own files only>
git commit -m "big review v2: bA-bB (pages)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
For `tools/train/label_single.py` changes: build the staged blob from `git show HEAD:tools/train/label_single.py`
plus your patch, `git hash-object -w`, `git update-index --cacheinfo 100644,<hash>,tools/train/label_single.py`;
check afterwards that `git diff tools/train/label_single.py` shows only the owner's CACHE_BREAKPOINT hunk.
`label_single` deliberately imports `draft_v2` from the MAIN checkout (gate identical to the live run): put
gate changes in label_single (this branch), not in draft_v2.

## 5. Review conventions in force (short list; the catalog is authoritative)

One name per person per window: the real name when the window gives it (A4), codenames/titles/mantles as
`Codename|alias_of|Real` (A143; never `became`, never `also_known_as`/`codename_of`); possession of another
body (Otto as Spider-Man) → rows on the inhabitant. learned/discovered/revealed/suspected → object `-`.
contacted = remote only. Recruiting/joining/rejoining/forming a team is no `met` (R4); "reunited with" IS met.
One act → one event: fight+defeat → defeated; fight+kill → killed; ambush+kidnap → captured; a meeting that
is the fight → drop the met. Orders: `X|ordered|Y` fact, the ordered act gets `|ordered|stated|X`. Attempts →
the attempted verb with `|attempted|stated|S` (never other_verb "tried"/"attempted"). Mind control/possession
→ other_verb fact on the controller, no fight (A116). Apparent death → `dies|-|…|actual|apparent`. Revival
for the revived's sake → `<reviver> saved` + `awakened`; a secondary mutation/spider bite → gained_power, not
awakened. Unnamed people/crowds/races/"the girl"/"the mayor" are no ends (race OK as object of
member_of/leader_of/revealed_as/transformed_into). Places/things/countries/companies are no doers;
organisations are no places (A65). A ship/vehicle is no place (A24); "the X" ends → "X". Description places
(lairs, graves, "prison") dropped. `gave` takes the recipient. Possessive before a thing object is fine.
Overlapping windows must agree. Production/continuity notes → production tags.

## 6. Rule fixes this session (all measured on approved rows, tested, catalogued)

Earlier in the session (b8165-b8794): A101 flag skips doer-less passives; `-`/none object = no object;
Agent-number codenames restored; LIST_END refusal for comma-list person ends; whole short list lines pass the
12-char floor; possessive before place/item/thing objects is no bare pronoun; 27B audit stages 2-4 with
~170 recovered rows hand-added and recoveries 2 and 3 into unviewed windows.
Since b8795:
- Citation templates `{{r|…}}` no longer feed name flags (17 false flags removed, none lost).
- `Washington, D.C.` stays one place in the event gate (comma before a two-letter initialism; 13 split rows
  in big v2; "Hydra, A.I.M." still splits).
- R4 "met from joining" no longer fires on "reunited with" (131 of 266 approved flags were false).
- "Description/garbage end" no longer fires on short capitalised names (MJ, Ox, Wu, Li, M: 26/26 kept).
- `rv fix` reports UNMATCHED removals; `asserted_by "-"` parses as none.
- Measured, not changed: raw wiki-link windows (16 windows, 11 recoverable rows → fix by hand on arrival).
- Rule checks kept as flags only: rank prefix ("Dr. Steve", "Emperor Yan" are names), A106 dormancy.

## 7. Report owed to the owner at the very end of the pass

Windows reviewed (this session b8165→cursor), the rule fixes with their measurements (§6), the 27B audit
findings (stage 2: 401 judged, most "wrong refusals" were prompt artifacts; stage 3: 9-10 alias rows added;
stage 4: ~160 accepts hand-added, 27B precision ~50%), recovery status, commits; end with a `result:` line.

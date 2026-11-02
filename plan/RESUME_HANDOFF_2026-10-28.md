# RESUME HANDOFF — 2026-10-28 (terminal Claude session)

Read first: `plan/RESUME_HANDOFF_2026-10-14b.md` (owner decisions, method), `plan/RESUME_REVIEW_HANDOFF_2026-10-10.md` §1
(binding rules), `plan/BIG_REVIEW_PATTERNS.md` (catalog; the 2026-10-28 block at the end), `plan/BIG_REVIEW_HANDOFF.md` §4.

## Where we are

| stage | state |
|---|---|
| 14,000 big Marvel/MCU windows: 35B v2 labels (events+facts+tags) | done |
| Claude review of all 14,000 (review_cursor_v2 = 14000) | done |
| overlap reconciliation | done; `recon.sh check all` = only logged exceptions (recon/exceptions.txt) |
| lint rule-fixes M1-M6 | applied |
| lint reading list (work_all.txt, 1,655 windows) | **DONE 2026-10-28** (fix files L001-L181; commit ad6476b5 + this) |
| gold v2 (3,822 gold windows; 35B added facts+tags, gold events kept) | labels done + mechanical lint; **Claude review: 0 / 3,822** |
| compose events+facts+tags, train 9B, score | not started (blocked on gold review) |

## Running now

- 27B (ninfer, :18080, 100k mode; started this session after a SWITCHPOINT entry) pre-reviewing ALL gold windows:
  `BV2_SET=gold pre27.sh run big/gold_v2/gold_all.txt --workers 3`, answers in `big/gold_v2/pre27/b<n>.txt`, log
  `big/gold_v2/pre27_run.log`. Throughput ~1-2 windows/min -> ~30-60 h for all 3,822. It skips windows already answered,
  so it can be restarted with the same command. Stop by exact PID (`ps -eo pid,cmd | grep "pre27.py run"`).
  Prompt: `plan/review_tools/gold27_system.md` (fixed this session: wounded rule, legal tags, 2026-10-28 rulings).

## Next session: the gold review

- Read answered windows: `BV2_SET=gold bash plan/review_tools/pre27.sh next big/gold_v2/gold_all.txt 8`
  (or `show B ...` for windows without an answer). Gold windows come from many series (berserk, jjk, csm, opm, ...).
- Write decisions as fix blocks (same format as the lint pass; every gold window needs a record, so an accepted window
  still gets `@B gold: ok` + `keep`) and submit with `BV2_SET=gold bash plan/review_tools/rv.sh fix FILE`.
  Check the env routes writes to `big/gold_v2/gold_audit_v2.jsonl` before the first submit.
- Gold events may change: the owner accepted that; re-score the old teacher on the revised test (ship bar .602).
- Then lint the gold set (`BV2_SET=gold lint.sh`), compose (`compose_big_set.py` v2: events+facts+tags, 30% empty,
  `--short-system`), extend the scorer for facts/tags, train Qwen3.5-9B seeds 1+2 (BIG_REVIEW_HANDOFF §4).
- Commit data the same way: copy `big_audit_v2.jsonl`/gold audit + fix files into the worktree, `git add -f`, explicit pathspecs.

## Update 2026-10-28 (later): gold review at b1059/3822

- Gold fix files G001-G109 in `big/gold_v2/fixes/` (committed through 9ab81464). Reviewed: b1-b1059.
- The 27B runner was restarted twice; it now runs `pre27.sh run big/gold_v2/gold_rest1150.txt --workers 3`
  (PID 246063 at the time of writing; list = b1150 onward). For b1060-b1149 there are no 27B answers: review them
  directly with `BV2_SET=gold bash plan/review_tools/pre27.sh show 1060 1061 ...` (from the worktree; the script sets
  SCRIPTENGINE_ROOT; launching pre27.py by hand without it fails on gold_in.jsonl).
- Fix-file headers are `@<b> gold: reason` (no "B" prefix). Long list windows: generate one tag per line from
  `gold_in.jsonl` (messages[1].content after "Passage:\n").
- New rulings are appended to `plan/review_tools/gold27_system.md` (sections "Rulings from the gold review"); key ones:
  production = interviews/design notes/adaptation comparisons (manga vs anime, filler, edits, dubs)/game content/
  credits/episode+chapter title lines/story-role lines/etymology; unnamed or species-noun individuals are no ends;
  saved/defeated are event-only; negation = certainty denied; speech acts actual; orders/asks carry the ordered act;
  cutting/slicing to pieces, restraining, knocking out = defeated; in-person calls are never `contacted`;
  "Devil embodies X" = other_verb embodies; the gate refuses "Kami" as a species end.

## Update 2026-11-02: gold review at 1,846 / 3,822 (48.3%) — stopped by the owner, resume later

Two Opus 5.5 (high) subagents reviewed in parallel, reading windows directly (no GPU, no model server; ninfer was
busy with the owner's work; there are no 27B answers for b1060+). Owner stopped both mid-run; neither committed or ran `mark`.

Audit coverage (`big/gold_v2/gold_audit_v2.jsonl`, unique `b`, counted from disk 2026-11-02):

| range | state |
|---|---|
| b1-b1059 | reviewed (G001-G109, committed through 369e8bbd) |
| b1060-b1402 | reviewed 2026-11-02, fix files G110-G129 (UNCOMMITTED) |
| b1403-b2441 | NOT reviewed (the lower agent's remainder) |
| b2442-b2885 | reviewed 2026-11-02, fix files G500-G528 (UNCOMMITTED) |
| b2886-b3822 | NOT reviewed (the upper agent's remainder) |

Remaining: 1,976 windows (b1403-b2441 = 1,039; b2886-b3822 = 937). Agents were stopped, so the last submitted fix
file of each may have been cut off mid-write: before resuming, re-derive the true cursor from the audit file (the
gaps above), and spot-check G129 / G528 against the audit. A window with no audit record is simply reviewed again.

To resume: same method as the section above (`BV2_SET=gold bash plan/review_tools/pre27.sh show B...`, fix blocks
`@<b> gold: reason` + `keep`/edits, submit with `rv.sh fix`, never `mark`). Number new fix files from G130 (lower
range) and G529 (upper range) to keep the two streams apart. Commit the new fix files + audit copy with explicit
pathspecs and `git add -f` (data is gitignored), as for earlier batches. New rulings noticed by the agents were not
collected (they were stopped before reporting); skim G110-G129 / G500-G528 for any new `gold:` reasons that look like
rules and add them to `plan/review_tools/gold27_system.md`.

## Update 2026-11-02 (evening): gold review at 2,902 / 3,822 (75.9%) — stopped at the 5-hour limit (owner: do not use credits)

Four Opus 5.5 (high) agents ran in parallel (no GPU), stopped by exact task at ~96% of the 5-hour window. Reviewed so far:
b1-b1618, b1922-b2078, b2442-b3252, b3355-b3670 (fix files G110-G139, G200-G205, G500-G548, G700-G718).
Still unreviewed (920 windows, from the audit-file gaps): **b1619-b1921 (303), b2079-b2441 (363), b3253-b3354 (102),
b3671-b3822 (152)**. The last fix file of each agent may be cut off: re-derive gaps from the audit file before resuming
(a window with no audit record is simply reviewed again). Next fix numbers: G140+, G206+, G549+, G719+ (any unused).
Same method/rules as the sections above; commit with explicit pathspecs and `git add -f`.

## Update 2026-11-03: gold review at 3,763 / 3,822 (98.5%) — only 59 windows left

Four Opus 5.5 (high) agents ran after the 5-hour reset (no GPU); the two unfinished ones were stopped at 96% of the
window (no credits). Fix files this run: G140-G159, G206-G218, G549-G567, G719-G729.
**Still unreviewed (59): b1841-b1849 (9) and b2187-b2236 (50).** Re-derive from the audit-file gaps first (the last
fix file of a stopped agent may be cut off). Fix numbers free: G160+, G219+.
Next after those 59: lint the gold set (`BV2_SET=gold lint.sh`), compose (`compose_big_set.py` v2, 30% empty,
`--short-system`), extend the scorer for facts/tags, re-score the old teacher on the revised test (ship bar .602), train 9B.
Open rulings noticed by agents (decide + add to `gold27_system.md` / catalog; not yet written): vehicles/ships are not
places (A24: Sanctuary II, Q-Ship, train -> other_verb facts); page-title subjects/ends not in the window text are dropped
(deictic/crowd_end tags instead); dialogue/quote-page rows removed; infobox tags must be pipe-free, one per field,
fields <12 chars untagged; possessive descriptions ("her father") as ends -> crowd_end; simulated events dropped (A107);
body destroyed while owner survives = defeated (A53); restraining allies is not a fight; lower-case "the king" for a
page-subject monarch (b3350 vs b3594) — needs an owner/Claude decision; codename->real-name without an alias row when
no sentence ties them (inconsistent across fix files — reconcile); "Voiced by Medusa" (b3811) is in-universe speech;
symmetric `fought` dedupe silently drops the reverse row (b3346); the tag gate refuses 2-char kanji list tags (b3696).

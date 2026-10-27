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

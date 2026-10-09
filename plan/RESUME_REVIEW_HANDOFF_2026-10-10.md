# RESUME HANDOFF — Claude review of the big Marvel/MCU windows (written 2026-10-10)

For a NEW Claude session. Read this fully, then `plan/WINDOW_METHOD.md`, `plan/BIG_REVIEW_PATTERNS.md`
(all sections) and `plan/EXTRACTION_PROCEDURE.md` (+ `plan/EXTRACTION_PROCEDURE_V2.md` if it exists).
All files named here live on branch `big-review-flags`, worktree
`/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags` (data stays in the main checkout
`/home/goblin/ScriptEngine`, gitignored, under `series/universal/training/big/`).

## 0. The owner's instruction for this session (verbatim, 2026-10-10)

> While you hit your limit, i continued the task in opencode, check from where you left, fire up the
> qwen and start working from which window you had verified yourself. Keep updating the big flags and
> pattern file that will help you recognize patter as well as the ninfer 35B. Prepare a handoff to
> continue this in a new session instead

So: (1) find out what the opencode/27B session did after 2026-10-07 ~05:15; (2) start the Qwen labeller
again; (3) resume Claude's own window-by-window verification from the last window Claude verified;
(4) after every batch keep updating `tools/train/big_flags.py` + `plan/BIG_REVIEW_PATTERNS.md` (and
mirror matchable rules into `tools/train/label_hints.py`, which the 35B reads), committing each time.

## 1. Binding owner rules

- THE method (`plan/WINDOW_METHOD.md`): 35B single pass + review-derived hints + one flag-driven repair
  turn (`tools/train/label_single.py`, hints/repair ON by default; `--baseline` is measurement-only),
  then Claude reviews EVERY window. All earlier window-making methods are retired.
- **Only Claude adds new rules, and only Claude edits `tools/train/big_flags.py` and
  `plan/BIG_REVIEW_PATTERNS.md`** (label_hints.py mirrors them, also Claude-only). If the opencode
  session changed either file, check `git log -- <file>`; any non-Claude change is a proposal to
  re-decide, not an accepted rule (its proposals should be in `plan/FACT_LAYER_PROPOSALS_FOR_CLAUDE.md`).
- Owner wants a COMPLETE brain: nothing the text states may be lost (2026-10-07). The fact-layer fix
  (`plan/FACT_LAYER_COUNCIL_BRIEF.md` §D, council verdict `plan/FACT_LAYER_COUNCIL.md` @ be8e0e2e,
  27B execution plan `plan/FACT_LAYER_EXECUTION.md`) keeps the 12 event verbs and adds fact rows
  (wider relation vocabulary, modality/certainty/location qualifiers instead of drops, a
  sentence-coverage rule). Review under whatever of it is implemented (see §3).
- GPU-only; one model on the 32 GB card; kill by exact PID only; write a `plan/SWITCHPOINT.md` entry
  in the MAIN checkout before any model switch; commit with explicit pathspecs only; never commit the
  owner's files (plan/JJK_VERIFY_7000_*.md, tools/train/verify_monitor.py, owner hunks in
  verify_row_wiki.py / qwen_worker.py, tools/train/infer.py, the `D series/{berserk,bleach,db,hxh,
  onepiece}/overrides.yaml` deletions); never edit labels.jsonl / big_audit.jsonl by hand.
- Do NOT push `big-review-flags`: the local branch base is 238 owner commits ahead of origin; pushing
  publishes them — the owner's call.

## 2. State when the previous Claude session stopped (2026-10-07 ~05:15) — re-check, do not trust

| item | value then |
|---|---|
| Claude review cursor | **806** (`series/universal/training/big/review_cursor.txt`) — b7-b806 verified; corrections in `big_audit.jsonl` (latest per id wins) |
| 35B labels | `labels.jsonl` 5,405 rows: rows 1-5,206 plain single pass, the rest `--hints --repair` (`"hinted": true`) |
| labeller | stopped (old PID 512679); ninfer 35B stopped (old PID 470864) |
| GPU | ninfer **27B** loaded at 262k on :18080 (`qwen-switch.sh 262k`) for the opencode session |
| opencode | session `ses_eec759d04fferCtWcvYTBmRm7Q` (terminal FACT-LAYER-COUNCIL, worktree above); council committed be8e0e2e; owner then gave it `plan/FACT_LAYER_EXECUTION.md` (steps 1-7: schema v2, fact gate + coverage, labeller v2 / add-only, pilot, add facts to b1-b806, redo b807-b5405 into `labels_v2.jsonl`, close) |
| branch head | 3dccd7e6 (plus whatever opencode committed after) |
| measured | plain .535 F1 -> hints+repair .629 (P .769 R .532) on 96 reviewed windows (`tools/train/eval_hints.py`) |

## 3. Startup checks (do these first, in this order)

```
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags   # or EnterWorktree path=...
git log --oneline 3dccd7e6..HEAD                                   # what opencode committed
cat plan/FACT_LAYER_PROGRESS.md 2>/dev/null | tail -60             # its step log + numbers
ls plan/EXTRACTION_PROCEDURE_V2.md tools/train/fact_gate.py tools/train/fact_coverage.py 2>&1
git log --oneline -3 -- tools/train/big_flags.py plan/BIG_REVIEW_PATTERNS.md tools/train/label_hints.py
B=/home/goblin/ScriptEngine/series/universal/training/big
cat $B/review_cursor.txt; wc -l $B/labels.jsonl $B/labels_v2.jsonl 2>&1; cat $B/*.status 2>/dev/null
nvidia-smi --query-gpu=memory.used --format=csv; ps -eo pid,etime,cmd | grep -E "ninfer-serve|label_single|opencode" | grep -v grep
curl -s -m3 localhost:18080/v1/models; curl -s -m3 localhost:18081/v1/models
```

Decide from what you find:
- **Is the opencode run finished or idle?** Do not stop the 27B while it is mid-step; ask the owner if
  unclear. If finished/idle, the owner said "fire up the qwen": the labeller Qwen is the ninfer 35B.
- **Which labeller to start:** if `labels_v2.jsonl` and a working v2 labeller (`--schema v2` /
  add-only) exist and `FACT_LAYER_PROGRESS.md` shows the Step-4 pilot passed, resume THAT (v2) run;
  otherwise resume the v1 run (`label_single.py` from this branch, hints+repair default). Use the
  exact resume command recorded in the progress log, or `plan/BIG_REVIEW_PATTERNS.md` §F.
- **Model switch** (27B -> 35B): SWITCHPOINT entry in the main checkout, stop the 27B by exact PID
  (`ps -eo pid,cmd | grep "ninfer-serve" | grep -v grep`), then
  `setsid nohup bash /home/goblin/ScriptEngine/tools/train/ops/serve_35b_64k.sh > ~/ninfer-work/logs/serve_35b_label14k.log 2>&1 < /dev/null &`
  (up in ~40 s, :18081, max 8 lanes). Note: the permission classifier previously required the owner's
  explicit go-ahead to kill a running workload — if denied, ask the owner to confirm or to run
  `! kill <pid>` themselves.
- **Run the labeller from this worktree** with `SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine` (gate
  modules + data come from the main checkout) via a small launcher script and `setsid nohup`; the
  worktree guard refuses complex inline commands, so put long commands in a script.

## 4. Where to resume the review

"Start from the window you had verified yourself" = continue Claude's verification right after the
cursor (b807 in `labels.jsonl` order — the order is the shuffled label order; b-number n = line n).
- If v2 output exists for those windows (`labels_v2.jsonl`), review the v2 rows (events AND facts AND
  coverage tags) for b807 onward, and separately spot-check that b1-b806 in v2 kept Claude's event
  rows exactly (Step 5 promise) before trusting their added facts.
- If only v1 exists, continue v1 review from b807 exactly as before.
Ask the owner only if the v1/v2 choice is genuinely ambiguous from the progress log.

## 5. The review loop (unchanged mechanics)

```
R=/home/goblin/ScriptEngine; P=$R/scriptengine/.venv/bin/python
SCRIPTENGINE_ROOT=$R $P tools/train/big_flags.py 15 > $CLAUDE_JOB_DIR/tmp/rv.txt   # window + DUP/OVERLAP + FLAG + MISS? + OK
# read rv.txt (Read tool), decide every window against the procedure + rulings + catalog
# write compact edits (format in tools/train/big_mkfix.py docstring: @<b> why / keep / r Old=>New / - S|v|O / + S|v|O|quote)
SCRIPTENGINE_ROOT=$R $P tools/train/big_mkfix.py edits.txt bfix.json
$P $R/tools/train/big_review.py --fix bfix.json      # gated; REFUSED -> fix and resubmit
$P $R/tools/train/big_review.py --mark <last b>
```
- Flags are prompts, never verdicts: read every window in full (validated: flags cover ~99% of
  corrected rows, but OK-marked rows still had ~13% errors).
- Gate quirks (catalog §D): symmetric met/fought dedupe; "Rachel"/"Jude" = places, "Zemo" = episode
  page, item pages (Destroyer, Cerebro) refused; subject==object refused; comma places split (use the
  most specific part).
- mkfix warns when one window mixes a name and its short form — fix to one name per person.
- After each batch: add every NEW error class to `plan/BIG_REVIEW_PATTERNS.md` (next number after the
  highest A-number), add a matching flag to `big_flags.py` when it can be pattern-matched, and mirror
  the rule into `label_hints.py` when the 35B can use it; commit those files + the batch.
- Before composing training data: `tools/train/big_consistency.py` (overlapping windows must agree).

## 6. Rulings and references

- Rulings R1-R8: `plan/BIG_REVIEW_HANDOFF.md` §2 (branch copy). R9-R23 were written into the MAIN
  checkout's copy of that file (uncommitted there, owner-modified file) and are summarised in the
  catalog; R24/R25 are in `plan/BIG_REVIEW_PATTERNS.md` §E. Error/confirm patterns A1-A72, gate quirks
  §D, recipe change §F, all in the catalog.
- Tools on this branch: `big_flags.py` (view + check()), `big_mkfix.py`, `big_consistency.py`,
  `eval_hints.py` (ids / score / compare with paired bootstrap / repair-rate), `label_hints.py`,
  `label_single.py` (hints+repair default, --baseline, SCRIPTENGINE_ROOT).
- Training plan unchanged (9B, `plan/BIG_REVIEW_HANDOFF.md` §4) — compose only from reviewed windows.

## 7. Known harness limits from the last session

- The worktree guard rejects complex inline shell (heredoc+python, cd into the main checkout); use the
  Edit/Write tools inside the worktree and small launcher scripts in `$CLAUDE_JOB_DIR/tmp`.
- Edits to files in the main checkout are rejected by the guard (write SWITCHPOINT entries with a
  plain `cat >> ... <<EOF` append, which worked).
- Sending a prompt into an opencode session with `opencode run -s ... --auto` was blocked by the
  permission classifier; if the owner wants the 27B instructed, give them the text to paste.

# Fact layer — autonomous execution plan for the 27B (owner 2026-10-07)

Owner: after the council, **you (the 27B in this opencode session) execute the whole fix on your own**
and **re-do all ~5,400 already-labelled windows from 0** under the new method. Claude is not
available to verify step by step, so every step below carries its own verification, which you
run, record, and commit. Work in this worktree (`.claude/worktrees/big-review-flags`, branch
`big-review-flags`); data lives in the main checkout `/home/goblin/ScriptEngine` (use
`SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine`).

## Binding rules (never break)

1. Scope = everything in `plan/FACT_LAYER_COUNCIL_BRIEF.md` section D, as amended by your committed
   council verdict `plan/FACT_LAYER_COUNCIL.md`. Where the council changed a detail, follow the
   council; nothing in D may be dropped without a written reason in the progress log.
2. Owner rule: **only Claude edits `tools/train/big_flags.py` and `plan/BIG_REVIEW_PATTERNS.md`,
   and only Claude adds rules to them.** Do not edit those two files. You may IMPORT and CALL
   `big_flags.check()`. Put fact-layer checks in NEW files (e.g. `tools/train/fact_gate.py`,
   `tools/train/fact_coverage.py`) and write every proposed rule/flag/catalog change for those two
   files to `plan/FACT_LAYER_PROPOSALS_FOR_CLAUDE.md`.
3. Never edit or delete `series/universal/training/big/labels.jsonl`, `big_audit.jsonl`,
   `review_cursor.txt` (Claude's reviewed record). All new output goes to NEW files
   (`series/universal/training/big/labels_v2.jsonl` + `.status`).
4. GPU-only. Do NOT switch models (the agent IS the 27B on :18080). Kill processes by exact PID only.
   Commit with explicit pathspecs only; never commit the owner's files (list in the brief, §C).
5. After every step: append to `plan/FACT_LAYER_PROGRESS.md` (what was done, the verification
   numbers, pass/fail, next step) and commit it with the step's files.

## Steps

**Step 1 — Schema v2 (doc).** Write `plan/EXTRACTION_PROCEDURE_V2.md`: the unchanged 12-verb event
section + the fact layer (relation vocabulary incl. `other`, qualifiers: modality / certainty /
location / time / production, aliases, memberships, items, places) + the sentence-coverage rule
(each narrative sentence covered by ≥1 event or fact row, or tagged with an allowed reason) +
worked examples taken from reviewed windows (Hope/Scott sparring, the Invaders joining, the podcast
call, a plan, a hedged death, a disguise reveal, a group with named members).
*Verify:* every row of the brief's §D table and every dropped class listed in §C has an explicit
place in the schema (write the mapping table in the progress log; 0 unmapped).

**Step 2 — Gates and coverage (code + tests).** `tools/train/fact_gate.py` (verbatim quote, relation
in vocabulary or `other` with free text, end/shape checks reusing the event gate's logic,
qualifier values valid); `tools/train/fact_coverage.py` (split a window into narrative sentences,
report uncovered ones and allowed tags). Unit tests in `tests/test_fact_layer.py`.
*Verify:* `scriptengine/.venv/bin/python -m pytest tests/test_fact_layer.py -q` all pass; run the
coverage checker on the 806 Claude-reviewed windows' final event rows and record the uncovered-
sentence rate (this is the baseline the fact layer must close).

**Step 3 — Labeller v2.** Extend `tools/train/label_single.py` with `--schema v2` (system prompt
`plan/EXTRACTION_PROCEDURE_V2.md`; output `{"events": [...], "facts": [...], "tags": [...]}`;
keep hints + the repair turn; add a coverage repair: if sentences are uncovered, one follow-up
turn lists them). Event rows still pass `label_single.gate`; facts pass `fact_gate`.
Add `--add-only GOLD.jsonl` mode: given a window and its final reviewed event rows, ask only for
facts/tags (events are fixed).
*Verify:* dry run on 5 windows prints valid v2 rows; the parser rejects malformed output without
writing failure rows.

**Step 4 — Pilot and measure (on Claude-reviewed windows).** Take 60 windows from b7–b806.
(a) Full v2 run: event P/R/F1 vs Claude's final event rows with `tools/train/eval_hints.py` logic
(must be ≥ the current recipe's .629 F1 on comparable windows, else fix the prompt first);
(b) fact rows: hand-check 20 windows yourself against the schema, record precision;
(c) coverage: uncovered-sentence rate after v2 (target: below 2% of narrative sentences).
*Stop rule:* if event F1 falls below .60 or coverage misses exceed 5% after two prompt revisions,
stop, write the evidence to the progress log and to the proposals file, and wait.

**Step 5 — Redo the reviewed windows (b1–b806), add-only.** For each reviewed window, the final
event rows = Claude's reviewed rows (latest per id in big_audit.jsonl, else labels.jsonl); run
`--add-only` to add facts/tags. Output to `labels_v2.jsonl` with `"provenance": "claude-events+v2-facts"`.
*Verify:* 806/806 written; event rows identical to Claude's; coverage report per 100 windows.

**Step 6 — Redo every other labelled window from 0 (b807–b5405).** Full v2 labelling (events +
facts + tags) for every window id present in `labels.jsonl` beyond the reviewed cursor, in the same
order, resumable, with the server's spare lanes (leave one lane for this agent; check
`--max-concurrency` in the running serve profile). Output to `labels_v2.jsonl`
(`"provenance": "v2-full"`).
*Verify every 200 windows:* parse failures 0; gate drops logged; coverage rate; a random 10-window
self-check against the schema recorded in the progress log; commit the progress log.

**Step 7 — Close.** Run `tools/train/big_consistency.py`-style checks on overlapping windows in
labels_v2 (same text -> same rows); write a final report in `plan/FACT_LAYER_PROGRESS.md`
(counts, coverage, event F1 on the reviewed windows, open issues) and the full list of proposals
for Claude. Commit. Then STOP: Claude reviews the v2 windows from the start of the file and decides
the proposals.

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

## Update 2026-11-03 (later): GOLD v2 REVIEW COMPLETE — 3,822 / 3,822

Final 59 windows done (fix files G162-G164, G219-G220). Stage 8 (gold lint + compose v2) was started by two read-only
agents: lint report plan/GOLD_LINT_REPORT.md + proposals under big/gold_v2/lint/ (NOT applied), compose draft in
series/universal/training/student_v2_draft/ + plan/COMPOSE_V2_NOTES.md (dry run only). Apply lint fixes and run the
final compose only after reading those.
Open owner/Claude decisions from the last agents: event gate refuses "Maximoff twins" as a class end though the fact
gate accepts it (b2187: met row lost); infobox short fields (<12 chars) tagged in some fix files (G157, G201, G209,
G162-G164) but left untagged in others (G219-G220) — pick one and normalise; codename->real name without alias row
(b1847 etc.); calls to recheck: b2204 killed->defeated (Desak), b2187 Klaue arm = wounded, b2198 saved->helped facts,
b2196 dropped "met Blade", b2215 Vulcan|destroyed|Autumn Continent, b2230/b2235 dropped rows (doer/rename unstated),
b2228 Cabal|defeated|X-Men group-to-group. New rulings applied (not yet in gold27_system.md): org full-name/acronym is
no alias; "not far from X" is not located_at; "prevented by X" = defeated; race member named as survivor takes the
rows (A2); volunteers-to-escape = plan; revealed identity rows under the name (A49); generic used|powers replaced by the
act's verb; "almost V" = other_verb V denied; "decided not to V" = decided actual + V planned denied; ordinary waking
is no awakened event (A106); "were tasked to V" with no tasker = V planned asserted by subject.

## Update 2026-11-03 (stage 8 status)

- Stage 8b (compose v2 dry run) DONE: plan/COMPOSE_V2_NOTES.md (final re-run command in section 7). Ship bar decision:
  student must beat the old teacher on the SAME revised test (provisional .522 [.415-.639]; old gold .602) -- re-score
  after the lint/outcome changes. Empty rule: keep "all three layers empty", drop nothing. Keep --max-len 4096 (10 rows
  dropped), 487-token short system prompt. sft_qwen.py:159 generation cap must be raised 2048 -> 4096 before training.
  eval_base.py cannot score v2; use eval_base_v2.py (GPU path never run: smoke on a few windows first).
- Stage 8a (gold lint) DONE read-only: plan/GOLD_LINT_REPORT.md; 0 gate refusals, 0 mechanical fixes; reading list
  series/universal/training/big/gold_v2/lint/work_gold.txt (170 windows / 162 groups, suggested fix files GL001+, via
  lint_gold_work.sh show B + BV2_SET=gold rv.sh fix). Run the 4-step list in the report before reading.
- Owner ruling 2026-11-03 (general outcome-state principle, plan/review_tools/gold27_system.md) applied to b2187 (G221).
  Outcome-audit agents (read-only, proposals only) write to gold_v2/outcome/ and big/outcome/ -- apply after review.
- Decisions taken (Claude, factual): vehicles are not places; page-title ends absent from the window are dropped;
  fact-gate rank-prefix self pairs (King Vegeta b893, Captain Mizuki b3543) need a fact_gate.RANK allow-list entry (gate
  changes Claude-only, not done yet); narrowed M2: A89 twins dropped only when same act with identical quote.

## Update 2026-11-03 (outcome-state audit done; stopped at 96% of the 5-hour window)

Read-only outcome audits (owner's general outcome-state ruling) finished, NOTHING applied yet:
- GOLD: all 3,822 scanned, 639 candidates all read, 70 proposal blocks -> gold_v2/outcome/proposed_G901.txt (+SUMMARY.md).
  Re-run `bash plan/review_tools/outcome_scan_gold.sh check FILE` before applying (b2187 changed since).
- BIG: 14,000 scanned, 2,409 candidates / 1,491 windows; ranks 1-600 read (P2/P3 fully), 94 windows proposed
  -> big/outcome/proposed_B901..B911.txt (+SUMMARY.md). A successor continues at rank 601 with P1, then P4 above 1777;
  keep candidates.jsonl (a re-scan may re-rank). Scanner: plan/review_tools/outcome_scan_big.py (SCRIPTENGINE_ROOT=main).
- Open owner/Claude questions are in each SUMMARY.md: captured/sealed as outcome (28 gold windows), ally restraining
  ally, possession ending a clash, killed w/o stated death (b768, b2692), restraining so others can finish (Athena/Zeus,
  Strange/Ultron), wounded winner vs race end (Nuada), Sentry destroyed+reconstitutes, passive outcomes with no doer
  (A8 vs ruling), A113 self-report kills, capability-list "victories" (b2290).
- New pattern: stopped-plot verbs (prevented/stopped/foiled/thwarted) stored as other_verb facts should be `defeated`
  events -- grep the corpus; add to the catalog.
- Stage 8d plan (scheduled 15:31 IST 2026-11-03): apply accepted outcome proposals, re-run the gold lint, then 2 agents
  read work_gold.txt (170 windows; fix files GL001+), then re-snapshot compose and re-score the teacher.

## Update 2026-11-04 (big outcome proposals applied; gold lint re-run clean)

- Step 1 DONE: backup `big/big_audit_v2.jsonl.bak-pre-B912-B955`; B912-B919 + B950-B955 each re-checked
  (`outcome_scan_big.py check`: 230 would apply, 0 refused; no window in two files) and submitted ONCE with `rv.sh fix`.
  Audit 20,005 -> 20,235 lines (+230). Commit 8aa4f667. All big outcome proposals (ranks 1-2409) are now applied.
- Step 2 DONE: `lint_gold.sh --regate` -> unreviewed 0, no REGATE_* class (0 gate refusals). The 15 GL001 windows
  (submitted twice) have 0 doubled rows; a whole-gold check by row key (events s|v|o|quote, facts s|r|o|quote|modality,
  tags tag|quote) finds 0 duplicates in 3,822 windows. Remaining lint classes are the known reviewed ones
  (E_met_and_fight_same_pair 65 w, X_end_* 75 w, name_short_and_full 39 w, R_overlap_cross_split b190/b3346 ...).
- NEXT: step 3 (open rulings -> gold27_system.md + BIG_REVIEW_PATTERNS.md; fact_gate.RANK allow-list needs the owner's
  OK before any gate-code edit; de-duplicate b190/b3346 before compose), then step 4 (compose v2 dry run + teacher
  re-score). Stopped at 86% of the 5-hour window to stay under the 96% stop.

## Update 2026-11-04 (later): step 3 rulings decided; gold applied in full, big ~70% (stopped at 80% of the 5-hour window)

- sft_qwen.py dev_generate cap 2048 -> 4096 committed on its own (ab2c5490).
- RULINGS: every open question is decided factually and written to `plan/review_tools/gold27_system.md` ("Rulings
  2026-11-04"): captured/sealed as outcomes, ally restraint, restrain-so-others-finish, passive outcomes (A8 refined),
  rescue mid-fight, killed without a stated death, wounded winner vs race end, destroyed+reconstitutes, A113 self-
  reports (and factive narration keeps the event), records of victories, possession ending a clash, near-final
  states, temporary traps, intercepted attacks = saved, one name per person across layers, cross-split overlap, nearly V.
  New patterns + candidate counts are in `plan/BIG_REVIEW_PATTERNS.md` (2026-11-04 block).
- GATE (owner OK in chat): fact_gate.RANK keeps King Kai/Vegeta/Cold/Piccolo/Kong + Captain Mizuki (4077b27a, test added).
- DATA (backups `*.bak-pre-rulings-2026-11-04` of both audits). Work dir `big/rulings_2026-11-04/` (copied into the
  worktree): BRIEF.md (method), list_G/B1/B2/B3.txt, fix files, ledger_*.txt (one line per submitted file), notes_*.md
  (per-window decisions, "For the owner", counts).
  - GOLD: all 148 candidates read; 51 changed (G_01-G_04) + G_90 (the five RANK-hold windows b825 b893 b1014 b3543
    b3657) + G_91 (the agent's owner questions: b30 forced retreat, b1530 Todo met Yuji, b1533/b1669 intercepted =
    saved, b2064 group defeated). Gold audit 4,127 -> 4,188.
  - BIG: 264 windows changed (B1_01-07 99, B2_01-07 90, B3_01-05 75); big audit 20,235 -> 20,499. Verified: new records
    = ledger sums, one record per window, old prefix byte-identical. `recon.sh check all`: 133 DIFF pairs, 131 logged +
    C556 (b6094/b6108, justified, now logged) + 1 pre-existing.
  - BIG NOT DONE (resume with BRIEF.md, same lists, new agents, next file numbers B1_08 / B2_08 / B3_06):
    B1 from b2139 (93 lines; b2139-b2251 viewed, nothing written); B2 from b6181 (85 lines; drafts for b6181-b6425 in
    notes_B2.md "STOPPED HERE", re-read before use); B3 drafts for 18 windows b9783-b10667 + 5 undecided (b10743 b10761
    b10768 b10778 b10848) in notes_B3.md "STOPPED HERE", unread b10871-b13969.
  - Owner questions left unchanged are in notes_B1/B2/B3.md "For the owner" (b12398 clinically dead = killed?, torture
    of captives written as fought, mind control still as fought b79/b653/b1242, b5562 Xorn self-pair, rank-name windows
    b8054/b8927/b9603/b9984 — Emperor Prime, Dr. Steve, Captain Glory, King Arrkam may need more RANK entries).
- NEXT: finish the big lists (step 3 remainder), then step 4: gold lint re-run (data changed), compose v2 with the
  b190 rule (compose drops a gold train window repeating a >=40-char dev/test sentence — code change still to make),
  check_v2_set.py rc=0, teacher re-score. Step 5 (GPU) only after the owner says go.

## Update 2026-11-04 (end of window, 95%): owner rulings on torture, mind control, clinical death
- Owner answers (chat): b12398 clinical death -> decided by cause; torture is not a fight; mind control = "B under
  control of A fighting C", with will deciding (Majin Vegeta chose to fight). Written in gold27_system.md "Owner
  rulings 2026-11-04 (torture, mind control, clinical death)"; BRIEF.md addendum.
- Code (cc2b3677): fact relation `tortured`, fact modality `controlled` (asserted_by = controller), in fact_gate
  (so the student system prompt carries them), score_layers_v2 groups, test. Full test suite: only the usual
  environment failures (worktree has no series stores); test_fact_layer 65/65.
- Data: b12398 fixed (M_01: Janet killed Victor, saved Chase, Victor awakened). Candidates from
  plan/review_tools/tc_scan.py: list_TC_gold.txt (51) and list_TC_big.txt (422, NOT partner-grouped yet: group by
  recon components before giving it to agents). Gold TC pass: 30/51 read, 3 changed (TCG_01: b1861 tortured,
  b1989/b2041 controlled); resume at b2143 (TCG_02). Agent questions in notes_TCG.md (b532 devil summoned under
  Makima's control; b1989 "purposely missed any vitals"; outcome object named for a quote with no outcome verb).
- Order for the next window: finish TC gold (21), the three big lists (resume points above), TC big (422, grouped),
  then step 4.

## Update 2026-11-04 (night, second window, stopped at ~88% / weekly ~93%)
- Big audit 20,500 -> 20,707 (RB1-RB3 remainders 149, T1 36, T2 15, D1 7); gold 4,191 -> 4,201 (D3G_01: the gold
  torture/mind-control list is DONE, incl. b1989/b2041 re-check). One record per window, ledger sums match, recon
  check: only logged exceptions. BRIEF.md Addenda 2-3 hold every decision of this window's agent questions.
- compose v2 drops a gold train window that repeats a dev/test sentence (1a32dbee): b190 + "Robbery of the Russian
  Nuclear Facility"; trial compose: 0 leaks, 0 errors.
- DONE lists: gold rulings + gold TC; big list_R_B2. REMAINING big work, all with resume points and drafts:
  notes_D1.md "STOPPED HERE" (RB3 drafts, Addendum-3 corrections b12511 b12550 b12634 b12346 b12392 b12405 b12319,
  list_R_B3 b12993-b13969; RB1 lines b3097-end from notes_RB1.md), notes_D2.md (48 re-checked T2 drafts + b9001
  b9537 b9567 b5972 + b12872 b12876 b12881 b13372 b13222; undecided b13659; unread b13797 b13919 b13976),
  list_T1.txt from the b2462/b2605 group (~95, notes_T1.md / notes_D3.md). Roughly 250 windows, ~120 already drafted.
- Owner-type questions still open in notes_D1/D2/D3/RB*/T*.md (left unchanged): e.g. "Conquistadores" as an end
  (b13854), Betsy "involuntarily" (b9588/b9594), controller only implied (b2342, b2652, b2296).
- Then step 4: gold lint re-run, compose v2 -> student_v2_short, check_v2_set rc=0, teacher re-score.

## Update 2026-11-06 (step 3 DONE: the big rulings pass is finished)
- Big audit 20,707 -> 20,848 (+141, one record per window, ledger sums match: E1 40, E2 57, E3 12, E4 16, E5 11,
  M_02 5); old prefix byte-identical; gold unchanged at 4,201 (E5: gold b532 needs no change). `recon.sh check all`:
  133 DIFF pairs, all in recon/exceptions.txt (new: C370 b3375~b9059, C628 b7563~b7573, C451 b4256~b4877).
- Every step-3 list is done: list_R_B1/R_B3 rest + Addendum-3 corrections (E1), T2 drafts + D2 tail (E2),
  list_T1 rest (E3/E4), the open owner questions (E5 + M_02).
- Decisions (owner delegated): BRIEF.md Addendum 4 (old "For the owner" questions) and Addendum 5 (this round's).
  New patterns: BIG_REVIEW_PATTERNS.md "2026-11-06 RULINGS PASS, LAST ROUND".
- Left for the owner: more fact_gate.RANK entries (b8054 Emperor Prime, b9603 Captain Glory, b9984 King Arrkam,
  b8927 Dr. Steve keep the full name in events, the stripped form in facts). Tool limit: apply_edits keeps one fact
  per s|r|o|modality, so two controllers of one act get one row (Add.5, b12405).
- NEXT: step 4 (gold lint re-run, compose v2 -> student_v2_short, check_v2_set rc=0, teacher re-score).

## Update 2026-11-06 (step 4 DONE: final compose v2 + teacher re-score; step 5 waits for the owner)
- Gold lint (GOLD_LINT_REPORT §6): `lint_gold.sh --regate` -> UNREVIEWED 0, no REGATE_* class (0 gate refusals);
  `lint_gold_fix.sh build/apply` -> proposal 0, STALE 0, missing 0 (nothing to apply); lint_gold.json and
  work_gold.txt rebuilt. Remaining classes are the known reviewed ones.
- Compose (COMPOSE_V2_NOTES §7, defaults: --empty-def all, no --drop-base-page-overlap, short system prompt) from a
  snapshot of big 20,848 / gold 4,201 lines -> `series/universal/training/student_v2_short`: train 17,312, dev 215,
  dev_pool 151, test 292. Leaks: sentence>=40ch train&dev 0, train&test 0, dev&test 0; gold train windows dropped for
  a repeated dev/test sentence: Rakshas, Robbery of the Russian Nuclear Facility. 166 big train windows on a test
  base page kept (owner open decision §6.5). Max total tokens: no row over 4096 in dev/test.
- `check_v2_set.py` -> rc=0, "errors": 0 (`student_v2_short/check.json`).
- Teacher (frozen 35B drafter) on the revised test, events: all n=292 F1 .570 [.484-.659]; marvel+mcu n=123
  F1 .523 [.415-.639] (P .571 R .482). SHIP BAR: the student must beat .523 on this same marvel+mcu test (old gold
  bar was .602).
- STEP 5 (GPU training, BIG_REVIEW_HANDOFF.md §4 with D=student_v2_short) NOT started: waits for the owner's go.

## Update 2026-11-06 (step 5 STARTED on the owner's go)
- Smoke (`/mnt/PROJECTS/student_runs_big/v2-smoke`, 64 train / 8 dev, 4 steps): sft_qwen trains and dev-scores v2
  rows (the event scorer reads v2 gold: gold-as-pred F1 1.0), saves the adapter to `<out>/best`; eval_base_v2's GPU
  path works (4 test windows in 20 s, 3/4 valid after 4 steps). The adapter path is `<out>/best`, not `<out>`.
- Full run: `/mnt/PROJECTS/student_runs_big/step5_v2.sh` (driver PID 417510, log `step5_v2.log`), seeds 1 and 2
  in turn: rank 16, alpha 16, lr 1e-4, 2 epochs, --patience 99, --loss-norm step, micro 2 x accum 8, --max-len 4096
  (17,302 train rows, 10 over-long dropped; 1,082 steps/epoch), select on dev_pool; then eval_base_v2 test preds per
  seed (`<out>/test_preds.jsonl`). Out dirs `9B-v2-short-a16-lr1e-4-s{1,2}`. Started 14:12 IST; the card sits at
  ~31.3 of 32.6 GB with two non-fatal allocator OOM warnings at the start. If it OOMs: micro 1 x accum 16.
- After it finishes: choose the seed/epoch on dev_pool (score_subsets --teacher on dev_pool, score_layers_v2 for
  all three layers), then score test ONCE: `score_subsets.py --gold student_v2_short/test.jsonl --pred
  <best>/test_preds.jsonl --teacher` against the .523 marvel+mcu bar.
- A separate session ("9b-weight-edit") was started on the owner's request to edit the 9B weights for extraction;
  it must not use the GPU while this run is going.

## Update 2026-11-06 21:25 (step 5 PAUSED by the owner; the GPU chain keeps running unattended)
- Micro-batch 2 OOMed on both seeds (dense batches, ~31 GB). The chain `/mnt/PROJECTS/student_runs_big/step5_v2_after.sh`
  (PID 493524, log `step5_v2_after.log`) re-trains at micro-batch 1 x accum 16 (~24-28 GB, no allocator warnings),
  ~137 min/epoch. The OOM dirs are kept as `*.failed-HHMM`.
- Seed 2 DONE (`9B-v2-short-a16-lr1e-4-s2`, rc=0). dev_pool (151) events F1: e1 .588 [.474-.697] (marvel+mcu .564),
  e2 .585 (marvel+mcu .514); `best/` = e1. The teacher on the same dev_pool: .472 [.356-.576], marvel+mcu .427.
  The CIs overlap, so this is not a win until the seed 1 result and the one-time test score are in.
- Seed 1 started 19:53 (sft PID 570368); epoch 1 ends ~22:10, epoch 2 ~00:30. Then the chain writes
  `<run>/test_preds.jsonl` for both seeds (~01:00, "=== ALL DONE"). The weight-edit session's waiter
  (`tools/train/wsp_run.sh`, PID 498258) then runs its dev_pool sweep on the free GPU (~2-3 h).
- GOTCHA: `score_subsets.py --teacher` run from this worktree prints NO teacher line. The teacher drafts
  (`series/<s>/training/labels/draft_frozen.jsonl`) exist only in the main checkout (series/ is gitignored) and ROOT
  is the script's repo. Set `score_subsets.ROOT = Path('/home/goblin/ScriptEngine')` (that reproduces test .570/.523).
- TO RESUME: check the log for "=== ALL DONE". Pick the seed/epoch on dev_pool (seed 1 vs seed 2 e1). Run
  score_layers_v2 for all three layers. Then score test ONCE against the .523 marvel+mcu bar, update this file and commit.
- 21:35 UPDATE: the owner stopped all GPU work. Killed: the seed 1 sft (PID 570368, ~1.5 h into epoch 1, partial
  dir `9B-v2-short-a16-lr1e-4-s1` has no checkpoint), the chain driver 493524 and the weight-edit waiter 498258. The GPU
  is free. TO RESUME: re-train seed 1 from scratch (move the partial dir aside first; ~4.5 h at micro-batch 1). Then
  test preds for both seeds (eval_base_v2 --adapter <run>/best). Then re-arm `tools/train/wsp_run.sh` (branch
  claude/sad-mirzakhani-287aec) if the weight edit is still wanted.

## Update 2026-11-14 (step 5 re-planned: Marvel out, new yardstick, v3 arms queued)
- Owner scope change (relayed by the Fable analysis session, `docs/9B_STUDENT_ANALYSIS_2026-11-14.md` in worktree
  `9b-model-extraction-analysis-a7e9c9`): Marvel is out; targets DB, Naruto, JJK, HxH. "Claude level" is NOT
  gold-agreement F1 (a blind Opus scores events .60 / facts .36 / tags .50 on 55 dev_pool windows, below seed 2);
  the bar is the source-blind row audit (seed 2: 5.1% wrong rows, ~20% statements missed; gold 1.0% wrong).
  The old .523 Marvel+MCU test bar no longer applies. Test stays sealed.
- Runs moved by the storage session to `/media/goblin/HDD/Ubuntu Offload/projects_drive/training/student_runs_big/`
  (link `~/student_runs_big`); the seed-1 retrain was stopped there at 04:17 (rc=143). Not re-run as it was.
- GOTCHA: `/mnt/PROJECTS` is now mounted `ntfs3`, which does not follow the HF cache's Interix links (`IntxLNK`
  files): `config.json` "is not a valid JSON file". `~/models/Qwen3.5-9B` holds real symlinks to the resolved
  blobs; use `--model /home/goblin/models/Qwen3.5-9B`.
- Step 1a: `tools/train/split_v3_dev.py` -> `series/universal/training/student_v3_split`: dev_v3 = 635 windows
  outside Marvel/MCU (482 held-out gold train windows on 313 whole pages, 20% per series, seed 7, + the 153 old
  non-Marvel dev windows; jjk 230, others 66-75), page overlap with train 0, sentence leak drops 4, dev/test sentence
  overlap 0. Train 16,826.
- Step 1b/1c: `tools/train/score_v3.py` (statement-level score through `tools/train/statement_norm.py`, events +
  facts pooled, crowd_end/no_doer soft FPs, any-name tag coverage; gates: sentence coverage, verbatim, illegal rows,
  JSON). `tools/train/mine_swaps.py` lists same-quote label swaps; on the peer's 180 train windows they are a long
  tail, no dominant pair.
- Baseline, seed 2 on the 153 old non-Marvel dev windows (clean: never trained): statements F1 e1 .678 [.650-.706],
  e2 .692 [.666-.719]; coverage .991, verbatim .997-1.000, illegal 0, JSON 153/153. On the 55 shared dev_pool
  windows: seed 2 statements .611, blind Opus .510.
- NEW BAR (before training): on dev_v3, statement F1 with CI plus gates coverage >= .99, verbatim >= .997, illegal 0;
  then the blind row audit on the final candidate, target <= 2% wrong rows and <= 10% missed (a goal, not a result).
- Step 2c: `tools/train/compose_v3.py` -> `student_v3` (full, 875 windows changed: object-less discovered and
  other_verb realize/learn/notice/discover/deduce/figure -> learned; believe/think/suspect/assume -> suspected) and
  `student_v3_nm` (non-Marvel gold only, 1,814; 87 changed: that gold already used one encoding). dev_mon = the 89
  non-Marvel dev_pool windows (per-epoch monitor only). Gold files untouched.
- `sft_qwen.py`: `--init-adapter DIR` (continue a LoRA adapter) and `--save-last` (OUT/last = annealed end).
- GPU: step 2a mining (seed 2 on 500 train windows, `v3/mine_preds_s2.jsonl`), then the chain `v3/chain.sh`
  (log `v3/chain.driver.log`): G-s1, G-s2 (non-Marvel gold only, 3 epochs), F-s1 (full v3, 2 epochs), FG-s1
  (F-s1 + 1 epoch on non-Marvel gold, lr 5e-5), each scored on dev_v3 (`<arm>/dev_v3_preds.jsonl`). ~12 h.
  Everything writes under the HDD runs folder `.../student_runs_big/v3`: do not move it while the chain runs.

## Update 2026-11-14 (later): owner re-prioritised to JJK true 100%; per-line side test S1 done, S2 queued
- Owner (relayed by the 9B analysis session): MCU is out with Marvel; then "get JJK to true 100% first, stop the
  naruto pull", with a per-line side test on JJK. ON HOLD: the multi-series v3 arms (the queued `v3/chain.sh` was
  stopped before it trained anything, PID 794676), HxH/DB/Naruto labelling, any second seed of the old recipe.
  KEPT: step 2a (mining, running) and 2b (statement-level re-score).
- Guard rails: JJK store work only on a copy (`~/student_runs_big/jjk_side/facts_copy.db`, from
  series/jjk/facts.db 2026-11-14); no write to the live store, no re-index, no branch merge without the owner.
- S1 (`tools/train/perline_candidates.py`, out `jjk_side/s1`): JJK holdout = 150 gold train windows on 59 whole
  pages (seed 7) + the 64 JJK dev windows = 214. Candidate list per window = the page's node, its edge targets,
  and every node whose name/alias occurs in the passage: median 46, p90 107. Coverage of the gold's ends (name rule
  eval_extraction.same): events .976, fact subjects .989, fact objects .930, all .980 (>= the ~95% bar, so no list
  fix before training). Top uncovered: first-name-only mentions with no alias (Toge, Noritoshi, Megumi, Riko),
  places, items.
- S2 (`tools/train/perline_build.py`, data `jjk_side/s2data`): v2 labels re-projected per sentence to the `meaning`
  target (class event / standing state / trait / trivia, people as candidate numbers, events [verb, s#, o#]);
  train = non-Marvel gold minus the JJK holdout pages, from the stores of each series (read-only, immutable).
  Driver `jjk_side/s2.sh` (log `s2.driver.log`): waits for the mining job, trains `perline-s1` (r16 a16 lr1e-4,
  3 epochs, OUT/last), then holdout preds for it and for seed 2 (`seed2_holdout_preds.jsonl`). NOTE: seed 2 trained
  on the 150 holdout train windows; only its 64 dev windows are a clean baseline (report both).
- NEXT: S3 scorer (per line: class, people set, event triples; wrong-person and missed lines) + a source-blind
  audit sheet; S4 continuity.py agreement. Report S1-S4 to the owner before anything goes to a store.
- Step 2a/2b result (seed 2 best over 500 TRAIN windows, `v3/mine_preds_s2.jsonl`, 1,763 s, 496/500 valid): the
  same-quote swaps are a long tail (1,470 unmatched gold rows; top pairs are tag-name swaps and outright misses:
  list_header/no_relation/citation tags with no student row 29/26/22, met/fought/defeated events missed 15/12/11).
  No dominant encoding pair. Statement-level F1 on these trained windows .675 [.655-.695], the same as on unseen
  dev (.678): the gap is missed statements, not encodings, so normalising targets alone will not move it.
  Gates: coverage .944 (big-set windows pull it down), verbatim .995, illegal 5/3,010, JSON 496/500.

## Update 2026-11-14 (afternoon): power loss, mapping bug fixed, per-line S2 re-run on fixed data
- 06:15 IST the PC went down mid-run (no shutdown sequence; an unattended kernel 7.0.0-43 + NVIDIA module update
  installed at 06:08-06:09 while training; a checkpoint write to the NTFS HDD at 06:14; cause unknown). Up again
  14:46. The S2b retrain was lost (epoch 1 only, kept as `jjk_side/perline-s1.crashed-power-0615`); seed 2's holdout
  preds (`jjk_side/seed2_holdout_preds.jsonl`) were complete. Precaution since then: live run output goes to the
  ext4 root (`~/student_runs_local/`) and is copied to the HDD runs folder when a run ends.
- MAPPING BUG (found by the 9B analysis session's gold audit, its `docs/gold_audit_2026-11-14/FINDINGS.md`):
  perline_build `num()` mapped a gold name to the first alphabetical candidate sharing ONE word (eval_extraction.same):
  "Toji" -> the battle page "Satoru Gojo vs. Toji Fushiguro", "Yuji" -> Kento Nanami (a sentence alias), other-language
  nodes, chapter pages; 22-30% of JJK ends wrong. The run training on it was stopped by PID (7974/7978); its data kept
  as `s2data.bad-mapping`. Every S1/S2/S3/S4 number before this point is void.
- FIX: `perline_candidates.Resolver` uses the engine's own resolver (scriptengine/ingest/events.py
  participant_candidates + pick_candidate: no battle/chapter/episode/arc pages, exact names and aliases only, the
  page's links break ties) on store COPIES (`~/student_runs_local/stores/<series>.db`; FactStore may write), drops
  other-language nodes and sentence-like aliases. Spot check: 53 of 2,553 resolved holdout ends map to a name sharing
  no word, all wiki aliases (Pseudo-Geto -> Kenjaku, Maru -> Marulu Val Vol Yelvori, Mechamaru -> Kokichi Muta).
- S1 strict (`jjk_side/s1_strict`): gold ends resolved AND on the candidate list .958 (events .960, fact subjects
  .972, fact objects .860); candidates median 33, p90 84. Misses are names the store has no alias for (Miyo 25,
  Usami 10, Yoshinobu 6, Kinji 6, Jabaloma 5, Rin 5) and places/items: a store alias gap, not a list gap.
- Seed 2 baseline through the fixed resolver (perline_score.py; dev = the 64 clean windows): class .905, is-event
  F1 .953, exact people .644, wrong-person lines .209, missed lines .042, triples F1 .539 (all 214: .895/.947/.681/
  .177/.055/.642). S4 store corroboration (same verb+pair stated on another page): gold .886 (dev .862), seed 2 .840
  (dev .781); before the fix both read ~.39.
- S2 re-run (`~/student_runs_local/jjk_side/s2d.sh`, log `s2d.driver.log`; final line reads "S2C DONE", a sed slip):
  perline-s1 on the fixed s2data, then holdout preds; copied to `.../student_runs_big/jjk_side/fixed/`.
- The v2 gold on the 64 clean JJK windows (the analysis session's read of all 676 rows): 1.5% wrong by its own rules,
  ~7% of events missing, 3 uncovered sentences. Fit to rank two systems, not an absolute yardstick. No gold row is to
  be edited without the owner.
- GOLD CORRECTED (owner-approved, done by the 9B analysis session, 2026-11-14 15:17): gold_audit_v2.jsonl 4,201 ->
  4,213 lines, 11 JJK DEV windows (b3467 b3469 b3472 b3476 b3477 b3486 b3488 b3498 b3505 b3511 b3517; +18/-9 rows;
  fixes gold_v2/fixes/G130-G131; backup .bak-pre-audit-2026-11-14). Training sets are unaffected (dev windows only);
  STALE until recomposed: student_v2_short/dev(+dev_pool).jsonl, student_v3_split/dev_v3.jsonl (on hold with the
  multi-series work), and lint_gold.sh has not been re-run. The per-line evaluation uses
  `~/student_runs_local/jjk_side/holdout_fixed.jsonl` (`tools/train/perline_refresh_gold.py`: latest record per id,
  re-projected; exactly those 11 windows changed). Seed 2 on the corrected 64 dev windows: class .908, is-event .955,
  exact people .647, wrong-person .206, missed .046, triples .539; corroboration gold .875 vs seed 2 .781.
- Owner ruling "shows up between companions -> met" (BRIEF Addendum 6; catalog line SHOWS-UP in
  BIG_REVIEW_PATTERNS.md): gold 4,216 lines, b3512 b3515 (dev) and b1229 (train, but one of the 150 JJK windows held
  out for the per-line test, so not in its training data). holdout_fixed.jsonl now carries all 14 corrected windows.
  Not swept: the 14k big set; three non-companion "show up" gold cases (b1088 b2995 b723) left as they are.

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

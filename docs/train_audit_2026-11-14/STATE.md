# Training-label audit: running state (kept current so the work survives a context reset)

Owner instruction 2026-11-14: check all 2,150 training passages by blind second reading, comparison and a
third look; "launch 4 subagents of Opus 5.5 high and complete this, But you (Fable 5.2) will supervise and
check if it makes a mistake". Earlier: "Don't run the project's gate" as the checking method.

Calibration (Fable reader, the 64 known JJK dev windows, `blind/calib_blind_A.jsonl`): at WINDOW level the
blind reading found 8 of the 9 events today's corrections added and lacked both events they removed. Line
level is useless as a filter (84% of lines differ) for two structural reasons: the gold's "people" holds only
the subject of an other_verb row, and the gold writes one fought/met per pair per window, on one sentence.
So compare per window: blind-only events = candidate missing, gold-only events = candidate wrong, gold
people the blind reader does not list = candidate wrong person.

Phase A, blind reading: `blind/chunks/chunk_NN_input.jsonl` (32 chunks, about 67 windows each), readers are
Opus 5.5 high subagents, four at a time, prompt = `blind/BRIEF_reader.md` with {INPUT} and {OUTPUT} filled,
output `blind/chunks/chunk_NN_blind.jsonl`. After each: validate, compare with
`python3 blind/compare_windows.py`, and spot-check five windows by eye.

Phase B, third look: per window with a disagreement, an adjudicator gets the window, the page text around it,
the gold rows and the reviewer's why-note, the blind lines, and the rulebook (procedure sections A to F,
BRIEF addenda 1 to 6). It proposes fix blocks with the rule and the quote. Fable reads every proposal before
anything is applied. Writes go through `big_review_v2.py fix` with a backup first (it is the only writer of
the gold audit file); nothing else of the project's gate is used as a check.

Progress log (append below):
- 15:55 Calibration scored (`blind/compare_windows.py`, 64 windows): gold events 116, blind 166, in both 103,
  blind-only 63, gold-only 13, gold people unlisted 1; answer key 8 of 9 added events found, 2 of 2 removed
  events absent. The Fable reader used 250k tokens and 17 minutes for 64 windows. Usage then: 5-hour window
  55%, so the full blind pass will span several usage windows. Stop launching at about 85% and resume after
  the reset; the training session shares the same allowance.
- 15:58 Round 1 launched, four Opus 5.5 high readers: the same 64 calibration windows
  (`blind/calib_blind_opus.jsonl`, to check Opus against the known errors and against the Fable reader) and
  chunks 01, 02, 03 (`blind/chunks/chunk_0N_blind.jsonl`). Chunks 04 to 32 not started.
  When a reader finishes: `python3 blind/compare_windows.py <gold> <blind> --worklist blind/chunks/chunk_NN_work.jsonl`
  with gold = `~/student_runs_local/jjk_side/s2data/train.jsonl` (calibration: `s2data/holdout.jsonl`
  `--answer holdout_fixed.jsonl`); expect class agreement near 93% and under 3% of gold people unlisted; a
  chunk far from that gets a closer read before it is trusted.
- 15:57 chunk 02 scored: windows 68/68; class 302/339=89%; events gold 24 blind 27 both 17 blind-only 10 gold-only 7; gold people unlisted 0/132; format problems 0; windows with something to look at 14/68
- 15:58 chunk 01 scored: windows 68/68; class 164/210=78%; events gold 43 blind 43 both 24 blind-only 19 gold-only 19; gold people unlisted 2/101; format problems 0; windows with something to look at 12/68
- 16:02 Chunk 01 reader reported that parallel readers share one scratch folder and overwrote each other's
  helper scripts (it read a batch of another reader's windows, noticed, discarded it and redid it). Running
  readers were warned by message; the brief now tells each reader to keep helpers in a private subfolder
  (`blind/BRIEF_reader.md`, {TAG}). New check after every chunk: `python3 blind/check_ids.py <input> <blind> <gold>`
  (same ids in the same order, and no window whose classes look like another passage's). Chunks 01 and 02 pass.
- Finding from the first chunks: where the gold-derived class is `trivia` and the blind reader says `event`
  (10 lines in chunk 01, 24 in chunk 02), the sentence usually narrates an act that the v2 gold tagged
  `no_relation` or left without a row because a participant is unnamed; the conversion then calls it trivia.
  That is a defect of the per-line targets, to be counted in the third look alongside event disagreements.
- 15:59 chunk 03 scored: windows 68/68; class 198/250=79%; events gold 21 blind 31 both 19 blind-only 12 gold-only 2; gold people unlisted 2/97; format problems 0; windows with something to look at 10/68
- 16:05 Chunk 03's reader also hit the shared-folder mix-up (it first labelled windows 17 to 48 from the
  calibration input, deleted them and redid them). Checked: ids match its input in order, and in the redone
  batch 99% of its people picks are names that occur in that window or page, so the labels belong to the
  right passages. Chunks 04, 05, 06 and the Opus calibration are running; 05 and 06 were briefed with a
  private helper folder. Launch order continues 07, 08, ... one per finished reader, tag cNN.
- 16:08 Opus 5.5 high calibration on the 64 known windows (`blind/calib_blind_opus.jsonl`): found 8 of the 9
  events the corrections added, lacked both removed events; ids clean. The two blind readers (Fable, Opus)
  agree with each other on class 98%, people F1 .97, events F1 .86, far more than either agrees with the
  gold-derived targets (class 92%, events about .7). So most reader-versus-gold disagreement is convention or
  conversion, not reader noise. Opus high accepted as the reader. Usage 66% of the 5-hour window; stop
  launching at 85%.
- 16:01 chunk 04 scored: windows 68/68; class 191/219=87%; events gold 36 blind 52 both 16 blind-only 36 gold-only 20; gold people unlisted 2/86; format problems 0; windows with something to look at 19/68
- 16:03 chunk 06 scored: windows 68/68; class 195/231=84%; events gold 52 blind 70 both 37 blind-only 33 gold-only 15; gold people unlisted 7/117; format problems 0; windows with something to look at 23/68
- 16:04 chunk 05 scored: windows 68/68; class 320/345=93%; events gold 32 blind 42 both 21 blind-only 21 gold-only 11; gold people unlisted 5/99; format problems 0; windows with something to look at 14/68
- 16:05 chunk 07 scored: windows 68/68; class 185/214=86%; events gold 34 blind 70 both 26 blind-only 44 gold-only 8; gold people unlisted 9/125; format problems 0; windows with something to look at 15/68
- 16:06 chunk 08 scored: windows 68/68; class 199/228=87%; events gold 43 blind 55 both 30 blind-only 25 gold-only 13; gold people unlisted 10/124; format problems 0; windows with something to look at 22/68
- 16:08 chunk 09 scored: windows 68/68; class 313/334=94%; events gold 30 blind 42 both 26 blind-only 16 gold-only 4; gold people unlisted 2/105; format problems 0; windows with something to look at 12/68
- 16:12 Owner: "Just fix all these passages, and wait for my go to start trainin". Training session told to
  start no training run until the owner's go, and not to rebuild until I send the list of changed windows.
- Chunks 01 to 09 read and checked clean (ids match, no foreign windows). Third-look inputs are built per chunk
  (`adj/make_adj_input.py NN` -> `adj/chunk_NN_adj_input.jsonl`); brief `adj/BRIEF_adjudicator.md` with {INPUT},
  {OUT}, {TAG}. Pilot adjudication A01 = chunks 02+03 (`adj/A01_adj_input.jsonl`, outputs `adj/A01_verdicts.jsonl`,
  `adj/A01_fix.txt`, `adj/A01_review.md`). Fable reads every fix in the review file, dry-runs it on a copy
  (`docs/gold_audit_2026-11-14/dry_run_fix.py`), then applies with a backup as fix file G133 onward.
- 16:08 chunk 11 scored: windows 68/68; class 123/164=75%; events gold 57 blind 41 both 32 blind-only 9 gold-only 25; gold people unlisted 9/136; format problems 0; windows with something to look at 20/68
- 16:15 USAGE CUTOFF REACHED: 5-hour window at 85%, resets 19:40 IST (14:10 UTC). No new subagent is launched
  until after the reset (owner rule: never use extra credits; the training session shares the allowance).
  Still running at the cutoff: readers for chunks 10 and 12, and the pilot third look A01 (chunks 02+03).
  Blind reading done and checked: 01-09, 11. Not started: 13-32.

## How to resume (read this after a context reset)
1. Check usage (`get_usage`); launch only while the 5-hour window is under 85%. Four Opus 5.5 high subagents at
   a time (owner's instruction), `model: opus`, `effort: high`, general-purpose.
2. Blind readers: prompt = `blind/BRIEF_reader.md` with {INPUT} = `<abs>/blind/chunks/chunk_NN_input.jsonl`,
   {OUTPUT} = `<abs>/blind/chunks/chunk_NN_blind.jsonl`, {TAG} = `cNN`. Next chunks: 13, 14, ... 32.
3. When a reader finishes: `python3 blind/check_ids.py blind/chunks/chunk_NN_input.jsonl blind/chunks/chunk_NN_blind.jsonl ~/student_runs_local/jjk_side/s2data/train.jsonl`
   (must show foreign 0, missing 0, order ok True), then `blind/supervise.sh NN`, then `python3 adj/make_adj_input.py NN`.
4. Third look: concatenate two or three chunks' `adj/chunk_NN_adj_input.jsonl` into `adj/Axx_adj_input.jsonl`
   (A02 = 01+04, A03 = 05+06, A04 = 07+08, A05 = 09+11, then onward), prompt = `adj/BRIEF_adjudicator.md` with
   {INPUT}, {OUT} = `<abs>/adj/Axx`, {TAG} = `Axx`.
5. When an adjudicator finishes: READ `adj/Axx_review.md` in full and judge every proposed fix yourself against
   the quoted sentence and the rule (the owner: "you (Fable 5.2) will supervise and check if it makes a
   mistake"). Strike what you do not accept. Dry-run the accepted blocks:
   `cd <big-review-flags worktree> && BV2_SET=gold SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine /home/goblin/ScriptEngine/scriptengine/.venv/bin/python <abs>/docs/gold_audit_2026-11-14/dry_run_fix.py tools/train <fixfile> <scratch copy>`
   then apply: backup `gold_v2/gold_audit_v2.jsonl` once per batch, copy the fix file to `gold_v2/fixes/G133.txt`
   (next free number), run `big_review_v2.py fix`. Record each batch here with window numbers.
6. When all 32 chunks are adjudicated and applied: send the training session the full list of changed windows.
   DO NOT ask it to train: the owner said "wait for my go to start trainin".
7. Unsure verdicts and the three open items from the dev audit go to the owner as a short list at the end.
- 16:09 chunk 10 scored: windows 68/68; class 269/318=85%; events gold 68 blind 73 both 52 blind-only 21 gold-only 16; gold people unlisted 11/200; format problems 0; windows with something to look at 23/68
- 16:10 chunk 12 scored: windows 68/68; class 190/357=53%; events gold 77 blind 47 both 31 blind-only 16 gold-only 46; gold people unlisted 0/128; format problems 0; windows with something to look at 13/68
- 16:17 chunks 10 and 12 read and checked clean. Blind reading done: 01-12. Not started: 13-32.
- 16:18 Chunk 12's class agreement is 53% because of one window, a 168-line battles list ("A vs. B") that the
  reader called trivia; the gold rightly has a fought row per line. Not a reader fault: the reader rules did
  not have the list rule. Added it to `blind/RULES.md` for chunks 13 onward. Chunk 12 otherwise checks clean.
- 16:22 Pilot third look A01 (chunks 02+03, 24 flagged windows): gold_ok 17, fix 1, unsure 6. Fable read the
  review file: the one fix is accepted (b39, Locus arrives where Griffith is: met, replacing the fact
  `other_verb arrives`; table "X arrived where Y was" and Addendum 6). Applied as gold_v2/fixes/G133.txt;
  backup for this whole audit: gold_audit_v2.jsonl.bak-pre-train-audit-2026-11-14 (4,216 lines).
  CHANGED TRAIN WINDOWS SO FAR: b39.
  Unsure cases recur as classes for the owner: (1) a single unnamed individual ("the goat-man", "the mayor") as
  an end, which step 6 / A20 allow and the reviewers refused; (2) wars between nations as fought; (3) noticing
  someone then talking as met; (4) a rescue stated only as a purpose. Collect them in `adj/*_review.md`.
  The adjudicator is conservative (it defers to the reviewer's note), so expect few fixes per batch. The third
  look covers events and participants only; fact-layer wording errors need a separate pass.
- 19:45 Usage window reset (1%). Round 2 launched, Opus 5.5 high: readers chunk 13, 14; third look A02 (01+04, 31 windows), A03 (05+06, 37). Built A04 (07+08), A05 (09+11), A06 (10+12) inputs. Launch queue: readers 15..32, then A04, A05, A06, then A07+ from chunks 13+.
- 19:48 chunk 13 scored: windows 68/68; class 270/301=90%; events gold 35 blind 66 both 28 blind-only 38 gold-only 7; gold people unlisted 4/91; format problems 0; windows with something to look at 19/68
- 19:48 chunk 14 scored: windows 68/68; class 301/336=90%; events gold 34 blind 45 both 31 blind-only 14 gold-only 3; gold people unlisted 0/99; format problems 0; windows with something to look at 9/68
- (about 19:50-20:00, clock not read) Third look A02 (chunks 01+04: gold_ok 20, fix 8, unsure 3) and A03 (05+06: gold_ok 30, fix 4, unsure 3) reviewed by Fable. Accepted and applied as G134 (10 windows): b166 +Eriza escaped Guts; b99 +Zepek saved Rosine; b248 Guts saved Farnese/Casca replacing protected facts; b105 +Crow fought Guts only; b83 +Schierke arrived Elfhelm; b447 +Bambietta fought Shinji; b441 +Gerard Valkyrie fought Byakuya; b458 Algora Lallau saved Nikita Deslock/Schutzstaffel replacing protected facts (group row added by Fable for consistency); b340 +Ichigo saved Nel; b288 +Lille fought Shunsui. STRUCK: the awakened-for-transformed_into swaps (b105 five disciples, b169, b69): the gold writes transformed_into for 78 of 82 transformations, so the swap would break a consistent convention (owner question: first transformation = awakened or transformed_into?). Backup gold_v2/bak_train_audit/gold_audit_v2.pre-G134.jsonl. CHANGED TRAIN WINDOWS SO FAR: b39 b166 b99 b248 b105 b83 b447 b441 b458 b340 b288. New unsure for owner: b185, b97, b66, b357, b281 (definite description of one individual), b412 (fled = escaped or departed; awaken his powers).
- 19:52 chunk 15 scored: windows 68/68; class 177/196=90%; events gold 26 blind 33 both 17 blind-only 16 gold-only 9; gold people unlisted 0/87; format problems 0; windows with something to look at 12/68
- 19:54 chunk 16 scored: windows 68/68; class 232/253=92%; events gold 95 blind 117 both 84 blind-only 33 gold-only 11; gold people unlisted 8/210; format problems 0; windows with something to look at 25/68
- (about 19:50-20:00, clock not read) FACT LAYER, script findings (own script facts/fact_layer_checks.py, no project gate): 62 other_verb rows whose verb is not a word of the quote (A88/B.3). Fable read each quote and chose the literal word (facts/build_m1_fix.py holds the table). Applied as G135: 49 windows, 58 rows re-verbed, 2 rows dropped (b647 Power states: no such verb in the sentence, the explains row covers it; b643 Fami reveals/claimed: quote has no verb and the actual reveals row exists). Left: b1538 Reggie told (dedupe workaround: a second 'tells' row cannot exist), b3110 Genus states ('According to Genus', owner list). Windows: b9 b304 b520 b643 b647 b1023 b1085 b1100 b1104 b1111 b1118 b1181 b1224 b1276 b1295 b1376 b1385 b1414 b1442 b1454 b1481 b1494 b1523 b1543 b1547 b1550 b1551 b1579 b1593 b1621 b1634 b1665 b1694 b1695 b1710 b1718 b1724 b1734 b2821 b2826 b2846 b2882 b2900 b2981 b3055 b3066 b3173 b3261 b3264. Backup bak_train_audit/gold_audit_v2.pre-G135.jsonl.
- 19:55 chunk 17 scored: windows 68/68; class 242/286=85%; events gold 119 blind 143 both 101 blind-only 42 gold-only 18; gold people unlisted 2/214; format problems 0; windows with something to look at 31/68
- 19:56 chunk 18 scored: windows 68/68; class 296/336=88%; events gold 110 blind 141 both 96 blind-only 45 gold-only 14; gold people unlisted 5/220; format problems 0; windows with something to look at 33/68
- (about 19:50-20:00, clock not read) chunks 13-18 read and checked clean (name-check alarms on 13, 15, 17 inspected: page-subject pronouns, labels belong to the passage). Third-look batches: A04 (07+08) running with a 'settled practice' paragraph added to the brief (transformed_into stays; a definite description of one unnamed individual is not an end: verdict gold_ok, reason says so). Built A07 (13+14), A08 (15+16), A09 (17). FACT LAYER third look FL launched: facts/FL_input.jsonl (56 windows: unlabelled sentences, outside names, names longer than the window), brief facts/BRIEF_fact_findings.md, outputs facts/FL_{verdicts.jsonl,fix.txt,review.md}.
- 19:59 chunk 19 scored: windows 68/68; class 277/317=87%; events gold 134 blind 164 both 110 blind-only 54 gold-only 24; gold people unlisted 4/232; format problems 0; windows with something to look at 34/68
- (about 19:50-20:00, clock not read) A04 (07+08: gold_ok 30, fix 5, unsure 2) reviewed by Fable; all five accepted and applied as G136: b341 +Isshin met Ryūken; b294 Shisuikyō killed Konoka (event) becomes a claimed fact asserted by Aizen (A113, Add.3 informed); b393 +Senjumaru fought Uryū, +Haschwalth awakened, +Schutzstaffel awakened; b593 Makima met Denji replacing other_verb confronts; b526 +Yoshida met Denji. A04's fix and review files are in the scratch folder (A04/): the subagent's Write tool refused the worktree path because the session's working directory had drifted to big-review-flags; launch agents with the cwd inside this worktree. Unsure for owner: b325 (met at a distance), b299 (Ichigo attacked Kurōdo as an actual fact: fought or other_verb slam). Chunk 19 read and checked.
- 20:01 chunk 20 scored: windows 68/68; class 269/298=90%; events gold 172 blind 193 both 125 blind-only 68 gold-only 47; gold people unlisted 9/262; format problems 0; windows with something to look at 44/68
- 20:04 A05 (09+11: gold_ok 26, fix 4, unsure 2) reviewed by Fable, applied as G137: b623 +Himeno saved Kobeni; b742 +Power escaped Makima (struck: Denji escaped Makima, carried not acting; Kishibe met Denji, 'is shown sitting next to him' states no arrival); b695 +Makima fought Chainsaw Man. STRUCK b751 (Pochita eating the Death Devil as killed: no stated death; note b674 writes consumed devils as killed, owner question). Unsure for owner: b652 (Reze attacked Whip as an actual fact: fought or accident), b625 (acts named only as what a reward is for: implied doer). Chunk 20 read and checked (44 flagged). A06 (10+12) and A07 (13+14) running.
- 20:05 chunk 21 scored: windows 68/68; class 237/268=88%; events gold 144 blind 167 both 113 blind-only 54 gold-only 31; gold people unlisted 7/241; format problems 0; windows with something to look at 40/68
- 20:05 FACT LAYER third look FL (56 windows: gold_ok 17, fix 38, unsure 1) reviewed by Fable in full (facts/FL_review.md) and applied as G138: 38 windows, 61 rows removed, 89 added. Kinds: narrated acts that had no row (A101, other_verb with the sentence's verb; repeat blows of a recorded fight), names shortened to the window's form (A112/A130: Maki Zenin->Maki, Aoi Todo->Todo, Suguru Geto->Geto ...), outside names removed (b1046 Pseudo-Geto rows, b1058 Toge Inumaki and Panda met rows). Checked against practice first: the gold already writes other_verb attack/fight/escape/reunited rows. Re-run of facts/fact_layer_checks.py after it: verb-not-in-quote 2 (b1538, b3110, left on purpose), outside names 0 beyond page subjects, unlabelled sentences 42 (fragments and list pieces). Unsure: b185 s1 (group against group with members tied). Chunk 21 read and checked (40 flagged).
- 20:07 chunk 22 scored: windows 68/68; class 279/304=92%; events gold 189 blind 226 both 155 blind-only 71 gold-only 34; gold people unlisted 1/261; format problems 0; windows with something to look at 38/68
- 20:08 A07 (13+14: gold_ok 21, fix 6, unsure 1) reviewed by Fable, all six applied as G139: b818 +Piccolo awakened, +Piccolo arrived Namek; b872 +Giru arrived M-2; b1019 +Goku/Vegeta arrived Capsule Corporation; b868 defeated quote moved inside one sentence; b850 +Goku met Gohan/Tien/Mr. Satan (Addendum 6, 'appears in the nick of time'); b964 +Sous/Sanka met Brianne. Unsure: b945 ('was sent as an infant to Earth' = arrived?). Chunk 22 read and checked (38 flagged). The two brief files now carry the standing additions (settled practice, battles-list note, scratch-folder helpers, write-refusal note); A08 onward is launched by pointing at adj/BRIEF_adjudicator.md with the three values.
- 20:11 A06 (10+12: gold_ok 26, fix 4, unsure 6) reviewed by Fable, applied as G140: b721 +Makima met Aki/Himeno (Addendum 6); b551 Makima saved Galgali (event) becomes a claimed fact (A113, 'explains'); b926 +Future Trunks fought Android 17; and b753, which the adjudicator left unsure and Fable decided: 'the latter backstabs him' is the Debt Collector betraying Denji, so Denji fought Zombie Devil is removed and Debt Collector betrayed Denji added. STRUCK b567 (Pochita consuming most of Yoru as defeated: same open question as b751/b674, what a devil being eaten is). Unsure for owner: b737 (hostile arrival with no fight: met?), b537 (killing an immortal in training), b728 (master makes unnamed minions kill: which verb for the master), b887 (a game's story arc tagged production while b926's game section is plot), b792 (returning and handing over in person: met?).
- 20:12 chunk 23 scored: windows 68/68; class 250/288=87%; events gold 135 blind 173 both 107 blind-only 66 gold-only 28; gold people unlisted 7/250; format problems 0; windows with something to look at 41/68
- 20:13 chunk 24 scored: windows 68/68; class 289/330=88%; events gold 132 blind 168 both 120 blind-only 48 gold-only 12; gold people unlisted 4/237; format problems 0; windows with something to look at 35/68
- 20:16 A08 (15+16: gold_ok 21, fix 10, unsure 6) and A09 (17: gold_ok 20, fix 7, unsure 4) reviewed by Fable, applied together as G141 (15 windows). A08: b802 +Piccolo arrived Lookout; b837 -Gohan fought Gamisalas (blasts fired to raise dust, A42); b957 +Yajirobe met Goku; b1600 +Sukuna fought Higuruma (interception = fought + saved); b1130 Naobito defeated Dagon becomes other_verb stopped (STOP ruling: a stop inside an ongoing exchange stays a fact); b1330 -Sukuna killed Mimiko, +no_doer tag (passive, no doer in the window; same as dev b3472); b1311 +Megumi arrived Shibuya Tollgate (A138); b1315 Choso met Yuji replacing other_verb arrives; b1782 -Pseudo-Geto met Yuji ('continues his conversation' = meeting already under way) with other_verb continues, +Choso met Yuji. A09: b1065 +Uraume sealed Yuji/Maki (table: trapped in ice), +Uraume met Sukuna, minus other_verb creates; b1640 Gojo met Yuta/Maki/Hakari/Yuji replacing other_verb appears (Addendum 6); b1593 Rika fought Sukuna replacing other_verb restrain; b1422 +Ui Ui met Kusakabe, +Sukuna fought Ui Ui; b1668 Yuji met Nanami replacing other_verb appears; b1307 +Satoru fought Toji. STRUCK: b1060 (Kusakabe met Yuta/Maki from a purpose clause), b1076 (Higuruma 'awakened as a sorcerer' to the event: reviewer ruled no; first gain of powers is written gained_power in this gold, owner question). Unsure for owner: b804, b992, b1705, b1517, b1450, b1710, b1078, b1731, b1775, b1507. Chunks 23, 24 read and checked.
- 20:16 chunk 25 scored: windows 68/68; class 181/224=81%; events gold 85 blind 77 both 59 blind-only 18 gold-only 26; gold people unlisted 11/174; format problems 0; windows with something to look at 25/68
- 20:17 chunk 26 scored: windows 68/68; class 198/235=84%; events gold 32 blind 31 both 21 blind-only 10 gold-only 11; gold people unlisted 7/123; format problems 0; windows with something to look at 15/68
- 20:20 A10 (18: gold_ok 19, fix 6, unsure 8) reviewed by Fable, all six applied as G142: b1444 Yuji met Nanami replacing other_verb breaks; b1584 +Yuji fought Kechizu (attack told in passing); b1547 +Mei Mei/Ui Ui met Yuji ('Team Mei Mei regroups'), the no_relation tag on that clause removed by Fable; b1345 Mei Mei killed Niji Ebina becomes fought (the axe swing is stated, the death is not); b1404 +Pseudo-Geto fought Mei Mei ('almost killed by', revealed = factive); b1348 +Todo met Mai. Unsure for owner: b1605, b1308 and b1598 (first power: awakened or fact), b1642, b1145, b1188, b1762, b1179. Chunks 25, 26 read and checked. Usage 46% at 20:16.
- 20:21 A11 (19: gold_ok 22, fix 10, unsure 2) reviewed by Fable, 7 applied as G143: b1059 +Kuroi arrived Okinawa (name form corrected by Fable: the window was renamed in G138 after the adjudicator's input was built); b1576 Hana fought Sukuna replacing other_verb casts; b1323 +Kento Nanami met Nobara (Addendum 6); b1344 Toji met Naobito/Dagon replacing other_verb coming; b1057 +Maki saved Megumi (interception); b1666 Toji Fushiguro met Nanami/Megumi replacing other_verb comes; b1402 +Choso fought Kenjaku (battle told in passing). STRUCK: b1254 (-Sukuna defeated Kashimo: the page is the battle 'Hajime Kashimo vs. Sukuna', the doer comes from the page subject), b1292 (Haruta woke up as awakened: the knockout is only in the text before the window), b1381 (awakened his cursed technique: reviewer ruled no, first-power question). Unsure: b1528, b1214. NOTE for later batches: adjudicator inputs for chunks 18-24 were built before G135/G138 changed some names and verbs; check every proposed row's name against the window's current rows (final regression: facts/fact_layer_checks.py).
- 20:21 chunk 27 scored: windows 68/68; class 242/289=84%; events gold 87 blind 78 both 50 blind-only 28 gold-only 37; gold people unlisted 6/162; format problems 0; windows with something to look at 18/68
- 20:22 chunk 28 scored: windows 68/68; class 191/245=78%; events gold 93 blind 80 both 60 blind-only 20 gold-only 33; gold people unlisted 7/169; format problems 0; windows with something to look at 20/68
- 20:24 chunk 29 scored: windows 68/68; class 159/185=86%; events gold 61 blind 57 both 42 blind-only 15 gold-only 19; gold people unlisted 1/101; format problems 0; windows with something to look at 12/68
- 20:25 A13 (21: gold_ok 28, fix 6, unsure 6) reviewed by Fable, 5 applied as G144: b1099 +Hanami fought Toge (roots attack dodged); b1260 +Mai saved Momo (stopped Nobara's attack); b1757 +Geto/Mimiko/Larue departed Tokyo Jujutsu High (the gold already has all four arriving, only Nanako leaving); b1667 +Yuji Itadori fought Choso (fight told in passing); b1284 Kashimo fought Panda replacing other_verb applying. STRUCK b1377 (blows withstood by Dagon's shield as fought: the reviewer tagged that clause no_relation on purpose; A42 is arguable). Unsure for owner: b1448, b1360, b1715, b1144, b1038, b1048, b1377. Chunks 27, 28, 29 read and checked. Third-look inputs for chunks 22-24 and 27-29 rebuilt from the current gold (after G135/G138); A14 (22) launched; A12 (20) was built before G138, check its names.
- 20:26 A12 (20: gold_ok 33, fix 6, unsure 5) reviewed by Fable, all six applied as G145: b1047 -Mechamaru fought Mahito (Mechamaru is Kokichi's piloted body; the pair is already recorded); b1594 +Geto/Nanako/Mimiko Hasaba arrived Jujutsu High; b1749 Yuki met Kenjaku replacing other_verb confronts; b1417 +Maki met Nobara Kugisaki (Addendum 6); b1685 +Megumi met Yuta/Maki ('Megami' is Megumi); b1475 +Toji Zenin fought Megumi. Unsure for owner: b1568, b1368, b1678, b1408, b1142. Name regression after it: see fact_layer_checks counts.
- 20:27 chunk 30 scored: windows 68/68; class 186/235=79%; events gold 82 blind 85 both 59 blind-only 26 gold-only 23; gold people unlisted 2/123; format problems 0; windows with something to look at 16/68
- 20:28 chunk 31 scored: windows 68/68; class 165/216=76%; events gold 71 blind 62 both 42 blind-only 20 gold-only 29; gold people unlisted 12/120; format problems 0; windows with something to look at 24/68
- 20:28 A14 (22: gold_ok 30, fix 6, unsure 2) reviewed by Fable, all six applied as G146: b1301 +Yuta fought Kurourushi (fight stated apart from the kill); b1154 +Rika fought Ryu; b1646 +Gojo met Riko (walked in on her); b1424 and b1212 +Toji Fushiguro fought Riko/Geto/Misato ('they were ambushed', rulebook Example 10: one row per named person); b1088 +Yuta Okkotsu arrived Tokyo Jujutsu High (A138). Unsure for owner: b1247 ('heart stopped' then healed: awakened?), b1669 (attempted kill prevented: fought?). ALL 32 CHUNKS ARE NOW BLIND-READ except 32 (running). Chunks 30, 31 read and checked. Running: reader 32, A15 (23), A16 (24), A17 (25+26). Built A18 (27+28), A19 (29+30); A20 = 31+32 to build.
- 20:29 chunk 32 scored: windows 42/42; class 79/102=77%; events gold 26 blind 34 both 18 blind-only 16 gold-only 8; gold people unlisted 3/65; format problems 0; windows with something to look at 11/42
- 20:32 A15 (23: gold_ok 30, fix 7, unsure 4) reviewed by Fable, all seven applied as G147: b1159 -Arata saved Yuji (first aid, the healed fact stays; the same act was both event and fact); b1456 +Yuji met Nanami; b1502 Megumi met Maki/Nanami/Naobito, and Fable also removed other_verb breaks for consistency with b1444; b1537 Toji met Maki/Naobito/Megumi replacing other_verb enters; b1442 +Smallpox Deity fought Mei Mei; b1056 Sukuna attacked Megumi/Jogo/Yuji (facts) become fought events (checked practice: actual attacked facts in this gold are for attacks on things, 4 of 9; a punch on a person is fought); b1735 Yuji fought Sukuna replacing the attempted attack fact (the attacks were made and countered). Unsure for owner: b1384, b1238, b1732 (waking from a domain-induced trance), b1100 (passive defeat, one possible opponent). ALL 32 CHUNKS BLIND-READ AND CHECKED (2,150 windows, 8,453 sentences). Running: A16 (24), A17 (25+26), A18 (27+28), A19 (29+30). Queued: A20 (31+32).
- 20:33 A16 (24: gold_ok 23, fix 6, unsure 6) reviewed by Fable, 5 applied as G148: b1637 Smallpox Deity fought Ui Ui replacing the attempted use fact (attack made, blocked); b1189 +Kenjaku fought Kasumi Miwa (interception = fought + saved); b1252 Yuji met Nanami replacing other_verb breaks (same scene as b1444); b1107 Sotomura met Junpei replacing other_verb caught; b1638 +Eso/Kechizu fought Yuji (Decay used on him). STRUCK b1199 (Yuta met Naoya: Naoya lies defeated, A135 no met when only one party is present). Unsure for owner: b1621, b1337 (a net 'closing in to end his life' as killed), b1061, b1439 and b1609 (first Domain Expansion: awakened or fact), b1210.
- 20:33 A17 (25+26: gold_ok 31, fix 7, unsure 2) reviewed by Fable, 6 applied as G149: b1401 -Kenjaku killed Yuki ('dealing a fatal blow', no stated death; killed NO column), with +Kenjaku wounded Yuki added by Fable so the sentence keeps a row; b2882 +Charlotte Pudding met Luffy/Chopper (A34: she already saves them and meets the other four); b2824 +Fire Tank Pirates fought Big Mom, +Magellan fought Luffy (attacks told in passing; the wounded fact was there without its fought); b2915 -Dragon met Kuma, -Ivankov met Kuma (asking him to stay among people already together); b2826 -Miss Valentine met Zoro ('We return to... ask him further': meeting already under way); b2965 +Roger arrived Shakky's Rip-off Bar. STRUCK b1554 (Yuta met Maki/Toge/Panda on finding them bloodied and battered: A135, and 'his friends' is expanded from another sentence). Unsure for owner: b1170 (unlocking a power; exorcising a named spirit as killed), b2982 ('Orochi's palace' as a proper place). Running: A18, A19, A20 (the last three third-look batches).
- 20:34 A19 (29+30: gold_ok 23, fix 3, unsure 2) reviewed by Fable, 2 applied as G150: b3164 King saved Tareo (event) becomes a claimed fact (A113, 'stating that'); b3292 defeated quote moved inside one sentence. STRUCK b3187 (heartbeat restarts on its own: awakened or healed; same open question as b1247, 'heart stopped' then healed). Unsure for owner: b3182 (restraining as defeated), b3103 (leaving a meeting held in a named place: departed?).
- 20:36 A18 (27+28: gold_ok 26, fix 8, unsure 4) reviewed by Fable, 7 applied as G151: b3042 +Luffy met Law (A34); b3040 Sabo saved Luffy replacing other_verb interfered; b2835 Luffy/Crocodile escaped Impel Down (events) become planned facts ('worked with him to escape' is a purpose; the window never states the escape); b2854 +Jinbe arrived Whole Cake Chateau, +Jinbe/Nami arrived Mirro-World; b2888 +Xiao met Luffy; b2873 four 'arrived Blue Station' rows become located_at facts (boarding there is being there, A151); b3251 Puri-Puri Prisoner met Child Emperor replacing the discovered fact. STRUCK b2995 (Kizaru met Edison: an enemy appearance Addendum 6 left for a reviewer; Vegapunk captured York: 'they' is ambiguous). Unsure for owner: b2878 (awakening a Devil Fruit), b2920, b3002, b2985, b2995. Running: A20 (31+32), the last third-look batch.
- 20:37 A20 (31+32: gold_ok 26, fix 5, unsure 4) reviewed by Fable, 4 applied as G152: b3214 -Saitama fought Gyoro Gyoro ('Saitama's attack' names no target; the text before shows it was on someone else); b3169 -Puri-Puri Prisoner met Baquma (talk inside a battle already under way); b3144 +Saitama arrived Moon; b3100 defeated quote moved inside one sentence. STRUCK b3174 (Gouketsu met Zakos: a hostile arrival, same open question as b737). Unsure for owner: b3262, b3155, b3261, b3065. THIRD LOOK COMPLETE FOR ALL 32 CHUNKS (A01-A20). Usage 75% at 20:37.
- 20:37 Residual check RC launched: facts/RC_input.jsonl (59 windows drawn at random per series from the corrected gold, seed 11: 71 events, 232 facts, 139 tags), brief facts/BRIEF_rowcheck.md; every row judged ok / error / debatable, plus missing rows. Purpose: a measured error rate for what the passes leave behind.
- 20:44 RESIDUAL CHECK RC: 59 windows, 442 rows: 2 reported errors, 0 missing, 20 debatable. Fable: b1377 confirmed and applied as G153 (other_verb destroyed becomes the listed relation destroyed with its object); b1560 struck (Nue fought Noritoshi follows A64, a named sent creature keeps its row). AUDIT COMPLETE. 181 windows changed (fixes/changed_windows.json); gold audit file 4,409 lines; FINDINGS.md sections 3-4 rewritten with the results; OPEN_RULINGS.md lists what waits for the owner. Next: send the training session the changed list; NO training until the owner's go.
- 20:45 Changed-window list sent to the training session (9b-train-claude-level) with: do not train, do not launch runs, refresh from the gold only on the owner's go. Memory note written. Nothing in this worktree is committed.
- 20:47 OWNER: 'Start training'. Forwarded to the training session with the order: refresh s2data from the 4,409-line gold, report counts, then start the planned JJK side-test run. Independent check ready: fixes/verify_refresh.py (copy of the pre-refresh train.jsonl kept in the session scratch folder).
- 20:47 CORRECTION by Fable: the changed list is 184 windows, not 181. Comparing the training file with the gold row by row (fixes/verify_refresh.py) showed three windows that differ only in an event's quote (b868, b3100, b3292: quote moved inside one sentence); the first count keyed events without the quote. fixes/changed_windows.json regenerated with them; FINDINGS.md corrected; training session to be told.
- 20:49 TRAINING STARTED by the training session on the owner's go: run ~/student_runs_local/jjk_side/perline-s2 (sft_qwen.py, same recipe and seed 1 as perline-s1, 402 steps), PID 303558, started 20:48, expected done about 21:25. It reads the refreshed data in jjk_side/s3data/ (s2data is left as it was). Fable's independent check of s3data/train.jsonl (fixes/verify_refresh.py): 2,150 windows, all equal to the gold's latest record; all 184 changed windows equal the gold; per-line target changed in 131 of them (53 were fact-only edits); 0 unchanged windows moved; holdout.jsonl identical to s2data's. Spot-check b39, b340, b1330: the new targets carry the corrections. GPU 99%.
- 21:01 OWNER (after asking what the waiting passages are): use the surrounding sentences to resolve who ('Jogo is effortlessly defeated'), confirm arrivals by what follows, name an unnamed individual by his description ('Kushan Leader') and use it wherever needed; 'Can we implement this'. Design proposed (the model must be given the same context; description-ends stay local to their page; each context-resolved name keeps its evidence sentence; job is about 450 passages: 452 carry a no_doer or crowd_end tag, 730 sentences). OWNER: 'Yes, start pilot'. Prepared: ctx/ADDENDUM_7_DRAFT.md (not yet in the rulings file), ctx/P1_input.jsonl (60 windows: 17 chosen cases incl. b1100 Jogo, b737 Katana Man, b66 Kushan leader and the rows removed under the old rule b1058 b1046 b1330, plus 43 at random from the pool; context 1,600 chars before, 900 after), split into ctx/P1a_input.jsonl and ctx/P1b_input.jsonl (30 each), brief ctx/BRIEF_context_pilot.md with {INPUT} {OUT} {TAG}. Usage 86% at 21:05: over the 85% cutoff, so the two pilot readers (Opus 5.5 high) launch after the reset at 00:40 IST; a timer wakes the session. The pilot proposes only: nothing is written to the gold until the owner has seen before and after.

## HANDOFF 2026-11-14 21:05 IST (owner: "Continue this in a new session Opus 5.5 Medium")
The Fable session stops working in this folder. A new session (Opus 5.5, medium effort) continues from here, in
this same worktree (the files under `docs/` are uncommitted and exist only here). Read this section, then
`FINDINGS.md` sections 3 and 4, `OPEN_RULINGS.md` and `ctx/ADDENDUM_7_DRAFT.md`.

### A. Now: report the training run to the owner
- Run `~/student_runs_local/jjk_side/perline-s2` (trainer PID 303558, started 20:48 IST, about 32 min of
  training plus 4 min of holdout predictions, expected done about 21:25). Logs `jjk_side/perline-s2.log`,
  `s3d.driver.log`. Same recipe and seed 1 as `perline-s1`, trained on the corrected labels in `jjk_side/s3data/`.
- It belongs to the training session (id `local_61b06ecf-891e-4a3e-bf02-a6a19586f4d8`, "Train the 9B student to
  Claude-level extraction"), which scores it and records it in `plan/RESUME_HANDOFF_2026-10-28.md` (worktree
  `big-review-flags`, last Update). Do not rerun or stop anything. Read the result, compare with `perline-s1`,
  and tell the owner in plain words what moved and what it does and does not show (the per-line format still has
  the defects in `FINDINGS.md` section 2; gold-agreement numbers are not "Claude level", see the memory notes).
  If the result is not there yet, wait for it with a background timer rather than polling.

### B. After the usage reset (19:10 UTC = 00:40 IST): the Addendum 7 pilot
The owner approved the design and said "Yes, start pilot". Usage was 86% of the 5-hour window, over the 85%
cutoff, so nothing was launched.
1. `get_usage`: launch only while the 5-hour window is under 85% (owner rule: never use extra credits; the
   training session shares the allowance). Set your own background timer to wake at 00:43 IST.
2. Launch two readers with the Agent tool (`subagent_type: general-purpose`, `model: opus`, `effort: high`: the
   owner's standing choice for readers), keeping the shell's working directory inside this worktree. Prompt for
   each: "Your task brief is the file <abs>/ctx/BRIEF_context_pilot.md. Read it in full and follow it exactly",
   with {INPUT} = `<abs>/ctx/P1a_input.jsonl`, {OUT} = `<abs>/ctx/P1a`, {TAG} = `P1a` (then `P1b`).
3. When they report: read `ctx/P1a_review.md` and `ctx/P1b_review.md` in full. For every proposed change check:
   the evidence sentence is word for word in that window's `page_text_before` or `page_text_after` (verify by
   script, not by eye); the name is what that sentence states, not series knowledge; the row is what the rulebook
   wants; a description-end is one specific individual, not a crowd or a kind. Strike what fails.
4. The pilot PROPOSES ONLY. Write nothing to the gold. You may dry-run on a copy (`fixes/apply.sh dry <file>`)
   to learn whether the writer's gate accepts a name that is not in the passage and a description as an end;
   report what it refuses. The gold record has no field for the evidence sentence yet: it rides in the block's
   why line for now, a schema field is a later decision.
5. Show the owner before and after: counts (changed, unchanged, unsure; by rule 7.1, 7.2, 7.3), and the
   chosen cases in full: b1100 (Jogo), b737 (Katana Man), b66 (Kushan leader), b1058, b1046, b1330 (rows the
   audit removed under the old rule), plus a few from the random part. Then ask for the go.
6. Only on the owner's go: add Addendum 7 to `rulings_2026-11-04/BRIEF.md` (backup first, as Addendum 6 was
   added), then run the full pass over the pool (the 452 training windows with a `no_doer` or `crowd_end` tag,
   plus groups 1, 5 and 6 of `OPEN_RULINGS.md`) with the same pipeline as the audit: readers, your review of
   every change, dry run, backup, `fixes/apply.sh apply GNNN` (next free number G154), log here. Tell the
   training session that the model input must carry the same context (7.4) before any retraining on these labels.

### Rules that hold
- No training is started or stopped by this session; training decisions are the owner's.
- Gold edits only through `big_review_v2.py fix` (`fixes/apply.sh`), only with the owner's approval, dry run and
  backup first. Before calling a gold row wrong, read the window's reviewer note, the catalog (procedure section
  F) and the BRIEF addenda, and check how the rest of the gold writes the same thing.
- Stop a process only by its exact PID. Commit nothing unless the owner asks.
- Say plainly what was not done or not verified. Keep this log current.

## 2026-11-14 21:10 IST: Opus 5.5 session took over (A then B of the handoff)
- Read the handoff, FINDINGS 3-4, OPEN_RULINGS, ADDENDUM_7_DRAFT, BRIEF_context_pilot, memory notes.
- perline-s2 at 21:07: epoch 1 done (train loss .0805 vs s1 .0790). The trainer's own dev F1 is null for BOTH runs
  (the in-trainer scorer does not read the per-line JSON: json_validity 0.0 in s1 too), so it says nothing; the
  comparison has to come from `perline_score.py` on the holdout preds. Background wait on "S3D DONE".
- Pilot inputs checked: P1a 30 windows, P1b 30; b33 and b2812 have no page context (passage not found in the page
  text), so 7.1 cannot apply there.
- `fixes/apply.sh` defaults SCRATCH to the Fable session's scratch folder: set SCRATCH to this session's when dry-running.
- 21:55 perline-s2 DONE (S3D DONE 21:24). Training session scored it (handoff "Update 2026-11-14 21:35"). I re-ran
  `perline_score.py` (scriptengine venv, `--db jjk_side/facts_resolver.db`) on both runs: numbers reproduce exactly.
  All 214, s1 -> s2: class .931/.920, is-event .966/.962, exact people .606/.606, wrong-person .267/.246, missed
  .008/.008, triples .564/.547, verbs .670/.649. Their paired bootstrap: only class moves beyond noise (about -1 pt).
  Caveat: the holdout's 150 windows were NOT in this audit, so the yardstick is uncorrected gold; 131 of 2,150
  targets changed; one seed. No blind audit of s2. Reported to the owner.
- 21:57 usage 5-hour window 90% (reset 19:10 UTC = 00:40 IST). Pilot not launched; background timer to 00:43 IST, then get_usage again.

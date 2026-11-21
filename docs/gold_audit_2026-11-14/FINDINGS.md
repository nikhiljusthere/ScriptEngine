# Is the benchmark gold 100% correct? No. Audit of 2026-11-14

Asked by the owner. Audited by a Fable session, one reader, against the gold's own rulebook
(`plan/EXTRACTION_PROCEDURE_V2.md` sections A to C and catalog entries A20, A88, A105, A155).

Two benchmarks were checked:

1. **The v2 gold rows** of the 64 JJK dev windows, the only windows the current 9B never trained on
   (676 rows: 123 events, 450 facts, 103 tags). Every row read. Sheet: `jjk_dev64_sheet.txt`, row numbers
   below refer to it, `jjk_dev64_key.json` maps them to window ids.
2. **The per-line benchmark** built from that gold for the side test (`jjk_side/s2data/holdout.jsonl` and
   `train.jsonl`), which replaces names by candidate numbers.

Plus script-provable checks on all 214 JJK holdout windows and the 635-window `dev_v3`
(`mechanical_checks.py`).

## 1. The v2 gold rows: close, not clean

| In the 64 clean JJK windows | Count | Share |
|---|---|---|
| Rows wrong by the gold's own rules, in a way that marks a correct answer wrong | 10 of 676 | 1.5% |
| Rows clearly missing (the rulebook requires them) | 11 (9 events, 2 facts) | 9 missing against 123 events present: 7% |
| Sentences with no row and no tag | 3 | |
| Rows that are a judgement call either way | about 13 | 2% |
| Quotes stitched across two sentences (rule broken, score unaffected) | 3 | |

**Wrong rows (10).**
- The verb of an `other_verb` row is not the word in its quote (rule B.3, catalog A88), and the scorer's
  prefix test then rejects the literal form: 244 asked/asks, 246 said/says, 247 told/tells (D29), 539 told/tell
  (D51), 658 said/says, 659 asked/asks (D62).
- An event written as a fact: 382 "Megumi wakes up" is `other_verb wakes` (D40); the same phrase is the event
  `awakened` in row 499 (D49).
- A name or a doer taken from outside the window: 627 "Rainbow Dragon", where the window says only "the
  dragon-like curse" (D58); 650 "Toji killed Kuchisake-Onna" from "The cursed spirit is instantly exorcised",
  which names neither (D61).
- An event the text does not state: 657 "Suguru fought Toji" from summoning spirits and a threat (D62).

**Missing rows (11).** D16 Hazenoki fought Megumi ("worn down by Hazenoki's relentless explosions"). D19 Ogi
Zenin met Maki ("she was confronted by her own father"). D36 Yuji met Megumi ("Yuji shows up"). D38 Gojo met
Megumi and Gojo met Yuji ("Gojo then shows up"; the same phrase gets `met` rows in D41). D45 Toji met Maki.
D52 Megumi met Yuta. D55 Maki Zenin fought Naoya Zenin and Noritoshi Kamo fought Naoya Zenin ("the fight
between ..."). D62 Toji's claim that he killed Satoru Gojo (the whole sentence is unlabelled). D37 Megumi
learned the object was gone ("finds that the cursed object is not there"; the same wording is `learned` in D44).

**Unlabelled sentences (3).** D18 sentence 2, D53 last sentence, D62 "Toji grins and reveals he killed Satoru
Gojo". The script finds 14 such sentences in the 214 holdout windows and 24 in `dev_v3`.

**Patterns that are not single errors but make the gold noisy.**
- One verb, three encodings on one page: "notices" is `learned` (316, 450), `discovered` (483) and
  `other_verb notices` (435, 485, 641).
- A single unnamed individual is tagged `crowd_end` (the grandson 301, 303, 304; the spirit 322, 323; his
  superior 329; the mother 407), although rule A step 6, B.6 and catalog A20 make a definite description of
  one individual a legal end.
- Tags and rows share a sentence (12 exact overlaps in the holdout, 48 in `dev_v3`), although section C gives
  a sentence rows or one tag.
- `wounded` points both ways: the injured person when there is no object (73, 586, 587, 652), the attacker
  when there is one (140, 478, 553, 583, 602, 613, 648). Catalog A105 allows both.
- A name longer than the window writes it ("Naoya Zenin" where the window says "Naoya", 10 rows).

Script checks found no illegal verb, relation, tag or modality and no quote that is not word for word.

This agrees with the earlier blind audit of 40 other windows (1.0% of gold rows wrong, about 10% of valid
statements absent). The gold is good enough to rank two systems. It is not an absolute yardstick: a perfect
extractor would lose about 7% on events to rows the gold lacks.

## 2. The per-line benchmark: the people numbers are wrong for a quarter or more of the ends

`tools/train/perline_build.py` turns each gold name into a candidate number with `num()`, which returns the
first candidate in alphabetical order whose name or any alias shares one word with the gold name
(`eval_extraction.same`). Measured with `perline_mapping_check.py` against a stricter rule:

| File | Gold ends | First match differs from the strict choice | Events with such an end |
|---|---|---|---|
| holdout, all 214 windows | 2,610 | 786 (30.1%) | 231 of 464 (49.8%) |
| holdout, the 64 clean windows | 727 | 199 (27.4%) | 66 of 123 (53.7%) |
| JJK part of the per-line training set, 611 windows | 6,814 | 2,215 (32.5%) | 707 of 1,305 (54.2%) |

The strict rule is itself a heuristic, so 30% is an upper figure. Reading the 22 most frequent pairs, 585 of
the 786 are plainly the wrong target, which puts the floor at 22%. What it picks:

| Gold name | Mapped to | Why |
|---|---|---|
| Yuji (88), Mahito (48), Gojo (28) | Kento Nanami | his stored alias is the raw string "7:3 sorcerer (by mahito) nanamin (by gojo and yuji)" |
| Yuji (90), Satoru (27), Yaga (19), Mahito (17), Hanami (10) | "Fr:..." and "Es:..." pages | 448 of the store's 1,557 nodes are other-language links |
| Sukuna (77), Toji (45), Yuta (33), Yuki (15), Yuka (12) | a battle page such as "Satoru Gojo vs. Toji Fushiguro" | the battle title contains the name and sorts first |
| Sukuna (23) | Chapter 1 | the chapter's title is "Ryomen Sukuna" |
| Sukuna (15) | Rika | her alias is "female spirit (by sukuna)" |
| Noritoshi (21), Geto (12) | Kenjaku | his aliases list the bodies he took |
| Naoya Zenin (15) | Maki Zenin | shared surname, sorts first |

Consequences. The per-line model is being trained on these numbers. The 98.0% candidate coverage reported in
S1 used the same one-shared-word rule, so it is too high. The seed 2 baseline in S3 passes through the same
mapping on both sides, so its agreement figures are consistent with themselves but do not mean "the right
person". No S2 or S3 number says anything about the per-line approach until the mapping is rebuilt.

What a rebuild needs: drop other-language nodes and, for people, battle, chapter, episode and volume nodes
(the store labels them); match a name to a candidate exactly or through the engine's own participant
resolver, never by one shared word; do not match through alias strings that are sentences; resolve a
body-swap alias by the window, not by the alias table.

## Reproduce

```
W=/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
J=/home/goblin/student_runs_big/jjk_side
A=docs/gold_audit_2026-11-14
python3 $A/mechanical_checks.py --tools $W/tools $J/s1/holdout.jsonl
python3 $A/perline_mapping_check.py --tools $W/tools --db $J/facts_copy.db $J/s2data/holdout.jsonl
```

## 3. Corrections applied 2026-11-14 (owner: "correct them, but also look up all the sources")

Before editing I read what section 1 had been written without: the reviewer's own note on each window
(`why` in `gold_audit_v2.jsonl`), the full pattern catalog (procedure section F, A1 to A153), the owner
rulings in `rulings_2026-11-04/BRIEF.md`, and the stored wiki text around each window. That changed the list.

**Two of my findings were wrong. The gold was right and is unchanged.**
- Row 382, "Megumi wakes up" as `other_verb wakes`: catalog A106 rules that ordinary sleep is no `awakened`.
  Row 499 is `awakened` because there he regains consciousness after being freed.
- D19, "she was confronted by her own father" with no `met`: catalog A145 rules that a confrontation that
  becomes the fight gets no `met`.

So section 1 should read 9 wrong rows, not 10, and 4 unlabelled sentences, not 3 (I had missed one in D29).

**Applied** through the project's gated tool (`big_review_v2.py fix`, fix files `fixes/G130.txt` and
`G131.txt`, copies beside this file). Every block passed the event, fact and tag gates. 11 windows changed,
18 rows added, 9 removed; 3,811 windows untouched. The audit file went from 4,201 to 4,213 lines, its old
content is byte-identical, and the backup is `gold_audit_v2.jsonl.bak-pre-audit-2026-11-14`. To undo a window,
append `{"id": "<window id>", "void": true}`.

| Window | Change | Rule | Source check |
|---|---|---|---|
| b3488 Episode 7 | `asked`, `said`, `told` become `asks`, `says`, `tells`; added `Geto other_verb returns` for the unlabelled first sentence | A88, A101 | the tool's own B.3 flags; quotes verbatim |
| b3476 Megumi/Shinjuku | `told` becomes `tell` | A88 | quote verbatim |
| b3467 Geto vs Toji, Prologue | `said`, `asked` become `says`, `asks`; `Suguru fought Toji` becomes `Toji met Suguru`; added `Toji other_verb grins` for the unlabelled reveal sentence | A88, A6, A101 | the page states the attack only in the next section ("sends Rainbow Dragon at him") |
| b3472 Geto vs Toji, Battle | removed `Toji killed Kuchisake-Onna`; added a `no_doer` tag on "The cursed spirit is instantly exorcised" | A8, A110, A112 | the slicing and both names are in the page's previous paragraph, not in this window |
| b3469 Geto vs Toji, Battle | `Toji killed Rainbow Dragon` becomes `Toji killed dragon-like curse` | A112, A130 | "Rainbow Dragon" is named in the previous paragraph only |
| b3486 Dragon-Bone | added `Maki other_verb slashed` for the unlabelled sentence | A101 | "She" is Maki |
| b3511 Megumi/Fearsome Womb | added `Megumi learned -` ("finds that the cursed object is not there") | A133 | |
| b3498 Culling Game | added `Hazenoki fought Megumi` ("worn down by Hazenoki's relentless explosions") | A120 | the previous paragraph has Hazenoki ambushing Megumi |
| b3517 Miyo/Culling Game | added `Maki Zenin fought Naoya Zenin` and `Noritoshi Kamo fought Naoya Zenin` ("the fight between ...") | verb table | the window sets Maki against Naoya; the page has Kamo beside her |
| b3505 Megumi/Shibuya | added `Toji met Maki` | one `met` per newcomer and person | Maki is inside the domain when Toji comes through |
| b3477 Megumi/Shinjuku | added `Megumi met Yuta` | verb table: "X arrived where Y was" | |

**Two true events left the gold on purpose.** The page does have Toji exorcising Kuchisake-Onna and the dragon
being Rainbow Dragon. Neither is stated inside its window, and the rulebook forbids supplying a name or a doer
from outside the window. A model that reads one window cannot know them, so a gold row that does would reward
a guess. This is a cost of cutting pages into windows, and an argument for the per-line design with the page's
entity list.

**Left unchanged, for a ruling.**
- b3467 "Toji grins and reveals he killed Satoru Gojo": whether the kill is written, and how. The wiki's own
  Aftermath section repeats "reveals that he killed Satoru Gojo", its Battle section has him stabbed through
  the neck and forehead, and the Rematch page has him alive. The clinical-death ruling keeps a stated kill
  whose victim returns; a kill known only from a character's telling is a `claimed` fact (A113).
- D53, last sentence unlabelled: the tool stores one row per subject, relation, object and modality, and
  `Miyo other_verb invites` already exists from another sentence.

**Not done here.** The composed sets still hold the old rows: `student_v2_short/dev.jsonl`, `student_v3_split/
dev_v3.jsonl` and the JJK holdout need a recompose, and the gold lint a re-run. The other 150 JJK holdout
windows and the 3,758 other gold windows were not read.

## 4. Owner ruling 2026-11-14: "shows up" between companions is a meeting

Asked "Should 'shows up' between companions count as a meeting in the gold?", the owner answered "Yes, add
met". Recorded as Addendum 6 in `series/universal/training/big/rulings_2026-11-04/BRIEF.md`. Applied through
the same gated tool (fix file `fixes/G132.txt`, copy beside this file), all three blocks passed:

| Window | Change |
|---|---|
| b3512 Megumi/Fearsome Womb (dev) | added `Yuji met Megumi` ("Yuji shows up by crashing through a window") |
| b3515 Megumi/Fearsome Womb (dev) | added `Gojo met Megumi` and `Gojo met Yuji`; removed the fact `Gojo other_verb shows`, since an event is never also a fact |
| b1229 Yuji/Vs. Mahito (train) | added `Nanami met Yuji` beside the existing `saved` and `fought` rows (A34) |

The audit file now has 4,216 lines; its original 4,201 are still byte-identical. A sweep found 33 gold
sentences with "show(s/ed) up", 19 of which already had a `met` row, so the ruling matches what the gold mostly
did. Three sentences where the one who shows up is not a companion (b1088, b2995, b723) were left alone. The
14k big set was not swept.


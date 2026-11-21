# The 9B student against Claude: where it stands and what to do

2026-11-14. Independent analysis by a Fable session, for the session training the Qwen3.5-9B extraction
student (worktree `big-review-flags`). Scope changed by the owner the same day: Marvel is out; the targets
are Dragon Ball, Naruto, Jujutsu Kaisen and Hunter x Hunter.

Evidence files: `docs/9b_student_analysis_2026-11-14/` (the blind sheet, its key, my verdicts, two scripts).

## Verdict

The student is not held back by too little training of the present kind. It is held back by the yardstick,
by a label space with more than one right answer, and by two real defects.

1. **The F1 number cannot reach "Claude level", because a blind Claude does not reach it either.** On the
   55 dev_pool windows the training session's two Opus 5.5 labellers finished, a blind Claude agrees with
   the gold at events .60 / facts .36 / tags .50. Seed 2 on the same windows: .61 / .51 / .62. The student
   already agrees with the gold better than Claude does without the rulebook.
2. **Half of what the scorer counts as an error is not one.** I judged all 248 rows the student and the gold
   disagree on, in 40 dev_pool windows, with the source hidden. 126 of them (51%) are the same statement
   written two legal ways (`learned` / `discovered`, `located_at` / `resides_at`, a typed relation against
   `other_verb` with the same verb, a row against a `crowd_end` tag for an unnamed individual).
3. **The student cannot reproduce its own training labels either.** On windows it trained on it scores
   facts .60 and tags .55, the same as on unseen windows. The label is not a function of the passage: the
   gold writes one verb several ways. Until one statement has one legal encoding, no amount of training
   moves the strict score much.
4. **The real gap to the gold is 5.1% wrong rows against 1.0%, and about 20% of statements missed.**
   Those two numbers are what the work should move. The .59 will not show it.

## What was measured

| Measurement | Result |
|---|---|
| Seed 2 (`best` = epoch 1) on dev_pool, 151 windows | events .588, facts .561, tags .627 (events CI .477 to .697) |
| Epoch 2 against epoch 1, dev_pool | events .585 against .588: flat. Train loss .051 against .070 |
| Seed 2 on the 89 dev_pool windows outside Marvel and MCU | epoch 1: events .621, facts .508, tags .625. Epoch 2: .684, .548, .626 |
| Blind Opus 5.5 against gold, 55 windows (no Marvel/MCU) | events .597, facts .363, tags .500 |
| Seed 2 against gold, the same 55 windows | events .608, facts .507, tags .618 |
| Gold against itself: one sentence in two train windows (5,418 pairs, after the recon pass) | events .932, facts .915, tags .869 |
| Blind row audit, 40 windows: student rows judged wrong | 15 of 295 = 5.1% |
| Blind row audit: gold rows judged wrong | 3 of 315 = 1.0% |
| Blind row audit: valid gold statements the student has no row for | 58 of 315 (72 counting the defensible ones) |
| Blind row audit: valid statements the gold has no row for | 32 (40 counting the defensible ones) |
| Review of the 14k big windows: drafted rows Claude dropped or changed | events 7,687, facts 25,034, tags 5,662 |
| Review of the 14k big windows: drafted rows Claude kept | events 21,530, facts 41,845, tags 24,703 |

Limits of the audit: one judge (me), 40 windows, judged against the short system prompt only, and the 181
rows both sides agree on were taken as correct. So both wrong-row rates are floors, and the audit should be
repeated on each new candidate rather than quoted as final.

### The student does not reproduce its own training labels

Seed 2 (`best`) on 180 windows drawn from its own training set, each seen once (GPU run, 865 s):

| Trained-on windows | events | facts | tags | sentences with a row or tag |
|---|---|---|---|---|
| gold_v2, series outside Marvel and MCU (50) | .851 | .602 | .619 | 99.4% |
| gold_v2, Marvel and MCU (50) | .582 | .627 | .601 | 95.2% |
| big set (80) | .560 | .593 | .452 | 95.8% |

On facts and tags the student scores the same on windows it trained on (.60 and .55) as on windows it has
never seen (.56 and .63). There is no generalisation gap there for more data of the same kind to close. The
one gap is events outside Marvel: .85 on trained windows against .62 to .68 held out, so labelled windows
from the target series do carry over. Two of the 180 answers ran to the 4,096-token cap and did not parse.

### One verb, several labels

Why a seen label is not reproduced: the gold writes the same surface verb more than one way. Rows in train
whose quote (160 characters or less) contains the verb:

| Verb in the quote | How the gold labelled it |
|---|---|
| realized (770 rows) | `learned` 53%, `other_verb` with that verb 21% |
| discovered (703) | `learned` 40%, `discovered` 22% |
| believed (400) | `suspected` 36%, `other_verb` with that verb 25% |
| questioned (321) | `other_verb` with that verb 61%, `interrogated` 11% |
| noticed (285) | `other_verb` with that verb 35%, `learned` 16%, `discovered` 9% |

The count is crude (it includes other rows on the same clause, and tags where an end is a crowd), so read
it as the pattern, not as rates. The rulebook allows it: rule A133 in `plan/EXTRACTION_PROCEDURE_V2.md`
accepts either `learned` or `other_verb` with the quote's verb.

### The training set teaches two conventions

81% of train is the big set (Marvel and MCU pages, 35B drafts corrected by Claude). The dev and test splits
are 100% gold_v2. The two are not labelled to the same depth:

| Per 1,000 passage characters | train gold_v2 | train big | Seed 2 on Marvel+MCU dev_pool | gold on the same |
|---|---|---|---|---|
| `other_verb` facts | 6.33 | 4.78 | 5.06 | 6.38 |
| tags | 5.09 | 3.47 | 4.93 | 4.93 |
| sentences with a row or a tag | 98.7% | 95.0% | 93.0% | 98.6% |

The schema says every sentence carries a row or a tag. One in twenty big-set sentences carries neither, and
the student reproduces that on Marvel and MCU text. Outside Marvel it does not: on the trained windows from
the other series its coverage is 99.4%. So this defect mostly leaves with Marvel. What it leaves behind is
a question step 3a answers: whether 15,000 Marvel and MCU windows help the four target series at all.

### What the wrong rows are

Of the 15 student rows I judged wrong: 5 name the wrong person (a pronoun or "Both" resolved to the wrong
character, and one fight between two names of the same man), 2 turn a passive around (the invited guest
becomes the inviter), 3 are tag mistakes, and the last 5 are one each of an over-read verb, an ability
written as a row, a row taken from dialogue, a quote that is not word for word, and a row that contradicts
the student's own tag.

## Plan, in order

**0. State.** Seed 1 is dead: the storage session stopped it at 04:17 and moved the runs to
`/media/goblin/HDD/Ubuntu Offload/projects_drive/training/student_runs_big/` (NTFS, no link left at
`/mnt/PROJECTS/student_runs_big`). Do not re-run it as it was. A second seed is still needed, but of the
recipe that comes out of steps 2 and 3.

**1. Fix the yardstick before any more GPU.**
- 1a. A dev set of 600 windows or more, none from Marvel or MCU, page-disjoint from train: hold out about
  450 of the 2,300 non-Marvel gold train windows and add the 153 existing non-Marvel dev windows. Test stays
  sealed. At 151 windows no arm under +.10 can be told from noise.
- 1b. Report every run two ways: the strict score as today, and a statement-level score that normalises
  both sides before matching. The 48 same-statement groups in `verdicts.txt` are the starting table.
  Scoring only; no label on disk changes.
- 1c. Report three gates as numbers: sentence coverage, word-for-word quotes, `fact_gate` legality.
- 1d. The real bar is the blind row audit (`build_sheet.py`, then `unblind.py`), run by Claude on every
  candidate. Baseline: student 5.1% wrong, about 20% missed. Gold: 1.0% wrong.

**2. One statement, one encoding.** This is the largest lever and needs no GPU to prove.
- 2a. Mine the confusions: run seed 2 over about 2,000 train windows and list, for rows on the same quote,
  which label pairs the gold and the student swap most. Together with the verb table above and the 48 audit
  groups, that gives the list of overlapping encodings.
- 2b. Write a deterministic normaliser from that list (a lemma table: which verbs become which relation,
  which of two near-identical relations survives). Apply it to both sides and re-score seed 2. No retrain:
  this shows at once how much of the .59 was encoding.
- 2c. Compose a copy of the training set with normalised targets (`student_v3`; the gold on disk is not
  touched) and train on it. Judge by the blind row audit, not by the strict score.

**3. Training arms, each judged on the new dev set.**
- 3a. Does Marvel data help these series? Compare the full set, the non-Marvel gold alone (small: two to six
  epochs, well under an hour), and the full set followed by a last stage on non-Marvel gold. The last one
  needs an option in `sft_qwen.py` to start from an adapter; it has none today.
- 3b. A reviewer task. The big-set review holds 38k rows Claude rejected or rewrote and 88k it kept: build
  (passage, one row) to keep or drop from `labels_v2.jsonl` against `big_audit_v2.jsonl`, train it with the
  extraction task, and run it over the student's own rows. Extraction-only training never shows the model a
  wrong row. Check it on my 248 verdicts first: it must drop the X rows without dropping the V rows.
- 3c. Names from the wiki's own links in the prompt ("Moon Knight = Marc Spector"). Aimed at the largest
  class of wrong rows. Needs a recompose; do it if the audit after 2c and 3b still shows wrong-person rows
  leading.
- 3d. More epochs or rank only on the normalised targets. On today's targets the student under-fits because
  the targets are not a function of the input, and a larger fit would only memorise which of two legal
  encodings each window happened to get.

**4. The extraction run for a series (JJK, then HxH, then DB, then Naruto).**
Two adapters extract. Mechanical gates drop rows with a non-verbatim quote or an illegal end. Rows both
adapters wrote are kept; rows only one wrote go to the reviewer pass. An answer that does not parse is
retried. Any sentence left with no row and no tag is asked again; what is still open goes to a Claude review queue. Before a series is called done, Claude
audits 300 random rows blind for the wrong-row rate and extracts 60 random windows independently for recall.

**5. Labels for the series that have none.** HxH has no labelled window. Naruto is not crawled. DB has 256
train windows. For each, draw the blind evaluation sample first and seal it, then pick about 300 windows
where the two adapters disagree most and label those by hand, then retrain. Events are where this pays:
.85 on trained windows against .62 to .68 held out.

**Not worth GPU time now:** more seeds or epochs of the present recipe on the present targets (epoch 2
changed nothing on dev_pool), and the weight-space edit (nothing here suggests it touches recall or
wrong-person rows).

## What "100%" can mean for these four series

No extractor is flawless against this schema. The gold disagrees with itself on about one row in ten when
the same sentence appears twice, and I judged 1% of its rows wrong. What can be made exactly 100% and
checked by a script: every sentence of every window ends with a row or a tag, and every quote is word for
word. What can be measured but not guaranteed: the share of wrong rows and the share of missed statements.
The 9B alone is at about 5% and 20% today. A fair target after steps 2 to 4 is 2% and 10% or better, with
the uncertain windows reviewed by Claude rather than shipped. That target is a goal, not a result.

## For the owner to decide

- Decided 2026-11-14 ("Yes, MCU out too"): MCU leaves with Marvel as a target. Their labelled windows stay
  available as training data, subject to what step 3a shows.
- Whether the normalised encoding of step 2 becomes the schema itself (the gold rewritten, the rulebook
  amended) or stays a transform applied at compose and scoring time. The plan assumes the transform.
- Naruto needs a crawl, an audit and its citation grammar before anything else can happen for it.

## Reproduce

```
W=/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
S=/home/goblin/ScriptEngine/series/universal/training/student_v2_short
R="/media/goblin/HDD/Ubuntu Offload/projects_drive/training/student_runs_big/9B-v2-short-a16-lr1e-4-s2"
E=docs/9b_student_analysis_2026-11-14
python3 $W/tools/train/score_layers_v2.py --gold $S/dev_pool.jsonl --pred "$R/dev_preds_e1.jsonl" --pred $E/blind_claude_55.jsonl
python3 $E/unblind.py --sheet $E/adjudicate_sheet.txt --key $E/adjudicate_key.json --verdicts $E/verdicts.txt
```

`blind_claude_55.jsonl` is a copy of the training session's two partial labeller files. The saved sheet was
drawn with 8 Marvel, 8 MCU and 4 windows from each of the other six series; `build_sheet.py` draws an equal
number per series.

## Addendum: measured against the repo's own definition of 100%

Asked by the owner the same day: is there a system other than windowing and labelling. The definition
(`franchise_kit/RUNBOOK_100.md` §0 and `reports/comprehension/COMPREHENSION_REMAINDER.md` §5) asks four
things: every line served by `/context`, every line classified with its events carrying participants and a
timeline position, every fact traceable, and a reasoning bank answered from served evidence. Per line it
asks for a class (event, standing state, trait, trivia), a participant set and an `arc_index`. It does not
ask which of 62 relations a line is. The table built to hold exactly that, `meaning`, has 0 rows on JJK.

Seed 2's existing dev_pool predictions, re-scored on those per-line questions (`score_per_line.py`, 445
sentences, epoch 2; no retraining):

| Per sentence | 9B F1 | Blind Opus F1 (its 55 windows) |
|---|---|---|
| carries a statement, or only a tag | .916 | .889 |
| is an event | .835 | .708 |
| coarse dimension (event, relationship, interaction, possession, identity, state, knowledge, other) | .750 | .577 |
| people named | .792 | .755 |
| set of people exactly the gold's | 52.0% of sentences | 47.8% |

So the coarse questions are far more settled than the fine labels, and the weak field is who takes part,
for Claude as well as for the student.

What the wiki gives for participants without a model, on JJK's 3,727 verified events in `facts.db`:

| Both ends of the event are | Share |
|---|---|
| linked somewhere on the same page (or are the page itself) | 77.9% |
| linked on the page, or named in the quoted clause by a stored name or alias | 95.2% |
| named in the quoted clause (no pronoun, nothing implied) | 65.2% |

The 95.2% is an upper estimate: these events survived a resolver that already required their names to
match the alias table. A page links a median of 35 entities.

Proposal. The owner approved a side test of it on JJK the same day ("Yes, get JJK to true 100% first"), and
put the other series on hold; nothing is adopted until that test reports. Fill `meaning` by visiting every sentence and having the model choose its
class and its participants from the page's entity list, with the timeline from the citation chain; use
cross-page agreement (the same event on both characters' pages and the chapter page) as the check that
needs no labels; keep the 12 event verbs, and stop typing the 62 relations unless a door reads them. The
existing 18k labelled windows re-project onto this target. None of this has been tested.

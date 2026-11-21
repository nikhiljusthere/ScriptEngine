# The 2,150 training passages and the per-line format: audit of 2026-11-14

Asked by the owner: were all 2,150 passages checked, fix their errors against the downloaded Fandom pages,
and is the structure being trained on correct. File audited:
`~/student_runs_local/jjk_side/s2data/train.jsonl` (2,150 windows, 8,453 sentences, seven series).

Status: the text of every passage is checked (section 1). The labels of every passage have been read a second
time and corrected (sections 3 and 4): 184 passages changed. The format has defects that need a redesign
(section 2). Open questions for the owner: `OPEN_RULINGS.md`.

## 1. Passage text against the downloaded pages (all 2,150, by script)

| Result | Passages |
|---|---|
| Found word for word in the page body as stored | 1,909 |
| Found word for word, sentence by sentence, in the page lead | 168 |
| Not in the stored text but in the raw downloaded wikitext | 54 |
| Only partly matched in the raw wikitext (tables, lists, transcluded text) | 18 |
| Not matched in the raw wikitext by a crude matcher | 9 |
| No downloaded file located under that title | 3 |

So 2,131 of 2,150 are confirmed against the downloaded page and 30 need a person to look
(`passage_fidelity.py`; the last three rows).

22 passages carry a hole or residue where the parser dropped a term or left template text, 17 of them on
Bleach (`passages_with_text_holes.json`). Examples: "The Shihakushō is composed of a white , a black , a
black , a white hakama-himo, white , and ." and "Grimmjow's special is , where he unleashes"; one keeps
"{{W|Kendo|kendō}}"; two keep table styling ("7px|7px|7px|7px}} text-align:center"). These are parser
defects on that wiki's term template, to be fixed in the parser or its overrides and re-windowed, not in
the labels.

## 2. Is the per-line format right? Not as built

Measured on the training file (`labels_and_structure.py`, the part that reads targets only):

| Defect | Count |
|---|---|
| Lines classed `event` where nothing happened: only a plan, an attempt, an order or a claim | 142 |
| Gold fact rows that are plans, attempts, orders, claims or hypotheticals, all folded into lines with no marker | 1,124 of 8,195 |
| Event triples with no object although the verb needs one (the object was not on the candidate list) | 146 of 2,811 |
| Gold events lost on their line because an end was not on the list | 153 |
| Lines cut after an abbreviation ("Dr.", "vs.") | 171 |
| Lines under 12 characters (citation markers and fragments as their own "sentence") | 504 |
| `event` lines with nobody in them | 478 |
| Lines that state a relationship, identity or possession, kept only as "standing state" plus a list of numbers | 244 |
| Non-entity pages still among the candidates (battle, chapter, other-language) | 375 of 25,773 |

What follows from it:
1. **A plan reads as a fact.** The format has no field for "did it happen". The gold has one (modality) and
   the conversion throws it away.
2. **A participant who is not on the list disappears**, and the event with them, or it becomes a triple with
   a hole. Strict list coverage is 95.8%, so about one end in 24.
3. **The sentence splitter breaks sentences**, and each fragment becomes a line with its own class.
4. **`event` is too wide to be useful**: narrated acts, speech, crowd scenes and plans are one class, 63% of
   all lines.
5. **Relations are dropped.** "Ogi Zenin is Maki's father" becomes "standing state, people 5 and 9". The
   100% definition asks for relationships, affiliations and abilities as structured rows; this format cannot
   produce them.
6. **`people` mixes characters, items, places and techniques**, with no roles outside the event triples.

A format that would hold up, per line: class; whether it happened (actual, planned, attempted, ordered,
claimed, hypothetical); characters and things as separate lists; event triples; for state lines a typed pair
(relation, a, b); and a slot for a participant named in the text but not on the list. The candidate list
should carry each entry's type from the store and drop non-entity pages. Citation markers should stay
attached to their sentence, since they are what places it in a chapter.

The run in progress still answers the side test's narrow question, whether picking from a list beats typing
names. It should not be taken as the production format.

## 3. The labels of all 2,150: two independent readings, a third look, then my review

Why not the existing checks: the project's gate validated every one of these labels when they were written,
so it cannot find what it already accepted, and it does not judge meaning. A reviewer who is shown the
existing rows tends to confirm them and is worst at seeing what is missing.

What was done (all of it logged step by step in `STATE.md`):
1. **Blind second reading** of every passage, sentence by sentence, by readers who never saw the gold
   (Opus 5.5 high, 32 chunks, `blind/`). Calibrated first on 64 JJK windows whose errors were known: the blind
   reading found 8 of the 9 events the corrections had added and none of the 2 they had removed. Every chunk
   was checked for the right passages in the right order.
2. **Comparison per passage** (`blind/compare_windows.py`): 699 of the 2,150 passages had an event or a person
   on which the two readings differed.
3. **Third look** on those 699 by a reader holding the rulebook, the owner rulings and the reviewer's own
   note on the window (`adj/`, batches A01 to A20). Verdicts: gold right 503, correction proposed 119, unsure 77.
4. **Fact layer**, by my own script (`facts/fact_layer_checks.py`, nothing from the project's gate): 62
   `other_verb` rows whose verb was not a word of the quote, 5 names taken from outside the passage, 21 names
   written longer than the passage writes them, 69 sentences with no label. The verb forms I fixed row by row;
   the rest went to a reader with the rulebook (56 passages: 17 gold right, 38 corrections, 1 unsure).
5. **My review of every proposed correction** against the sentence, the rule and, where a convention was at
   stake, the rest of the gold. I struck the proposals for 16 passages in full and for 2 in part, amended 6 (a stale name form, a tag, a
   twin fact, a row to keep the sentence labelled) and decided one the reader had left open (b753).
6. **Writing** through the project's fix tool, a dry run on a copy first, a backup before each batch
   (`gold_v2/bak_train_audit/`), fix files `fixes/G133.txt` to `G153.txt`. The audit file grew from 4,216 to
   4,409 lines and its old content is byte-identical.

## 4. Result

184 of the 2,150 passages changed (8.6%). List: `fixes/changed_windows.json`. (First counted as 181: three
passages changed only in the quote of an event, which the first count did not see; found when the training
file was compared with the gold row by row.)

| Change | Count |
|---|---|
| Events added (met 49, fought 39, arrived 17, saved 10, others 11) | 126 |
| Events removed (not stated, wrong person, outside doer, a plan or claim written as fact) | 27 |
| Events renamed to the passage's own name form | 21 |
| Events whose quote was moved inside one sentence | 3 |
| Facts: verb set to the word in the quote | 56 |
| Facts added (narrated acts that had no row; claims moved out of events) | 48 |
| Facts removed (twins of an event, outside names, verbs not in the sentence) | 34 |
| Facts renamed to the passage's own name form | 31 |

Against 2,528 events before: 5.0% were missing and 1.1% were wrong, close to what the 64-window audit
predicted (7% and 1.5%). Events now 2,626, facts 8,209, tags 4,726.

**What is left, measured.** After all corrections a reader checked every row of 59 passages drawn at random
(442 rows: 71 events, 232 facts, 139 tags; `facts/RC_review.md`). It reported 2 rows in error, 0 missing rows
and 20 debatable rows. I confirmed one error and fixed it (b1377); the other follows a catalog ruling (A64: a
named summoned creature keeps its own row). So about 1 row in 400 clearly wrong, and about 1 in 22 a judgement
call. Limits of that number: the checker was shown the rows, which favours confirming them; and one sample of
59 cannot rule out an error rate up to about 1.5%.

**What this audit does not claim.** The fact rows were checked by script for the error kinds the dev audit
found, and by that sample; they were not re-read one by one. 78 passages stay as they were because the
question is the owner's: `OPEN_RULINGS.md`. The passage text problems of section 1 and the format defects of
section 2 are untouched.

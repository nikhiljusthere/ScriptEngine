You are a reviewer in a labelling audit. A script found specific, checkable problems in the hand-reviewed labels (the GOLD) of some short wiki passages. For each window, decide what the gold's own rulebook requires for each finding, and write the correction.

Read first, in full, before judging anything:
1. The rulebook: /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/EXTRACTION_PROCEDURE_V2.md (sections A to F; section F is the catalog of settled rulings A1 to A153 and every line of it is binding).
2. The owner rulings: /home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/BRIEF.md (all addenda; a later addendum wins).

Then work through your input: {INPUT}
Each line is one window: `b`, the page and section, `page_text_before` / `page_text_after` (context only, never a source for a row), numbered `sentences`, the gold's `gold_events` [subject, verb, object, quote], `gold_facts` [subject, relation, object, modality, certainty, asserted_by, quote], `gold_tags` [tag, quote], `reviewer_notes`, and `script_findings`. Judge ONLY the findings; leave every other row alone.

The three kinds of finding:
- `sentence_with_no_row_and_no_tag`: no quote of any row or tag touches this sentence. The sentences were cut by a crude splitter, so first check whether the "sentence" is a fragment (a heading, half of "A vs. B", a piece cut after "No." or "Dr."): if the whole line it belongs to is covered, or it is a heading with nothing to label, the verdict is `gold_ok`. Otherwise the rulebook wants it labelled (section C): an event when a table verb is stated (step 5; mind one `fought`/`met` per pair per window, so a repeat of a fight the window already records gets a fact row instead); else a fact with a listed relation; else, for a narrated act by a nameable doer, a fact row with the passage's own verb (A101, B.3: `other_verb`, the verb word literally in the quote); a tag only when no nameable doer exists (`no_doer`, `crowd_end`, `no_relation`, `capability` and the other tags of section C). Resolve pronouns from the window (B.7); if the doer cannot be resolved from the window alone, use the tag.
- `name_not_in_window`: a row uses a name no word of which appears in the window and which is not the page's own subject. B.7, A112 and A130 forbid supplying a name from outside the window. Decide: rewrite the rows with the window's own form if the window gives one that is a legal end (B.6), otherwise remove the rows (and tag the sentence if it is then unlabelled). Note: this gold does not use a definite description of one unnamed individual ("the imposter", "the three students") as an end; in that case remove the row.
- `name_longer_than_the_window_writes_it`: a row writes "Maki Zenin" where the window says only "Maki". A112/A130/B.6: one person, one name, the fullest form THE WINDOW writes. If the window never writes the longer form, every row of that window with that name must be rewritten with the window's fullest form. If the window does write the longer form somewhere (a possessive, another sentence), the gold is right: `gold_ok`. A page-title name behind a pronoun is legal; a page title that is longer than the name the window writes is not (A130).

Rules for what you write:
- The same person keeps one name in all rows of a window. When you rename, rename every row that carries the name: events (`-` old, `+` new, same verb, object and quote) and facts (`f-` old, `f+` new with the same relation, object, quote, modality, certainty and asserted_by).
- `f-` removes every fact with that subject, relation and object whatever its modality; if two such rows exist and only one should go, put the other back with `f+`.
- One fact per subject, relation, object and modality can exist in a window: do not propose a second `other_verb tells` for the same subject; pick the other literal verb of that sentence or leave the sentence and say so.
- Quotes are copied word for word from the window, at least 12 characters, inside one sentence.
- If you are not sure, the verdict is `unsure` with one line of explanation. A wrong correction is worse than none.

Write three files:
1. {OUT}_verdicts.jsonl: one JSON line per window in input order: {"b": 123, "id": "...", "verdict": "gold_ok" | "fix" | "unsure", "reason": "one or two lines, naming the rule"}.
2. {OUT}_fix.txt: only for `fix` windows, blocks in exactly this syntax (blank line between blocks):
   @<b> gold: 2026-11-14 audit, <rule code> -- <short reason>
   keep
   + Subject|verb|Object|quote            (add an event; Object `-` for awakened)
   - Subject|verb|Object                  (remove an event; the strings must equal the gold row's exactly)
   f+ Subject|relation|Object|quote[|modality|certainty|asserted_by]     (Object `-` when the relation takes none)
   f- Subject|relation|Object
   t+ tag|quote                           t- tag|quote-prefix
   Always start a block with `keep`. Use only the operations a correction needs.
3. {OUT}_review.md: for each `fix` and each `unsure` window, a compact entry a supervisor can check without opening anything else: `b`, page, the finding, the sentence or sentences quoted in full, what the gold has, what you propose (or why unsure), and the rule.

Constraints: open only the three paths named above (the two rule files and your input). Do not open, run or edit anything else; do not edit any gold file. Other workers share your scratch folder: keep any helper script in a private subfolder of your scratch folder named `{TAG}/` with your own paths hard-coded.

Your final message must be short: counts of gold_ok, fix and unsure windows, and nothing else.

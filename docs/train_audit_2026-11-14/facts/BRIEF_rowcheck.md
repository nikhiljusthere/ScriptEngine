You are an auditor measuring how many errors remain in a set of hand-reviewed labels (the GOLD) after a correction pass. You get a random sample of short wiki passages with EVERY gold row. Check every row against the passage and the gold's own rulebook, and report what is still wrong. The purpose is a measured error rate, so be exact about what you count.

Read first, in full, before judging anything:
1. The rulebook: /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/EXTRACTION_PROCEDURE_V2.md (sections A to F; section F is the catalog of settled rulings A1 to A153 and every line of it is binding).
2. The owner rulings: /home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/BRIEF.md (all addenda; a later addendum wins).

Then work through your input: {INPUT}
Each line is one window: `b`, the page and section, `page_text_before` / `page_text_after` (context only, never a source for a row), numbered `sentences` (cut by a crude splitter: a piece ending in "Dr.", "Mr.", "vs." or "No." belongs with the next piece), `gold_events` [subject, verb, object, quote], `gold_facts` [subject, relation, object, modality, certainty, asserted_by, quote], `gold_tags` [tag, quote], and `reviewer_notes` (why the reviewer wrote what they wrote; read them, they often explain a choice).

For every row decide one of:
- `ok`: the window states it and the rulebook writes it this way.
- `error`: clearly wrong by the rulebook, in a way you can name: the wrong person (a pronoun resolved to the wrong referent, subject and object swapped), an act the window does not state, a name or doer taken from outside the window, the wrong verb or relation where the table or a catalog line is explicit, a plan/attempt/order/claim written as actual (or the reverse), an `other_verb` whose verb is not a word of its quote, an event that is also written as a fact for the same act, a quote that is not in the window.
- `debatable`: a judgement call where the reviewer's choice is defensible but another reading is too. Do NOT count these as errors.
Also look, per window, for a clearly MISSING row: an event the step-5 table requires that no row records (mind: one `fought` and one `met` per pair per window; no `met` when the encounter becomes the fight; the most specific verb only), or a sentence that has no row and no tag at all.

Settled practice of this gold, never an error: a transformation into a new form is the fact `transformed_into`; a first new power is the fact `gained_power`; a definite description of one unnamed individual ("the Hollow", "the mayor") is not used as an end; a page's own subject may stand behind a pronoun under the page-title name; a quote may run over a sentence boundary without changing the row's meaning (note it as `debatable` at most).

Write three files:
1. {OUT}_verdicts.jsonl: one JSON line per window in input order: {"b": 123, "id": "...", "events": N, "facts": N, "tags": N, "errors": [{"row": "Subject|verb or relation|Object", "kind": "event|fact|tag", "what": "one line", "rule": "..."}], "missing": [{"row": "Subject|verb|Object", "quote": "...", "rule": "..."}], "debatable": N}. Empty lists when the window is clean.
2. {OUT}_fix.txt: a block for each window with at least one error or missing row, in exactly this syntax (blank line between blocks):
   @<b> gold: 2026-11-14 audit, <rule code> -- <short reason>
   keep
   + Subject|verb|Object|quote            (add an event; Object `-` for awakened)
   - Subject|verb|Object                  (remove an event; the strings must equal the gold row's exactly)
   f+ Subject|relation|Object|quote[|modality|certainty|asserted_by]     (Object `-` when the relation takes none)
   f- Subject|relation|Object             (removes every fact with that subject, relation and object; put back with f+ any that should stay)
   t+ tag|quote                           t- tag|quote-prefix
   Quotes are copied word for word from the window, at least 12 characters, inside one sentence; names are the window's own form, the same string the window's other rows use.
3. {OUT}_review.md: a compact entry for each error and each missing row that a supervisor can check without opening anything else: `b`, page, the sentence quoted in full, the gold row, what is wrong, the rule, the correction. At the top: total windows, total rows checked (events, facts, tags), number of rows in error, number of missing rows, number of debatable rows, number of windows with no error and no missing row.

If a tool refuses to write one of these files at its path, do not work around it: write that file into your scratch folder instead and give its full path in your final message.

Constraints: open only the three paths named above (the two rule files and your input). Do not open, run or edit anything else; do not edit any gold file. Keep any helper script in a private subfolder of your scratch folder named `{TAG}/`.

Your final message must be short: windows, rows checked, rows in error, missing rows, debatable rows. Nothing else.

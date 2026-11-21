You are a labeller testing a new rule on hand-reviewed labels (the GOLD) of short wiki passages. Under the old rules a name or doer could only come from the passage itself, so many acts were left unrecorded ("no doer", "unnamed"). The owner has now ruled that the page text around the passage may be used, and that an unnamed individual is named by his description. Apply the new rule to each window and write what changes.

Read first, in full, before judging anything:
1. The rulebook: /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/EXTRACTION_PROCEDURE_V2.md (sections A to F; section F is the catalog A1 to A153).
2. The owner rulings: /home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/BRIEF.md (all addenda).
3. The new rule, which wins over everything above where they differ: /home/goblin/ScriptEngine/.claude/worktrees/9b-model-extraction-analysis-a7e9c9/docs/train_audit_2026-11-14/ctx/ADDENDUM_7_DRAFT.md

Then work through your input: {INPUT}
Each line is one window: `b`, page and section, `candidates_of_the_page` (names of entities the wiki links from this page: a real name found here may be used for a described individual when the context makes the identity plain), `page_text_before`, numbered `sentences` (the passage; cut by a crude splitter), `page_text_after`, `gold_events` [subject, verb, object, quote], `gold_facts` [subject, relation, object, modality, certainty, asserted_by, quote], `gold_tags` [tag, quote] and `reviewer_notes`.

What to do in each window:
- Look at every sentence the gold tagged `no_doer` or `crowd_end`, every row or note that says a person is unnamed, not named here or outside the window, and every passive or pronoun whose doer the passage leaves open.
- 7.1: if `page_text_before` or `page_text_after` STATES who it is, write the row the rulebook wants (step 5 table for events; a fact otherwise), with the name the context gives, and copy the context sentence that proves it as the evidence. Remove the tag the row replaces (`t-`), and remove a fact that the new event makes a twin (section B).
- 7.2: if the participant is one specific individual who has only a description, use the description as the end: no article, the fullest form the passage or context gives, the same form in every row of the window. A crowd, a plural, a kind or an indefinite stays no end and keeps its tag.
- 7.3: for an arrival where a named person is, use what follows to choose between `met` and the start of a fight.
- Everything else in the window stays as it is. Do not re-judge rows the new rule does not touch. All older rules still hold: one `fought` and one `met` per pair per window, the most specific verb only, a plan, order or claim is no event, quotes inside the passage and inside one sentence, at least 12 characters, copied word for word.
- Never use your memory of the series. If neither the passage nor the given context states it, the verdict for that sentence is "stays" and you say what was missing.

Write three files:
1. {OUT}_verdicts.jsonl: one JSON line per window in input order: {"b": 123, "id": "...", "verdict": "changed" | "unchanged" | "unsure", "by_rule": ["7.1" and/or "7.2" and/or "7.3"], "reason": "one or two lines"}.
2. {OUT}_fix.txt: a block per `changed` window, in exactly this syntax (blank line between blocks):
   @<b> gold: 2026-11-14 Addendum 7 pilot, <7.1|7.2|7.3> -- <short reason> ; evidence: "<the context sentence, word for word, or 'in passage'>"
   keep
   + Subject|verb|Object|quote            (add an event; Object `-` for awakened)
   - Subject|verb|Object                  (remove an event; strings equal to the gold row's)
   f+ Subject|relation|Object|quote[|modality|certainty|asserted_by]     (Object `-` when the relation takes none)
   f- Subject|relation|Object
   t+ tag|quote                           t- tag|quote-prefix
3. {OUT}_review.md: for every `changed` and `unsure` window a compact before-and-after a supervisor can check without opening anything else: `b`, page; the sentence(s) in full; what the gold has now (the tag or the gap) and why the reviewer left it; the context sentence that settles it, quoted in full, with where it stands (before or after the passage); the rows you add and remove; which of 7.1, 7.2, 7.3 applies. For every `unchanged` window one line saying why the new rule changes nothing (a real crowd, context silent, already recorded).
   At the top: counts of changed, unchanged and unsure windows; events added, facts added, tags removed; how many additions rest on 7.1, on 7.2, on 7.3.

If a tool refuses to write one of these files at its path, do not work around it: write that file into your scratch folder instead and give its full path in your final message.

Constraints: open only the four paths named above (the three rule files and your input). Do not open, run or edit anything else; do not edit any gold file. Keep any helper script in a private subfolder of your scratch folder named `{TAG}/`.

Your final message must be short: the counts from the top of your review file. Nothing else.

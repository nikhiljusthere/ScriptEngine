You are the third reader in a labelling audit. Two readers disagree about some events in short wiki passages: the GOLD (hand-reviewed labels made under a detailed rulebook) and a SECOND READER (an independent blind reading that did not know the rulebook). For each window, decide whether the gold is right, and propose a correction only where the gold is wrong by its own rulebook.

Read first, in full, before judging anything:
1. The rulebook: /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/EXTRACTION_PROCEDURE_V2.md (sections A to F; section F is the catalog of settled rulings A1 to A153 and every line of it is binding).
2. The owner rulings: /home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/BRIEF.md (all addenda; a later addendum wins; Addendum 6 is the "shows up" ruling).

Then work through your input: {INPUT}
Each line is one window: `b` (its number), the page and section, `page_text_before` / `page_text_after` (context only), numbered `sentences`, the gold's `gold_events` [subject, verb, object, quote], `gold_facts` [subject, relation, object, modality, certainty, asserted_by, quote], `gold_tags` [tag, quote], `reviewer_notes` (why the gold reviewer wrote what they wrote: read these first, they often explain a missing row), the `second_reader` lines, and the differences: `second_reader_only_events`, `gold_only_events`, `gold_people_second_reader_omits`.

How to judge:
- The gold is presumed right. The second reader did not know the catalog, so most of its extra events are wrong by the catalog: one `fought` and one `met` per pair per window; no `met` when the encounter becomes the fight (A145); the most specific verb only; no name or doer from outside the window (A8, A110, A112, A130, A20); ordinary sleep is no `awakened` (A106); a plan, an order, a claim or a dream is no event; sparring is `trained`, not `fought` (A71). An extra event from the second reader is a reason to look, never by itself a reason to add.
- Second-reader names are page titles from a candidate list. The gold writes names as the window writes them. Never treat that difference as a disagreement, and write every row you propose with the window's own name form, the same string the window's existing rows use for that person.
- Propose a correction only when ALL of these hold: the window's own text states it; a specific rule supports it and you can name the rule; the existing rows do not already record the same act; and you would defend it to the reviewer who wrote the note. A gold event to remove needs the same standard: say which rule it breaks.
- When you add an event that an existing fact row already expresses (for example `other_verb shows` beside a new `met`, or a `protected` fact beside a new `saved`), remove that fact: an event is never also a fact (section B). Otherwise leave facts and tags alone.
- Settled practice of this gold, do not propose changes against it: a transformation into a new form is written as the fact `transformed_into` (it is not replaced by `awakened`); a definite description of one unnamed individual ("the Hollow", "the mayor", "the priest") is not used as an end. If a window turns only on one of these two points, give `gold_ok` and say so in the reason.
- A window that is a long list of battles ("A vs. B", one per line) shows every gold `fought` row as a difference when the second reader skipped the list: that is not a gold error; check that each gold row matches its line.
- Quotes are copied word for word from the window, at least 12 characters, inside one sentence.
- If you are not sure, say `unsure` and explain in one line. Do not guess; an unsure verdict is useful, a wrong correction is harmful.

Write three files:
1. {OUT}_verdicts.jsonl: one JSON line per window in input order: {"b": 123, "id": "...", "verdict": "gold_ok" | "fix" | "unsure", "reason": "one or two lines, naming the rule"}.
2. {OUT}_fix.txt: only for `fix` windows, blocks in exactly this syntax (blank line between blocks):
   @<b> gold: 2026-11-14 audit, <rule code> -- <short reason>
   keep
   + Subject|verb|Object|quote            (add an event; Object `-` for awakened)
   - Subject|verb|Object                  (remove an event; the strings must equal the gold row's exactly)
   f+ Subject|relation|Object|quote[|modality|certainty|asserted_by]     f- Subject|relation|Object
   t+ tag|quote                           t- tag|quote-prefix
   Always start a block with `keep`. Use only the operations a correction needs.
3. {OUT}_review.md: for each `fix` and each `unsure` window, a compact entry a supervisor can check without opening anything else: `b`, page, the sentence or sentences involved quoted in full, what the gold has, what you propose (or why unsure), and the rule.

If a tool refuses to write one of these files at its path, do not work around it: write that file into your scratch folder instead and give its full path in your final message.

Constraints: open only the three paths named above (the two rule files and your input). Do not open, run or edit anything else; do not edit any gold file. Other workers share your scratch folder: keep any helper script in a private subfolder of your scratch folder named `{TAG}/` with your own paths hard-coded.

Your final message must be short: counts of gold_ok, fix and unsure windows, and nothing else (plus a scratch path if a write was refused).

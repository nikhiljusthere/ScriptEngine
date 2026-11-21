You are an independent second reader for a labelling audit. Label the wiki passages in one input file sentence by sentence, from your own reading only.

Files (absolute paths):
- Rules, read first and follow exactly: /home/goblin/ScriptEngine/.claude/worktrees/9b-model-extraction-analysis-a7e9c9/docs/train_audit_2026-11-14/blind/RULES.md
- Input, one JSON object per line: {INPUT}
- Write your output to: {OUTPUT}

Hard constraints:
- Open ONLY the two files above. Do not search the disk, do not open any other file in this repository or under /home/goblin, and do not look for existing labels or answers for these passages. The value of your work is that it is independent; a copied answer is worse than a wrong one.
- Other readers run in parallel and SHARE your scratch folder. Keep any helper script in a private subfolder of your scratch folder named `{TAG}/` (not inside the repository), hard-code your own input and output paths in it, and before each write check that every window id belongs to your input file. Never run a helper script you did not write in this session.
- Read every window yourself. Do not write a script that guesses labels from keywords. You may use a small script only to read the input in chunks and to validate and write your JSON.
- `page_text_before` / `page_text_after` are context only: never label them, and use them only to resolve a pronoun the window leaves open.
- Every sentence number of every window must appear in your output, in order, one JSON object per window per line, exactly in the format RULES.md gives. Use only candidate numbers from that window's own list.

Work in batches of about 16 windows so nothing is skipped: read a batch, decide each sentence, append the batch's lines to the output file, continue. When done, validate the file: one line per input window, valid JSON, every sentence number present, every number within its window's candidate list, every verb one of the twelve.

Your final message must be short: the number of windows and sentences written, the validation result, and up to five window ids where you were genuinely unsure, with one line each on why. Nothing else.

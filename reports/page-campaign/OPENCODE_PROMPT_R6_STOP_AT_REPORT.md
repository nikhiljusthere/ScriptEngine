# OPENCODE PROMPT — R6: stop at the report, do not start Episodes/Techniques

Paste this into the live opencode session now — it corrects the tail instruction in
`OPENCODE_PROMPT_R6.md`, which said to move to the episode pass after R6. That's superseded:
R7 (roster/set precision) folds in between R6 and the next volume, per the user's decision.

---

Confirmed: the paraphrase generation is alive and progressing normally in the background
(261/2,321 as of the last check, ETA ~95 min) — the chat going quiet is expected, not a stall.
Keep it running exactly as it is. No action needed on the generation itself.

**Correction to R6's scope, effective now: stop when R6's own todo is done. Do not start the
episodes wave or the techniques wave afterward.**

R6 finishes at:
1. Part C assembly (dedup the 6,963 rows) + page-run + root-cause table, once generation hits
   `done == 2321`.
2. The conditional re-gate (`pytest`, `eval --series jjk`, `canon-run --series opm`) — **only**
   if Part C's root-causing pass actually changed code in `scriptengine/`. If every failure
   gets a G-number and stays documented-open with no code touched, this is a no-op — say so
   explicitly in the report rather than skipping it silently.
3. `reports/page-campaign/R6_RECALL_FLOOR/REPORT.md` written.
4. `HANDOFF_PROSE_PASS.md` updated with the final state.

**Then stop.** Do not begin the episodes wave (59 pages) or the techniques wave (149 pages).
There's a next release (roster/set precision, R7) queued to run before any more volume — it
will be handed to you separately once R6's report is reviewed. Report back when R6's todo is
fully checked off and wait there.

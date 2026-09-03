# OPENCODE PROMPT — R6 Part C amendment: triage before full-pipeline scoring

Paste this into the live opencode session. It changes only the **scoring plan** for the
6,963 generated paraphrases (the "assemble + page-run + root-cause + report" step, still
pending). It does **not** touch the generation loop currently running — let that keep going
exactly as it is; nothing here requires restarting or discarding any in-flight work.

---

## Why

Right now the plan is: for every one of the 6,963 paraphrases, run full retrieval + routing +
strict substring scoring. Most of that is redundant. R6 Part B's recall floor already
guarantees a resolved subject's content lands in the bundle for any phrasing that resolves the
same entity and mode — so a paraphrase that routes identically to its original question adds
little new information by being fully re-scored. The paraphrases worth spending the expensive
full pipeline on are the ones that **don't** route the same way as their original — those are
the actual router-phrasing gaps this exercise exists to find.

## What does NOT change

- The strict substring `present()` check stays the final word on correctness for anything that
  gets fully scored. Do not replace it with an LLM judgment of "is this answer correct" — that
  swaps a deterministic, gateable check for a probabilistic one, on the exact claim (100%
  correct, single-line precision) this campaign is built to prove. The precedent for this is
  already in the repo: `scriptengine/script/writer.py`'s own docstring — "a number the model
  invented is caught by `verify_script` the same way it catches one written by hand." The LLM
  proposes here (which paraphrases look risky); the deterministic scorer still disposes (is the
  fact actually present, verbatim).
- Every paraphrase still gets generated and still gets a routing check. Nothing is skipped
  outright — some paraphrases just don't need the *full* pipeline.

## The triage mechanism

For each of the 2,321 original questions (already routed once to a known subject + mode) and
its generated paraphrases:

1. **Cheap classification, not a full pipeline call.** Ask Qwen (the same local model already
   running, no new server needed) a single short completion per paraphrase: "would this
   paraphrase resolve to the same subject and the same mode (qa/roster/narrative) as its
   original?" This is a classification call, not a retrieval call — far cheaper than routing +
   retrieving + scoring.
2. **Paraphrases classified "same subject + same mode"**: sample a **bounded, fixed fraction —
   15%** — through the full retrieval + routing + strict-scoring pipeline, as a calibration
   check on the classifier itself. The rest are logged as "presumed consistent, not
   exhaustively scored" with the classification recorded, not silently dropped.
3. **Paraphrases classified "different subject or different mode"**: send **all** of these
   through the full pipeline. This is the expensive, rigorous check, spent on the cases most
   likely to reveal a genuine router-phrasing gap — exactly the ones worth finding.
4. **Calibration check on the 15% sample**: if the classifier's "same subject + mode" calls
   turn out wrong at a rate above ~5% in that sample, the classifier isn't reliable enough to
   trust for triage — fall back to full-pipeline scoring for everything and report that the
   amendment didn't hold, rather than quietly accepting a triage step that's letting gaps
   through unscored.

## Scope discipline (same rule as the rest of R6/R7)

The 15% calibration fraction is a hard cap, not a floor — do not tune it up or down based on
a hunch mid-run; if the calibration check in step 4 fails, that is the trigger to change
strategy, not a manual adjustment. Every shell command still needs a timeout and must never go
silent longer than ~10-15s, per the standing rule already in `OPENCODE_PROMPT_R6.md`.

## Report

In `R6_RECALL_FLOOR/REPORT.md`, add: how many paraphrases were classified each way, the
calibration sample's actual accuracy, how many full-pipeline scores this saved versus scoring
all 6,963 directly, and the same root-cause table for every full-pipeline failure the method
already requires (with a real G-number, never a rephrase-to-dodge).

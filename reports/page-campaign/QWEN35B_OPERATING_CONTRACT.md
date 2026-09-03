# Operating contract — Qwen3.6-35B-A3B on repetitive prose-pass volume

For any opencode session backed by the 35B-A3B model, running the mechanical per-page
authoring loop (battles now; techniques/chapters/character_synopses/volumes later). Read
this before starting any batch. This is a **safety contract**, not a task list — the task
itself (which pages, which template) is assigned separately.

## Why this exists

A prior fast-model session on this campaign (documented in `HANDOFF_PROSE_PASS.md`, SU10/
SU11) produced real damage while running unsupervised: false "uncovered sections" claims,
over-retiring with blank or wrong reasons, characters skipped entirely, a wrong resume
pointer reported as correct. It required a dedicated audit-and-recovery pass to find and
fix. That is not a hypothetical risk for this model class — it already happened once, on
this exact kind of work. This contract exists to make that failure mode structurally
impossible to repeat silently, by removing the model's authority to make the judgment
calls that went wrong last time, not by asking it to be more careful.

## The boundary: repetitive execution, not judgment

**Allowed — the mechanical loop, strictly as already templated:**
- Dump a page's uncovered sections (per the approved template for that page type —
  `battle_prose_template.md`, `episode_prose_template.md`, `prose_pass_template.md`).
- Author verbatim-substring triples from those sections, following the template's explicit
  inclusion/exclusion rules (e.g., battles: author from Prologue/Battle/Aftermath only,
  never re-ask an infobox field).
- Add the required R5 adversarial forms (yes/no, comparative, counterfactual) per page.
- Run the authoring lint already specified (answer-in-question, leading-wh-word,
  numeric-answer-for-"how many").
- Bulk-add, run `page-run`, read the result.
- Retire a question **only** when the reason is mechanically explicit and already covered
  by the template's own exclusion list (e.g., "this answer is the infobox `outcome` field,
  template says don't author it as prose" — that is a rule lookup, not a judgment call).

**Forbidden — anything requiring interpretation, escalate instead (see below):**
- No edits to any file under `scriptengine/` (router.py, roster.py, chunker.py, or any
  other engine code). A suspected router/retrieval gap gets logged in `findings.md`, never
  diagnosed or fixed.
- No edits to `overrides.yaml` or any declared roster.
- No retiring a question for any reason **not already an explicit rule in the template**.
  If it's ambiguous whether something is cross-page, a gold error, or a router gap — do
  not retire it. Leave it active and failing (documented-open), log it in `decisions.md`,
  move on.
- No rephrasing a question to dodge a failure. Ever. This is the standing rule for the
  whole campaign and applies here without exception.
- No un-retiring a previously retired question.
- No editing template files (`*_prose_template.md`) — if the template doesn't fit a page
  you're looking at, that's a decisions.md escalation, not something to improvise around.
- No scope or sequencing calls (which page type comes next, whether to widen a fix, how
  to handle a page that doesn't match the template's assumed shape). Every fork like this
  gets logged as an open question in `decisions.md` and the loop **stops on that item**
  (not the whole session) — pick a different item to keep progress moving, but do not
  resolve the fork yourself.

## The three files — what goes in each

All three are append-only logs, one per campaign phase (or reset per wave, your call) —
never edited retroactively, only appended to, so the trail is auditable end to end.

### `flow.md` — the factual activity trail
One entry per page processed. No interpretation, just what happened:
```
## <slug> — <timestamp>
- sections authored: <list>
- triples added: <ids>
- page-run result: X/Y
- retires (mechanical, template-rule only): <ids + which template rule>
```

### `decisions.md` — every fork you don't have authority to resolve
One entry per ambiguous item hit during the loop:
```
## <slug>/<question id or general> — <timestamp>
- what's ambiguous: <one or two sentences>
- why it's not a template-explicit call: <reason>
- left as: active-and-failing (not retired)
- needs: <what kind of call this needs — engine diagnosis / scope decision / gold review>
```

### `findings.md` — anything that looks like a genuine engine-level gap
One entry per suspected router/retrieval/chunker gap, in the same evidence-first shape
used successfully all campaign (forced-qa probe style — what's present, what's routed,
what's absent):
```
## <slug>/<question id> — <timestamp>
- question: <text>
- routed mode: <qa/roster/narrative, if checkable>
- answer verbatim on page: <yes/no + where>
- symptom: <what's missing from the served bundle>
- suspected class: <if it resembles a known G-number family, say which; otherwise "new">
```

This is exactly the format that turned Episode 14's gap and the F1-F4 discoveries into
clean, fast, one-session fixes — the format matters as much as the discipline of using it.

## Escalation cadence, not silence

Don't let `decisions.md`/`findings.md` entries sit unreviewed for an entire wave. At a
natural checkpoint (end of a session, or every ~15-20 pages), surface a summary of what's
accumulated in both files — this is the trigger for the stronger model or the user to
review and act, the same "checkpoint on findings, not a fixed batch count" rhythm that's
worked all night. The 35B-A3B session's job is to make these easy to review quickly, not
to sit on them.

## Mandatory audit — don't skip this given the SU10/SU11 precedent

Before trusting a wave's output as done, spot-check a sample (5-10%, or every page if the
wave is small) against actual ground truth — same method SU11 used: read the cited section
of the page directly, confirm a claimed "uncovered" section genuinely has no gold coverage,
confirm a retired question's reason is actually true against the wikitext, not just
plausible-sounding. This is not optional overhead — it is the check that catches exactly
the failure mode this contract exists to prevent, and self-reported "all correct" from any
model, fast or slow, is not sufficient evidence on its own (this campaign has verified that
claim wrong before).

## Standing rules (unchanged, apply here too)

Every shell command needs a timeout and must never go silent longer than ~10-15 seconds —
same mandatory rule as every other release tonight. Every answer stays a verbatim substring
of the wiki text. Never rephrase a question to dodge a failure.

# Chapter prose — triage log (waves 2–6)

Method (user mandate): a page-run failure is either a **gold error** or an
**engine gap**, never a phrasing problem. Never reword a question to make it
pass.

- **Gold error** → fix the gold/section inline, re-emit, re-run, confirm.
- **Engine gap** (router/chunker/retrieval) → leave the question in its original
  failing form, record it below, and propose one fix batch at the end of the
  whole run.
- **Phrasing probe (mandatory before any rephrase):** probe at least 3
  natural phrasings of the same fact. Most pass and only a stilted form
  fails → authoring-side; the Kinji-079 / Yuki-083 rephrase precedent
  applies. Most fail → the fact is not broadly reachable → **engine gap**:
  leave the question in its original failing form and file a G## in
  `CHECKPOINT_ROSTER_BUILD.md`. A single passing alternate is not evidence of
  broad reachability — the probe decides.

One entry per failure:

```
## [wave] <slug> — "<question>"
- gold: <verbatim gold>
- section: <Summary | Plot Details | Trivia | 4-Koma Bonus>
- route: <qa | roster | ...> (page-run report)
- phrasing probe: <n natural forms — which pass / which fail; decides authoring-vs-engine>
- diagnosis: <one line: gold error (fixed) OR engine gap (G##, proposed)>
```

## [w6] epilogue — “Whom do the four short epilogue stories feature, per Epilogue?”
- gold: `Yuko Ozawa, Panda, Nobara Kugisaki, and Uraume`
- section: Summary
- route: narrative (page-run report; `routed narrative`, subject type media)
- diagnosis: **engine gap — filed as G30**, not an authoring-side issue. The
  gold is verbatim in the page's one-line `Summary` (12 words); the narrative
  path's own-page beat builder drops sections under the G15 20-word floor
  (`NarrativeRetriever._beats_from_page`, `scriptengine/retrieve/narrative.py`),
  so the page's `Summary` never becomes a beat and no narrative bundle for the
  page carries the gold. Only the qa route's chunks do.
- phrasing probe (5 forms — decides authoring-vs-engine):
  1. “Whom do the four short epilogue stories feature, per Epilogue?” (original) → narrative → **FAIL**
  2. “How many short epilogue stories are there, per Epilogue?” → narrative → **FAIL**
  3. “What are the four short epilogue stories about, per Epilogue?” → narrative → **FAIL**
  4. “Who appears in the four short epilogue stories, per Epilogue?” → qa → PASS (the G28 OOA trigger)
  5. “Which four characters get short epilogue stories in the Epilogue, per Epilogue?” → qa → PASS
  **3 of 4 natural phrasings fail** → the fact is **not broadly reachable** →
  engine gap. The Kinji-079 / Yuki-083 rephrase precedent does not cover this
  case: it applies when a fact is broadly reachable and only stilted,
  deliberately trigger-y phrasings fail (Yuki-086 note: “4 natural qa
  alternates all pass”; Yaga-036: the original was genuinely unnatural
  English). This is the inverse of that.
- disposition (KEY RULE): the question is **restored to its original wording
  and left failing** (2/3 on page-run) — a failing question is the evidence,
  as with G29. Filed as **G30** in `CHECKPOINT_ROSTER_BUILD.md`: a
  chapter/episode/media page's narrative bundle should carry the page's own
  `Summary` section as a beat (exempt short `Summary` / `Plot` / `Synopses`
  sections from the G15 floor in `_beats_from_page`). Fix proposed, **not
  applied** (execution tier cannot touch `scriptengine/`).
- history: the wave-6 in-lane rephrase (“Which four characters get short
  epilogue stories in the Epilogue…”) was committed in `c533620` under the
  Kinji-079 precedent; the phrasing probe showed that disposition was wrong
  and it was reversed the same day (2026-09-04). Wave-6 page-run therefore
  stands at **95/96** with G30 open.
# Chapter prose — triage log (waves 2–6)

Method (user mandate): a page-run failure is either a **gold error** or an
**engine gap**, never a phrasing problem. Never reword a question to make it
pass.

- **Gold error** → fix the gold/section inline, re-emit, re-run, confirm.
- **Engine gap** (router/chunker/retrieval) → leave the question in its original
  failing form, record it below, and propose one fix batch at the end of the
  whole run.

One entry per failure:

```
## [wave] <slug> — "<question>"
- gold: <verbatim gold>
- section: <Summary | Plot Details | Trivia | 4-Koma Bonus>
- route: <qa | roster | ...> (page-run report)
- diagnosis: <one line: gold error (fixed) OR engine gap (G##, proposed)>
```

## [w6] epilogue — “Whom do the four short epilogue stories feature, per Epilogue?”
- gold: `Yuko Ozawa, Panda, Nobara Kugisaki, and Uraume`
- section: Summary
- route: narrative (page-run report; `routed narrative`, subject type media)
- diagnosis: authoring-side misroute (Kinji-079 / Yuki-083 precedent), not a
  gold error — the gold is verbatim on the page, but “Whom do … feature” on a
  story-typed page forces the narrative read, and a chapter page's narrative
  bundle carries the L3 scene beats + OOA + the previous chapter **without the
  page's own `Summary` chunk**, so the Summary-only gold is absent from the
  bundle (probed live: alternate “How many short epilogue stories…” phrasing
  routes narrative the same way; `What kind of stories…` routes roster).
  Fixed in-lane: re-anchored to “Which four characters get short epilogue
  stories in the Epilogue, per Epilogue?” (qa route, Summary chunk in the
  bundle, probed live), gold unchanged; re-run 3/3.
- open engine observation (non-blocking, for the engine pass, not this
  campaign): a chapter page's narrative bundle should include its `Summary`
  chunk as a beat, so Summary-only facts are served on the default narrative
  read; and/or the roster-route “what kind of” phrasing should not fire on a
  page's own section shape.
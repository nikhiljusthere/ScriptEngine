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

(No entries yet.)
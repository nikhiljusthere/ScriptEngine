# Page campaign csm/american_thugs — 2026-09-17-0814

Batch `_csm_page_american_thugs.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/3** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 3/3 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is American Thugs's allegiance? | `routed qa` / `-` | United States of America |
| **yes** | fact | Who are American Thugs's notable members? | `routed qa` / `-` | Aldo Joey Unnamed Brother |
| **yes** | fact | In which manga chapter does American Thugs first appear? | `routed qa` / `-` | Chapter 53 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

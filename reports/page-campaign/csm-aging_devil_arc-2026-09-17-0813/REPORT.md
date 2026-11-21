# Page campaign csm/aging_devil_arc — 2026-09-17-0813

Batch `_csm_page_aging_devil_arc.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/4** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | Which saga does Aging Devil arc belong to? | `routed qa` / `-` | Academy Saga |
| **yes** | fact | Which chapters are included in Aging Devil arc? | `routed qa` / `-` | Chapter 156 - 190 |
| **yes** | fact | What comes before Aging Devil arc? | `routed qa` / `-` | Chainsaw Man Church arc |
| **yes** | fact | What comes after Aging Devil arc? | `routed qa` / `-` | War Devil arc |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

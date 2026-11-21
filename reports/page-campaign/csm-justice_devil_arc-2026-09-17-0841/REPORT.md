# Page campaign csm/justice_devil_arc — 2026-09-17-0841

Batch `_csm_page_justice_devil_arc.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.5s wall clock.

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
| **yes** | fact | Which saga does Justice Devil arc belong to? | `routed qa` / `-` | Academy Saga |
| **yes** | fact | Which chapters are included in Justice Devil arc? | `routed qa` / `-` | Chapter 98 - 111 |
| **yes** | fact | What comes before Justice Devil arc? | `routed qa` / `-` | Control Devil arc |
| **yes** | fact | What comes after Justice Devil arc? | `routed qa` / `-` | Dating Denji arc |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

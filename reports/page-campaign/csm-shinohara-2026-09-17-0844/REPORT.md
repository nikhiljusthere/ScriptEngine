# Page campaign csm/shinohara — 2026-09-17-0844

Batch `_csm_page_shinohara.json`: 2 questions (0 set, 2 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **2/2** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 2/2 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Shinohara's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Shinohara? | `routed qa` / `-` | Alive |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

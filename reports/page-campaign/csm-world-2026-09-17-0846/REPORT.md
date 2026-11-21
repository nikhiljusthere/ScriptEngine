# Page campaign csm/world — 2026-09-17-0846

Batch `_csm_page_world.json`: 1 questions (0 set, 1 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 0.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **1/1** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 1/1 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is World? | `routed qa` / `-` | World 世界 Sekai, also known as Human World or Earth is where humans reside. |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

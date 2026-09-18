# Page campaign csm/devil — 2026-09-18-0317

Batch `_csm_page_devil.json`: 1 questions (1 set, 0 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 0.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **1/1** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 0/0 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the affiliations of Devil? | `Devil's affiliations` / `declared` | 1 found, 0 missing; returned 1 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

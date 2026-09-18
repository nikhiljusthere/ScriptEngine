# Page campaign csm/class_president — 2026-09-18-0431

Batch `_csm_page_class_president.json`: 5 questions (2 set, 3 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 2.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/5** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 6/6 (100.0%) |
| fact answers present | 3/3 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Class President? | `Every named technique of Class President` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the affiliations of Class President? | `Class President's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What is Class President's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Class President? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Class President's occupation? | `routed qa` / `-` | High School Student Class President |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

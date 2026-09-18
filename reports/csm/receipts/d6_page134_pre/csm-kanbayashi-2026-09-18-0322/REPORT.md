# Page campaign csm/kanbayashi — 2026-09-18-0322

Batch `_csm_page_kanbayashi.json`: 4 questions (1 set, 3 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 3.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/4** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 3/3 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the affiliations of Kanbayashi? | `Kanbayashi's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What is Kanbayashi's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Kanbayashi? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Kanbayashi's occupation? | `routed qa` / `-` | Inn Owner |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

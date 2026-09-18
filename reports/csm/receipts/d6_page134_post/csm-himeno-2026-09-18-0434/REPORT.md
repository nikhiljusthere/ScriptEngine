# Page campaign csm/himeno — 2026-09-18-0434

Batch `_csm_page_himeno.json`: 15 questions (9 set, 6 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 8.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **15/15** |
| set questions exact | 9/9 (100.0%) |
| canon items recovered | 31/31 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Himeno? | `Every named technique of Himeno` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the allies of Himeno? | `Every ally of Himeno` / `declared` | 9 found, 0 missing; returned 9 |
| **yes** | set | What are all the enemies of Himeno? | `Every enemy of Himeno` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the friends of Himeno? | `Every friend of Himeno` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the romantics of Himeno? | `Every romantic of Himeno` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the subordinates of Himeno? | `Every subordinate of Himeno` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the superiors of Himeno? | `Every superior of Himeno` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the aliases of Himeno? | `Himeno's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Himeno? | `Himeno's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Himeno's name? | `routed qa` / `-` | 姫野 |
| **yes** | fact | What is the romaji of Himeno's name? | `routed qa` / `-` | Himeno |
| **yes** | fact | What is Himeno's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Himeno's height? | `routed qa` / `-` | 175 cm (5'9") |
| **yes** | fact | What is the status of Himeno? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Himeno's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/furio — 2026-09-18-0433

Batch `_csm_page_furio.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 3/3 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Furio? | `Every named technique of Furio` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Furio? | `Furio's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What is the status of Furio? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Furio's occupation? | `routed qa` / `-` | High School Student Devil Hunter |
| **yes** | fact | What is Furio's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Furio's name? | `routed qa` / `-` | フリオ |
| **yes** | fact | What is the romaji of Furio's name? | `routed qa` / `-` | Furio |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/joey — 2026-09-18-0435

Batch `_csm_page_joey.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 6/6 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Joey? | `Every named technique of Joey` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the enemies of Joey? | `Every enemy of Joey` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Joey? | `Joey's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What is the status of Joey? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Joey's occupation? | `routed qa` / `-` | Private Devil Hunter |
| **yes** | fact | What is Joey's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Joey's name? | `routed qa` / `-` | ジョーイ |
| **yes** | fact | What is the romaji of Joey's name? | `routed qa` / `-` | Jōi |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

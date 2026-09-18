# Page campaign csm/kishibe — 2026-09-18-0435

Batch `_csm_page_kishibe.json`: 15 questions (8 set, 7 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 8.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **15/15** |
| set questions exact | 8/8 (100.0%) |
| canon items recovered | 38/38 (100.0%) |
| fact answers present | 7/7 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Kishibe? | `Every named technique of Kishibe` / `declared` | 10 found, 0 missing; returned 10 |
| **yes** | set | What are all the allies of Kishibe? | `Every ally of Kishibe` / `declared` | 9 found, 0 missing; returned 9 |
| **yes** | set | What are all the enemies of Kishibe? | `Every enemy of Kishibe` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the mentors of Kishibe? | `Every mentor of Kishibe` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the students of Kishibe? | `Every student of Kishibe` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the superiors of Kishibe? | `Every superior of Kishibe` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the aliases of Kishibe? | `Kishibe's aliases` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the affiliations of Kishibe? | `Kishibe's affiliations` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | fact | What are the kanji for Kishibe's name? | `routed qa` / `-` | 岸辺 |
| **yes** | fact | What is the romaji of Kishibe's name? | `routed qa` / `-` | Kishibe |
| **yes** | fact | What is Kishibe's gender? | `routed qa` / `-` | Male |
| **yes** | fact | How old is Kishibe? | `routed qa` / `-` | 50+ |
| **yes** | fact | What is Kishibe's height? | `routed qa` / `-` | 194 cm (6'4½") |
| **yes** | fact | What is the status of Kishibe? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Kishibe's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

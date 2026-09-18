# Page campaign csm/denji — 2026-09-18-0431

Batch `_csm_page_denji.json`: 21 questions (13 set, 8 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 11.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **21/21** |
| set questions exact | 13/13 (100.0%) |
| canon items recovered | 145/145 (100.0%) |
| fact answers present | 8/8 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Denji? | `Every named technique of Denji` / `declared` | 23 found, 0 missing; returned 23 |
| **yes** | set | What are all the allies of Denji? | `Every ally of Denji` / `declared` | 30 found, 0 missing; returned 30 |
| **yes** | set | What are all the enemies of Denji? | `Every enemy of Denji` / `declared` | 31 found, 0 missing; returned 31 |
| **yes** | set | What are all the families of Denji? | `Every family of Denji` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the friends of Denji? | `Every friend of Denji` / `declared` | 10 found, 0 missing; returned 10 |
| **yes** | set | What are all the mentors of Denji? | `Every mentor of Denji` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the rivals of Denji? | `Every rival of Denji` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the romantics of Denji? | `Every romantic of Denji` / `declared` | 8 found, 0 missing; returned 8 |
| **yes** | set | What are all the students of Denji? | `Every student of Denji` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the subordinates of Denji? | `Every subordinate of Denji` / `declared` | 10 found, 0 missing; returned 10 |
| **yes** | set | What are all the superiors of Denji? | `Every superior of Denji` / `declared` | 9 found, 0 missing; returned 9 |
| **yes** | set | What are all the aliases of Denji? | `Denji's aliases` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the affiliations of Denji? | `Denji's affiliations` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | fact | What are the kanji for Denji's name? | `routed qa` / `-` | デンジ |
| **yes** | fact | What is the romaji of Denji's name? | `routed qa` / `-` | Denji |
| **yes** | fact | What is Denji's gender? | `routed qa` / `-` | Male |
| **yes** | fact | How old is Denji? | `routed qa` / `-` | 16 (Chapter 1-82; current timeline by Chapter 232)
17 (Chapter 83-???; original timeline) 18 (???; original timeline) |
| **yes** | fact | What is Denji's height? | `routed qa` / `-` | 173 cm (5'8") |
| **yes** | fact | What is Denji's birthday? | `routed qa` / `-` | 1980 (specific date is unknown) |
| **yes** | fact | What is the status of Denji? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Denji's occupation? | `routed qa` / `-` | Private Devil Hunter (formerly)
Public Safety Devil Hunter
High School Student (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

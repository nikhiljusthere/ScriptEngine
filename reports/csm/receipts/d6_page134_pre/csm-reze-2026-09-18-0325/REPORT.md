# Page campaign csm/reze — 2026-09-18-0325

Batch `_csm_page_reze.json`: 14 questions (7 set, 7 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 8.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **14/14** |
| set questions exact | 7/7 (100.0%) |
| canon items recovered | 43/43 (100.0%) |
| fact answers present | 7/7 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Reze? | `Every named technique of Reze` / `declared` | 16 found, 0 missing; returned 16 |
| **yes** | set | What are all the allies of Reze? | `Every ally of Reze` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the enemies of Reze? | `Every enemy of Reze` / `declared` | 12 found, 0 missing; returned 12 |
| **yes** | set | What are all the subordinates of Reze? | `Every subordinate of Reze` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the superiors of Reze? | `Every superior of Reze` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the affiliations of Reze? | `Reze's affiliations` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the aliases of Reze? | `Reze's aliases` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Reze's name? | `routed qa` / `-` | レゼ |
| **yes** | fact | What is the romaji of Reze's name? | `routed qa` / `-` | Reze |
| **yes** | fact | What is Reze's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Reze? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Reze's occupation? | `routed qa` / `-` | Spy (formerly) Waitress (formerly) |
| **yes** | fact | How old is Reze? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Reze's birthday? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

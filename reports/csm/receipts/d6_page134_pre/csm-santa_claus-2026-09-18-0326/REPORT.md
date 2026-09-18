# Page campaign csm/santa_claus — 2026-09-18-0326

Batch `_csm_page_santa_claus.json`: 12 questions (6 set, 6 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 6.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **12/12** |
| set questions exact | 6/6 (100.0%) |
| canon items recovered | 23/23 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Santa Claus? | `Every named technique of Santa Claus` / `declared` | 11 found, 0 missing; returned 11 |
| **yes** | set | What are all the enemies of Santa Claus? | `Every enemy of Santa Claus` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the subordinates of Santa Claus? | `Every subordinate of Santa Claus` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the superiors of Santa Claus? | `Every superior of Santa Claus` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Santa Claus? | `Santa Claus's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the aliases of Santa Claus? | `Santa Claus's aliases` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | fact | What are the kanji for Santa Claus's name? | `routed qa` / `-` | サンタクロース |
| **yes** | fact | What is the romaji of Santa Claus's name? | `routed qa` / `-` | Santa Kurōsu |
| **yes** | fact | What is Santa Claus's gender? | `routed qa` / `-` | Unknown Female (presumably) |
| **yes** | fact | What is the status of Santa Claus? | `routed qa` / `-` | Incapacitated |
| **yes** | fact | What is Santa Claus's occupation? | `routed qa` / `-` | Private Devil Hunter |
| **yes** | fact | How old is Santa Claus? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

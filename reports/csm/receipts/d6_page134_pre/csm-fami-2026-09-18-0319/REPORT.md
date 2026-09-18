# Page campaign csm/fami — 2026-09-18-0319

Batch `_csm_page_fami.json`: 12 questions (6 set, 6 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 10.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **12/12** |
| set questions exact | 6/6 (100.0%) |
| canon items recovered | 34/34 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Fami? | `Every ally of Fami` / `declared` | 12 found, 0 missing; returned 12 |
| **yes** | set | What are all the enemies of Fami? | `Every enemy of Fami` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the families of Fami? | `Every family of Fami` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the subordinates of Fami? | `Every subordinate of Fami` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the affiliations of Fami? | `Fami's affiliations` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the aliases of Fami? | `Fami's aliases` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Fami's name? | `routed qa` / `-` | キガ |
| **yes** | fact | What is the romaji of Fami's name? | `routed qa` / `-` | Kiga |
| **yes** | fact | What is Fami's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Fami? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Fami's occupation? | `routed qa` / `-` | High School Student (cover) Wild Devil |
| **yes** | fact | How old is Fami? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

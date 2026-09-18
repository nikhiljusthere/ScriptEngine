# Page campaign csm/gun_devil — 2026-09-18-0320

Batch `_csm_page_gun_devil.json`: 10 questions (5 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 9.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 5/5 (100.0%) |
| canon items recovered | 15/15 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Gun Devil? | `Every named technique of Gun Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the allies of Gun Devil? | `Every ally of Gun Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the enemies of Gun Devil? | `Every enemy of Gun Devil` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the aliases of Gun Devil? | `Gun Devil's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Gun Devil? | `Gun Devil's affiliations` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | fact | What are the kanji for Gun Devil's name? | `routed qa` / `-` | 銃の悪魔 |
| **yes** | fact | What is the romaji of Gun Devil's name? | `routed qa` / `-` | Jū no Akuma |
| **yes** | fact | What is the status of Gun Devil? | `routed qa` / `-` | Deceased (48%) Alive (52%) |
| **yes** | fact | What is Gun Devil's occupation? | `routed qa` / `-` | Wild Devil (formerly)
Contract Devil for the USA
Contract Devil for Governments |
| **yes** | fact | How old is Gun Devil? | `routed qa` / `-` | 15 years (of known existence) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/tank_devil — 2026-09-18-0440

Batch `_csm_page_tank_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.4s wall clock.

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
| **yes** | set | What are all the aliases of Tank Devil? | `Tank Devil's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Tank Devil? | `Tank Devil's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Tank Devil's name? | `routed qa` / `-` | 戦車の悪魔 |
| **yes** | fact | What is the romaji of Tank Devil's name? | `routed qa` / `-` | Sensha no Akuma |
| **yes** | fact | What is the status of Tank Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Tank Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Tank Devil's occupation? | `routed qa` / `-` | Wild Devil (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

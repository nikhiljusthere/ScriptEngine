# Page campaign csm/nail_fiend — 2026-09-18-0437

Batch `_csm_page_nail_fiend.json`: 10 questions (5 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 5.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 5/5 (100.0%) |
| canon items recovered | 16/16 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Nail Fiend? | `Every named technique of Nail Fiend` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the allies of Nail Fiend? | `Every ally of Nail Fiend` / `declared` | 8 found, 0 missing; returned 8 |
| **yes** | set | What are all the enemies of Nail Fiend? | `Every enemy of Nail Fiend` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Nail Fiend? | `Nail Fiend's aliases` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Nail Fiend? | `Nail Fiend's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Nail Fiend's name? | `routed qa` / `-` | 釘の魔人 |
| **yes** | fact | What is the romaji of Nail Fiend's name? | `routed qa` / `-` | Kugi no Majin |
| **yes** | fact | What is Nail Fiend's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Nail Fiend? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Nail Fiend's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (formerly) Wild Fiend |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

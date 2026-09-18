# Page campaign csm/galgali — 2026-09-18-0320

Batch `_csm_page_galgali.json`: 11 questions (5 set, 6 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 9.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/11** |
| set questions exact | 5/5 (100.0%) |
| canon items recovered | 14/14 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Galgali? | `Every named technique of Galgali` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the allies of Galgali? | `Every ally of Galgali` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the enemies of Galgali? | `Every enemy of Galgali` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Galgali? | `Galgali's aliases` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Galgali? | `Galgali's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Galgali's name? | `routed qa` / `-` | ガルガリ |
| **yes** | fact | What is the romaji of Galgali's name? | `routed qa` / `-` | Garugari |
| **yes** | fact | What is the status of Galgali? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Galgali's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |
| **yes** | fact | What is Galgali's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Galgali's height? | `routed qa` / `-` | 178 cm (5'10") |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

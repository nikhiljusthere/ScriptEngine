# Page campaign csm/aldo — 2026-09-18-0430

Batch `_csm_page_aldo.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 10/10 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Aldo? | `Every named technique of Aldo` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the enemies of Aldo? | `Every enemy of Aldo` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the affiliations of Aldo? | `Aldo's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What is the status of Aldo? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Aldo's occupation? | `routed qa` / `-` | Private Devil Hunter |
| **yes** | fact | What is Aldo's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Aldo's name? | `routed qa` / `-` | アルド |
| **yes** | fact | What is the romaji of Aldo's name? | `routed qa` / `-` | Arudo |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

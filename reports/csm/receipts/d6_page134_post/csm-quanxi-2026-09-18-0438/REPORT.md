# Page campaign csm/quanxi — 2026-09-18-0438

Batch `_csm_page_quanxi.json`: 14 questions (9 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 8.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **14/14** |
| set questions exact | 9/9 (100.0%) |
| canon items recovered | 59/59 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Quanxi? | `Every named technique of Quanxi` / `declared` | 11 found, 0 missing; returned 11 |
| **yes** | set | What are all the allies of Quanxi? | `Every ally of Quanxi` / `declared` | 7 found, 0 missing; returned 7 |
| **yes** | set | What are all the enemies of Quanxi? | `Every enemy of Quanxi` / `declared` | 14 found, 0 missing; returned 14 |
| **yes** | set | What are all the rivals of Quanxi? | `Every rival of Quanxi` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the romantics of Quanxi? | `Every romantic of Quanxi` / `declared` | 7 found, 0 missing; returned 7 |
| **yes** | set | What are all the subordinates of Quanxi? | `Every subordinate of Quanxi` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the superiors of Quanxi? | `Every superior of Quanxi` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the affiliations of Quanxi? | `Quanxi's affiliations` / `declared` | 7 found, 0 missing; returned 7 |
| **yes** | set | What are all the aliases of Quanxi? | `Quanxi's aliases` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What is the status of Quanxi? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Quanxi's occupation? | `routed qa` / `-` | Private Devil Hunter (formerly)
Public Safety Devil Hunter |
| **yes** | fact | What is Quanxi's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What are the kanji for Quanxi's name? | `routed qa` / `-` | クァンシ |
| **yes** | fact | What is the romaji of Quanxi's name? | `routed qa` / `-` | Kwanshi |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

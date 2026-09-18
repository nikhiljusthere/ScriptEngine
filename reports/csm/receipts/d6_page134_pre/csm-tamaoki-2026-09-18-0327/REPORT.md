# Page campaign csm/tamaoki — 2026-09-18-0327

Batch `_csm_page_tamaoki.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 6/6 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Tamaoki? | `Every ally of Tamaoki` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the affiliations of Tamaoki? | `Tamaoki's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What is the status of Tamaoki? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Tamaoki's occupation? | `routed qa` / `-` | Public Safety Devil Hunter
Denji’s Bodyguard (formerly) |
| **yes** | fact | What is Tamaoki's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Tamaoki's name? | `routed qa` / `-` | 玉置 |
| **yes** | fact | What is the romaji of Tamaoki's name? | `routed qa` / `-` | Tamaoki |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

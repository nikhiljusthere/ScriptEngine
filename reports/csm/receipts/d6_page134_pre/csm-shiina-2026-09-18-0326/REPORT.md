# Page campaign csm/shiina — 2026-09-18-0326

Batch `_csm_page_shiina.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 7.2s wall clock.

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
| **yes** | set | What are all the allies of Shiina? | `Every ally of Shiina` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Shiina? | `Shiina's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Shiina's name? | `routed qa` / `-` | 椎名 |
| **yes** | fact | What is the romaji of Shiina's name? | `routed qa` / `-` | Shiina |
| **yes** | fact | What is Shiina's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Shiina? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Shiina's occupation? | `routed qa` / `-` | Police Officer Riot Soldier |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

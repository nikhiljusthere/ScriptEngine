# Page campaign csm/kusakabe — 2026-09-18-0435

Batch `_csm_page_kusakabe.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 5.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 7/7 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Kusakabe? | `Every named technique of Kusakabe` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the allies of Kusakabe? | `Every ally of Kusakabe` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the affiliations of Kusakabe? | `Kusakabe's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What is the status of Kusakabe? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Kusakabe's occupation? | `routed qa` / `-` | Public Safety Devil Hunter
Denji’s Bodyguard (formerly) |
| **yes** | fact | What is Kusakabe's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the romaji of Kusakabe's name? | `routed qa` / `-` | Kusakabe |
| **yes** | fact | What are the kanji for Kusakabe's name? | `routed qa` / `-` | 日下部 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

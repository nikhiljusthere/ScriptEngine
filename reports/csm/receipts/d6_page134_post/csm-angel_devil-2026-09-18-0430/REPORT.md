# Page campaign csm/angel_devil — 2026-09-18-0430

Batch `_csm_page_angel_devil.json`: 10 questions (4 set, 6 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 6.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 12/12 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Angel Devil? | `Every named technique of Angel Devil` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the allies of Angel Devil? | `Every ally of Angel Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the affiliations of Angel Devil? | `Angel Devil's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Angel Devil? | `Angel Devil's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Angel Devil's name? | `routed qa` / `-` | エンジェル 天使の悪魔 |
| **yes** | fact | What is the romaji of Angel Devil's name? | `routed qa` / `-` | Enjeru Tenshi no Akuma |
| **yes** | fact | What is the status of Angel Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Angel Devil's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |
| **yes** | fact | What is Angel Devil's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Angel Devil's height? | `routed qa` / `-` | 155 cm (5'1") |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

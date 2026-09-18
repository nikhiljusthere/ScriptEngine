# Page campaign csm/loneliness_fiend — 2026-09-18-0436

Batch `_csm_page_loneliness_fiend.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.8s wall clock.

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
| **yes** | set | What are all the named techniques of Loneliness Fiend? | `Every named technique of Loneliness Fiend` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the enemies of Loneliness Fiend? | `Every enemy of Loneliness Fiend` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Loneliness Fiend's name? | `routed qa` / `-` | 孤独の魔人 |
| **yes** | fact | What is the romaji of Loneliness Fiend's name? | `routed qa` / `-` | Kodoku no Majin |
| **yes** | fact | What is Loneliness Fiend's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Loneliness Fiend? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Loneliness Fiend's occupation? | `routed qa` / `-` | Wild Fiend |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

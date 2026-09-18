# Page campaign csm/nobana_higashiyama — 2026-09-18-0437

Batch `_csm_page_nobana_higashiyama.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 5.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **9/9** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 14/14 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Nobana Higashiyama? | `Every ally of Nobana Higashiyama` / `declared` | 8 found, 0 missing; returned 8 |
| **yes** | set | What are all the enemies of Nobana Higashiyama? | `Every enemy of Nobana Higashiyama` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Nobana Higashiyama? | `Nobana Higashiyama's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the aliases of Nobana Higashiyama? | `Nobana Higashiyama's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Nobana Higashiyama's name? | `routed qa` / `-` | 東山 ノバナ |
| **yes** | fact | What is the romaji of Nobana Higashiyama's name? | `routed qa` / `-` | Higashiyama Nobana |
| **yes** | fact | What is Nobana Higashiyama's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Nobana Higashiyama? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Nobana Higashiyama's occupation? | `routed qa` / `-` | High School Student Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

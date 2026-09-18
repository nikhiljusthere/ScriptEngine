# Page campaign csm/bat_devil — 2026-09-18-0316

Batch `_csm_page_bat_devil.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **9/9** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 15/15 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Bat Devil? | `Every named technique of Bat Devil` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the enemies of Bat Devil? | `Every enemy of Bat Devil` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the affiliations of Bat Devil? | `Bat Devil's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Bat Devil? | `Bat Devil's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Bat Devil's name? | `routed qa` / `-` | コウモリの悪魔 |
| **yes** | fact | What is the romaji of Bat Devil's name? | `routed qa` / `-` | Kōmori no Akuma |
| **yes** | fact | What is Bat Devil's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Bat Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Bat Devil's occupation? | `routed qa` / `-` | Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

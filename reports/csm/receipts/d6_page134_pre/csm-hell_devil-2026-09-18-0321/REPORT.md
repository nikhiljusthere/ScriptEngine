# Page campaign csm/hell_devil — 2026-09-18-0321

Batch `_csm_page_hell_devil.json`: 8 questions (4 set, 4 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 6.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 7/7 (100.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Hell Devil? | `Every named technique of Hell Devil` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the enemies of Hell Devil? | `Every enemy of Hell Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the subordinates of Hell Devil? | `Every subordinate of Hell Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Hell Devil? | `Hell Devil's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Hell Devil's name? | `routed qa` / `-` | 地獄の悪魔 |
| **yes** | fact | What is the romaji of Hell Devil's name? | `routed qa` / `-` | Jigoku no Akuma |
| **yes** | fact | What is the status of Hell Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Hell Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

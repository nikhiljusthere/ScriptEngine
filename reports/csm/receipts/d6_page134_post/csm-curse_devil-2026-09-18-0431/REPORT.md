# Page campaign csm/curse_devil — 2026-09-18-0431

Batch `_csm_page_curse_devil.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 3.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/6** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 2/2 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Curse Devil? | `Every named technique of Curse Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Curse Devil's name? | `routed qa` / `-` | 呪いの悪魔 |
| **yes** | fact | What is the romaji of Curse Devil's name? | `routed qa` / `-` | Noroi no Akuma |
| **yes** | fact | What is Curse Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Curse Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Curse Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

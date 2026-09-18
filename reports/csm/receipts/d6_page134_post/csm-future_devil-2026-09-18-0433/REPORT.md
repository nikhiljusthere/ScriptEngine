# Page campaign csm/future_devil — 2026-09-18-0433

Batch `_csm_page_future_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 2/2 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Future Devil? | `Every named technique of Future Devil` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Future Devil? | `Future Devil's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Future Devil's name? | `routed qa` / `-` | 未来の悪魔 |
| **yes** | fact | What is the romaji of Future Devil's name? | `routed qa` / `-` | Mirai no Akuma |
| **yes** | fact | What is the status of Future Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Future Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Future Devil's occupation? | `routed qa` / `-` | Wild Devil (formerly) Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

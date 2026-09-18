# Page campaign csm/pochita — 2026-09-18-0438

Batch `_csm_page_pochita.json`: 12 questions (7 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 7.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **12/12** |
| set questions exact | 7/7 (100.0%) |
| canon items recovered | 49/49 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Pochita? | `Every named technique of Pochita` / `declared` | 10 found, 0 missing; returned 10 |
| **yes** | set | What are all the allies of Pochita? | `Every ally of Pochita` / `declared` | 11 found, 0 missing; returned 11 |
| **yes** | set | What are all the enemies of Pochita? | `Every enemy of Pochita` / `declared` | 16 found, 0 missing; returned 16 |
| **yes** | set | What are all the rivals of Pochita? | `Every rival of Pochita` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the romantics of Pochita? | `Every romantic of Pochita` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Pochita? | `Pochita's aliases` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the affiliations of Pochita? | `Pochita's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Pochita's name? | `routed qa` / `-` | ポチタ |
| **yes** | fact | What is the romaji of Pochita's name? | `routed qa` / `-` | Pochita |
| **yes** | fact | What is Pochita's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Pochita? | `routed qa` / `-` | Erased (original timeline) Unknown (new timeline) |
| **yes** | fact | What is Pochita's occupation? | `routed qa` / `-` | Wild Devil (formerly) Contract Devil Denji's Heart |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

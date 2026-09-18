# Page campaign csm/fox_devil — 2026-09-18-0319

Batch `_csm_page_fox_devil.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 6.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 6/6 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Fox Devil? | `Every named technique of Fox Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the allies of Fox Devil? | `Every ally of Fox Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Fox Devil? | `Fox Devil's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Fox Devil's name? | `routed qa` / `-` | 狐の悪魔 |
| **yes** | fact | What is the romaji of Fox Devil's name? | `routed qa` / `-` | Kitsune no Akuma |
| **yes** | fact | What is the status of Fox Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Fox Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Fox Devil's occupation? | `routed qa` / `-` | Wild Devil (formerly) Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

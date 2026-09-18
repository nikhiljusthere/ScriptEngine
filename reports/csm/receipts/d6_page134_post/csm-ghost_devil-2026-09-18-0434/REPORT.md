# Page campaign csm/ghost_devil — 2026-09-18-0434

Batch `_csm_page_ghost_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 6/6 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Ghost Devil? | `Every named technique of Ghost Devil` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the superiors of Ghost Devil? | `Every superior of Ghost Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Ghost Devil's name? | `routed qa` / `-` | 幽霊の悪魔 |
| **yes** | fact | What is the romaji of Ghost Devil's name? | `routed qa` / `-` | Yūrei no Akuma |
| **yes** | fact | What is Ghost Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Ghost Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Ghost Devil's occupation? | `routed qa` / `-` | Wild Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

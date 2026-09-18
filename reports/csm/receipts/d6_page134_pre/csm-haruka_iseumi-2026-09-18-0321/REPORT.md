# Page campaign csm/haruka_iseumi — 2026-09-18-0321

Batch `_csm_page_haruka_iseumi.json`: 11 questions (6 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 8.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/11** |
| set questions exact | 6/6 (100.0%) |
| canon items recovered | 19/19 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Haruka Iseumi? | `Every ally of Haruka Iseumi` / `declared` | 7 found, 0 missing; returned 7 |
| **yes** | set | What are all the enemies of Haruka Iseumi? | `Every enemy of Haruka Iseumi` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the subordinates of Haruka Iseumi? | `Every subordinate of Haruka Iseumi` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the superiors of Haruka Iseumi? | `Every superior of Haruka Iseumi` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Haruka Iseumi? | `Haruka Iseumi's affiliations` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the aliases of Haruka Iseumi? | `Haruka Iseumi's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Haruka Iseumi's name? | `routed qa` / `-` | 伊勢海 ハルカ |
| **yes** | fact | What is the romaji of Haruka Iseumi's name? | `routed qa` / `-` | Iseumi Haruka |
| **yes** | fact | What is the status of Haruka Iseumi? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Haruka Iseumi's occupation? | `routed qa` / `-` | High School Student Devil Hunter Public Speaker |
| **yes** | fact | What is Haruka Iseumi's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

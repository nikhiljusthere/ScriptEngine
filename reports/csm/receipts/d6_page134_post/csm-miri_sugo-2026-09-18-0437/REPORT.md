# Page campaign csm/miri_sugo — 2026-09-18-0437

Batch `_csm_page_miri_sugo.json`: 12 questions (7 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 6.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **12/12** |
| set questions exact | 7/7 (100.0%) |
| canon items recovered | 22/22 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Miri Sugo? | `Every named technique of Miri Sugo` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the allies of Miri Sugo? | `Every ally of Miri Sugo` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the enemies of Miri Sugo? | `Every enemy of Miri Sugo` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the subordinates of Miri Sugo? | `Every subordinate of Miri Sugo` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the superiors of Miri Sugo? | `Every superior of Miri Sugo` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Miri Sugo? | `Miri Sugo's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Miri Sugo? | `Miri Sugo's affiliations` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | fact | What are the kanji for Miri Sugo's name? | `routed qa` / `-` | 須郷 ミリ |
| **yes** | fact | What is the romaji of Miri Sugo's name? | `routed qa` / `-` | Sugō Miri |
| **yes** | fact | What is the status of Miri Sugo? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Miri Sugo's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (brainwashed) High School Student |
| **yes** | fact | What is Miri Sugo's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

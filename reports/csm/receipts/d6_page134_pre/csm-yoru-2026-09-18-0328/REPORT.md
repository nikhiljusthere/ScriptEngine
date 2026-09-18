# Page campaign csm/yoru — 2026-09-18-0328

Batch `_csm_page_yoru.json`: 17 questions (11 set, 6 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 10.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **17/17** |
| set questions exact | 11/11 (100.0%) |
| canon items recovered | 98/98 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Yoru? | `Every named technique of Yoru` / `declared` | 34 found, 0 missing; returned 34 |
| **yes** | set | What are all the allies of Yoru? | `Every ally of Yoru` / `declared` | 16 found, 0 missing; returned 16 |
| **yes** | set | What are all the creators of Yoru? | `Every creator of Yoru` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the enemies of Yoru? | `Every enemy of Yoru` / `declared` | 15 found, 0 missing; returned 15 |
| **yes** | set | What are all the families of Yoru? | `Every family of Yoru` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the friends of Yoru? | `Every friend of Yoru` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the rivals of Yoru? | `Every rival of Yoru` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the romantics of Yoru? | `Every romantic of Yoru` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the subordinates of Yoru? | `Every subordinate of Yoru` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the affiliations of Yoru? | `Yoru's affiliations` / `declared` | 7 found, 0 missing; returned 7 |
| **yes** | set | What are all the aliases of Yoru? | `Yoru's aliases` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | fact | What are the kanji for Yoru's name? | `routed qa` / `-` | ヨル |
| **yes** | fact | What is the romaji of Yoru's name? | `routed qa` / `-` | Yoru |
| **yes** | fact | What is Yoru's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Yoru? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Yoru? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Yoru's occupation? | `routed qa` / `-` | High School Student (cover; formerly) Private Devil Hunter (formerly) Wild Fiend (formerly) Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

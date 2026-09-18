# Page campaign csm/makima — 2026-09-18-0323

Batch `_csm_page_makima.json`: 16 questions (8 set, 8 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 10.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **16/16** |
| set questions exact | 8/8 (100.0%) |
| canon items recovered | 78/78 (100.0%) |
| fact answers present | 8/8 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Makima? | `Every named technique of Makima` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the allies of Makima? | `Every ally of Makima` / `declared` | 8 found, 0 missing; returned 8 |
| **yes** | set | What are all the enemies of Makima? | `Every enemy of Makima` / `declared` | 13 found, 0 missing; returned 13 |
| **yes** | set | What are all the romantics of Makima? | `Every romantic of Makima` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the subordinates of Makima? | `Every subordinate of Makima` / `declared` | 27 found, 0 missing; returned 27 |
| **yes** | set | What are all the superiors of Makima? | `Every superior of Makima` / `declared` | 16 found, 0 missing; returned 16 |
| **yes** | set | What are all the affiliations of Makima? | `Makima's affiliations` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the aliases of Makima? | `Makima's aliases` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Makima's name? | `routed qa` / `-` | マキマ |
| **yes** | fact | What is the romaji of Makima's name? | `routed qa` / `-` | Makima |
| **yes** | fact | What is Makima's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Makima's height? | `routed qa` / `-` | 168 cm (5'6") |
| **yes** | fact | What is the status of Makima? | `routed qa` / `-` | Deceased; Reincarnated |
| **yes** | fact | What is Makima's occupation? | `routed qa` / `-` | Public Safety Devil Hunter Contract Devil |
| **yes** | fact | How old is Makima? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Makima's birthday? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

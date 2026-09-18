# Page campaign csm/seigi_akoku — 2026-09-18-0326

Batch `_csm_page_seigi_akoku.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 13/13 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Seigi Akoku? | `Every named technique of Seigi Akoku` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the allies of Seigi Akoku? | `Every ally of Seigi Akoku` / `declared` | 9 found, 0 missing; returned 9 |
| **yes** | set | What are all the affiliations of Seigi Akoku? | `Seigi Akoku's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What is the status of Seigi Akoku? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Seigi Akoku's occupation? | `routed qa` / `-` | High School Student Devil Hunter |
| **yes** | fact | What is Seigi Akoku's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Seigi Akoku's name? | `routed qa` / `-` | 亜国 セイギ |
| **yes** | fact | What is the romaji of Seigi Akoku's name? | `routed qa` / `-` | Akoku Seigi |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/nayuta — 2026-09-18-0437

Batch `_csm_page_nayuta.json`: 14 questions (8 set, 6 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 7.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **14/14** |
| set questions exact | 8/8 (100.0%) |
| canon items recovered | 25/25 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Nayuta? | `Every named technique of Nayuta` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the allies of Nayuta? | `Every ally of Nayuta` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the enemies of Nayuta? | `Every enemy of Nayuta` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the families of Nayuta? | `Every family of Nayuta` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the subordinates of Nayuta? | `Every subordinate of Nayuta` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the superiors of Nayuta? | `Every superior of Nayuta` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Nayuta? | `Nayuta's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Nayuta? | `Nayuta's aliases` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | fact | What are the kanji for Nayuta's name? | `routed qa` / `-` | ナユタ |
| **yes** | fact | What is the romaji of Nayuta's name? | `routed qa` / `-` | Nayuta |
| **yes** | fact | What is Nayuta's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Nayuta? | `routed qa` / `-` | Deceased (original timeline) Alive (new timeline) |
| **yes** | fact | What is Nayuta's occupation? | `routed qa` / `-` | School Student (formerly) Wild Devil (formerly) Public Safety Devil Hunter |
| **yes** | fact | What is Nayuta's birthday? | `routed qa` / `-` | 1997 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

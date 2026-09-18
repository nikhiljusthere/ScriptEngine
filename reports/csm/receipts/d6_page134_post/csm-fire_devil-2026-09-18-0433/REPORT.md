# Page campaign csm/fire_devil — 2026-09-18-0433

Batch `_csm_page_fire_devil.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 6.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **9/9** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 11/11 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Fire Devil? | `Every named technique of Fire Devil` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the allies of Fire Devil? | `Every ally of Fire Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Fire Devil? | `Fire Devil's affiliations` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the aliases of Fire Devil? | `Fire Devil's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Fire Devil's name? | `routed qa` / `-` | 火の悪魔 |
| **yes** | fact | What is the romaji of Fire Devil's name? | `routed qa` / `-` | Hi no Akuma |
| **yes** | fact | What is Fire Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Fire Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Fire Devil's occupation? | `routed qa` / `-` | Wild Contract Devil High School Student (Allegedly) Death's Pawn |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

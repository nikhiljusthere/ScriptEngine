# Page campaign csm/guillotine_devil — 2026-09-18-0434

Batch `_csm_page_guillotine_devil.json`: 7 questions (3 set, 4 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 5.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 4/4 (100.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Guillotine Devil? | `Every named technique of Guillotine Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Guillotine Devil? | `Guillotine Devil's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Guillotine Devil? | `Guillotine Devil's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Guillotine Devil's name? | `routed qa` / `-` | ギロチンの悪魔 |
| **yes** | fact | What is the romaji of Guillotine Devil's name? | `routed qa` / `-` | Girochin no Akuma |
| **yes** | fact | What is the status of Guillotine Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Guillotine Devil's occupation? | `routed qa` / `-` | Death's Pawn |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

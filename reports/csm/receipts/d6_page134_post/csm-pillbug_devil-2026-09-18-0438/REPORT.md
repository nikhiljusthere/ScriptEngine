# Page campaign csm/pillbug_devil — 2026-09-18-0438

Batch `_csm_page_pillbug_devil.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 4/4 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Pillbug Devil? | `Every named technique of Pillbug Devil` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the aliases of Pillbug Devil? | `Pillbug Devil's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Pillbug Devil? | `Pillbug Devil's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Pillbug Devil's name? | `routed qa` / `-` | ダンゴムシの悪魔 |
| **yes** | fact | What is the romaji of Pillbug Devil's name? | `routed qa` / `-` | Dangomushi no Akuma |
| **yes** | fact | What is Pillbug Devil's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Pillbug Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Pillbug Devil's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

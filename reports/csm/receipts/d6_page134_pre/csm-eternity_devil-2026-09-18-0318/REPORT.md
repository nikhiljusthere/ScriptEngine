# Page campaign csm/eternity_devil — 2026-09-18-0318

Batch `_csm_page_eternity_devil.json`: 9 questions (4 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 7.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **9/9** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 12/12 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Eternity Devil? | `Every named technique of Eternity Devil` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the allies of Eternity Devil? | `Every ally of Eternity Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the enemies of Eternity Devil? | `Every enemy of Eternity Devil` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the affiliations of Eternity Devil? | `Eternity Devil's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Eternity Devil's name? | `routed qa` / `-` | 永遠の悪魔 |
| **yes** | fact | What is the romaji of Eternity Devil's name? | `routed qa` / `-` | Eien no Akuma |
| **yes** | fact | What is Eternity Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Eternity Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Eternity Devil's occupation? | `routed qa` / `-` | Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

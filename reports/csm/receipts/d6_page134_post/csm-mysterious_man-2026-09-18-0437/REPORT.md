# Page campaign csm/mysterious_man — 2026-09-18-0437

Batch `_csm_page_mysterious_man.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 5.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 3/3 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Mysterious Man? | `Every named technique of Mysterious Man` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the aliases of Mysterious Man? | `Mysterious Man's aliases` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Mysterious Man? | `Mysterious Man's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Mysterious Man's name? | `routed qa` / `-` | 謎の男 |
| **yes** | fact | What is the romaji of Mysterious Man's name? | `routed qa` / `-` | Nazo no Otoko |
| **yes** | fact | What is Mysterious Man's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Mysterious Man? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Mysterious Man's occupation? | `routed qa` / `-` | Private Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

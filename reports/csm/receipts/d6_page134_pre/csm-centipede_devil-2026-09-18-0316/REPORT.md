# Page campaign csm/centipede_devil — 2026-09-18-0316

Batch `_csm_page_centipede_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 4.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 4/4 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Centipede Devil? | `Every ally of Centipede Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Centipede Devil? | `Centipede Devil's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Centipede Devil's name? | `routed qa` / `-` | ムカデの悪魔 |
| **yes** | fact | What is the romaji of Centipede Devil's name? | `routed qa` / `-` | Mukade no Akuma |
| **yes** | fact | What is the status of Centipede Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Centipede Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Centipede Devil's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

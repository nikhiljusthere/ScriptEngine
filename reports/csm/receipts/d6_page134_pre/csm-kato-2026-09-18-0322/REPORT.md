# Page campaign csm/kato — 2026-09-18-0322

Batch `_csm_page_kato.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 4.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 3/3 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Kato? | `Every named technique of Kato` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the affiliations of Kato? | `Kato's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Kato's name? | `routed qa` / `-` | 加藤 |
| **yes** | fact | What is the romaji of Kato's name? | `routed qa` / `-` | Katō |
| **yes** | fact | What is Kato's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Kato? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Kato's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

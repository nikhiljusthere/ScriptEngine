# Page campaign csm/nomo — 2026-09-18-0438

Batch `_csm_page_nomo.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.1s wall clock.

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
| **yes** | set | What are all the named techniques of Nomo? | `Every named technique of Nomo` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Nomo? | `Nomo's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Nomo's name? | `routed qa` / `-` | 野茂 |
| **yes** | fact | What is the romaji of Nomo's name? | `routed qa` / `-` | Nomo |
| **yes** | fact | What is Nomo's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Nomo? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Nomo's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

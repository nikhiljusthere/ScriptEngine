# Page campaign csm/virtue — 2026-09-18-0441

Batch `_csm_page_virtue.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/6** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the affiliations of Virtue? | `Virtue's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Virtue's name? | `routed qa` / `-` | ヴァーチェ |
| **yes** | fact | What is the romaji of Virtue's name? | `routed qa` / `-` | Vāche |
| **yes** | fact | What is Virtue's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Virtue? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Virtue's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

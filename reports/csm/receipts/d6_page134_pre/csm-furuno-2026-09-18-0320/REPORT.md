# Page campaign csm/furuno — 2026-09-18-0320

Batch `_csm_page_furuno.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 7.5s wall clock.

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
| **yes** | set | What are all the allies of Furuno? | `Every ally of Furuno` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Furuno? | `Furuno's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Furuno's name? | `routed qa` / `-` | 古野 |
| **yes** | fact | What is the romaji of Furuno's name? | `routed qa` / `-` | Furuno |
| **yes** | fact | What is Furuno's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Furuno? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Furuno's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

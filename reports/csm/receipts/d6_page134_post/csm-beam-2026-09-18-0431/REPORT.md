# Page campaign csm/beam — 2026-09-18-0431

Batch `_csm_page_beam.json`: 11 questions (5 set, 6 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 7.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/11** |
| set questions exact | 5/5 (100.0%) |
| canon items recovered | 16/16 (100.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Beam? | `Every named technique of Beam` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the allies of Beam? | `Every ally of Beam` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the enemies of Beam? | `Every enemy of Beam` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the affiliations of Beam? | `Beam's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the aliases of Beam? | `Beam's aliases` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Beam's name? | `routed qa` / `-` | ビーム |
| **yes** | fact | What is the romaji of Beam's name? | `routed qa` / `-` | Bīmu |
| **yes** | fact | What is Beam's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Beam's height? | `routed qa` / `-` | 176 cm (5'9¼") |
| **yes** | fact | What is the status of Beam? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Beam's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

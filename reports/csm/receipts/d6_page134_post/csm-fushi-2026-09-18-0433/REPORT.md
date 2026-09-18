# Page campaign csm/fushi — 2026-09-18-0433

Batch `_csm_page_fushi.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/6** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 2/2 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the affiliations of Fushi? | `Fushi's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Fushi's name? | `routed qa` / `-` | 伏 |
| **yes** | fact | What is the romaji of Fushi's name? | `routed qa` / `-` | Fushi |
| **yes** | fact | What is the status of Fushi? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Fushi's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |
| **yes** | fact | What is Fushi's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

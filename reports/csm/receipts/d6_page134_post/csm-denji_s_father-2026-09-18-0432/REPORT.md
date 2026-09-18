# Page campaign csm/denji_s_father — 2026-09-18-0432

Batch `_csm_page_denji_s_father.json`: 4 questions (2 set, 2 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 2.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/4** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 3/3 (100.0%) |
| fact answers present | 2/2 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the families of Denji's Father? | `Every family of Denji's Father` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Denji's Father? | `Denji's Father's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What is Denji's Father's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Denji's Father? | `routed qa` / `-` | Deceased |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

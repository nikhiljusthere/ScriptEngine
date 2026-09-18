# Page campaign csm/spear_hybrid — 2026-09-18-0439

Batch `_csm_page_spear_hybrid.json`: 7 questions (4 set, 3 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 3.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 4/4 (100.0%) |
| canon items recovered | 13/13 (100.0%) |
| fact answers present | 3/3 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Spear Hybrid? | `Every named technique of Spear Hybrid` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the allies of Spear Hybrid? | `Every ally of Spear Hybrid` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the superiors of Spear Hybrid? | `Every superior of Spear Hybrid` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Spear Hybrid? | `Spear Hybrid's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What is the status of Spear Hybrid? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Spear Hybrid's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (brainwashed) |
| **yes** | fact | What is Spear Hybrid's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

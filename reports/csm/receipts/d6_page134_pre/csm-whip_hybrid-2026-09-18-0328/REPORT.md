# Page campaign csm/whip_hybrid — 2026-09-18-0328

Batch `_csm_page_whip_hybrid.json`: 10 questions (5 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 5/5 (100.0%) |
| canon items recovered | 16/16 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Whip Hybrid? | `Every named technique of Whip Hybrid` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the allies of Whip Hybrid? | `Every ally of Whip Hybrid` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the enemies of Whip Hybrid? | `Every enemy of Whip Hybrid` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the superiors of Whip Hybrid? | `Every superior of Whip Hybrid` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Whip Hybrid? | `Whip Hybrid's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What is the status of Whip Hybrid? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Whip Hybrid's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (brainwashed) |
| **yes** | fact | What is Whip Hybrid's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Whip Hybrid? | `routed qa` / `-` | 81 |
| **yes** | fact | What is Whip Hybrid's birthday? | `routed qa` / `-` | 1917 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

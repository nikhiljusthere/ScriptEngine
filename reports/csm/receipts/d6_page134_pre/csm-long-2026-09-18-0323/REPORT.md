# Page campaign csm/long — 2026-09-18-0323

Batch `_csm_page_long.json`: 10 questions (5 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 5.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 5/5 (100.0%) |
| canon items recovered | 8/8 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Long? | `Every named technique of Long` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | set | What are all the allies of Long? | `Every ally of Long` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the enemies of Long? | `Every enemy of Long` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the subordinates of Long? | `Every subordinate of Long` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Long? | `Long's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Long's name? | `routed qa` / `-` | ロン |
| **yes** | fact | What is the romaji of Long's name? | `routed qa` / `-` | Ron |
| **yes** | fact | What is the status of Long? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Long's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Long's occupation? | `routed qa` / `-` | Private Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

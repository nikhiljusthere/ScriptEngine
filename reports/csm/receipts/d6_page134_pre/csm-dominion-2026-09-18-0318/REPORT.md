# Page campaign csm/dominion — 2026-09-18-0318

Batch `_csm_page_dominion.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 6.3s wall clock.

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
| **yes** | set | What are all the affiliations of Dominion? | `Dominion's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Dominion's name? | `routed qa` / `-` | ドミニオン |
| **yes** | fact | What is the romaji of Dominion's name? | `routed qa` / `-` | Dominion |
| **yes** | fact | What is Dominion's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Dominion? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Dominion's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/bat_devil_arc — 2026-09-17-1351

Batch `_csm_page_bat_devil_arc.json`: 5 questions (0 set, 5 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 4.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/5** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | Which saga does Bat Devil arc belong to? | `routed qa` / `-` | Public Safety Saga |
| **yes** | fact | Which chapters are included in Bat Devil arc? | `routed qa` / `-` | Chapter 5 - 13 |
| **yes** | fact | Which episodes are included in Bat Devil arc? | `routed qa` / `-` | Episode 2 - 5 |
| **yes** | fact | What comes before Bat Devil arc? | `routed qa` / `-` | Introduction arc |
| **yes** | fact | What comes after Bat Devil arc? | `routed qa` / `-` | Eternity Devil arc |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

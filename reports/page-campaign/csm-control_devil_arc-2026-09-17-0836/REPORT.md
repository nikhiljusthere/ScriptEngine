# Page campaign csm/control_devil_arc — 2026-09-17-0836

Batch `_csm_page_control_devil_arc.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/4** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | Which saga does Control Devil arc belong to? | `routed qa` / `-` | Public Safety Saga |
| **yes** | fact | Which chapters are included in Control Devil arc? | `routed qa` / `-` | Chapter 80 - 97 |
| **yes** | fact | What comes before Control Devil arc? | `routed qa` / `-` | Gun Devil arc |
| **yes** | fact | What comes after Control Devil arc? | `routed qa` / `-` | Justice Devil arc |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

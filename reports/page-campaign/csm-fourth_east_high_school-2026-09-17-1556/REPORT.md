# Page campaign csm/fourth_east_high_school — 2026-09-17-1556

Batch `_csm_page_fourth_east_high_school.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-17T14:24:38+00:00), 2.9s wall clock.

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
| **yes** | fact | What type of song is Fourth East High School? | `routed qa` / `-` | High School |
| **yes** | fact | What services does Fourth East High School provide? | `routed qa` / `-` | Education |
| **yes** | fact | In which manga chapter does Fourth East High School first appear? | `routed qa` / `-` | Chapter 98 |
| **yes** | fact | Which series does Fourth East High School belong to? | `routed qa` / `-` | Fourth East High School |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

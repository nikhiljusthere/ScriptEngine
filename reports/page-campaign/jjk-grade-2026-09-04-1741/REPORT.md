# Page campaign jjk/grade — 2026-09-04-1741

Batch `_jjk_page_grade.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.4s wall clock.

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
| **yes** | fact | How does Jujutsu High assign sorcerer grades? | `routed qa` / `-` | ascending from grade 4 to grade 1 |
| **yes** | fact | What distinguishes a grade 2 curse from a semi-grade 1 curse? | `routed qa` / `-` | whether or not it is capable of using cursed techniques |
| **yes** | fact | What is a special grade sorcerer capable of? | `routed qa` / `-` | wiping out a nation singlehandedly |
| **yes** | fact | How can jujutsu sorcerers be promoted up in rank? | `routed qa` / `-` | by receiving a recommendation from a sorcerer of a higher rank |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

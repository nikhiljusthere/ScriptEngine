# Page campaign csm/tokyo_special_division_4 — 2026-09-18-0440

Batch `_csm_page_tokyo_special_division_4.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 2.6s wall clock.

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
| **yes** | fact | What is Tokyo Special Division 4's allegiance? | `routed qa` / `-` | Public Safety Devil Hunters |
| **yes** | fact | Who are Tokyo Special Division 4's notable members? | `routed roster` / `partial` | Himeno, Denji, Aki Hayakawa, Power |
| **yes** | fact | Which series does Tokyo Special Division 4 belong to? | `routed qa` / `-` | Tokyo Special Division 4 |
| **yes** | fact | In which manga chapter does Tokyo Special Division 4 first appear? | `routed qa` / `-` | Chapter 5 (mentioned) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

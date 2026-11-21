# Page campaign csm/anti_makima_squad — 2026-09-17-0814

Batch `_csm_page_anti_makima_squad.json`: 2 questions (0 set, 2 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **2/2** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 2/2 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | Who are Anti-Makima Squad's notable members? | `routed qa` / `-` | Kishibe Hell Devil |
| **yes** | fact | In which manga chapter does Anti-Makima Squad first appear? | `routed qa` / `-` | Chapter 83 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

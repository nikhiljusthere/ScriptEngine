# Page campaign csm/prophecy_of_nostradamus — 2026-09-17-0844

Batch `_csm_page_prophecy_of_nostradamus.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/3** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 3/3 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Prophecy of Nostradamus's allegiance? | `routed qa` / `-` | Devils |
| **yes** | fact | Who are Prophecy of Nostradamus's notable members? | `routed qa` / `-` | Death Devil |
| **yes** | fact | In which manga chapter does Prophecy of Nostradamus first appear? | `routed qa` / `-` | Chapter 122 (Mentioned) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

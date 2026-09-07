# Page campaign jjk/chapter_91 — 2026-09-04-1442

Batch `_jjk_page_chapter_91.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 5.0s wall clock.

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
| **yes** | fact | What must the team act quickly to do, per Chapter 91? | `routed qa` / `-` | rescue Gojo before the entire world as they know it is upended |
| **yes** | fact | On what date was Kokichi Muta killed by Mahito, per Chapter 91? | `routed qa` / `-` | October 19th |
| **yes** | fact | How many of these Mechamaru puppets are there in separate locations, per Chapter 91? | `routed roster` / `exact` | three |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

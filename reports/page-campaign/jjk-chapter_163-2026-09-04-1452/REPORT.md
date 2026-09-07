# Page campaign jjk/chapter_163 — 2026-09-04-1452

Batch `_jjk_page_chapter_163.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.5s wall clock.

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
| **yes** | fact | Who leads Megumi into a confrontation with another player named Reggie, per Chapter 163? | `routed qa` / `-` | Remi |
| **yes** | fact | What is Yuji's nickname in Sendai, per Chapter 163? | `routed qa` / `-` | the Tiger of West Junior High |
| **yes** | fact | Where is Higuruma sitting when Yuji enters the theater, per Chapter 163? | `routed qa` / `-` | in a bathtub filled with water while he's still fully clothed |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

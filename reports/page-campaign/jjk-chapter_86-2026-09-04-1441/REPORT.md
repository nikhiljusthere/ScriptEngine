# Page campaign jjk/chapter_86 — 2026-09-04-1441

Batch `_jjk_page_chapter_86.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 5.0s wall clock.

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
| **yes** | fact | Who does the jujutsu student come face to face with, per Chapter 86? | `routed qa` / `-` | a very "smart" cursed spirit |
| **yes** | fact | How many basement floors are in the station, per Chapter 86? | `routed roster` / `exact` | five basement floors |
| **yes** | fact | Whom does Yuji discover devouring a deceased man's head in B2F, per Chapter 86? | `routed qa` / `-` | a grasshopper curse |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

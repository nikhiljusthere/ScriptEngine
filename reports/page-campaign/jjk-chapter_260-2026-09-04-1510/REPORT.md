# Page campaign jjk/chapter_260 — 2026-09-04-1510

Batch `_jjk_page_chapter_260.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.6s wall clock.

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
| **yes** | fact | Who does Todo fight alongside to bring down Sukuna, per Chapter 260? | `routed roster` / `declared` | Yuji |
| **yes** | fact | What does Todo replace his severed left hand with, per Chapter 260? | `routed qa` / `-` | a vibraslap |
| **yes** | fact | What does Sukuna destroy with a kick just as Todo strikes the vibraslap, per Chapter 260? | `routed qa` / `-` | the bird |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

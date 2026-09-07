# Page campaign jjk/chapter_2 — 2026-09-04-1428

Batch `_jjk_page_chapter_2.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 4.2s wall clock.

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
| **yes** | fact | What option does Satoru give Yuji instead of being executed, per Chapter 2? | `routed qa` / `-` | find the appendages of Sukuna and consume them all |
| **yes** | fact | For how long must Yuji switch to Sukuna's consciousness to prove he can contain the curse, per Chapter 2? | `routed qa` / `-` | ten seconds |
| **yes** | fact | How many of Sukuna's fingers does Jujutsu High have in its possession, per Chapter 2? | `routed qa` / `-` | six |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/chapter_140 — 2026-09-04-1448

Batch `_jjk_page_chapter_140.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.4s wall clock.

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
| **yes** | fact | What does Yuta do to cut in the middle of Yuji and Choso's scuffle with Naoya, per Chapter 140? | `routed qa` / `-` | descends on the scene |
| **yes** | fact | What does Choso say Yuta must be, per Chapter 140? | `routed qa` / `-` | Yuji's executioner |
| **yes** | fact | What does Yuji remember from Nanami's final words, per Chapter 140? | `routed qa` / `-` | he can't die yet |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

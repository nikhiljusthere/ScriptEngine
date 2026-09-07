# Page campaign jjk/chapter_120 — 2026-09-04-1446

Batch `_jjk_page_chapter_120.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.4s wall clock.

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
| **yes** | fact | Whom does Nanami reluctantly reunite with, per Chapter 120? | `routed qa` / `-` | a familiar foe |
| **yes** | fact | Whom does the curtain inside the photo booth reveal, per Chapter 120? | `routed qa` / `-` | Mahito |
| **yes** | fact | What does Mahito do to Nanami in his final moments, per Chapter 120? | `routed qa` / `-` | totally destroying the top half of his body |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

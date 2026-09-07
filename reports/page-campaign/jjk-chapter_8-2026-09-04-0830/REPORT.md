# Page campaign jjk/chapter_8 — 2026-09-04-0830

Batch `_jjk_page_chapter_8.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T08:23:53+00:00), 3.6s wall clock.

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
| **yes** | fact | What does Sukuna end up doing, contrary to his intent to slaughter Yuji's friends, per Chapter 8? | `routed qa` / `-` | killing the other special grade curse |
| **yes** | fact | Using which Domain Expansion does Sukuna slice the special grade curse to pieces, per Chapter 8? | `routed qa` / `-` | Malevolent Shrine |
| **yes** | fact | What does Sukuna rip out of Yuji, per Chapter 8? | `routed qa` / `-` | Yuji's heart |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

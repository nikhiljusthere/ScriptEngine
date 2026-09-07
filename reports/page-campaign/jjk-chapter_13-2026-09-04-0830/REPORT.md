# Page campaign jjk/chapter_13 — 2026-09-04-0830

Batch `_jjk_page_chapter_13.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T08:23:53+00:00), 3.6s wall clock.

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
| **yes** | fact | What must Yuji control while watching movies if he is ever to control cursed energy, per Chapter 13? | `routed qa` / `-` | his emotions |
| **yes** | fact | What does Gojo task Yuji with holding onto while he watches the films, per Chapter 13? | `routed qa` / `-` | one of the Principal's cursed corpses |
| **yes** | fact | What will awaken and attack if it is not receiving a constant flow of cursed energy, per Chapter 13? | `routed qa` / `-` | The doll |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

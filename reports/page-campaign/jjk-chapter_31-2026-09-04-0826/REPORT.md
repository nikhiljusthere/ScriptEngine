# Page campaign jjk/chapter_31 — 2026-09-04-0826

Batch `_jjk_page_chapter_31.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T08:23:53+00:00), 3.6s wall clock.

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
| **yes** | fact | What does Nanami talk with Yuji about, after Yuji is upset by his prior actions, per Chapter 31? | `routed qa` / `-` | what it means to die a natural death |
| **yes** | fact | What form does Mahito mutate into in order to avoid death, per Chapter 31? | `routed qa` / `-` | a tall, bloated form |
| **yes** | fact | Whom does Nanami call to intercept Mahito in the sewers, per Chapter 31? | `routed qa` / `-` | Ino |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

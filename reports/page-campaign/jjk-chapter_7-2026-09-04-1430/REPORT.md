# Page campaign jjk/chapter_7 — 2026-09-04-1430

Batch `_jjk_page_chapter_7.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.3s wall clock.

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
| **yes** | fact | What last resort plan does Yuji bet on to turn the battle in their favor, per Chapter 7? | `routed qa` / `-` | use Sukuna to their advantage |
| **yes** | fact | Which flying shikigami does Megumi call on to secure him as he falls, per Chapter 7? | `routed qa` / `-` | Nue |
| **yes** | fact | Which shikigami does Megumi use to rescue Nobara before she is devoured, per Chapter 7? | `routed qa` / `-` | his Toad shikigami |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

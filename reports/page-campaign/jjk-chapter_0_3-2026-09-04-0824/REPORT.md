# Page campaign jjk/chapter_0_3 — 2026-09-04-0824

Batch `_jjk_page_chapter_0_3.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T08:23:53+00:00), 3.3s wall clock.

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
| **yes** | fact | What does Suguru invoke to summon thousands of curses in Kyoto and Shinjuku, per Chapter 0-3? | `routed qa` / `-` | the Night Parade of a Hundred Demons |
| **yes** | fact | How is Suguru able to accurately guess the woman's daughter's symptoms at his temple, per Chapter 0-3? | `routed qa` / `-` | he can see the curse hanging on to her |
| **yes** | fact | What is the name of Suguru's assistant, per Chapter 0-3? | `routed qa` / `-` | Manami Suda |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/chapter_5 — 2026-09-04-0829

Batch `_jjk_page_chapter_5.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T08:23:53+00:00), 4.2s wall clock.

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
| **yes** | fact | Whom do Nobara and Yuji manage to save inside the abandoned house, per Chapter 5? | `routed qa` / `-` | a young boy |
| **yes** | fact | What begins to grow a special grade cursed spirit elsewhere, per Chapter 5? | `routed qa` / `-` | a cursed womb |
| **yes** | fact | In July 2018, how many of the three students who went to deal with the curse died, per Chapter 5? | `routed qa` / `-` | one |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

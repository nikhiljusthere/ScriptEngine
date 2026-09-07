# Page campaign jjk/chapter_30 — 2026-09-04-1428

Batch `_jjk_page_chapter_30.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.5s wall clock.

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
| **yes** | fact | What was Nanami's occupation after he left Jujutsu High, per Chapter 30? | `routed qa` / `-` | a personal banker |
| **yes** | fact | Why did Nanami initially quit Jujutsu High, per Chapter 30? | `routed qa` / `-` | the notion of accepting your comrade's sacrifice was moronic |
| **yes** | fact | What does Nanami decide to do for the bakery girl, per Chapter 30? | `routed qa` / `-` | exorcise the curse bothering the girl |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

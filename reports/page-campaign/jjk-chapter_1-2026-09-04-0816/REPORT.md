# Page campaign jjk/chapter_1 — 2026-09-04-0816

Batch `_jjk_page_chapter_1.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T07:31:43+00:00), 73.6s wall clock.

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
| **yes** | fact | What is Megumi Fushiguro sent to find at Sugisawa Municipal High School, per Chapter 1? | `routed qa` / `-` | a powerful cursed object |
| **yes** | fact | What does the student council president threaten to do to the Occult Research club, per Chapter 1? | `routed qa` / `-` | close down the club and re-assign the space to the girl's track team |
| **yes** | fact | What game does the track coach challenge Yuji to, staking his club membership on the result, per Chapter 1? | `routed qa` / `-` | shot put |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

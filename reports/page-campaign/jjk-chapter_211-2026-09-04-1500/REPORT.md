# Page campaign jjk/chapter_211 — 2026-09-04-1500

Batch `_jjk_page_chapter_211.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 4.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/4** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 3/4 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | fact | What do all the group's collective points get transferred to, per Chapter 211? | Megumi | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Chapter_211</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What does Maki deliver to her allies, per Chapter 211? | `routed qa` / `-` | the bad news about Tengen and Tsukumo |
| **yes** | fact | What happens as the Culling Game colonies activate one after the other, per Chapter 211? | `routed qa` / `-` | the pre-prep for the merger concludes |
| no | fact | What do all the group's collective points get transferred to, per Chapter 211? | `routed roster` / `exact` | answer absent |
| **yes** | fact | Who is the man from the second page, per the Chapter 211 Trivia? | `routed qa` / `-` | the waiter who quit his job in Chapter 12 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

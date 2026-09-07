# Page campaign jjk/chapter_114 — 2026-09-04-1445

Batch `_jjk_page_chapter_114.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 4.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **2/3** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 2/3 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | fact | Who are the two curse users the Kusakabe Team is interrupted by, per Chapter 114? | Manami Suda and Toshihisa Negi | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Chapter_114</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What takes precedence over all the chaos, per Chapter 114? | `routed qa` / `-` | a grand battle between two special grades |
| no | fact | Who are the two curse users the Kusakabe Team is interrupted by, per Chapter 114? | `routed roster` / `exact` | answer absent |
| **yes** | fact | By what time is the Kusakabe Team in front of Shibuya Stream, per Chapter 114? | `routed qa` / `-` | 11:01 P.M. |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/chapter_209 — 2026-09-04-1500

Batch `_jjk_page_chapter_209.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.8s wall clock.

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
| `exact` | fact | What do each and every soldier ignore, per Chapter 209? | Kogane | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Chapter_209</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | Whom do foreign armed forces believe they are in Japan to capture, per Chapter 209? | `routed qa` / `-` | jujutsu sorcerers |
| no | fact | What do each and every soldier ignore, per Chapter 209? | `routed roster` / `exact` | answer absent |
| **yes** | fact | What was Kenjaku's proposal to use sorcerers for research, per Chapter 209? | `routed qa` / `-` | a ploy |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

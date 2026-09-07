# Page campaign jjk/chapter_195 — 2026-09-04-1457

Batch `_jjk_page_chapter_195.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 4.5s wall clock.

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
| `exact` | fact | Who are the two newcomers that jump into the fray, per Chapter 195? | a swordsman with no katana and a sumo enthusiast with no one to wrestle | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Chapter_195</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | fact | Who are the two newcomers that jump into the fray, per Chapter 195? | `routed roster` / `exact` | answer absent |
| **yes** | fact | What is Hagane Daido yelling as he runs around, per Chapter 195? | `routed qa` / `-` | katana!!! |
| **yes** | fact | What does Miyo's simple domain create behind Maki, per Chapter 195? | `routed qa` / `-` | a sumo wrestling ring |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/chapter_55 — 2026-09-04-1436

Batch `_jjk_page_chapter_55.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 4.9s wall clock.

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
| **yes** | fact | What do Jujutsu High's first-years investigate after the Goodwill Event, per Chapter 55? | `routed qa` / `-` | the mysterious deaths connected to Megumi's old junior high school |
| **yes** | fact | How many years had passed since the junior-high victims graduated when the first-years investigate, per Chapter 55? | `routed roster` / `exact` | twenty years |
| **yes** | fact | What is Yasohachi Bridge known for, per Chapter 55? | `routed qa` / `-` | a place known for suicides |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/chapter_6 — 2026-09-04-1430

Batch `_jjk_page_chapter_6.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.4s wall clock.

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
| **yes** | fact | What has the fearsome womb already given birth to, per Chapter 6? | `routed qa` / `-` | a special grade cursed spirit |
| **yes** | fact | Where in West Tokyo City has the cursed womb appeared, per Chapter 6? | `routed qa` / `-` | the Eishu Juvenile Detention Center |
| **yes** | fact | What does Megumi summon to track the scent of any survivors, per Chapter 6? | `routed qa` / `-` | one of his Divine Dogs |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/chapter_19 — 2026-09-04-0830

Batch `_jjk_page_chapter_19.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T08:23:53+00:00), 3.6s wall clock.

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
| **yes** | fact | Where are three deformed corpses found, per Chapter 19? | `routed qa` / `-` | Kinema Cinema |
| **yes** | fact | What is the name of the young boy who becomes the only known witness, per Chapter 19? | `routed qa` / `-` | Junpei Yoshino |
| **yes** | fact | What grade of jujutsu sorcerer is Kento Nanami, per Chapter 19? | `routed qa` / `-` | grade 1 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/modulo_chapter_12 — 2026-09-04-1524

Batch `_jjk_page_modulo_chapter_12.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.5s wall clock.

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
| **yes** | fact | What ritual do the representatives of Japan and Simuria rush to halt, per Modulo Chapter 12? | `routed qa` / `-` | the Great Purification Ritual |
| **yes** | fact | Which senior sorcerer enters the building to clear it, per Modulo Chapter 12? | `routed qa` / `-` | Yakumaru |
| **yes** | fact | How long has the village Kalyan been worshipped, per Modulo Chapter 12? | `routed qa` / `-` | two thousand years |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

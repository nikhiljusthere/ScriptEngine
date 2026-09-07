# Page campaign jjk/shinjuku — 2026-09-04-1744

Batch `_jjk_page_shinjuku.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/4** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Shinjuku? | `routed qa` / `-` | a city-level ward that serves as a major commercial and administrative district in Tokyo |
| **yes** | fact | What is Shinjuku considered according to Suguru Geto? | `routed qa` / `-` | the crucible of curses |
| **yes** | fact | Where did the Night Parade of a Hundred Demons take place? | `routed qa` / `-` | in Shinjuku and Kyoto |
| **yes** | fact | What happened to Shinjuku following the Shibuya Incident? | `routed qa` / `-` | Shinjuku was left desolate, off-limits to the public, and home to only cursed spirits |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

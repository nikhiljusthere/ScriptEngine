# Page campaign jjk/tokyo_metropolitan_curse_technical_college — 2026-09-04-1744

Batch `_jjk_page_tokyo_metropolitan_curse_technical_college.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.1s wall clock.

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
| **yes** | fact | What does Tokyo Jujutsu High serve as? | `routed qa` / `-` | a training ground for the next generation of sorcerers but a headquarters for all alumni |
| **yes** | fact | Over how long is the school's curriculum taught? | `routed qa` / `-` | four years |
| **yes** | fact | What is the male school uniform? | `routed qa` / `-` | asymmetrical blue jackets with high collars and two pins on the left side engraved with the school logo |
| **yes** | fact | Where is Tokyo Jujutsu High located? | `routed qa` / `-` | in Tokyo's outskirts, far and high in the mountains |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

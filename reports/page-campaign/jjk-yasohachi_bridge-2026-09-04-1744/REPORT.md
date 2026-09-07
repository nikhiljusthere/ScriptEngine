# Page campaign jjk/yasohachi_bridge — 2026-09-04-1744

Batch `_jjk_page_yasohachi_bridge.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 2.7s wall clock.

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
| **yes** | fact | What is the Yasohachi Bridge? | `routed qa` / `-` | a large stone commercial bridge in the mountains of Koinokuchi Canyon |
| **yes** | fact | What is Yasohachi Bridge known for? | `routed qa` / `-` | a place known for suicides and a famous hotspot for paranormal activity |
| **yes** | fact | What happened to the four students who didn't show up to school? | `routed qa` / `-` | all four of them were found unconscious below Yasohachi Bridge |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

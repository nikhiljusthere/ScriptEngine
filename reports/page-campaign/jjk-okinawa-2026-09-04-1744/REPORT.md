# Page campaign jjk/okinawa — 2026-09-04-1744

Batch `_jjk_page_okinawa.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 3.0s wall clock.

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
| **yes** | fact | What is Okinawa? | `routed qa` / `-` | a coastal prefecture and a vacation spot for tourists |
| **yes** | fact | Why did Riko's escort team go to Okinawa? | `routed qa` / `-` | After Misato Kuroi is abducted by the Time Vessel Association, Riko Amanai's escort team takes a plane to the Naha Airport |
| **yes** | fact | What is Naha Airport? | `routed qa` / `-` | a large airport in Okinawa that the jujutsu students used to travel to the prefecture |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

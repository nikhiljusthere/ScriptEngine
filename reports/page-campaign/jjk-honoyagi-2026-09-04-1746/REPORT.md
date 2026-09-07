# Page campaign jjk/honoyagi — 2026-09-04-1746

Batch `_jjk_page_honoyagi.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 3.3s wall clock.

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
| **yes** | fact | What does Honoyagi resemble? | `routed qa` / `-` | a katana with an ornate, roughly rectangular tsuba (hand guard) |
| **yes** | fact | What does Honoyagi generate when the guard hits against the scabbard? | `routed qa` / `-` | sparks |
| **yes** | fact | Who wields Honoyagi? | `routed qa` / `-` | Tsurugi |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

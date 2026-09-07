# Page campaign jjk/shibuya_tokyo_metro — 2026-09-04-1744

Batch `_jjk_page_shibuya_tokyo_metro.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 3.8s wall clock.

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
| **yes** | fact | How do the citizens of Shibuya generally travel? | `routed qa` / `-` | using the main railway system; the Tokyo Metro |
| **yes** | fact | How many basement floors are subway stations divided into? | `routed qa` / `-` | five basement floors labeled "BF" |
| **yes** | fact | What is the Ginza Line? | `routed qa` / `-` | a subway line adjacent to the Fukutoshin Line, but its route to Shibuya Station is above ground |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

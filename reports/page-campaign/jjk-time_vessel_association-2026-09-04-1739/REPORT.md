# Page campaign jjk/time_vessel_association — 2026-09-04-1739

Batch `_jjk_page_time_vessel_association.json`: 6 questions (0 set, 6 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 6.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/6** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | When did the Time Vessel Association begin? | `routed qa` / `-` | in the Nara period |
| **yes** | fact | What was the Time Vessel Association's public name? | `routed qa` / `-` | the Star Religious Group |
| **yes** | fact | What were followers of the Time Vessel Association called? | `routed qa` / `-` | Children of the Star |
| **yes** | fact | What did the Time Vessel Association offer to pay for the Star Plasma Vessel's assassination? | `routed qa` / `-` | thirty-million yen |
| **yes** | fact | Who did the Time Vessel Association enlist to assassinate the Star Plasma Vessel? | `routed qa` / `-` | the Sorcerer Killer |
| **yes** | fact | What is the primary headquarters for the Star Religious Group? | `routed qa` / `-` | the House of the Children of the Star |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

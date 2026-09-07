# Page campaign jjk/prison_realm — 2026-09-04-1746

Batch `_jjk_page_prison_realm.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.4s wall clock.

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
| **yes** | fact | What is Prison Realm? | `routed qa` / `-` | the final remains of the Buddhist Monk Genshin |
| **yes** | fact | How is the Prison Realm curse activated? | `routed qa` / `-` | the curse is activated with the incantation "gate open" |
| **yes** | fact | What must be met for Prison Realm to activate? | `routed qa` / `-` | they must be kept within a four-meter radius for a minute's worth of time within their mind |
| **yes** | fact | What is the limit on occupants in Prison Realm? | `routed qa` / `-` | Only one occupant can be contained at a time |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

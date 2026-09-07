# Page campaign jjk/cursed_object — 2026-09-04-1742

Batch `_jjk_page_cursed_object.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.5s wall clock.

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
| **yes** | fact | What is a cursed object? | `routed qa` / `-` | items that contain cursed energy are referred to as cursed objects |
| **yes** | fact | How are particularly dangerous cursed objects ranked? | `routed qa` / `-` | special grade |
| **yes** | fact | What is incarnation? | `routed qa` / `-` | a phenomenon where an ancient "curse" (a cursed object) obtains a physical body |
| **yes** | fact | Which special grade cursed object is the remains of the Buddhist monk Genshin? | `routed qa` / `-` | Prison Realm |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

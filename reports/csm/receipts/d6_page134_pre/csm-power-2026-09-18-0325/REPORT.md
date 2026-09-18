# Page campaign csm/power — 2026-09-18-0325

Batch `_csm_page_power.json`: 16 questions (9 set, 7 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 9.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **16/16** |
| set questions exact | 9/9 (100.0%) |
| canon items recovered | 61/61 (100.0%) |
| fact answers present | 7/7 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Power? | `Every named technique of Power` / `declared` | 16 found, 0 missing; returned 16 |
| **yes** | set | What are all the allies of Power? | `Every ally of Power` / `declared` | 11 found, 0 missing; returned 11 |
| **yes** | set | What are all the enemies of Power? | `Every enemy of Power` / `declared` | 9 found, 0 missing; returned 9 |
| **yes** | set | What are all the friends of Power? | `Every friend of Power` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the mentors of Power? | `Every mentor of Power` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the subordinates of Power? | `Every subordinate of Power` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the superiors of Power? | `Every superior of Power` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the affiliations of Power? | `Power's affiliations` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the aliases of Power? | `Power's aliases` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | fact | What are the kanji for Power's name? | `routed qa` / `-` | パワー |
| **yes** | fact | What is the romaji of Power's name? | `routed qa` / `-` | Pawā |
| **yes** | fact | What is Power's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Power's height? | `routed qa` / `-` | 170 cm (5'7") |
| **yes** | fact | What is the status of Power? | `routed qa` / `-` | Deceased (original timeline) Alive (new timeline) |
| **yes** | fact | What is Power's occupation? | `routed qa` / `-` | Public Safety Devil Hunter Contract Devil |
| **yes** | fact | How old is Power? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

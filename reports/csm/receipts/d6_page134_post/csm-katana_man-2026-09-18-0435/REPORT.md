# Page campaign csm/katana_man — 2026-09-18-0435

Batch `_csm_page_katana_man.json`: 12 questions (8 set, 4 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 6.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **12/12** |
| set questions exact | 8/8 (100.0%) |
| canon items recovered | 44/44 (100.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Katana Man? | `Every named technique of Katana Man` / `declared` | 9 found, 0 missing; returned 9 |
| **yes** | set | What are all the allies of Katana Man? | `Every ally of Katana Man` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the enemies of Katana Man? | `Every enemy of Katana Man` / `declared` | 9 found, 0 missing; returned 9 |
| **yes** | set | What are all the rivals of Katana Man? | `Every rival of Katana Man` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the subordinates of Katana Man? | `Every subordinate of Katana Man` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the superiors of Katana Man? | `Every superior of Katana Man` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the affiliations of Katana Man? | `Katana Man's affiliations` / `declared` | 8 found, 0 missing; returned 8 |
| **yes** | set | What are all the aliases of Katana Man? | `Katana Man's aliases` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | fact | What is Katana Man's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Katana Man's height? | `routed qa` / `-` | 195 cm (6'5") |
| **yes** | fact | What is the status of Katana Man? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Katana Man's occupation? | `routed qa` / `-` | Yakuza (formerly) Private Devil Hunter (formerly) Public Safety Devil Hunter (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

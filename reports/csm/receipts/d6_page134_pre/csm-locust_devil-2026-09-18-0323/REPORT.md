# Page campaign csm/locust_devil — 2026-09-18-0323

Batch `_csm_page_locust_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 4.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 5/5 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Locust Devil? | `Every named technique of Locust Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the enemies of Locust Devil? | `Every enemy of Locust Devil` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Locust Devil's name? | `routed qa` / `-` | バッタの悪魔 |
| **yes** | fact | What is the romaji of Locust Devil's name? | `routed qa` / `-` | Batta no Akuma |
| **yes** | fact | What is the status of Locust Devil? | `routed qa` / `-` | Erased (original timeline) Unknown (new timeline) |
| **yes** | fact | What is Locust Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Locust Devil's occupation? | `routed qa` / `-` | Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

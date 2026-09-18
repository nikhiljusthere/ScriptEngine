# Page campaign csm/barem_bridge — 2026-09-18-0430

Batch `_csm_page_barem_bridge.json`: 11 questions (6 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 6.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/11** |
| set questions exact | 6/6 (100.0%) |
| canon items recovered | 29/29 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Barem Bridge? | `Every named technique of Barem Bridge` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the allies of Barem Bridge? | `Every ally of Barem Bridge` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the enemies of Barem Bridge? | `Every enemy of Barem Bridge` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the subordinates of Barem Bridge? | `Every subordinate of Barem Bridge` / `declared` | 5 found, 0 missing; returned 5 |
| **yes** | set | What are all the superiors of Barem Bridge? | `Every superior of Barem Bridge` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the affiliations of Barem Bridge? | `Barem Bridge's affiliations` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | fact | What are the kanji for Barem Bridge's name? | `routed qa` / `-` | バルエム・ブリッチ |
| **yes** | fact | What is the romaji of Barem Bridge's name? | `routed qa` / `-` | Baruemu Buritchi |
| **yes** | fact | What is the status of Barem Bridge? | `routed qa` / `-` | Erased (original timeline) |
| **yes** | fact | What is Barem Bridge's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (brainwashed) Chainsaw Man Church Contractor |
| **yes** | fact | What is Barem Bridge's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

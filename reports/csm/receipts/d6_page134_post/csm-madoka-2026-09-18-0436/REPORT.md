# Page campaign csm/madoka — 2026-09-18-0436

Batch `_csm_page_madoka.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-18T04:25:03+00:00), 4.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/6** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 2/2 (100.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the affiliations of Madoka? | `Madoka's affiliations` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | fact | What are the kanji for Madoka's name? | `routed qa` / `-` | 円 |
| **yes** | fact | What is the romaji of Madoka's name? | `routed qa` / `-` | Madoka |
| **yes** | fact | What is Madoka's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Madoka? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Madoka's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/chapter_66 — 2026-09-17-0833

Batch `_csm_page_chapter_66.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/11** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 11/11 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Chapter 66's title? | `routed qa` / `-` | Woof! |
| **yes** | fact | In which volume does Chapter 66 appear? | `routed qa` / `-` | 8 |
| **yes** | fact | In which chapter does Chapter 66 appear? | `routed qa` / `-` | 66 |
| **yes** | fact | What is the Japanese title of Chapter 66? | `routed qa` / `-` | ワン！ |
| **yes** | fact | What is the romaji title of Chapter 66? | `routed qa` / `-` | Wan! |
| **yes** | fact | On which page does Chapter 66 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 66? | `routed qa` / `-` | April 13, 2020 |
| **yes** | fact | What issue is Chapter 66 from? | `routed qa` / `-` | Issue 2020-20 |
| **yes** | fact | In which arc does Chapter 66 appear? | `routed qa` / `-` | International Assassins arc |
| **yes** | fact | What comes before Chapter 66? | `routed qa` / `-` | Chapter 65 |
| **yes** | fact | What comes after Chapter 66? | `routed qa` / `-` | Chapter 67 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

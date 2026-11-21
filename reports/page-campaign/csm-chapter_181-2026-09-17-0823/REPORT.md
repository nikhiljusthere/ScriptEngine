# Page campaign csm/chapter_181 — 2026-09-17-0823

Batch `_csm_page_chapter_181.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **10/10** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 10/10 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Chapter 181's title? | `routed qa` / `-` | Trees on the Mind |
| **yes** | fact | In which volume does Chapter 181 appear? | `routed qa` / `-` | 20 |
| **yes** | fact | In which chapter does Chapter 181 appear? | `routed qa` / `-` | 181 |
| **yes** | fact | What is the Japanese title of Chapter 181? | `routed qa` / `-` | 気になる木 |
| **yes** | fact | What is the romaji title of Chapter 181? | `routed qa` / `-` | Ki ni naru Ki |
| **yes** | fact | On which page does Chapter 181 appear? | `routed qa` / `-` | 17 |
| **yes** | fact | What date is associated with Chapter 181? | `routed qa` / `-` | October 23, 2024 |
| **yes** | fact | In which arc does Chapter 181 appear? | `routed qa` / `-` | Aging Devil arc |
| **yes** | fact | What comes before Chapter 181? | `routed qa` / `-` | Chapter 180 |
| **yes** | fact | What comes after Chapter 181? | `routed qa` / `-` | Chapter 182 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

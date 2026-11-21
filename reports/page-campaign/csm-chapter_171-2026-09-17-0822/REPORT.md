# Page campaign csm/chapter_171 — 2026-09-17-0822

Batch `_csm_page_chapter_171.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.9s wall clock.

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
| **yes** | fact | What is Chapter 171's title? | `routed qa` / `-` | Special Division 5 |
| **yes** | fact | In which volume does Chapter 171 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | In which chapter does Chapter 171 appear? | `routed qa` / `-` | 171 |
| **yes** | fact | What is the Japanese title of Chapter 171? | `routed qa` / `-` | 特異5課 |
| **yes** | fact | What is the romaji title of Chapter 171? | `routed qa` / `-` | Tokui 5-ka |
| **yes** | fact | On which page does Chapter 171 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | What date is associated with Chapter 171? | `routed qa` / `-` | July 17, 2024 |
| **yes** | fact | In which arc does Chapter 171 appear? | `routed qa` / `-` | Aging Devil arc |
| **yes** | fact | What comes before Chapter 171? | `routed qa` / `-` | Chapter 170 |
| **yes** | fact | What comes after Chapter 171? | `routed qa` / `-` | Chapter 172 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

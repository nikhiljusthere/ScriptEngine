# Page campaign csm/chapter_140 — 2026-09-17-0818

Batch `_csm_page_chapter_140.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.2s wall clock.

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
| **yes** | fact | What is Chapter 140's title? | `routed qa` / `-` | Scales |
| **yes** | fact | In which volume does Chapter 140 appear? | `routed qa` / `-` | 16 |
| **yes** | fact | In which chapter does Chapter 140 appear? | `routed qa` / `-` | 140 |
| **yes** | fact | What is the Japanese title of Chapter 140? | `routed qa` / `-` | 天秤 |
| **yes** | fact | What is the romaji title of Chapter 140? | `routed qa` / `-` | Tenbin |
| **yes** | fact | On which page does Chapter 140 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 140? | `routed qa` / `-` | August 23, 2023 |
| **yes** | fact | In which arc does Chapter 140 appear? | `routed qa` / `-` | Chainsaw Man Church arc |
| **yes** | fact | What comes before Chapter 140? | `routed qa` / `-` | Chapter 139 |
| **yes** | fact | What comes after Chapter 140? | `routed qa` / `-` | Chapter 141 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

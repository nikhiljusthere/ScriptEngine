# Page campaign csm/chapter_135 — 2026-09-17-0818

Batch `_csm_page_chapter_135.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.5s wall clock.

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
| **yes** | fact | What is Chapter 135's title? | `routed qa` / `-` | Sentimental Drive |
| **yes** | fact | In which volume does Chapter 135 appear? | `routed qa` / `-` | 16 |
| **yes** | fact | In which chapter does Chapter 135 appear? | `routed qa` / `-` | 135 |
| **yes** | fact | What is the Japanese title of Chapter 135? | `routed qa` / `-` | センチメンタルドライブ |
| **yes** | fact | What is the romaji title of Chapter 135? | `routed qa` / `-` | Senchimentaru Doraibu |
| **yes** | fact | On which page does Chapter 135 appear? | `routed qa` / `-` | 22 |
| **yes** | fact | What date is associated with Chapter 135? | `routed qa` / `-` | July 12, 2023 |
| **yes** | fact | In which arc does Chapter 135 appear? | `routed qa` / `-` | Chainsaw Man Church arc |
| **yes** | fact | What comes before Chapter 135? | `routed qa` / `-` | Chapter 134 |
| **yes** | fact | What comes after Chapter 135? | `routed qa` / `-` | Chapter 136 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

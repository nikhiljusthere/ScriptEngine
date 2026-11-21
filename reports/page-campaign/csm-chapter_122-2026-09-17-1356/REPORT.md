# Page campaign csm/chapter_122 — 2026-09-17-1356

Batch `_csm_page_chapter_122.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 12.1s wall clock.

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
| **yes** | fact | What is Chapter 122's title? | `routed qa` / `-` | The Prophecies |
| **yes** | fact | In which volume does Chapter 122 appear? | `routed qa` / `-` | 14 |
| **yes** | fact | In which chapter does Chapter 122 appear? | `routed qa` / `-` | 122 |
| **yes** | fact | What is the Japanese title of Chapter 122? | `routed qa` / `-` | 大予言 |
| **yes** | fact | What is the romaji title of Chapter 122? | `routed qa` / `-` | Dai Yogen |
| **yes** | fact | On which page does Chapter 122 appear? | `routed qa` / `-` | 18 |
| **yes** | fact | What date is associated with Chapter 122? | `routed qa` / `-` | March 8, 2023 |
| **yes** | fact | In which arc does Chapter 122 appear? | `routed qa` / `-` | Falling Devil arc |
| **yes** | fact | What comes before Chapter 122? | `routed qa` / `-` | Chapter 121 |
| **yes** | fact | What comes after Chapter 122? | `routed qa` / `-` | Chapter 123 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

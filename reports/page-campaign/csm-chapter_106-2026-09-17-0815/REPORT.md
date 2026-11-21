# Page campaign csm/chapter_106 — 2026-09-17-0815

Batch `_csm_page_chapter_106.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.0s wall clock.

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
| **yes** | fact | What is Chapter 106's title? | `routed qa` / `-` | Bonfire |
| **yes** | fact | In which volume does Chapter 106 appear? | `routed qa` / `-` | 13 |
| **yes** | fact | In which chapter does Chapter 106 appear? | `routed qa` / `-` | 106 |
| **yes** | fact | What is the Japanese title of Chapter 106? | `routed qa` / `-` | 焚火 |
| **yes** | fact | What is the romaji title of Chapter 106? | `routed qa` / `-` | Takibi |
| **yes** | fact | On which page does Chapter 106 appear? | `routed qa` / `-` | 17 |
| **yes** | fact | What date is associated with Chapter 106? | `routed qa` / `-` | October 12, 2022 |
| **yes** | fact | In which arc does Chapter 106 appear? | `routed qa` / `-` | Justice Devil arc |
| **yes** | fact | What comes before Chapter 106? | `routed qa` / `-` | Chapter 105 |
| **yes** | fact | What comes after Chapter 106? | `routed qa` / `-` | Chapter 107 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

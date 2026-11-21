# Page campaign csm/chapter_179 — 2026-09-17-0822

Batch `_csm_page_chapter_179.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.2s wall clock.

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
| **yes** | fact | What is Chapter 179's title? | `routed qa` / `-` | Vamvagah |
| **yes** | fact | In which volume does Chapter 179 appear? | `routed qa` / `-` | 20 |
| **yes** | fact | In which chapter does Chapter 179 appear? | `routed qa` / `-` | 179 |
| **yes** | fact | What is the Japanese title of Chapter 179? | `routed qa` / `-` | ヴァンヴァガ |
| **yes** | fact | What is the romaji title of Chapter 179? | `routed qa` / `-` | Van'vaga |
| **yes** | fact | On which page does Chapter 179 appear? | `routed qa` / `-` | 17 |
| **yes** | fact | What date is associated with Chapter 179? | `routed qa` / `-` | October 2, 2024 |
| **yes** | fact | In which arc does Chapter 179 appear? | `routed qa` / `-` | Aging Devil arc |
| **yes** | fact | What comes before Chapter 179? | `routed qa` / `-` | Chapter 178 |
| **yes** | fact | What comes after Chapter 179? | `routed qa` / `-` | Chapter 180 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

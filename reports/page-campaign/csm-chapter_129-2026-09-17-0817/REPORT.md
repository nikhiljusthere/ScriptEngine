# Page campaign csm/chapter_129 — 2026-09-17-0817

Batch `_csm_page_chapter_129.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.7s wall clock.

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
| **yes** | fact | What is Chapter 129's title? | `routed qa` / `-` | Save Me, Chainsaw Man |
| **yes** | fact | In which volume does Chapter 129 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | In which chapter does Chapter 129 appear? | `routed qa` / `-` | 129 |
| **yes** | fact | What is the Japanese title of Chapter 129? | `routed qa` / `-` | 助けてチェンソーマン |
| **yes** | fact | What is the romaji title of Chapter 129? | `routed qa` / `-` | Tasukete Chensōman |
| **yes** | fact | On which page does Chapter 129 appear? | `routed qa` / `-` | 18 |
| **yes** | fact | What date is associated with Chapter 129? | `routed qa` / `-` | May 10, 2023 |
| **yes** | fact | In which arc does Chapter 129 appear? | `routed qa` / `-` | Falling Devil arc |
| **yes** | fact | What comes before Chapter 129? | `routed qa` / `-` | Chapter 128 |
| **yes** | fact | What comes after Chapter 129? | `routed qa` / `-` | Chapter 130 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

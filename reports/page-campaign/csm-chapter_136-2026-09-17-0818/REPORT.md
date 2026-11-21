# Page campaign csm/chapter_136 — 2026-09-17-0818

Batch `_csm_page_chapter_136.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.8s wall clock.

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
| **yes** | fact | What is Chapter 136's title? | `routed qa` / `-` | Normal Life |
| **yes** | fact | In which volume does Chapter 136 appear? | `routed qa` / `-` | 16 |
| **yes** | fact | In which chapter does Chapter 136 appear? | `routed qa` / `-` | 136 |
| **yes** | fact | What is the Japanese title of Chapter 136? | `routed qa` / `-` | 普通の日々 |
| **yes** | fact | What is the romaji title of Chapter 136? | `routed qa` / `-` | Futsū no Hibi |
| **yes** | fact | On which page does Chapter 136 appear? | `routed qa` / `-` | 14 |
| **yes** | fact | What date is associated with Chapter 136? | `routed qa` / `-` | July 19, 2023 |
| **yes** | fact | In which arc does Chapter 136 appear? | `routed qa` / `-` | Chainsaw Man Church arc |
| **yes** | fact | What comes before Chapter 136? | `routed qa` / `-` | Chapter 135 |
| **yes** | fact | What comes after Chapter 136? | `routed qa` / `-` | Chapter 137 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

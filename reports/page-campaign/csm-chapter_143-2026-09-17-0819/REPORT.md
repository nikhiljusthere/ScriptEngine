# Page campaign csm/chapter_143 — 2026-09-17-0819

Batch `_csm_page_chapter_143.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.4s wall clock.

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
| **yes** | fact | What is Chapter 143's title? | `routed qa` / `-` | Rawr |
| **yes** | fact | In which volume does Chapter 143 appear? | `routed qa` / `-` | 16 |
| **yes** | fact | In which chapter does Chapter 143 appear? | `routed qa` / `-` | 143 |
| **yes** | fact | What is the Japanese title of Chapter 143? | `routed qa` / `-` | がおー |
| **yes** | fact | What is the romaji title of Chapter 143? | `routed qa` / `-` | Gaō |
| **yes** | fact | On which page does Chapter 143 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | What date is associated with Chapter 143? | `routed qa` / `-` | September 20, 2023 |
| **yes** | fact | In which arc does Chapter 143 appear? | `routed qa` / `-` | Chainsaw Man Church arc |
| **yes** | fact | What comes before Chapter 143? | `routed qa` / `-` | Chapter 142 |
| **yes** | fact | What comes after Chapter 143? | `routed qa` / `-` | Chapter 144 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

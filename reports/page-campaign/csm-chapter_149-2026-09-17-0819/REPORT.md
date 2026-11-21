# Page campaign csm/chapter_149 — 2026-09-17-0819

Batch `_csm_page_chapter_149.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.7s wall clock.

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
| **yes** | fact | What is Chapter 149's title? | `routed qa` / `-` | Devil's Choice |
| **yes** | fact | In which volume does Chapter 149 appear? | `routed qa` / `-` | 17 |
| **yes** | fact | In which chapter does Chapter 149 appear? | `routed qa` / `-` | 149 |
| **yes** | fact | What is the Japanese title of Chapter 149? | `routed qa` / `-` | 悪魔の選択 |
| **yes** | fact | What is the romaji title of Chapter 149? | `routed qa` / `-` | Akuma no Sentaku |
| **yes** | fact | On which page does Chapter 149 appear? | `routed qa` / `-` | 20 |
| **yes** | fact | What date is associated with Chapter 149? | `routed qa` / `-` | November 22, 2023 |
| **yes** | fact | In which arc does Chapter 149 appear? | `routed qa` / `-` | Chainsaw Man Church arc |
| **yes** | fact | What comes before Chapter 149? | `routed qa` / `-` | Chapter 148 |
| **yes** | fact | What comes after Chapter 149? | `routed qa` / `-` | Chapter 150 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

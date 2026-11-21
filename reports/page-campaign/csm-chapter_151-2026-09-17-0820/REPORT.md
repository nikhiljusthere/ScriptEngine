# Page campaign csm/chapter_151 — 2026-09-17-0820

Batch `_csm_page_chapter_151.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.3s wall clock.

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
| **yes** | fact | What is Chapter 151's title? | `routed qa` / `-` | The Return of Chainsaw Man |
| **yes** | fact | In which volume does Chapter 151 appear? | `routed qa` / `-` | 17 |
| **yes** | fact | In which chapter does Chapter 151 appear? | `routed qa` / `-` | 151 |
| **yes** | fact | What is the Japanese title of Chapter 151? | `routed qa` / `-` | 帰ってきたチェンソーマン |
| **yes** | fact | What is the romaji title of Chapter 151? | `routed qa` / `-` | Kaettekita Chensōman |
| **yes** | fact | On which page does Chapter 151 appear? | `routed qa` / `-` | 16 |
| **yes** | fact | What date is associated with Chapter 151? | `routed qa` / `-` | December 20, 2023 |
| **yes** | fact | In which arc does Chapter 151 appear? | `routed qa` / `-` | Chainsaw Man Church arc |
| **yes** | fact | What comes before Chapter 151? | `routed qa` / `-` | Chapter 150 |
| **yes** | fact | What comes after Chapter 151? | `routed qa` / `-` | Chapter 152 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/chapter_127 — 2026-09-17-1357

Batch `_csm_page_chapter_127.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 11.6s wall clock.

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
| **yes** | fact | What is Chapter 127's title? | `routed qa` / `-` | Save the Asa |
| **yes** | fact | In which volume does Chapter 127 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | In which chapter does Chapter 127 appear? | `routed qa` / `-` | 127 |
| **yes** | fact | What is the Japanese title of Chapter 127? | `routed qa` / `-` | セーブザアサ |
| **yes** | fact | What is the romaji title of Chapter 127? | `routed qa` / `-` | Sēbu za Asa |
| **yes** | fact | On which page does Chapter 127 appear? | `routed qa` / `-` | 16 |
| **yes** | fact | What date is associated with Chapter 127? | `routed qa` / `-` | April 19, 2023 |
| **yes** | fact | In which arc does Chapter 127 appear? | `routed qa` / `-` | Falling Devil arc |
| **yes** | fact | What comes before Chapter 127? | `routed qa` / `-` | Chapter 126 |
| **yes** | fact | What comes after Chapter 127? | `routed qa` / `-` | Chapter 128 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

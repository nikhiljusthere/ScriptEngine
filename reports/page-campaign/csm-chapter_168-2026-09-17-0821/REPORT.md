# Page campaign csm/chapter_168 — 2026-09-17-0821

Batch `_csm_page_chapter_168.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.3s wall clock.

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
| **yes** | fact | What is Chapter 168's title? | `routed qa` / `-` | Kiss, Love, Sperm |
| **yes** | fact | In which volume does Chapter 168 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | In which chapter does Chapter 168 appear? | `routed qa` / `-` | 168 |
| **yes** | fact | What is the Japanese title of Chapter 168? | `routed qa` / `-` | キス・好き・スペルマ |
| **yes** | fact | What is the romaji title of Chapter 168? | `routed qa` / `-` | Kisu, Suki, Superuma |
| **yes** | fact | On which page does Chapter 168 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | What date is associated with Chapter 168? | `routed qa` / `-` | June 12, 2024 |
| **yes** | fact | In which arc does Chapter 168 appear? | `routed qa` / `-` | Aging Devil arc |
| **yes** | fact | What comes before Chapter 168? | `routed qa` / `-` | Chapter 167 |
| **yes** | fact | What comes after Chapter 168? | `routed qa` / `-` | Chapter 169 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

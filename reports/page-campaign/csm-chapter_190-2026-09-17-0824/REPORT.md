# Page campaign csm/chapter_190 — 2026-09-17-0824

Batch `_csm_page_chapter_190.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.3s wall clock.

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
| **yes** | fact | What is Chapter 190's title? | `routed qa` / `-` | To Their Respective Worlds |
| **yes** | fact | In which volume does Chapter 190 appear? | `routed qa` / `-` | 21 |
| **yes** | fact | In which chapter does Chapter 190 appear? | `routed qa` / `-` | 190 |
| **yes** | fact | What is the Japanese title of Chapter 190? | `routed qa` / `-` | 元の世界へ |
| **yes** | fact | What is the romaji title of Chapter 190? | `routed qa` / `-` | Moto no Sekai e |
| **yes** | fact | On which page does Chapter 190 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | What date is associated with Chapter 190? | `routed qa` / `-` | January 15, 2025 |
| **yes** | fact | In which arc does Chapter 190 appear? | `routed qa` / `-` | Aging Devil arc |
| **yes** | fact | What comes before Chapter 190? | `routed qa` / `-` | Chapter 189 |
| **yes** | fact | What comes after Chapter 190? | `routed qa` / `-` | Chapter 191 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/chapter_215 — 2026-09-17-0826

Batch `_csm_page_chapter_215.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.9s wall clock.

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
| **yes** | fact | What is Chapter 215's title? | `routed qa` / `-` | Declaration of War |
| **yes** | fact | In which volume does Chapter 215 appear? | `routed qa` / `-` | 23 |
| **yes** | fact | In which chapter does Chapter 215 appear? | `routed qa` / `-` | 215 |
| **yes** | fact | What is the Japanese title of Chapter 215? | `routed qa` / `-` | 宣戦布告 |
| **yes** | fact | What is the romaji title of Chapter 215? | `routed qa` / `-` | Sensen Fukoku |
| **yes** | fact | On which page does Chapter 215 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | What date is associated with Chapter 215? | `routed qa` / `-` | September 24, 2025 |
| **yes** | fact | In which arc does Chapter 215 appear? | `routed qa` / `-` | War Devil arc |
| **yes** | fact | What comes before Chapter 215? | `routed qa` / `-` | Chapter 214 |
| **yes** | fact | What comes after Chapter 215? | `routed qa` / `-` | Chapter 216 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

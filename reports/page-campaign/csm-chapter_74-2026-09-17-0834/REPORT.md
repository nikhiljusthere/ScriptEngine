# Page campaign csm/chapter_74 — 2026-09-17-0834

Batch `_csm_page_chapter_74.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **11/11** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 11/11 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Chapter 74's title? | `routed qa` / `-` | What the Waves Say |
| **yes** | fact | In which volume does Chapter 74 appear? | `routed qa` / `-` | 9 |
| **yes** | fact | In which chapter does Chapter 74 appear? | `routed qa` / `-` | 74 |
| **yes** | fact | What is the Japanese title of Chapter 74? | `routed qa` / `-` | 波の言う事 |
| **yes** | fact | What is the romaji title of Chapter 74? | `routed qa` / `-` | Nami no Iukoto |
| **yes** | fact | On which page does Chapter 74 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 74? | `routed qa` / `-` | June 22, 2020 |
| **yes** | fact | What issue is Chapter 74 from? | `routed qa` / `-` | Issue 2020-29 |
| **yes** | fact | In which arc does Chapter 74 appear? | `routed qa` / `-` | Gun Devil arc |
| **yes** | fact | What comes before Chapter 74? | `routed qa` / `-` | Chapter 73 |
| **yes** | fact | What comes after Chapter 74? | `routed qa` / `-` | Chapter 75 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

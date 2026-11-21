# Page campaign csm/chapter_162 — 2026-09-17-0821

Batch `_csm_page_chapter_162.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.2s wall clock.

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
| **yes** | fact | What is Chapter 162's title? | `routed qa` / `-` | Fearsome |
| **yes** | fact | In which volume does Chapter 162 appear? | `routed qa` / `-` | 18 |
| **yes** | fact | In which chapter does Chapter 162 appear? | `routed qa` / `-` | 162 |
| **yes** | fact | What is the Japanese title of Chapter 162? | `routed qa` / `-` | 恐ろしい奴 |
| **yes** | fact | What is the romaji title of Chapter 162? | `routed qa` / `-` | Osoroshī Yatsu |
| **yes** | fact | On which page does Chapter 162 appear? | `routed qa` / `-` | 17 |
| **yes** | fact | What date is associated with Chapter 162? | `routed qa` / `-` | April 10, 2024 |
| **yes** | fact | In which arc does Chapter 162 appear? | `routed qa` / `-` | Aging Devil arc |
| **yes** | fact | What comes before Chapter 162? | `routed qa` / `-` | Chapter 161 |
| **yes** | fact | What comes after Chapter 162? | `routed qa` / `-` | Chapter 163 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/chapter_99 — 2026-09-17-0836

Batch `_csm_page_chapter_99.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.7s wall clock.

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
| **yes** | fact | What is Chapter 99's title? | `routed qa` / `-` | Two Birds |
| **yes** | fact | In which volume does Chapter 99 appear? | `routed qa` / `-` | 12 |
| **yes** | fact | In which chapter does Chapter 99 appear? | `routed qa` / `-` | 99 |
| **yes** | fact | What is the Japanese title of Chapter 99? | `routed qa` / `-` | ２羽 |
| **yes** | fact | What is the romaji title of Chapter 99? | `routed qa` / `-` | Ni wa |
| **yes** | fact | On which page does Chapter 99 appear? | `routed qa` / `-` | 24 |
| **yes** | fact | What date is associated with Chapter 99? | `routed qa` / `-` | July 20, 2022 |
| **yes** | fact | In which arc does Chapter 99 appear? | `routed qa` / `-` | Justice Devil arc |
| **yes** | fact | What comes before Chapter 99? | `routed qa` / `-` | Chapter 98 |
| **yes** | fact | What comes after Chapter 99? | `routed qa` / `-` | Chapter 100 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/chapter_229 — 2026-09-17-0828

Batch `_csm_page_chapter_229.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.5s wall clock.

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
| **yes** | fact | What is Chapter 229's title? | `routed qa` / `-` | Nightjar and Asa |
| **yes** | fact | In which volume does Chapter 229 appear? | `routed qa` / `-` | 24 |
| **yes** | fact | In which chapter does Chapter 229 appear? | `routed qa` / `-` | 229 |
| **yes** | fact | What is the Japanese title of Chapter 229? | `routed qa` / `-` | ヨタカとアサ |
| **yes** | fact | What is the romaji title of Chapter 229? | `routed qa` / `-` | Yotaka to Asa |
| **yes** | fact | On which page does Chapter 229 appear? | `routed qa` / `-` | 15 |
| **yes** | fact | What date is associated with Chapter 229? | `routed qa` / `-` | February 18, 2026 |
| **yes** | fact | In which arc does Chapter 229 appear? | `routed qa` / `-` | War Devil arc |
| **yes** | fact | What comes before Chapter 229? | `routed qa` / `-` | Chapter 228 |
| **yes** | fact | What comes after Chapter 229? | `routed qa` / `-` | Chapter 230 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

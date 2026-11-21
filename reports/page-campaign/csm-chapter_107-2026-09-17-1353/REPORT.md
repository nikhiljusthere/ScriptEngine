# Page campaign csm/chapter_107 — 2026-09-17-1353

Batch `_csm_page_chapter_107.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 11.5s wall clock.

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
| **yes** | fact | What is Chapter 107's title? | `routed qa` / `-` | School Attacker |
| **yes** | fact | In which volume does Chapter 107 appear? | `routed qa` / `-` | 13 |
| **yes** | fact | In which chapter does Chapter 107 appear? | `routed qa` / `-` | 107 |
| **yes** | fact | What is the Japanese title of Chapter 107? | `routed qa` / `-` | 学校の襲撃者 |
| **yes** | fact | What is the romaji title of Chapter 107? | `routed qa` / `-` | Gakkō no Shūgeki-sha |
| **yes** | fact | On which page does Chapter 107 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 107? | `routed qa` / `-` | October 19, 2022 |
| **yes** | fact | In which arc does Chapter 107 appear? | `routed qa` / `-` | Justice Devil arc |
| **yes** | fact | What comes before Chapter 107? | `routed qa` / `-` | Chapter 106 |
| **yes** | fact | What comes after Chapter 107? | `routed qa` / `-` | Chapter 108 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

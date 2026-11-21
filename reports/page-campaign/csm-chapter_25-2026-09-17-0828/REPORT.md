# Page campaign csm/chapter_25 — 2026-09-17-0828

Batch `_csm_page_chapter_25.json`: 12 questions (0 set, 12 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **12/12** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 12/12 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Chapter 25's title? | `routed qa` / `-` | Ghost, Snake, Chainsaw |
| **yes** | fact | In which volume does Chapter 25 appear? | `routed qa` / `-` | 3 |
| **yes** | fact | In which chapter does Chapter 25 appear? | `routed qa` / `-` | 25 |
| **yes** | fact | What is the Japanese title of Chapter 25? | `routed qa` / `-` | ゴースト・ヘビ・チェンソー |
| **yes** | fact | What is the romaji title of Chapter 25? | `routed qa` / `-` | Gōsuto Hebi Chensō |
| **yes** | fact | On which page does Chapter 25 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 25? | `routed qa` / `-` | June 10, 2019 |
| **yes** | fact | What issue is Chapter 25 from? | `routed qa` / `-` | Issue 2019-28 |
| **yes** | fact | In which episode does Chapter 25 appear? | `routed qa` / `-` | Episode 8 Episode 9 |
| **yes** | fact | In which arc does Chapter 25 appear? | `routed qa` / `-` | Katana Man arc |
| **yes** | fact | What comes before Chapter 25? | `routed qa` / `-` | Chapter 24 |
| **yes** | fact | What comes after Chapter 25? | `routed qa` / `-` | Chapter 26 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

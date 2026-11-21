# Page campaign csm/chapter_104 — 2026-09-17-0815

Batch `_csm_page_chapter_104.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.1s wall clock.

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
| **yes** | fact | What is Chapter 104's title? | `routed qa` / `-` | Spoiler |
| **yes** | fact | In which volume does Chapter 104 appear? | `routed qa` / `-` | 13 |
| **yes** | fact | In which chapter does Chapter 104 appear? | `routed qa` / `-` | 104 |
| **yes** | fact | What is the Japanese title of Chapter 104? | `routed qa` / `-` | ネタバレ |
| **yes** | fact | What is the romaji title of Chapter 104? | `routed qa` / `-` | Netabare |
| **yes** | fact | On which page does Chapter 104 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 104? | `routed qa` / `-` | September 14, 2022 |
| **yes** | fact | In which arc does Chapter 104 appear? | `routed qa` / `-` | Justice Devil arc |
| **yes** | fact | What comes before Chapter 104? | `routed qa` / `-` | Chapter 103 |
| **yes** | fact | What comes after Chapter 104? | `routed qa` / `-` | Chapter 105 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/chapter_61 — 2026-09-17-0832

Batch `_csm_page_chapter_61.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.2s wall clock.

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
| **yes** | fact | What is Chapter 61's title? | `routed qa` / `-` | News Reporter |
| **yes** | fact | In which volume does Chapter 61 appear? | `routed qa` / `-` | 7 |
| **yes** | fact | In which chapter does Chapter 61 appear? | `routed qa` / `-` | 61 |
| **yes** | fact | What is the Japanese title of Chapter 61? | `routed qa` / `-` | ニュースレポーター |
| **yes** | fact | What is the romaji title of Chapter 61? | `routed qa` / `-` | Nyūsu Repōtā |
| **yes** | fact | On which page does Chapter 61 appear? | `routed qa` / `-` | 21 |
| **yes** | fact | What date is associated with Chapter 61? | `routed qa` / `-` | March 9, 2020 |
| **yes** | fact | What issue is Chapter 61 from? | `routed qa` / `-` | Issue 2020-15 |
| **yes** | fact | In which arc does Chapter 61 appear? | `routed qa` / `-` | International Assassins arc |
| **yes** | fact | What comes before Chapter 61? | `routed qa` / `-` | Chapter 60 |
| **yes** | fact | What comes after Chapter 61? | `routed qa` / `-` | Chapter 62 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

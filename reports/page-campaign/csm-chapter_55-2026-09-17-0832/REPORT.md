# Page campaign csm/chapter_55 — 2026-09-17-0832

Batch `_csm_page_chapter_55.json`: 11 questions (0 set, 11 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.7s wall clock.

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
| **yes** | fact | What is Chapter 55's title? | `routed qa` / `-` | Let's Go |
| **yes** | fact | In which volume does Chapter 55 appear? | `routed qa` / `-` | 7 |
| **yes** | fact | In which chapter does Chapter 55 appear? | `routed qa` / `-` | 55 |
| **yes** | fact | What is the Japanese title of Chapter 55? | `routed qa` / `-` | レッツゴー |
| **yes** | fact | What is the romaji title of Chapter 55? | `routed qa` / `-` | Rettsu Gō |
| **yes** | fact | On which page does Chapter 55 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 55? | `routed qa` / `-` | January 27, 2020 |
| **yes** | fact | What issue is Chapter 55 from? | `routed qa` / `-` | Issue 2020-09 |
| **yes** | fact | In which arc does Chapter 55 appear? | `routed qa` / `-` | International Assassins arc |
| **yes** | fact | What comes before Chapter 55? | `routed qa` / `-` | Chapter 54 |
| **yes** | fact | What comes after Chapter 55? | `routed qa` / `-` | Chapter 56 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

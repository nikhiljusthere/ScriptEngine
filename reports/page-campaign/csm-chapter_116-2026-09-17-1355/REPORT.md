# Page campaign csm/chapter_116 — 2026-09-17-1355

Batch `_csm_page_chapter_116.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 10.9s wall clock.

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
| **yes** | fact | What is Chapter 116's title? | `routed qa` / `-` | Taste of Starfish |
| **yes** | fact | In which volume does Chapter 116 appear? | `routed qa` / `-` | 14 |
| **yes** | fact | In which chapter does Chapter 116 appear? | `routed qa` / `-` | 116 |
| **yes** | fact | What is the Japanese title of Chapter 116? | `routed qa` / `-` | ヒトデの味 |
| **yes** | fact | What is the romaji title of Chapter 116? | `routed qa` / `-` | Hitode no Aji |
| **yes** | fact | On which page does Chapter 116 appear? | `routed qa` / `-` | 20 |
| **yes** | fact | What date is associated with Chapter 116? | `routed qa` / `-` | January 4, 2023 |
| **yes** | fact | In which arc does Chapter 116 appear? | `routed qa` / `-` | Dating Denji arc |
| **yes** | fact | What comes before Chapter 116? | `routed qa` / `-` | Chapter 115 |
| **yes** | fact | What comes after Chapter 116? | `routed qa` / `-` | Chapter 117 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

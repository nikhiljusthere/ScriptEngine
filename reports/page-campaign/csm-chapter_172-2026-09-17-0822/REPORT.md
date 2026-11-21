# Page campaign csm/chapter_172 — 2026-09-17-0822

Batch `_csm_page_chapter_172.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.0s wall clock.

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
| **yes** | fact | What is Chapter 172's title? | `routed qa` / `-` | Bzzz! Boom! Chomp! |
| **yes** | fact | In which volume does Chapter 172 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | In which chapter does Chapter 172 appear? | `routed qa` / `-` | 172 |
| **yes** | fact | What is the Japanese title of Chapter 172? | `routed qa` / `-` | ヴヴン！ドオン！ガブ！ |
| **yes** | fact | What is the romaji title of Chapter 172? | `routed qa` / `-` | Vuvun! Doon! Gabu! |
| **yes** | fact | On which page does Chapter 172 appear? | `routed qa` / `-` | 16 |
| **yes** | fact | What date is associated with Chapter 172? | `routed qa` / `-` | July 24, 2024 |
| **yes** | fact | In which arc does Chapter 172 appear? | `routed qa` / `-` | Aging Devil arc |
| **yes** | fact | What comes before Chapter 172? | `routed qa` / `-` | Chapter 171 |
| **yes** | fact | What comes after Chapter 172? | `routed qa` / `-` | Chapter 173 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/chapter_166 — 2026-09-17-0821

Batch `_csm_page_chapter_166.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.3s wall clock.

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
| **yes** | fact | What is Chapter 166's title? | `routed qa` / `-` | Rain, Brothel, Removal |
| **yes** | fact | In which volume does Chapter 166 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | In which chapter does Chapter 166 appear? | `routed qa` / `-` | 166 |
| **yes** | fact | What is the Japanese title of Chapter 166? | `routed qa` / `-` | 雨・ソープ・切断 |
| **yes** | fact | What is the romaji title of Chapter 166? | `routed qa` / `-` | Ame, Sōpu, Setsudan |
| **yes** | fact | On which page does Chapter 166 appear? | `routed qa` / `-` | 16 |
| **yes** | fact | What date is associated with Chapter 166? | `routed qa` / `-` | May 22, 2024 |
| **yes** | fact | In which arc does Chapter 166 appear? | `routed qa` / `-` | Aging Devil arc |
| **yes** | fact | What comes before Chapter 166? | `routed qa` / `-` | Chapter 165 |
| **yes** | fact | What comes after Chapter 166? | `routed qa` / `-` | Chapter 167 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

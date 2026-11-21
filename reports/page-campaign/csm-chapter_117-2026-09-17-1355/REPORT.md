# Page campaign csm/chapter_117 — 2026-09-17-1355

Batch `_csm_page_chapter_117.json`: 10 questions (0 set, 10 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 11.7s wall clock.

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
| **yes** | fact | What is Chapter 117's title? | `routed qa` / `-` | Penguin and Weapon |
| **yes** | fact | In which volume does Chapter 117 appear? | `routed qa` / `-` | 14 |
| **yes** | fact | In which chapter does Chapter 117 appear? | `routed qa` / `-` | 117 |
| **yes** | fact | What is the Japanese title of Chapter 117? | `routed qa` / `-` | ペンギンと武器 |
| **yes** | fact | What is the romaji title of Chapter 117? | `routed qa` / `-` | Pengin to Buki |
| **yes** | fact | On which page does Chapter 117 appear? | `routed qa` / `-` | 19 |
| **yes** | fact | What date is associated with Chapter 117? | `routed qa` / `-` | January 11, 2023 |
| **yes** | fact | In which arc does Chapter 117 appear? | `routed qa` / `-` | Dating Denji arc |
| **yes** | fact | What comes before Chapter 117? | `routed qa` / `-` | Chapter 116 |
| **yes** | fact | What comes after Chapter 117? | `routed qa` / `-` | Chapter 118 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

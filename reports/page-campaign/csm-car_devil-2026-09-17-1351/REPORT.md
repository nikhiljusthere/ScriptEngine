# Page campaign csm/car_devil — 2026-09-17-1351

Batch `_csm_page_car_devil.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 4.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/4** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What are the kanji for Car Devil's name? | `routed qa` / `-` | 車の悪魔 |
| **yes** | fact | What is the romaji of Car Devil's name? | `routed qa` / `-` | Kuruma no Akuma |
| **yes** | fact | What is Car Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Car Devil? | `routed qa` / `-` | Alive |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

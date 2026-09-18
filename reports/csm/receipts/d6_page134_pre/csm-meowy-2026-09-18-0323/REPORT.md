# Page campaign csm/meowy — 2026-09-18-0323

Batch `_csm_page_meowy.json`: 5 questions (2 set, 3 fact), scored against the live server (started 2026-09-18T02:49:28+00:00), 2.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/5** |
| set questions exact | 2/2 (100.0%) |
| canon items recovered | 6/6 (100.0%) |
| fact answers present | 3/3 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Meowy? | `Every ally of Meowy` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the superiors of Meowy? | `Every superior of Meowy` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | fact | What are the kanji for Meowy's name? | `routed qa` / `-` | ニャーコ |
| **yes** | fact | What is the romaji of Meowy's name? | `routed qa` / `-` | Nyāko |
| **yes** | fact | What is the status of Meowy? | `routed qa` / `-` | Deceased (original timeline) Alive (new timeline) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

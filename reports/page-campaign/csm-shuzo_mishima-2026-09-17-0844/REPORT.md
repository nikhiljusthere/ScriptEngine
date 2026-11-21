# Page campaign csm/shuzo_mishima — 2026-09-17-0844

Batch `_csm_page_shuzo_mishima.json`: 5 questions (0 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/5** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What are the kanji for Shuzo Mishima's name? | `routed qa` / `-` | 三島シュウゾウ |
| **yes** | fact | What is the romaji of Shuzo Mishima's name? | `routed qa` / `-` | Mishima Shuzo |
| **yes** | fact | What is Shuzo Mishima's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Shuzo Mishima? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Shuzo Mishima's occupation? | `routed qa` / `-` | Civilian |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

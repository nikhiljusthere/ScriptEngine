# Page campaign csm/yuki_tomoda — 2026-09-17-0846

Batch `_csm_page_yuki_tomoda.json`: 5 questions (0 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.2s wall clock.

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
| **yes** | fact | What are the kanji for Yuki Tomoda's name? | `routed qa` / `-` | 友田ユウキ |
| **yes** | fact | What is the romaji of Yuki Tomoda's name? | `routed qa` / `-` | Tomoda Yūki |
| **yes** | fact | What is Yuki Tomoda's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Yuki Tomoda? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Yuki Tomoda's occupation? | `routed qa` / `-` | Chief of Cabinet Secretary |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/kentaro_ishita — 2026-09-17-0841

Batch `_csm_page_kentaro_ishita.json`: 5 questions (0 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.2s wall clock.

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
| **yes** | fact | What are the kanji for Kentaro Ishita's name? | `routed qa` / `-` | 石多ケンタロウ |
| **yes** | fact | What is the romaji of Kentaro Ishita's name? | `routed qa` / `-` | Ishita Kentarō |
| **yes** | fact | What is Kentaro Ishita's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Kentaro Ishita? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Kentaro Ishita's occupation? | `routed qa` / `-` | Prime Minister of Japan |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

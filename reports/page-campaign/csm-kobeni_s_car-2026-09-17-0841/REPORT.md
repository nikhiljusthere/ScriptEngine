# Page campaign csm/kobeni_s_car — 2026-09-17-0841

Batch `_csm_page_kobeni_s_car.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/3** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 3/3 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What are the kanji for Kobeni's car's name? | `routed qa` / `-` | コベニの愛車 |
| **yes** | fact | What is the romaji of Kobeni's car's name? | `routed qa` / `-` | Kobeni no Aisha |
| **yes** | fact | What is the status of Kobeni's car? | `routed qa` / `-` | Destroyed |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

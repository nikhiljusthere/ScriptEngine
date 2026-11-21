# Page campaign csm/marshmallow_devil — 2026-09-17-0842

Batch `_csm_page_marshmallow_devil.json`: 5 questions (0 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.1s wall clock.

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
| **yes** | fact | What are the kanji for Marshmallow Devil's name? | `routed qa` / `-` | マシュマロの悪魔 |
| **yes** | fact | What is the romaji of Marshmallow Devil's name? | `routed qa` / `-` | Mashumaro no Akuma |
| **yes** | fact | What is the status of Marshmallow Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Marshmallow Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Marshmallow Devil's occupation? | `routed qa` / `-` | Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

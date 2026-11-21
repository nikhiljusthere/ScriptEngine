# Page campaign csm/mold_devil — 2026-09-17-0842

Batch `_csm_page_mold_devil.json`: 7 questions (0 set, 7 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/7** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 7/7 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What are the kanji for Mold Devil's name? | `routed qa` / `-` | カビの悪魔 |
| **yes** | fact | What is the romaji of Mold Devil's name? | `routed qa` / `-` | Kabi no Akuma |
| **yes** | fact | What is the status of Mold Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | How old is Mold Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Mold Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Mold Devil's occupation? | `routed qa` / `-` | Contract Devil |
| **yes** | fact | What is Mold Devil's birthday? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

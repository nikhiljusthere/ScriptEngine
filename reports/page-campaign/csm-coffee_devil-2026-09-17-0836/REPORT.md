# Page campaign csm/coffee_devil — 2026-09-17-0836

Batch `_csm_page_coffee_devil.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.8s wall clock.

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
| **yes** | fact | What are the kanji for Coffee Devil's name? | `routed qa` / `-` | コーヒーの悪魔 |
| **yes** | fact | What is the romaji of Coffee Devil's name? | `routed qa` / `-` | Kōhī no Akuma |
| **yes** | fact | What is Coffee Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Coffee Devil? | `routed qa` / `-` | Alive |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

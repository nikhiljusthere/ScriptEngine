# Page campaign csm/knife_devil — 2026-09-17-0841

Batch `_csm_page_knife_devil.json`: 5 questions (0 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.2s wall clock.

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
| **yes** | fact | What are the kanji for Knife Devil's name? | `routed qa` / `-` | ナイフの悪魔 |
| **yes** | fact | What is the romaji of Knife Devil's name? | `routed qa` / `-` | Naifu no Akuma |
| **yes** | fact | What is the status of Knife Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Knife Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Knife Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

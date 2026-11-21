# Page campaign csm/stone_devil — 2026-09-17-0845

Batch `_csm_page_stone_devil.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/6** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/1 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Stone Devil? | Petrification | - | <sub>https://chainsaw-man.fandom.com/wiki/Stone_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Stone Devil? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Stone Devil's name? | `routed qa` / `-` | 石の悪魔 |
| **yes** | fact | What is the romaji of Stone Devil's name? | `routed qa` / `-` | Ishi no Akuma |
| **yes** | fact | What is the status of Stone Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Stone Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Stone Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

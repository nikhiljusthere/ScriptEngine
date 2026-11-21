# Page campaign csm/loneliness_fiend — 2026-09-17-0842

Batch `_csm_page_loneliness_fiend.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 1/3 (33.3%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | set | What are all the named techniques of Loneliness Fiend? | Crossbows | Aki Hayakawa, Asa Mitaka, Beam, Cosmo, Galgali, Gun Devil, Loneliness Fiend, Long, Nail Fiend, Pingtsi, Power, Tsugihagi… | <sub>https://chainsaw-man.fandom.com/wiki/Loneliness_Fiend</sub> |
| `exact` | set | What are all the enemies of Loneliness Fiend? | Himeno | Aki Hayakawa, Asa Mitaka, Beam, Cosmo, Galgali, Gun Devil, Loneliness Fiend, Long, Nail Fiend, Pingtsi, Power, Tsugihagi… | <sub>https://chainsaw-man.fandom.com/wiki/Loneliness_Fiend</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Loneliness Fiend? | `Fiends` / `exact` | 0 found, 1 missing; returned 13 |
| no | set | What are all the enemies of Loneliness Fiend? | `Fiends` / `exact` | 1 found, 1 missing; returned 13 |
| **yes** | fact | What are the kanji for Loneliness Fiend's name? | `routed qa` / `-` | 孤独の魔人 |
| **yes** | fact | What is the romaji of Loneliness Fiend's name? | `routed qa` / `-` | Kodoku no Majin |
| **yes** | fact | What is Loneliness Fiend's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Loneliness Fiend? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Loneliness Fiend's occupation? | `routed qa` / `-` | Wild Fiend |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/doll_devil — 2026-09-17-0837

Batch `_csm_page_doll_devil.json`: 8 questions (1 set, 7 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/8** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/1 (0.0%) |
| fact answers present | 7/7 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | set | What are all the affiliations of Doll Devil? | Santa Claus | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Doll_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Doll Devil? | `Devils (Affiliation)` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Doll Devil's name? | `routed qa` / `-` | 人形の悪魔 |
| **yes** | fact | What is the romaji of Doll Devil's name? | `routed qa` / `-` | Ningyō no Akuma |
| **yes** | fact | What is the status of Doll Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | How old is Doll Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Doll Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Doll Devil's birthday? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Doll Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

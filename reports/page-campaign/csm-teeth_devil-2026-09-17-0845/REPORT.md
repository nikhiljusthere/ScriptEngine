# Page campaign csm/teeth_devil — 2026-09-17-0845

Batch `_csm_page_teeth_devil.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.1s wall clock.

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
| `exact` | set | What are all the affiliations of Teeth Devil? | Death Devil (brainwashed) | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Teeth_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Teeth Devil? | `Devils (Affiliation)` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What is the romaji of Teeth Devil's name? | `routed qa` / `-` | Ha no Akuma |
| **yes** | fact | What are the kanji for Teeth Devil's name? | `routed qa` / `-` | 歯の悪魔 |
| **yes** | fact | What is Teeth Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Teeth Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Teeth Devil's occupation? | `routed qa` / `-` | Death's Pawn (formerly) Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

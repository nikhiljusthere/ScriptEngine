# Page campaign csm/mannequin_devil — 2026-09-17-0842

Batch `_csm_page_mannequin_devil.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/4 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Mannequin Devil? | Mannequin Mimicry, Mannequin Possession | - | <sub>https://chainsaw-man.fandom.com/wiki/Mannequin_Devil</sub> |
| `exact` | set | What are all the enemies of Mannequin Devil? | Kishibe, Quanxi | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Mannequin_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Mannequin Devil? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the enemies of Mannequin Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 88 |
| **yes** | fact | What are the kanji for Mannequin Devil's name? | `routed qa` / `-` | マネキンの悪魔 |
| **yes** | fact | What is the romaji of Mannequin Devil's name? | `routed qa` / `-` | Manekin no Akuma |
| **yes** | fact | What is Mannequin Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Mannequin Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Mannequin Devil's occupation? | `routed qa` / `-` | Wild Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

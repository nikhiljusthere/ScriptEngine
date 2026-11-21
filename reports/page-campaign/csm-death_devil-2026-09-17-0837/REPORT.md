# Page campaign csm/death_devil — 2026-09-17-0837

Batch `_csm_page_death_devil.json`: 14 questions (8 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/14** |
| set questions exact | 0/8 (0.0%) |
| canon items recovered | 20/39 (51.3%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Death Devil? | Absolute Immortality, Death Inducement, Resurrection, Enhancing Healing, Enslavement, Teleportation, Murdercraft | - | <sub>https://chainsaw-man.fandom.com/wiki/Death_Devil</sub> |
| `exact` | set | What are all the allies of Death Devil? | Denji, Asa Mitaka, Miri Sugo | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Death_Devil</sub> |
| `exact` | set | What are all the enemies of Death Devil? | - | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Death_Devil</sub> |
| `exact` | set | What are all the families of Death Devil? | Yuko | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Death_Devil</sub> |
| `exact` | set | What are all the subordinates of Death Devil? | Denji, Fake Chainsaw Man | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Death_Devil</sub> |
| `exact` | set | What are all the superiors of Death Devil? | Denji, Fake Chainsaw Man | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Death_Devil</sub> |
| `exact` | set | What are all the aliases of Death Devil? | Ultimate Terror Great King of Terror Lady Death Devil Li'l D (self-proclaimed) Death (by Yoru) Fami (fake alias) Famine Devil (fake alias) | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Death_Devil</sub> |
| `exact` | set | What are all the affiliations of Death Devil? | Fourth East High School, Devil Hunter Club (formerly), Chainsaw Man Church | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Death_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Death Devil? | `-` / `-` | 0 found, 7 missing; returned 0 |
| no | set | What are all the allies of Death Devil? | `Devils` / `exact` | 3 found, 3 missing; returned 88 |
| no | set | What are all the enemies of Death Devil? | `Devils` / `exact` | 3 found, 0 missing; returned 88 |
| no | set | What are all the families of Death Devil? | `Devils` / `exact` | 5 found, 1 missing; returned 88 |
| no | set | What are all the subordinates of Death Devil? | `Devils` / `exact` | 6 found, 2 missing; returned 88 |
| no | set | What are all the superiors of Death Devil? | `Devils` / `exact` | 2 found, 2 missing; returned 88 |
| no | set | What are all the aliases of Death Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| no | set | What are all the affiliations of Death Devil? | `Devils (Affiliation)` / `exact` | 1 found, 3 missing; returned 88 |
| **yes** | fact | What are the kanji for Death Devil's name? | `routed qa` / `-` | 死の悪魔 |
| **yes** | fact | What is the romaji of Death Devil's name? | `routed qa` / `-` | Shi no Akuma |
| **yes** | fact | What is Death Devil's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Death Devil? | `routed qa` / `-` | Unknown (eldest among the Horsemen) |
| **yes** | fact | What is the status of Death Devil? | `routed qa` / `-` | Erased (original timeline) Unknown (new timeline) |
| **yes** | fact | What is Death Devil's occupation? | `routed qa` / `-` | High School Student (cover) Primal Fear Leader of the Chainsaw Man Church School Festival Planning Committee |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

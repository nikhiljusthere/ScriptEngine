# Page campaign csm/zombie_devil — 2026-09-17-0846

Batch `_csm_page_zombie_devil.json`: 10 questions (3 set, 7 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/10** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/6 (0.0%) |
| fact answers present | 7/7 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Zombie Devil? | Zombie Creation, Blood Consumption | - | <sub>https://chainsaw-man.fandom.com/wiki/Zombie_Devil</sub> |
| `exact` | set | What are all the creations of Zombie Devil? | Katana Man, Akane Sawatari | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Zombie_Devil</sub> |
| `exact` | set | What are all the affiliations of Zombie Devil? | Yakuza (formerly), Makima (brainwashed) | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Zombie_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Zombie Devil? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the creations of Zombie Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 88 |
| no | set | What are all the affiliations of Zombie Devil? | `Devils (Affiliation)` / `exact` | 0 found, 2 missing; returned 88 |
| **yes** | fact | What are the kanji for Zombie Devil's name? | `routed qa` / `-` | ゾンビの悪魔 |
| **yes** | fact | What is the romaji of Zombie Devil's name? | `routed qa` / `-` | Zonbi no Akuma |
| **yes** | fact | How old is Zombie Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Zombie Devil's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Zombie Devil? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Zombie Devil's occupation? | `routed qa` / `-` | Wild Devil
Contract Devil |
| **yes** | fact | What is Zombie Devil's birthday? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

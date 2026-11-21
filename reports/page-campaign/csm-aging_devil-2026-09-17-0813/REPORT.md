# Page campaign csm/aging_devil — 2026-09-17-0813

Batch `_csm_page_aging_devil.json`: 10 questions (4 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/10** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 2/15 (13.3%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Aging Devil? | Nigh-Absolute Immortality, Immense Healing Factor, Hell Connection, Time Manipulation, Rapid-Onset Aging, Remote Harm, Aging's World | - | <sub>https://chainsaw-man.fandom.com/wiki/Aging_Devil</sub> |
| `exact` | set | What are all the enemies of Aging Devil? | Denji, Hirofumi Yoshida, Fumiko Mifune, Aging Devil's Victim | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Aging_Devil</sub> |
| `exact` | set | What are all the aliases of Aging Devil? | Aging (by Public Safety) | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Aging_Devil</sub> |
| `exact` | set | What are all the affiliations of Aging Devil? | Public Safety Devil Hunters | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Aging_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Aging Devil? | `-` / `-` | 0 found, 7 missing; returned 0 |
| no | set | What are all the enemies of Aging Devil? | `Devils` / `exact` | 2 found, 4 missing; returned 88 |
| no | set | What are all the aliases of Aging Devil? | `Devils` / `exact` | 0 found, 1 missing; returned 88 |
| no | set | What are all the affiliations of Aging Devil? | `Devils (Affiliation)` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Aging Devil's name? | `routed qa` / `-` | 老いの悪魔 |
| **yes** | fact | What is the romaji of Aging Devil's name? | `routed qa` / `-` | Oi no Akuma |
| **yes** | fact | What is Aging Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Aging Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Aging Devil's occupation? | `routed qa` / `-` | Primal Fear Wild Devil Contract Devil |
| **yes** | fact | How old is Aging Devil? | `routed qa` / `-` | 2,000+ |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

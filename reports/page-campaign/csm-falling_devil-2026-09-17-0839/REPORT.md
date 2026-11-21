# Page campaign csm/falling_devil — 2026-09-17-0839

Batch `_csm_page_falling_devil.json`: 10 questions (4 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/10** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 5/27 (18.5%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Falling Devil? | Nigh-Absolute Immortality, Immense Healing Factor, Hell Connection, Gravity Manipulation, Traumatic Anti-Gravity, Levitation, Area Denial, Targeted Control, Energy Beam, Thought Manipulation, Emotion Manipulation, Psychic Assault, Trauma based anti-gravity powers, Body Control, Object Creation, Immense Strength, Immense Speed, Enhanced Smell, Low Durability | - | <sub>https://chainsaw-man.fandom.com/wiki/Falling_Devil</sub> |
| `exact` | set | What are all the enemies of Falling Devil? | Asa Mitaka, Denji | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Falling_Devil</sub> |
| `exact` | set | What are all the superiors of Falling Devil? | - | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Falling_Devil</sub> |
| `exact` | set | What are all the affiliations of Falling Devil? | Yoru (transformed) Death Devil (brainwashed) † Justice Devil † | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Falling_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Falling Devil? | `-` / `-` | 0 found, 19 missing; returned 0 |
| no | set | What are all the enemies of Falling Devil? | `Devils` / `exact` | 2 found, 2 missing; returned 88 |
| no | set | What are all the superiors of Falling Devil? | `Devils` / `exact` | 3 found, 0 missing; returned 88 |
| no | set | What are all the affiliations of Falling Devil? | `Devils (Affiliation)` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What are the kanji for Falling Devil's name? | `routed qa` / `-` | 落下の悪魔 |
| **yes** | fact | What is the romaji of Falling Devil's name? | `routed qa` / `-` | Rakka no Akuma |
| **yes** | fact | What is Falling Devil's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Falling Devil? | `routed qa` / `-` | Incapacitated |
| **yes** | fact | How old is Falling Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Falling Devil's occupation? | `routed qa` / `-` | Primal Fear Wild Devil Hell's Chef Yoru's Pawn Death's Pawn (formally) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

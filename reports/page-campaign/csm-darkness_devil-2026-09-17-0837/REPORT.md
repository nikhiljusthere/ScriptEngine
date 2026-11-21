# Page campaign csm/darkness_devil — 2026-09-17-0837

Batch `_csm_page_darkness_devil.json`: 8 questions (2 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/8** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 2/12 (16.7%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Darkness Devil? | Immense Speed, Immense Strength, Nigh-Absolute Immortality, Immense Healing Factor, Darkness Manipulation, Blade of Darkness, Force Manipulation, Regeneration Nullification, Shapeshifting, Devil Manifestation | - | <sub>https://chainsaw-man.fandom.com/wiki/Darkness_Devil</sub> |
| `exact` | set | What are all the enemies of Darkness Devil? | - | AIDS Devil, Accident Devil, Aging Devil, Angel Devil, Arnolone Syndrome Devil, Bat Devil, Bitterness Devil, Bucky, Car Devil, Carpenter Bee Devil, Centipede Devil, Claw Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Darkness_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Darkness Devil? | `-` / `-` | 0 found, 10 missing; returned 0 |
| no | set | What are all the enemies of Darkness Devil? | `Devils` / `exact` | 2 found, 0 missing; returned 88 |
| **yes** | fact | What are the kanji for Darkness Devil's name? | `routed qa` / `-` | 闇の悪魔 |
| **yes** | fact | What is the romaji of Darkness Devil's name? | `routed qa` / `-` | Yami no Akuma |
| **yes** | fact | What is the status of Darkness Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | How old is Darkness Devil? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Darkness Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Darkness Devil's occupation? | `routed qa` / `-` | Primal Fear Wild Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

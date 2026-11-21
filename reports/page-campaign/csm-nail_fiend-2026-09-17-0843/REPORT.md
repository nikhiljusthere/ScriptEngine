# Page campaign csm/nail_fiend — 2026-09-17-0843

Batch `_csm_page_nail_fiend.json`: 10 questions (5 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/10** |
| set questions exact | 0/5 (0.0%) |
| canon items recovered | 3/15 (20.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | set | What are all the named techniques of Nail Fiend? | Enhanced Physique | Aki Hayakawa, Asa Mitaka, Beam, Cosmo, Galgali, Gun Devil, Loneliness Fiend, Long, Nail Fiend, Pingtsi, Power, Tsugihagi… | <sub>https://chainsaw-man.fandom.com/wiki/Nail_Fiend</sub> |
| `exact` | set | What are all the allies of Nail Fiend? | Katana Man, Fami, Denji, Seigi Akoku, Haruka Iseumi, Nobana Higashiyama | Aki Hayakawa, Asa Mitaka, Beam, Cosmo, Galgali, Gun Devil, Loneliness Fiend, Long, Nail Fiend, Pingtsi, Power, Tsugihagi… | <sub>https://chainsaw-man.fandom.com/wiki/Nail_Fiend</sub> |
| `exact` | set | What are all the enemies of Nail Fiend? | Quanxi | Aki Hayakawa, Asa Mitaka, Beam, Cosmo, Galgali, Gun Devil, Loneliness Fiend, Long, Nail Fiend, Pingtsi, Power, Tsugihagi… | <sub>https://chainsaw-man.fandom.com/wiki/Nail_Fiend</sub> |
| `exact` | set | What are all the aliases of Nail Fiend? | Nail (by Public Safety) Nail Devil | Aki Hayakawa, Asa Mitaka, Beam, Cosmo, Galgali, Gun Devil, Loneliness Fiend, Long, Nail Fiend, Pingtsi, Power, Tsugihagi… | <sub>https://chainsaw-man.fandom.com/wiki/Nail_Fiend</sub> |
| `exact` | set | What are all the affiliations of Nail Fiend? | Public Safety Devil Hunters (formerly), Tokyo Special Division 7 (formerly), Katana Man | Yoru, Power, Aki Hayakawa, Beam, Galgali, Nail Fiend, Cosmo, Long, Pingtsi, Tsugihagi, Gun Devil, Asa Mitaka… | <sub>https://chainsaw-man.fandom.com/wiki/Nail_Fiend</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Nail Fiend? | `Fiends` / `exact` | 0 found, 1 missing; returned 13 |
| no | set | What are all the allies of Nail Fiend? | `Fiends` / `exact` | 2 found, 6 missing; returned 13 |
| no | set | What are all the enemies of Nail Fiend? | `Fiends` / `exact` | 1 found, 1 missing; returned 13 |
| no | set | What are all the aliases of Nail Fiend? | `Fiends` / `exact` | 0 found, 1 missing; returned 13 |
| no | set | What are all the affiliations of Nail Fiend? | `Fiends (Affiliation)` / `exact` | 0 found, 3 missing; returned 13 |
| **yes** | fact | What are the kanji for Nail Fiend's name? | `routed qa` / `-` | 釘の魔人 |
| **yes** | fact | What is the romaji of Nail Fiend's name? | `routed qa` / `-` | Kugi no Majin |
| **yes** | fact | What is Nail Fiend's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Nail Fiend? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Nail Fiend's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (formerly) Wild Fiend |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

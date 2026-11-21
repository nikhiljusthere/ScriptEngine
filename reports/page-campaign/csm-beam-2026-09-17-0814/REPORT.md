# Page campaign csm/beam — 2026-09-17-0814

Batch `_csm_page_beam.json`: 11 questions (5 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/11** |
| set questions exact | 0/5 (0.0%) |
| canon items recovered | 0/15 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Beam? | Enhanced Durability, Intangibility, Devil Transformation, Enhanced Smell | - | <sub>https://chainsaw-man.fandom.com/wiki/Beam</sub> |
| `-` | set | What are all the allies of Beam? | Denji, Aki Hayakawa, Hirofumi Yoshida, Angel Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Beam</sub> |
| `-` | set | What are all the enemies of Beam? | Akane Sawatari, Reze, Typhoon Devil, Tolka | - | <sub>https://chainsaw-man.fandom.com/wiki/Beam</sub> |
| `-` | set | What are all the affiliations of Beam? | Public Safety Devil Hunters, Tokyo Special Division 4 | - | <sub>https://chainsaw-man.fandom.com/wiki/Beam</sub> |
| `-` | set | What are all the aliases of Beam? | Shark Fiend Shark Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Beam</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Beam? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the allies of Beam? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the enemies of Beam? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the affiliations of Beam? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the aliases of Beam? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Beam's name? | `routed qa` / `-` | ビーム |
| **yes** | fact | What is the romaji of Beam's name? | `routed qa` / `-` | Bīmu |
| **yes** | fact | What is Beam's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Beam's height? | `routed qa` / `-` | 176 cm (5'9¼") |
| **yes** | fact | What is the status of Beam? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Beam's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

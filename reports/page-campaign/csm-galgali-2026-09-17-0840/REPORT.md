# Page campaign csm/galgali — 2026-09-17-0840

Batch `_csm_page_galgali.json`: 11 questions (5 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/11** |
| set questions exact | 0/5 (0.0%) |
| canon items recovered | 0/13 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Galgali? | Enhanced Strength, Poison Resistance, Body Transformation, Hand-to-Hand Combat | - | <sub>https://chainsaw-man.fandom.com/wiki/Galgali</sub> |
| `-` | set | What are all the allies of Galgali? | Makima, Kobeni Higashiyama, Aki Hayakawa, Hirofumi Yoshida | - | <sub>https://chainsaw-man.fandom.com/wiki/Galgali</sub> |
| `-` | set | What are all the enemies of Galgali? | Reze, Grape Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Galgali</sub> |
| `-` | set | What are all the aliases of Galgali? | Violence Fiend Violence Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Galgali</sub> |
| `-` | set | What are all the affiliations of Galgali? | Public Safety Devil Hunters, Tokyo Special Division 4 | - | <sub>https://chainsaw-man.fandom.com/wiki/Galgali</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Galgali? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the allies of Galgali? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the enemies of Galgali? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the aliases of Galgali? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the affiliations of Galgali? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Galgali's name? | `routed qa` / `-` | ガルガリ |
| **yes** | fact | What is the romaji of Galgali's name? | `routed qa` / `-` | Garugari |
| **yes** | fact | What is the status of Galgali? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Galgali's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |
| **yes** | fact | What is Galgali's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Galgali's height? | `routed qa` / `-` | 178 cm (5'10") |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

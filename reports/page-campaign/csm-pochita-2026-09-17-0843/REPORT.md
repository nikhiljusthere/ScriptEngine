# Page campaign csm/pochita — 2026-09-17-0843

Batch `_csm_page_pochita.json`: 12 questions (7 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/12** |
| set questions exact | 0/7 (0.0%) |
| canon items recovered | 0/45 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Pochita? | Immense Speed, Immense Durability, Immense Strength, Immense Healing Factor, Immense Hearing, Devil Erasure, Chainsaw Appendage, Chain Entanglement, Body Assimilation, Devil Transformation | - | <sub>https://chainsaw-man.fandom.com/wiki/Pochita</sub> |
| `-` | set | What are all the allies of Pochita? | Denji, Makima, Kobeni Higashiyama, Power, Hirofumi Yoshida, Yoru, Death Devil, Asa Mitaka, Famine Devil, Katana Man, Ear Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Pochita</sub> |
| `-` | set | What are all the enemies of Pochita? | Makima, Reze, Yoru, Aging Devil, Katana Man, Death Devil, Famine Devil, Asa Mitaka, Fami, Whip Hybrid, Hell Devil, Ear Devil, World War II Devil, Centipede Devil, Cockroach Devil, Accident Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Pochita</sub> |
| `-` | set | What are all the rivals of Pochita? | Yoru, Katana Man, Makima | - | <sub>https://chainsaw-man.fandom.com/wiki/Pochita</sub> |
| `-` | set | What are all the romantics of Pochita? | Asa Mitaka, Makima | - | <sub>https://chainsaw-man.fandom.com/wiki/Pochita</sub> |
| `-` | set | What are all the aliases of Pochita? | Chainsaw Chainsaw Devil Chainsaw Man Hero of Hell Black Chainsaw Man | - | <sub>https://chainsaw-man.fandom.com/wiki/Pochita</sub> |
| `-` | set | What are all the affiliations of Pochita? | Yakuza (formerly), Denji | - | <sub>https://chainsaw-man.fandom.com/wiki/Pochita</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Pochita? | `-` / `-` | 0 found, 10 missing; returned 0 |
| no | set | What are all the allies of Pochita? | `-` / `-` | 0 found, 11 missing; returned 0 |
| no | set | What are all the enemies of Pochita? | `-` / `-` | 0 found, 16 missing; returned 0 |
| no | set | What are all the rivals of Pochita? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the romantics of Pochita? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the aliases of Pochita? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the affiliations of Pochita? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Pochita's name? | `routed qa` / `-` | ポチタ |
| **yes** | fact | What is the romaji of Pochita's name? | `routed qa` / `-` | Pochita |
| **yes** | fact | What is Pochita's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Pochita? | `routed qa` / `-` | Erased (original timeline) Unknown (new timeline) |
| **yes** | fact | What is Pochita's occupation? | `routed qa` / `-` | Wild Devil (formerly) Contract Devil Denji's Heart |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/nayuta — 2026-09-17-0843

Batch `_csm_page_nayuta.json`: 14 questions (8 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 5.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/14** |
| set questions exact | 0/8 (0.0%) |
| canon items recovered | 0/21 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Nayuta? | Bang!, Memory Alteration, Perception Alteration | - | <sub>https://chainsaw-man.fandom.com/wiki/Nayuta</sub> |
| `-` | set | What are all the allies of Nayuta? | Fumiko Mifune, Denji, Death Devil, Seigi Akoku | - | <sub>https://chainsaw-man.fandom.com/wiki/Nayuta</sub> |
| `-` | set | What are all the enemies of Nayuta? | Yoru, Barem Bridge, Fumiko Mifune | - | <sub>https://chainsaw-man.fandom.com/wiki/Nayuta</sub> |
| `-` | set | What are all the families of Nayuta? | Denji, Fami, Death Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Nayuta</sub> |
| `-` | set | What are all the subordinates of Nayuta? | Denji, Power, Meowy | - | <sub>https://chainsaw-man.fandom.com/wiki/Nayuta</sub> |
| `-` | set | What are all the superiors of Nayuta? | Denji, Power | - | <sub>https://chainsaw-man.fandom.com/wiki/Nayuta</sub> |
| `-` | set | What are all the affiliations of Nayuta? | Four Horsemen, Public Safety Devil Hunters | - | <sub>https://chainsaw-man.fandom.com/wiki/Nayuta</sub> |
| `-` | set | What are all the aliases of Nayuta? | Control Devil Control (by "Fami") Conquest Devil Devil of Domination The Former Makima (by Barem) | - | <sub>https://chainsaw-man.fandom.com/wiki/Nayuta</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Nayuta? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the allies of Nayuta? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the enemies of Nayuta? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the families of Nayuta? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the subordinates of Nayuta? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the superiors of Nayuta? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Nayuta? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the aliases of Nayuta? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Nayuta's name? | `routed qa` / `-` | ナユタ |
| **yes** | fact | What is the romaji of Nayuta's name? | `routed qa` / `-` | Nayuta |
| **yes** | fact | What is Nayuta's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Nayuta? | `routed qa` / `-` | Deceased (original timeline) Alive (new timeline) |
| **yes** | fact | What is Nayuta's occupation? | `routed qa` / `-` | School Student (formerly) Wild Devil (formerly) Public Safety Devil Hunter |
| **yes** | fact | What is Nayuta's birthday? | `routed qa` / `-` | 1997 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/santa_claus — 2026-09-17-0844

Batch `_csm_page_santa_claus.json`: 12 questions (6 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/12** |
| set questions exact | 0/6 (0.0%) |
| canon items recovered | 0/20 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Santa Claus? | Doll Creation, Perfect Doll Creation, Mind Transfer, Curse Devil Contract, Hell Devil Contract, Enhanced Doll Devil Power, Enhanced Strength, Enhanced Speed, Enhanced Intelligence, Immense Regeneration, Devil Transformation | - | <sub>https://chainsaw-man.fandom.com/wiki/Santa_Claus</sub> |
| `-` | set | What are all the enemies of Santa Claus? | Denji, Quanxi, Cosmo | - | <sub>https://chainsaw-man.fandom.com/wiki/Santa_Claus</sub> |
| `-` | set | What are all the subordinates of Santa Claus? | Tolka, Makima | - | <sub>https://chainsaw-man.fandom.com/wiki/Santa_Claus</sub> |
| `-` | set | What are all the superiors of Santa Claus? | Tolka, Hell Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Santa_Claus</sub> |
| `-` | set | What are all the affiliations of Santa Claus? | Germany (possible ruse) | - | <sub>https://chainsaw-man.fandom.com/wiki/Santa_Claus</sub> |
| `-` | set | What are all the aliases of Santa Claus? | Santa Claus Master The Puppeteer Tolka’s Master | - | <sub>https://chainsaw-man.fandom.com/wiki/Santa_Claus</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Santa Claus? | `-` / `-` | 0 found, 11 missing; returned 0 |
| no | set | What are all the enemies of Santa Claus? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the subordinates of Santa Claus? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the superiors of Santa Claus? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Santa Claus? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the aliases of Santa Claus? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Santa Claus's name? | `routed qa` / `-` | サンタクロース |
| **yes** | fact | What is the romaji of Santa Claus's name? | `routed qa` / `-` | Santa Kurōsu |
| **yes** | fact | What is Santa Claus's gender? | `routed qa` / `-` | Unknown Female (presumably) |
| **yes** | fact | What is the status of Santa Claus? | `routed qa` / `-` | Incapacitated |
| **yes** | fact | What is Santa Claus's occupation? | `routed qa` / `-` | Private Devil Hunter |
| **yes** | fact | How old is Santa Claus? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

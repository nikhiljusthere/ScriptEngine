# Page campaign csm/hell_devil — 2026-09-17-0840

Batch `_csm_page_hell_devil.json`: 8 questions (4 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/8** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 0/7 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Hell Devil? | Hell Connection | - | <sub>https://chainsaw-man.fandom.com/wiki/Hell_Devil</sub> |
| `exact` | set | What are all the enemies of Hell Devil? | Makima, Pochita | Falling Devil, Hell Devil | <sub>https://chainsaw-man.fandom.com/wiki/Hell_Devil</sub> |
| `exact` | set | What are all the subordinates of Hell Devil? | Santa Claus, Makima | Falling Devil, Hell Devil | <sub>https://chainsaw-man.fandom.com/wiki/Hell_Devil</sub> |
| `exact` | set | What are all the affiliations of Hell Devil? | Santa Claus, Anti-Makima Squad | Falling Devil, Hell Devil | <sub>https://chainsaw-man.fandom.com/wiki/Hell_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Hell Devil? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the enemies of Hell Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 2 |
| no | set | What are all the subordinates of Hell Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 2 |
| no | set | What are all the affiliations of Hell Devil? | `Devils` / `exact` | 0 found, 2 missing; returned 2 |
| **yes** | fact | What are the kanji for Hell Devil's name? | `routed qa` / `-` | 地獄の悪魔 |
| **yes** | fact | What is the romaji of Hell Devil's name? | `routed qa` / `-` | Jigoku no Akuma |
| **yes** | fact | What is the status of Hell Devil? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Hell Devil's occupation? | `routed qa` / `-` | Contract Devil |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

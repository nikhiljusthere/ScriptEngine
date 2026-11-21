# Page campaign csm/death_devil — 2026-09-17-1340

Batch `_csm_page_death_devil.json`: 14 questions (8 set, 6 fact), scored against the live server (started 2026-09-17T13:38:35+00:00), 7.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **13/14** |
| set questions exact | 7/8 (87.5%) |
| canon items recovered | 44/45 (97.8%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `declared` | set | What are all the affiliations of Death Devil? | Fourth East High School | Chainsaw Man Church, Devil Hunter Club (formerly), Four Horsemen | <sub>https://chainsaw-man.fandom.com/wiki/Death_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the named techniques of Death Devil? | `Every named technique of Death Devil` / `declared` | 7 found, 0 missing; returned 7 |
| **yes** | set | What are all the allies of Death Devil? | `Every ally of Death Devil` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the enemies of Death Devil? | `Every enemy of Death Devil` / `declared` | 3 found, 0 missing; returned 3 |
| **yes** | set | What are all the families of Death Devil? | `Every family of Death Devil` / `declared` | 6 found, 0 missing; returned 6 |
| **yes** | set | What are all the subordinates of Death Devil? | `Every subordinate of Death Devil` / `declared` | 8 found, 0 missing; returned 8 |
| **yes** | set | What are all the superiors of Death Devil? | `Every superior of Death Devil` / `declared` | 4 found, 0 missing; returned 4 |
| **yes** | set | What are all the aliases of Death Devil? | `Death Devil's aliases` / `declared` | 7 found, 0 missing; returned 7 |
| no | set | What are all the affiliations of Death Devil? | `Death Devil's affiliations` / `declared` | 3 found, 1 missing; returned 3 |
| **yes** | fact | What are the kanji for Death Devil's name? | `routed qa` / `-` | 死の悪魔 |
| **yes** | fact | What is the romaji of Death Devil's name? | `routed qa` / `-` | Shi no Akuma |
| **yes** | fact | What is Death Devil's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Death Devil? | `routed qa` / `-` | Unknown (eldest among the Horsemen) |
| **yes** | fact | What is the status of Death Devil? | `routed qa` / `-` | Erased (original timeline) Unknown (new timeline) |
| **yes** | fact | What is Death Devil's occupation? | `routed qa` / `-` | High School Student (cover) Primal Fear Leader of the Chainsaw Man Church School Festival Planning Committee |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

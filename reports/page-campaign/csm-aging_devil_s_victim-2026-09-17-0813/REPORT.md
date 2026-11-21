# Page campaign csm/aging_devil_s_victim — 2026-09-17-0813

Batch `_csm_page_aging_devil_s_victim.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/2 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Aging Devil's Victim? | Aging Devil Contract | - | <sub>https://chainsaw-man.fandom.com/wiki/Aging_Devil's_Victim</sub> |
| `exact` | set | What are all the affiliations of Aging Devil's Victim? | Public Safety Devil Hunters (formerly) | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Aging_Devil's_Victim</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Aging Devil's Victim? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the affiliations of Aging Devil's Victim? | `Devils (Affiliation)` / `exact` | 0 found, 1 missing; returned 88 |
| **yes** | fact | What is Aging Devil's Victim's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Aging Devil's Victim's birthday? | `routed qa` / `-` | Before 1917 |
| **yes** | fact | What is the status of Aging Devil's Victim? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Aging Devil's Victim's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (formerly)
Construction Worker |
| **yes** | fact | How old is Aging Devil's Victim? | `routed qa` / `-` | 82+ |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/fiend — 2026-09-17-0839

Batch `_csm_page_fiend.json`: 1 questions (1 set, 0 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 0.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **0/1** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/1 (0.0%) |
| fact answers present | 0/0 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `partial` | set | What are all the affiliations of Fiend? | Government, Private Sector, Devils | Aki Hayakawa, Asa Mitaka, Beam, Cosmo, Galgali, Gun Devil, Loneliness Fiend, Long, Nail Fiend, Pingtsi, Power, Tsugihagi… | <sub>https://chainsaw-man.fandom.com/wiki/Fiend</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Fiend? | `Fiends` / `partial` | 0 found, 1 missing; returned 13 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

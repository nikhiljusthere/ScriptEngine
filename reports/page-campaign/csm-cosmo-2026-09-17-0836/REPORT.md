# Page campaign csm/cosmo — 2026-09-17-0836

Batch `_csm_page_cosmo.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/8** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/5 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Cosmo? | Total Understanding, Omniscience | - | <sub>https://chainsaw-man.fandom.com/wiki/Cosmo</sub> |
| `-` | set | What are all the enemies of Cosmo? | Santa Claus, Makima | - | <sub>https://chainsaw-man.fandom.com/wiki/Cosmo</sub> |
| `-` | set | What are all the affiliations of Cosmo? | Quanxi and the Fiends | - | <sub>https://chainsaw-man.fandom.com/wiki/Cosmo</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Cosmo? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the enemies of Cosmo? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Cosmo? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Cosmo's name? | `routed qa` / `-` | コスモ |
| **yes** | fact | What is the romaji of Cosmo's name? | `routed qa` / `-` | Kosumo |
| **yes** | fact | What is the status of Cosmo? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Cosmo's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Cosmo's occupation? | `routed qa` / `-` | Private Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

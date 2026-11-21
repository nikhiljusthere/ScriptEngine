# Page campaign csm/denji_s_father — 2026-09-17-0837

Batch `_csm_page_denji_s_father.json`: 4 questions (2 set, 2 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **2/4** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/3 (0.0%) |
| fact answers present | 2/2 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the families of Denji's Father? | Denji, Asa Mitaka | - | <sub>https://chainsaw-man.fandom.com/wiki/Denji's_Father</sub> |
| `-` | set | What are all the affiliations of Denji's Father? | Yakuza | - | <sub>https://chainsaw-man.fandom.com/wiki/Denji's_Father</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the families of Denji's Father? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Denji's Father? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What is Denji's Father's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Denji's Father? | `routed qa` / `-` | Deceased |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

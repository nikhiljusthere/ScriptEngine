# Page campaign csm/nazi_devil — 2026-09-17-0843

Batch `_csm_page_nazi_devil.json`: 5 questions (1 set, 4 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/5** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 4/4 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | set | What are all the affiliations of Nazi Devil? | - | Yoru, Power, Leech Devil, Fire Devil, Guillotine Devil, Legs Devil, Teeth Devil, Justice Devil, Eternity Devil, Death Devil, Fami, Famine Devil… | <sub>https://chainsaw-man.fandom.com/wiki/Nazi_Devil</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Nazi Devil? | `Devils (Affiliation)` / `exact` | 1 found, 0 missing; returned 88 |
| **yes** | fact | What are the kanji for Nazi Devil's name? | `routed qa` / `-` | ナチスの悪魔 |
| **yes** | fact | What is the romaji of Nazi Devil's name? | `routed qa` / `-` | Nachisu no Akuma |
| **yes** | fact | What is Nazi Devil's gender? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is the status of Nazi Devil? | `routed qa` / `-` | Erased (original timeline) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

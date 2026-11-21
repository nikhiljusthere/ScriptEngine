# Page campaign csm/kenzo — 2026-09-17-0841

Batch `_csm_page_kenzo.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/6** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/1 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the aliases of Kenzo? | Grandpa (by Denji and Power) | - | <sub>https://chainsaw-man.fandom.com/wiki/Kenzo</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the aliases of Kenzo? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | How old is Kenzo? | `routed qa` / `-` | 25 |
| **yes** | fact | What is Kenzo's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Kenzo? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Kenzo's occupation? | `routed qa` / `-` | Private Devil Hunter |
| **yes** | fact | What is Kenzo's birthday? | `routed qa` / `-` | 1972 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

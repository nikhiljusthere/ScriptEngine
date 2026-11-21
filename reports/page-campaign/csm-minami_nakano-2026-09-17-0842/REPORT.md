# Page campaign csm/minami_nakano — 2026-09-17-0842

Batch `_csm_page_minami_nakano.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/3 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the aliases of Minami Nakano? | Minami, New Kid (by Kishibe) | - | <sub>https://chainsaw-man.fandom.com/wiki/Minami_Nakano</sub> |
| `-` | set | What are all the affiliations of Minami Nakano? | Public Safety Devil Hunters (formerly) | - | <sub>https://chainsaw-man.fandom.com/wiki/Minami_Nakano</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the aliases of Minami Nakano? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Minami Nakano? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What is the Japanese spelling of Minami Nakano's name? | `routed qa` / `-` | ナカノミナミ |
| **yes** | fact | What is the romaji of Minami Nakano's name? | `routed qa` / `-` | Nakano Minami |
| **yes** | fact | What is Minami Nakano's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Minami Nakano? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Minami Nakano's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (formerly) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

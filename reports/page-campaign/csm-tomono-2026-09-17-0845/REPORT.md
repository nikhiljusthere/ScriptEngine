# Page campaign csm/tomono — 2026-09-17-0845

Batch `_csm_page_tomono.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/5 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the allies of Tomono? | Yutaro Kurose, Aldo | - | <sub>https://chainsaw-man.fandom.com/wiki/Tomono</sub> |
| `-` | set | What are all the friends of Tomono? | Yutaro Kurose, Michiko Tendo, Aldo | - | <sub>https://chainsaw-man.fandom.com/wiki/Tomono</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Tomono? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the friends of Tomono? | `-` / `-` | 0 found, 3 missing; returned 0 |
| **yes** | fact | What are the kanji for Tomono's name? | `routed qa` / `-` | 友野 |
| **yes** | fact | What is the romaji of Tomono's name? | `routed qa` / `-` | Tomono |
| **yes** | fact | What is the status of Tomono? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Tomono's occupation? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Tomono's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

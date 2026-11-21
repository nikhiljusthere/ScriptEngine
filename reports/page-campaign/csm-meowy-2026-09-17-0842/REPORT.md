# Page campaign csm/meowy — 2026-09-17-0842

Batch `_csm_page_meowy.json`: 5 questions (2 set, 3 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 1.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/5** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/6 (0.0%) |
| fact answers present | 3/3 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the allies of Meowy? | Kishibe, Power, Denji | - | <sub>https://chainsaw-man.fandom.com/wiki/Meowy</sub> |
| `-` | set | What are all the superiors of Meowy? | Power, Denji, Nayuta | - | <sub>https://chainsaw-man.fandom.com/wiki/Meowy</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Meowy? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the superiors of Meowy? | `-` / `-` | 0 found, 3 missing; returned 0 |
| **yes** | fact | What are the kanji for Meowy's name? | `routed qa` / `-` | ニャーコ |
| **yes** | fact | What is the romaji of Meowy's name? | `routed qa` / `-` | Nyāko |
| **yes** | fact | What is the status of Meowy? | `routed qa` / `-` | Deceased (original timeline) Alive (new timeline) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

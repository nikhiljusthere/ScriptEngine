# Page campaign jjk/cursed_womb — 2026-09-04-1741

Batch `_jjk_page_cursed_womb.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/4** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 3/4 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `exact` | fact | What are cursed wombs? | cursed spirits in an early stage of their development that are capable of growing and changing into stronger forms | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Cursed_Womb</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | fact | What are cursed wombs? | `routed roster` / `exact` | answer absent |
| **yes** | fact | What can a cursed womb turn into after enough time? | `routed qa` / `-` | a Finger Bearer |
| **yes** | fact | What is a Cursed Womb: Death Painting? | `routed qa` / `-` | a type of cursed womb that is half-human, half-cursed spirit |
| **yes** | fact | What does Kusozu literally mean? | `routed qa` / `-` | Nine Phase Diagram |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/cursed_corpse — 2026-09-04-1746

Batch `_jjk_page_cursed_corpse.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 5.2s wall clock.

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
| `exact` | fact | What are cursed corpses? | inanimate objects possessed by a curse that is capable of standing on its own | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Cursed_Corpse</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | fact | What are cursed corpses? | `routed roster` / `exact` | answer absent |
| **yes** | fact | What does the core of an artificial cursed corpse act as? | `routed qa` / `-` | a core that acts as their heart |
| **yes** | fact | Who was the foremost practitioner of puppet jujutsu? | `routed qa` / `-` | Masamichi Yaga |
| **yes** | fact | What was the first Abrupt-Mutation Cursed Corpse? | `routed qa` / `-` | Panda |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

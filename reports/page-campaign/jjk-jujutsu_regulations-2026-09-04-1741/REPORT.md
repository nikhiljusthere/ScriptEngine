# Page campaign jjk/jujutsu_regulations — 2026-09-04-1741

Batch `_jjk_page_jujutsu_regulations.json`: 9 questions (0 set, 9 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 11.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/9** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 8/9 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `partial` | fact | What are retired sorcerers forbidden from doing? | forbidden from using any manner of jujutsu | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Jujutsu_Regulations</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | Who agree with the Japanese government to stipulate the Jujutsu Regulations? | `routed qa` / `-` | the Zenin, Gojo, and Kamo families |
| **yes** | fact | What is a sorcerer's mission under the Jujutsu Regulations? | `routed qa` / `-` | to prevent harm to humanity caused by jujutsu, cursed spirits, and cursed objects |
| **yes** | fact | What is Jujutsu Headquarters described as? | `routed qa` / `-` | the division of the Japanese government that is the highest body governing sorcerers |
| **yes** | fact | What is one punishment the Jujutsu Inspector General can impose? | `routed qa` / `-` | Secret execution |
| no | fact | What are retired sorcerers forbidden from doing? | `routed roster` / `partial` | answer absent |
| **yes** | fact | What are threats defined as in the Jujutsu Regulations? | `routed qa` / `-` | cursed spirits, cursed objects, and curse users |
| **yes** | fact | What must sorcerers never do to non-sorcerers? | `routed qa` / `-` | Sorcerers must never harm non-sorcerers through the use of jujutsu, cursed spirits, or cursed objects |
| **yes** | fact | What provision was created during the Culling Game? | `routed qa` / `-` | the Hakari Provision |
| **yes** | fact | What did the Hakari Provision legally permit? | `routed qa` / `-` | sorcerers contracted with Jujutsu Headquarters to battle each other for monetary compensation |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

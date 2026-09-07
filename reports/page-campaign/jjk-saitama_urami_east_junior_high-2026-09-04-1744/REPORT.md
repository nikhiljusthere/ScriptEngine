# Page campaign jjk/saitama_urami_east_junior_high — 2026-09-04-1744

Batch `_jjk_page_saitama_urami_east_junior_high.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 3.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **2/3** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 2/3 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `partial` | fact | What are the student uniforms composed of? | a tan suit jacket with a navy trim over a white dress shirt with a maroon tie | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Saitama_Urami_East_Junior_High</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is Saitama Urami East Junior High? | `routed qa` / `-` | a normal middle school composed of a few different buildings |
| no | fact | What are the student uniforms composed of? | `routed roster` / `partial` | answer absent |
| **yes** | fact | Where would Megumi often get into fights? | `routed qa` / `-` | a courtyard in another that also serves as a parking lot |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

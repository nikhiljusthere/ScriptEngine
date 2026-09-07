# Page campaign jjk/cursed_human — 2026-09-04-1741

Batch `_jjk_page_cursed_human.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.1s wall clock.

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
| `exact` | fact | Who are cursed humans generally? | generally non-sorcerers who have been cursed | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Cursed_Human</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | fact | Who are cursed humans generally? | `routed roster` / `exact` | answer absent |
| **yes** | fact | What did Suguru Geto's religious organization do with cursed humans? | `routed qa` / `-` | It allowed him to collect cursed spirits from them while appearing to alleviate symptoms as a spiritual priest |
| **yes** | fact | What grade was Yuta Okkotsu initially registered as? | `routed qa` / `-` | a special grade cursed human |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

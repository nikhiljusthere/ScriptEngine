# Page campaign jjk/cursed_tool — 2026-09-04-1746

Batch `_jjk_page_cursed_tool.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 5.0s wall clock.

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
| `declared` | fact | What are cursed tools? | weapons infused with cursed energy | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Cursed_Tool</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | fact | What are cursed tools? | `routed roster` / `declared` | answer absent |
| **yes** | fact | How are cursed tools categorized? | `routed qa` / `-` | from grade one to four based on their power and potency |
| **yes** | fact | What can special grade cursed tools be worth? | `routed qa` / `-` | upwards of five hundred million yen |
| **yes** | fact | Where were the cursed tools collected by the Big Three Sorcerer Families stored? | `routed qa` / `-` | in a vault called the cursed warehouse within Tokyo Jujutsu High |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

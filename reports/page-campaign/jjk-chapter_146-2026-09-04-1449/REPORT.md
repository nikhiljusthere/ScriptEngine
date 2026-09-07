# Page campaign jjk/chapter_146 — 2026-09-04-1449

Batch `_jjk_page_chapter_146.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.6s wall clock.

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
| `partial` | fact | What does each player receive as the game's interface, per Chapter 146? | a shikigami known as a Kogane | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Chapter_146</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What have normal people awakened, per Chapter 146? | `routed qa` / `-` | new abilities |
| no | fact | What does each player receive as the game's interface, per Chapter 146? | `routed roster` / `partial` | answer absent |
| **yes** | fact | What does Maki go to collect from the Zenin clan, per Chapter 146? | `routed qa` / `-` | cursed tools |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

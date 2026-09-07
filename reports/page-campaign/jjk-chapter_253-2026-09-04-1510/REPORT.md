# Page campaign jjk/chapter_253 — 2026-09-04-1510

Batch `_jjk_page_chapter_253.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.7s wall clock.

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
| `exact` | fact | What remains to continue the fight when all other options seem lost, per Chapter 253? | one unexpected grade 1 sorcerer | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Chapter_253</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | fact | What remains to continue the fight when all other options seem lost, per Chapter 253? | `routed roster` / `exact` | answer absent |
| **yes** | fact | Whom do Mei Mei, Nanami, and Gojo name as the strongest grade 1 sorcerer, per Chapter 253? | `routed qa` / `-` | Kusakabe |
| **yes** | fact | What devastating blow does Sukuna unleash on Maki, per Chapter 253? | `routed qa` / `-` | a devastating Black Flash |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

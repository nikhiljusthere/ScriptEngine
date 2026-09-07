# Page campaign jjk/chapter_20 — 2026-09-04-0826

Batch `_jjk_page_chapter_20.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T08:23:53+00:00), 4.5s wall clock.

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
| `partial` | fact | What are the curses at Kinema Cinema actually revealed to be, per Chapter 20? | ex-humans that have had their bodies transmogrified by cursed energy | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Chapter_20</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | Whom does the only known witness, Junpei, discuss the origin of curses with, per Chapter 20? | `routed qa` / `-` | Mahito |
| **yes** | fact | What is the name of Yuji's newly developed double-impacted strike, per Chapter 20? | `routed qa` / `-` | Divergent Fist |
| no | fact | What are the curses at Kinema Cinema actually revealed to be, per Chapter 20? | `routed roster` / `partial` | answer absent |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/assistant_manager — 2026-09-04-1735

Batch `_jjk_page_assistant_manager.json`: 6 questions (0 set, 6 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 6.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/6** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 4/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | fact | What combat training do assistant managers receive as students? | During their years as students, managers receive minimal combat training (Fanbook) and are forbidden from engaging in battle. (Volume 2) | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Assistant_Manager</sub> |
| `-` | fact | What happened to assistant managers during the Shibuya Incident? | During the Shibuya Incident, they were once again targeted, with Haruta Shigemo killing several of them. (Chapter 92, Episode 34) | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Assistant_Manager</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is an assistant manager? | `routed qa` / `-` | A jujutsu sorcerer who does not specialize in combat, only acting as helpers to other sorcerers, such as driving, communicating, or assisting the Jujutsu High students. (Volume 2) (Fanbook) |
| no | fact | What combat training do assistant managers receive as students? | `routed qa` / `-` | answer absent |
| **yes** | fact | How do assistant managers differ from windows? | `routed qa` / `-` | Unlike windows, who can only see cursed spirits, assistant managers have the necessary brain structure to manipulate cursed energy, which makes them sorcerers. (Chapter 20, Episode 9) |
| **yes** | fact | What techniques can assistant managers use to assist students? | `routed qa` / `-` | They can use simple shikigami and barrier techniques to assist students, (Volume 2) (Fanbook) and Tengen helps their barriers with their own cursed energy. (Chapter 220) |
| no | fact | What happened to assistant managers during the Shibuya Incident? | `routed narrative` / `-` | answer absent |
| **yes** | fact | Who is noted as having the qualifications to be an assistant manager? | `routed qa` / `-` | Kyoko Tomoe has the qualifications to be an assistant manager. (Modulo Volume 2) |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

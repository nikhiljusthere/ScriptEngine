# Page campaign jjk/assistant_manager — 2026-09-04-1736

Batch `_jjk_page_assistant_manager.json`: 9 questions (0 set, 9 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 9.8s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **9/9** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 9/9 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is an assistant manager? | `routed qa` / `-` | a jujutsu sorcerer who does not specialize in combat |
| **yes** | fact | What roles do assistant managers serve for other sorcerers? | `routed qa` / `-` | acting as helpers to other sorcerers, such as driving, communicating, or assisting the Jujutsu High students |
| **yes** | fact | Are assistant managers permitted to engage in battle? | `routed qa` / `-` | forbidden from engaging in battle |
| **yes** | fact | What combat training do assistant managers receive as students? | `routed qa` / `-` | receive minimal combat training |
| **yes** | fact | How do assistant managers differ from windows? | `routed qa` / `-` | assistant managers have the necessary brain structure to manipulate cursed energy |
| **yes** | fact | What techniques do assistant managers use to assist students? | `routed qa` / `-` | simple shikigami and barrier techniques |
| **yes** | fact | Which student aspired to become an assistant manager? | `routed qa` / `-` | Akari Nitta |
| **yes** | fact | Who killed several assistant managers during the Shibuya Incident? | `routed qa` / `-` | Haruta Shigemo killing several of them |
| **yes** | fact | Who is noted as qualified to be an assistant manager? | `routed qa` / `-` | Kyoko Tomoe has the qualifications to be an assistant manager |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

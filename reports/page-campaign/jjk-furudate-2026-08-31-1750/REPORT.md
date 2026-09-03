# Page campaign jjk/furudate — 2026-08-31-1750

Batch `_jjk_page_furudate.json`: 17 questions (1 set, 16 fact), scored against the live server (started 2026-08-31T13:45:28+00:00), 15.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **17/17** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 16/16 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the affiliations of Furudate? | `Furudate's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Furudate's name? | `routed qa` / `-` | フルダテ |
| **yes** | fact | What is the romaji of Furudate's name? | `routed qa` / `-` | Furudate |
| **yes** | fact | What is Furudate's race? | `routed qa` / `-` | Human |
| **yes** | fact | What is Furudate's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Furudate? | `routed qa` / `-` | Alive |
| **yes** | fact | In which manga chapter does Furudate first appear? | `routed qa` / `-` | Chapter 138 |
| **yes** | fact | In which anime episode is Furudate first depicted? | `routed qa` / `-` | Episode 48 |
| **yes** | fact | Who is Furudate's Japanese voice actor? | `routed qa` / `-` | Tomomichi Nishimura |
| **yes** | fact | What role does Furudate play in the series? | `routed qa` / `-` | a minor character in the Jujutsu Kaisen series |
| **yes** | fact | What is Furudate's role in relation to Naobito Zenin? | `routed qa` / `-` | the executor of Naobito Zenin's will |
| **yes** | fact | What does Furudate look like? | `routed qa` / `-` | a short, old man who wears glasses and whose eyes appear to be barely open |
| **yes** | fact | How is Furudate's personality described? | `routed qa` / `-` | formal and direct, calmly reading out Naobito's will |
| **yes** | fact | What did Furudate announce about Naobito? | `routed qa` / `-` | Naobito has passed away |
| **yes** | fact | Who will become the 27th head of the Zenin Clan, per the will? | `routed qa` / `-` | Naoya will become the 27th head of the Zenin Clan |
| **yes** | fact | What is the condition for Naoya taking over all duties? | `routed qa` / `-` | he is approved by either Ogi or Jinichi |
| **yes** | fact | What did the clause in the will state about Satoru Gojo? | `routed qa` / `-` | if Satoru Gojo has died or become mentally incapacitated, Megumi Fushiguro will assume the role instead |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

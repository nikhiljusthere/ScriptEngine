# Page campaign csm/barem_bridge — 2026-09-17-0814

Batch `_csm_page_barem_bridge.json`: 11 questions (6 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/11** |
| set questions exact | 0/6 (0.0%) |
| canon items recovered | 0/29 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Barem Bridge? | Hybrid Transformation, Augmented Body, Flamethrowers, Blood Consumption, Nigh-Immortality | - | <sub>https://chainsaw-man.fandom.com/wiki/Barem_Bridge</sub> |
| `-` | set | What are all the allies of Barem Bridge? | Makima, Miri Sugo, Whip Hybrid, Spear Hybrid, Fami, Fumiko Mifune | - | <sub>https://chainsaw-man.fandom.com/wiki/Barem_Bridge</sub> |
| `-` | set | What are all the enemies of Barem Bridge? | Denji, Nayuta, Hirofumi Yoshida, Asa Mitaka, Haruka Iseumi, Nobana Higashiyama | - | <sub>https://chainsaw-man.fandom.com/wiki/Barem_Bridge</sub> |
| `-` | set | What are all the subordinates of Barem Bridge? | Haruka Iseumi, Nobana Higashiyama, Miri Sugo, Whip Hybrid, Spear Hybrid | - | <sub>https://chainsaw-man.fandom.com/wiki/Barem_Bridge</sub> |
| `-` | set | What are all the superiors of Barem Bridge? | Makima, Fami, Miri Sugo | - | <sub>https://chainsaw-man.fandom.com/wiki/Barem_Bridge</sub> |
| `-` | set | What are all the affiliations of Barem Bridge? | Makima (brainwashed), Tokyo Special Division 5 (formerly), Fami, Chainsaw Man Church | - | <sub>https://chainsaw-man.fandom.com/wiki/Barem_Bridge</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Barem Bridge? | `-` / `-` | 0 found, 5 missing; returned 0 |
| no | set | What are all the allies of Barem Bridge? | `-` / `-` | 0 found, 6 missing; returned 0 |
| no | set | What are all the enemies of Barem Bridge? | `-` / `-` | 0 found, 6 missing; returned 0 |
| no | set | What are all the subordinates of Barem Bridge? | `-` / `-` | 0 found, 5 missing; returned 0 |
| no | set | What are all the superiors of Barem Bridge? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the affiliations of Barem Bridge? | `-` / `-` | 0 found, 4 missing; returned 0 |
| **yes** | fact | What are the kanji for Barem Bridge's name? | `routed qa` / `-` | バルエム・ブリッチ |
| **yes** | fact | What is the romaji of Barem Bridge's name? | `routed qa` / `-` | Baruemu Buritchi |
| **yes** | fact | What is the status of Barem Bridge? | `routed qa` / `-` | Erased (original timeline) |
| **yes** | fact | What is Barem Bridge's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (brainwashed) Chainsaw Man Church Contractor |
| **yes** | fact | What is Barem Bridge's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

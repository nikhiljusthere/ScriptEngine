# Page campaign csm/hirokazu_arai — 2026-09-17-0840

Batch `_csm_page_hirokazu_arai.json`: 11 questions (4 set, 7 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **7/11** |
| set questions exact | 0/4 (0.0%) |
| canon items recovered | 0/11 (0.0%) |
| fact answers present | 7/7 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Hirokazu Arai? | Fox Devil Contract | - | <sub>https://chainsaw-man.fandom.com/wiki/Hirokazu_Arai</sub> |
| `-` | set | What are all the allies of Hirokazu Arai? | Aki Hayakawa, Kobeni Higashiyama, Himeno, Denji, Power, Fox Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Hirokazu_Arai</sub> |
| `-` | set | What are all the subordinates of Hirokazu Arai? | Himeno, Kobeni Higashiyama | - | <sub>https://chainsaw-man.fandom.com/wiki/Hirokazu_Arai</sub> |
| `-` | set | What are all the affiliations of Hirokazu Arai? | Public Safety Devil Hunters, Tokyo Special Division 4 | - | <sub>https://chainsaw-man.fandom.com/wiki/Hirokazu_Arai</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Hirokazu Arai? | `-` / `-` | 0 found, 1 missing; returned 0 |
| no | set | What are all the allies of Hirokazu Arai? | `-` / `-` | 0 found, 6 missing; returned 0 |
| no | set | What are all the subordinates of Hirokazu Arai? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Hirokazu Arai? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Hirokazu Arai's name? | `routed qa` / `-` | 荒井 ヒロカズ |
| **yes** | fact | What is the romaji of Hirokazu Arai's name? | `routed qa` / `-` | Arai Hirokazu |
| **yes** | fact | How old is Hirokazu Arai? | `routed qa` / `-` | 22 |
| **yes** | fact | What is Hirokazu Arai's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Hirokazu Arai's height? | `routed qa` / `-` | 178 cm (5'10") |
| **yes** | fact | What is the status of Hirokazu Arai? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Hirokazu Arai's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/yutaro_kurose — 2026-09-17-0846

Batch `_csm_page_yutaro_kurose.json`: 8 questions (2 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/8** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/9 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the allies of Yutaro Kurose? | Aki Hayakawa, Michiko Tendo, Subaru, Denji, Tomono, Punishment Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Yutaro_Kurose</sub> |
| `-` | set | What are all the affiliations of Yutaro Kurose? | Public Safety Devil Hunters, Kyoto Division 1, Makima (postmortem) | - | <sub>https://chainsaw-man.fandom.com/wiki/Yutaro_Kurose</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Yutaro Kurose? | `-` / `-` | 0 found, 6 missing; returned 0 |
| no | set | What are all the affiliations of Yutaro Kurose? | `-` / `-` | 0 found, 3 missing; returned 0 |
| **yes** | fact | What are the kanji for Yutaro Kurose's name? | `routed qa` / `-` | 黒瀬 ユウタロウ |
| **yes** | fact | What is the romaji of Yutaro Kurose's name? | `routed qa` / `-` | Kurose Yūtarō |
| **yes** | fact | What is Yutaro Kurose's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Yutaro Kurose's height? | `routed qa` / `-` | 165 cm (5'5") |
| **yes** | fact | What is the status of Yutaro Kurose? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Yutaro Kurose's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

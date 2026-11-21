# Page campaign csm/fami — 2026-09-17-0839

Batch `_csm_page_fami.json`: 12 questions (6 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 4.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/12** |
| set questions exact | 0/6 (0.0%) |
| canon items recovered | 0/32 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the allies of Fami? | Haruka Iseumi, Barem Bridge, Asa Mitaka, Yoru, Denji, Nobana Higashiyama, Seigi Akoku, Fumiko Mifune, Hirofumi Yoshida, Falling Devil, Nail Fiend, Eternity Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Fami</sub> |
| `-` | set | What are all the enemies of Fami? | Pochita, Yoru, Asa Mitaka, Haruka Iseumi, Takagi | - | <sub>https://chainsaw-man.fandom.com/wiki/Fami</sub> |
| `-` | set | What are all the families of Fami? | Yuko, Yoru, Asa Mitaka, Death Devil, Nayuta | - | <sub>https://chainsaw-man.fandom.com/wiki/Fami</sub> |
| `-` | set | What are all the subordinates of Fami? | Haruka Iseumi, Barem Bridge, Asa Mitaka, Death Devil, Falling Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Fami</sub> |
| `-` | set | What are all the affiliations of Fami? | Four Horsemen, Fourth East High School, Devil Hunter Club (formerly), Chainsaw Man Church | - | <sub>https://chainsaw-man.fandom.com/wiki/Fami</sub> |
| `-` | set | What are all the aliases of Fami? | Famine Devil Hunger Devil Hunger (by Makima) | - | <sub>https://chainsaw-man.fandom.com/wiki/Fami</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Fami? | `-` / `-` | 0 found, 12 missing; returned 0 |
| no | set | What are all the enemies of Fami? | `-` / `-` | 0 found, 5 missing; returned 0 |
| no | set | What are all the families of Fami? | `-` / `-` | 0 found, 5 missing; returned 0 |
| no | set | What are all the subordinates of Fami? | `-` / `-` | 0 found, 5 missing; returned 0 |
| no | set | What are all the affiliations of Fami? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the aliases of Fami? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Fami's name? | `routed qa` / `-` | キガ |
| **yes** | fact | What is the romaji of Fami's name? | `routed qa` / `-` | Kiga |
| **yes** | fact | What is Fami's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is the status of Fami? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Fami's occupation? | `routed qa` / `-` | High School Student (cover) Wild Devil |
| **yes** | fact | How old is Fami? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

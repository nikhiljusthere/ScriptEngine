# Page campaign csm/masaki_ando — 2026-09-17-0842

Batch `_csm_page_masaki_ando.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.0s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/6** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/2 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the affiliations of Masaki Ando? | Public Safety Devil Hunters, Tokyo Division 2 | - | <sub>https://chainsaw-man.fandom.com/wiki/Masaki_Ando</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Masaki Ando? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Masaki Ando's name? | `routed qa` / `-` | 安藤 マサキ |
| **yes** | fact | What is the romaji of Masaki Ando's name? | `routed qa` / `-` | Andō Masaki |
| **yes** | fact | What is Masaki Ando's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Masaki Ando? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Masaki Ando's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

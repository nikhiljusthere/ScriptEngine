# Page campaign csm/takagi — 2026-09-17-0845

Batch `_csm_page_takagi.json`: 9 questions (3 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/9** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/10 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the enemies of Takagi? | Asa Mitaka, Fami, Yoru, Katana Man | - | <sub>https://chainsaw-man.fandom.com/wiki/Takagi</sub> |
| `-` | set | What are all the subordinates of Takagi? | Denji, Katana Man, Quanxi | - | <sub>https://chainsaw-man.fandom.com/wiki/Takagi</sub> |
| `-` | set | What are all the affiliations of Takagi? | Public Safety Devil Hunters, Tokyo Special Division 7, Tokyo Devil Detention Center | - | <sub>https://chainsaw-man.fandom.com/wiki/Takagi</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the enemies of Takagi? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the subordinates of Takagi? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the affiliations of Takagi? | `-` / `-` | 0 found, 3 missing; returned 0 |
| **yes** | fact | What are the kanji for Takagi's name? | `routed qa` / `-` | 高木 |
| **yes** | fact | What is the romaji of Takagi's name? | `routed qa` / `-` | Takagi |
| **yes** | fact | How old is Takagi? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Takagi's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Takagi? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Takagi's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

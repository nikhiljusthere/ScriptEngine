# Page campaign csm/subaru — 2026-09-17-0845

Batch `_csm_page_subaru.json`: 7 questions (2 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/7** |
| set questions exact | 0/2 (0.0%) |
| canon items recovered | 0/4 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the allies of Subaru? | Yutaro Kurose, Michiko Tendo | - | <sub>https://chainsaw-man.fandom.com/wiki/Subaru</sub> |
| `-` | set | What are all the affiliations of Subaru? | Public Safety Devil Hunters, Kyoto Division 1 | - | <sub>https://chainsaw-man.fandom.com/wiki/Subaru</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Subaru? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Subaru? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What is the status of Subaru? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Subaru's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |
| **yes** | fact | What is Subaru's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What are the kanji for Subaru's name? | `routed qa` / `-` | 昴 |
| **yes** | fact | What is the romaji of Subaru's name? | `routed qa` / `-` | Subaru |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

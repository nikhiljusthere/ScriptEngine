# Page campaign csm/bucky — 2026-09-17-0814

Batch `_csm_page_bucky.json`: 6 questions (1 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/6** |
| set questions exact | 0/1 (0.0%) |
| canon items recovered | 0/1 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the affiliations of Bucky? | Fourth East High School | - | <sub>https://chainsaw-man.fandom.com/wiki/Bucky</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the affiliations of Bucky? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What is the status of Bucky? | `routed qa` / `-` | Deceased (original timeline) Alive (new timeline) |
| **yes** | fact | What are the kanji for Bucky's name? | `routed qa` / `-` | コケピー |
| **yes** | fact | What is the romaji of Bucky's name? | `routed qa` / `-` | Kokepī |
| **yes** | fact | What is Bucky's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is Bucky's occupation? | `routed qa` / `-` | Wild Devil (formerly) Class Pet |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign csm/michiko_tendo — 2026-09-17-0842

Batch `_csm_page_michiko_tendo.json`: 9 questions (3 set, 6 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.4s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **6/9** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/9 (0.0%) |
| fact answers present | 6/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the allies of Michiko Tendo? | Yutaro Kurose, Subaru, Denji, Punishment Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Michiko_Tendo</sub> |
| `-` | set | What are all the enemies of Michiko Tendo? | Aldo, Joey | - | <sub>https://chainsaw-man.fandom.com/wiki/Michiko_Tendo</sub> |
| `-` | set | What are all the affiliations of Michiko Tendo? | Public Safety Devil Hunters, Kyoto Division 1, Makima (postmortem) | - | <sub>https://chainsaw-man.fandom.com/wiki/Michiko_Tendo</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the allies of Michiko Tendo? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the enemies of Michiko Tendo? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Michiko Tendo? | `-` / `-` | 0 found, 3 missing; returned 0 |
| **yes** | fact | What are the kanji for Michiko Tendo's name? | `routed qa` / `-` | 天童 ミチコ |
| **yes** | fact | What is the romaji of Michiko Tendo's name? | `routed qa` / `-` | Tendō Michiko |
| **yes** | fact | What is Michiko Tendo's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Michiko Tendo's height? | `routed qa` / `-` | 175 cm (5'9") |
| **yes** | fact | What is the status of Michiko Tendo? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Michiko Tendo's occupation? | `routed qa` / `-` | Public Safety Devil Hunter |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

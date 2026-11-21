# Page campaign csm/tolka — 2026-09-17-0845

Batch `_csm_page_tolka.json`: 8 questions (3 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 3.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/8** |
| set questions exact | 0/3 (0.0%) |
| canon items recovered | 0/7 (0.0%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the enemies of Tolka? | Denji, Beam, Makima | - | <sub>https://chainsaw-man.fandom.com/wiki/Tolka</sub> |
| `-` | set | What are all the superiors of Tolka? | Santa Claus, Curse Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Tolka</sub> |
| `-` | set | What are all the affiliations of Tolka? | Soviet Union, Santa Claus (mentor) | - | <sub>https://chainsaw-man.fandom.com/wiki/Tolka</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the enemies of Tolka? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the superiors of Tolka? | `-` / `-` | 0 found, 2 missing; returned 0 |
| no | set | What are all the affiliations of Tolka? | `-` / `-` | 0 found, 2 missing; returned 0 |
| **yes** | fact | What are the kanji for Tolka's name? | `routed qa` / `-` | トーリカ |
| **yes** | fact | What is the romaji of Tolka's name? | `routed qa` / `-` | Tōrika |
| **yes** | fact | What is the status of Tolka? | `routed qa` / `-` | Deceased |
| **yes** | fact | What is Tolka's occupation? | `routed qa` / `-` | Private Devil Hunter |
| **yes** | fact | What is Tolka's gender? | `routed qa` / `-` | Male |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

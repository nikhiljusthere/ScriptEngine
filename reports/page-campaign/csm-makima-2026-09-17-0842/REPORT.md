# Page campaign csm/makima — 2026-09-17-0842

Batch `_csm_page_makima.json`: 16 questions (8 set, 8 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 6.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/16** |
| set questions exact | 0/8 (0.0%) |
| canon items recovered | 0/76 (0.0%) |
| fact answers present | 8/8 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Makima? | Immense Strength, Enhanced Smell, Control, Force Manipulation | - | <sub>https://chainsaw-man.fandom.com/wiki/Makima</sub> |
| `-` | set | What are all the allies of Makima? | Aki Hayakawa, Pochita, Kishibe, Denji, Power, Himeno, Barem Bridge, Galgali | - | <sub>https://chainsaw-man.fandom.com/wiki/Makima</sub> |
| `-` | set | What are all the enemies of Makima? | Denji, Reze, Quanxi, Kishibe, Power, Pochita, Death Devil, Himeno, Gun Devil, Darkness Devil, Hell Devil, Tolka, Cosmo | - | <sub>https://chainsaw-man.fandom.com/wiki/Makima</sub> |
| `-` | set | What are all the romantics of Makima? | Pochita, Denji, Aki Hayakawa | - | <sub>https://chainsaw-man.fandom.com/wiki/Makima</sub> |
| `-` | set | What are all the subordinates of Makima? | Denji, Aki Hayakawa, Angel Devil, Power, Akane Sawatari, Beam, Kusakabe, Tamaoki, Subaru, Hirofumi Yoshida, Princi, Reze, Katana Man, Himeno, Quanxi, Kishibe, Kobeni Higashiyama, Barem Bridge, Miri Sugo, Whip Hybrid, Spear Hybrid, Yutaro Kurose, Michiko Tendo, Zombie Devil, Tsugihagi, Madoka, Punishment Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Makima</sub> |
| `-` | set | What are all the superiors of Makima? | Denji, Power, Aki Hayakawa, Santa Claus, Akane Sawatari, Beam, Princi, Angel Devil, Reze, Quanxi, Katana Man, Himeno, Miri Sugo, Whip Hybrid, Spear Hybrid, Hell Devil | - | <sub>https://chainsaw-man.fandom.com/wiki/Makima</sub> |
| `-` | set | What are all the affiliations of Makima? | Four Horsemen, Public Safety Devil Hunters, Head of the Tokyo Special Division 4, Head of the Tokyo Special Division 5 | - | <sub>https://chainsaw-man.fandom.com/wiki/Makima</sub> |
| `-` | set | What are all the aliases of Makima? | Control Devil Conquest Devil Devil of Domination | - | <sub>https://chainsaw-man.fandom.com/wiki/Makima</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Makima? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the allies of Makima? | `-` / `-` | 0 found, 8 missing; returned 0 |
| no | set | What are all the enemies of Makima? | `-` / `-` | 0 found, 13 missing; returned 0 |
| no | set | What are all the romantics of Makima? | `-` / `-` | 0 found, 3 missing; returned 0 |
| no | set | What are all the subordinates of Makima? | `-` / `-` | 0 found, 27 missing; returned 0 |
| no | set | What are all the superiors of Makima? | `-` / `-` | 0 found, 16 missing; returned 0 |
| no | set | What are all the affiliations of Makima? | `-` / `-` | 0 found, 4 missing; returned 0 |
| no | set | What are all the aliases of Makima? | `-` / `-` | 0 found, 1 missing; returned 0 |
| **yes** | fact | What are the kanji for Makima's name? | `routed qa` / `-` | マキマ |
| **yes** | fact | What is the romaji of Makima's name? | `routed qa` / `-` | Makima |
| **yes** | fact | What is Makima's gender? | `routed qa` / `-` | Female |
| **yes** | fact | What is Makima's height? | `routed qa` / `-` | 168 cm (5'6") |
| **yes** | fact | What is the status of Makima? | `routed qa` / `-` | Deceased; Reincarnated |
| **yes** | fact | What is Makima's occupation? | `routed qa` / `-` | Public Safety Devil Hunter Contract Devil |
| **yes** | fact | How old is Makima? | `routed qa` / `-` | Unknown |
| **yes** | fact | What is Makima's birthday? | `routed qa` / `-` | Unknown |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

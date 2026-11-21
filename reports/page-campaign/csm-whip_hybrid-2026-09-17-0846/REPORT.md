# Page campaign csm/whip_hybrid — 2026-09-17-0846

Batch `_csm_page_whip_hybrid.json`: 10 questions (5 set, 5 fact), scored against the live server (started 2026-09-17T08:00:09+00:00), 2.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/10** |
| set questions exact | 0/5 (0.0%) |
| canon items recovered | 5/16 (31.2%) |
| fact answers present | 5/5 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `-` | set | What are all the named techniques of Whip Hybrid? | Hybrid Transformation, Augmented Body, Whips, Blood Consumption, Nigh-Immortality | - | <sub>https://chainsaw-man.fandom.com/wiki/Whip_Hybrid</sub> |
| `exact` | set | What are all the allies of Whip Hybrid? | - | Barem Bridge, Denji, Katana Man, Miri Sugo, Quanxi, Reze, Spear Hybrid, Whip Hybrid | <sub>https://chainsaw-man.fandom.com/wiki/Whip_Hybrid</sub> |
| `exact` | set | What are all the enemies of Whip Hybrid? | Pochita, Fumiko Mifune | Barem Bridge, Denji, Katana Man, Miri Sugo, Quanxi, Reze, Spear Hybrid, Whip Hybrid | <sub>https://chainsaw-man.fandom.com/wiki/Whip_Hybrid</sub> |
| `exact` | set | What are all the superiors of Whip Hybrid? | Makima | Barem Bridge, Denji, Katana Man, Miri Sugo, Quanxi, Reze, Spear Hybrid, Whip Hybrid | <sub>https://chainsaw-man.fandom.com/wiki/Whip_Hybrid</sub> |
| `exact` | set | What are all the affiliations of Whip Hybrid? | Makima (brainwashed), Tokyo Special Division 5 (formerly), Chainsaw Man Church | Barem Bridge, Denji, Katana Man, Miri Sugo, Quanxi, Reze, Spear Hybrid, Whip Hybrid | <sub>https://chainsaw-man.fandom.com/wiki/Whip_Hybrid</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | set | What are all the named techniques of Whip Hybrid? | `-` / `-` | 0 found, 5 missing; returned 0 |
| no | set | What are all the allies of Whip Hybrid? | `Hybrids` / `exact` | 3 found, 0 missing; returned 8 |
| no | set | What are all the enemies of Whip Hybrid? | `Hybrids` / `exact` | 1 found, 2 missing; returned 8 |
| no | set | What are all the superiors of Whip Hybrid? | `Hybrids` / `exact` | 1 found, 1 missing; returned 8 |
| no | set | What are all the affiliations of Whip Hybrid? | `Hybrids` / `exact` | 0 found, 3 missing; returned 8 |
| **yes** | fact | What is the status of Whip Hybrid? | `routed qa` / `-` | Alive |
| **yes** | fact | What is Whip Hybrid's occupation? | `routed qa` / `-` | Public Safety Devil Hunter (brainwashed) |
| **yes** | fact | What is Whip Hybrid's gender? | `routed qa` / `-` | Female |
| **yes** | fact | How old is Whip Hybrid? | `routed qa` / `-` | 81 |
| **yes** | fact | What is Whip Hybrid's birthday? | `routed qa` / `-` | 1917 |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

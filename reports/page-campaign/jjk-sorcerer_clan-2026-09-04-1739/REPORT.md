# Page campaign jjk/sorcerer_clan — 2026-09-04-1739

Batch `_jjk_page_sorcerer_clan.json`: 6 questions (0 set, 6 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 7.5s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/6** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 5/6 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `declared` | fact | What are the Big Three Families? | a trio of great sorcerer clans of the jujutsu world consisting of the Zenin Clan, the Gojo Clan, and the Kamo Clan | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Sorcerer_Clan</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| no | fact | What are the Big Three Families? | `routed roster` / `declared` | answer absent |
| **yes** | fact | Which two clans have especially bad blood? | `routed qa` / `-` | the Gojo and Zenin Clans |
| **yes** | fact | Which clan descends from Michizane Sugawara? | `routed qa` / `-` | is a clan that descends from Michizane Sugawara |
| **yes** | fact | When did the Kamo Clan rise to prominence? | `routed qa` / `-` | during the Heian era |
| **yes** | fact | What clan is made up of Cursed Speech users marked with the Snake Eyes and Fangs sigil? | `routed qa` / `-` | a widely recognized sorcerer clan made up of Cursed Speech users marked with the Snake Eyes and Fangs sigil |
| **yes** | fact | What sorcerer family was prominent during the golden age of jujutsu? | `routed qa` / `-` | was a prominent sorcerer family during the golden age of jujutsu |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

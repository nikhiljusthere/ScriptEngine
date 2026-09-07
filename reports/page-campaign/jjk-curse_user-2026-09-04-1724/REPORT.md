# Page campaign jjk/curse_user — 2026-09-04-1724

Batch `_jjk_page_curse_user.json`: 9 questions (0 set, 9 fact), scored against the live server (started 2026-09-04T16:43:29+00:00), 162.9s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **5/9** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 5/9 |

## Failures to triage

| | kind | question | missing | returned / intruders | source |
|---|---|---|---|---|---|
| `partial` | fact | What are Non-Curse Users? | Evil non-sorcerers who possess knowledge of jujutsu and are active in the curse user community are known as Non-Curse Users. (Chapter 66, Episode 25) | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Curse_User</sub> |
| `-` | fact | Why was a bounty placed on the young Satoru Gojo? | The threat of the Six Eyes was enough for a bounty of over a hundred thousand to be placed on the child's head. However, no one was ever able to claim it. (Chapter 96, Episode 35) | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Curse_User</sub> |
| `-` | fact | How did the Star Religious Group operate against the Star Plasma Vessel? | The Star Religious Group hired Toji Zenin to assassinate the Star Plasma Vessel while masquerading themselves as a religious order. (Chapter 68, Episode 26) | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Curse_User</sub> |
| `-` | fact | What categories are listed under the list of curse users? | Geto's Original Group, Sukuna & Kenjaku's Alliance, Q, Other Curse Users, and Non-Curse Users. | - | <sub>https://jujutsu-kaisen.fandom.com/wiki/Curse_User</sub> |

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What is a curse user? | `routed qa` / `-` | A curse user is an evil human sorcerer who uses jujutsu with evil intent. (Chapter 21, Episode 9) |
| no | fact | What are Non-Curse Users? | `routed roster` / `partial` | answer absent |
| **yes** | fact | Since when have curse users existed? | `routed qa` / `-` | They have existed as long as jujutsu sorcerers have, and were also prominent threats during the Heian Era alongside cursed spirits. (Chapter 82, Episode 31) |
| no | fact | Why was a bounty placed on the young Satoru Gojo? | `routed qa` / `-` | answer absent |
| **yes** | fact | What effect did Satoru Gojo's presence have on curse users? | `routed qa` / `-` | Satoru's overwhelming presence altered the balance of the jujutsu world. He stripped curse users of their freedom, keeping all evil forces in check. (Chapter 96, Episode 35) |
| no | fact | How did the Star Religious Group operate against the Star Plasma Vessel? | `routed qa` / `-` | answer absent |
| **yes** | fact | Why was Suguru Geto branded a curse user? | `routed qa` / `-` | Suguru Geto, a former student of Tokyo Jujutsu High, was expelled from the school after murdering over a hundred civilians. In accordance with article nine of jujutsu regulations, he was branded a curse user. (Chapter 77, Episode 29) |
| **yes** | fact | What was the goal of the Night Parade of a Hundred Demons? | `routed qa` / `-` | In a major curse user terrorist incident known as the Night Parade of a Hundred Demons, Suguru's group attempted to introduce an era where non-sorcerers would be exterminated. (Chapter 0-3) |
| no | fact | What categories are listed under the list of curse users? | `routed qa` / `-` | answer absent |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/ryu — 2026-09-03-1009

Batch `_jjk_page_ryu.json`: 8 questions (0 set, 8 fact), scored against the live server (started 2026-09-03T08:26:48+00:00), 7.7s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **8/8** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 8/8 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What are the kanji for Ryu's name? | `routed qa` / `-` | 竜 |
| **yes** | fact | What is the romaji of Ryu's name? | `routed qa` / `-` | Ryū |
| **yes** | fact | In which manga chapter does Ryu first appear? | `routed qa` / `-` | Chapter 97 (Attempted)
Chapter 257 |
| **yes** | fact | In which anime episode is Ryu first depicted? | `routed qa` / `-` | Episode 35 (Attempted) |
| **yes** | fact | What form does Ryu take? | `routed qa` / `-` | Ryu takes the form of a large serpentine creature with two forearms that end in claws, black eyes, and a pair of horns. |
| **yes** | fact | How is Ryu summoned from the user's hand? | `routed qa` / `-` | It is summoned from the user's right hand after they concentrate cursed energy through it. |
| **yes** | fact | What did Ino claim about Ryu's power as an Auspicious Beast? | `routed qa` / `-` | According to Ino, Ryu is a powerful Auspicious Beast, as none of his opponents survived to tell the tale after he used it against them. |
| **yes** | fact | What is Ryu a reference to? | `routed qa` / `-` | Ryu is a reference to the Japanese name of the Chinese dragon, a creature from East Asian mythology. |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

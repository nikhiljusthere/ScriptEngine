# Page campaign jjk/dapa — 2026-08-31-1801

Batch `_jjk_page_dapa.json`: 22 questions (3 set, 19 fact), scored against the live server (started 2026-08-31T13:45:28+00:00), 21.1s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **22/22** |
| set questions exact | 3/3 (100.0%) |
| canon items recovered | 5/5 (100.0%) |
| fact answers present | 19/19 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | What are all the allies of Dapa? | `Every ally of Dapa` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the enemies of Dapa? | `Every enemy of Dapa` / `declared` | 2 found, 0 missing; returned 2 |
| **yes** | set | What are all the affiliations of Dapa? | `Dapa's affiliations` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Dapa's name? | `routed qa` / `-` | ダパ |
| **yes** | fact | What is the romaji of Dapa's name? | `routed qa` / `-` | Dapa |
| **yes** | fact | What is Dapa's race? | `routed qa` / `-` | Simurian |
| **yes** | fact | What is Dapa's gender? | `routed qa` / `-` | Male |
| **yes** | fact | What is the status of Dapa? | `routed qa` / `-` | Alive |
| **yes** | fact | In which manga chapter does Dapa first appear? | `routed qa` / `-` | Modulo Chapter 8 |
| **yes** | fact | What role does Dapa play in the series? | `routed qa` / `-` | a minor character in Jujutsu Kaisen Modulo |
| **yes** | fact | What is Dapa's origin, and how did he come to Earth? | `routed qa` / `-` | a Simurian of the Rumel Tribe that arrived at Earth in 2086 seeking refuge |
| **yes** | fact | Who is Dapa a close friend of? | `routed qa` / `-` | one of Osuki's close friends |
| **yes** | fact | What does Dapa look like? | `routed qa` / `-` | a moderately muscular man of average height with long, light-green hair |
| **yes** | fact | What does Dapa wear? | `routed qa` / `-` | a long, sleeveless purple robe that reaches below his knees, paired with dark-colored pants |
| **yes** | fact | Why did Dapa become bitter toward the Deskunte Tribe? | `routed qa` / `-` | after they exiled his people to barren lands and burned down their village |
| **yes** | fact | What did Dapa sabotage? | `routed qa` / `-` | Dura Val Bobbidi Mechika's efforts to build a canal |
| **yes** | fact | What is Dapa's attitude toward the people of Earth? | `routed qa` / `-` | support coexistence with the people of Earth and shows a genuine interest in Earth culture |
| **yes** | fact | What tendency does Dapa have regarding Osuki's orders? | `routed qa` / `-` | initially agree with Osuki’s orders, only to raise objections afterward |
| **yes** | fact | What did Dapa witness at the Deskunte fighting tournament? | `routed qa` / `-` | Dura's victory |
| **yes** | fact | Who attacked Dapa and his friends in the tent, and why? | `routed qa` / `-` | Cross entered the tent and attacked them in retaliation for their sabotage |
| **yes** | fact | What is the source of a Simurian's rolloluca? | `routed qa` / `-` | a third eye on their foreheads |
| **yes** | fact | When do Rumelians cry from their third eye? | `routed qa` / `-` | when a Kalyan dies |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

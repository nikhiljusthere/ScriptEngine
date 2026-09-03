# Page campaign jjk/decay — 2026-09-03-0516

Batch `_jjk_page_decay.json`: 13 questions (1 set, 12 fact), scored against the live server (started 2026-09-03T04:03:51+00:00), 11.6s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **13/13** |
| set questions exact | 1/1 (100.0%) |
| canon items recovered | 1/1 (100.0%) |
| fact answers present | 12/12 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | set | Every battle involving Decay | `Every battle involving Decay` / `declared` | 1 found, 0 missing; returned 1 |
| **yes** | fact | What are the kanji for Decay's name? | `routed qa` / `-` | 朽 |
| **yes** | fact | What is the romaji of Decay's name? | `routed qa` / `-` | Kyū |
| **yes** | fact | In which manga chapter does Decay first appear? | `routed qa` / `-` | Chapter 60 |
| **yes** | fact | In which anime episode is Decay first depicted? | `routed qa` / `-` | Episode 24 |
| **yes** | fact | What is the outcome of Yuji Itadori & Nobara Kugisaki vs. Eso & Kechizu? | `routed qa` / `-` | Yuji & Nobara are victorious. |
| **yes** | fact | Where did Yuji Itadori & Nobara Kugisaki vs. Eso & Kechizu take place? | `routed qa` / `-` | Yasohachi Bridge |
| **yes** | fact | In which manga chapter does Yuji Itadori & Nobara Kugisaki vs. Eso & Kechizu begin? | `routed qa` / `-` | Chapter 59 |
| **yes** | fact | In which episode is Yuji Itadori & Nobara Kugisaki vs. Eso & Kechizu depicted? | `routed qa` / `-` | Episode 23 - 24 |
| **yes** | fact | In which arc does Yuji Itadori & Nobara Kugisaki vs. Eso & Kechizu take place? | `routed qa` / `-` | Death Painting |
| **yes** | fact | What does the Decay technique do? | `routed qa` / `-` | This technique creates a floral pattern on the target that decomposes their body quickly. |
| **yes** | fact | How can Decay afflict someone? | `routed qa` / `-` | Anyone who takes in the blood of a Rot Technique user through membranes or wounds can be afflicted with this technique. |
| **yes** | fact | What is Decay called in the VIZ English translation? | `routed qa` / `-` | In VIZ Media's English translation of Jujutsu Kaisen, this ability is referred to as Supreme Rot Technique: Decay. |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/chapter_4 — 2026-09-04-0825

Batch `_jjk_page_chapter_4.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T08:23:53+00:00), 3.3s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **3/3** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 3/3 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | Where does Gojo send Yuji and Nobara to exorcise cursed spirits as a field test, per Chapter 4? | `routed qa` / `-` | an abandoned building near a cemetery |
| **yes** | fact | What weapon does Yuji use to slice the curse in the abandoned house, per Chapter 4? | `routed qa` / `-` | the Slaughter Demon knife |
| **yes** | fact | What does Nobara discover about curses in the city compared to those from her hometown, per Chapter 4? | `routed qa` / `-` | much more powerful |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Page campaign jjk/modulo_chapter_13 — 2026-09-04-1528

Batch `_jjk_page_modulo_chapter_13.json`: 3 questions (0 set, 3 fact), scored against the live server (started 2026-09-04T14:06:10+00:00), 3.4s wall clock.

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
| **yes** | fact | What do the Simurians request the Japanese government to do, per Modulo Chapter 13? | `routed qa` / `-` | cease its efforts of exorcising cursed spirits |
| **yes** | fact | Why is Usami in critical condition, per Modulo Chapter 13? | `routed qa` / `-` | the recoil from his Cursed Speech |
| **yes** | fact | Whose recording reveals that Yuji vanished after Hana Kurusu's funeral, per Modulo Chapter 13? | `routed qa` / `-` | an elderly Nobara Kugisaki |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

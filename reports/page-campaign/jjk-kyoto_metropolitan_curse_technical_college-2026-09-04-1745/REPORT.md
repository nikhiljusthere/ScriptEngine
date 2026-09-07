# Page campaign jjk/kyoto_metropolitan_curse_technical_college — 2026-09-04-1745

Batch `_jjk_page_kyoto_metropolitan_curse_technical_college.json`: 4 questions (0 set, 4 fact), scored against the live server (started 2026-09-04T17:31:17+00:00), 4.2s wall clock.

## Headline

| | |
|---|---:|
| **questions passed** | **4/4** |
| set questions exact | 0/0 (0.0%) |
| canon items recovered | 0/0 (0.0%) |
| fact answers present | 4/4 |

## Failures to triage

None. The batch is at 100%.

## All questions

| passed | kind | question | basis / confidence | detail |
|---|---|---|---|---|
| **yes** | fact | What role do the Jujutsu Highs play in Japan? | `routed qa` / `-` | the pillars of the jujutsu community in Japan |
| **yes** | fact | What is the Kyoto Sister-School Goodwill Event? | `routed qa` / `-` | both Jujutsu Highs hold a competition between two teams comprised of their first, second, and third-year students |
| **yes** | fact | Where is Kyoto Jujutsu High located? | `routed qa` / `-` | in Kyoto, which is jujutsu's sacred land |
| **yes** | fact | Who lives beneath Tokyo Jujutsu High in the Tombs of the Star? | `routed qa` / `-` | Master Tengen |

Triage rule: a miss is either a **gold error** (the batch's answer is not what the cited page documents -- fix the batch) or an **engine gap** (undeclared roster, stolen routing, missing link -- declare it in `series/<name>/overrides.yaml` with a comment naming this question).

# Anti-AI Scripting — learning from Wikipedia:Signs of AI writing

**Source:** [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(also via `Wikipedia:AIDETECTION`). A field guide to the identifiable style of
LLM-generated text, with real examples. Distilled here for the one output this
project produces: **spoken narration scripts** for YouTube videos about anime.

The distilled rules below live in `scriptengine/api/rules.py` and are appended to
every context bundle `/context` renders, so every script is written against them
whatever writes it. This document is the full learning: read it to understand
*why* those rules exist, or to tune them.

## Why LLMs sound like LLMs

LLMs pick the most statistically likely next word, so they **regress to the
mean**: specific, unusual facts get replaced by generic positive descriptions.
"The inventor of the first train-coupling device" becomes "a revolutionary
titan of industry". The output is always fluent, always smooth — and always
about the category, never the thing.

The corollary that makes the whole strategy work: **specificity is the moat.**
A script that names chapter numbers, techniques, and who did what to whom
cannot be generic. Everything below exists to defend that.

## The tells (in order of how loudly they scream in a script)

### 1. Significance inflation
LLMs puff up importance: "a pivotal moment", "a crucial turning point",
"changing the Jujutsu world forever", "one of the most devastating attacks in
the series". The same fact stated flatly is more human:

- ✗ "This battle marks a pivotal shift in the Shibuya arc."
- ✓ "The battle ends with Gojo sealed and half the city evacuated."

### 2. The "It's not X, it's Y" reframe
Clearing up a misconception nobody had. "It's not just a punch, it's a
technique." "This isn't about power, it's about conviction." Both are hollow
when B is vague. Delete the contrast and make a direct claim.

### 3. Superficial -ing analyses
Participle phrases tacked onto the end of a sentence that claim significance
without saying anything: "…, highlighting his growth", "…, underscoring the
stakes", "…, paving the way for the final battle". If the analysis matters,
give it its own sentence with a real claim. Otherwise cut it.

### 4. Rule of three reflex
Every list has exactly three items, every claim three supports. Real thinking
has uneven counts. A two-item list stays two items; a four-item list stays
four.

### 5. Avoiding plain words
LLMs dodge "is" and "has": "serves as a", "stands as", "marks a", "boasts",
"features", "plays a role in". A script should use the plain verb: *is, has,
does, fights, says*. The bloated forms are the cadence of a press release, not
a person talking.

### 6. AI vocabulary density
Words that co-occur in LLM output, and where there's one there are usually
more: *delve, realm, testament, pivotal, crucial, transformative, intricate,
showcase, underscore, captivate, embark, unleash, tapestry, foster, seamless,
empower, elevate, revolutionize, landscape, journey, nuanced, rich*. Cut every
word doing PR for an idea instead of describing it.

### 7. Negative parallelism / weasel wording
Vague attribution: "many fans believe", "some argue", "critics consider". If
the context doesn't name them, the script doesn't either. Also: don't
exaggerate how widely held an opinion is from one source.

### 8. Formatting tells (mostly written content, but leak into scripts)
- Em dashes overused for "punched up" emphasis → use periods and commas.
- Boldface and "key takeaways" structure.
- Inline-header vertical lists: "**Name:** description" walls.
- Symmetric parallelism: "He trains, he fights, he wins." Sounds great, says
  nothing.

### 9. Outline conclusions
"Despite its power, the technique faces challenges…" then a vaguely positive
assessment, then "Future Prospects". A script ends when the story ends — not
with a summary paragraph repeating the point.

### 10. Elegant variation
Refusing to repeat a name: "Yuji… the young sorcerer… the vessel…". Humans
say the name again. Lexical diversity for its own sake is a detector tell.

## What does NOT apply to spoken scripts

The written-content tells are weaker or absent in speech: bullet formatting,
boldface, hashtags, em dashes (read aloud they're a pause), and the vocab
blocklist matters less when the line is spoken with a voice behind it. The
rules that always apply out loud: **specificity, no significance inflation,
no hollow reframes, no weasel wording, varied sentence rhythm.**

## The audit (apply before shipping a script)

1. Does it name concrete facts — chapters, techniques, characters — or generic
   categories?
2. Any "pivotal / crucial / testament / realm" doing PR? Cut.
3. Any "It's not X, it's Y" or "Most people think X, but…"? Rewrite as a
   direct claim.
4. Any "-ing" tail ("…, underscoring the stakes")? Cut or make real.
5. Any list with a suspicious rule-of-three symmetry? Check the real count.
6. Any sentence you'd read the same way as the one before? Vary the length.
7. Cover the byline: could an AI write about any anime have produced this
   line? If yes, rewrite it with a fact only this wiki's graph has.

## Where this is enforced

| Layer | Mechanism |
|---|---|
| Always on (every fetch) | `VOICE_RULES` in `scriptengine/api/rules.py`, appended by `render_prompt` to every `/context` bundle |
| The contract, with reasoning | `docs/SCRIPT_STYLE.md` |
| Human-readable learning | this file, `docs/ANTI_AI_SCRIPTING.md` |
| Code-session awareness | referenced from `CLAUDE.md` so future working sessions follow it |

Companion skill (written content, deeper blocklists):
`~/.claude/skills/anti-ai-writing/SKILL.md`.

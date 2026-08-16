"""The writing contract, served with the context.

Until now these three blocks lived in `custom_nodes/ScriptEngineRAG/nodes.py`,
inside the ComfyUI install, a file that is not in this repository. Every
document referred to it as the source of truth, and the direct path (the
assistant writing from `POST /context`) never saw a word of it: the served
`prompt` was research with no instructions attached, so the rules only reached
the writer if it happened to read the docs first.

They live here now, and `docs/SCRIPT_STYLE.md` quotes this module rather than
the other way round. One copy, served to every client.

* `STYLE_RULES`: the house format, from the finished scripts in `sample scripts/`.
* `VOICE_RULES`: the anti-AI voice, distilled from Wikipedia:Signs of AI
  writing. The full learning is `docs/ANTI_AI_SCRIPTING.md`.
* `ANNOTATION_RULES`: how a line states the chapter and episode it came from.
"""

from __future__ import annotations

STYLE_RULES = """\
=== SCRIPT FORMAT ===
- First line: the title, bold, on its own line. A clean name for the topic. Never a question, never a subtitle.
- Then the body: sections, one per item, in a deliberate order (rank, level, arc, chronology, debut order).
- Each section opens with a bulleted bold heading naming the item: `* **Zodd**`, `* **GRADE 4**`, `* **First Layer**`.
- Under a heading the narration is spoken prose. No bullet lists, no sub-headers, no lists of facts.
- Sections are long: one to three dense paragraphs, 800-1500 characters of specific detail each.
- A section is self-contained: name the thing, tell its story with specifics, end it cleanly. No filler transitions ("moving on to...", "next up...").
- Never write a section titled "Final Thoughts". A short plain closing paragraph is fine when it earns one; otherwise end on the last section.
"""

INTRO_ON = """\
- Intro: ON. Between the title and the first section write a hook paragraph, 2-4 sentences, spoken to a viewer who already knows the series. Name the angle and why it is worth watching.
"""

INTRO_OFF = """\
- Intro: OFF. After the title go straight into the first section heading. No preamble of any kind.
"""

VOICE_RULES = """\
=== VOICE RULES: you are a person, not a writer-bot ===
- Write like a fan explaining this arc to a friend out loud. Not like a wiki article, a trailer, or a summary.
- Specificity is everything: name the chapter, the technique, the exact thing that happened. Never trade a fact from the context for a vague superlative ("legendary", "revolutionary", "unforgettable").
- No significance inflation: no "a pivotal moment", "a crucial turning point", "changing everything". State what happened; the facts carry the weight.
- No "It's not X, it's Y" reframes. No "Most people think X, but..." openers. Make the direct claim.
- No -ing tail analyses: "…, highlighting his growth", "…, underscoring the stakes". Cut them or make them a real sentence.
- No rule-of-three packing. No symmetric listicles ("He trains, he fights, he wins.").
- Vary sentence length. Let a short one land, then one breathe. Same-length sentences in a row read robotic.
- Avoid AI vocabulary: delve, realm, testament, pivotal, crucial, transformative, intricate, showcase, underscore, captivate, embark, unleash, tapestry, foster, seamless, empower, elevate, revolutionize, journey, nuanced, rich.
- Use plain verbs: is, has, does, fights, says. Not "serves as", "stands as", "marks a", "boasts", "plays a role in".
- No em dashes. Use periods and commas.
- No weasel wording: "many fans believe", "some argue", "critics say". If the context doesn't name them, the script doesn't either.
- Say the name again rather than inventing epithets ("the young sorcerer", "the vessel").
- Don't repeat the same point twice. No "In conclusion"-style ending that recaps.
- Test every sentence: could an AI writing about any anime have produced it? If yes, rewrite it with a fact only this wiki has.
"""

ANNOTATION_RULES = """\
=== CHAPTER/EPISODE ANNOTATION RULES: every line must be sourced ===
- Each block of narration ends with the chapter and episode it came from, as a bracketed tag on the last line: e.g. "(Chapter 101, Episode 37)". When the context only gives a chapter, write "(Chapter 101)".
- If several consecutive lines share the same chapter or episode, tag them once, at the end of that block. Never repeat the tag on every line.
- Group by the story beat: when a beat spans several consecutive lines, put one tag on the last line of the beat.
- Every section of this context carries a `sourced:` header naming the chapters and episodes its prose comes from, and the prose itself carries inline "(Chapter N, Episode M)" locators. Use those numbers and no others.
- Never invent a chapter or episode number. Only numbers stated in the research context may be used: the `sourced:` headers, the inline locators, debut lines, and "Used by <character> in: Chapter N" lines.
- When the context gives no chapter or episode for a fact, write that line plainly with no tag. Do not guess.
- Tags name the chapter/episode of the moment being described. They are not a citation list.
- Never write a bare retriever marker such as "[1]" or "[12]" in the script.
"""


def writing_rules(intro: bool = True, words: int = 0) -> str:
    """The full contract, with the two choices the user makes folded in."""
    length = (
        f"- Target length: about {words:,} words. Reach it by giving every section "
        "full treatment with real specifics from the context, never by padding.\n"
        if words
        else ""
    )
    return "\n".join(
        [
            STYLE_RULES + (INTRO_ON if intro else INTRO_OFF) + length,
            VOICE_RULES,
            ANNOTATION_RULES,
        ]
    )

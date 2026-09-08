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
* `SCRIPT_FORMAT`: how a *narrative* script is built from a beat list (the
  through-line, flashbacks, which beats to skip).
* `VOICE_RULES`: the HumanScope voice contract — the AI fingerprint is in the
  story's *structure*, so the writer decides the shape (ten structure
  decisions, budget rule) before drafting. Full skill (30-feature audit,
  model fingerprints): `.pi/skills/humanscope/`.
* `ESSENCE_RULES`: the essence contract (owner rule 2026-09-09) — the owner
  supplies the script's shape (opening, pacing, resolution, the tragedies in
  between) before any drafting; anime scripts pace slowly.
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

SCRIPT_FORMAT = """\
=== SCRIPT FORMAT: a narrative script is a story, not a dump ===
- Choose a through-line. A narrative bundle returns dozens of beats; a script wants the ones that carry the story forward, in story order. Fold a background beat into the section it explains rather than giving it a section of its own.
- A prequel sorts first chronologically but is not the start of the story. Volume 0 / Chapter 0.x material belongs in an opening flashback section, not as beat 1 of the main timeline.
- Skip the list beats. Sections that enumerate Chapters, Episodes, Characters Introduced or Terminology Introduced are reference material, not narration; drop them, or fold the one useful fact into the surrounding prose.
- Facts come from the context and nowhere else. A section whose beat carries no locator may set a scene, but may not state a fact; a line that needs a number the context never gives is written plainly without one.
- Open each section with a bulleted bold heading naming the beat, tell it with specifics, and end it cleanly. No filler transitions between beats.
"""

VOICE_RULES = """\
=== VOICE RULES (HumanScope): shape the story before you write it ===
The AI fingerprint is in the story's structure, not its words: a professional
rewrite that removed every stylistic tell moved detection only 1.6 points,
and structure alone still detects at 93.2. So decide the shape first, then
draft from that decision. Never fix a draft by rewording it.

Before any prose, write a 10-line Structure Sheet. One line per decision,
each with a one-clause reason (say why even when you keep the common option):
 1. Timeline: straight through, or jumps? (humans use more flashback/flash-forward)
 2. Subplots: none, one parallel, one contrasting, one unrelated? (humans: no subplots 57%)
 3. What causes the ending: protagonist's choice, mixed, or outside force? (humans: choice 46%)
 4. How it ends: internal acceptance, external action, or unresolved? (humans: acceptance 27%)
 5. The moral: does the narrator ever say what the story means? (humans: says it 52%)
 6. How emotion arrives: body sensation, plain word, or behaviour? (humans: plain word 29%)
 7. How the lead enters: described, mid-action, in dialogue, or in thought? (humans: described 30%)
 8. References: real named things, or vague echoes? (humans: about half and half)
 9. Reader address: does the piece ever acknowledge someone is reading? (humans: sometimes, rarely)
 10. Is the lead morally clean or ambivalent? (humans: ambivalent 59%)

Budget rule: break hard on three or four of the ten, let the rest sit where the
story naturally wants them. A piece that breaks every axis is a new formula,
not a human one. Target the human rate — never the opposite of the AI rate.

While drafting:
- Say the feeling out loud ("he was scared") about a third of the time; do not
  reach for body sensation (tight chest, cold sweat, throat closing) — the
  single biggest AI tell.
- Cut the closing line that explains. If the last paragraph tells the reader
  what the story was about, delete it. Check the second-to-last one too.
- Specificity is everything: name the chapter, the technique, the exact thing
  that happened. Never trade a fact from the context for a vague superlative.
  Plain verbs (is, has, does, fights, says). Vary sentence length. No "It's
  not X, it's Y" reframes, no -ing tail analyses, no rule-of-three packing,
  no weasel wording, no em dashes.

Full 30-feature audit and model fingerprints: the `humanscope` skill
(`.pi/skills/humanscope/`). For a finished draft, run its Mode B audit and fix
only the structural items.
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
- Cite the thing the line is about, not the whole arc. A line on a character's appearance in an arc cites that character's span in it (Toji in Gojo's Past is Ch 66-75, not the arc's full Ch 66-79); a line on a fight cites the fight's span, Chapters X-Y, Episodes A-B, plus a start timestamp when it is a distinct scene.
- A verbatim quote the context carries as a transcript line (speaker + MM:SS) is marked with its timestamp in square brackets, [E27 14:17]; a multi-line quote takes a comma-separated span, [E27 14:17, 14:22].
- Every third passage (paragraph) carries a source-span line directly beneath it, `[covers 4-6]` for the second group of three, naming the distinct events/battles and their ch/ep ranges that those passages draw on, deduplicated. It is a reference line, not narration, and the only list a script may contain.
- Never write a bare retriever marker such as "[1]" (a number alone). A timestamp `[E<n> mm:ss]` and a source-span `[covers n-m]` line are the only square-bracket markers a script may contain.
"""


ESSENCE_RULES = """\
=== ESSENCE RULES: the owner's essence comes before the draft ===
- Before drafting a script, ask the owner for its ESSENCE: the opening (what
  the video starts on and how heavy it is), the pacing, the resolution (the
  thematic verdict the video lands on — a reading of the story, not a literal
  claim), and the bad things / tragedies the video works through in between.
- Anime scripts pace slowly: long deliberate passages, fewer beats per breath.
- Do not guess the essence from the research. The research supplies the facts;
  the owner supplies the shape. If the owner asks, offer some options per
  element and let them pick.
- The essence is the spine: every section serves it, and the closing lands on
  the resolution the owner gave.
"""


def writing_rules(intro: bool = True, words: int = 0) -> str:
    """The full contract, with the two choices the user makes folded in."""
    length = (
        f"- Length contract: the script must be between "
        f"{max(0, words - 500):,} and {words + 500:,} words. "
        f"Count your words before you finish and land inside that band. "
        "Reach it by giving every section full treatment with real specifics "
        "from the context, never by padding.\n"
        if words
        else ""
    )
    return "\n".join(
        [
            STYLE_RULES + (INTRO_ON if intro else INTRO_OFF) + length,
            SCRIPT_FORMAT,
            VOICE_RULES,
            ESSENCE_RULES,
            ANNOTATION_RULES,
        ]
    )

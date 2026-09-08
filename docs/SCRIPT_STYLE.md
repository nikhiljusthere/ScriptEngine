# Script style guide: the house format

The one document that defines how every ScriptEngine script is written. It is the
distillation of three things:

1. The rule blocks in `scriptengine/api/rules.py` (`STYLE_RULES`,
   `SCRIPT_FORMAT`, `VOICE_RULES`, `ANNOTATION_RULES`), which `/context`
   appends to every rendered prompt.
2. The finished scripts in `sample scripts/` (the canonical examples).
3. The `humanscope` skill (`.pi/skills/humanscope/`): the full anti-AI voice
   contract — structure-first decisions, the 30-feature audit, model
   fingerprints.

Write every script to this spec. When the user asks for a script, this document
is the contract; the samples are the proof.

The rules themselves live in code, in one file, and are served with the research
context. They used to live in `custom_nodes/ScriptEngineRAG/nodes.py` inside the
ComfyUI install (a file that is not in this repository), so the direct path
served research with no instructions attached and every client had to find this
document first. Quote `rules.py`; do not re-copy it.

---

## 1. The format at a glance

Two allowed shapes, identical except for the intro:

**With intro:**

```
**Every Level of the Abyss from Made in Abyss**        ← bold title line

<hook paragraph, 2-4 sentences, fan voice>            ← THE INTRO

* **First Layer**                                      ← section heading

<long narration paragraph(s), spoken prose>
...

* **Second Layer**
...
```

**No intro:**

```
**Every Apostle in Berserk Explained**

* **Zodd**

<long narration paragraph(s), spoken prose>
...

* **Wyald**
...
```

The script is saved as `<Title>.md`, one numbered folder per video:
`Video N - <Title>/Script/<Title>.md` in the production tree (the root is
`SCRIPTENGINE_SCRIPTS_ROOT`). Ask `cli script-path "<title>" --create` where it
goes rather than guessing, so a rewrite reuses its own folder.

## 2. The title

First line of the file, bold, on its own line. A clean name for the topic,
never a question, never a subtitle. **The title is the saved filename**, so keep
it the video's actual title: if the engine resolves the subject to something
longer (a full canonical page name), save under the title you asked for, not the
resolved name — `script-gen` rewrites the bold line to match whatever it saves as.

```
**What It's Like to be Every Rank of Curse in Jujutsu Kaisen**
```

## 3. The intro toggle

The user picks **intro yes/no** before the script is written.

**Intro ON**: a hook paragraph between the title and the first section.
2–4 sentences, spoken to a viewer who already knows the series. It names the
angle and why it's worth watching. Real examples from the samples:

> If you thought the Chimera Ants were the scariest thing in *Hunter x Hunter*,
> there's something way worse out there. The same ants that nearly wiped out
> humanity are just a sample of what's crawling around in the most dangerous
> place in the entire series: the Dark Continent. We're talking about a
> location so hostile that its survival rate is 0.04%. So buckle up, because
> today we're breaking down everything you need to know about the Dark
> Continent in a way that actually makes sense.

> Today, we're not watching from the sorcerer's side. We're flipping the script
> entirely and living the curse life, grade by grade, from the absolute jokes
> at the bottom all the way to the catastrophic nightmares at the top.

**Intro OFF**: after the title, go straight into the first section heading.
No preamble of any kind:

```
**Every Level of the Abyss from Made in Abyss**

* **First Layer**
```

## 4. Sections and headings

- The body is a list of sections, one per item, in a deliberate order
  (rank, level, arc, chronology, debut order).
- Each section starts with a heading line that names the item. In the samples
  it is most often a bulleted bold line: `* **Zodd**`, `* **GRADE 4**`,
  `* **First Layer**`. Plain bold (`**The Five Successful Trips and the Five
  Threats**`) and plain bullets (`* First Trip: Begerossé Union and Pap`) also
  appear; a bulleted bold heading is the default.
- A section is a self-contained spoken segment: name the thing, tell its story
  with specifics, end it cleanly. No filler transitions between sections
  ("moving on to...", "next up...").
- Sub-items within a section may be plain bullets with short labels
  (`* First Trip: ...`), each followed by its own narration.
- Under the headings the narration is natural spoken prose: **no bullet lists,
  no sub-headers, no lists of facts**.
- Sections are long. A finished section in the samples is one to three dense
  paragraphs, often 800–1500 characters of specific detail, not a few lines.

## 5. Voice: `VOICE_RULES`

The HumanScope voice block, as served (source of truth:
`scriptengine/api/rules.py`; full skill in `.pi/skills/humanscope/` —
30-feature audit, model fingerprints):

```
=== VOICE RULES (HumanScope): shape the story before you write it ===
...
(quote of the `VOICE_RULES` block in `scriptengine/api/rules.py` — the
Structure Sheet's ten decisions, the budget rule, and the drafting habits;
quote, do not re-copy, per the rule at the top of this doc.)
```

Voice specifics seen in the samples: the "what it's like" scripts (curse ranks,
Abyss levels) use a direct **second person** ("Let's paint you a picture. You
are a Grade 4 curse."); the explainer scripts (Apostles, Dark Continent) use
third person with the fan explaining to a friend. Match the topic.

## 6. Chapter/episode annotations: `ANNOTATION_RULES`

The pipeline rule, as served:

```
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
```

### The three deliverables a script ships with

`script-gen` produces two files, not one. The main script carries the tags,
timestamps and `[covers X-Y]` source-span lines above. Beside it, the pipeline
writes a words-only companion, `<title>-clean.md`, with every citation,
timestamp and source-span marker stripped: the narration an editor records
from, no locators. If the model leaves out the source-span lines, a
deterministic backstop (`writer.ensure_covers_blocks`) rebuilds them from the
chapter/episode tags the three passages already carry, so the spans are the
real ones, never invented.

### Where the numbers come from

Nothing is guessed, and nothing has to be. `scriptengine/retrieve/citations.py`
does two things to the context before it is served:

- **Each `{{Ref}}` covers the sentences before it**, back to the previous
  reference. A wiki cites once at the end of a passage, not once per sentence,
  so reading the reference the way it was placed is what makes every block
  taggable: the Shibuya Incident page goes from 12.8% of sentences carrying a
  locator to 99.6%.
- **A chapter resolves to its episode through the graph.** Half the corpus's
  references give a chapter and no episode, and the wiki states the mapping
  elsewhere as `Chapter N -anime episode-> Episode M`. A chapter the anime never
  adapted resolves to nothing and stays `(Chapter N)`.

So the `sourced:` header on a beat is the range that block may be tagged with,
and it is never empty for prose the wiki cited.

**Note on the finished form:** the published samples in `sample scripts/` do
not carry inline tags; the same sourcing information appears as a
`*References:*` block at the end of each section:

```
*References:*
Episode 32 (Ko-Guy)
Episode 23 (Bridge Curse)
```

or, for manga:

```
*References:*
Manga Chapter 2 (Riko meets Reg in the First Layer)
Manga Chapter 28 / Movie 3 (Debut)
```

Default: write with inline tags per `ANNOTATION_RULES`. If the user wants the
finished form, replace them with per-section `*References:*` blocks listing
the episodes/chapters actually used, each with a short note in parentheses.
Either way: never invent a number.

## 7. Closings

No section titled "Final Thoughts", ever (the user has explicitly banned the
title). A short, plain closing paragraph that lands the topic is fine when it
earns it; the Dark Continent script ends:

> It's not a land waiting to be conquered. It's a place that has already proven
> humans are not ready. And now, humanity is heading back again, fully aware of
> what happened the last time. That's the Dark Continent, explained simply.

If the script doesn't need one, end on the last section's content.

## 8. Length

The whole point of writing scripts outside ComfyUI is length: scripts run to
**6,000 words** by default (the `script-gen` target), not the node's ~2k-token
window. The contract is a **band**, not a floor: land between target − 500 and
target + 500 words. Reach it by giving every section full treatment with real
specifics from the context, never padding; every section should add facts the
others don't repeat. `script-gen` enforces this automatically — expanding while
the draft is under the band's low edge and trimming once past the high edge, up
to ten passes — so a hand-written script must count its words before it is done.

## 9. The canonical samples

| Sample | Demonstrates |
|---|---|
| `Every Apostle in Berserk Explained.docx.md` | No intro; `* **Name**` section headings; third-person fan voice |
| `Every Forbidden Jutsu (Kinjutsu) in Naruto Explained.md` | No intro; item-per-jutsu sections |
| `Every Level of the Abyss from Made in Abyss.docx.md` | No intro; second person; `*References:*` blocks per section |
| `The Dark Continent Explained Simply.md` | Intro ON; sub-bullet sections (`* First Trip: ...`); closing recap without a heading |
| `What Its Like to be Every Rank of Curse in Jujutsu Kaisen.docx.md` | Intro ON; second person; `*References:*` blocks per section |

Before writing any script, skim the relevant sample(s) for the beat of the
prose.

## 10. Which context a topic gets

Four of the five samples are **rosters**: a set enumerated one member per
section. One is a **narrative**: an account told in order. The engine answers in
whichever shape the topic needs, and the fetched bundle says which it used in
`resolved_mode`.

| Topic shape | Mode | What the context looks like |
|---|---|---|
| "Every Apostle", "Every Rank of Curse", "Every Level of the Abyss" | `roster` | `## Members`, optionally under `### <group>` headings, each with its facts, `debut:` and `sourced:` lines |
| "Shibuya Incident", "19 Days without Satoru Gojo" | `narrative` | `## Events in order`, beats in story order under the page they came from |

A roster's `### <group>` headings are the wiki's own tiers: the distinct values
of one infobox field, found through the wiki's label for it. They are the
section order for the script; walk them in whichever direction the topic wants
(the samples climb from weakest to strongest). Members inside a group keep their
order.

The engine states the set it used on a `Set:` line: `Cursed Spirits (class)`
means the members are the wiki's `Cursed Spirits` category, grouped by the field
it labels "Grade". If that set is wrong for the script, re-fetch with a sharper
`-Question` rather than writing around it.

### Narrative scripts: `SCRIPT_FORMAT`

A narrative bundle can return dozens of beats; a script is a through-line, not
a dump. The `SCRIPT_FORMAT` block in `rules.py` (served with every prompt)
says how to build it: pick the beats that carry the story forward and order
them by story time; open a prequel (Volume 0 / Chapter 0.x) as a flashback
section instead of beat 1; skip the list beats (Chapters, Episodes, Characters
Introduced, Terminology Introduced); and never state a fact a beat's
`sourced:` header does not cover. A script on a single character or event is
always written from a narrative bundle: the CLI and MCP research path route a
bare name to narrative precisely so a story comes back, not a lookup.

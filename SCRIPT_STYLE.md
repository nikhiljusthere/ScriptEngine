# What the scripts look like, and what the engine owes them

Derived by reading the 38 scripts in `sample scripts/` — measured, not guessed.
This is the target the engine is building toward: the output has to serve these,
and beat them where they are weakest.

---

## Referencing: the sample scripts' style is *not* the target

The samples cite in italics — `(*Episode 47*)`, 261 of them — and the Jujutsu
Kaisen ones do not cite at all: `All 7 Levels of Curses` and `Cursed Techniques
That Should Not Exist` carry **zero** references across ~17,000 words.

Neither is what we follow. The reference is
`scripts output/Every Fight Mahoraga Has Ever Been In.md`, an engine-produced
script, and its forms are:

| form | count |
|---|---:|
| `(Modulo Chapter N)` | 20 |
| `(Chapter N)` | 20 |
| `(Chapter N, Episode N)` | 11 |
| `(Episode N)` | 1 |

**That is exactly what `citations.Locator.render()` already emits** — plain
parentheses, chapter first, episode appended when the wiki supports it, and the
work named once at the front so `(Modulo Chapter 16)` cannot be confused with
main-series Chapter 16. Nothing about the renderer needs changing.

Two properties of that style worth keeping deliberately:

- **A citation covers the sentences before it, back to the previous one** — it
  sits at the end of a paragraph, not on every clause. This matches how
  `citations.attribute()` already reads refs, and it is why the Mahoraga script
  reads as prose rather than as a bibliography.
- **A chapter with no adaptation stays a bare `(Chapter N)`.** The engine
  resolves chapter → episode through the wiki's own `anime episode` /
  `adapted from` edges, so a missing episode means the anime never adapted it,
  not that the lookup failed. Do not invent one.

The samples' timestamp form — `Episode N 12:30-14:05`, 18 uses — has no
supporting data in the store and is out of scope. Do not fake it.

---

## Two archetypes

Everything in the folder is one of two shapes.

### A. The character life — sectioned by arc

`The Entire Life of Killua Zoldyck`:

```
1. Introduction        5. Yorknew City arc
2. Background          6. Greed Island arc
3. Hunter Exam arc     7. Chimera Ant arc
4. Heavens Arena arc   8. 13th Hunter Chairman Election arc
```

The spine is **arc-by-arc chronology for one character**. Introduction sells the
character, Background covers origin and family, then one section per arc they
appear in.

What that needs from the engine, per arc: what this character did, who they did
it with, what changed for them, and the episode range. Every one of those is a
scoped query — *character × arc* — not a page lookup.

### B. The enumeration — sectioned by tier or member

`All 7 Levels of Sorcerer in JJK`: `Grade 4 → Grade 3 → Grade 2 → Grade 1 →
Special Grade 1 → Ungraded Powerhouses → Special Grade`.

`Every Nen Vow`: `Chain Jail (Kurapika)`, `Emperor Time (Kurapika)`,
`Adult Transformation (Gon)`, `Skill Hunter (Chrollo)` … — **ability plus owner**,
which is exactly the `(member, owner)` shape `roster` mode already returns.

Each entry then wants: the canonical description, a named example, and a feat
that demonstrates it. `All 7 Levels of Curses` quotes the wiki's own wording
directly — *"A wooden bat is enough"* — so canonical phrasing matters as much as
the fact.

**Archetype B is the one the engine already serves.** The question bank is full
of it: "Every ability of X", "Every sword style of Zoro". Archetype A is not
served yet.

---

## How relationships are written

Never as a label. Always as a scene with a turning point:

> His training comes directly from his parents, Silva and Kikyo, and his older
> brother Illumi.

> In an act of rebellion, he lashes out violently, injuring his mother and older
> brother before running away from home.

> When Leorio declares that Gon already considers him his friend, Illumi coldly
> threatens to kill Gon.

> Silva makes him promise never to betray them and then gives him permission to
> go.

Three consequences for `ingest/relations.py`:

- **The quote is the payload, not the label.** `family` is what makes the row
  groupable; the verbatim clause is what a script can actually use. Both are
  stored, and the quote is the one that gets read out.
- **`era` is not optional decoration.** "Killua and Illumi" is a different
  relationship before and after the Hunter Exam. A single flat triple would be
  false for most of the story.
- **The vocabulary is right but thin at the edges.** `family, friend, ally,
  rival, enemy, mentor, student, superior, subordinate, romantic, creator,
  creation` covers all of the above. Watch for `captor`/`captive` and
  `betrayer` — the Zoldyck material leans on both and currently flattens to
  `family` and `enemy`.

---

## What is missing, in priority order

1. **Arc-scoped character chronology.** Archetype A's whole spine. opm arcs
   carry 172 `characters` edges; **jjk arcs carry none**, so "who was in the
   Shibuya Incident" is answerable for one wiki and not the other. Without this
   the engine cannot serve a character-life script at all.
2. **Citation rendering.** Episode-led, italic. Small, and it makes every
   returned bundle paste-ready.
3. **Relations coverage on jjk.** jjk has no `Relationships` section — its
   relationship prose lives in `History` (174 chunks) and `Synopsis` (1,189).
   The default sections reach only 25 jjk characters. Whether `Synopsis` earns
   inclusion is a judgement to make on real output, not in advance: it is plot
   narration, so it is rich but noisy, and "fought once" is not `enemy`.
4. **Timestamps.** Not in the store. Probably out of scope; note it rather than
   fake it.

---

## Voice

Worth recording because the engine's output should not fight it:

- Second person and direct address — "congratulations, they've got at least a
  bit of cursed perception".
- Blunt register mixed with precision — "bottom-feeders" in the same paragraph
  as "3,722 metres".
- Facts are load-bearing and specific: heights, family positions, episode
  numbers, canonical quotes. The prose is casual; the underlying claims are not.

The engine's job is the second half of that. It supplies the precise, cited,
checkable claim; the writing voice sits on top.

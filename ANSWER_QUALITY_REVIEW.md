# Why the answers still miss when the data is there

Reviewed 2026-08-15 against `reports/2026-08-15-0751`: 1176/1362 canon items
(86.3%), **53.4% precision**, 311 questions.

The premise in the question is right and worth stating precisely, because it
narrows the search:

- **158 of 160 set questions return at least one correct item.** Only 2 return
  nothing.
- **102 of 160 find every canon item.**
- **45 of 160 are clean.**

So retrieval is finding the data. The gap between 102 complete and 45 clean is
the whole problem: **57 questions know the right answer and hand it over buried
in wrong ones.** 849 intruders across 78 closed questions.

Where they come from has *changed* as earlier fixes landed, which is why the old
diagnosis no longer applies:

| source | now | at session start |
|---|---:|---:|
| **category page** | **420 (49%)** | 213 (24%) |
| prose row | 287 (34%) | 490 (56%) |
| heading | 104 (12%) | 151 (17%) |
| ownership edge | 26 (3%) | 26 (3%) |

**83% of intruders are vouched for by exactly one source.** Corroboration is
sitting unused.

---

## 1. The category path answers a different question, and calls it `exact`

The single largest defect. When a topic resolves to a category, the character in
the question is discarded entirely.

```
Every named technique Ichigo uses with Zangetsu
  basis `Techniques (technique type)`  confidence `exact`
  4/4 canon, 200 returned, 2% precision
  junk: Ave Mellizos, Barón Puntapiés Alto, Hierro, Cero Córnea, Bukkomi Dogeza
```

Those are Espada and Arrancar techniques. The answer is every technique in
Bleach. One question produces **196 intruders, 23% of every wrong name in the
run.**

Same shape elsewhere:

| question | basis | returned | precision |
|---|---|---:|---:|
| How many special divisions exist in Public Safety | `Devil Hunters` | 74 | 3% |
| Every member of the Disaster Curses | `Cursed Spirits (class)` | 22 | 18% |
| Every member of the Black Swordsman Party | `Black Swordsman Arc Characters` | 21 | 10% |

**`confidence` is `exact` on the first and third of those.** That is the most
damaging part: the bundle tells the caller to trust a 2%-correct answer. A
visibly thin answer gets checked; a confident wrong one reaches the script.

`confidence` is computed from how the set was *found*, never from whether the
members survived scrutiny. A category that matched by name is "exact" by
construction.

**Fix:** when a query names a character and resolves to a category, either
intersect the category with that character's ownership/prose, or refuse. And
`exact` must require that the members were validated, not that the label matched.

## 2. A `Battles` category satisfies a character query

```
Every shikigami of Megumi Fushiguro   basis `Megumi Fushiguro Battles`
  4/9 canon, 24 returned, 17% precision
  junk: Megumi Fushiguro vs. Aoi Todo, Megumi Fushiguro vs. Sukuna, …
```

Every intruder is a battle page. `_files_by_character` (`roster.py:869`) exists
for exactly this (its docstring names `Yuji Itadori Battles` as the case) and
it is not stopping it. Battle pages are `semantics.EVENT`, which
`NEVER_MEMBERS` already declares can never be a member of anything
(`semantics.py:125`); that rule is not being applied on this path.

**Fix:** apply `NEVER_MEMBERS` to category-derived members. It costs nothing and
is already the stated policy.

## 3. Section headings still arrive as members

```
Every Gear technique of Monkey D. Luffy     4/4 canon, 25 returned, 16%
  junk: Speed and Agility, Durability, Endurance, Luck, Artistic Skill
Every sword style of Zoro                   basis `Intelligence / Luck`
```

`Speed and Agility` and `Luck` are headings on a character's page.
`_drop_templates` (`roster.py:1217`) removes headings shared by more than ten
pages; these sit under that threshold on One Piece, so they survive. The
`ability_stopwords` list would catch them and does not cover One Piece.

**Fix:** cheapest is declaring them as stopwords, since the mechanism already applies
on every path since this session. A structural fix is to treat a heading with no
prose of its own as a container.

## 4. Two questions, one set, one of them declared: a bug I introduced

```
Every member of the Black Swordsman Party      -> no declared match  (21 members, 10%)
Who are the members of the Black Swordsman Party? -> declared        (12 members, 100%)
```

Same set, same wiki page, opposite outcomes. `RosterDefinition.matches` tests
`\b{phrase}s?\b`, which allows a trailing `s` on the **whole phrase** but not on
a word inside it. The declaration generated from the newer question carries
`members of the black swordsman party`, and the older question says
`member of the …`. It never matches.

**Fix:** generate singular and plural variants of each match phrase. 12 of the
36 declarations written this session are exposed to this.

Related, and also mine: five declarations carry `subject: Berserk`,
`subject: Bleach`, `subject: One Piece`: the *series*, not a person. `subject:`
exists to say "this set is about this character"; a series name there is
meaningless and, because a `subject:` roster is now excluded from the set
vocabulary, it silently weakens character resolution for that whole wiki.

## 5. `_KIND_NOISE` lets one character's forms into another's

```
Every form of Cell   4/4 canon, 24 returned, 17%
  junk: Super Saiyan, Super Saiyan 2, Super Saiyan Third Grade, Super Saiyan Full Power
```

Cell absorbs Saiyan cells, so his page discusses Saiyan forms; the extraction
attributes them to him. `validate_member` would reject them, since no field on
`Super Saiyan` names Cell as a user, but `_extracted_roster` skips validation by
design (`roster.py:1069-1080`).

**Fix:** this is the case for a per-member score. A row that only prose supports,
where the page it names does not name the character back, is the weakest class
of evidence in the system and is currently indistinguishable from the strongest.

## 6. Duplicate spellings are scored as intruders

`Every form of Cell` returns `Imperfect Form`, `Semi-Perfect Form`, `Perfect
Form` **and** their `…Cell` spellings. The aliases are in the bank, so the canon
item matches once, and the second spelling is then counted as a wrong name
(`canon_gold.py:148`, first alias wins).

This is arithmetic, not a retrieval error, but it costs real precision points on
the questions that have alias-rich golds. Deduplicating members by alias before
scoring would price it correctly.

---

## What to do, in order of measured value

1. **Never let a category answer a character question, and stop calling it
   `exact`.** ~420 intruders, and it is the only defect that produces
   confidently wrong answers.
2. **Apply `NEVER_MEMBERS` to category members.** Removes every battle page.
   Already the declared policy.
3. **Fix the match phrases** (singular/plural) and the five wrong `subject:`
   values. This is repairing my own work from this session.
4. **Widen `ability_stopwords` for One Piece** with the heading names.
5. **Per-member scoring**, which is Phase 2 of `PRECISION_PLAN.md` and the only
   durable answer to 83% single-source.

Nothing here needs a re-crawl or a re-extraction. Every fault is in how stored
evidence is selected, ranked and labelled.

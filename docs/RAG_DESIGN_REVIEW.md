# RAG design review

A 28-point improvement plan was raised against this engine after "Every Saiyan
transformation" returned Black Frieza. This document records what was found,
what was built, and what was already there, so the same ground is not covered
twice.

## The finding

The premise of the plan was that the engine answers by embedding similarity.
**Roster mode never touches the vector store.** It reads a category out of
SQLite and returns its members; there is no embedding, no chunk, no reranker
anywhere in that path.

Black Frieza appeared because **the Dragon Ball wiki files it under
`Transformations`** (correctly, it is one) and nothing downstream ever asked
the second half of the question: *is it Saiyan?*

That distinction decides the fix. If similarity were the cause, the answer would
be better embeddings, more candidates, query expansion, multi-query retrieval.
Because membership is the cause, the answer is a validator that reads structured
data already in the store:

| page | what the store already held, before any change |
|---|---|
| `Black Frieza` | categories `Transformations`, **`Frieza's race`**; `Users = Frieza`, `Inventor = Frieza` |
| `Super Saiyan Blue` | categories `Transformations`, **`Saiyans`**; `Users = Goku, Vegeta` |
| `Class-up` | `Debut = Game: Dragon Ball Heroes` |
| `Android 1617` | category `Fusion`; `Debut = Dragon Ball Fusions`; lead: *"Android 16 and 17's EX-Fusion form"* |

Two corrections worth recording:

* **The structured metadata asked for in point 2 already existed and was already
  extracted.** Race, owner, class, media and debut are in `facts` and
  `categories` today. Rejecting Black Frieza needed no re-crawl and no new
  extraction pass, only a stage that reads them.
* **`Android 1617` was not a retrieval error.** The engine inferred nothing; the
  wiki states it is an EX-Fusion of 16 and 17 from *Dragon Ball Fusions*. The
  legitimate complaint was canon, not correctness.

## What was built

`scriptengine/retrieve/roster.py`, between choosing a set and rendering it:

1. **`parse_constraints`** reads what the topic asked for beyond the set's
   name. "Every Saiyan transformation" resolves to the declared `Transformations`
   set; what is left is `saiyan`. Also reads scope: canon by default, everything
   when the topic says "ever", "including games", "non-canon".
2. **`_profile`** assembles each candidate from the store: categories, owners
   (`Users`, `Inventor`), identity fields, and media parsed from `Debut`, which
   already carries it verbatim.
3. **`_grounded`** keeps only qualifier words the wiki has an article about.
   This is what stops "Every Cursed Technique of Sukuna" from filtering on
   `cursed`: every technique on that wiki is cursed, the word is a genre, and
   enforcing it threw away Malevolent Shrine. `Saiyan` has an article and is a
   real constraint; `cursed` has none and is not.
4. **`validate_member`** rejects, with a reason: index pages (`List of …`),
   the set's own article (`Dragon Ball (object)` inside `Dragon Balls`),
   out-of-scope media, and members the qualifier does not reach. The qualifier
   is checked against title, categories and ownership fields, then, one graph
   hop later, against the owner's own race (`Super Saiyan Blue` → Goku → `Saiyan`).
5. **Never silently empty.** If validation would remove everything, the
   unfiltered set is returned. A visibly-too-broad list beats a blank one.
6. **Reported, not applied quietly.** Rosters carry `candidates`, `rejected`
   (name + reason) and `scope`; `cli query` prints them and `/context` returns
   them.

Deliberately matched to the request: **nothing is deleted**. Games, Heroes,
Xenoverse and Fusions stay in the store and come back when the topic asks for
them.

### Result on the three reported failures

| topic | before | after |
|---|---|---|
| Every Saiyan transformation | 150, incl. Black Frieza, Golden Frieza, Orange Piccolo | **75 of 160**, all three rejected as *"not saiyan"* |
| All types of Dragon Balls | 17, incl. `Dragon Ball (object)` | **15**, rejected as *"describes the set rather than belonging to it"* |
| Every Fusion | 110, incl. `Android 1617` | **93**, rejected as *"outside the story (Dragon Ball Fusions)"*; returns at `scope=all` |

Super Saiyan 1–4, God, Blue, Great Ape, Golden Great Ape, Ultra Ego and Kaio-ken
all survive; every non-Saiyan form is gone.

## The 28 points, mapped

**Already in the engine before this review**, verified, with the code:

| # | asked for | where it lives |
|---|---|---|
| 1 | intent classification | `looks_like_enumeration()`; modes roster / narrative / qa / auto |
| 3 | hybrid search | FTS5 BM25 + Qdrant, fused with RRF, in `retrieve/hybrid.py` |
| 4, 18 | dynamic strategy / tool selection | four modes chosen per topic shape |
| 5, 27 | recall, adaptive top-k | rosters return up to 150; qa returns 8 |
| 6 | cross-encoder rerank | `bge-reranker-v2-m3` |
| 9 | chunking by structure | section-driven, never fixed token counts |
| 11, 13, 16 | graph, relationships, recursion | ~1.2M resolved wikilink edges with named relations |
| 12, 14 | entities, ontology | discovered per wiki; 89–100% of pages typed |
| 22 | hierarchy | section tree with breadcrumbs and parent pointers |
| 23, 24 | canonical ids, aliases | `nodes`, `aliases`; `AltName` / `Alternate names` extracted |
| 26 | duplicate detection | `_distinct` on members, groups and categories |

**Added by this work**: 2 (metadata filtering), 15 (self-query), 19 (coverage
verification), 28 (confidence: `declared`/`exact`/`partial`/`weak`, plus
`candidates` and `rejected`).

**Deliberately not done, with reasons:**

* **7, 8, query expansion and multi-query.** These widen a *search*. A roster is
  a category read, so expanding "transformation" into form/evolution/power-up
  would not add a member, since the set is already the wiki's own list. Where
  vocabulary genuinely differs (`movie` vs `Films`, `Yonko` vs `Four Emperors`)
  it is declared in `overrides.yaml`, which is exact rather than probabilistic.
* **10, chunk summaries.** Real, but it affects `qa` mode embeddings, not any
  of the reported failures. Worth doing on its own merits, not as a fix for this.
* **20, 21, answer and citation validation by an LLM.** ScriptEngine retrieves;
  it does not generate. The writer is downstream, and `cli verify` already checks
  a finished script's citations against the raw crawl.

## The ability ontology

Validation initially kept **Kaio-ken** in "Every Saiyan transformation", because
Goku is a Saiyan and Goku uses it. That is the wrong test. King Kai invented
Kaio-ken and Krillin and Yamcha use it: it is a *teachable technique*, not
something a Saiyan body does.

So abilities are classified by **how they are acquired**, derived from data and
never declared per series:

| class | when | example |
|---|---|---|
| `race_exclusive` | the inventor *is* a race, or the wiki files it under one | Super Saiyan, Great Ape, Super Saiyan Blue, Beast |
| `character_specific` | exactly one user, and their race, until someone else has it | Ultra Ego (Vegeta) |
| `teachable` | users span races, or an inventor of another race taught it | Kaio-ken, `Ultra Instinct (technique)` |
| `unknown` | no users, no inventor, no race category | anything the wiki left bare |

A race qualifier then keeps only `race_exclusive` and `character_specific`
members of that race. Nothing here names a series: a word counts as a race if it
appears in a race field *and* has an article, which is how `Saiyan` qualifies on
Dragon Ball and `Quincy` or `Mink` would on their own wikis.

**The classification corrects itself.** Because it is computed rather than
stored, a second race acquiring an ability turns it from race-exclusive into
teachable with no code and no config touched. There is a test asserting exactly
that.

Two refinements the real data forced:

* **The wiki's own filing outranks inferred user races.** `Super Saiyan Blue` is
  filed under `Saiyans`; letting the Xenoverse avatar, who can be any race,
  vote turned it "teachable".
* **Game-only users do not vote**, for the same reason game-only members are out
  of canon scope.

### Result

`Every Saiyan transformation`: **160 candidates → 58**. Kaio-ken, Black Frieza,
Golden Frieza, Orange Piccolo and Great Namekian all rejected; Super Saiyan 1–4,
God, Blue, Great Ape, Golden Great Ape, Beast and Ultra Ego all kept. Across the
55-question answer sheet, **that one count moved and nothing else did.**

### Coverage is limited by each wiki's metadata

Verified, and worth being plain about:

| wiki | ability metadata | classifier |
|---|---|---|
| Dragon Ball | `inventor`/`user` edges, `Race` facts, race categories | works fully |
| Bleach, One Piece | `Sulong` has one category and **no infobox fields**; `Haki` likewise | degrades to no constraint |

Sulong cannot be computed Mink-exclusive today: the wiki says so in prose and
nothing structured records it. The classifier declines rather than guesses, so
those series are unchanged. Coverage improves when those pages carry more
structure, not by adding per-series rules here.

## The semantic type layer

A category is a filing decision; membership is a semantic one. Asked for the
members of the Galactic Frieza Army, the engine returned all 230 pages in that
category: 121 characters, but also 37 races, 24 techniques, 23 factions, 18
planets and 6 battles. **A planet is not a member of an army.**

The wiki already says what each page is, in the infobox it chose, which the
crawler stores as `page_type`. What it does not do is speak one vocabulary: a
character is `character` on Dragon Ball, `char_box` on One Piece,
`hunterpedia_character` on Hunterpedia, `bleach_wiki_character_arrancar` on
Bleach. `scriptengine/retrieve/semantics.py` folds those into one set of types
character, race, organization, location, technique, transformation, power_up,
(fusion, item, event, media) by matching **tokens inside the discovered id**
rather than a table of ids, so a new wiki is covered as soon as it names its
infoboxes in recognisable words.

A roster then takes its expected type from the majority of its own candidates,
and rejects the ones that disagree. Three rules keep it from over-reaching:

* **Abilities never reject each other.** Whether a page reads `technique` or
  `transformation` depends on whether an editor filled in a `Class` field, so
  letting the majority decide would have thrown out Super Saiyan for
  disagreeing with the techniques around it.
* **Organisations are never rejected.** Wikis reach for a group infobox for
  anything collective. `Angel` and `Shadow Dragon` are typed that way on pages
  about races, and rejecting them cost three real races to catch nothing.
* **A set without a clear majority is left alone**, rather than guessed at.

### Result, measured across the 88-question sheet

17 counts moved, every one inspected:

| set | before | after | what left |
|---|---:|---:|---|
| Galactic Frieza Army | 225 | **144** | planets, races, battle armour, conflicts |
| Every Demon | 192 | **151** | techniques, power-ups, races |
| Every member of the Royal Guard | 8 | **6** | `Ōken`, `Blood Oath's Seal`, both items |
| Every member of the Kurta Clan | 9 | **7** | `Lukso Province`, `Scarlet Eyes` |
| All types of Dragon Balls | 15 | **14** | `Nameless Planet` |
| Every Devil Hunter | 75 | **74** | `Tokyo Devil Detention Center` |

Sets that are already homogeneous (Devils, Espada, Warlords) did not move.

### Race qualifiers: two more structural tests

* **The wiki calls it a power-up and never a transformation** → rejected. Dark
  Dragon Ball Enhancement is granted by Dark Shenron and coexists with Super
  Saiyan; Evil Aura is the same shape.
* **Filed under three or more races and used by a crowd** → not intrinsic to
  any of them. Unlock Potential reaches Earthlings, Majin and Saiyans across 18
  users.

`Every Saiyan transformation` is now **160 → 50**, and of the ten wrong members
reported, seven are gone while every one of the ten that belong is kept.

### The four that structure cannot reach

**Spirit Bomb Super Saiyan, Culture Fluid Absorption, Powerhouse, Fusion of Ki**
and `Mutation` survive, because structurally they are identical to forms
that belong: `Class = Transformation`, filed under `Saiyans` alone. Telling them
apart needs "stacked on another form", "externally caused", "an energy state",
which no wiki field records. That is the boundary between structural and
semantic information, and the index-time classifier below is what is meant to
cross it.

One rule here is honestly weak: the crowd threshold is **twelve users**, chosen
because Golden Great Ape has 11 and Unlock Potential has 18 and nothing
structural separates them. It should be replaced, not tuned.

## Index-time semantic classification

Built: `scriptengine/ingest/classify.py`, `cli classify --series <name>`. The
reason it belongs at index time rather than query time is that retrieval must
stay deterministic, or the same question answers differently twice and the eval
sets stop being a regression guard.

```
wiki page → structured fields → deterministic rules
          → LLM classification (only where the rules are uncertain)
          → stored semantic metadata → retrieval reads the metadata
```

* Scoped to **ability-like pages the rules cannot settle**, a few hundred per
  wiki, not 23,656. A full-corpus pass is hours of local inference for no extra
  benefit.
* Emits **properties, not one label**: `race_exclusive`,
  `biologically_intrinsic`, `externally_granted`, `teachable`, `stackable`,
  `temporary`, `requires_artifact`, `requires_fusion`, so validation can
  compose them per question, plus a one-line **reason**, stored so a
  questionable classification can be argued with.
* **Cached on `documents.revid` and a prompt version**, so a page is
  reclassified only when it or the prompt changes.
* **May reject or annotate, never add.** A wrong property costs precision; it
  can never invent a member. `_semantic_reason` in `roster.py` reads the stored
  row and acts only on the disqualifying properties; a page the classifier never
  saw falls through to the structural rules untouched.

### How narrow the scope actually is

Ability pages only, minus the ones the wiki's own fields already settle, minus
the ones filed under no race at all. Those can never reach a race-qualified
answer, so classifying them buys nothing:

| series | pages to classify |
|---|---:|
| `db` | 88 |
| `bleach` | 14 |
| the other six | 0 |

88 rather than the 2,524 technique pages Dragon Ball holds, and 0 where a wiki
records no ability structure at all. Selection is in `needs_classifying`.

The store's `semantics` table is deliberately **not** dropped by
`FactStore.reset()`, and `ensure_semantics()` grows it in place on a store built
before it existed. Everything else in the schema is rebuilt by `index` and
cheap, this is the one thing that costs local inference.

### Measured

88 Dragon Ball pages and 14 Bleach pages, on a local 8B model, **about six
minutes per wiki**. `Every Saiyan transformation` went 50 → **43**, and across
the 88-question sheet **that one count moved and nothing else did**.

Of the twelve wrong members reported, **ten are now rejected** and all ten of
the forms that belong are kept:

| now rejected | why |
|---|---|
| Spirit Bomb Super Saiyan | *"granted externally by absorbing a Spirit Bomb, which requires an artifact"* |
| Powerhouse | *"can be learned by multiple users across races"* |
| Fusion of Ki | requires fusion |
| Culture Fluid Absorption | **still present** |
| Mutation | **still present** |

Two remain. That is the honest count: the classifier fixed three of the four
cases structure could not reach, and left one.

### What the first run got wrong, and what fixed it

The first prompt marked **Great Ape**, **Super Saiyan God** and **Beast** as
`externally_granted`, reading a full moon, a ritual and Piccolo's mentoring as
external grants, which would have thrown out three forms that belong. Two
changes fixed it, and both are worth keeping in mind for any future prompt:

* **`race_exclusive` outranks everything.** A form can need a trigger and still
  be something only one race's body does; only a Saiyan responds to a full moon.
* **The prompt now distinguishes a trigger from a grant**, and says that latent
  potential another character draws out is still intrinsic: the power was
  already theirs.

`PROMPT_VERSION` was bumped, which invalidated all 88 rows and reclassified
them, which is the cache-invalidation path working as intended.

### The rule this was meant to delete

The twelve-user threshold in `validate_member` is still there and still
arbitrary. It should now be removable, since the classifier judges the same
pages on better evidence, worth testing by deleting it and re-running the
evals.

## Audited against the web

Twelve answers were checked against canon sources rather than against the
engine's own confidence. **Six were right, six were wrong**, and every wrong one
came back `declared` or `exact`, the confidently-wrong failure mode, in a place
none of the previous work looked.

| question | was | canon | now |
|---|---:|---:|---:|
| Every God of Destruction | 168 | **12** | **12** |
| Every Chimera Ant Royal Guard | 64 | **3** | **3** |
| Every Hunter rank | Provisional/Unclassified/Amateur | Single/Double/Triple Star | **the star ranks** |
| Every member of the Espada | 24 | 10 seats | **18** |
| Every Vasto Lorde | 6, `Tier Harribel` twice | ~4 | **1, no duplicates** |
| Every member of the Phantom Troupe | 16, incl. Omokage | 13 seats | **15, Omokage rejected** |

The six that were right (Nen types 6, hero classes 4, God Hand 5, Primal Fears
4, Namekian transformations 2, Frieza Race transformations 4) are unchanged and
are now eval cases so they stay that way.

### Four defects, four fixes

**Subpages were counted as members.** `Tier Harribel` and `Tier
Harribel/Expanded Universe` are the same hollow. Across four wikis 504 titles
carry a slash and 97% have their parent in the store: alternate continuities,
anime-only variants, galleries. A title `X/Y` whose parent `X` exists is now a
view of `X`, not a member. This is the single largest correction: it also took
`Every Captain of the Gotei 13` from 27 to **13**, which is the number of
divisions, by removing fourteen `/Anime Continuity` variants.

**Films were canon everywhere.** Right for Dragon Ball (*Broly*, *Battle of
Gods*) and wrong for Hunter × Hunter, whose films are not. `canon_media:` is
now per series. The subtlety: Hunterpedia files its films under **`anime
debut`**, so the field text says anime; only the debut edge's *target*
(`Hunter × Hunter: Phantom Rouge`, page type `movie`) gives it away. Media is
now read from the instalment page's own type, not from the field string.

**Some sets the wiki never filed anywhere.** There is no Gods of Destruction
category, and Hunterpedia's `Royal Guards` page names its three only in prose.
A `members:` list in `overrides.yaml` names them, checked against the store so a
wrong name shows as a short roster rather than a silent gap, which is exactly
how `Mosco` was caught: this wiki titles him `Mule`.

**One declaration was simply wrong.** `Hunter Ranks` pointed at employment
status; `Single Star Hunters`, `Double Star Hunters` and `Triple Star Hunters`
already existed as categories.

## What is still wrong

* **Current versus former membership.** The Espada returns 18 where ten seats
  exist, because the wiki files everyone who ever held one in the same category.
  `Every member of the Straw Hat Pirates` returns 11 including Nefertari Vivi,
  whom One Piece files under `Straw Hat Pirates Members` and canon calls a
  former member. Nothing distinguishes current from historical.
* **A set that is incomplete rather than mismatched.** `Every island in the Grand
  Line` returns four and reports `exact`, because the name genuinely matches;
  the wiki files most islands elsewhere. Only the count reveals it.
* **Canon detection needs a `Debut` field.** Wikis that record debut differently
  get no media filter: the validator is only as good as the field, and it
  correctly does nothing when the field is absent.
* **Ability classification needs user and inventor links**, which Bleach and One
  Piece do not carry for abilities. See the coverage table above.

Fixed since the first version of this document: the Ultra Instinct
inconsistency (there is no page called `Ultra Instinct` at all,
`Ultra Instinct (technique)` is teachable and rejected, while the Goku-only
`True`/`Perfected` variants are character-specific and kept), and the 150-member
cap, now 300 with a `capped` count reported when it still bites. "Every
transformation ever" returns 159 where it used to silently return 150.

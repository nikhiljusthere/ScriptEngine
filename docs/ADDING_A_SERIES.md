# Adding a series

> Ingestion lands in Phase 1. This page documents the intended interface; the
> commands below will not run until then.

Adding a series should be a name and a URL. No Python, no schema, no alias table.

```powershell
python -m scriptengine.cli crawl --series csm --start-url https://chainsaw-man.fandom.com/wiki/Chainsaw_Man_Wiki
python -m scriptengine.cli audit --series csm
python -m scriptengine.cli index --series csm
```

The `--series` value is a short id used as the folder name under `series/`. Keep
it lowercase and filesystem-safe: `jjk`, `csm`, `jojo`, `dbz`, `marvel`.

## What happens on crawl

Nothing about the series is assumed. ScriptEngine asks the wiki what it contains:

1. **Enumerate pages** — `list=allpages` in the main namespace, following
   continuations.
2. **Discover the type vocabulary** — every template matching `*Infobox*` in the
   `Template:` namespace. Jujutsu Kaisen defines 20 (`Character Infobox`,
   `Battle Infobox`, `Episode Infobox`, `Technique Infobox`, `Story Arcs
   Infobox`, …). Chainsaw Man and Marvel define their own; whatever they are,
   they become that wiki's page types.
3. **Fetch each page** — rendered HTML, section tree, categories, transcluded
   templates, and raw wikitext, in one pass.
4. **Type each page** — by the infobox it transcludes, refined by its categories.

## Always audit before indexing

```powershell
python -m scriptengine.cli audit --series csm --sample 50
```

The audit reports what the extractor actually understood: pages by discovered
type, infobox coverage, facts per page, edges resolved versus dangling, sections
captured, citations extracted, pages rejected as non-content.

Index only once the audit looks right. Reading
[EXTRACTION_AUDIT.md](EXTRACTION_AUDIT.md) first is worth the five minutes —
indexing a corpus you have not audited is how the previous pipeline ended up
embedding Angular documentation alongside the wiki.

## When a wiki needs special handling

Put it in `series/<name>/overrides.yaml`. Never in a `.py` file.

```yaml
# series/marvel/overrides.yaml
skip_categories:
  - Disambiguation Pages
  - Images
type_aliases:
  "Character Template": character

# Which discovered page types a script is never about, and which it usually is.
# Both have defaults in `scriptengine/config.py` that work on any wiki using the
# common names; override when this wiki's types are called something else.
# Without the first list, "Every Rank of Curse in Jujutsu Kaisen" resolved to the
# series page and returned one beat from `Volume 0`.
subject_demote_types:
  - series
  - volume
  - issue
subject_type_priority:
  - character
  - event
  - location
```

### The roster registry

Most scripts are enumerations, and roster mode finds the set by scoring the
wiki's categories against the words in the topic. That works until the wiki's
word is not the viewer's word. One-Punch Man files its monsters under
`Mysterious Beings`, so "Every Monster" scored `Monster Association` (71) over
the real set of 219. Worse, a category named for the pages a wiki *could not*
classify wins by containing the query's words: "Every Nen Type" resolved to
`Unknown Nen type users`, 247 of them, instead of the six Nen categories.

So declare the sets that matter. A declared topic resolves the same way every
time; anything undeclared still goes through discovery.

```yaml
rosters:
  - name: Mysterious Beings
    match: [monster, monsters, mysterious being]
    category: Mysterious Beings
    group_by: level             # optional: an infobox field to group members by

  - name: S-Class Heroes
    match: [s-class hero, s class hero, s-class]
    category: S-Class

  - name: Nen Types
    match: [nen type, nen types, type of nen]
    groups:                     # the members ARE the groups
      Enhancer: Enhancers
      Transmuter: Transmuters
```

A set is backed by `category:`, `label:` (a discovered page type), or
`fact: {key, value}`. `groups:` is for a taxonomy — "Every Nen Type" wants the
six types, each with its users, not a flat list of 111 people.

Three rules worth knowing:

- **The longest matching phrase wins**, so declaring both `hero` and
  `s-class hero` sends the narrower topic to the smaller set. Declare compound
  phrases when two sets collide: `captain of the gotei 13` had to be spelled out
  or "Every Captain of the Gotei 13" answered with all 127 members.
- **A topic that names a person falls through to discovery**, because a declared
  set is a general one. "Every Cursed Technique of Sukuna" wants his eight, not
  all 38 innate techniques. The test is what the character contributes beyond
  the matched phrase, since these wikis name characters after the sets they
  belong to (`Devil Hunter`, `TV Junkyard Monster`).
- **Group by a field only when it has few repeated values.** Wikis qualify these
  in prose — Chainsaw Man writes `Devil (80%) Fiend (20%, formerly)` in
  `species` — so only the first clause is used, and a field where every member
  answers differently is an attribute rather than a tier.

Check what a series declares, and that every entry still returns members, with:

```powershell
python -m scriptengine.cli rosters --series opm
```

### The citation grammar

Every wiki invents its own, and the difference decides whether a script can put
a chapter on a line at all. Five wikis crawled, five grammars, none of them the
same as Jujutsu Kaisen's. The mechanism is generic; the vocabulary goes here.

| Key | For | Example |
|---|---|---|
| `citation_works` | a flag saying which work the number belongs to | `{{Ref\|modulo=y\|chap=16}}` → `(Modulo Chapter 16)` |
| `citation_instalments` | a parameter that *is* the instalment | `{{Ref\|movie=0}}` → `(Movie 0)` |
| `citation_params` | this wiki's parameter names | `{{ref\|ch=20}}` → `(Chapter 20)` |
| `citation_positional` | references with no named parameters | `{{Ref\|m\|216\|3-4}}` → `(Chapter 216)` |
| `citation_ref_tags` | a locator written as prose in an HTML `<ref>` | `<ref>''Bleach'' manga; Chapter 686</ref>` → `(Chapter 686)` |

```yaml
# One-Punch Man: a webcomic and a manga, numbered separately.
citation_params:
  ch: {as: chapter}
  wch: {as: chapter, work: Webcomic}
  p: {as: page}

# Chainsaw Man: no named parameters at all. The first argument picks the
# medium, the second holds the number.
citation_positional:
  select: 0
  number: 1
  mediums:
    m: {as: chapter}
    a: {as: episode}

# Bleach, Hunterpedia, Berserk: the locator is prose inside <ref>. Rules are
# tried in order and the first match wins; anything unmatched renders nothing,
# which is right for the interviews and cover art these wikis also cite.
citation_ref_tags:
  - match: 'anime,?\s*Episode\s+([\d.\-]+)'
    as: episode
  - match: 'Chapter\s+([\d.\-]+)'
    as: chapter
```

`as` is `chapter`, `episode`, `volume` or `page`; `page` is recognised so it can
be dropped on purpose, because a page number inside a sentence is retrieval
noise. `work` prefixes the label when a wiki numbers two works separately.

**Why this is not optional.** Before the grammar existed, Chainsaw Man's 2,946
references rendered as nothing and the series scored 0.0% sourced prose, while
Bleach and Hunterpedia's `<ref>` bodies survived into the text and landed inside
the sentence they were citing: *"Ichigo fights. Bleach anime, Episode 179 He
wins."* That is bibliography in the embeddings, which is the failure that killed
the previous pipeline. `audit` reports `cited directly`, `sentences w/ chapter`
and `sentences w/ episode` so a new wiki tells you which of these it needs.

Marvel is the expected hard case: `Spider-Man` is a disambiguation page, and the
wiki uses `Module:PageType` and reality variants where JJK uses a plain infobox.

The rule is simple. **If a fix mentions a series name and lives in Python, it is
in the wrong place.** The moment series logic enters the code, the next wiki
breaks.

## Disk

Each series is self-contained under `series/<name>/`:

```
raw/          rendered HTML, one file per page
wikitext/     wikitext + API metadata, one JSON per page
facts.db      SQLite: facts, graph, FTS5 index
vectors/      Qdrant local storage
manifest.json what was crawled, when, from where
audit/        extraction reports
obsidian/     exported Obsidian vault, regenerated by `export`
overrides.yaml optional, only if the wiki needs it
```

Everything but `manifest.json` and `overrides.yaml` is gitignored and
regenerable. Delete the folder to remove a series; copy it to move one.

## Be a good citizen

The crawler runs 10 concurrent workers with a 0.2 s delay and honours HTTP 429
`Retry-After`. That pacing pulled ~850 JJK pages without trouble. Raising
`SCRIPTENGINE_CRAWL_CONCURRENCY` is not encouraged — Fandom is a free host, and
the polite settings are also the ones that do not get you blocked.

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
```

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
overrides.yaml optional, only if the wiki needs it
```

Everything but `manifest.json` and `overrides.yaml` is gitignored and
regenerable. Delete the folder to remove a series; copy it to move one.

## Be a good citizen

The crawler runs 10 concurrent workers with a 0.2 s delay and honours HTTP 429
`Retry-After`. That pacing pulled ~850 JJK pages without trouble. Raising
`SCRIPTENGINE_CRAWL_CONCURRENCY` is not encouraged — Fandom is a free host, and
the polite settings are also the ones that do not get you blocked.

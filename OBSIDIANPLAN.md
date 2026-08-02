# OBSIDIANPLAN.md

Export the ScriptEngine wiki graph to an Obsidian vault so it can be explored in
Obsidian's graph view. Read-only over the existing SQLite store — no changes to
ingestion, retrieval, or the schema.

Status: **planned**. Execute when ready.

## Why it works

Obsidian's graph view is built from markdown files containing `[[wikilinks]]`.
ScriptEngine already stores exactly that shape as directed, typed edges in
`facts.db`:

```
nodes   = page titles + every wikilink target (resolved or not)
edges   = infobox relations (confidence 0.95) + prose mentions (0.4)
facts   = infobox parameters, stored as data (exact lookups)
aliases = names a page is known by (redirects + harvested link display text)
```

Verified example from `series/jjk/facts.db` (34,546 edges):

```
Boogie Woogie -user-> Aoi Todo            (0.95, infobox)
Boogie Woogie -type-> Cursed Technique    (0.95, infobox)
Boogie Woogie -debut-> Chapter 35         (0.95, infobox)
Chapter 35 -cover-> Aoi Todo              (0.95, infobox)
Aoi Todo -affiliation-> Kyoto Metropolitan Curse Technical College
```

Real-world graph shape: `Cursed Technique` is a hub that 40+ technique pages
point at via `type`; each technique page points at its users via `user`;
characters connect to each other transitively through organisation nodes
(`affiliation`); chapters point at characters (`cover`, `new character`,
`mentions`). 653 nodes are unresolved links (never-crawled pages, interwiki
links like `Fr:Boogie Woogie`) and must be marked as stubs.

## Deliverables

### 1. `scriptengine/export.py` (new module)

`export_obsidian(paths, out_dir, min_confidence=0.4, include_documents=True)`

- Reads `facts.db` through the existing `FactStore` (read-only).
- Queries: all nodes, all edges (join source/target names), all facts, all
  aliases.
- `min_confidence` filters edges: 0.4 = the full graph (structural core + mention
  web, the 34,546 edges), 0.95 = clean infobox-only graph.
- Filenames: reuse `sanitise_filename` from `ingest/crawler.py`; build a
  collision map so every `[[Name]]` resolves to exactly one file; rewrite links
  to the collided filename when needed.
- Unresolved nodes (`is_resolved = 0`) → stub files with `resolved: false`.
- Returns a small report dict (counts, path) for the CLI.

### 2. Vault layout — `series/<name>/obsidian/`

```
obsidian/
  README.md        # "Open as vault" instructions
  nodes/           # one file per node — the graph
    Aoi Todo.md
    ...
  documents/       # one file per document — readable pages
    Aoi Todo.md
    ...
```

**Node file** (`nodes/Aoi Todo.md`):

```markdown
---
type: character
aliases:
  - Todo
  - Todo Aoi
resolved: true
grade: Grade 1
affiliation: Kyoto Metropolitan Curse Technical College
---

# Aoi Todo

## Relations

- [[Boogie Woogie|user]]
- [[Yuji Itadori]]
- [[Chapter 35|cover]]
```

- frontmatter: `type`, `aliases`, facts as properties (label or key: value),
  `resolved`
- body: one `- [[Target]]` bullet per edge; typed relations rendered as
  `[[Target|relation]]`, `mentions` plain
- citation attached where a fact has one (as a comment or a `_citation` field)

**Document file** (`documents/Aoi Todo.md`):

```markdown
---
type: character
url: https://jujutsu-kaisen.fandom.com/wiki/Aoi_Todo
grade: Grade 1
---

# Aoi Todo

## Abilities and Powers

prose with [[wikilinks]] re-inserted...
```

- frontmatter: type, url, facts (with citations)
- sections as `##` headings (breadcrumb order, skipping boilerplate sections
  like References/Gallery)
- wikilinks re-inserted into prose: sections keep their original wikitext in
  the crawl JSON; use each section's parsed `links` and replace display text
  with `[[target|display]]`
- lead paragraph first

### 3. CLI — new `export` command in `cli.py`

```powershell
python -m scriptengine.cli export --series jjk
# optional: --min-confidence 0.95   (default 0.4)
# optional: --out <dir>             (default series/<name>/obsidian/)
```

Prints: nodes written, documents written, unresolved stubs, vault path.

### 4. `tests/test_export.py`

Mirror the temp-dir fixture pattern from `test_stores.py`:

- builds a tiny FactStore with a few nodes/edges/facts/aliases
- asserts: node + document files exist; every `[[link]]` in a file resolves to
  a file in the vault; frontmatter contains aliases + facts; unresolved nodes
  marked `resolved: false`; `min_confidence` drops `mentions` edges.

### 5. Docs

- `README.md` Use section: one `export` line.
- `CLAUDE.md` Commands: one `export` line.
- `docs/ADDING_A_SERIES.md` disk layout note (optional).

## Execution order

1. `scriptengine/export.py`
2. CLI command in `cli.py`
3. `tests/test_export.py` — run `python -m pytest tests/test_export.py -q`
4. Run `python -m scriptengine.cli export --series jjk` (then again with
   `--min-confidence 0.95` if the full graph is too noisy)
5. Launch Obsidian with `series/jjk/obsidian/` as the vault
6. Update README + CLAUDE.md

## Notes / risks

- 1,626 nodes / 984 documents / 34,546 edges for jjk — export is a few seconds
  at most, but keep the per-file edge list capped (e.g. 500 edges per node file)
  so no single file explodes (huge mentions hubs like `Yuji Itadori`).
- Windows-invalid characters in titles are already handled by
  `sanitise_filename`; collision suffix must be deterministic across runs.
- Obsidian resolves `[[Name]]` by exact filename; aliases in frontmatter make
  backlinks work for alternate names.
- Edge direction is preserved in link text; Obsidian graph arrows are
  configurable in graph settings.
- Obsidian must not be running on the vault while it is being regenerated
  (it watches files; regenerate with Obsidian closed or accept the refresh).

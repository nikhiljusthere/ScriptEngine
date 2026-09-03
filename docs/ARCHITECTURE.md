# Architecture

## The premise

A Fandom wiki is not a pile of prose. It is a database that happens to render as
prose, and the MediaWiki API will hand you the database.

Everything else here follows from taking that seriously. The previous pipeline
did the opposite. It rendered pages to text, then spent ~3,700 lines trying to
reconstruct entities and relationships from that text using NER, regex, and
hand-maintained lists of Jujutsu Kaisen character names. ScriptEngine reads the
structure directly and never destroys it.

## Data flow

```
                        MediaWiki API
                             │
      ┌──────────────────────┼──────────────────────┐
      │                      │                      │
  action=parse         action=query            action=query
  prop=sections        prop=revisions          list=allpages
       categories      rvslots=main            list=categorymembers
       templates       (raw wikitext)          (enumeration)
       text
      │                      │                      │
      └──────────────────────┼──────────────────────┘
                             ▼
                      ingest/crawler.py
                 series/<name>/wikitext/*.json
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
      ingest/ontology.py            ingest/wikitext.py
   page types from infobox       infobox → facts
   templates + categories        [[links]] → edges
   (no series-specific code)     {{Ref}} → citations
                                 sections → structure
              └──────────────┬──────────────┘
                             ▼
                      index/build.py
              ┌──────────────┴──────────────┐
              ▼                             ▼
         facts.db (SQLite)            vectors/ (Qdrant local)
   documents, sections, nodes,       chunk embeddings
   edges, facts, chunks_fts (BM25)   bge-large-en-v1.5
               └──────────────┬──────────────┘
                              ▼
        retrieve/  hybrid + narrative + roster (+ battles-in)
          vector ∪ BM25 ∪ graph → RRF → cross-encoder → ordered
          citations.py resolves chapter → episode for every beat/member
                              ▼
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
        api/main.py       cli.py (Typer)      mcp/server.py
            :8000         script-gen/verify   research / verify_script
              │                 │             / script_path  (stdio)
              └─────────────────┼──────────────────┘
                                ▼
                     build_context + render_prompt
                     (one implementation, three doors)
                                ▼
        writer model → prose → verify tags against raw crawl
                        → length band (target ± 500) → saved file
```

The three doors are the same code. `build_context` and `render_prompt` in
`scriptengine/api/context.py` assemble the bundle; the HTTP endpoint, the CLI's
`script-gen`, and the MCP `research` tool all call them rather than re-implementing
the logic. That is why a fix to retrieval or sourcing reaches every client at once,
and why there is no second copy of the writing rules to drift. The writing loop in
`scriptengine/script/writer.py` sits downstream of all three: it takes the bundle,
asks the writer model for prose, checks every chapter/episode tag against the raw
crawl (repairing failures), and expands or trims until the draft lands within 500
words of the target before saving.

## Why the structure survives

The load-bearing decision is that **facts are stored as facts**, not flattened
into prose and re-extracted later.

An infobox parameter like `|affiliation = [[Kyoto Metropolitan Curse Technical College|Kyoto Jujutsu High]]`
becomes three separate things, each in its proper place:

1. a **fact**: `(Aoi Todo, affiliation, Kyoto Metropolitan Curse Technical College)`
2. an **edge**, from the `Aoi Todo` node to the `Kyoto Metropolitan…` node, with
   provenance and a confidence score
3. a **prose card**, a compact rendering, embedded so that semantic search can
   still reach it

Only the third of those is a chunk. The first two are queryable directly, which
is what makes `/facts/{entity}` exact rather than approximate.

Crucially, the wikilink target is already canonical. `[[Kyoto Metropolitan Curse
Technical College|Kyoto Jujutsu High]]` tells you the display name *and* the page
it resolves to. No entity resolution, no alias table, no NER: for the factual
backbone. spaCy remains available for prose-only relations, but it is a booster,
never a dependency.

## Store choices

**SQLite** holds documents, sections, nodes, edges, facts, and the FTS5 index.

- No daemon. The previous design needed Neo4j and Qdrant running in Docker; the
  Docker daemon was not even installed on the target machine.
- Schemaless labels. Every series brings different entity types. JJK has
  `Technique` and `Story Arcs`, Marvel has realities and appearances. A node's
  label is data, not DDL, so a new series needs no migration. This is why
  SQLite beat Kuzu, which would require a table per label.
- FTS5 gives BM25 on disk. The previous retriever scrolled every chunk out of
  Qdrant into RAM and rebuilt a `rank_bm25` index *per process start*.
- One file per series. Copy it, delete it, back it up.

**Qdrant in local mode** holds vectors, with the same client API as the server, no
process to manage.

Graph traversal uses recursive CTEs. At the scale of a wiki (~850 pages, tens of
thousands of nodes) this is instant, and it removes an entire class of failure:
the old Cypher used `[r*1..$depth]`, a parameterised variable-length bound that
Neo4j rejects outright.

## Retrieval

The hybrid shape is inherited from the previous code, which had it right:

1. link entities in the query against the alias table, **word-boundary matched**,
   not substring, so `Ryu` no longer matches inside `Ryomen`
2. expand through the graph to related entities
3. vector search (Qdrant), lexical search (FTS5 BM25), graph-adjacent chunks
4. fuse with Reciprocal Rank Fusion, `k=60`
5. rerank with `bge-reranker-v2-m3`
6. expand each surviving chunk to its parent section for context

BM25 is not optional. Character and technique names are exactly the queries where
dense retrieval is weakest and lexical matching is strongest.

### Narrative retrieval

Relevance ranking answers questions. It does not write scripts.

Asked about the Shibuya Incident, a QA retriever returns the eight most similar
fragments in similarity order. A script needs the event **in sequence**: what
happened, to whom, in what order, and what it caused. `retrieve/narrative.py`
walks chronology edges (chapter, episode, volume, and arc ordering extracted
during ingestion) and returns ordered beats with participants and outcomes.

This is the capability the previous pipeline had no path to, and the reason
ScriptEngine is not just a wiki chatbot.

### Roster retrieval

A third shape answers enumeration: "Every Rank of Curse", "Every Apostle". A
reranker returns the eight most interesting members out of twenty-two; a roster
returns all twenty-two in the order the wiki files them. `retrieve/roster.py`
reads the set from whatever structure states it — a category, a union of
categories, the sections of one page, a discovered page type, or the distinct
values of an infobox field — and validates each member against the topic's own
constraints before returning it.

The battles-in path is the same idea turned around: instead of listing the
members of a set, it lists every battle page a fighter appears on, reading the
sides from this wiki's own infobox vocabulary (`side1`/`powers1`, `combatant1`/
`abilities1`) and labelling each fight with whether they were a direct combatant
or a deployed tool. Nothing here names a series; the field names come from the
wiki, so the path works on any corpus that files its fights as pages.

## Models and VRAM

| Role | Model | Size |
|---|---|---|
| Embedding | `BAAI/bge-large-en-v1.5` | ~1.3 GB |
| Reranking | `BAAI/bge-reranker-v2-m3` | ~2.2 GB |
| Generation | remote, via Ollama or LM Studio | not resident |

ComfyUI and a resident LLM cannot share VRAM on this machine. So ScriptEngine's
models load on first use and unload after `model_idle_unload_seconds`, and
`device: auto` degrades to CPU rather than failing. The previous code hardcoded
`device="cuda"` in five places, which would have raised immediately. The
installed torch is a CPU-only build.

Generation is deliberately not in-process. The previous step loaded
Qwen2.5-7B through `transformers` alongside the embedder and reranker, competing
for the same GPU. ScriptEngine speaks HTTP to whatever model is already loaded.

## Per-series configuration

There is none by default, and that is the point: a series is a name and a URL.

When a wiki genuinely needs special handling, it goes in
`series/<name>/overrides.yaml`, never in Python. Marvel is the expected case:
its pages use `Module:PageType`, reality variants, and disambiguation pages where
JJK has none.

The rule: **if a fix mentions a series name and lives in a `.py` file, it is in
the wrong place.**

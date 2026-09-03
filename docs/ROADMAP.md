# Roadmap

What ScriptEngine is trying to become, and where it currently stands. The
phase table below is the canonical status list (also mirrored in
`README.md`'s Roadmap section). This document adds the narrative behind the
open phases and what comes after phase 21.

## The goal

Serve ordered, cited, structured knowledge from any Fandom wiki to whatever
writes a video script, without a line of series-specific code. The pipeline
should scale to a new series by pointing it at a URL and, at most, describing
that wiki's citation grammar in `overrides.yaml`. Everything else (page
types, relationships, sections, sources) should come from the wiki's own
structure.

## Phase status

| Phase | Work | Status |
|---|---|---|
| 0 | Rename, restructure, drop Docker, retire the dead stack | done |
| 1 | Wikitext-first ingestion: ontology discovery, infobox and wikilink extraction | done |
| 2 | SQLite fact/graph/FTS5 store, Qdrant local vectors, section-driven chunking | done |
| 3 | Hybrid retrieval, narrative ordering, gold eval set | done |
| 4 | FastAPI service, Electron UI wired to it | done |
| 5 | Fresh crawl, extraction audit, iterate until coverage plateaus | done |
| 6 | Prove universality on Chainsaw Man and Marvel with no new code | in progress (Chainsaw Man done; Marvel untested) |
| 7 | Graph-driven abilities endpoint (`/abilities`), ComfyUI answer workflow | done |
| 8 | Direct AI script-writing path: `STARTME.md`, `script_writer.ps1`, house style guide | done |
| 9 | Subject resolution, roster mode, per-sentence sourcing, rules served with context | done |
| 10 | Five more wikis, and the per-wiki citation grammar each needed | done |
| 11 | Dragon Ball and One Piece, cite mode, generated catalogue | done |
| 12 | Batched crawling (50 pages/request), type-level pruning | done |
| 13 | Enumeration scored against the wikis: series-name defect fixed, new sources, eval sets | done |
| 14 | A roster reports how well it matched, instead of looking certain when wrong | done |
| 15 | Membership validation: candidates checked against topic constraints, canon by default | done |
| 16 | Ability ontology: race-exclusive vs teachable vs character-specific, self-correcting | done |
| 17 | Semantic types: a set admits only what it's made of | done |
| 18 | Index-time semantic classification for what structure can't settle | done |
| 19 | Audited against canon sources: subpage folding, per-series canon media | done |
| 20 | Tell a current set member from a former one (e.g. Espada: 18 pages, 10 seats) | open |
| 21 | Detect an *incomplete* set: name matches exactly, category barely filled | open |
| 22 | MCP server (`scriptengine/mcp/server.py`): `research`, `verify_script`, `script_path` over stdio, wrapping the same functions the API serves | done |
| 23 | CLI script-writing loop: `script-gen` (route → fetch → write → verify tags → repair) and `verify` as first-class commands | done |
| 24 | Battles-in roster mode: a fighter's whole fight list, per-fight role read from the wiki's own infobox vocabulary | done |
| 25 | Length-band enforcement (target ± 500 words) and title normalization so filename ≡ content and a rewrite reuses its folder | done |

## What's open right now

**Phase 5, extraction audit (done).** Three data-integrity bugs were fixed by
auditing the JJK crawl: citations captured but never rendered into prose, the
three main character pages skipped by an over-broad maintenance-banner filter,
and 845 junk `:Category:` edges from a defeated namespace check. The phase closed
when a fresh crawl's audit plateaued with no further silent extraction failures;
Jujutsu Kaisen now scores 24/24 on its gold set.

**Phase 6, universality proof.** Eight wikis are indexed and typing above 90%.
Chainsaw Man is done; Marvel is a legacy wiki using Lua modules
(`Marvel Database:Character Template`) that structural discovery should reach
but hasn't been re-tested since that landed. This phase closes when a wiki
with a meaningfully different template convention is onboarded with zero new
Python, only an `overrides.yaml` entry for its citation grammar.

**Phases 22–25 (done).** The engine now reaches the writer through three doors:
the HTTP API on :8000, the Typer CLI (`script-gen`, `verify`, and the rest of the
pipeline as commands), and an MCP server that exposes `research`, `verify_script`
and `script_path` over stdio so an agent host can drive it without a running
server. All three wrap the same functions, so there is one implementation to keep
correct. The writing loop gained two guarantees: every chapter/episode tag is
checked against the raw crawl before a script is called done (with repair passes
for failures), and length is enforced as a band of target ± 500 words rather than
a hope. Roster mode also learned to answer "every fight X has been in" by reading
the wiki's own battle infoboxes, per-fight role included.

**Phase 20, current vs. former membership.** Sets like the Espada hold more
pages than seats because departed/replaced members keep their page. Needs a
way to read "current" from the wiki's own signals (infobox status fields,
narrative timeline) rather than hardcoding per-series logic.

**Phase 21, incomplete-set detection.** A set can score `exact` on name
match while the wiki's own category coverage is thin (`Grand Line Islands`
has four members and reports `exact`). The membership-validation work in
phase 15 catches wrong sets, not thin ones. This needs a coverage signal
independent of match confidence.

## Beyond phase 21: longer-term direction

Not yet phased, but the direction the project is heading once the above
close:

- **More wikis, zero new code.** Each series added so far has needed only a
  citation-grammar description. The real test of the "no series-specific
  Python" claim is volume: keep adding wikis and watch for the first one
  that breaks the pattern.
- **Tighter roster confidence signals.** Phases 14, 15, 20, and 21 are all
  variations on the same question ("how much should a caller trust this
  set?") and could eventually collapse into one confidence model instead of
  four separate checks.
- **Reduce dependence on manual `overrides.yaml` authorship.** Right now a
  human describes each wiki's citation grammar by hand. Long-term, part of
  that description could plausibly be inferred the same way page types are.

## Where a design decision belongs

The rule that governs every phase above: **if a fix mentions a series name
and lives in a `.py` file, it is in the wrong place.** Per-wiki quirks go in
`series/<name>/overrides.yaml`. This roadmap should never gain a phase whose
implementation violates that rule. If one does, the phase needs rethinking,
not the rule.

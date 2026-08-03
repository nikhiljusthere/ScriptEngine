# The corpus, the indices, and how pages get here

Eight wikis, 23,656 pages, 119 declared enumeration sets. This is the report on
what was built, what broke on the way, what actually happens when a page is
pulled through the MediaWiki API, and why the crawler now asks for fifty pages
at a time instead of one.

`docs/RETRIEVAL_SCENARIOS.md` is the companion: ten real enumeration questions
put to the two largest wikis, eight of which came back wrong, and what that
exposed.

Numbers here come from `docs/CATALOGUE.md`, which is generated from the live
stores by `python -m scriptengine.cli catalogue`. If the two disagree, the
catalogue is right and this document is stale.

---

## 1. The eight series

| series | wiki | pages | typed | prose → chapter | → episode | instalment pages | rosters |
|---|---|---:|---:|---:|---:|---:|---:|
| `db` | dragonball | 8,052 | 89% | 3% | 8% | 0 | 14 |
| `onepiece` | onepiece | 7,613 | 94% | 0% | 0% | 2,603 | 14 |
| `bleach` | bleach | 2,126 | 95% | 34% | 1% | 0 | 19 |
| `hxh` | hunterxhunter | 2,014 | 96% | 50% | 1% | 455 | 13 |
| `opm` | onepunchman | 1,565 | 98% | 30% | 21% | 263 | 17 |
| `jjk` | jujutsu-kaisen | 987 | 99% | 55% | 37% | 393 | 16 |
| `berserk` | berserk | 762 | 90% | 0% | 0% | 451 | 11 |
| `csm` | chainsaw-man | 537 | 97% | 42% | 8% | 268 | 9 |

Each series is a self-contained folder under `series/`: its own SQLite fact
store, its own Qdrant collection, its own manifest, its own `overrides.yaml`.
Delete the folder and the series is gone; copy it and the series moves. Nothing
is shared between them except the code — which is the rule that keeps the
engine from becoming eight special cases wearing a trench coat.

### The indices are not one index

Every series gets four retrieval paths over the same store, and a query picks
between them (`--mode auto`, or forced with `qa` / `narrative` / `roster`):

* **`qa`** — hybrid BM25 + vectors, fused with RRF, reranked. For "how" and
  "why" questions.
* **`narrative`** — story order rather than relevance order. A question about
  the Shibuya Incident wants the beats in sequence, not the six best-matching
  paragraphs.
* **`roster`** — enumeration. "Every Division of the Gotei 13" is not a search
  problem, it is a *set* problem, and a reranker will happily return the eight
  most interesting divisions out of thirteen.
* **`auto`** — picks by the shape of the question.

The graph is the fourth path and it underlies the rest: over a million resolved
wikilink edges across the eight series, taken from the wikitext where they are
canonical rather than reconstructed from prose with an NER model.

### Per-wiki classifiers

The types are discovered from each wiki's own infoboxes, not declared by us —
89–99% of pages get typed, into whatever taxonomy the wiki actually uses. What
*is* declared, per series, is the vocabulary that matters for enumeration:

* `csm` — devils, fiends, hybrids, Public Safety divisions
* `opm` — monster threat levels (Wolf → God), hero classes and their ranks
* `bleach` — Shinigami, Arrancar, Quincy, Hollow, and the **sub-divisions
  inside them**: all thirteen Gotei 13 divisions individually, the Espada, the
  Sternritter
* `berserk` — Apostles, **Pseudo-Apostles as a distinct set**, the God Hand,
  the Band of the Hawk
* `hxh` — Nen categories, Phantom Troupe, Chimera Ants, Zodiacs
* `jjk` — curse grades, cursed techniques, sorcerer ranks, the Disaster Curses
* `db` — Saiyans, Frieza's forces, Androids, Gods of Destruction, transformations
* `onepiece` — Devil Fruits by class, the pirate crews, Marines by rank, the
  Worst Generation

That is 119 declared sets, and the point of declaring them is that a set has a
*correct size*. `cli rosters --series bleach` lists each one with its member
count, so an enumeration script can be checked against a number rather than
against a vibe.

Declaring a set is also how a wiki's vocabulary is bridged to a viewer's: Dragon
Ball files its movies under `Films`, and nothing scores "movie" onto that name.
Sets can be declared four ways — a category, a union of categories, the sections
of a single page, or a grouping of an infobox field — and which one a series
needs is a fact about that wiki, not a preference.

### Sourcing: two independent routes to a citation

A script line is worth nothing without a chapter or episode on it, and there
are exactly two ways to get one:

1. **The wiki cites its own prose.** JJK footnotes 55% of its sentences. Read
   the `{{Ref}}` and you have the locator.
2. **The wiki writes one page per instalment.** One Piece footnotes *nothing* —
   0% — but has 2,603 pages titled `Chapter 1015` and `Episode 957`. The title
   *is* the citation.

Route 2 was built because route 1 alone declared One Piece unsourceable, which
was false. Berserk has neither — 0% inline refs, and its 451 instalment pages
still leave most prose unsourced, because that wiki cites cover art. That is a
fact about the wiki, and the catalogue reports it as 0% rather than hiding it
behind a dash.

Dragon Ball and Bleach show **zero** instalment pages despite having thousands
of chapters, because they title chapter pages by name — `...And into the Fire!`
— not by number. Nothing is broken there; the route simply does not apply.

### Pruning what a script will never cite

A wiki is crawled whole and filtered afterwards, because you cannot tell from
`allpages` what a page is. That leaves real weight in the corpus that no script
will ever use: video game entries, soundtrack and single pages, dub credits,
publisher and staff stubs. Each one still costs a slot in the fact store and a
point in the vector index, and each one is a chance for a retriever to return a
CD track listing when asked about a fight.

`cli prune --series <name>` removes them, driven by `prune_types` in that
series' `overrides.yaml` — the only place a series-specific decision is allowed
to live. Matching is by type *family*, so pruning `song_box` also removes
`song_box_other_versions`. Nothing is lost permanently: `crawl --refresh`
brings the pages back.

| series | before | pruned | after |
|---|---:|---:|---:|
| `db` | 9,242 | 1,190 | 8,052 |
| `onepiece` | 7,937 | 324 | 7,613 |
| `bleach` | 2,248 | 122 | 2,126 |

Dragon Ball loses the most by a wide margin, which is exactly what its wiki
looks like: it carries decades of video games, and `cvg` alone is most of that
1,190. Pruning changes the stored wikitext, so it is followed by `audit` and
`index` — until those run, the store still holds the pages that were removed.

---

## 2. Problems, and how each was tackled

The pattern worth noting: nearly every one of these was found by running the
tool against a wiki it had not seen before. None of them were found by reading
the code.

**The Modulo bug.** `{{Ref|modulo=y|chap=16}}` rendered as `(Chapter 16)` —
427 references pointing a reader at the wrong series, because Modulo restarts
its numbering at 1. Fixed with a `CitationGrammar` carrying per-wiki flags, and
the vocabulary lives in `overrides.yaml`. Every series that renumbers from 1
now carries a work qualifier: Z / Super / GT / Daima / Kai / Heroes, Manga vs
Anime, Webcomic vs Manga.

**The sentence splitter never fired after an inline marker.**
`.(Chapter 145, Episode 50) Next` merged two sentences into one, so a locator
bled onto a claim it did not cover. Fixed in `_SENTENCE_BREAK` with a `tail`
group.

**Episodes silently lost their work qualifier.** Berserk's `(Anime Episode 1)`
had been broken since the day it was declared and nobody could see it, because
Berserk sources 0% of its prose — the code path never ran on real data.

**`cli verify` gave false failures three separate times**, each on a wiki it had
not met:
* it keyed off `page_type == "chapter"`, and Chainsaw Man types its chapter
  pages `unknown`;
* it regexed `"Chapter 22, 23, 24, 25"` and caught only the first, reporting
  three correct tags as invented — fixed by reading MediaWiki's already-resolved
  link edges instead of parsing infobox text meant for humans;
* it required a reference to cite the chapter, and One Piece cites nothing — so
  page existence is now the evidence, and a missing reference is only an issue
  when the page is missing too.

**The roster matcher was too broad, twice.** The first `_names_a_character`
broke "Every Public Safety Devil Hunter" and "Every Monster". The version that
shipped tests what a phrase contributes *beyond the whole series' set
vocabulary*, rather than against a hardcoded list.

**A registry entry hijacked a query.** Declaring `cursed technique` as a JJK
roster made "Every Cursed Technique of Sukuna" return all 38 innate techniques
in the series. Caught because the eval dropped from 24/24 to 23/24 — which is
the entire argument for keeping a regression eval that a change has to move.

**`FactStore.counts` crashed** with `no such table: categories` against the
older Dragon Ball index. Made tolerant of missing tables rather than requiring
a reindex.

**Rate limiting was self-inflicted.** A test crawl was running alongside the
background crawl — two clients, one IP. The background crawl on its own took
zero 429s across ~8,500 pages. It cleared without intervention and no VPN was
needed.

---

## 3. What actually happens when a page is pulled

The crawler never scrapes HTML. Every stage below is the MediaWiki API.

**Enumerate.** `list=allpages` walks the main namespace in pages of 500 and
returns every article title. This is the query Fandom throttles first — it is
the expensive one — and it runs once per wiki. No link-following: `allpages`
already has everything, so crawling links only rediscovers queued pages.
Wikilinks are still collected, but as graph edges, not as a frontier.

**Fetch, fifty at a time.** Titles are drained from the queue in batches of 50
and requested with `action=query&prop=revisions|categories|templates`,
`rvprop=content`, `rvslots=main`. One HTTP request returns fifty pages of
wikitext with their categories and transclusions.

**Skip the packaging.** Galleries, maintenance pages and image lists are
dropped during the crawl; the type-level blocklist above removes the rest
afterwards.

**Extract.** From wikitext, per page:
* **sections** — `split_sections` finds headings by counting `=` signs;
* **facts** — infobox fields, with labels learned from the wiki's own schema;
* **edges** — `[[wikilinks]]`, namespace-checked, already resolved by MediaWiki;
* **citations** — `{{Ref}}` templates and `<ref>` tags, parsed per the series'
  declared grammar, kept structured *and* inlined into prose as
  `(Chapter 143, Episode 30)`.

**Store.** Wikitext plus metadata to `series/<n>/wikitext/*.json`, one file per
page, and a manifest recording what was crawled, when, and from where. `crawl`
resumes from these files, so a throttled run loses nothing.

Then `audit` (before trusting anything), `index` (fact store, FTS5, graph,
chunks, vectors), and optionally `export` to an Obsidian vault.

---

## 4. The batched worker — now the default, and the only path

### Why the old one was slow

The obvious diagnosis was wrong. The crawler was not CPU-bound, GPU-bound or
bandwidth-bound; a very good machine did not help, and could not have.

**Fandom rate-limits per request, not per page, and it does it per IP.** The
old crawler asked for one page per request with `action=parse`. So the ceiling
was requests-per-second, and adding workers only split the same allowance into
more, slower connections. Measured, on the same wiki:

| workers | delay | throughput |
|---:|---:|---:|
| 3 | 1.0 s | 112 pages/min |
| 10 | 0.25 s | 117 pages/min |

Three times the concurrency and a quarter of the delay bought **4%**. That
number is the whole argument: concurrency was never the lever.

### What changed

`action=query` accepts up to 50 titles per request — MediaWiki's cap for
anonymous callers, not a tuning knob, and it rejects the whole request past it.
Fifty pages now arrive per request instead of one.

| | old (`action=parse`, 1/request) | new (`action=query`, 50/request) |
|---|---:|---:|
| raw fetch | 51 pages/min | 686 pages/min |
| full crawl, real wiki | 112 pages/min | ~2,500 pages/min |

One Piece — 7,937 pages — took **3 minutes 4 seconds**, with zero rate limiting.
The same crawl on the old path would have run over an hour.

### What `action=query` does not return, and why it does not matter

Two things came free with `action=parse` and had to be recovered. Both were
cheaper than the request they were riding on.

**The section tree.** `action=query` returns no section list. It turns out the
API was only ever supplying the *levels*, because the byte offsets it gives
shift the moment templates expand — so `split_sections` was already locating
headings in the wikitext itself. Counting `=` signs agrees with the API on
**3,113 of 3,114** sections across a 400-page sample. The one disagreement is a
heading inside a template.

**The infobox schema.** `prop=properties` describes a page *type*, not a page.
So it is fetched once per newly-seen type instead of once per page: roughly
twenty extra requests per wiki, against the nine thousand it replaces.

### Reinforced as default

There is no old path left to fall back to:

* `fetch_page` and `PAGE_PROPS` are **deleted**, not deprecated. The batched
  `fetch_batch` is the only way a page enters the engine. It returns
  `action=parse`-shaped dicts, so everything downstream of it is unchanged and
  untouched by the switch.
* `BATCH_SIZE = 50` is documented as the API's cap rather than a knob.
* `crawl_concurrency = 10` and `crawl_delay_seconds = 0.25` are the settings
  that pulled One Piece clean, and the comment in `config.py` now says why
  raising them cannot help and lowering them does not protect you — what
  triggers a 429 is the *number of requests*, and batching already cut that by
  fifty.
* The crawler's module docstring leads with the batching and carries the
  measurements, so the next person to open the file gets the reasoning rather
  than the archaeology.

Rate limiting is still handled honestly underneath all of this: HTTP 429 pauses
every worker, retries four times, and then aborts with a message telling you to
re-run — and re-running resumes from disk.

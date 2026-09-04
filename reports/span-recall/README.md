# Span-recall harness

Exhaustive, line-level reachability testing — the complement to the gold
question bank.

## Why this exists

The prose pass samples. At its calibrated density (~11.4 questions per 1,000
words) the bank asks about roughly **one line in eight**, and 9,008
hand-authored prose questions across the whole campaign have yielded 24
distinct engine gaps — about **one finding per 375 questions authored**. The
bank is excellent regression protection and an expensive discovery instrument,
and it cannot deliver the campaign's stated mandate ("down to a single line"),
because per-line coverage by hand is arithmetically out of reach at 1M words.

This harness covers the complement mechanically, with zero authoring:

- **tier 0 (`index`)** — is every sentence present, whole, inside some chunk?
  Pure SQLite, no server, **0.3 s for the entire JJK corpus**. A miss here is
  an indexing/chunking defect: the line is invisible to retrieval no matter
  what anyone asks.
- **tier 1 (`recall`)** — does `/context` actually serve the line back? Needs
  the live server, ~0.5 s/probe on GPU, so it is sampled by default.

Run tier 0 after every re-index. It is free.

## Usage

Promoted into the package as a first-class command, alongside `eval`,
`canon-run` and `page-run`:

```
python -m scriptengine.cli span-recall --series jjk
python -m scriptengine.cli span-recall --series jjk --probe 400
python -m scriptengine.cli span-recall --series jjk --probe 400 --mode scoped
```

Tier 0 is the default and needs no server. `--probe N` adds the live tier-1
sample on top. Results land in `reports/span-recall/<series>/` as JSONL, one
row per probe, so runs are diffable across re-indexes.

**Exit codes.** Tier 0 exits 2 on any unreachable line — that is a defect, and
a re-index that silently drops content should fail loudly. A tier 1 score never
fails the command, following `canon-run`'s rule that "a measurement command
that fails the build is one nobody runs". Exit 1 means the run itself could not
be trusted (no index, no server).

Tier 0 also runs as part of the test suite (`tests/test_span_recall.py`), which
is the durable form: the segmentation rules, the citation-comparison rule and
the boilerplate policy are all pinned by tests, so a future change cannot
quietly reintroduce the bugs listed at the bottom of this file.

A full `--probe` sweep of every sentence is ~48k probes, roughly 7 h on GPU.
Sample first.

### Query modes

| mode | query | what it isolates |
|---|---|---|
| `verbatim` | the sentence itself | reachability floor — if this fails, the line is hard to reach by any phrasing |
| `scoped` | `<page title>: <sentence>` | control for corpus redundancy (below) |
| `terms` | content terms, stopwords stripped | realistic user-shaped probe (implemented, not yet characterised) |

### Verdicts

| verdict | meaning | points at |
|---|---|---|
| `HIT` | served bundle contains the line | — |
| `MISS_DOC` | the line's own page never made the bundle | ranking |
| `MISS_SPAN` | the page *was* returned, the line was not | chunk selection inside the doc |
| `TRUNCATED` | bundle hit the token budget | budget |

Splitting `MISS` this way matters: the two have different fixes, and lumping
them produces a number nobody can act on.

## Results — JJK, 2026-09-03

### Tier 0: the index is essentially complete

```
sections=5,416   substantive sentences=48,473   in-chunk=48,471
MISSING=2        coverage=99.9959%              (0.3s)
```

Both misses are `Chapter 239 / References` — 69 words of real trivia prose (the
chapter title referencing *Baka Survivor* by Ulfuls) present in **none of that
document's 22 chunks**. This is the already-known **Trivia chunking gap**,
standing open #5, independently rediscovered in 0.3 s with no authoring — the
harness validating itself against a defect the campaign originally found the
expensive way.

Link-list boilerplate (`Navigation`, `See Also`, `External Links` — 52
sentences of interwiki name lists) is excluded by default. Those are correct
exclusions, not defects, and counting them buried the real finding at 99.875%.
`References` is deliberately *not* excluded, which is exactly why the Chapter
239 gap surfaced.

**Conclusion: storage is not the problem.** Every substantive line in the
corpus except two is present, whole, and retrievable in principle. The engine
does hold the full text of every page verbatim; the question bank never was
the storage layer.

### Tier 1: retrieval, 400 probes, `verbatim`, citation-insensitive

```
HIT         387   96.8%
MISS_DOC      7    1.8%   source page never retrieved (ranking)
MISS_SPAN     6    1.5%   source page retrieved, line not served
TRUNCATED     0    0.0%
ERROR         0    0.0%
```

Most of the *apparent* failure along the way was instrumentation, not engine.
The honest sequence was **90% → 92.8% → 96.8%** as each of my own harness bugs
was removed (below). Treat any future miss rate the same way: assume the
harness is wrong until the miss survives a control.

**`MISS_DOC` (1.8%)** — a line queried verbatim sometimes returns the sibling
pages narrating the same event, without returning the page the line lives on.
The JJK wiki tells each event on the chapter page, the episode page, the
character synopsis *and* the battle page, so a bare sentence is genuinely
ambiguous about which is wanted; every one of the seven is in that redundant
cluster (`Chapter 93`, `Episode 44`, `Chapter 146`, two battle pages, two
synopses). Scoping the query by page title (`--mode scoped`) reduces this but
does not eliminate it.

Whether that is a defect is a judgement call, not a measurement: the engine
serves correct information, from a sibling page, with different wording and a
different citation. For an engine whose contract is *verbatim* accuracy, that
distinction is worth an explicit decision rather than a silent pass.

**`MISS_SPAN` (1.5%)** — down from an apparent 5.3% before the citation fix.
At least one of the six is a further harness artifact: a `Sorcerer Clan` table
row (`| Hei Maki Zenin: Daughter of Ogi...`) that slipped the pipe-count filter
because it carries only one pipe. The rest are long narrative sections and are
the only candidates here for a genuine chunk-selection gap — too few to
generalise from. Re-probe them individually before treating any as confirmed.

### Cross-series tier 0 — JJK is the outlier, not the norm

The harness is series-agnostic. Running it on the other indexed wikis:

| series | sections | sentences | missing | coverage | time |
|---|---:|---:|---:|---:|---:|
| jjk | 5,416 | 48,473 | **2** | 99.9959% | 0.3 s |
| bleach | 13,509 | 132,797 | **1,171** | 99.1182% | 1.3 s |
| opm | 8,501 | 45,726 | **1,039** | 97.7278% | 0.3 s |

JJK is near-perfect because it is the series the campaign has been working;
the others have never had this scrutiny. OPM's 1,039 unreachable sentences
cluster in real content sections — `Trivia` (139), `Personality` (120),
`Equipment` (77), `Abilities and Powers` (70), `Appearance` (65) — on documents
that *do* have chunks.

Spot-verified: `170,000-Year-Old Cicada Adult` has 9 chunks covering its
infobox, Appearance and Abilities, and its entire `Personality` section is in
none of them. This is the same family as JJK's Trivia chunking gap (standing
open #5), two to three orders of magnitude larger.

Open question, not yet answered: how much of this a corpus-wide re-index would
fix on its own (the deferred colon-truncation re-index, State 65 item 3) versus
how much is a live parser/chunker gap. Worth settling before any prose pass is
pointed at a non-JJK series — authoring gold questions over an index missing
1,039 lines would measure the wrong thing.

## Harness defects found while building this

Recorded because each would have produced a confident, wrong finding:

1. **BOM on the JSONL.** G10's `utf-8-sig` write path belongs on the JSON batch
   files the engine reads back; on a JSONL stream it corrupts the first record
   for every ordinary reader.
2. **Sentence splitter welding sentences.** The corpus writes
   `...into a cliff.(Chapter 151) He thinks...` with no space after the period,
   so a plain `(?<=[.!?])\s+` split produced multi-sentence blobs and then
   probed with them. Fixing it surfaced **5,410 additional sentences**.
3. **Citation rendering mismatch — the one that mattered.** The section store
   renders `(Chapter 143)` where the served beat renders
   `(Chapter 143, Episode 49)`. Comparing raw text failed on the citation
   alone: such sentences were **71% of apparent `MISS_SPAN` but under 10% of
   `HIT`**. Comparison is now citation-insensitive on both sides, and
   `MISS_SPAN` largely disappeared. Before this fix the harness would have
   reported a chunk-selection bug that does not exist.

## Recommended use

1. **After every re-index:** run tier 0. Free, and it covers the entire
   indexing/chunking defect class corpus-wide.
2. **Before committing to a large tranche** (chapters — 304 pages, ~3× all
   hand-authoring done so far) run tier 1 sampled, and hand-author only where
   it shows weakness. This inverts the loop from *author → run → discover* to
   *sweep → discover → author*.
3. **Treat surviving miss clusters as the authoring backlog** — they name the
   sections where retrieval is actually weak, which is where gold questions buy
   something.

## Known limits

- Tier 1 compares served text against `sections.text`. Citation rendering is
  now normalised, but other renderer differences may remain unquantified.
- `terms` mode is implemented and unmeasured.
- Sentence segmentation is regex-based, with guards for the corpus's
  `.(Chapter N)` citation style and for known abbreviations. Table rows are
  dropped at 3+ pipes; single-pipe rows (some `Members` tables) still slip
  through and show up as spurious `MISS_SPAN`.
- Tier 0 proves a line sits inside *some* chunk. It does not prove the chunk is
  embedded well or ranks sensibly — that is tier 1's job.

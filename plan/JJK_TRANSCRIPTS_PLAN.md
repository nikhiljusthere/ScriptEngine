# JJK Anime Transcript Ingestion — Plan (2026-09-08, v2 post-council)

Status: **Phase 1 EXECUTED (2026-09-08, drift log D12) + Phase 2 EXECUTED (2026-09-08, D13).** Council-reviewed
(run ea58f12b; verdict `/tmp/jjk-transcript-council/verdict.md`).
v1's shared-collection Phase 2 was rejected as technically broken (code-verified:
no `doc_type` payload field exists; point ids are the wiki `chunks` rowids and
rowids restart on re-index; `recreate()` rmtree's the storage dir, so a
same-directory second collection is silently wiped by the next `index`;
`hybrid.py` resolves vector hits against the wiki `chunks` table and drops or
mis-resolves unknown ids). v2 below is the revised design.

## What

Add the JJK anime's closed captions (all released episodes, subs.yakuaru.com /
SubArchivist) to the JJK corpus as a first-class document type, with a
per-character dialogue dataset. Goals: (a) know what happened in each episode
with detail, (b) a dataset of all dialogue per character.
**Framing (council):** this advances D6's anime-timeline dimension and is a
real voice-dataset product — it is *not* D6 comprehension of the existing
corpus, and it does **not** enter the D6 denominator or closed definition.
Drift-log entry required (campaign-neutral addition).

## Source (verified 2026-09-08)

- Bulk plaintext export endpoints, one fetch per season:
  - `.../chapter/season-1/export/plaintext` → **E1–E24** (497 KB)
  - `.../chapter/season-2/export/plaintext` → **E25–E47** "Shibuya Incident – Gate, Close" (389 KB)
  - `.../chapter/movie/export/plaintext` → **M1 JUJUTSU KAISEN 0** (79 KB)
- **48 documents.** Line format: `[MM:SS] Speaker` + indented continuation
  lines; `SIGN <text>` = on-screen text (not dialogue). Per-episode header:
  source (Crunchyroll) + sub-team credits.
- Speaker names are the archive's **best effort** (their own note).
- The anime ends at E47 = Gojo sealed — the same frontier as the wiki.
  **Single-source fragility (blind spot #6):** the raw exports + sha256 in the
  manifest are the mitigation if the archive vanishes.
- **Licensing (blind spot #8, corrected):** personal local KB only; the old
  "no redistribution" line was self-contradictory (a published script with
  CC-derived lines *is* redistribution). Source + sub-team credits recorded
  in the manifest and marked on any derived tag.

## Phase 1 — import (no model, no GPU; campaign-neutral) — **DONE 2026-09-08**

New CLI `transcripts-import --series jjk`:
- Download the three exports (browser UA; retry on Cloudflare 520) →
  `series/jjk/transcripts/ep<NN>.json` + `movie.json`, each
  `{episode, season, title, source, credits, lines: [{t, speaker, text,
  kind: line|sign}]}`.
- Raw exports + `manifest.json` (urls, sha256, fetched_at, per-episode line
  counts) — idempotent re-runs hash-compare and skip unchanged files.
- New `series/jjk/transcripts.db` (separate from `facts.db` — the campaign
  measures `facts.db`, untouched): `lines(episode, season, ts, speaker,
  text, kind)` + FTS5; `speakers` view.
- **Speaker alias table (deterministic, no LLM)** — canonicalize the
  archive's labels (Itadori/Yuji, romanization variants, Surname vs First
  usage) so `dialogue --character` is per-character, not per-label
  (resolves the B-vs-C clash over goal (b)).
- Verbatim names otherwise, with the archive's "best-effort" disclaimer
  printed in `dialogue` output. LLM attribution = separate later campaign on
  demonstrated need (unverifiable guesswork in a never-guess corpus + heavy
  GPU job under the hard rule + re-runs on every re-export).
- **JJK0 movie (blind spot #1):** import `movie.json`, but mark movie lines
  **out of scope for v1 citation** — `verify.py`'s episode regex is
  `Episode\s+([\d.\-]+)` (digits only) and the wiki has no "Episode M1"
  page; a movie tag shape + verify branch is a later task.
- Read commands: `transcript --episode N [--from --to] [--movie]`;
  `dialogue --character X [--episode N] [--limit]` (FTS-backed, alias-aware).
- Checks: 48 docs, zero parse failures (assert every `[ts]` line carries
  speaker + text), spot-check 3 episodes against live pages.

### Phase 1 execution record (2026-09-08)

- Code: `scriptengine/transcripts.py` (fetch/parse/import/db + alias rule),
  `SeriesPaths.transcripts` / `.transcripts_db`, CLI doors
  `transcripts-import` / `transcript` / `dialogue`.
- Result: 48 docs (S1 E1–24, S2 E25–47, M1), **15,411 dialogue lines** (==
  raw `[ts]` line count, zero loss), 815 sign lines (814 `SIGN` + 1
  unprefixed text line, lossless fallback). E1 spot-check vs the live page
  passes.
- Speaker aliases as designed: `(Flashback) X` → X + 8-entry `VARIANT_MAP`
  (checked against the 368-label inventory). Deliberately NOT merged:
  `Fushiguro` (covers both Megumi and Toji — merging would fabricate an
  identity) and every generic label.
- Parser quirks handled: NBSP indentation (U+00A0, the archive's
  continuation marker), one-syllable-per-line SFX signs, subtitle lines the
  archive re-writes in full on the next row.
- Data lives under `series/jjk/` (gitignored); the DB is separate from
  `facts.db`; no gated code touched.

**What Phase 1 does NOT claim:** `verify.py`'s episode branch only checks a
wiki page titled "Episode N" exists — it never checks the quoted line is in
the transcript (blind spot #2: false green). No "already verified" claim
anywhere; line-level cross-checking is a later task.

## Phase 2 — embedding — **EXECUTED 2026-09-08 (D13)**

**Rejected (v1 design):** shared Qdrant collection + `doc_type` payload —
mechanically impossible/contaminating as analyzed above.

**v2 design:**
- Separate directory `series/jjk/qdrant-transcripts/`, reusing `VectorStore`
  with a directory parameter (one param, zero changes to gated code, no
  `recreate()` rmtree hazard).
- Own door: `transcript-search` CLI (+ later a `/transcript` HTTP endpoint if
  wanted). Zero contamination of wiki bundles by construction; zero
  4-gate re-baseline.
- **Trigger:** a concrete retrieval ask that fails at the FTS layer, **after
  D6 closes** (4/5 council: mid-campaign embedding shifts every retrieval
  rank, collides with the campaign's 150k GPU waves, and re-opens the
  "remainder 0" exit condition — all avoidable by waiting).
- **Re-export cadence owner (blind spot #3):** "new episode drops →
  re-import via manifest hash-compare; if Phase 2 has run, invalidate stale
  transcript embeddings for changed episodes" (the documented stale-vector
  bug class). Owner: campaign session of record (recorded in drift log).
- Optional later: `[MM:SS]` time-rank anchor for the timeline door
  (blind spot #7); the tier-0 transcript containment check, if ever added,
  is a **fifth gate** and needs its own governance sign-off (blind spot #5).

## Phase 2 execution record (2026-09-08)

- Code (pre-written before the run; the run verified it): `embed_series()` /
  `search_series()` / `stale_reasons()` in `scriptengine/transcripts.py`; CLI
  doors `transcripts-embed` (idempotent, `--force`) + `transcript-search`
  (`--limit`, `--episode`). Separate `series/jjk/qdrant-transcripts/` Qdrant
  dir + `embed_meta.json` (manifest-sha + per-export sha staleness marker).
  Zero changes to the gated store code.
- One-line fix during the run: `_export_shas` keyed the manifest's export
  entries on a `key` field that does not exist (the import manifest keys
  them by `url`) — the first two embed runs (23:01, 23:06) crashed with
  `KeyError: 'key'` after writing the vectors but before the meta file; the
  crash was invisible twice because the pipeline rc was masked by `| tail`
  (caught on the third run, RC=1). Fixed: key by `url` (1 line + comment).
- Receipts: **16,226 points** (15,411 dialogue lines + 815 sign lines),
  `device=cuda`, model `BAAI/bge-large-en-v1.5` (1024 dims), ~3.5 min in the
  one-copy window (A stopped `:8000` 22:51:42, restarted it on CUDA
  23:17:41, pid 23306 — `reports/master-work/decisions.md`). Idempotency:
  immediate re-run = "Unchanged since the last embed (16226 points) -
  skipped" (RC=0). Staleness marker live: `embed_meta.json` holds the
  manifest sha + the 3 export shas (S1/S2/movie).
- Smoke (no STALE warnings either way): plain query "Sukuna threatens the
  students at the school" → top hit E21 `[03:26]` Geto "Sukuna's actions"
  (0.754); `--episode E22` filter → all 5 hits E22 (top: `[09:29]` Mahito
  "Sukuna's fingers cause harm, though." 0.683).
- Movie-tag branch (recorded here per the plan's blind spot #1): the
  `(Movie <name>)` citation branch in `scriptengine/eval/verify.py` does a
  structural check against the corpus film page ("Jujutsu Kaisen 0" matches
  "Jujutsu Kaisen 0: The Movie"), like the episode branch; the line-level
  cross-check against the transcript store remains a later task (same shape
  as Phase 1's blind spot #2). `tests/test_verify_movie.py` 3/3 green
  (offline, run first per the job spec).
- Deliberate exclusions (with reasons):
  - **LLM speaker attribution** = a separate campaign on demonstrated need
    (unverifiable guesswork in a never-guess corpus + heavy GPU job under the
    hard rule + re-runs on every re-export) — carried over from Phase 1.
  - **Tier-0 transcript containment as a 5th standing gate** = needs its own
    governance sign-off (blind spot #5); not added.
  - **`/transcript` HTTP endpoint** = YAGNI; the `transcript-search` CLI door
    covers the demonstrated need.
  - **`[MM:SS]` time-rank anchors** for the timeline door (blind spot #7)
    = optional later; the payload already carries `ts`, so this is a
    retriever-side feature when the timeline ask appears.
- Campaign-neutral as planned: no `facts.db` writes, the four standing gates
  untouched, transcripts stay out of the D6 denominator.

**What Phase 2 does NOT claim:** `transcript-search` ranks by cosine
similarity over the whole store (episode filter is a payload match, not a
re-rank within the episode); speaker labels remain the archive's best effort
until the attribution campaign; "no STALE warnings" at run time only proves
the manifest matched — a re-import must re-run `transcripts-embed` (the
marker exists exactly so that re-run is detectable).

## Governance

- Drift-log entry: Phase 1 campaign-neutral; transcripts outside the D6
  denominator and COVERAGE.md's closed definition.
- A COVERAGE.md section would mean editing `coverage_report.py`
  mid-campaign (the campaign's own measuring tool) — **waits on campaign
  sign-off**; not part of Phase 1.
- Re-export owner: as above.

## The one thing to do first (council)

Run the Phase 1 import: three exports → 48 JSONs + `transcripts.db` (FTS5) +
hash manifest + alias table + `transcript`/`dialogue` commands. One
afternoon, zero GPU, zero gates, zero campaign touch — delivers goal (b) in
full. Everything else (movie tag shape, separate-collection embedding,
attribution) waits on demonstrated need.
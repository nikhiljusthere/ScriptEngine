#!/usr/bin/env python3
"""Regenerate the 3×500 verify pools on the new sentence grid (windowing-100,
2026-09-30). Zero LLM cost: the builder only.

The pools the 35B campaign reads are the grid's labeled windows -- one
whole-sentence span of one sub-topic each, never a character slice. The empty
share is re-measured on the new grid, not carried over (council C6: "~43%"
was an output of the old grid, not an input): a window is non-empty when at
least one of the store's own event rows maps into it (the row's quote,
located on the passage's grid, covered by one window). Each pool is
stratified to the measured share, and rare-verb windows keep their ×3
sampling weight (the same RARE set build_trainset.py repeats with).

Supersede, don't salvage (council ruling): ~117 of the 1,500 old "verified"
rows are unproven on the old grid, and re-running those 117 verifications is
cheaper than proving a salvage safe. The old pool files and done-logs are
archived as *.old-grid (renamed, never deleted) and the campaign restarts at
n=0 on the new grid.

A pool line is the old campaign shape plus the builder's identity fields, so
`opencode_check.py` and `windows_to_messages.py` keep working:

    {"n", "id", "page", "section", "passage", "gen", "sub"}

Held-out pages and re-keyed gold are excluded from the sampling universe
BEFORE stratification (2026-10-04, WP2): the plan's rule
(`plan/JJK_STUDENT_TRAINING.md` section 4) is split by PAGE, never by row --
a held-out page never trains, and the old gold600/pilot400 respected it (0
overlap) while the gen-2 emitter dropped it (207/1,500 pool windows sat on
v1 dev/test pages, 40/56 blind-gold pages appeared in the pools). The gold
records' window ids are RECOMPUTED on the current grid, never read from the
file (the stored ids go stale with every id-scheme or store change). The
emit asserts the result and exits non-zero on any failure: pools pairwise
disjoint, pool ids unique, zero pool pages in the holdout, zero pool ids in
the gold. The pilot's ADJUDICATED windows (kept/reexpressed) are excluded
the same way (2026-10-04, WP3b-2, --gold2); its reread/straddle windows
STAY in the universe -- the 35B re-read owns them.

WP6b (2026-10-04) strata: a series whose store has no extraction trace
(MCU: 1,794 of 43,250 pages carry an event row) must NOT read 'no
teacher row' as 'empty' -- on a never-read page it means NEVER READ.
With --stratify-read N --stratify-unread M the train pool is N windows
from READ pages (>= 1 event row), stratified at the MEASURED read-page
non-empty share with the usual rare x3, plus M uniform windows from
NEVER-READ pages (the student sees page types the teacher never read);
the page-type mix of both strata (documents.page_type) is reported in
the receipt. With --test-pool NAME (WP6b test pool) a page-disjoint
test pool of --test-read-n read-page windows (stratified like the train
pool) + --test-unread-n never-read windows (uniform), at most
--test-per-page-max per page (one-per-page pass first, so 100 windows
span ~100 pages), is emitted alongside: its pages are chosen seeded
BEFORE the train pools, recorded to series/<s>/training/
holdout_pages.json (which holdout_pages() then reads, so the train
pools never sample them on any later run), and excluded from the train
sampling universe.

U-WP4 (2026-10-04, plan/UNIVERSAL_DATASET_PLAN.md): the universal
pools. --era-thirds (the Marvel franchise): the U-WP2 era stamp's era
thirds (old/mid/new) x read/never-read at 50/50 inside each third (the
plan's 50/50 convention; a window's era is its SECTION's era when the
page's `sections` map carries the section, else the page's era --
U-WP2c). The read side stratifies at the measured per-cell non-empty
share with the usual rare x3; the never-read side is uniform. Undated
pages: --undated-policy exclude (marvel: counted, never sampled) or old
(mcu: the plan's "mcu old = 2008-2009 + undated-by-rule" -- folded into
the old third; the pool line still records their real era `undated`).
The era pool lines carry `era` + `page_type` (documents.page_type).
--eventish (the teacher-less wikis): the U-WP3 zero-LLM proxy 50/50
eventish/non-eventish split (the lines carry the `eventish` flag);
--read-evidence (csm): the READ pages (>= 1 event row) take 50/50 of
the pool, stratified at the measured evidence share (rare x3); the
never-read pages keep the proxy 50/50. The hxh holdout wiki runs
--pools none (0 train) + the test pool only. A U-WP4 test pool
(--test-n N) is the WP6b spread pool re-stratified on the pool's own
cells, with the per-page cap GLOBAL across cells (a page's windows may
sit in two era cells -- the section-era rule); its candidate universe
also excludes the pages of the wiki's OTHER train pool files (the
page-disjoint is against EVERY train pool of the wiki, and the set is
stable across re-runs: the current run's own pool names are exempt from
that exclusion, so a same-seed re-run reproduces the pool byte-for-
byte). The holdout json gains a `pools` list (one entry per recorded
pool; `pages` is the union) so a second pool of one series keeps the
first pool's pages recorded; a WP6b flat file is migrated, never
clobbered. U-WP4c: pass 1 of the fill stays strictly one-per-page
 (the WP6b spread rule); a page that already holds a window (its
 windows may sit in two cells) takes its second only in pass 2, under
 the global cap -- the U-WP4b pass-1 could take a page's second window
 in pass 1, which shrank the page spread below the pool's spread floor
 once the U-WP4c universe shrank (csm's 50-window test pool spanned 49
 pages, 2026-10-04).

    U-WP4b (2026-10-04, plan/UNIVERSAL_DATASET_PLAN.md): universe() now
also carries the declared narrative FACT passages the extractor reads
(`events.build_passages(scope='all')` = sections + lead +
`events.fact_passages`; wiki overrides `events: narrative_fact_keys`).
Marvel's `history` beats and `synopsis*` comic-issue plots held 66% of
its teacher event rows (5,936/9,004: fact:history 3,742, fact:synopsis1
1,662; 106.7M fact chars vs 69.3M section), so the old universe's pools
missed the comic synopses and character histories. The fact passages
are built on the engine's own `fact_passages` rules (the declared
patterns, `_fact_key_order`, the panel-sentence floor, the `fact:<key>`
label) and are appended AFTER each page's sections, so the per-page
order (lead, sections in ordinal order) is kept. The lead/section
selection is the U-WP4 one, unchanged: a wiki that declares no
`narrative_fact_keys` (JJK, MCU, every anime wiki -- verified per
overrides.yaml) sees an empty fact list and a byte-identical universe
(the re-emit cmp proof). The U-WP4 test pool's recorded pages are
STICKY: a re-run re-derives the pool's windows on the recorded pages
and never re-rolls the draw -- a universe change must not reserve a
fresh page set per re-emit (measured: 75 -> 147 -> 222 holdout pages
per run before the fix).

    U-WP4c (2026-10-04, plan/UNIVERSAL_DATASET_PLAN.md): universe() is
the PRODUCTION READ SET, exactly: the pages of
`events.scope_plan(store, 'all')` (the placement rule's extractable
pages + the corpus rule's pages + the R1 prose scope's pages + the R10
fact scope's pages), and per page the passages of
`events.build_passages(store, page, by_page[page], 'all', axis_rank)`
-- the page's READ sections (scope_plan's by_page selection, deduped by
id), then its lead, then its declared narrative fact values, each with
the extractor's panel-sentence floor and label. The U-WP4b universe
read every document's lead and every panel-eligible section of the
store, but the extractor reads per QUEUED page: 5-40 pct of every
U-WP4b pool's windows sat on sections the extractor never selects or
pages not in its queue (measured 2026-10-04). Two bulk passes stand in
for the per-page call, proven label-for-label: the lead pass (one
query over the queue's documents, `lead_passage`'s strip + panel
floor) and `bulk_fact_passages` (the U-WP4b bulk fact pass, identical
to the per-page `fact_passages`; a page with a narrative fact value is
in the queue via the R10 fact scope, so the bulk pass over all pages
is the union over the queue's pages). `axis_rank` only RANKS the
passages (R3) -- it never changes which are read or what they hold --
so the read set is rank-independent and the pass needs no store-axis
build. The per-page order is `build_passages`' (sections, lead,
facts): the order never enters the content-addressed window id. The
U-WP4c re-emit re-derives the test pool STICKY (the record is a
record, not an input): a re-emit with the same seed re-reads the
recorded pool's lines, re-locates each on the current universe (the
content-addressed id re-derives), and re-merges the recorded holdout
entry unchanged -- the re-emit is byte-identical (the re-emit cmp
proof), while the page draw itself is rolled exactly once, on the
fresh emit.

    python tools/train/emit_windows.py --series jjk [--pools mimo,nemotron,spacebunny]
                                        [--n 500] [--seed 20260930] [--dry-run] [--no-archive]
                                        [--out-dir DIR] [--no-holdout] [--gold FILE]
                                        [--gold2 FILE] [--archive-suffix .pre-wp3b]
                                        [--test-pool NAME] [--test-read-n 70]
                                        [--test-unread-n 30] [--test-per-page-max 2]
                                        [--stratify-read 350] [--stratify-unread 150]
                                        [--holdout-json FILE]
    python tools/train/emit_windows.py --series marvel --pools marvel --n 600
                                         --era-thirds --test-pool marvel_test --test-n 75
    python tools/train/emit_windows.py --series mcu --pools mcu_era --n 600
                                         --era-thirds --undated-policy old
                                         --test-pool mcu_era_test --test-n 75
    python tools/train/emit_windows.py --series csm --pools csm --n 300
                                         --read-evidence --test-pool csm_test --test-n 50
    python tools/train/emit_windows.py --series hxh --pools none
                                         --eventish --test-pool hxh_test --test-n 150

"""
import argparse
import json
import math
import random
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scriptengine.ingest.windows import (  # noqa: E402
    CURRENT_GEN,
    build_windows,
    quote_grid_span,
)
from scriptengine.stores.facts import FactStore  # noqa: E402

# U-WP4 siblings (same directory; the script dir is on sys.path for a
# direct run, and dataset_gates adds it for its import of this module):
# the U-WP2 era rule (one source of truth for the old/mid/new bounds)
# and the U-WP3 zero-LLM eventish proxy (the 50/50 split flag).
from era_stamp import era_of  # noqa: E402
from eventish import is_eventish  # noqa: E402

# Same rare-verb set build_trainset.py repeats with `--rare-x 3`: a window
# that states one of these is under-represented in natural prose, so the
# campaign over-samples it to keep the student seeing them.
RARE = {"killed", "saved", "captured", "escaped", "betrayed",
        "sealed", "awakened", "departed", "arrived"}


def bulk_fact_passages(store):
    """U-WP4b: the wiki's declared narrative FACT values as
    ``(page, label, text)`` passages, in one bulk query instead of the
    per-page ``events.fact_passages`` call (one overrides parse + one
    query PER PAGE -- ~20 min on marvel's 236,720 pages).

    Label-for-label identical to ``fact_passages``: the same declared
    fnmatch patterns, the engine's ``_fact_key_order`` key order, the
    in-value order, the panel-sentence floor, and the extractor's
    ``fact:<key>`` label (0 (page, key) carries >1 value on marvel,
    2026-10-04, so the in-value order is the store's row order either
    way). Re-proven on 1,000 pages for U-WP4c (2026-10-04): a wiki
    that declares no ``narrative_fact_keys`` (JJK, MCU, every anime
    wiki -- verified per overrides.yaml) gets ``{}`` and an empty fact
    list, so its universe is sections + lead only. U-WP4c note: a page
    with a panel-eligible narrative fact value is in the `all` queue
    via the R10 fact scope (`fact_pages`), so this pass over ALL pages
    is exactly the union of the queue's pages' ``fact_passages``."""
    from scriptengine.ingest.events import (
        _fact_key_order,
        narrative_fact_keys,
        panel_sentences,
    )
    from scriptengine.ingest.wikitext import strip_markup

    facts_by_page = {}
    patterns = narrative_fact_keys(store)
    if not patterns:
        return facts_by_page
    import fnmatch

    # The declared keys the store actually carries: the engine's own
    # distinct-key pre-filter (`fact_pages` / `fact_key_census` run
    # this same query), so the value pass touches only declared
    # rows.
    distinct = {
        row["key"]
        for row in store.connection.execute(
            "SELECT DISTINCT LOWER(key) AS key FROM facts"
        )
    }
    keys = [
        key for key in sorted(distinct)
        if any(fnmatch.fnmatch(key, p) for p in patterns)
    ]
    if not keys:
        return facts_by_page
    placeholders = ",".join("?" * len(keys))
    # `fact_passages` reads per page (in-value order); the bulk
    # pass orders by the store's row order per (page, key) --
    # identical here (0 (page, key) has >1 value, marvel,
    # 2026-10-04) and deterministic either way. Pages arrive in
    # d.id order, so each page's facts flush when the page
    # turns (O(one page) memory, not the whole fact table).
    cur_page, cur_values = None, {}

    def flush(page, values):
        # `fact_passages`' per-value handling: the keys in the
        # engine's `_fact_key_order`, the values in in-value
        # order, the panel floor, the `fact:<key>` label.
        out = []
        for key in sorted(values, key=_fact_key_order):
            for value in values[key]:
                text = strip_markup(value).strip()
                if panel_sentences(text):
                    out.append((f"fact:{key}", text))
        if out:
            facts_by_page[page] = out

    for row in store.connection.execute(
        "SELECT d.title AS page, f.key AS key, f.value AS value"
        " FROM facts f JOIN nodes n ON n.id = f.node_id"
        " JOIN documents d ON d.id = n.document_id"
        f" WHERE LOWER(f.key) IN ({placeholders})"
        " ORDER BY d.id, f.rowid",
        keys,
    ):
        key = (row["key"] or "").strip()
        if not any(fnmatch.fnmatch(key.lower(), p)
                   for p in patterns):
            continue  # `fact_passages`' per-row rule, verbatim
        if row["page"] != cur_page:
            if cur_page is not None:
                flush(cur_page, cur_values)
            cur_page, cur_values = row["page"], {}
        cur_values.setdefault(key, []).append(row["value"] or "")
    if cur_page is not None:
        flush(cur_page, cur_values)
    return facts_by_page


def universe(store):
    """Every (page, label, text) the production extractor reads -- the
    read set, EXACTLY (U-WP4c, 2026-10-04, plan/UNIVERSAL_DATASET_PLAN.md):
    the pages of ``events.scope_plan(store, 'all')`` -- the placement
    rule's extractable pages, the corpus rule's pages, the R1 prose
    scope's pages and the R10 fact scope's pages -- and, per page, the
    passages of ``events.build_passages(store, page, by_page[page],
    'all', axis_rank)``: the page's READ sections (scope_plan's by_page
    selection: the page's own extractable sections, then the corpus
    rule, then the R1 prose sections, deduped by id), then its lead,
    then its declared narrative FACT values, each with the extractor's
    panel-sentence floor and label.

    Why the U-WP4b universe was wrong: it read every document's lead
    and every panel-eligible section of the store, but the production
    extractor reads per QUEUED PAGE -- a lead of a page the queue never
    carries, and a section no scope rule selects (furniture on a
    non-placement page, a heading no rule names), are never read.
    Measured 2026-10-04 (the U-WP4c trigger): 5-40 pct of every
    U-WP4b pool's windows sat on such sections or pages (jjk 18-22,
    csm 29 (test 40), hxh 35, opm 21 (test 34), db 22, bleach 13
    (test 26), onepiece 15 (test 22), berserk 14, mcu 18 (test 39),
    marvel 5 (test 12) pct).

    Two bulk passes stand in for the per-page ``build_passages`` call,
    proven label-for-label: the lead pass (one query over the queue's
    documents, ``lead_passage``'s strip + panel floor) and
    ``bulk_fact_passages`` (the U-WP4b bulk fact pass, identical to the
    per-page ``fact_passages``). ``axis_rank`` only RANKS the
    passages (R3) -- it never changes which are read or what they
    hold -- so the read set is rank-independent and the pass needs no
    store-axis build. The per-page order is ``build_passages``'
    (sections in read order, then the lead, then the fact values): the
    order never enters the content-addressed window id, but the
    universe reads like the extractor."""
    from scriptengine.ingest.events import (
        panel_sentences,
        scope_plan,
    )
    from scriptengine.ingest.wikitext import strip_markup

    # The production queue: scope_plan('all') = the placement rule's
    # pages + the corpus rule's pages + the R1 prose scope's pages +
    # the R10 fact scope's pages; by_page[page] = the page's read
    # sections (the rules' union, deduped by id, in the extractor's
    # read order).
    pages, by_page = scope_plan(store, "all")
    queue = set(pages)

    # The extractor's LEAD read (`lead_passage`'s rule, bulked): only a
    # QUEUED page's lead is read (build_passages appends it per queued
    # page), and only when it holds a panel-eligible sentence -- the
    # counted `lead_dropped` class, never silently dropped.
    lead_text = {}
    for row in store.connection.execute(
        "SELECT title AS page, lead FROM documents"
        " WHERE COALESCE(lead, '') <> ''"
    ):
        if row["page"] not in queue:
            continue
        lead = strip_markup(row["lead"]).strip()
        if lead and panel_sentences(lead):
            lead_text[row["page"]] = lead

    # The extractor's SECTION read: scope_plan's by_page selection, NOT
    # "every panel-eligible section in the store" (the U-WP4 rule).
    # build_passages floors no section -- the floor was applied when the
    # scope SELECTED it (the panel test on the prose rule, the word
    # floor on the placement rule) -- so the universe carries the
    # selected sections as read (a selection holding no sentence builds
    # no windows, and D6 checks it the way the extractor reads it).
    sections = {}
    for page in pages:
        for section in by_page[page]:
            text = (section["text"] or "").strip()
            if text:
                sections.setdefault(page, []).append(
                    ((section["title"] or "").strip(), text)
                )

    # The extractor's FACT read: the U-WP4b bulk pass (label-for-label
    # the per-page `fact_passages`; a page with a narrative fact value
    # is in the queue via the R10 fact scope, so the pass over all
    # pages is the union over the queue's pages).
    facts_by_page = bulk_fact_passages(store)

    # Per-page order is build_passages' (sections in read order, then
    # the lead, then the fact values) -- the order never enters the
    # content-addressed id, but the universe reads like the extractor.
    out = []
    for page in sorted(queue):
        for label, text in sections.get(page, []):
            out.append((page, label, text))
        if page in lead_text:
            out.append((page, "lead", lead_text[page]))
        for label, text in facts_by_page.get(page, []):
            out.append((page, label, text))
    return out


def row_passage_text(store, row):
    """The text a stored event row was read from -- the same resolution
    `events._row_passage_text` uses (section, lead, or a declared fact
    value holding the quote)."""
    from scriptengine.ingest.wikitext import strip_markup

    # The csm store predates the `passage` column (U-WP4, 2026-10-04):
    # its rows are section-addressed only (a NULL section_id is the lead
    # read), so the passage is the empty string and the resolution below
    # lands on the section / the lead exactly as it does for a modern
    # row with no passage.
    has_passage = "passage" in row.keys()
    passage = (row["passage"] or "") if has_passage else ""
    if row["section_id"] is not None and not passage:
        hit = store.connection.execute(
            "SELECT text FROM sections WHERE id = ?", (row["section_id"],)
        ).fetchone()
        return (hit["text"] if hit else "") or ""
    if passage.startswith("fact:"):
        quote = (row["quote"] or "")[:60]
        for (value,) in store.connection.execute(
            "SELECT f.value FROM facts f JOIN nodes n ON n.id = f.node_id"
            " JOIN documents d ON d.id = n.document_id"
            " WHERE d.title = ? COLLATE NOCASE AND f.key = ?",
            (row["doc_title"], passage[5:]),
        ):
            text = strip_markup(value or "")
            if quote in text:
                return text
        return ""
    hit = store.connection.execute(
        "SELECT lead FROM documents WHERE title = ? COLLATE NOCASE",
        (row["doc_title"],),
    ).fetchone()
    return strip_markup((hit["lead"] if hit else "") or "")


def build_universe_windows(store, uni=None):
    """The grid's windows, keyed the way the store's rows address them.

    A window id hashes (gen, page, section-label, sub, span, the
    window's sentence-hash list) -- content-addressed (2026-10-04), so
    same-titled sections of one page (the wiki has 7 of them) with
    different text get distinct ids; only identical text under one
    (page, label) collapses to one id, and the first-read copy is kept,
    the collapse counted, not silently dropped. The section-keyed map
    keeps the union so a stored row quoting either copy still maps.
    ``uni`` (a ``universe(store)`` list) may be passed in so the store
    is walked once when the caller also maps gold onto the same texts."""
    if uni is None:
        uni = universe(store)
    windows = []
    seen_ids = set()
    duplicate_ids = 0
    by_key = {}
    for page, label, text in uni:
        built = build_windows(page, label, text, gen=CURRENT_GEN)
        if not built:
            continue
        for w in built:
            if w.id in seen_ids:
                duplicate_ids += 1
                continue
            seen_ids.add(w.id)
            windows.append(w)
        by_key.setdefault((page, label), []).extend(built)
    return windows, by_key, duplicate_ids


def _has_events_table(store):
    """U-WP4 (2026-10-04): some stores carry NO `events` table at all --
    the six anime wikis with no teacher rows (no extraction trace was
    ever run). The evidence map is then empty and the read-page set is
    empty: a genuine "never read", not a crash and not a guess."""
    row = store.connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='events'"
    ).fetchone()
    return row is not None


def map_evidence(store, by_key):
    """Which windows the store's own rows state something in.

    Returns (verbs_per_window, unmapped_rows): a window is non-empty when
    at least one stored quote maps into it via the grid (a quote the grid
    does not carry in one window is counted unmapped -- the window-level
    G1's loud failure, not a silent attribute). A store with no events
    table (U-WP4's six anime wikis) maps nothing: the empty map is the
    "never read" signal, not an error."""
    verbs = {}
    unmapped = 0
    if not _has_events_table(store):
        return verbs, unmapped
    for row in store.connection.execute("SELECT * FROM events"):
        text = row_passage_text(store, row)
        quote = row["quote"] or ""
        # The csm store predates the `passage` column (U-WP4, 2026-10-04):
        # its rows are section-addressed only, and a NULL section_id is
        # the lead read. Modern rows keep the exact old logic (the legacy
        # branch is dead for them).
        legacy = "passage" not in row.keys()
        passage = (row["passage"] or "") if not legacy else ""
        if row["section_id"] is not None and not passage:
            label = store.connection.execute(
                "SELECT title FROM sections WHERE id = ?", (row["section_id"],)
            ).fetchone()
            label = (label["title"] or "").strip() if label else ""
        elif passage == "lead" or (legacy and row["section_id"] is None):
            label = "lead"
        else:
            label = passage  # `fact:<key>`: not in the section/lead universe
        if not text or not quote:
            unmapped += 1
            continue
        built = by_key.get((row["doc_title"] or "", label))
        if built is None:
            unmapped += 1
            continue
        span = quote_grid_span(text, quote)
        if span is None:
            unmapped += 1
            continue
        a, b = span
        for window in built:
            if window.s_start <= a and b <= window.s_end:
                verbs.setdefault(window.id, set()).add((row["verb"] or "").lower())
                break
        else:
            unmapped += 1  # the quote is in the passage, no window carries it
    return verbs, unmapped


def holdout_pages(paths_root):
    """The held-out pages: the v1 dev/test record pages unioned with the
    blind test gold's pages (recall_gold_v3/windows_100.json, when
    present). Split by PAGE, never by row (plan/JJK_STUDENT_TRAINING.md
    section 4): a held-out page never trains, and the old gold600/pilot400
    respected that (0 overlap). The gen-2 emitter dropped the rule on the
    way in -- 207/1,500 pool windows sat on v1 dev/test pages and 40/56
    blind-gold pages appeared in the pools (2026-10-04)."""
    pages = set()
    for name in ("v1/dev.jsonl", "v1/test.jsonl"):
        path = paths_root / "training" / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                page = (json.loads(line) or {}).get("page")
                if page:
                    pages.add(page)
    blind = paths_root / "training" / "recall_gold_v3" / "windows_100.json"
    if blind.exists():
        for rec in json.loads(blind.read_text(encoding="utf-8")):
            if rec.get("page"):
                pages.add(rec["page"])
    # The series' own recorded holdout (WP6, 2026-10-04): the test pool's
    # pages, written by emit_windows -- a series with a page-disjoint test
    # pool records those pages here so the train pools never sample them.
    recorded = paths_root / "training" / "holdout_pages.json"
    if recorded.exists():
        data = json.loads(recorded.read_text(encoding="utf-8"))
        pages.update(data["pages"] if isinstance(data, dict) else data)
    return pages


def gold_window_ids(uni, gold_path, statuses=None):
    """The window ids the gold file's records cover, RECOMPUTED on the
    current grid (2026-10-04): the file's stored ids are only valid until
    the next id-scheme or store change (WP1 changed the scheme, WP3
    re-runs the re-key), so they are never trusted. Each record's
    (page, section, passage) is located on the universe's own text and
    the windows whose spans cover it supply the ids -- the same
    mechanical rule as rekey_gold.py. A gold window re-verified in a
    pool wastes 35B time. ``statuses`` (WP3b-2, 2026-10-04): when given,
    only records whose rekey status is in the set contribute -- the
    pilot exclusion is kept/reexpressed only (their windows are already
    adjudicated); reread/straddle windows STAY eligible, the 35B re-read
    owns them. Returns (ids, mapped, unmapped, records, eligible):
    records = every record in the file, eligible = the ones the filter
    admitted (== records when unfiltered); a missing file is the empty
    set (a series with no re-keyed gold yet)."""
    path = Path(gold_path)
    if not path.exists():
        return set(), 0, 0, 0, 0
    # The universe's own (page, label) -> text map: building the windows
    # on exactly these texts makes the recomputed ids identical to the
    # sampling universe's (same text, same builder, same gen), whatever
    # duplicate-titled sections a page carries.
    texts = {}
    for page, label, text in uni:
        texts.setdefault((page, label), set()).add(text)
    ids = set()
    mapped = unmapped = records = 0
    grid_cache = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        records += 1
        if statuses is not None and \
                (record.get("rekey") or {}).get("status") not in statuses:
            continue  # not excluded: the 35B re-read owns those windows
        page = (record.get("page") or "").strip()
        label = (record.get("section") or "").strip() or "lead"
        user = record["messages"][1]["content"]
        at = user.find("Passage:\n")
        passage = user[at + len("Passage:\n"):].strip() if at >= 0 else ""
        if not passage:
            unmapped += 1
            continue
        covering = []
        for text in sorted(texts.get((page, label), ())):
            windows = grid_cache.setdefault(
                (page, label, text),
                build_windows(page, label, text, gen=CURRENT_GEN),
            )
            span = quote_grid_span(text, passage)
            covering += [
                w for w in windows
                if span is not None and w.s_start <= span[0] and span[1] <= w.s_end
            ]
        if covering:
            ids.update(w.id for w in covering)
            mapped += 1
        else:
            unmapped += 1
    return ids, mapped, unmapped, records, mapped + unmapped


def sample_pool(rng, candidates, k, weights=None):
    """k distinct items, weighted without replacement (Efraimidis-Spirakis).

    An item's key is -ln(u) / weight (u uniform); the SMALLEST k keys are
    the sample -- equivalently the largest k of u**(1/weight) -- which is
    the exact weighted-without-replacement draw and is stable for a seed.
    Higher weight -> smaller key on average -> more often in the top.
    With no weights this reduces to a uniform sample."""
    keyed = []
    for item in candidates:
        w = 1.0 if weights is None else weights(item)
        keyed.append((-math.log(rng.random()) / w, item))
    keyed.sort(key=lambda pair: pair[0])
    return [item for _k, item in keyed[:k]]


def es_page_pick(rng, items, weights=None):
    """The single Efraimidis-Spirakis winner over `items` (one-window
    picks, the WP6b test pool): the same key rule as sample_pool, only
    the one best key -- a page's window is drawn the way the pool draws
    it (rare x3 on the non-empty side), one per page per pass."""
    best_key, best = None, None
    for item in items:
        w = 1.0 if weights is None else weights(item)
        key = -math.log(rng.random()) / w
        if best_key is None or key < best_key:
            best_key, best = key, item
    return best


def read_pages_set(store):
    """WP6b (2026-10-04): the READ pages -- pages with >= 1 event row,
    i.e. the teacher extracted something from them. Every other page is
    NEVER-READ: it carries no extraction trace, so its windows are
    'no evidence' (never read), not 'empty' (read, nothing stated).
    Conflating the two is the artifact that made the MCU pool's empty
    share 0.976 -- the strata stratify on the read pages only. A store
    with no events table (U-WP4's six anime wikis) has NO read pages:
    the empty set, not a crash."""
    if not _has_events_table(store):
        return set()
    return {row["doc_title"] for row in
            store.connection.execute("SELECT DISTINCT doc_title FROM events")}


def page_types(store):
    """WP6b: the documents table's page_type per title ('' -> <none>) --
    the strata's page-type mix is reported, never assumed."""
    out = {}
    for row in store.connection.execute("SELECT title, page_type FROM documents"):
        out[row["title"]] = (row["page_type"] or "").strip() or "<none>"
    return out


def load_era_map(series):
    """U-WP4: the U-WP2 era stamp (series/<s>/training/era.json):
    {page: {year, era, source, [story_year], sections{title: year}}}.
    None when the file is absent (the era mode then refuses to run: a
    missing stamp is an error, not a guess)."""
    path = ROOT / "series" / series / "training" / "era.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def window_era(w, era_map):
    """U-WP4: the window's era -- the U-WP2c section rule: a section the
    page's `sections` map carries (a dated issue/media title, e.g. a
    2012 film section on an actor page) dates ITS windows, else the
    page's own era. None when the page has no stamp row at all."""
    rec = era_map.get(w.page)
    if rec is None:
        return None
    if w.section != "lead":
        year = (rec.get("sections") or {}).get(w.section)
        if year is not None:
            return era_of(year)
    return rec["era"]


def uwp4_cells(mode, n_total):
    """U-WP4: the pool's cell list [(cell, quota, kind)] summing to
    `n_total`, in fill order (deterministic). `kind` is the cell's
    sampling rule: `read`/`evidence` stratify at the measured cell
    non-empty share (rare x3 on the non-empty side); `proxy` is a
    uniform draw. era: 3 thirds (a remainder to the earliest) x 50/50
    read/never-read inside each third (the odd window to read).
    eventish: the U-WP3 proxy 50/50 (the odd window to eventish).
    evidence (csm): the read pages at 50/50 of the pool (the odd one
    to read), the never-read half the proxy 50/50 (the odd one to
    eventish)."""
    if mode == "era":
        base, rem = divmod(n_total, 3)
        out = []
        for i, third in enumerate(("old", "mid", "new")):
            q = base + (1 if i < rem else 0)
            n_read = (q + 1) // 2
            out += [(f"{third}-read", n_read, "read"),
                    (f"{third}-never_read", q - n_read, "proxy")]
        return out
    if mode == "eventish":
        n_ev = (n_total + 1) // 2
        return [("eventish", n_ev, "proxy"),
                ("non_eventish", n_total - n_ev, "proxy")]
    # evidence (csm): read 50/50 by the measured evidence, the
    # never-read half the proxy 50/50.
    n_read = (n_total + 1) // 2
    n_nr = n_total - n_read
    n_nr_ev = (n_nr + 1) // 2
    return [("read_evidence", n_read, "evidence"),
            ("never_read_eventish", n_nr_ev, "proxy"),
            ("never_read_non_eventish", n_nr - n_nr_ev, "proxy")]


def pool_line(i, w, extra=None):
    """The pool line (the old campaign shape + the builder's identity
    fields); `extra` (U-WP4: era/page_type or the eventish flag) is
    appended, so the pre-U-WP4 lines are byte-identical for a None."""
    line = {
        "n": i,
        "id": w.id,
        "page": w.page,
        "section": "" if w.section == "lead" else w.section,
        "passage": w.text,
        "gen": w.gen,
        "sub": w.sub,
    }
    if extra:
        line.update(extra)
    return line


def write_holdout_json_merged(hj, series, pool, seed, test_pages, entry,
                              note):
    """U-WP4: record the test pool's pages in the series' holdout,
    MERGED with earlier pools' entries (WP6b wrote one pool per file;
    a series' SECOND pool must keep the first pool's pages recorded,
    or they would silently re-enter the train universe). The file is
    a record, not an input: a re-run re-merges to identical bytes (the
    same pages, the same entries). A WP6b flat file is migrated into
    the `pools` list (its fields kept); a bare page list is kept as
    pages with no identity (counted, never guessed)."""
    pools = []
    old_pages = set()
    if hj.exists():
        data = json.loads(hj.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            if "pools" in data:
                pools = [e for e in data["pools"] if e.get("pool") != pool]
            elif "pool" in data:
                # WP6b flat file: migrate the single entry; its top-level
                # `pages` list belongs to that one pool (carry it, or a
                # re-run would lose the reservation and re-pick the pages
                # of the older pool).
                legacy = {k: data[k] for k in
                          ("pool", "seed", "count", "read_n", "unread_n",
                           "note") if k in data}
                legacy["pages"] = list(data.get("pages") or [])
                if legacy.get("pool") != pool:
                    pools.append(legacy)
            old_pages = set(data.get("pages", []))
        elif isinstance(data, list):
            old_pages = set(data)
    pools.append(entry)
    # Canonical entry order (pool name), independent of which emit path
    # last re-merged -- the record's bytes are stable across paths.
    pools.sort(key=lambda e: e.get("pool") or "")
    pages = sorted(old_pages | set(test_pages))
    hj.parent.mkdir(parents=True, exist_ok=True)
    hj.write_text(
        json.dumps({"series": series, "count": len(pages), "pages": pages,
                    "pools": pools, "note": note},
                   indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    return pages


def assert_pool_invariants(picks, holdout, gold_ids):
    """The WP2 gate (2026-10-04): exit non-zero on any failure. The
    pre-stratification exclusions make these pass by construction; the
    assertions are the belt -- a future edit that re-introduces a leak
    (a held-out page in a pool, a gold window re-verified in a pool)
    fails the emit loudly instead of wasting the 35B campaign on it."""
    items = list(picks.items())
    for i, (name_a, ws_a) in enumerate(items):
        ids_a = {w.id for w in ws_a}
        for name_b, ws_b in items[i + 1:]:
            shared = ids_a & {w.id for w in ws_b}
            if shared:
                sys.exit(f"assertion: pools {name_a} and {name_b} share "
                         f"{len(shared)} window id(s) (e.g. {sorted(shared)[:3]})")
    for name, ws in items:
        ids = [w.id for w in ws]
        if len(ids) != len(set(ids)):
            sys.exit(f"assertion: pool {name} has duplicate window ids")
        leaked = {w.page for w in ws} & holdout
        if leaked:
            sys.exit(f"assertion: pool {name} has {len(leaked)} held-out "
                     f"page(s) (e.g. {sorted(leaked)[:3]})")
        gold_hits = {w.id for w in ws} & gold_ids
        if gold_hits:
            sys.exit(f"assertion: pool {name} contains {len(gold_hits)} "
                     f"gold window id(s) (e.g. {sorted(gold_hits)[:3]})")


def emit(series, pools, n, seed, dry_run, do_archive, out_dir=None,
         do_holdout=True, gold_path=None, pilot_path=None,
         test_pool=None, test_read_n=70, test_unread_n=30,
         test_per_page_max=2, holdout_json=None,
         stratify_read=None, stratify_unread=None,
         archive_suffix=".old-grid",
         era_thirds=False, undated_policy="exclude",
         eventish_split=False, read_evidence=False, test_n=None):
    paths_root = ROOT / "series" / series
    db = paths_root / "facts.db"
    if not db.exists():
        sys.exit(f"{series} is not indexed (no {db}); run `index` first")
    t0 = time.time()
    holdout = holdout_pages(paths_root) if do_holdout else set()
    with FactStore(db) as store:
        uni = universe(store)
        windows, by_key, duplicate_ids = build_universe_windows(store, uni)
        verbs, unmapped_rows = map_evidence(store, by_key)
        gold_ids, gold_mapped, gold_unmapped, gold_records, gold_eligible = \
            gold_window_ids(uni, gold_path)
        # WP3b-2 (2026-10-04): the pilot's ADJUDICATED windows (kept /
        # reexpressed) are excluded too -- re-verifying them in a pool
        # wastes 35B time. reread/straddle STAY eligible: the 35B
        # re-read owns those windows.
        pilot_ids, pilot_mapped, pilot_unmapped, pilot_records, \
            pilot_eligible = gold_window_ids(
                uni, pilot_path, statuses=("kept", "reexpressed"))
        gold_ids_all = gold_ids | pilot_ids
        # WP6b: the read/never-read split and the page types are only
        # needed by the strata paths (a plain jjk emit runs no new query).
        # U-WP4 needs them too (the read/never-read cells + the page-type
        # mix of the new pools).
        read_pages, ptypes = set(), {}
        uwp4_mode = ("era" if era_thirds
                     else ("evidence" if read_evidence
                           else ("eventish" if eventish_split else None)))
        if (test_pool or stratify_read is not None
                or stratify_unread is not None or uwp4_mode):
            read_pages = read_pages_set(store)
            ptypes = page_types(store)

    holdout_windows = [w for w in windows if w.page in holdout]
    gold_windows = [w for w in windows if w.id in gold_ids]
    pilot_windows = [w for w in windows if w.id in pilot_ids]
    gold_windows_all = [w for w in windows if w.id in gold_ids_all]
    # Excluded BEFORE stratification (WP2/WP3b-2): the empty share is
    # measured on what is left to sample, not on the full universe --
    # council C6's "measure, never carry over" applies to the post-
    # exclusion universe.
    sample_universe = [
        w for w in windows
        if w.page not in holdout and w.id not in gold_ids_all
    ]

    # U-WP4 (2026-10-04): the era mode reads the U-WP2 stamp once; the
    # cell assignment (both the test pool's and the train pools') is
    # one pure function, so a re-run assigns the same cells.
    era_map = None
    if uwp4_mode == "era":
        era_map = load_era_map(series)
        if era_map is None:
            sys.exit(f"--era-thirds needs {paths_root / 'training' / 'era.json'} "
                     f"(run tools/train/era_stamp.py --series {series} first)")

    def cell_of(w):
        """U-WP4: the window's pool cell (the mode's stratum key), or
        None when the window is NOT samplable: marvel's undated pages
        (excluded from sampling, counted in the receipt) and any page
        with no era stamp row (counted, never guessed)."""
        if uwp4_mode == "era":
            era = window_era(w, era_map)
            if era is None or (era == "undated"
                               and undated_policy == "exclude"):
                return None
            stratum = ("old" if (era == "undated"
                                 and undated_policy == "old") else era)
            kind = "read" if w.page in read_pages else "never_read"
            return f"{stratum}-{kind}"
        if uwp4_mode == "evidence":
            if w.page in read_pages:
                return "read_evidence"
            return ("never_read_eventish" if is_eventish(w.text)
                    else "never_read_non_eventish")
        if uwp4_mode == "eventish":
            return "eventish" if is_eventish(w.text) else "non_eventish"
        return None

    # WP6b (2026-10-04): the SPREAD test pool -- test_read_n windows from
    # READ pages (>= 1 event row: stratified at the measured read-page
    # non-empty share, rare x3, exactly like the train pool's read
    # stratum) + test_unread_n from NEVER-READ pages (uniform), at most
    # test_per_page_max windows per page; the one-per-page pass runs
    # first, so 100 windows at cap 2 span ~100 distinct pages, never 50.
    # The pages are sampled seeded BEFORE the train pools, recorded to
    # --holdout-json (the series' holdout), and excluded from the train
    # sampling universe (page-disjoint by construction).
    #
    # The candidates come from the FULL universe (minus gold and the
    # non-recorded holdout), not sample_universe: on a re-run the
    # recorded test pages already sit in holdout_pages() and out of
    # sample_universe, which would empty the candidate set. The same
    # seeded draw over the same candidate set reproduces the
    # byte-identical pool on a re-run (idempotent); the recorded json
    # is the record, not the input.
    test_picks, test_pages = [], set()
    test_read_picks, test_unread_picks = [], []
    read_nonempty_share = 0.0
    archived = []
    # U-WP4 (2026-10-04, plan/UNIVERSAL_DATASET_PLAN.md): the universal
    # spread test pool -- the WP6b mechanism (seeded BEFORE the train
    # pools, recorded to --holdout-json, excluded from the train
    # sampling universe) re-stratified on the pool's own cells (the era
    # thirds x read/never-read, the eventish 50/50, or csm's
    # read-evidence/never-read-proxy). Two additions over WP6b:
    # (1) the per-page cap is GLOBAL across cells (a page's windows may
    # sit in two era cells -- the section-era rule): a page takes a
    # second window only while its TOTAL allocation is under the cap;
    # (2) the candidate universe also excludes the pages of the wiki's
    # OTHER train pool files -- the plan's page-disjoint is against
    # EVERY train pool of the wiki, and the exclusion set is stable
    # across re-runs (the current run's own pool names are exempt from
    # it, so a same-seed re-run sees the same candidate set and
    # reproduces the pool byte-for-byte). U-WP4b adds a third rule:
    # once a pool's pages are recorded, a re-run re-derives the pool's
    # windows on THOSE pages (sticky) instead of re-rolling the draw
    # (the record is a record, not an input; see the exclusion-set
    # comment below).
    uwp4_test_strata = {}
    era_receipt = None
    if test_pool and uwp4_mode:
        if test_n is None:
            sys.exit("assertion: a U-WP4 test pool needs --test-n "
                     f"(the {test_pool} pool's window count)")
        # The exclusion set (every member stable across a same-seed
        # re-run, see above): the v1/blind holdout pages not recorded
        # for THIS pool + the pages recorded for OTHER pools (the
        # holdout json's other entries) + the pages of the wiki's
        # OTHER train pool files (this wiki's test-pool files are
        # already recorded, so they come in through the json).
        recorded_current, reserved_other = set(), set()
        # U-WP4c: the recorded entry for THIS pool -- the re-merge's
        # record: a sticky re-emit re-merges it UNCHANGED (the holdout
        # json re-writes to the same bytes; only a fresh draw writes a
        # new entry).
        recorded_entry = None
        if holdout_json and Path(holdout_json).exists():
            data = json.loads(Path(holdout_json).read_text(encoding="utf-8"))
            if isinstance(data, dict):
                if "pools" in data:
                    for e in data["pools"]:
                        pg = e.get("pages")
                        if isinstance(pg, (list, tuple, set)):
                            pg = set(pg)
                        else:
                            # The broken first U-WP4 write (2026-10-04)
                            # stored the page COUNT, not the list; the
                            # top-level union is the only record of the
                            # actual names. A re-merge (writer above)
                            # rewrites the entry with the list, so this
                            # fallback is one-shot per file.
                            pg = set(data.get("pages") or [])
                        if e.get("pool") == test_pool:
                            recorded_current |= pg
                            recorded_entry = e
                        else:
                            reserved_other |= pg
                elif "pool" in data:
                    pg = set(data.get("pages") or [])
                    if data.get("pool") == test_pool:
                        recorded_current |= pg
                        recorded_entry = data
                    else:
                        reserved_other |= pg
            elif isinstance(data, list):
                reserved_other |= set(data)  # no pool identity: reserve all
        opencode_dir = paths_root / "training" / "opencode"
        current_names = set(pools) | {test_pool}
        other_train_pages = set()
        if opencode_dir.exists():
            for pf in sorted(opencode_dir.glob("*_windows.jsonl")):
                base = pf.name[: -len("_windows.jsonl")]
                if base in current_names or not pf.is_file():
                    continue  # the current run's own (re)emit: re-run stability
                rows = [json.loads(l) for l in
                        pf.read_text(encoding="utf-8").splitlines()
                        if l.strip()]
                pgs = {r["page"] for r in rows}
                if rows and pgs <= holdout:
                    continue  # this wiki's test pool: already recorded
                other_train_pages |= pgs
        exclude = ((holdout - recorded_current) | reserved_other
                   | other_train_pages)
        # U-WP4b (2026-10-04): the recorded test pages are STICKY -- the
        # record is a record, not an input (the plan: the test pages are
        # recorded FIRST). A re-run re-derives the pool's WINDOWS on the
        # recorded pages; it does not re-roll the page draw. Without this,
        # a universe change (U-WP4b's fact passages) breaks the same-seed
        # re-run's fixed point: the holdout union keeps the older
        # selection's pages while the entry re-records the new draw, so
        # the next run's exclusion set changes and a fresh 75-page set is
        # reserved on every re-emit (measured 2026-10-04: 75 -> 147 ->
        # 222 per run, the entry drifting from the on-disk pool). A fresh
        # seeded draw runs only when the pool has no recorded entry (or
        # its pages all left the universe).
        #
        # U-WP4c (2026-10-04): the recorded POOL FILE is the record. A
        # re-emit re-DERIVES its lines on the current universe (each
        # line's (page, section, passage) re-located; the id is
        # content-addressed, so an unchanged store re-derives the same id
        # and the re-emit is byte-identical -- the re-emit cmp proof)
        # instead of re-rolling the fill: a re-roll re-shuffles the
        # recorded pages' windows (the fill's page order and RNG
        # consumption depend on the candidate set, which a re-run sees
        # shrunk to the recorded pages) and the pool would drift from its
        # own record. The draw is rolled exactly once, on the fresh
        # emit; the holdout entry is re-merged UNCHANGED (the json
        # re-writes to the same bytes). A fresh draw runs when the pool
        # has no recorded entry, or no recorded pool file.
        record_path = (paths_root / "training" / "opencode"
                       / f"{test_pool}_windows.jsonl")
        sticky_picks = None
        if recorded_current and record_path.exists():
            sticky_lines = [
                json.loads(l) for l in
                record_path.read_text(encoding="utf-8").splitlines()
                if l.strip()
            ]
            if sticky_lines:
                # The universe's own (page, label, window-text) index:
                # the same texts + builder + gen that built the pool at
                # draw time, so an unchanged store re-derives the same
                # window (id and all).
                win_by_text = {}
                for w in windows:
                    win_by_text.setdefault(
                        (w.page, w.section, w.text), []).append(w)
                sticky_picks = []
                for line in sticky_lines:
                    label = (line.get("section") or "") or "lead"
                    cands = win_by_text.get((line["page"], label,
                                             line["passage"]))
                    if not cands:
                        sys.exit(f"assertion: recorded test pool "
                                 f"{test_pool} line {line['n'] + 1} "
                                 f"({line['id']}, page {line['page']!r}) "
                                 f"does not re-derive on the current "
                                 f"store (drift); let dataset_gates D2 "
                                 f"explain the cause before re-emitting")
                    if len(cands) > 1:
                        # Identical window text under one (page, label):
                        # the universe's own collapse kept the first
                        # read; prefer the line's sub, fall back to the
                        # first.
                        cands = ([x for x in cands
                                  if x.sub == line.get("sub")] or cands)
                    sticky_picks.append(cands[0])

        if sticky_picks is not None:
            # The re-emit: the draw is NOT re-rolled (the record is a
            # record, not an input); the pool's lines re-derive on the
            # current store, and the holdout json re-merges the RECORDED
            # entry unchanged (the same bytes, the same page union).
            test_picks = sticky_picks
            test_pages = {w.page for w in test_picks}
            req_pages = min(60, test_n)
            if len(test_pages) < req_pages:
                sys.exit(f"assertion: test pool {test_pool} spans only "
                         f"{len(test_pages)} distinct pages (requirement: "
                         f">= {req_pages})")
            # The recorded strata, recomputed on the re-derived picks
            # (the receipt's numbers; the record's bytes unchanged).
            uwp4_test_strata = {
                c: sum(1 for w in test_picks if cell_of(w) == c)
                for c, _q, _k in uwp4_cells(uwp4_mode, test_n)
            }
            if holdout_json and not dry_run:
                # U-WP4c: the json IS the record (the recorded entry +
                # the page union); the re-emit re-derives the pool on
                # the recorded pages, so there is nothing new to
                # record -- a rewrite would only change the top-level
                # note (the writer's), breaking byte-identity. Write
                # only when the recorded entry is in the broken first
                # U-WP4 shape (its `pages` a count, not a list -- the
                # one-shot fix the writer performs), else leave the
                # record's bytes untouched.
                list_pages = (recorded_entry is not None
                               and isinstance(
                                   recorded_entry.get("pages"),
                                   (list, tuple)))
                if not list_pages:
                    pages_now = write_holdout_json_merged(
                        Path(holdout_json), series, test_pool, seed,
                        test_pages, recorded_entry,
                        note=("U-WP4c (2026-10-04, tools/train/emit"
                              "_windows.py): one-shot shape fix of the "
                              "recorded entry (its `pages` was a count, "
                              "not a list)."))
                    archived.append(
                        f"holdout pages -> {Path(holdout_json).name} "
                        f"({len(pages_now)} pages; {test_pool} "
                        f"{len(test_pages)})")
                else:
                    archived.append(
                        f"holdout pages -> {Path(holdout_json).name} "
                        f"(kept: the recorded entry, byte-identical)")
            # The test pages are out of the TRAIN sampling universe.
            sample_universe = [w for w in sample_universe
                               if w.page not in test_pages]
        else:
            # The FRESH draw (no recorded entry, or no recorded pool
            # file): the seeded page draw, recorded to --holdout-json.
            # Recorded-but-file-missing keeps the U-WP4b rule: the draw
            # runs on the recorded pages (their windows), a fresh
            # universe-wide draw only when no recorded page survives.
            if recorded_current:
                uni_pages = {w.page for w in windows}
                keep = recorded_current & uni_pages
                if keep:
                    missing = recorded_current - uni_pages
                    if missing:
                        print(f"note: {len(missing)} recorded test page(s) for "
                              f"{test_pool} carry no window on the current "
                              f"store (e.g. {sorted(missing)[:3]}); they stay "
                              f"reserved in the holdout union", file=sys.stderr)
                    test_cand_universe = [w for w in windows
                                          if w.id not in gold_ids_all
                                          and w.page in recorded_current]
                else:
                    test_cand_universe = [w for w in windows
                                          if w.id not in gold_ids_all
                                          and w.page not in exclude]
            else:
                test_cand_universe = [w for w in windows
                                  if w.id not in gold_ids_all
                                  and w.page not in exclude]

            cells_spec = uwp4_cells(uwp4_mode, test_n)
            cell_windows = {c: [] for c, _q, _k in cells_spec}
            for w in test_cand_universe:
                c = cell_of(w)
                if c is not None:
                    cell_windows[c].append(w)
            cell_by_page = {c: {} for c in cell_windows}
            for c, ws in cell_windows.items():
                for w in ws:
                    cell_by_page[c].setdefault(w.page, []).append(w)
            # The measured per-cell non-empty share on the TEST-candidate
            # universe (pre-exclusion, the WP6b rule: a re-run's recorded
            # pages are already out, so the share is measured on the same
            # candidate set the first run saw).
            cell_share = {}
            for c, _q, k in cells_spec:
                if k in ("read", "evidence") and cell_windows[c]:
                    cell_share[c] = (sum(1 for w in cell_windows[c]
                                         if w.id in verbs)
                                     / len(cell_windows[c]))
                else:
                    cell_share[c] = 0.0
            # The seeded fills: per cell, a sorted+cell-seeded page order and
            # two passes (one window per page first, then a second while the
            # page's GLOBAL allocation is under the cap); the non-empty quota
            # of a read/evidence cell runs first (the rare x3, as WP6b). A
            # short cell (the store ran dry, or the page cap bound it)
            # CASCADES its deficit to the next cell, as the train pools:
            # the pool total is the hard requirement, the split is soft.
            fill_rng = random.Random(f"{seed}-{test_pool}-fill")
            rare_w = lambda w: 3.0 if RARE & verbs.get(w.id, set()) else 1.0
            alloc, used_ids = {}, set()
            gotc = {c: 0 for c, _q, _k in cells_spec}
            carry = 0
            for c, quota, k in cells_spec:
                need = quota + carry
                ne_need = round(need * cell_share[c]) if k in ("read", "evidence") else 0
                em_need = (need - ne_need) if k in ("read", "evidence") else need
                c_pages = sorted({w.page for w in cell_windows[c]})
                random.Random(f"{seed}-{test_pool}-{c}-pages").shuffle(c_pages)
                for pass_no in (1, 2):
                    if gotc[c] >= need:
                        break
                    for page in c_pages:
                        if gotc[c] >= need:
                            break
                        # Pass 1 is strictly ONE per page (the WP6b spread
                        # rule: N windows span ~N pages): a page that
                        # already holds a window (its windows may sit in
                        # two cells -- the section-era rule, or an
                        # eventish/non-eventish split of one page's
                        # windows) takes its second only in pass 2, while
                        # the global cap allows it (U-WP4c, 2026-10-04:
                        # the U-WP4b pass-1 could take a page's second
                        # window in pass 1, which shrank the page spread
                        # below the pool's spread floor once the U-WP4c
                        # universe shrank -- csm's 50-window test pool
                        # spanned 49 pages, 2026-10-04).
                        if pass_no == 1:
                            if alloc.get(page, 0) >= 1:
                                continue
                        elif alloc.get(page, 0) >= test_per_page_max:
                            continue
                        w = None
                        if k in ("read", "evidence"):
                            if ne_need > 0:
                                ws = [x for x in cell_by_page[c].get(page, [])
                                      if x.id in verbs and x.id not in used_ids]
                                if ws:
                                    w = es_page_pick(fill_rng, ws, rare_w)
                                    ne_need -= 1
                            if w is None and em_need > 0:
                                ws = [x for x in cell_by_page[c].get(page, [])
                                      if x.id not in verbs and x.id not in used_ids]
                                if ws:
                                    w = es_page_pick(fill_rng, ws)
                                    em_need -= 1
                        else:
                            ws = [x for x in cell_by_page[c].get(page, [])
                                  if x.id not in used_ids]
                            if ws:
                                w = es_page_pick(fill_rng, ws)
                        if w is not None:
                            test_picks.append(w)
                            used_ids.add(w.id)
                            alloc[page] = alloc.get(page, 0) + 1
                            gotc[c] += 1
                carry = need - gotc[c]  # the deficit cascades to the next cell
            if carry > 0:
                sys.exit(f"assertion: test pool {test_pool} short of its total "
                         f"({carry} window(s) the cascade cannot absorb; actual "
                         f"cell counts: "
                         f"{ {c: gotc[c] for c, _q, _k in cells_spec} })")
            test_pages = {w.page for w in test_picks}
            # The plan's page-spread requirement, quota-aware: the 150-window
            # hxh pool must span >= 60 pages; a smaller pool cannot span
            # more than its own window count (50 windows span <= 50 pages).
            req_pages = min(60, test_n)
            if len(test_pages) < req_pages:
                sys.exit(f"assertion: test pool {test_pool} spans only "
                         f"{len(test_pages)} distinct pages (requirement: "
                         f">= {req_pages})")
            random.Random(f"{seed}-{test_pool}-shuffle").shuffle(test_picks)
            uwp4_test_strata = {c: gotc[c] for c, _q, _k in cells_spec}
            if holdout_json and not dry_run:
                pages_now = write_holdout_json_merged(
                    Path(holdout_json), series, test_pool, seed, test_pages,
                    {"pool": test_pool, "seed": seed,
                     "windows": len(test_picks), "pages": sorted(test_pages),
                     "strata": uwp4_test_strata,
                     "per_page_max": test_per_page_max},
                    note=("U-WP4 (2026-10-04, tools/train/emit_windows.py): the "
                          "test pool's pages -- the series' holdout. The train "
                          "pools never sample these pages (page-disjoint by "
                          "construction); a re-run reuses the recorded pages. "
                          "Earlier pools' entries are kept (merged, never "
                          "clobbered)."))
                archived.append(f"holdout pages -> {Path(holdout_json).name} "
                                f"({len(pages_now)} pages; {test_pool} "
                                f"{len(test_pages)})")
            # The test pages are out of the TRAIN sampling universe.
            sample_universe = [w for w in sample_universe
                               if w.page not in test_pages]
    elif test_pool:
        recorded = set()
        if holdout_json and Path(holdout_json).exists():
            rec = json.loads(Path(holdout_json).read_text(encoding="utf-8"))
            recorded = set(rec["pages"] if isinstance(rec, dict) else rec)
        v1blind = holdout - recorded
        test_cand_universe = [w for w in windows
                              if w.id not in gold_ids_all
                              and w.page not in v1blind]
        cand_by_page = {}
        for w in test_cand_universe:
            cand_by_page.setdefault(w.page, []).append(w)
        # The read-page share WP6b measures (test side, pre-exclusion): 'no
        # event row' on a never-read page means NEVER READ, not empty --
        # so the share is measured on the READ pages only, and the test
        # pool's read side stratifies there. The TRAIN strata re-measure
        # it on their final universe (below) and stratify at that.
        test_read_uni = [w for w in test_cand_universe if w.page in read_pages]
        n_test_read_nonempty = sum(1 for w in test_read_uni if w.id in verbs)
        test_read_share = (n_test_read_nonempty / len(test_read_uni)
                           if test_read_uni else 0.0)
        pages_rng = random.Random(f"{seed}-pages")
        read_cand = sorted(p for p in cand_by_page if p in read_pages)
        unread_cand = sorted(p for p in cand_by_page if p not in read_pages)
        pages_rng.shuffle(read_cand)
        pages_rng.shuffle(unread_cand)
        test_rng = random.Random(f"{seed}-{test_pool}")
        rare_w = lambda w: 3.0 if RARE & verbs.get(w.id, set()) else 1.0
        ne_need = round(test_read_n * test_read_share)
        em_need = test_read_n - ne_need
        def pick_on(page, nonempty_only, exclude=()):
            ws = [w for w in cand_by_page.get(page, [])
                  if (w.id in verbs) == nonempty_only and w.id not in exclude]
            if not ws:
                return None
            return es_page_pick(test_rng, ws,
                                rare_w if nonempty_only else None)
        # READ side: pass 1 (one window per page, seeded page order, the
        # non-empty quota first), pass 2 (a second window per page).
        alloc, got = {}, []
        def fill_read(pages, pass_no):
            nonlocal ne_need, em_need
            for page in pages:
                if ne_need + em_need == 0:
                    break
                if pass_no > 1 and alloc.get(page, 0) >= test_per_page_max:
                    continue
                used = {w.id for w in got if w.page == page}
                w = None
                if ne_need > 0:
                    w = pick_on(page, True, used)
                    if w is not None:
                        ne_need -= 1
                if w is None and em_need > 0:
                    w = pick_on(page, False, used)
                    if w is not None:
                        em_need -= 1
                if w is not None:
                    got.append(w)
                    alloc[page] = alloc.get(page, 0) + 1
        fill_read(read_cand, 1)
        if ne_need + em_need > 0:
            fill_read(read_cand, 2)
        # NEVER-READ side: uniform, the same two passes.
        ur_need, ur_alloc, ur_got = test_unread_n, {}, []
        def fill_unread(pages, pass_no):
            nonlocal ur_need
            for page in pages:
                if ur_need == 0:
                    break
                if pass_no > 1 and ur_alloc.get(page, 0) >= test_per_page_max:
                    continue
                used = {w.id for w in ur_got if w.page == page}
                w = es_page_pick(
                    test_rng,
                    [x for x in cand_by_page.get(page, []) if x.id not in used])
                if w is not None:
                    ur_need -= 1
                    ur_got.append(w)
                    ur_alloc[page] = ur_alloc.get(page, 0) + 1
        fill_unread(unread_cand, 1)
        if ur_need > 0:
            fill_unread(unread_cand, 2)
        test_read_picks, test_unread_picks = got, ur_got
        test_picks = got + ur_got
        test_rng.shuffle(test_picks)
        test_pages = {w.page for w in test_picks}
        if len(got) != test_read_n or len(ur_got) != test_unread_n:
            sys.exit(f"assertion: test pool {test_pool} short of its "
                     f"quota (read {len(got)}/{test_read_n}, never-read "
                     f"{len(ur_got)}/{test_unread_n} candidate windows)")
        if len(test_pages) < 60:
            sys.exit(f"assertion: test pool {test_pool} spans only "
                     f"{len(test_pages)} distinct pages (requirement: "
                     f">= 60)")
        if holdout_json and not dry_run:
            # U-WP4: the WP6b write is MERGED too -- a series with a
            # second (U-WP4) test pool keeps the first pool's pages
            # recorded, and vice versa; a flat clobber would silently
            # re-open the other pool's pages to the train universe. The
            # entry's key order matches the legacy migration's, so a
            # re-merge of a migrated flat file is byte-identical.
            entry = {"pool": test_pool, "seed": seed,
                     "count": len(test_pages),
                     "read_n": test_read_n, "unread_n": test_unread_n,
                     "note": ("WP6b (2026-10-04, tools/train/emit_windows"
                              ".py): the test pool's pages -- the series' "
                              "holdout. The train pools never sample these "
                              "pages (page-disjoint by construction); a "
                              "re-run reuses the recorded pages.")}
            entry["pages"] = sorted(test_pages)
            pages_now = write_holdout_json_merged(
                Path(holdout_json), series, test_pool, seed, test_pages,
                entry,
                note=("U-WP4 (2026-10-04, tools/train/emit_windows.py): the "
                      "test pool's pages -- the series' holdout. The train "
                      "pools never sample these pages (page-disjoint by "
                      "construction); a re-run reuses the recorded pages. "
                      "Earlier pools' entries are kept (merged, never "
                      "clobbered)."))
            archived.append(f"holdout pages -> {Path(holdout_json).name} "
                            f"({len(pages_now)} pages; {test_pool} "
                            f"{len(test_pages)})")
        # The test pages are out of the TRAIN sampling universe.
        sample_universe = [w for w in sample_universe if w.page not in test_pages]

    nonempty = [w for w in sample_universe if w.id in verbs]
    empty = [w for w in sample_universe if w.id not in verbs]
    empty_share = len(empty) / len(sample_universe) if sample_universe else 0.0
    n_empty = round(n * empty_share)
    n_nonempty = n - n_empty

    if uwp4_mode == "era":
        # The era receipt counts, measured on the FINAL train universe
        # (post test-page exclusion when a test pool ran). marvel: the
        # undated pages are EXCLUDED from sampling, never guessed; mcu:
        # folded into the old third by the plan's rule (the pool line
        # keeps their real era `undated`).
        n_undated_pages = sum(1 for r in era_map.values()
                              if r["era"] == "undated")
        n_undated_windows = sum(
            1 for w in sample_universe if window_era(w, era_map) == "undated")
        n_missing_pages = len({w.page for w in sample_universe
                               if era_map.get(w.page) is None})
        era_receipt = {
            "undated_policy": undated_policy,
            "undated_pages": n_undated_pages,
            ("undated_windows_excluded" if undated_policy == "exclude"
             else "undated_windows_in_old_third"): n_undated_windows,
            "pages_missing_era_stamp": n_missing_pages,
            "note": ("a window's era is its section's when the page's "
                     "`sections` map carries the section, else the "
                     "page's era (U-WP2c); the pool line records the "
                     "REAL era (an mcu undated window says `undated` "
                     "and sits in the old third)"),
        }

    pool_dir = (
        Path(out_dir) if out_dir else paths_root / "training" / "opencode"
    )
    pools_dir = pool_dir
    receipt = {
        "series": series,
        "gen": CURRENT_GEN,
        "universe_windows": len(windows),
        "duplicate_window_ids": duplicate_ids,
        "holdout_pages": len(holdout),
        "holdout_windows_excluded": len(holdout_windows),
        "gold_records": gold_records,
        "gold_records_unmapped": gold_unmapped,
        "gold_windows_excluded": len(gold_windows),
        "pilot_records": pilot_records,
        "pilot_kept_reexpressed": pilot_eligible,
        "pilot_kept_reexpressed_unmapped": pilot_unmapped,
        "pilot_windows_excluded": len(pilot_windows),
        "gold_windows_excluded_total": len(gold_windows_all),
        "sample_universe_windows": len(sample_universe),
        "nonempty_windows": len(nonempty),
        "empty_windows": len(empty),
        "empty_share_remeasured": round(empty_share, 4),
        "evidence_rows_unmapped": unmapped_rows,
        "pools": {},
        "archived": archived,
        "dry_run": dry_run,
    }

    # U-WP4: the pool line's extra fields (era mode: the window's REAL era
    # (mcu undated windows say `undated`) + the source documents.page_type;
    # proxy/evidence modes: the U-WP3 flag). None pre-U-WP4, so the old
    # lines stay byte-identical.
    def line_extra(w):
        if uwp4_mode == "era":
            return {"era": window_era(w, era_map),
                    "page_type": ptypes.get(w.page, "<none>")}
        if uwp4_mode in ("eventish", "evidence"):
            return {"eventish": is_eventish(w.text)}
        return None

    taken = set()
    picks = {}
    pool_strata = {}
    uwp4_pool_strata = {}
    stratified = (stratify_read is not None or stratify_unread is not None)
    if stratified:
        read_uni = [w for w in sample_universe if w.page in read_pages]
        unread_uni = [w for w in sample_universe if w.page not in read_pages]
        # The stratification share, measured on THIS final train universe
        # (post test-page exclusion when a test pool ran) -- the
        # strata stratify at it (WP6b).
        read_nonempty_share = (
            sum(1 for w in read_uni if w.id in verbs) / len(read_uni)
            if read_uni else 0.0)
        # The strata receipt (WP6b): a READ page's 'empty' window is a
        # genuine empty (the teacher read the page, no event was
        # stated); a NEVER-READ page's window carries no evidence
        # either way -- the student sees it as a page type the teacher
        # never read.
        receipt["strata"] = {
            "read_pages": len({w.page for w in read_uni}),
            "never_read_pages": len({w.page for w in unread_uni}),
            "read_nonempty_share_remeasured": round(read_nonempty_share, 4),
            "read_empty_share_remeasured": round(1 - read_nonempty_share, 4),
            "note": ("WP6b (2026-10-04): 'empty' is measured on READ "
                     "pages (>= 1 event row) only -- never-read pages "
                     "carry no evidence, so their windows are a uniform "
                     "stratum, not empties"),
        }
    for pool in pools:
        pool_rng = random.Random(f"{seed}-{pool}")
        if uwp4_mode:
            # U-WP4 (2026-10-04, plan/UNIVERSAL_DATASET_PLAN.md): the
            # universal strata. era thirds x read/never-read (the read
            # side at the MEASURED per-cell non-empty share, rare x3 on
            # the non-empty side, the never-read side uniform) or the
            # U-WP3 proxy 50/50 (csm: the read pages at the measured
            # evidence share instead of the proxy). Pool k draws from
            # what pools 1..k-1 left (the `taken` set), as always.
            #
            # The split is SOFT where the store runs dry (marvel's
            # `new-read` cell carries 49 windows, not 100: most of the
            # marvel teacher rows read FACT passages, whose pages sit
            # outside the lead/section universe): the era thirds (and
            # the pool total) are the hard requirement -- a short cell
            # CASCADES its deficit to the next cell of its group (the
            # same era's never-read side; the other proxy half), and a
            # deficit the chain cannot absorb fails the emit. The
            # receipt reports the nominal quotas and the actual.
            cells_spec = uwp4_cells(uwp4_mode, n)
            got_cells = {}
            carry = 0
            for c, quota, k in cells_spec:
                need = quota + carry
                cands = [w for w in sample_universe
                         if cell_of(w) == c and w.id not in taken]
                if k in ("read", "evidence"):
                    # The cell's non-empty share, measured on THIS
                    # final train universe (post test-page exclusion
                    # when a test pool ran) -- the WP6b rule.
                    ne_c = [w for w in cands if w.id in verbs]
                    em_c = [w for w in cands if w.id not in verbs]
                    share = (len(ne_c) / len(cands)) if cands else 0.0
                    n_ne = min(round(need * share), len(ne_c))
                    got_ne = sample_pool(
                        random.Random(f"{seed}-{pool}-{c}-nonempty"),
                        ne_c, n_ne,
                        weights=lambda w: 3.0 if RARE & verbs.get(w.id, set()) else 1.0,
                    )
                    got_em = sample_pool(
                        random.Random(f"{seed}-{pool}-{c}-empty"),
                        em_c, min(need - len(got_ne), len(em_c)),
                    )
                    got = got_ne + got_em
                else:
                    got = sample_pool(
                        random.Random(f"{seed}-{pool}-{c}"),
                        cands, min(need, len(cands)))
                carry = need - len(got)  # the deficit cascades to the next cell
                got_cells[c] = got
            if carry > 0:
                sys.exit(f"assertion: pool {pool} short of its total "
                         f"({carry} window(s) the cascade cannot absorb; "
                         f"actual cell counts: "
                         f"{ {c: len(ws) for c, ws in got_cells.items()} })")
            picked = [w for c, _q, _k in cells_spec for w in got_cells[c]]
            uwp4_pool_strata[pool] = got_cells
        elif stratified:
            # WP6b: stratify_read from the READ pages (at the measured
            # read-page non-empty share, rare x3 on the non-empty side)
            # + stratify_unread uniform from the NEVER-READ pages.
            n_read = stratify_read or 0
            n_unread = stratify_unread or 0
            r_cand = [w for w in read_uni if w.id not in taken]
            r_ne = [w for w in r_cand if w.id in verbs]
            r_em = [w for w in r_cand if w.id not in verbs]
            n_r_ne = min(round(n_read * read_nonempty_share), len(r_ne))
            got_r_ne = sample_pool(
                random.Random(f"{seed}-{pool}-read-nonempty"),
                r_ne, n_r_ne,
                weights=lambda w: 3.0 if RARE & verbs.get(w.id, set()) else 1.0,
            )
            got_r_em = sample_pool(
                random.Random(f"{seed}-{pool}-read-empty"),
                r_em, min(n_read - len(got_r_ne), len(r_em)),
            )
            u_cand = [w for w in unread_uni if w.id not in taken]
            got_unread = sample_pool(
                random.Random(f"{seed}-{pool}-unread"),
                u_cand, min(n_unread, len(u_cand)),
            )
            picked = (got_r_ne + got_r_em + got_unread)
            pool_strata[pool] = {
                "read_windows": got_r_ne + got_r_em,
                "read_nonempty": got_r_ne,
                "never_read_windows": got_unread,
            }
        else:
            # Pool k draws from what pools 1..k-1 left: the old pools
            # were disjoint (0 shared ids), and 15k windows need no
            # recycling.
            cand_nonempty = [w for w in nonempty if w.id not in taken]
            cand_empty = [w for w in empty if w.id not in taken]
            got_nonempty = sample_pool(
                pool_rng, cand_nonempty, min(n_nonempty, len(cand_nonempty)),
                weights=lambda w: 3.0 if RARE & verbs.get(w.id, set()) else 1.0,
            )
            got_empty = sample_pool(
                pool_rng, cand_empty, min(n_empty, len(cand_empty)),
            )
            picked = (got_nonempty + got_empty)
        pool_rng.shuffle(picked)  # presentation order: no empty block at the tail
        taken.update(w.id for w in picked)
        picks[pool] = picked

        # Display-only ordinals (the id is the identity, the n is a
        # per-file sort key -- review 4).
        lines = [pool_line(i, w, line_extra(w))
                 for i, w in enumerate(picked)]
        if not dry_run:
            pools_dir.mkdir(parents=True, exist_ok=True)
            out = pools_dir / f"{pool}_windows.jsonl"
            arch = out.with_name(out.name + archive_suffix)
            if do_archive and out.exists() and not arch.exists():
                out.rename(arch)
                archived.append(out.name + " -> " + arch.name)
            out.write_text(
                "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lines),
                encoding="utf-8",
            )
        if uwp4_mode:
            # U-WP4 receipt: the per-cell counts (the non-empty share +
            # rare for the read/evidence cells), the era or eventish
            # mix, the distinct pages.
            strata_rec = {}
            for c, q_nom, k in uwp4_cells(uwp4_mode, n):
                ws = uwp4_pool_strata[pool][c]
                strata_rec[c] = {
                    "windows": len(ws),
                    "nominal": q_nom,
                    "nonempty": sum(1 for w in ws if w.id in verbs),
                    "empty": sum(1 for w in ws if w.id not in verbs),
                    "rare": (sum(1 for w in ws
                                 if w.id in verbs and RARE & verbs[w.id])
                             if k in ("read", "evidence") else None),
                }
            rec = {
                "windows": len(picked),
                "strata": strata_rec,
                "distinct_pages": len({w.page for w in picked}),
                "file": str(pools_dir / f"{pool}_windows.jsonl"),
                "note": ("U-WP4: the top-level split (the era thirds / the "
                         "pool total) is hard; a short cell cascades its "
                         "deficit to the next cell (the split is soft "
                         "where the store runs dry) -- see the nominal vs "
                         "actual per-cell counts"),
            }
            if uwp4_mode == "era":
                rec["era_mix"] = dict(Counter(
                    window_era(w, era_map) for w in picked))
            else:
                rec["eventish_split"] = {
                    "eventish": sum(1 for w in picked if is_eventish(w.text)),
                    "non_eventish": sum(1 for w in picked
                                        if not is_eventish(w.text)),
                }
            receipt["pools"][pool] = rec
        elif stratified:
            st = pool_strata[pool]
            receipt["pools"][pool] = {
                "windows": len(picked),
                "strata": {
                    "read": {"windows": len(st["read_windows"]),
                             "nonempty": len(st["read_nonempty"]),
                             "empty": (len(st["read_windows"])
                                        - len(st["read_nonempty"]))},
                    "never_read": {"windows": len(st["never_read_windows"])},
                },
                "rare_windows": sum(
                    1 for w in st["read_nonempty"]
                    if RARE & verbs.get(w.id, set())
                ),
                "file": str(pools_dir / f"{pool}_windows.jsonl"),
            }
        else:
            receipt["pools"][pool] = {
                "windows": len(picked),
                "nonempty": len(got_nonempty),
                "empty": len(got_empty),
                "rare_windows": sum(
                    1 for w in got_nonempty if RARE & verbs.get(w.id, set())
                ),
                "file": str(pools_dir / f"{pool}_windows.jsonl"),
            }

    assert_pool_invariants(picks, holdout, gold_ids_all)

    # WP6: the test pool file (same line shape). It is EXEMPT from the
    # holdout/gold checks -- its pages ARE the recorded holdout -- but is
    # asserted id-unique and disjoint from every train pool.
    receipt["test_pool"] = {}
    if test_pool:
        t_ids = [w.id for w in test_picks]
        if len(t_ids) != len(set(t_ids)):
            sys.exit(f"assertion: test pool {test_pool} has duplicate "
                     f"window ids")
        for name, ws in picks.items():
            shared = set(t_ids) & {w.id for w in ws}
            if shared:
                sys.exit(f"assertion: test pool {test_pool} shares "
                         f"{len(shared)} window id(s) with train pool "
                         f"{name} (e.g. {sorted(shared)[:3]})")
        t_lines = [pool_line(i, w, line_extra(w))
             for i, w in enumerate(test_picks)]
        if not dry_run:
            pools_dir.mkdir(parents=True, exist_ok=True)
            out = pools_dir / f"{test_pool}_windows.jsonl"
            arch = out.with_name(out.name + archive_suffix)
            if do_archive and out.exists() and not arch.exists():
                out.rename(arch)
                archived.append(out.name + " -> " + arch.name)
            out.write_text(
                "".join(json.dumps(l, ensure_ascii=False) + "\n"
                        for l in t_lines),
                encoding="utf-8")
        if uwp4_mode:
            # U-WP4 receipt: the per-cell counts (the non-empty side +
            # rare for the read/evidence cells) + the era / eventish
            # mix + the page spread (the per-page cap is global across
            # cells).
            t_cell_ws = {c: [w for w in test_picks if cell_of(w) == c]
                         for c, _q, _k in uwp4_cells(uwp4_mode, test_n)}
            t_strata = {}
            for c, q_nom, k in uwp4_cells(uwp4_mode, test_n):
                ws = t_cell_ws[c]
                t_strata[c] = {
                    "windows": len(ws),
                    "nominal": q_nom,
                    "nonempty": sum(1 for w in ws if w.id in verbs),
                    "empty": sum(1 for w in ws if w.id not in verbs),
                    "rare": (sum(1 for w in ws
                                 if w.id in verbs and RARE & verbs[w.id])
                             if k in ("read", "evidence") else None),
                }
            t_rec = {
                "pool": test_pool, "windows": len(test_picks),
                "strata": t_strata,
                "distinct_pages": len(test_pages),
                "per_page_max": test_per_page_max,
                "holdout_json": str(holdout_json) if holdout_json else None,
                "file": str(pools_dir / f"{test_pool}_windows.jsonl"),
                "note": ("U-WP4: the pages are recorded in the series' "
                         "holdout BEFORE the train pools (merged with the "
                         "earlier pools' entries); the per-page cap is "
                         "global across cells; a short cell cascades its "
                         "deficit to the next cell (the split is soft, "
                         "the pool total is hard) -- see the nominal vs "
                         "actual per-cell counts"),
            }
            if uwp4_mode == "era":
                t_rec["era_mix"] = dict(Counter(
                    window_era(w, era_map) for w in test_picks))
            else:
                t_rec["eventish_split"] = {
                    "eventish": sum(1 for w in test_picks
                                    if is_eventish(w.text)),
                    "non_eventish": sum(1 for w in test_picks
                                        if not is_eventish(w.text)),
                }
            receipt["test_pool"] = t_rec
        else:
            receipt["test_pool"] = {
                "pool": test_pool, "windows": len(test_picks),
                "read": len(test_read_picks),
                "never_read": len(test_unread_picks),
                "nonempty": sum(1 for w in test_picks if w.id in verbs),
                "empty": sum(1 for w in test_picks if w.id not in verbs),
                "rare_windows": sum(
                    1 for w in test_picks
                    if w.id in verbs and RARE & verbs[w.id]
                ),
                "distinct_pages": len(test_pages),
                "per_page_max": test_per_page_max,
                "read_nonempty_share_remeasured": round(test_read_share, 4),
                "holdout_json": str(holdout_json) if holdout_json else None,
                "file": str(pools_dir / f"{test_pool}_windows.jsonl"),
            }
        # WP6b: the page-type mix (documents.page_type) of the strata --
    # reported, never assumed. U-WP4 pools report the whole-pool mix
    # (the cells are the strata; the mix is over the pool's windows).
    if ptypes and (pool_strata or uwp4_pool_strata or test_pool):
        def type_mix(ws):
            return dict(Counter(ptypes.get(w.page, "<none>") for w in ws))
        mix = {}
        for p in pools:
            if p in pool_strata:
                st = pool_strata[p]
                mix[p] = {"read": type_mix(st["read_windows"]),
                          "never_read": type_mix(st["never_read_windows"])}
            elif p in uwp4_pool_strata:
                mix[p] = type_mix(picks[p])
        if test_pool:
            if uwp4_mode:
                mix[f"test_pool ({test_pool})"] = type_mix(test_picks)
            else:
                mix[f"test_pool ({test_pool})"] = {
                    "read": type_mix(test_read_picks),
                    "never_read": type_mix(test_unread_picks),
                }
        receipt["page_type_mix"] = mix

    if era_receipt:
        receipt["era"] = era_receipt

    if do_archive and not dry_run and archive_suffix == ".old-grid":
        # The done-logs and pilot window files of the retired grid, the way
        # the council ruled: archived, not deleted. Gated to the .old-grid
        # suffix (2026-10-04): a *.pre-<WP> re-emit must not rename the
        # new campaign's done-logs, which are gen-grid artifacts.
        relic_archived = 0
        for old in sorted(pools_dir.glob(".*_done")):
            old.rename(old.with_name(old.name + ".old-grid"))
            archived.append(old.name + " -> " + old.name + ".old-grid")
            relic_archived += 1
        for old in sorted(pools_dir.glob("*P[0-9]_windows.jsonl")):
            old.rename(old.with_name(old.name + ".old-grid"))
            archived.append(old.name + " -> " + old.name + ".old-grid")
            relic_archived += 1
        if relic_archived:
            marker = pools_dir / "SUPERSEDED.md"
            if not marker.exists():
                marker.write_text(
                    f"# SUPERSEDED (windowing-100, 2026-09-30)\n\n"
                    "The 4,000/300 character-sliced pools under this directory are "
                    "retired: ~7% of their passages began mid-sentence, so a quote "
                    "read across a cut could not be anchored to any whole sentence.\n"
                    "The *.old-grid files are frozen evidence, not inputs. The "
                    f"campaign restarts at n=0 on the gen-{CURRENT_GEN} grid, emitted by "
                    "`tools/train/emit_windows.py` (receipt: SUPERSEDED_receipt.json).\n",
                    encoding="utf-8",
                )
                archived.append("wrote SUPERSEDED.md")

    receipt["seconds"] = round(time.time() - t0, 1)
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--pools", default="mimo,nemotron,spacebunny")
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--seed", type=int, default=20260930)
    ap.add_argument("--dry-run", action="store_true",
                    help="build + sample, write nothing (no archive either)")
    ap.add_argument("--no-archive", action="store_true",
                    help="emit the pools but leave the old pool files untouched")
    ap.add_argument("--out-dir", default=None,
                    help="write the pool files here instead of "
                         "series/<s>/training/opencode (determinism runs)")
    ap.add_argument("--no-holdout", action="store_true",
                    help="disable the held-out page exclusion (v1 dev/test + "
                         "blind gold pages; on by default: split by page, "
                         "never by row)")
    ap.add_argument("--gold", default=None,
                    help="gold file whose windows are excluded from the "
                         "pools (default series/<s>/training/gold600/"
                         "gold600.gen2.jsonl; ids recomputed, not read)")
    ap.add_argument("--gold2", default=None,
                    help="second gold file, excluded by rekey status "
                         "kept/reexpressed only (WP3b-2; default "
                         "series/<s>/training/gold/gold_pilot_all.gen2."
                         "jsonl; reread/straddle windows stay eligible)")
    ap.add_argument("--archive-suffix", default=".old-grid",
                    help="suffix for superseded pool files (WP2: .pre-wp2, "
                         "WP3b: .pre-wp3b)")
    ap.add_argument("--test-pool", default=None,
                    help="a page-disjoint test pool (WP6b): its pages are "
                         "chosen seeded BEFORE the train pools, recorded "
                         "to --holdout-json, and excluded from the train "
                         "sampling universe")
    ap.add_argument("--test-read-n", type=int, default=70,
                    help="WP6b: test-pool windows from READ pages "
                         "(stratified at the measured read-page share)")
    ap.add_argument("--test-unread-n", type=int, default=30,
                    help="WP6b: test-pool windows from NEVER-READ pages "
                         "(uniform)")
    ap.add_argument("--test-per-page-max", type=int, default=2,
                    help="WP6b: at most this many test-pool windows per "
                         "page (one-per-page pass runs first)")
    ap.add_argument("--stratify-read", type=int, default=None,
                    help="WP6b: train-pool windows drawn from READ pages "
                         "(>= 1 event row), stratified at the measured "
                         "read-page non-empty share, rare x3")
    ap.add_argument("--stratify-unread", type=int, default=None,
                    help="WP6b: train-pool windows drawn uniformly from "
                         "NEVER-READ pages (the student sees page types "
                         "the teacher never read)")
    ap.add_argument("--holdout-json", default=None,
                    help="where the test pool's pages are recorded "
                         "(default series/<s>/training/holdout_pages.json "
                         "when --test-pool is given)")
    ap.add_argument("--era-thirds", action="store_true",
                    help="U-WP4: the U-WP2 era stamp's era thirds "
                         "(old/mid/new) x read/never-read 50/50 inside "
                         "each third (the Marvel franchise; the read "
                         "side stratifies at the measured cell share, "
                         "rare x3; --era.json must exist)")
    ap.add_argument("--undated-policy", choices=("exclude", "old"),
                    default="exclude",
                    help="U-WP4: pages the era stamp left undated -- "
                         "exclude (marvel: counted, never sampled) or "
                         "fold into the old third (mcu: the plan's "
                         "'mcu old = 2008-2009 + undated-by-rule')")
    ap.add_argument("--eventish", action="store_true",
                    help="U-WP4: the 50/50 eventish/non-eventish split "
                         "on the U-WP3 zero-LLM proxy (the teacher-less "
                         "wikis; the lines carry the `eventish` flag)")
    ap.add_argument("--read-evidence", action="store_true",
                    help="U-WP4 (csm): the READ pages (>= 1 event row) "
                         "take 50/50 of the pool, stratified at the "
                         "measured evidence share (rare x3); the "
                         "never-read pages keep the eventish 50/50")
    ap.add_argument("--test-n", type=int, default=None,
                    help="U-WP4: the test pool's total window count "
                         "(its strata scale from it: era thirds x 50/50, "
                         "eventish 50/50)")
    a = ap.parse_args()
    # U-WP4: the modes are mutually exclusive (the Marvel franchise era
    # thirds vs the proxy 50/50 vs csm's read-evidence).
    n_modes = sum((a.era_thirds, a.read_evidence,
                   a.eventish and not a.read_evidence))
    if n_modes > 1:
        sys.exit("--era-thirds / --read-evidence / --eventish are "
                 "mutually exclusive (one strata mode per run)")
    # --pools none (the hxh holdout wiki): a test-pool-only emit.
    pool_names = [p for p in a.pools.split(",") if p and p != "none"]
    gold = a.gold or str(
        ROOT / "series" / a.series / "training" / "gold600" / "gold600.gen2.jsonl"
    )
    pilot = a.gold2 or str(
        ROOT / "series" / a.series / "training" / "gold" / "gold_pilot_all.gen2.jsonl"
    )
    holdout_json = a.holdout_json
    if a.test_pool and not holdout_json:
        holdout_json = str(
            ROOT / "series" / a.series / "training" / "holdout_pages.json")
    uwp4_run = a.era_thirds or a.eventish or a.read_evidence
    if uwp4_run and a.test_pool and a.test_n is None:
        sys.exit(f"assertion: a U-WP4 test pool ({a.test_pool}) needs "
                 "--test-n (its window count)")
    receipt = emit(
        a.series, pool_names, a.n, a.seed,
        dry_run=a.dry_run, do_archive=not a.no_archive, out_dir=a.out_dir,
        do_holdout=not a.no_holdout, gold_path=gold, pilot_path=pilot,
        test_pool=a.test_pool, test_read_n=a.test_read_n,
        test_unread_n=a.test_unread_n, test_per_page_max=a.test_per_page_max,
        holdout_json=holdout_json,
        stratify_read=a.stratify_read, stratify_unread=a.stratify_unread,
        archive_suffix=a.archive_suffix,
        era_thirds=a.era_thirds, undated_policy=a.undated_policy,
        eventish_split=a.eventish, read_evidence=a.read_evidence,
        test_n=a.test_n,
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
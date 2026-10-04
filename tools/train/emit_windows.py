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

    python tools/train/emit_windows.py --series jjk [--pools mimo,nemotron,spacebunny]
                                        [--n 500] [--seed 20260930] [--dry-run] [--no-archive]
                                        [--out-dir DIR] [--no-holdout] [--gold FILE]
                                        [--gold2 FILE] [--archive-suffix .pre-wp3b]
                                        [--test-pool NAME] [--test-read-n 70]
                                        [--test-unread-n 30] [--test-per-page-max 2]
                                        [--stratify-read 350] [--stratify-unread 150]
                                        [--holdout-json FILE]
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

# Same rare-verb set build_trainset.py repeats with `--rare-x 3`: a window
# that states one of these is under-represented in natural prose, so the
# campaign over-samples it to keep the student seeing them.
RARE = {"killed", "saved", "captured", "escaped", "betrayed",
        "sealed", "awakened", "departed", "arrived"}


def universe(store):
    """Every (page, label, text) the extractor actually reads: the document's
    lead, then its sections in page order -- each floored the way the
    extractor floors it, so a passage it would never read never lands in a
    pool (the counted `below_floor` class stays accounted for, never read)."""
    from scriptengine.ingest.events import panel_sentences
    from scriptengine.ingest.wikitext import strip_markup

    # Two queries, no join: joining documents x sections fans each
    # document's lead out once per section row (a page with 7 sections
    # would list its lead 8 times, and its lead windows 8x in the
    # sample). The extractor reads per document -- lead, then sections
    # in ordinal order -- which is the order rebuilt here per page.
    lead_text = {}
    for row in store.connection.execute(
        "SELECT title AS page, lead FROM documents"
        " WHERE COALESCE(lead, '') <> ''"
    ):
        lead = strip_markup(row["lead"]).strip()
        if lead and panel_sentences(lead):
            lead_text[row["page"]] = lead
    sections = {}
    for row in store.connection.execute(
        "SELECT d.title AS page, s.title AS title, s.text AS text"
        " FROM sections s JOIN documents d ON d.id = s.document_id"
        " WHERE COALESCE(s.text, '') <> ''"
        " ORDER BY d.title, s.ordinal"
    ):
        text = (row["text"] or "").strip()
        if text and panel_sentences(text):
            sections.setdefault(row["page"], []).append(
                ((row["title"] or "").strip(), text)
            )
    out = []
    for page in sorted(set(lead_text) | set(sections)):
        if page in lead_text:
            out.append((page, "lead", lead_text[page]))
        for label, text in sections.get(page, []):
            out.append((page, label, text))
    return out


def row_passage_text(store, row):
    """The text a stored event row was read from -- the same resolution
    `events._row_passage_text` uses (section, lead, or a declared fact
    value holding the quote)."""
    from scriptengine.ingest.wikitext import strip_markup

    passage = row["passage"] or ""
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


def map_evidence(store, by_key):
    """Which windows the store's own rows state something in.

    Returns (verbs_per_window, unmapped_rows): a window is non-empty when
    at least one stored quote maps into it via the grid (a quote the grid
    does not carry in one window is counted unmapped -- the window-level
    G1's loud failure, not a silent attribute)."""
    verbs = {}
    unmapped = 0
    for row in store.connection.execute("SELECT * FROM events"):
        text = row_passage_text(store, row)
        quote = row["quote"] or ""
        passage = row["passage"] or ""
        if row["section_id"] is not None and not passage:
            label = store.connection.execute(
                "SELECT title FROM sections WHERE id = ?", (row["section_id"],)
            ).fetchone()
            label = (label["title"] or "").strip() if label else ""
        elif passage == "lead":
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
    share 0.976 -- the strata stratify on the read pages only."""
    return {row["doc_title"] for row in
            store.connection.execute("SELECT DISTINCT doc_title FROM events")}


def page_types(store):
    """WP6b: the documents table's page_type per title ('' -> <none>) --
    the strata's page-type mix is reported, never assumed."""
    out = {}
    for row in store.connection.execute("SELECT title, page_type FROM documents"):
        out[row["title"]] = (row["page_type"] or "").strip() or "<none>"
    return out


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
         archive_suffix=".old-grid"):
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
        read_pages, ptypes = set(), {}
        if (test_pool or stratify_read is not None
                or stratify_unread is not None):
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
    if test_pool:
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
            hj = Path(holdout_json)
            hj.parent.mkdir(parents=True, exist_ok=True)
            hj.write_text(
                json.dumps({
                    "series": series, "pool": test_pool, "seed": seed,
                    "count": len(test_pages), "pages": sorted(test_pages),
                    "read_n": test_read_n, "unread_n": test_unread_n,
                    "note": ("WP6b (2026-10-04, tools/train/emit_windows"
                             ".py): the test pool's pages -- the series' "
                             "holdout. The train pools never sample these "
                             "pages (page-disjoint by construction); a "
                             "re-run reuses the recorded pages."),
                }, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8")
            archived.append(f"holdout pages -> {hj.name}")
        # The test pages are out of the TRAIN sampling universe.
        sample_universe = [w for w in sample_universe if w.page not in test_pages]

    nonempty = [w for w in sample_universe if w.id in verbs]
    empty = [w for w in sample_universe if w.id not in verbs]
    empty_share = len(empty) / len(sample_universe) if sample_universe else 0.0
    n_empty = round(n * empty_share)
    n_nonempty = n - n_empty

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

    taken = set()
    picks = {}
    pool_strata = {}
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
        if stratified:
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
        lines = [
            {
                "n": i,
                "id": w.id,
                "page": w.page,
                "section": "" if w.section == "lead" else w.section,
                "passage": w.text,
                "gen": w.gen,
                "sub": w.sub,
            }
            for i, w in enumerate(picked)
        ]
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
        if stratified:
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
        t_lines = [
            {"n": i, "id": w.id, "page": w.page,
             "section": "" if w.section == "lead" else w.section,
             "passage": w.text, "gen": w.gen, "sub": w.sub}
            for i, w in enumerate(test_picks)
        ]
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
    # reported, never assumed.
    if ptypes and (pool_strata or test_pool):
        def type_mix(ws):
            return dict(Counter(ptypes.get(w.page, "<none>") for w in ws))
        mix = {}
        for p in pools:
            if p in pool_strata:
                st = pool_strata[p]
                mix[p] = {"read": type_mix(st["read_windows"]),
                          "never_read": type_mix(st["never_read_windows"])}
        if test_pool:
            mix[f"test_pool ({test_pool})"] = {
                "read": type_mix(test_read_picks),
                "never_read": type_mix(test_unread_picks),
            }
        receipt["page_type_mix"] = mix

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
    a = ap.parse_args()
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
    receipt = emit(
        a.series, a.pools.split(","), a.n, a.seed,
        dry_run=a.dry_run, do_archive=not a.no_archive, out_dir=a.out_dir,
        do_holdout=not a.no_holdout, gold_path=gold, pilot_path=pilot,
        test_pool=a.test_pool, test_read_n=a.test_read_n,
        test_unread_n=a.test_unread_n, test_per_page_max=a.test_per_page_max,
        holdout_json=holdout_json,
        stratify_read=a.stratify_read, stratify_unread=a.stratify_unread,
        archive_suffix=a.archive_suffix,
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
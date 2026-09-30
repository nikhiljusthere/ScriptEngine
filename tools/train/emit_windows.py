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

    python tools/train/emit_windows.py --series jjk [--pools mimo,nemotron,spacebunny]
                                       [--n 500] [--seed 20260930] [--dry-run] [--no-archive]

A pool line is the old campaign shape plus the builder's identity fields, so
`opencode_check.py` and `windows_to_messages.py` keep working:

    {"n", "id", "page", "section", "passage", "gen", "sub"}
"""
import argparse
import json
import math
import random
import sys
import time
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


def build_universe_windows(store):
    """The grid's windows, keyed the way the store's rows address them.

    A window id hashes (gen, page, section-label, sub, span) -- so two
    same-titled sections of one page (the wiki has 7 of them) collide
    id-for-id. The first-read copy is kept and the collisions are
    counted, not silently dropped; the section-keyed map keeps the
    union so a stored row quoting either copy still maps."""
    windows = []
    seen_ids = set()
    duplicate_ids = 0
    by_key = {}
    for page, label, text in universe(store):
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


def emit(series, pools, n, seed, dry_run, do_archive, out_dir=None):
    paths_root = ROOT / "series" / series
    db = paths_root / "facts.db"
    if not db.exists():
        sys.exit(f"{series} is not indexed (no {db}); run `index` first")
    t0 = time.time()
    with FactStore(db) as store:
        windows, by_key, duplicate_ids = build_universe_windows(store)
        verbs, unmapped_rows = map_evidence(store, by_key)

    nonempty = [w for w in windows if w.id in verbs]
    empty = [w for w in windows if w.id not in verbs]
    empty_share = len(empty) / len(windows) if windows else 0.0
    n_empty = round(n * empty_share)
    n_nonempty = n - n_empty

    pool_dir = out_dir or (paths_root / "training" / "opencode")
    pools_dir = pool_dir
    archived = []
    receipt = {
        "series": series,
        "gen": CURRENT_GEN,
        "universe_windows": len(windows),
        "duplicate_window_ids": duplicate_ids,
        "nonempty_windows": len(nonempty),
        "empty_windows": len(empty),
        "empty_share_remeasured": round(empty_share, 4),
        "evidence_rows_unmapped": unmapped_rows,
        "pools": {},
        "archived": archived,
        "dry_run": dry_run,
    }

    taken = set()
    for pool in pools:
        pool_rng = random.Random(f"{seed}-{pool}")
        # Pool k draws from what pools 1..k-1 left: the old pools were
        # disjoint (0 shared ids), and 15k windows need no recycling.
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
            if do_archive and out.exists() and not out.with_name(out.name + ".old-grid").exists():
                out.rename(out.with_name(out.name + ".old-grid"))
                archived.append(out.name + " -> " + out.name + ".old-grid")
            out.write_text(
                "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lines),
                encoding="utf-8",
            )
        receipt["pools"][pool] = {
            "windows": len(picked),
            "nonempty": len(got_nonempty),
            "empty": len(got_empty),
            "rare_windows": sum(
                1 for w in got_nonempty if RARE & verbs.get(w.id, set())
            ),
            "file": str(pools_dir / f"{pool}_windows.jsonl"),
        }

    if do_archive and not dry_run:
        # The done-logs and pilot window files of the retired grid, the way
        # the council ruled: archived, not deleted.
        for old in sorted(pools_dir.glob(".*_done")):
            old.rename(old.with_name(old.name + ".old-grid"))
            archived.append(old.name + " -> " + old.name + ".old-grid")
        for old in sorted(pools_dir.glob("*P[0-9]_windows.jsonl")):
            old.rename(old.with_name(old.name + ".old-grid"))
            archived.append(old.name + " -> " + old.name + ".old-grid")
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
    a = ap.parse_args()
    receipt = emit(
        a.series, a.pools.split(","), a.n, a.seed,
        dry_run=a.dry_run, do_archive=not a.no_archive,
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
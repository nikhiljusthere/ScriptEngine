#!/usr/bin/env python3
"""Fixed-list fetcher for the MARVEL 100% campaign egress batch (untracked
campaign tooling, public API only).

Re-crawls an explicit title list with the engine's `fetch_batch` +
`build_page` machinery (so pages stamp `revid` natively via the F1
`rvprop=ids|content` fix, 664796b2) and saves them under controlled
filenames:

  * default: `sanitise_filename(title).json` (the engine's own name);
  * with `--disambiguate`: every title whose sanitised name collides with
    another title in the list gets a `(pageid)` suffix — the F3 collision
    groups (4 titles -> 2 files) become 4 owner files.

Two modes:
  * `--disambiguate` (F3): sequential single-title fetches, one write +
    rename per title, so a collision can never last-write-win;
  * batch (F5): one 50-title `fetch_batch` request, sequential per-page
    saves (build_page mutates the shared ontology, so order is pinned).

The ontology comes from the series manifest (the vocabulary the corpus was
crawled with); unknown infobox templates degrade exactly as a capped crawl
does (`type_for_templates` infobox-word fallback). `manifest.json` is NOT
touched — the reconciliation run owns the canonical manifest.

Usage (from the repo root, one egress window):
  PYTHONPATH=$PWD scriptengine/.venv/bin/python tools/marvel/fixlist_fetch.py \
      --series marvel --titles-file tools/marvel/f3_recrawl_2026-09-26.jsonl \
      --disambiguate --shard-id f3_recrawl_2026-09-26 \
      --egress-note "GB 194.88.x (nordvpn, exhausted pool)"
  PYTHONPATH=$PWD scriptengine/.venv/bin/python tools/marvel/fixlist_fetch.py \
      --series mcu --titles-file tools/marvel/mcu_topup_f5_2026-09-26.jsonl \
      --shard-id mcu_topup_f5_2026-09-26 \
      --egress-note "GB 194.88.x (nordvpn, exhausted pool)"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scriptengine.config import get_settings, load_overrides, series_paths  # noqa: E402
from scriptengine.ingest.crawler import (  # noqa: E402
    WikiCrawler,
    api_base,
    load_manifest,
    sanitise_filename,
)
from scriptengine.ingest.ontology import Ontology  # noqa: E402

WIKIS = {
    "marvel": "https://marvel.fandom.com",
    "mcu": "https://marvelcinematicuniverse.fandom.com",
}


def atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


async def fetch_one(
    crawler: WikiCrawler,
    base: str,
    wiki_url: str,
    ontology: Ontology,
    title: str,
) -> dict[str, Any] | None:
    """Fetch + build one title. Returns the parse dict, or None (missing)."""
    fetched = await crawler.fetch_batch(base, [title])
    if not fetched:
        return None
    parse = fetched[0]
    page = crawler.build_page(parse, wiki_url, ontology)
    await crawler._learn_labels(base, page.title, page.page_type, ontology)
    reason = ontology.is_skippable(page.categories)
    if reason:
        return {"title": parse.get("title", ""), "pageid": parse.get("pageid", 0),
                "status": f"skipped: {reason}"}
    if not page.word_count and not page.facts:
        return {"title": parse.get("title", ""), "pageid": parse.get("pageid", 0),
                "status": "skipped: no content"}
    parse["_page"] = page
    return parse


async def run(a: argparse.Namespace) -> int:
    settings = get_settings()
    paths = series_paths(a.series, settings)
    overrides = load_overrides(paths)  # noqa: F841 (kept for parity with the crawl)
    manifest = load_manifest(paths)
    ontology = Ontology.from_dict(manifest.get("ontology") or {})
    if not ontology.types:
        raise SystemExit(f"no ontology in the {a.series} manifest; refusing to guess")

    titles = [
        line.strip()
        for line in Path(a.titles_file).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not titles:
        raise SystemExit(f"titles file {a.titles_file} is empty")

    base = api_base(WIKIS[a.series])
    wiki_url = WIKIS[a.series]
    # Titles whose sanitised name collides with a sibling in this list are
    # the ones that need the (pageid) suffix.
    names = [sanitise_filename(t) for t in titles]
    colliding = {name for name in names if names.count(name) > 1}

    rows: list[dict[str, Any]] = []
    async with WikiCrawler(settings) as crawler:
        if a.disambiguate:
            # Sequential: fetch one title, write it to its final (disambiguated)
            # name before the next fetch, so a collision can never overwrite.
            for title in titles:
                print(f"[fixlist] fetching {title!r}", flush=True)
                parse = await fetch_one(crawler, base, wiki_url, ontology, title)
                if parse is None:
                    rows.append({"title": title, "status": "missing-or-failed"})
                    continue
                if "status" in parse and parse.get("status", "").startswith("skipped"):
                    rows.append({"title": title, "status": parse["status"]})
                    continue
                page = parse.pop("_page")
                stem = sanitise_filename(page.title)
                dest = (
                    f"{stem} ({page.pageid}).json"
                    if stem in colliding
                    else f"{stem}.json"
                )
                destination = paths.wikitext / dest
                if a.dry_run:
                    rows.append({"title": page.title, "pageid": page.pageid,
                                 "revid": page.revid, "file": destination.name,
                                 "status": "dry-run"})
                    continue
                atomic_write(destination, page.to_json())
                rows.append({"title": page.title, "pageid": page.pageid,
                             "revid": page.revid, "file": destination.name,
                             "type": page.page_type, "facts": len(page.facts),
                             "status": "written"})
                print(f"[fixlist]   -> {destination.name} "
                      f"(revid={page.revid}, facts={len(page.facts)})", flush=True)
        else:
            # Batch mode: one request for the whole list (50-title cap),
            # sequential per-page saves.
            fetched = await crawler.fetch_batch(base, titles[:50])
            returned = {p.get("title", "") for p in fetched}
            for title in titles[:50]:
                if title not in returned:
                    rows.append({"title": title, "status": "missing-or-failed"})
            for parse in fetched:
                page = crawler.build_page(parse, wiki_url, ontology)
                await crawler._learn_labels(base, page.title, page.page_type, ontology)
                reason = ontology.is_skippable(page.categories)
                if reason:
                    rows.append({"title": page.title, "pageid": page.pageid,
                                 "status": f"skipped: {reason}"})
                    continue
                if not page.word_count and not page.facts:
                    rows.append({"title": page.title, "pageid": page.pageid,
                                 "status": "skipped: no content"})
                    continue
                destination = paths.wikitext / f"{sanitise_filename(page.title)}.json"
                if a.dry_run:
                    rows.append({"title": page.title, "pageid": page.pageid,
                                 "revid": page.revid, "file": destination.name,
                                 "status": "dry-run"})
                    continue
                atomic_write(destination, page.to_json())
                rows.append({"title": page.title, "pageid": page.pageid,
                             "revid": page.revid, "file": destination.name,
                             "type": page.page_type, "facts": len(page.facts),
                                 "status": "written"})

    receipt = {
        "shard_id": a.shard_id,
        "series": a.series,
        "wiki": WIKIS[a.series],
        "mode": "disambiguate" if a.disambiguate else "batch",
        "titles_in": len(titles),
        "rows": rows,
        "written": sum(1 for r in rows if r["status"] == "written"),
        "dry_run": a.dry_run,
        "egress_note": a.egress_note,
        "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "manifest_note": ("canonical manifest untouched; reconciliation run "
                          "rebuilds it"),
    }
    if not a.dry_run:
        out = REPO / "reports" / "marvel" / "receipts" / f"fixlist_{a.shard_id}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False),
                       encoding="utf-8")
        print(f"receipt -> {out}")
    print(json.dumps({k: v for k, v in receipt.items() if k != "rows"},
                     indent=2, ensure_ascii=False))
    # Any non-written, non-skipped row is a live failure that needs a record.
    bad = [r for r in rows if r["status"] not in ("written", "dry-run")
           and not r["status"].startswith("skipped")]
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", required=True, choices=sorted(WIKIS))
    ap.add_argument("--titles-file", required=True)
    ap.add_argument("--disambiguate", action="store_true",
                    help="sequential fetch + (pageid)-suffixed names for "
                         "colliding titles (F3)")
    ap.add_argument("--shard-id", required=True)
    ap.add_argument("--egress-note", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.disambiguate and len(
            [l for l in Path(a.titles_file).read_text(encoding="utf-8").splitlines()
             if l.strip()]) > 50:
        raise SystemExit("--disambiguate lists are sequential; keep them small")
    return asyncio.run(run(a))


if __name__ == "__main__":
    sys.exit(main())
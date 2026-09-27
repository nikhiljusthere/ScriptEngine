#!/usr/bin/env python3
"""Shard fetcher for the Marvel 100% campaign (untracked tooling, public API only).

Fetches one disjoint shard of page titles with its own manifest, reusing the
WikiCrawler crawl machinery (batched 50-page fetch, extraction, ontology,
watchdog, filename-based resume) unchanged. Two campaign modifications:

  * the page list comes from a shard file instead of a fresh enumeration —
    `ShardCrawler.list_all_pages` returns it, and `_crawl` treats it exactly
    like an enumeration result (including the on-disk resume skip);
  * the manifest lands in `manifest.shard_<id>.json` instead of the canonical
    `manifest.json`, so two egresses can never write the same manifest.

The shared `series/<series>/wikitext/` directory is safe for concurrent shard
processes: the shards are disjoint, and resume is filename-based. The final
canonical manifest is rebuilt later by a reconciliation run.

Usage (one process per egress, c3 per egress per campaign protocol):
    SCRIPTENGINE_CRAWL_CONCURRENCY=3 .venv/bin/python tools/marvel/shard_fetch.py \
        --series marvel --shard-file tools/marvel/shard_a.jsonl --shard-id a \
        --egress-note "CA 187.15.140.90 (nordvpn #1980)"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root

from scriptengine.config import SeriesPaths, get_settings, load_overrides, series_paths
from scriptengine.ingest.crawler import WikiCrawler, api_base  # noqa: F401  (api_base documents the base form)


class ShardCrawler(WikiCrawler):
    """A WikiCrawler whose enumeration returns a fixed shard title list."""

    def __init__(self, settings: Any, shard_titles: list[str]) -> None:
        super().__init__(settings)
        self._shard_titles = list(shard_titles)

    async def list_all_pages(self, base: str, limit: int = 0) -> list[str]:
        # `_crawl` feeds this through its resume-skip filter exactly as it
        # would a fresh enumeration, so on-disk pages are never re-fetched.
        titles = self._shard_titles
        return titles[:limit] if limit else list(titles)


class ShardPaths(SeriesPaths):
    """A SeriesPaths whose manifest is shard-specific.

    Every SeriesPaths field is a property of `root`, so only `manifest` is
    overridden; `wikitext/` stays shared so both shards resume from the same
    on-disk set.
    """

    def __init__(self, base: SeriesPaths, shard_id: str) -> None:
        # SeriesPaths is a frozen dataclass: its generated __init__ uses
        # object.__setattr__, and so must we for the extra attribute.
        SeriesPaths.__init__(self, base.name, base.root)
        object.__setattr__(self, "_shard_id", shard_id)

    @property
    def manifest(self) -> Path:
        return self.root / f"manifest.shard_{self._shard_id}.json"


async def run_shard(
    series: str,
    start_url: str,
    shard_file: Path,
    shard_id: str,
    egress_note: str,
) -> dict:
    settings = get_settings()
    paths = series_paths(series, settings)
    shard_paths = ShardPaths(paths, shard_id)

    titles = [line.strip() for line in shard_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not titles:
        raise SystemExit(f"shard file {shard_file} is empty; nothing to fetch")
    print(f"[shard {shard_id}] {len(titles)} titles from {shard_file.name}", flush=True)

    overrides = load_overrides(paths)
    crawler = ShardCrawler(settings, titles)
    async with crawler:
        manifest = await crawler.crawl(start_url, shard_paths, max_pages=0, overrides=overrides)

    receipt = {
        "shard_id": shard_id,
        "series": series,
        "shard_titles": len(titles),
        "pages_fetched_this_run": manifest.get("pages_fetched_this_run"),
        "pages_on_disk": manifest.get("pages_on_disk"),
        "pages_failed": manifest.get("pages_failed"),
        "manifest": str(shard_paths.manifest),
        "egress": egress_note,
    }
    print(json.dumps(receipt))
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series", default="marvel")
    parser.add_argument("--start-url", default="https://marvel.fandom.com/wiki/Marvel_Database")
    parser.add_argument("--shard-file", required=True)
    parser.add_argument("--shard-id", required=True, help="a, b, ... (becomes manifest.shard_<id>.json)")
    parser.add_argument("--egress-note", default="")
    args = parser.parse_args()

    asyncio.run(run_shard(args.series, args.start_url, Path(args.shard_file), args.shard_id, args.egress_note))


if __name__ == "__main__":
    main()
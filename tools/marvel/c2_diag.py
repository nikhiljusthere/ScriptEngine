#!/usr/bin/env python3
"""c2 silent-stall diagnostic for the Marvel campaign (untracked tooling).

Reproduces the c2 silent stall (four consecutive CrawlStalled runs with 0
completions, 0 rate-limit lines, 0 failures) and, on SIGUSR1, dumps every
live asyncio task's coroutine stack — the only way to see where a suspended
`await` is stuck, since py-spy only sees OS threads and the event loop shows
merely idle in `select`.

Run (c2, browser UA, 60-s timeout, same as the stalling runs):
    SCRIPTENGINE_CRAWL_CONCURRENCY=2 SCRIPTENGINE_CRAWL_TIMEOUT_SECONDS=60 \
    SCRIPTENGINE_USER_AGENT="Mozilla/5.0 ... Chrome/136.0.0.0 Safari/537.36" \
    .venv/bin/python tools/marvel/c2_diag.py --limit-titles 200
then, once it is in the fetch phase:
    kill -USR1 <pid>
The task dump is printed to stdout (captured in the run log).
"""

from __future__ import annotations

import argparse
import asyncio
import faulthandler
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/marvel

import shard_fetch  # noqa: E402  (reuses run_shard / ShardCrawler / ShardPaths)
from scriptengine.config import get_settings, load_overrides, series_paths  # noqa: E402
from scriptengine.ingest.crawler import WikiCrawler  # noqa: E402


def _dump_tasks(_signum: int, _frame: object) -> None:
    try:
        loop = asyncio.get_running_loop()
        tasks = asyncio.all_tasks(loop)
        print(f"\n=== SIGUSR1: {len(tasks)} live task(s) ===", flush=True)
        for task in tasks:
            print(f"--- {task!r}", flush=True)
            try:
                task.print_stack()
            except Exception as error:  # noqa: BLE001
                print(f"    (stack unavailable: {error!r})", flush=True)
        print("=== end task dump ===\n", flush=True)
    except Exception as error:  # noqa: BLE001
        print(f"=== SIGUSR1 dump failed: {error!r} ===", flush=True)


class LimitedShardCrawler(shard_fetch.ShardCrawler):
    """A ShardCrawler that only ever offers a fixed slice of the shard (fast repro)."""

    def __init__(self, settings, shard_slice: list[str]) -> None:
        super().__init__(settings, shard_slice)

    async def list_all_pages(self, base: str, limit: int = 0) -> list[str]:
        return list(self._shard_titles)


async def run(
    series: str,
    start_url: str,
    shard_file: Path,
    egress_note: str,
    limit_titles: int,
    offset_titles: int = 0,
) -> dict:
    settings = get_settings()
    paths = series_paths(series, settings)
    titles = [line.strip() for line in shard_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    chosen = titles[offset_titles:] if limit_titles <= 0 else titles[offset_titles:offset_titles + limit_titles]
    print(f"[c2 diag] {len(titles)} titles in {shard_file.name}; using "
          f"index {offset_titles}..{offset_titles + len(chosen)} ({len(chosen)} titles)", flush=True)

    overrides = load_overrides(paths)
    diag_paths = shard_fetch.ShardPaths(paths, "c2diag")
    crawler = LimitedShardCrawler(settings, chosen)
    async with crawler:
        # Same call as run_shard, but with the shard-manifest paths swapped out
        # (the canonical manifest.json is only ever written by full runs).
        manifest = await crawler.crawl(start_url, diag_paths, max_pages=0, overrides=overrides)
    print("done:", {k: manifest.get(k) for k in ("pages_fetched_this_run", "pages_failed", "pages_on_disk")}, flush=True)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series", default="marvel")
    parser.add_argument("--start-url", default="https://marvel.fandom.com/wiki/Marvel_Database")
    parser.add_argument("--shard-file", required=True)
    parser.add_argument("--limit-titles", type=int, default=200)
    parser.add_argument("--offset-titles", type=int, default=0,
                        help="start at this index into the shard file (use the tail for titles not yet on disk)")
    parser.add_argument("--egress-note", default="c2 SIGUSR1 diagnostic")
    args = parser.parse_args()

    faulthandler.enable()
    signal.signal(signal.SIGUSR1, _dump_tasks)
    print("[c2 diag] SIGUSR1 = dump all asyncio task stacks; faulthandler on", flush=True)
    asyncio.run(run(args.series, args.start_url, Path(args.shard_file), args.egress_note,
                    args.limit_titles, args.offset_titles))


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Split the outstanding Marvel titles into N disjoint shards (untracked tooling).

Reads the full enumerated title list, subtracts what is already on disk
(same filename rule as the crawler's resume logic), and partitions the
remainder into N shards by stable title hash (sha256 mod N), so a page always
lands in the same shard and shards never overlap.

Usage:
    .venv/bin/python tools/marvel/make_shards.py \
        --all-pages reports/marvel/receipts/marvel_all_pages.jsonl \
        --series marvel --shards 2 --out-dir tools/marvel
"""

from __future__ import annotations

import argparse
import hashlib
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root

from scriptengine.config import get_settings, series_paths
from scriptengine.ingest.crawler import sanitise_filename


def shard_index(title: str, n: int) -> int:
    return int(hashlib.sha256(title.encode("utf-8")).hexdigest(), 16) % n


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-pages", required=True)
    parser.add_argument("--series", default="marvel")
    parser.add_argument("--shards", type=int, default=2)
    parser.add_argument("--out-dir", default="tools/marvel")
    args = parser.parse_args()

    all_titles: list[str] = []
    seen: set[str] = set()
    for line in Path(args.all_pages).read_text(encoding="utf-8").splitlines():
        title = line.strip()
        if title and title not in seen:
            seen.add(title)
            all_titles.append(title)

    settings = get_settings()
    paths = series_paths(args.series, settings)
    on_disk: set[str] = set()
    if paths.wikitext.exists():
        on_disk = {path.stem for path in paths.wikitext.glob("*.json")}

    outstanding = [t for t in all_titles if sanitise_filename(t) not in on_disk]
    buckets: list[list[str]] = [[] for _ in range(args.shards)]
    for title in outstanding:
        buckets[shard_index(title, args.shards)].append(title)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"enumerated={len(all_titles)} on_disk={len(on_disk)} outstanding={len(outstanding)}")
    for i, bucket in enumerate(buckets):
        letter = string.ascii_lowercase[i]
        dest = out_dir / f"shard_{letter}.jsonl"
        dest.write_text("\n".join(bucket) + "\n", encoding="utf-8")
        print(f"shard {letter}: {len(bucket)} titles -> {dest}")


if __name__ == "__main__":
    main()
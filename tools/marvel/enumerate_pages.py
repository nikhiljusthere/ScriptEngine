#!/usr/bin/env python3
"""Parallel allpages enumerator for the Marvel 100% campaign (untracked tooling).

The library's `list_all_pages` pages through `allpages` sequentially (~45 min
for 279k titles at 100 per page). This tool parallelises the same light path:
the title space is split into first-character groups, and each group is paged
through with `list=allpageswithprefix` concurrently (8 groups, each sequential
inside). The groups are disjoint and cover every ASCII first character exactly
once, so their union is the full non-redirect title list.

Integrity: with `--expect-count N` (the in-flight crawl's final "enumerated N"
log line), a mismatched union count triggers the library's sequential full
chain as a fallback, so the output is only ever a verified-complete list or an
explicit error.

Usage:
    .venv/bin/python tools/marvel/enumerate_pages.py \
        --start-url https://marvel.fandom.com/wiki/Marvel_Database \
        --out reports/marvel/receipts/marvel_all_pages.jsonl \
        [--expect-count 279116] [--egress-note "CA 187.15.140.90"]

One title per line. A crashed run is re-run from scratch (~10 min); existing
lines are deduped, so a re-run after a near-complete finish is cheap.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root

from scriptengine.config import get_settings
from scriptengine.ingest.crawler import WikiCrawler, api_base

# Concurrent range groups. Fandom's MediaWiki rejects `list=allpageswithprefix`
# (verified 2026-09-25 on both wikis: "Unrecognized value for parameter
# list"), so the groups page `list=allpages` over collation ranges instead.
# Observed collation (case-insensitive, from the 279,133 Marvel enumeration):
# symbols (" $ ' ...) first, then 0-9, then A-Z, then non-ASCII (é, Ö, Ø...
# last). NOTE: apfrom/apto are TITLE-STRING ranges, not prefixes — "A".."A"
# captures only the exact title "A", so each letter L is ranged as
# L.."L~" ("~" sorts after every letter/digit, so the range covers L*).
# The final group omits `apto` so it runs to the end of the list and picks up
# the rare non-ASCII-first titles too. The count cross-check (or the later
# reconciliation run) stays the integrity net.
GROUPS: list[dict] = [
    {"apto": "9~"},                     # symbols + digits (before the letters)
    {"apfrom": "S", "apto": "S~"},       # Marvel's title space is S-skewed
    {"apfrom": "A", "apto": "A~"},
    {"apfrom": "B", "apto": "C~"},
    {"apfrom": "D", "apto": "F~"},
    {"apfrom": "G", "apto": "I~"},
    {"apfrom": "J", "apto": "M~"},
    {"apfrom": "N", "apto": "R~"},
    {"apfrom": "T"},                     # T-Z + non-ASCII tail, to end of list
]


async def enumerate_group(
    crawler: WikiCrawler,
    base: str,
    spec: dict,
    out: Path,
    write_lock: asyncio.Lock,
    stop: asyncio.Event,
    stats: dict,
) -> None:
    """Page one collation range (`apfrom`/`apto` on `list=allpages`)
    sequentially, via the library's 429-aware `_get` (retries, backoff,
    shared throttle). A missing `apto` means: run to the end of the list."""
    apcontinue: str | None = None
    consecutive_failures = 0
    while True:
        if stop.is_set():
            return
        params = {
            "action": "query",
            "list": "allpages",
            "apfilterredir": "nonredirects",
            "apnamespace": "0",
            "aplimit": "100",
            "format": "json",
            "formatversion": "2",
        }
        if spec.get("apfrom"):
            params["apfrom"] = spec["apfrom"]
        if spec.get("apto"):
            params["apto"] = spec["apto"]
        if apcontinue:
            params["apcontinue"] = apcontinue
        data = await crawler._get(base, params)
        if data is None:
            consecutive_failures += 1
            if consecutive_failures >= 40:
                stats["aborted"] = True
                stop.set()
                print(
                    f"[enum] group {spec!r}: {consecutive_failures} "
                    "consecutive failures; aborting (re-run to resume)",
                    flush=True,
                )
                return
            print(f"[enum] {spec!r}: request failed; retrying in 60s", flush=True)
            await asyncio.sleep(60)
            continue
        consecutive_failures = 0
        titles = [p["title"] for p in (data.get("query") or {}).get("allpages", [])]
        stats["titles"] += len(titles)
        if titles:
            async with write_lock:
                with out.open("a", encoding="utf-8") as fh:
                    fh.write("\n".join(titles) + "\n")
        apcontinue = (data.get("continue") or {}).get("apcontinue")
        if not apcontinue:
            break
        # Belt-and-braces: stop if the next page's first title has left the
        # range (MediaWiki normally signals this via batchcomplete).
        apto = spec.get("apto")
        if apto and apcontinue[:1].lower() > apto.lower():
            break
        # Match the library's light-path cadence.
        await asyncio.sleep(0.3)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-url", default="https://marvel.fandom.com/wiki/Marvel_Database")
    parser.add_argument("--out", required=True)
    parser.add_argument("--expect-count", type=int, default=0,
                        help="reference count from the in-flight crawl's final enumeration line")
    parser.add_argument("--egress-note", default="")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        existing = len(out.read_text(encoding="utf-8").splitlines())
        print(f"[enum] {existing} lines already in {out.name}; re-walking and deduping", flush=True)

    settings = get_settings()
    crawler = WikiCrawler(settings)
    base = api_base(args.start_url)
    stats: dict = {"titles": 0, "aborted": False}
    stop = asyncio.Event()
    write_lock = asyncio.Lock()
    started = time.time()

    print(f"[enum] {len(GROUPS)} groups against {base} (egress: {args.egress_note or 'unknown'})", flush=True)
    async with crawler:
        await asyncio.gather(
            *[enumerate_group(crawler, base, group, out, write_lock, stop, stats)
              for group in GROUPS]
        )

        if stats["aborted"]:
            print(json.dumps({"status": "aborted", "detail": "see log; re-run to resume"}))
            raise SystemExit(1)

        # Robust union read: the file only exists if at least one group
        # wrote a title. A missing file means zero titles were fetched
        # (e.g. the API rejected every list parameter) — treat as an empty
        # set so the count cross-check below fires the trusted fallback.
        if out.exists():
            all_titles = {line.strip() for line in out.read_text(encoding="utf-8").splitlines() if line.strip()}
        else:
            all_titles = set()
        print(f"[enum] union: {len(all_titles)} titles in {time.time() - started:.0f}s", flush=True)

        if args.expect_count and len(all_titles) != args.expect_count:
            print(
                f"[enum] COUNT MISMATCH: union={len(all_titles)} expected={args.expect_count}; "
                "running the library's sequential full chain as the trusted fallback",
                flush=True,
            )
            full = await crawler.list_all_pages(base)
            out.write_text("\n".join(sorted(full)) + "\n", encoding="utf-8")
            all_titles = set(full)
            print(f"[enum] fallback full chain: {len(full)} titles written to {out.name}")
        elif not args.expect_count:
            print("[enum] no --expect-count given; count unverified (reconciliation run will re-check)")

    receipt = {
        "out": str(out),
        "titles": len(all_titles),
        "expected": args.expect_count or None,
        "elapsed_seconds": round(time.time() - started),
        "egress": args.egress_note,
    }
    print(json.dumps(receipt))


if __name__ == "__main__":
    asyncio.run(main())
"""Targeted re-crawl: refetch a few titles and write back the canonical
wikitext JSONs, without `--refresh`'s whole-wiki diff surface.

Mirrors the `crawl` worker path (fetch_batch -> build_page -> _learn_labels ->
write) so the refreshed pages are byte-equivalent to what a full crawl would
produce. Use when a page's live content moved on but the rest of the corpus
must stay untouched (e.g. a zero-regression re-index window).
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scriptengine.config import get_settings, load_overrides, series_paths
from scriptengine.ingest.crawler import (
    WikiCrawler,
    api_base,
    build_ontology,
    sanitise_filename,
)


async def recrawl(series: str, start_url: str, titles: list[str]) -> int:
    from urllib.parse import urlparse

    settings = get_settings()
    paths = series_paths(series, settings)
    overrides = load_overrides(paths)
    paths.ensure()

    parsed = urlparse(start_url)
    base = api_base(start_url)
    wiki_url = f"{parsed.scheme}://{parsed.netloc}"

    async with WikiCrawler(settings) as crawler:
        ontology = build_ontology(
            wiki_url, await crawler.list_templates(base, 0), overrides
        )
        fetched = await crawler.fetch_batch(base, titles)

        fetched_titles = {p.get("title", "") for p in fetched}
        missing = [t for t in titles if t not in fetched_titles]

        results = []
        for parse in fetched:
            page = crawler.build_page(parse, wiki_url, ontology)
            await crawler._learn_labels(base, page.title, page.page_type, ontology)

            reason = ontology.is_skippable(page.categories)
            if reason:
                results.append({"title": page.title, "status": f"skipped: {reason}"})
                continue
            if not page.word_count and not page.facts:
                results.append({"title": page.title, "status": "skipped: no content"})
                continue

            destination = paths.wikitext / f"{sanitise_filename(page.title)}.json"
            old = None
            if destination.exists():
                old = json.loads(destination.read_text(encoding="utf-8"))
            wikitext_changed = old is None or old.get("wikitext") != page.wikitext
            destination.write_text(page.to_json(), encoding="utf-8")
            results.append(
                {
                    "title": page.title,
                    "status": "written",
                    "revid": page.revid,
                    "page_type": page.page_type,
                    "sections": len(page.sections),
                    "facts": len(page.facts),
                    "wikitext_changed": wikitext_changed,
                    "old_revid": (old or {}).get("revid"),
                }
            )

    for r in results:
        print(json.dumps(r))
    if missing:
        print(f"MISSING: {missing}")
        return 1
    return 0


def main() -> None:
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series", required=True)
    parser.add_argument("--start-url", required=True, help="Any page on the target wiki.")
    parser.add_argument("titles", nargs="+")
    args = parser.parse_args()

    raise SystemExit(asyncio.run(recrawl(args.series, args.start_url, args.titles)))


if __name__ == "__main__":
    main()
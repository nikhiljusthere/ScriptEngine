"""Crawl stall detection (`CrawlStalled`) — the throttle → switch-IP protocol.

A crawl that completes zero pages while titles are still outstanding has a
dead or throttled egress path, not a slow one: it must stop so the operator
can change the egress IP (a different VPN server/country) and resume, and a
partial manifest must survive the stop. A crawl that is genuinely making
progress must never trip the watchdog.
"""

import asyncio
import json

import pytest

from scriptengine.config import Settings, SeriesPaths
from scriptengine.ingest.crawler import CrawlStalled, WikiCrawler


def _crawler_for(tmp_path, stall_seconds, fetch, name):
    class FakeCrawler(WikiCrawler):
        async def list_templates(self, base, limit=0):
            return []

        async def list_all_pages(self, base, limit=0):
            return [f"Page {i}" for i in range(4)]

        async def fetch_batch(self, base, titles):
            return await fetch(titles)

    settings = Settings(
        crawl_stall_seconds=stall_seconds,
        crawl_concurrency=2,
        crawl_delay_seconds=0.0,
    )
    return FakeCrawler(settings), SeriesPaths(name=name, root=tmp_path / name)


def test_crawl_raises_stalled_when_pages_never_complete(tmp_path):
    """Zero completed pages with work outstanding = a stalled egress path."""
    async def hang(titles):
        # Longer than the stall window, short enough to keep the test fast:
        # the watchdog fires while the batch is in flight, and the workers
        # drain out once the (fictitious) fetch gives up.
        await asyncio.sleep(2.0)
        return []

    crawler, paths = _crawler_for(tmp_path, stall_seconds=0.3, fetch=hang, name="stall")
    with pytest.raises(CrawlStalled):
        asyncio.run(
            crawler._crawl("https://example.fandom.com/wiki/Home", paths, 0, None)
        )

    # The partial manifest must survive the stop: `all_titles` has audit
    # value, and the stall must be recorded, not just raised.
    manifest = json.loads((paths.root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["stalled"] is True
    assert manifest["pages_enumerated"] == 4
    assert manifest["stall_remaining"] >= 0


def test_crawl_completes_without_stall(tmp_path):
    """A crawl that keeps completing pages never trips the watchdog."""
    async def fetch(titles):
        return [
            {
                "title": title,
                "pageid": i + 1,
                "revid": 1,
                "wikitext": f"== {title} ==\n\nProse about {title} with a sentence.",
                "sections": [],
                "categories": [],
                "templates": [],
                "redirects": [],
            }
            for i, title in enumerate(titles)
        ]

    crawler, paths = _crawler_for(tmp_path, stall_seconds=1.0, fetch=fetch, name="ok")
    manifest = asyncio.run(
        crawler._crawl("https://example.fandom.com/wiki/Home", paths, 0, None)
    )

    assert manifest["pages_written"] == 4
    assert not manifest.get("stalled")
    assert manifest["pages_failed"] == 0
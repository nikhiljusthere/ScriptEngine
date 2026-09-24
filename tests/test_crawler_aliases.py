"""Alias extraction from infobox parameters, including the wiki's own.

The engine's built-in keys cover the common wikis; a wiki whose alias fields
sit under other parameter names (Marvel's `CurrentAlias`) declares them via
the `alias_fact_keys:` override so the data lands on disk instead of being
dropped (plan MARVEL_100_PLAN.md §1 L2, step A1b).
"""

from __future__ import annotations

from scriptengine.ingest.crawler import WikiCrawler
from scriptengine.ingest.documents import Fact, WikiPage


def make_page(fact_keys: dict[str, str]) -> WikiPage:
    page = WikiPage(
        title="Spider-Man",
        url="https://marvel.fandom.com/wiki/Spider-Man",
    )
    page.facts = [Fact(key=key, value=value) for key, value in fact_keys.items()]
    return page


class TestAliasFactKeys:
    def test_the_builtin_keys_still_work(self):
        crawler = WikiCrawler()
        page = make_page({"alias": "Miles Morales"})
        assert crawler._aliases(page) == ["Miles Morales"]

    def test_declared_keys_are_additive_not_replacing(self):
        crawler = WikiCrawler()
        page = make_page(
            {
                "currentalias": "Spider-Man",
                "alias": "Friendly Neighbourhood Spider-Man",
            }
        )
        page.title = "Peter Parker (Earth-616)"
        # Without the declaration the live alias is invisible to `_aliases`.
        assert crawler._aliases(page) == ["Friendly Neighbourhood Spider-Man"]
        # With the Marvel declaration it lands alongside the built-ins.
        assert crawler._aliases(page, ("currentalias",)) == [
            "Friendly Neighbourhood Spider-Man",
            "Spider-Man",
        ]

    def test_declared_keys_are_read_lowercased(self):
        # The YAML may spell the key the wiki's way; the ontology normalises
        # it, and the stored fact keys are already lowercase.
        crawler = WikiCrawler()
        page = make_page({"currentalias": "Peter Parker"})
        assert crawler._aliases(page, ("currentalias",)) == ["Peter Parker"]
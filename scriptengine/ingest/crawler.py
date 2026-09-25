"""Fandom wiki crawler.

Descended from the previous project's crawler, which was the strongest code in
it: MediaWiki API instead of HTML scraping, `curl_cffi` browser impersonation to
satisfy Cloudflare, `allpages` enumeration, a worker pool with a semaphore, and
honest 429 handling. All of that is kept.

Two things changed.

**Fifty pages per request, not one.** This is the default and the only path;
there is no single-page fetch left to fall back to. Fandom rate-limits per
request rather than per page, which is why concurrency cannot buy speed here:
measured, raising workers from 3 to 10 and cutting the delay fourfold moved a
crawl from 112 pages/min to 117, because the extra connections were simply
served more slowly. `action=query` returns up to 50 pages of wikitext,
categories and templates in one call, and the same wiki then answers at over
2,000 pages/min. One Piece's 7,937 pages took three minutes.

What `action=query` withholds is recovered rather than lost, and both
compensations are cheap:

* the **section tree** is not needed, because `split_sections` locates headings
  in the wikitext anyway: byte offsets shift once templates expand, so the API
  only ever supplied the levels, and counting `=` signs agrees with it on 3,113
  of 3,114 sections across a 400-page sample;
* the **infobox schema** in `properties` describes a page *type*, so it is
  fetched once per newly seen type instead of once per page, roughly twenty
  requests per wiki rather than nine thousand.

**No link-following.** `allpages` already enumerates every article, so walking
links only re-discovers pages that are already queued. Wikilinks are still
collected (from the wikitext, where they are canonical) but as graph edges
rather than as a crawl frontier.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, cast
from urllib.parse import quote, urlparse

from curl_cffi import BrowserTypeLiteral
from curl_cffi.requests import AsyncSession, BrowserType

from scriptengine.config import Settings, SeriesPaths, get_settings
from scriptengine.ingest.documents import Edge, WikiPage
from scriptengine.ingest.ontology import (
    Ontology,
    build_ontology,
    discover_infoboxes,
    learn_field_labels,
    slugify_type as _slug,
)
from scriptengine.ingest.wikitext import (
    collect_ref_definitions,
    extract_citations,
    extract_links,
    facts_from_infobox,
    find_infobox,
    split_sections,
)

logger = logging.getLogger(__name__)

# Newest first: curl_cffi negotiates the closest fingerprint it supports.
PREFERRED_IMPERSONATIONS = (
    "chrome136", "chrome131", "chrome124", "chrome120",
    "chrome116", "chrome110", "firefox135", "firefox133",
)

# Titles per `action=query` request. MediaWiki caps this at 50 for anonymous
# callers and rejects the whole request past it, so this is the API's number
# rather than a tuning knob.
BATCH_SIZE = 50

# `list=allpages` is a far heavier query than `action=parse`, and Fandom
# throttles it much sooner for anonymous clients. 500 per page is the documented
# maximum and reliably triggers a 429; 100 does not.
ENUMERATION_PAGE_SIZE = 100

# Infobox fact keys that name a page's other names. The common wikis agree on
# this vocabulary; a wiki that does not (Marvel's `CurrentAlias`) adds its own
# via the `alias_fact_keys:` override, which `_aliases` reads off the ontology.
_ALIAS_FACT_KEYS = ("name", "romaji", "alias", "aliases", "othername", "eng name")


class EnumerationFailed(RuntimeError):
    """The wiki would not return its page list. Distinct from an empty wiki."""

class CrawlStalled(RuntimeError):
    """No page completed for the stall window while work remained.

    That is a dead or throttled egress path, not a slow one: the operator
    changes the egress IP (a different VPN server/country, or another
    network) and re-runs the same command, and the crawl resumes from disk.
    """

# Only one crawl at a time. The Electron UI can deliver the same IPC message
# twice, which previously produced two interleaved crawls writing the same files.
_CRAWL_LOCK = asyncio.Lock()


def select_impersonation() -> str:
    try:
        supported = {item.value for item in BrowserType}
    except Exception:
        supported = set()
    if not supported:
        return PREFERRED_IMPERSONATIONS[0]
    for candidate in PREFERRED_IMPERSONATIONS:
        if candidate in supported:
            return candidate
    return next(iter(supported))


def sanitise_filename(name: str) -> str:
    for char in r'/\:*?"<>|':
        name = name.replace(char, "_")
    return name.strip()[:150] or "page"


def api_base(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Not a usable wiki URL: {url!r}")
    return f"{parsed.scheme}://{parsed.netloc}/api.php"


class WikiCrawler:
    """Fetches a wiki into `series/<name>/wikitext/*.json`."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._session: AsyncSession | None = None
        self._impersonation = select_impersonation()
        self._last_error: str | None = None
        # When the wiki rate-limits, every worker waits, not just the one that
        # was told to. Ten workers each independently retrying is what turns a
        # single 429 into a sustained throttle.
        self._resume_at = 0.0
        self._throttle_lock = asyncio.Lock()

    async def _await_throttle(self) -> None:
        while True:
            delay = self._resume_at - asyncio.get_running_loop().time()
            if delay <= 0:
                return
            await asyncio.sleep(min(delay, 5.0))

    async def _throttle(self, seconds: float) -> None:
        # Some hosts answer 429 with an hour-long Retry-After. Honouring that
        # literally would hang the crawl; capping it keeps the back-off polite
        # without turning a transient limit into an overnight wait.
        seconds = min(float(seconds), 120.0)
        async with self._throttle_lock:
            resume = asyncio.get_running_loop().time() + seconds
            if resume > self._resume_at:
                self._resume_at = resume
                logger.warning("rate limited; pausing all workers for %.0fs", seconds)

    # ── session ──────────────────────────────────────────────────────────────

    async def __aenter__(self) -> "WikiCrawler":
        self._session = AsyncSession(
            # `select_impersonation` only ever returns a `BrowserType` value
            # spelled as a string; the stub wants the literal union.
            impersonate=cast(BrowserTypeLiteral, self._impersonation),
            max_clients=self.settings.crawl_concurrency,
            timeout=self.settings.crawl_timeout_seconds,
        )
        logger.info("session ready (impersonate=%s)", self._impersonation)
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._session is not None:
            closed = self._session.close()
            if inspect.isawaitable(closed):
                await closed
            self._session = None

    # ── API ──────────────────────────────────────────────────────────────────

    async def _get(self, base: str, params: dict[str, Any]) -> dict[str, Any] | None:
        """One API call, with retries, backoff, and rate-limit compliance."""
        assert self._session is not None, "Use WikiCrawler as an async context manager"
        headers = {
            "User-Agent": self.settings.user_agent,
            # No `Accept: application/json`: Fandom's edge WAF answers 403 to
            # it (verified 2026-09-18, the 2026-08-16 CSM crawl predates the
            # rule). The format is pinned by the `format=json` parameter, so
            # the header only cost blocks.
            "Accept-Language": "en-US,en;q=0.9",
        }

        for attempt in range(1, self.settings.crawl_max_retries + 1):
            try:
                await self._await_throttle()
                if attempt > 1:
                    await asyncio.sleep(random.uniform(1.0, 2.0) * attempt)

                response = await self._session.get(base, params=params, headers=headers)

                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After", 30))
                    await self._throttle(wait)
                    continue

                if response.status_code >= 400:
                    self._last_error = f"HTTP {response.status_code}"
                    logger.warning("HTTP %s for %s", response.status_code, params.get("page", ""))
                    return None

                return response.json()

            except Exception as error:  # network, TLS, JSON, all retryable
                self._last_error = str(error)
                logger.warning(
                    "attempt %s/%s failed for %s: %s",
                    attempt, self.settings.crawl_max_retries, params.get("page", ""), error,
                )
                await asyncio.sleep(min(2**attempt, 15))

        return None

    async def _enumerate(
        self,
        base: str,
        namespace: int,
        limit: int = 0,
        label: str = "titles",
        skip_redirects: bool = False,
    ) -> list[str]:
        """See `list_all_pages`. Raises `EnumerationFailed` rather than returning
        an empty list, because "the wiki has no pages" and "the wiki refused to
        answer" must not look the same to the caller."""
        """Page through `allpages` in one namespace.

        `limit` stops the walk early. This matters more than it looks: Jujutsu
        Kaisen has ~850 articles, but Marvel has hundreds of thousands, and
        enumerating all of them before fetching a single page turns a 25-page
        sample crawl into a multi-minute wait.
        """
        titles: list[str] = []
        apcontinue: str | None = None

        while True:
            params = {
                "action": "query", "list": "allpages",
                "aplimit": str(ENUMERATION_PAGE_SIZE),
                "apnamespace": str(namespace), "format": "json", "formatversion": "2",
            }
            if skip_redirects:
                params["apfilterredir"] = "nonredirects"
            if apcontinue:
                params["apcontinue"] = apcontinue

            data = await self._get(base, params)
            if not data:
                raise EnumerationFailed(
                    f"the wiki stopped answering after {len(titles)} {label}. "
                    "This is usually rate limiting; wait a few minutes and re-run "
                    "(the crawl resumes from what is already on disk)."
                )

            titles.extend(p["title"] for p in data.get("query", {}).get("allpages", []))
            logger.info("enumerated %s %s", len(titles), label)

            if limit and len(titles) >= limit:
                return titles[:limit]

            apcontinue = data.get("continue", {}).get("apcontinue")
            if not apcontinue:
                break
            await asyncio.sleep(0.3)

        return titles

    async def list_all_pages(self, base: str, limit: int = 0) -> list[str]:
        """Real article titles in the main namespace.

        Redirects are excluded. `allpages` lists them by default, and fetching
        one just returns the article it points at, a page already on disk. On
        Jujutsu Kaisen that inflated the wiki from 984 articles to 1,179
        "pages", and made every resumed crawl re-fetch ~195 redirects to
        rewrite files it already had.

        Redirect titles are still valuable as aliases, but they come from
        `prop=redirects` on the article, not from crawling them as pages.
        """
        return await self._enumerate(base, 0, limit, "articles", skip_redirects=True)

    async def list_templates(self, base: str, limit: int = 0) -> list[str]:
        """Pages in the `Template:` namespace, the wiki's own vocabulary."""
        return await self._enumerate(base, 10, limit, "templates")

    async def fetch_batch(
        self, base: str, titles: list[str]
    ) -> list[dict[str, Any]]:
        """Fetch many pages in one request, shaped like `action=parse` output.

        Fandom throttles per request, not per page, so asking for one page at a
        time is what makes a large wiki slow, measured at 51 pages/min against
        686 for a batched call, a 14x difference that no amount of concurrency
        recovers, because extra connections are simply served more slowly.

        `action=query` returns up to 50 pages of wikitext, categories and
        templates at once. It does not return two things `action=parse` does:

        * **the section tree.** Not needed: `split_sections` locates headings in
          the wikitext anyway, because byte offsets shift once templates are
          expanded, and the API only supplied the levels. Counting the `=` signs
          agrees with the API on 3,113 of 3,114 sections across a 400-page
          sample, the exception being a malformed level-1 heading.
        * **`properties`,** which carries the Portable Infobox schema and with it
          the wiki's own field labels ("class" is displayed as "Grade"). Those
          are per page *type*, not per page, so `_learn_labels` fetches them for
          one page of each new type instead of for all 8,000.
        """
        if not titles:
            return []

        data = await self._get(
            base,
            {
                "action": "query",
                "titles": "|".join(titles),
                "prop": "revisions|categories|templates",
                "rvprop": "content",
                "rvslots": "main",
                "cllimit": "max",
                "tllimit": "max",
                "clshow": "!hidden",
                "format": "json",
                "formatversion": "2",
                "redirects": "1",
            },
        )
        if not data or "error" in data:
            return []

        pages = []
        for page in (data.get("query") or {}).get("pages", []):
            if page.get("missing") or not page.get("revisions"):
                continue
            revision = page["revisions"][0]
            content = (revision.get("slots") or {}).get("main", {}).get("content", "")
            pages.append(
                {
                    "title": page.get("title", ""),
                    "pageid": page.get("pageid", 0),
                    "revid": revision.get("revid", 0),
                    "wikitext": content,
                    # `split_sections` reads levels from the wikitext when this
                    # is empty, which is what the docstring above measured.
                    "sections": [],
                    "categories": [
                        {"category": c.get("title", "").split(":", 1)[-1]}
                        for c in page.get("categories", [])
                    ],
                    "templates": [
                        {"title": t.get("title", "")} for t in page.get("templates", [])
                    ],
                    "redirects": [],
                }
            )
        return pages

    async def _learn_labels(
        self, base: str, title: str, page_type: str, ontology: Ontology
    ) -> None:
        """Fetch one page's infobox schema, once per page type.

        The labels are a property of the type, and `learn_field_labels` already
        ignores a type it has seen. Fetching them per page cost one request per
        page for information that changes once per twenty-odd types.

        The fetch is bounded: a challenged egress (a WAF 429-loop on the parse
        endpoint) used to wedge this call for minutes, and the wedge sat
        between the batch fetch and the page write, so a hot egress stalled the
        whole crawl with "0 written" while the batch endpoint was healthy.
        Labels are enrichment only, so a failed or timed-out attempt falls back
        to the default labels and the crawl keeps moving.
        """
        if not page_type or page_type == "unknown" or page_type in ontology.field_labels:
            return
        try:
            data = await asyncio.wait_for(
                self._get(
                    base,
                    {
                        "action": "parse", "page": title, "prop": "properties",
                        "format": "json", "formatversion": "2", "redirects": "1",
                    },
                ),
                timeout=self.settings.crawl_timeout_seconds + 30.0,
            )
        except Exception as error:
            logger.warning(
                "label learning failed for type %r (%s); using default labels",
                page_type, error,
            )
            data = None
        if data and "error" not in data:
            learn_field_labels(ontology, page_type, (data.get("parse") or {}).get("properties"))
        if page_type not in ontology.field_labels:
            # The attempt found no Portable Infobox schema (or failed above):
            # record the type anyway, or every page of it pays this request
            # again.
            ontology.field_labels[page_type] = {}

    async def expand_templates(self, base: str, text: str) -> str:
        """Expand one template call, returning the resolved wikitext.

        `action=expandtemplates` is the only API call that returns wikitext:
        `action=parse` with `prop=wikitext` leaves a transclusion unresolved and
        `prop=text` renders HTML, and this engine parses wikitext. The crawler
        skips the Template: namespace, so a page's canonical curated list can
        be a bare `{{Ten Shadows Shikigami}}` with no links; resolution is what
        makes that list visible to the index.
        """
        data = await self._get(
            base,
            {
                "action": "expandtemplates",
                "text": text,
                "prop": "wikitext",
                "format": "json",
                "formatversion": "2",
            },
        )
        if not data or "error" in data:
            return ""
        return (data.get("expandtemplates") or {}).get("wikitext", "") or ""

    # ── extraction ───────────────────────────────────────────────────────────

    def build_page(
        self, parse: dict[str, Any], wiki_url: str, ontology: Ontology
    ) -> WikiPage:
        """Turn one API response into a fully extracted `WikiPage`."""
        title = parse.get("title", "")
        wikitext = parse.get("wikitext", "") or ""
        categories = [
            c.get("category", "").replace("_", " ")
            for c in parse.get("categories", [])
            if not c.get("hidden")
        ]
        templates = [t.get("title", t) if isinstance(t, dict) else t
                     for t in parse.get("templates", [])]

        page_type, matched = ontology.type_for_templates(templates)

        # MediaWiki subpages ("Aoi Todo/Synopsis") carry no infobox of their own
        # they elaborate on their parent. Typing them from the parent keeps
        # substantial prose out of the "unknown" bucket. This is MediaWiki
        # convention, not a wiki-specific rule.
        if page_type == "unknown" and "/" in title:
            parent, _, leaf = title.rpartition("/")
            parent_type = ontology.page_types.get(parent, "")
            if parent and parent_type and parent_type != "unknown":
                page_type = f"{parent_type}_{_slug(leaf)}"
            elif parent:
                # An untyped parent gives the leaf nothing to qualify. Naming the
                # type after the leaf anyway invents one type per subpage,
                # "page_premature_death_vol_1" and friends.
                page_type = "subpage"
            matched = matched or f"subpage of {parent}"

        learn_field_labels(ontology, page_type, parse.get("properties"))

        lead, sections = split_sections(
            wikitext,
            parse.get("sections", []),
            ontology.citation_works,
            item_sections=ontology.item_sections,
            title=title,
        )
        # Named references are defined once per page and reused by name, so the
        # map has to be built from the whole page before anything is stripped.
        ref_names = collect_ref_definitions(wikitext)

        facts = []
        infobox = find_infobox(wikitext, set(ontology.infobox_types))
        if infobox:
            template_name, params = infobox
            facts = facts_from_infobox(
                params, ontology.labels_for(page_type), ref_names
            )
            if page_type == "unknown":
                page_type = ontology.infobox_types.get(
                    template_name.lower().replace("_", " "), "unknown"
                )
            matched = matched or template_name

        page = WikiPage(
            title=title,
            url=f"{wiki_url}/wiki/{quote(title.replace(' ', '_'))}",
            pageid=parse.get("pageid", 0),
            revid=parse.get("revid", 0),
            page_type=page_type,
            infobox_template=matched,
            categories=categories,
            templates=[str(t) for t in templates],
            lead=lead,
            sections=sections,
            facts=facts,
            links=extract_links(wikitext),
            citations=extract_citations(wikitext, ref_names),
            redirects=[r.get("from", "") for r in parse.get("redirects", [])],
            wikitext=wikitext,
            fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        ontology.page_types[title] = page_type
        page.aliases = self._aliases(page, ontology.alias_fact_keys)
        page.edges = self._edges(page)

        if not sections and not lead:
            page.warnings.append("no prose extracted")
        if page_type == "unknown" and facts:
            page.warnings.append("infobox parsed but type not in discovered vocabulary")

        return page

    def _aliases(self, page: WikiPage, extra_keys: tuple[str, ...] = ()) -> list[str]:
        """Other names this page answers to, for entity linking later.

        ``extra_keys`` comes from the series' `alias_fact_keys:` override:
        the built-ins cover the common wikis, and a wiki whose alias fields
        sit under other parameter names (Marvel's `CurrentAlias`) declares
        them, so the data lands on disk instead of being dropped (plan §1 L2).
        """
        names = {page.title, *page.redirects}
        for key in dict.fromkeys((*_ALIAS_FACT_KEYS, *extra_keys)):
            fact = page.fact(key)
            if fact and fact.value:
                # Aliases are often a comma or <br>-separated list.
                names.update(part.strip() for part in fact.value.split(",") if part.strip())
        return sorted(n for n in names if n and n != page.title)

    def _edges(self, page: WikiPage) -> list[Edge]:
        """Relationships, strongest evidence first.

        An infobox parameter is an editor stating a fact and scores high. A link
        in prose is weaker (it means the pages are related, not how) so it is
        recorded as a generic mention and ranked accordingly.
        """
        edges: list[Edge] = []
        seen: set[tuple[str, str, str]] = set()

        for fact in page.facts:
            for link in fact.links:
                key = (fact.key, link.target, "infobox")
                if key in seen:
                    continue
                seen.add(key)
                edges.append(
                    Edge(
                        source=page.title,
                        relation=fact.key,
                        target=link.target,
                        confidence=0.95,
                        provenance="infobox",
                        section=fact.label or fact.key,
                    )
                )

        for section in page.sections:
            for link in section.links:
                key = ("mentions", link.target, section.title)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(
                    Edge(
                        source=page.title,
                        relation="mentions",
                        target=link.target,
                        confidence=0.4,
                        provenance="prose",
                        section=section.breadcrumb,
                    )
                )

        return edges

    # ── crawl ────────────────────────────────────────────────────────────────

    async def crawl(
        self,
        start_url: str,
        paths: SeriesPaths,
        max_pages: int = 0,
        overrides: dict[str, Any] | None = None,
        refresh: bool = False,
    ) -> dict[str, Any]:
        if _CRAWL_LOCK.locked():
            logger.warning("a crawl is already running; refusing to start a second")
            return {"status": "already_running", "pages": 0}
        async with _CRAWL_LOCK:
            return await self._crawl(start_url, paths, max_pages, overrides, refresh)

    async def _crawl(
        self,
        start_url: str,
        paths: SeriesPaths,
        max_pages: int,
        overrides: dict[str, Any] | None,
        refresh: bool = False,
    ) -> dict[str, Any]:
        base = api_base(start_url)
        parsed = urlparse(start_url)
        wiki_url = f"{parsed.scheme}://{parsed.netloc}"
        paths.ensure()

        logger.info("discovering type vocabulary from %s", base)
        # On a sample crawl, cap the vocabulary scan too. A truncated vocabulary
        # degrades gracefully: `type_for_templates` falls back to matching the
        # word "infobox" in the template name, which is the Fandom convention.
        template_limit = 3000 if max_pages else 0
        ontology = build_ontology(
            wiki_url, await self.list_templates(base, template_limit), overrides
        )
        logger.info(
            "discovered %s page types: %s",
            len(ontology.types), ", ".join(ontology.types) or "(none)",
        )

        # A capped crawl only needs enough titles to fill the cap. Ask for a
        # margin so that skipped pages (galleries, disambiguations) still leave
        # `max_pages` worth of real content.
        enumeration_limit = max_pages * 3 if max_pages else 0
        all_titles = await self.list_all_pages(base, enumeration_limit)
        titles = all_titles[:max_pages] if max_pages else list(all_titles)

        # Resume by default. A wiki can rate-limit or a run can be interrupted
        # partway through several hundred pages; refetching everything to reach
        # the point of failure is both slow and rude to the host.
        already_have: set[str] = set()
        if not refresh:
            already_have = {
                path.stem for path in paths.wikitext.glob("*.json")
            }
            remaining = [
                title for title in titles
                if sanitise_filename(title) not in already_have
            ]
            if len(remaining) < len(titles):
                logger.info(
                    "resuming: %s of %s pages already on disk",
                    len(titles) - len(remaining), len(titles),
                )
            titles = remaining

        logger.info("crawling %s of %s enumerated pages", len(titles), len(all_titles))

        queue: asyncio.Queue[str] = asyncio.Queue()
        for title in titles:
            queue.put_nowait(title)

        semaphore = asyncio.Semaphore(self.settings.crawl_concurrency)
        written = 0
        skipped: list[dict[str, str]] = []
        failed: list[str] = []
        counter_lock = asyncio.Lock()
        # `redirects=1` means several enumerated titles can resolve to the same
        # article, which otherwise gets fetched and written more than once.
        seen_pages: set[Any] = set()
        # A stalled crawl is one with work left but no progress: a throttled or
        # dead egress path, where every in-flight batch times out and the queue
        # never drains. Waiting it out in place burns hours, so a watchdog stops
        # the crawl after `crawl_stall_seconds` of zero completed pages and the
        # operator changes the egress IP (a different VPN server/country, or
        # another network) and re-runs: the crawl resumes from disk, so
        # stopping costs nothing. The watchdog only counts real work — queued
        # titles plus in-flight batches — so a crawl finishing its last batch
        # is never mistaken for a stall.
        loop = asyncio.get_running_loop()
        progress = {"last": loop.time()}
        in_flight = {"titles": 0}
        stalled = asyncio.Event()

        async def watchdog() -> None:
            while True:
                await asyncio.sleep(min(5.0, self.settings.crawl_stall_seconds / 10))
                remaining = queue.qsize() + in_flight["titles"]
                if remaining and loop.time() - progress["last"] > self.settings.crawl_stall_seconds:
                    logger.error(
                        "no page completed for %.0fs with %s titles still "
                        "outstanding; the egress path is stalled, stopping the "
                        "crawl (CrawlStalled)",
                        self.settings.crawl_stall_seconds, remaining,
                    )
                    stalled.set()
                    return

        async def worker() -> None:
            nonlocal written
            while not stalled.is_set():
                batch: list[str] = []
                while len(batch) < BATCH_SIZE:
                    try:
                        batch.append(queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break
                if not batch:
                    return

                in_flight["titles"] += len(batch)
                try:
                    async with semaphore:
                        fetched = await self.fetch_batch(base, batch)

                    returned = {parse.get("title", "") for parse in fetched}
                    failed.extend(t for t in batch if t not in returned)

                    for parse in fetched:
                        identity = parse.get("pageid") or parse.get("title")
                        async with counter_lock:
                            if identity in seen_pages:
                                continue
                            seen_pages.add(identity)

                        page = self.build_page(parse, wiki_url, ontology)
                        await self._learn_labels(
                            base, page.title, page.page_type, ontology
                        )

                        reason = ontology.is_skippable(page.categories)
                        if reason:
                            skipped.append({"page": page.title, "reason": reason})
                            continue
                        if not page.word_count and not page.facts:
                            skipped.append({"page": page.title, "reason": "no content"})
                            continue

                        destination = (
                            paths.wikitext / f"{sanitise_filename(page.title)}.json"
                        )
                        destination.write_text(page.to_json(), encoding="utf-8")

                        async with counter_lock:
                            written += 1
                            done = written
                            # A page hit disk: the egress path is alive, and the
                            # stall clock resets.
                            progress["last"] = loop.time()
                        # The UI parses this line for live progress.
                        print(
                            f"[{done}/{len(titles)}] {page.title} "
                            f"| type={page.page_type} | facts={len(page.facts)} "
                            f"| sections={len(page.sections)} | queue={queue.qsize()}",
                            flush=True,
                        )

                except Exception as error:
                    logger.warning("failed on batch of %s: %s", len(batch), error)
                    failed.extend(batch)
                finally:
                    in_flight["titles"] -= len(batch)
                    for _ in batch:
                        queue.task_done()
                    if self.settings.crawl_delay_seconds:
                        await asyncio.sleep(self.settings.crawl_delay_seconds)

        watchdog_task = asyncio.ensure_future(watchdog())
        try:
            await asyncio.gather(
                *(worker() for _ in range(self.settings.crawl_concurrency))
            )
        finally:
            watchdog_task.cancel()

        manifest = {
            "series": paths.name,
            "wiki": wiki_url,
            "api": base,
            "crawled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pages_enumerated": len(all_titles),
            # A capped run never saw the whole wiki, so link targets pointing at
            # pages it did not enumerate are not broken links. The audit needs
            # to know the difference before it reports on graph integrity.
            "enumeration_capped": bool(max_pages),
            "pages_fetched_this_run": written,
            # Total on disk, including anything a resumed run already had.
            "pages_on_disk": len(list(paths.wikitext.glob("*.json"))),
            # Every article title on the wiki. The audit resolves wikilink
            # targets against this rather than against what was crawled, so a
            # capped sample does not report thousands of false dangling edges.
            "all_titles": all_titles,
            "pages_written": written,
            "pages_skipped": len(skipped),
            "pages_failed": len(failed),
            "ontology": ontology.to_dict(),
            "skipped": skipped[:200],
            "failed": failed[:200],
        }
        # A capped run deliberately enumerates a slice, so it must not overwrite
        # the full title list the audit resolves links against.
        #
        # An uncapped run is always trusted now, even when it sees fewer titles
        # than before: failed enumeration raises `EnumerationFailed` and never
        # reaches this point, so a smaller number here means a more accurate one.
        # Guarding on size alone kept a stale count of 1,179 after redirects
        # were excluded and the real article count turned out to be 1,089.
        previous = load_manifest(paths)
        if max_pages and len(previous.get("all_titles") or ()) > len(all_titles):
            logger.warning(
                "keeping the previous manifest: it lists %s titles, this run saw %s",
                len(previous["all_titles"]), len(all_titles),
            )
            manifest["all_titles"] = previous["all_titles"]
            manifest["pages_enumerated"] = len(previous["all_titles"])

        if stalled.is_set():
            # Persist the partial manifest (the full `all_titles` list still
            # has audit value on an incomplete run), then stop: a crawl with
            # zero progress and work left is stalled, not finished.
            manifest["stalled"] = True
            manifest["stall_remaining"] = queue.qsize() + in_flight["titles"]
            manifest["stall_reason"] = (
                f"no page completed for "
                f"{self.settings.crawl_stall_seconds:.0f}s while titles were "
                "outstanding; change the egress IP and re-run to resume"
            )
        paths.manifest.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        if stalled.is_set():
            raise CrawlStalled(
                f"no pages completed for {self.settings.crawl_stall_seconds:.0f}s "
                f"while {manifest['stall_remaining']} titles were still "
                f"outstanding ({written} written this run). The egress path is "
                "stalled (throttled or dead), not slow: change the egress IP "
                "(a different VPN server/country, or another network), then "
                "re-run the same command — the crawl resumes from what is on "
                "disk."
            )
        logger.info(
            "crawl complete: %s written, %s skipped, %s failed",
            written, len(skipped), len(failed),
        )
        return manifest


def reextract(page: WikiPage, ontology: Ontology) -> WikiPage:
    """Re-run extraction on a page's stored wikitext.

    Fetching a page is expensive; parsing it is not. Keeping the wikitext means
    a parser fix can be applied to the whole corpus in seconds instead of
    re-crawling several hundred pages, and it keeps the index honest, since
    indexing always reflects the extraction code as it stands now rather than
    as it stood on the day of the crawl.
    """
    if not page.wikitext:
        return page

    crawler = WikiCrawler.__new__(WikiCrawler)  # no session needed for parsing
    parse = {
        "title": page.title,
        "wikitext": page.wikitext,
        "pageid": page.pageid,
        "revid": page.revid,
        "sections": [
            {"line": section.title, "level": section.level}
            for section in page.sections
        ],
        "categories": [{"category": category} for category in page.categories],
        "templates": page.templates,
        "redirects": [{"from": name} for name in page.redirects],
    }
    wiki_url = page.url.split("/wiki/")[0] if "/wiki/" in page.url else ""
    refreshed = crawler.build_page(parse, wiki_url, ontology)
    refreshed.fetched_at = page.fetched_at
    return refreshed


def load_extracted(
    paths: SeriesPaths, overrides: dict[str, Any] | None = None
) -> tuple[list[WikiPage], Ontology]:
    """Load a crawled corpus and re-extract it with the current parser.

    The single entry point for everything downstream, so that `audit` and
    `index` can never disagree about what the corpus contains: auditing the
    extraction stored at crawl time while indexing a freshly parsed one would
    make the audit a report on history.

    The type vocabulary is merged from two directions: what the crawl found by
    template name, and what page structure votes for. Name matching alone finds
    Jujutsu Kaisen's "* Infobox" templates and nothing on a wiki that calls its
    infobox `Character`.
    """
    manifest = load_manifest(paths)
    pages = list(load_pages(paths))
    if not pages:
        return [], Ontology()

    ontology = Ontology.from_dict(manifest.get("ontology") or {})
    discovered = discover_infoboxes(
        manifest.get("wiki", ""),
        ((page.title, page.wikitext) for page in pages if page.wikitext),
        overrides,
    )
    ontology.infobox_types.update(discovered.infobox_types)
    ontology.infobox_votes = discovered.infobox_votes
    ontology.skip_categories |= discovered.skip_categories
    # The manifest predates the overrides being read here, and re-extraction is
    # the only place the citation vocabulary is used. Taking it from the freshly
    # built ontology is what lets `overrides.yaml` reach a corpus that is being
    # re-parsed rather than re-crawled.
    ontology.citation_works = discovered.citation_works
    # Same reason: the manifest was written before `ability_sections` existed,
    # and re-extraction is the only place the item markers are read.
    ontology.item_sections = discovered.item_sections
    # L2 hooks (plan §1): only where the current override declares them, so a
    # corpus crawled with a declared set is not wiped by a later no-override
    # re-extraction.
    if discovered.skip_patterns is not None:
        ontology.skip_patterns = discovered.skip_patterns
    if discovered.alias_fact_keys:
        ontology.alias_fact_keys = discovered.alias_fact_keys

    return [reextract(page, ontology) for page in pages], ontology


def load_pages(paths: SeriesPaths) -> Iterable[WikiPage]:
    """Read back everything a crawl wrote."""
    for path in sorted(paths.wikitext.glob("*.json")):
        try:
            yield WikiPage.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            logger.warning("skipping unreadable page %s: %s", path.name, error)


def load_manifest(paths: SeriesPaths) -> dict[str, Any]:
    if not paths.manifest.exists():
        return {}
    return json.loads(paths.manifest.read_text(encoding="utf-8"))


def parse_page(paths: SeriesPaths, title: str) -> WikiPage:
    """Parse one stored page with the current extraction code.

    `load_extracted` re-parses a whole corpus; this reads a single page, for
    callers that need one page's current facts and sections without touching
    the rest of the disk. Missing file is a `FileNotFoundError` naming the
    title, because "not crawled" is a different failure from "bad page".
    """
    path = paths.wikitext / f"{sanitise_filename(title)}.json"
    if not path.exists():
        raise FileNotFoundError(f"no stored crawl for page {title!r} at {path}")
    page = WikiPage.from_dict(json.loads(path.read_text(encoding="utf-8")))
    manifest = load_manifest(paths)
    ontology = Ontology.from_dict(manifest.get("ontology") or {})
    return reextract(page, ontology)

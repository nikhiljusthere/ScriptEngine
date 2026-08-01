"""Fandom wiki crawler.

Descended from the previous project's crawler, which was the strongest code in
it: MediaWiki API instead of HTML scraping, `curl_cffi` browser impersonation to
satisfy Cloudflare, `allpages` enumeration, a worker pool with a semaphore, and
honest 429 handling. All of that is kept.

Two things changed.

**One request per page instead of two.** `action=parse` accepts
`prop=wikitext|sections|categories|templates|links|properties`, so the wikitext,
the section tree, the categories, the transclusions and the infobox schema all
arrive together.

**No link-following.** `allpages` already enumerates every article, so walking
links only re-discovers pages that are already queued. Wikilinks are still
collected — from the wikitext, where they are canonical — but as graph edges
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
from typing import Any, Iterable
from urllib.parse import quote, urlparse

from curl_cffi.requests import AsyncSession, BrowserType

from scriptengine.config import Settings, SeriesPaths, get_settings
from scriptengine.ingest.documents import Edge, WikiPage
from scriptengine.ingest.ontology import (
    Ontology,
    build_ontology,
    learn_field_labels,
    slugify_type as _slug,
)
from scriptengine.ingest.wikitext import (
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

PAGE_PROPS = "wikitext|sections|categories|templates|properties|displaytitle|revid"

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

    # ── session ──────────────────────────────────────────────────────────────

    async def __aenter__(self) -> "WikiCrawler":
        self._session = AsyncSession(
            impersonate=self._impersonation,
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
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }

        for attempt in range(1, self.settings.crawl_max_retries + 1):
            try:
                if attempt > 1:
                    await asyncio.sleep(random.uniform(1.0, 2.0) * attempt)

                response = await self._session.get(base, params=params, headers=headers)

                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After", 30))
                    logger.warning("rate limited, sleeping %ss", wait)
                    await asyncio.sleep(wait)
                    continue

                if response.status_code >= 400:
                    self._last_error = f"HTTP {response.status_code}"
                    logger.warning("HTTP %s for %s", response.status_code, params.get("page", ""))
                    return None

                return response.json()

            except Exception as error:  # network, TLS, JSON — all retryable
                self._last_error = str(error)
                logger.warning(
                    "attempt %s/%s failed for %s: %s",
                    attempt, self.settings.crawl_max_retries, params.get("page", ""), error,
                )
                await asyncio.sleep(min(2**attempt, 15))

        return None

    async def _enumerate(
        self, base: str, namespace: int, limit: int = 0, label: str = "titles"
    ) -> list[str]:
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
                "action": "query", "list": "allpages", "aplimit": "500",
                "apnamespace": str(namespace), "format": "json", "formatversion": "2",
            }
            if apcontinue:
                params["apcontinue"] = apcontinue

            data = await self._get(base, params)
            if not data:
                break

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
        """Article titles in the main namespace."""
        return await self._enumerate(base, 0, limit, "articles")

    async def list_templates(self, base: str, limit: int = 0) -> list[str]:
        """Pages in the `Template:` namespace — the wiki's own vocabulary."""
        return await self._enumerate(base, 10, limit, "templates")

    async def fetch_page(self, base: str, title: str) -> dict[str, Any] | None:
        data = await self._get(
            base,
            {
                "action": "parse", "page": title, "prop": PAGE_PROPS,
                "format": "json", "formatversion": "2", "redirects": "1",
            },
        )
        if not data or "error" in data:
            if data and data.get("error", {}).get("code") not in {"missingtitle", None}:
                logger.warning("API error on %s: %s", title, data["error"].get("code"))
            return None
        return data.get("parse")

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
        # — they elaborate on their parent. Typing them from the parent keeps
        # substantial prose out of the "unknown" bucket. This is MediaWiki
        # convention, not a wiki-specific rule.
        if page_type == "unknown" and "/" in title:
            parent, _, leaf = title.rpartition("/")
            if parent:
                page_type = f"{ontology.page_types.get(parent, 'page')}_{_slug(leaf)}"
                matched = matched or f"subpage of {parent}"

        learn_field_labels(ontology, page_type, parse.get("properties"))

        lead, sections = split_sections(wikitext, parse.get("sections", []))

        facts = []
        infobox = find_infobox(wikitext, set(ontology.infobox_types))
        if infobox:
            template_name, params = infobox
            facts = facts_from_infobox(params, ontology.labels_for(page_type))
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
            citations=extract_citations(wikitext),
            redirects=[r.get("from", "") for r in parse.get("redirects", [])],
            wikitext=wikitext,
            fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        ontology.page_types[title] = page_type
        page.aliases = self._aliases(page)
        page.edges = self._edges(page)

        if not sections and not lead:
            page.warnings.append("no prose extracted")
        if page_type == "unknown" and facts:
            page.warnings.append("infobox parsed but type not in discovered vocabulary")

        return page

    def _aliases(self, page: WikiPage) -> list[str]:
        """Other names this page answers to, for entity linking later."""
        names = {page.title, *page.redirects}
        for key in ("name", "romaji", "alias", "aliases", "othername", "eng name"):
            fact = page.fact(key)
            if fact and fact.value:
                # Aliases are often a comma or <br>-separated list.
                names.update(part.strip() for part in fact.value.split(",") if part.strip())
        return sorted(n for n in names if n and n != page.title)

    def _edges(self, page: WikiPage) -> list[Edge]:
        """Relationships, strongest evidence first.

        An infobox parameter is an editor stating a fact and scores high. A link
        in prose is weaker — it means the pages are related, not how — so it is
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
    ) -> dict[str, Any]:
        if _CRAWL_LOCK.locked():
            logger.warning("a crawl is already running; refusing to start a second")
            return {"status": "already_running", "pages": 0}
        async with _CRAWL_LOCK:
            return await self._crawl(start_url, paths, max_pages, overrides)

    async def _crawl(
        self,
        start_url: str,
        paths: SeriesPaths,
        max_pages: int,
        overrides: dict[str, Any] | None,
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
        seen_pages: set[int] = set()

        async def worker() -> None:
            nonlocal written
            while True:
                try:
                    title = queue.get_nowait()
                except asyncio.QueueEmpty:
                    return

                try:
                    async with semaphore:
                        parse = await self.fetch_page(base, title)

                    if not parse:
                        failed.append(title)
                        continue

                    identity = parse.get("pageid") or parse.get("title")
                    async with counter_lock:
                        if identity in seen_pages:
                            continue
                        seen_pages.add(identity)

                    page = self.build_page(parse, wiki_url, ontology)

                    reason = ontology.is_skippable(page.categories)
                    if reason:
                        skipped.append({"page": page.title, "reason": reason})
                        continue
                    if not page.word_count and not page.facts:
                        skipped.append({"page": page.title, "reason": "no content"})
                        continue

                    destination = paths.wikitext / f"{sanitise_filename(page.title)}.json"
                    destination.write_text(page.to_json(), encoding="utf-8")

                    async with counter_lock:
                        written += 1
                        done = written
                    # The UI parses this line for live progress.
                    print(
                        f"[{done}/{len(titles)}] {page.title} "
                        f"| type={page.page_type} | facts={len(page.facts)} "
                        f"| sections={len(page.sections)} | queue={queue.qsize()}",
                        flush=True,
                    )

                except Exception as error:
                    logger.warning("failed on %s: %s", title, error)
                    failed.append(title)
                finally:
                    queue.task_done()
                    if self.settings.crawl_delay_seconds:
                        await asyncio.sleep(self.settings.crawl_delay_seconds)

        await asyncio.gather(
            *(worker() for _ in range(self.settings.crawl_concurrency))
        )

        manifest = {
            "series": paths.name,
            "wiki": wiki_url,
            "api": base,
            "crawled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pages_enumerated": len(titles),
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
        paths.manifest.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        logger.info(
            "crawl complete: %s written, %s skipped, %s failed",
            written, len(skipped), len(failed),
        )
        return manifest


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

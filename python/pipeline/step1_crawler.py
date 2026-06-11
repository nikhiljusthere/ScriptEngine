"""Fandom wiki crawler using MediaWiki API — bypasses Cloudflare entirely."""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse, quote

from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession
from curl_cffi.requests import BrowserType
from python.config import config
from python.helper import get_scrapped_data_dir


logger = logging.getLogger(__name__)

CRAWL_INGESTION_DATA_DIR = get_scrapped_data_dir()

PREFERRED_IMPERSONATIONS = (
    "chrome136", "chrome131", "chrome124", "chrome120",
    "chrome116", "chrome110", "firefox135", "firefox133",
)

API_HEADERS = {
    "User-Agent": "AnimeRAGBot/1.0 (research crawler)",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── module-level lock so only ONE crawl_series runs at a time ────────────────
_CRAWL_LOCK = asyncio.Lock()


def _select_impersonation() -> str:
    try:
        supported = {item.value for item in BrowserType}
    except Exception:
        supported = set()
    if not supported:
        return PREFERRED_IMPERSONATIONS[0]
    for imp in PREFERRED_IMPERSONATIONS:
        if imp in supported:
            return imp
    return next(iter(supported))


def _sanitize(name: str) -> str:
    for ch in r'/\:*?"<>|':
        name = name.replace(ch, "_")
    return name


def _root_domain(netloc: str) -> str:
    return netloc.lower().removeprefix("www.")


def _is_fandom(url: str) -> bool:
    return "fandom.com/wiki/" in url


def _fandom_api_base(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/api.php"


def _wiki_title(url: str) -> str:
    path = urlparse(url).path
    title = path.split("/wiki/", 1)[-1]
    return title.replace("_", " ")


class AnimeCrawler:
    def __init__(
        self,
        concurrency: int = 10,
        max_retries: int = 4,
        timeout: float = 20.0,
        delay_between_requests: float = 0.2,
    ):
        self.concurrency = concurrency
        self.max_retries = max_retries
        self.timeout = timeout
        self.delay_between_requests = delay_between_requests
        self._session: Optional[AsyncSession] = None
        self._impersonation = _select_impersonation()
        self._last_fetch_error: Optional[str] = None

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    async def _init_session(self) -> None:
        if self._session is not None:
            return
        self._session = AsyncSession(
            impersonate=self._impersonation,
            max_clients=self.concurrency,
            timeout=self.timeout,
        )
        logger.info(f"curl_cffi session ready (impersonate={self._impersonation})")

    async def _close_session(self) -> None:
        if self._session is not None:
            close_result = self._session.close()
            if inspect.isawaitable(close_result):
                await close_result
            self._session = None

    # ------------------------------------------------------------------
    # MediaWiki API fetch
    # ------------------------------------------------------------------

    async def _fetch_via_mediawiki_api(
        self, url: str, series: str, page_type: str
    ) -> Optional[Dict[str, Any]]:
        api_base = _fandom_api_base(url)
        title = _wiki_title(url)

        for attempt in range(1, self.max_retries + 1):
            try:
                if attempt > 1:
                    await asyncio.sleep(random.uniform(1.0, 2.0) * attempt)

                response = await self._session.get(
                    api_base,
                    params={
                        "action": "parse",
                        "page": title,
                        "prop": "text|links",
                        "format": "json",
                        "redirects": "1",
                        "disableeditsection": "1",
                    },
                    headers=API_HEADERS,
                )

                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After", 30))
                    logger.warning(f"Rate limited — sleeping {wait}s")
                    await asyncio.sleep(wait)
                    continue

                if response.status_code >= 400:
                    self._last_fetch_error = f"HTTP {response.status_code} for {url}"
                    logger.warning(self._last_fetch_error)
                    return None

                data = response.json()

                if "error" in data:
                    code = data["error"].get("code", "")
                    if code == "missingtitle":
                        return None
                    self._last_fetch_error = f"API error for {url}: {code}"
                    logger.warning(self._last_fetch_error)
                    return None

                parse = data.get("parse", {})
                html = parse.get("text", {}).get("*", "")
                if not html:
                    return None

                soup = BeautifulSoup(html, "lxml")
                for tag in soup(["script", "style", "nav", "footer",
                                  "aside", "table", "noscript"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)
                page_title = parse.get("title", title)

                parsed_url = urlparse(url)
                base = f"{parsed_url.scheme}://{parsed_url.netloc}/wiki/"
                links = [
                    base + link["*"].replace(" ", "_")
                    for link in parse.get("links", [])
                    if link.get("ns") == 0
                ]

                return {
                    "url": url,
                    "series": series,
                    "page_type": page_type,
                    "content": text,
                    "html": html,
                    "title": page_title,
                    "links": links,
                    "metadata": {"status_code": 200, "content_type": "mediawiki-api"},
                }

            except Exception as e:
                self._last_fetch_error = f"{url}: {e}"
                logger.warning(f"API attempt {attempt}/{self.max_retries} error for {url}: {e}")
                await asyncio.sleep(min(2 ** attempt, 15))

        self._last_fetch_error = f"All {self.max_retries} API attempts failed for {url}"
        logger.error(self._last_fetch_error)
        return None

    # ------------------------------------------------------------------
    # HTML fetch (non-Fandom sites)
    # ------------------------------------------------------------------

    async def crawl_url(
        self, url: str, series: str, page_type: str = "other"
    ) -> Optional[Dict[str, Any]]:
        if _is_fandom(url):
            return await self._fetch_via_mediawiki_api(url, series, page_type)

        assert self._session is not None, "Session not initialised"

        for attempt in range(1, self.max_retries + 1):
            try:
                if attempt > 1:
                    await asyncio.sleep(random.uniform(1.0, 3.0) * attempt)

                response = await self._session.get(
                    url,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/136.0.0.0 Safari/537.36"
                        ),
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Cache-Control": "no-cache",
                    },
                )

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 30))
                    await asyncio.sleep(retry_after)
                    continue

                if response.status_code >= 400:
                    self._last_fetch_error = f"HTTP {response.status_code} for {url}"
                    logger.warning(self._last_fetch_error)
                    return None

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    return None

                soup = BeautifulSoup(response.text, "lxml")
                links = self._extract_links(soup, url)

                for tag in soup(["script", "style", "nav", "footer",
                                  "aside", "header", "noscript"]):
                    tag.decompose()

                text = soup.get_text(separator="\n", strip=True)
                title = soup.title.string.strip() if soup.title else ""

                return {
                    "url": url,
                    "series": series,
                    "page_type": page_type,
                    "content": text,
                    "html": response.text,
                    "title": title,
                    "links": links,
                    "metadata": {"status_code": response.status_code, "content_type": content_type},
                }

            except Exception as e:
                self._last_fetch_error = f"{url}: {e}"
                logger.warning(f"Attempt {attempt}/{self.max_retries} error for {url}: {e}")
                await asyncio.sleep(min(2 ** attempt, 15))

        self._last_fetch_error = f"All {self.max_retries} attempts failed for {url}"
        logger.error(self._last_fetch_error)
        return None

    # ------------------------------------------------------------------
    # Seed all pages via allpages API
    # ------------------------------------------------------------------

    async def _seed_all_pages(self, wiki_base_url: str) -> List[str]:
        api_base = _fandom_api_base(wiki_base_url)
        parsed = urlparse(wiki_base_url)
        url_base = f"{parsed.scheme}://{parsed.netloc}/wiki/"

        all_titles: List[str] = []
        apcontinue: Optional[str] = None
        batch = 0

        logger.info(f"Seeding all pages from {api_base} ...")

        while True:
            params: Dict[str, Any] = {
                "action": "query",
                "list": "allpages",
                "aplimit": "500",
                "apnamespace": "0",
                "format": "json",
            }
            if apcontinue:
                params["apcontinue"] = apcontinue

            try:
                response = await self._session.get(
                    api_base, params=params, headers=API_HEADERS
                )
                data = response.json()
            except Exception as e:
                logger.warning(f"allpages seed error: {e}")
                break

            pages = data.get("query", {}).get("allpages", [])
            for p in pages:
                title = p["title"].replace(" ", "_")
                all_titles.append(url_base + quote(title, safe="/:@!$&'()*+,;="))

            batch += 1
            logger.info(f"  Seeded batch {batch}: {len(all_titles)} titles so far")

            apcontinue = data.get("continue", {}).get("apcontinue")
            if not apcontinue:
                break

            await asyncio.sleep(0.3)

        logger.info(f"Seed complete — {len(all_titles)} articles found")
        return all_titles

    # ------------------------------------------------------------------
    # Crawl series
    # ------------------------------------------------------------------

    async def crawl_series(
        self,
        start_url: str,
        series: str,
        page_type_map: Optional[Dict[str, str]] = None,
        max_pages: Optional[int] = None,
        output_format: str = "txt",
    ) -> List[Dict[str, Any]]:

        # ── prevent duplicate concurrent crawls ─────────────────────────
        # The double-logging you saw means crawl_series was called twice
        # simultaneously (likely two IPC messages from Electron). This lock
        # ensures only one runs at a time; the second call waits then exits
        # immediately since results are already on disk.
        if _CRAWL_LOCK.locked():
            logger.warning("crawl_series called while another crawl is running — skipping duplicate")
            return []

        async with _CRAWL_LOCK:
            return await self._do_crawl(
                start_url, series, page_type_map, max_pages, output_format
            )

    async def _do_crawl(
        self,
        start_url: str,
        series: str,
        page_type_map: Optional[Dict[str, str]] = None,
        max_pages: Optional[int] = None,
        output_format: str = "txt",
    ) -> List[Dict[str, Any]]:
        start_parsed = urlparse(start_url)
        allowed_domain = _root_domain(start_parsed.netloc)
        logger.info(f"Allowed domain: '{allowed_domain}'")
        output_format = output_format.lower().strip()
        if output_format not in {"txt", "raw"}:
            raise ValueError(f"Unsupported output format: {output_format}")

        seen_urls: Set[str] = set()
        seen_lock = asyncio.Lock()
        queue: asyncio.Queue[str] = asyncio.Queue()
        results: List[Dict[str, Any]] = []
        results_lock = asyncio.Lock()
        pages_started = 0
        pages_done = 0
        pages_lock = asyncio.Lock()
        sem = asyncio.Semaphore(self.concurrency)
        stop_event = asyncio.Event()

        async def _enqueue(url: str) -> bool:
            async with seen_lock:
                if url in seen_urls:
                    return False
                seen_urls.add(url)
            await queue.put(url)
            return True

        def _discard_pending_queue() -> int:
            discarded = 0
            while True:
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    return discarded
                queue.task_done()
                discarded += 1

        logger.info(f"Starting crawl for '{series}' from {start_url}")
        await self._init_session()

        if _is_fandom(start_url):
            seed_urls = await self._seed_all_pages(start_url)
            if not seed_urls:
                seed_urls = [start_url]
            for u in seed_urls:
                await _enqueue(u)
        else:
            await _enqueue(start_url)

        async def worker() -> None:
            nonlocal pages_done, pages_started
            while not stop_event.is_set():
                try:
                    url = await asyncio.wait_for(queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                try:
                    async with pages_lock:
                        if max_pages is not None and pages_started >= max_pages:
                            stop_event.set()
                            discarded = _discard_pending_queue()
                            if discarded:
                                logger.info(
                                    f"Reached max_pages={max_pages}; discarded "
                                    f"{discarded} pending URLs"
                                )
                            return
                        pages_started += 1

                    async with sem:
                        result = await self._crawl_single(url, series, page_type_map)

                    async with pages_lock:
                        pages_done += 1
                        done_now = pages_done
                        reached_limit = (
                            max_pages is not None and pages_done >= max_pages
                        )
                        if reached_limit:
                            stop_event.set()

                    if result and (result.get("content") or result.get("html")):
                        dump_dir = Path(CRAWL_INGESTION_DATA_DIR) / _sanitize(series)
                        dump_dir.mkdir(parents=True, exist_ok=True)
                        safe_name = (
                            _sanitize(result.get("title", "page"))[:100]
                            or _sanitize(url)[:100]
                        )
                        if output_format == "raw":
                            file_path = dump_dir / f"{safe_name}.html"
                            file_content = result.get("html", "") or result.get("content", "")
                        else:
                            file_path = dump_dir / f"{safe_name}.txt"
                            file_content = result.get("content", "") or ""

                        file_path.write_text(file_content, encoding="utf-8")
                        print(f"WRITING PAGE: {file_path.name}")
                        async with results_lock:
                            results.append(result)

                    new_count = 0
                    if not stop_event.is_set() and result and result.get("links"):
                        for link in result["links"]:
                            if _root_domain(urlparse(link).netloc) != allowed_domain:
                                continue
                            if await _enqueue(link):
                                new_count += 1

                    logger.info(
                        f"[{done_now}] {url[:90]} "
                        f"| +{new_count} links | queue={queue.qsize()} | seen={len(seen_urls)}"
                    )

                    if reached_limit:
                        discarded = _discard_pending_queue()
                        if discarded:
                            logger.info(
                                f"Reached max_pages={max_pages}; discarded "
                                f"{discarded} pending URLs"
                            )

                finally:
                    queue.task_done()

                if self.delay_between_requests > 0:
                    await asyncio.sleep(self.delay_between_requests)

        try:
            workers = [asyncio.create_task(worker()) for _ in range(self.concurrency)]
            await queue.join()
            stop_event.set()
            await asyncio.gather(*workers)
        finally:
            await self._close_session()

        if pages_done > 0 and not results:
            detail = self._last_fetch_error or "pages returned no crawlable content"
            raise RuntimeError(f"Crawl stopped with 0 pages with content. Last error: {detail}")

        logger.info(
            f"Crawl complete — {len(results)} pages with content / "
            f"{pages_done} visited / {len(seen_urls)} unique URLs discovered"
        )
        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _crawl_single(self, url: str, series: str, page_type_map=None):
        page_type = self._detect_page_type(url, page_type_map)
        result = await self.crawl_url(url, series, page_type)
        if result:
            result["checksum"] = hashlib.sha256(
                (result.get("content", "") or "").encode()
            ).hexdigest()
        return result

    def _detect_page_type(self, url: str, page_type_map=None) -> str:
        if page_type_map and url in page_type_map:
            return page_type_map[url]
        u = url.lower()
        if "/episode" in u or "ep=" in u:     return "episode"
        if "/chapter" in u or "ch=" in u:     return "chapter"
        if "/character" in u or "char=" in u: return "character_page"
        if "/technique" in u or "tech=" in u: return "technique_page"
        if "/arc" in u or "arc=" in u:        return "arc_page"
        return "other"

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        valid: List[str] = []
        seen: Set[str] = set()
        for tag in soup.find_all("a", href=True):
            href = tag["href"].strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            if parsed.scheme not in ("http", "https"):
                continue
            clean = parsed._replace(fragment="").geturl()
            if clean not in seen:
                seen.add(clean)
                valid.append(clean)
        return valid


anime_crawler = AnimeCrawler(
    concurrency=10,
    max_retries=4,
    timeout=20.0,
    delay_between_requests=0.2,
)

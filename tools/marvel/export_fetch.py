#!/usr/bin/env python3
"""Fetch a Fandom wiki via Special:Export — an independent source B.

The pipeline crawl (source A) reads a wiki through the MediaWiki *query API*
(`action=query&prop=revisions`). This tool reads the same wiki through a
different MediaWiki code path, the *export handler* (`Special:Export/<Title>`,
export-0.11 XML), with its own independent enumeration. If both agree
page-for-page, the corpus has two independent witnesses; if they disagree,
the reconcile receipt (tools/marvel/reconcile.py) names exactly which pages
and which source moved.

Verified 2026-09-25 on marvel.fandom.com: the batch `pages=` parameter is
ignored by Fandom (GET and POST, wildcard and real csrf token all return the
bare XML skeleton), so the export path is per-title: `Special:Export/<Title>`.
That is ~279k requests for Marvel Database — resumable, one file per page.

What it does (all resumable — re-run continues from disk):
  1. enumerate main-namespace non-redirect pages via `list=allpages`
     (independent of the crawl's enumeration) -> <series>/export/enumeration.jsonl
  2. fetch `Special:Export/<title>` one title at a time,
     one JSON per page under <series>/export/
  3. write <series>/export/RECEIPT.json once every enumerated title is on disk

Run:  scriptengine/.venv/bin/python tools/marvel/export_fetch.py --wiki marvel
      scriptengine/.venv/bin/python tools/marvel/export_fetch.py --wiki mcu --workers 2
"""
import json
import sys
import threading
import time
import xml.etree.ElementTree as ET
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from curl_cffi.requests import get

REPO = Path(__file__).resolve().parent.parent.parent

# wiki id -> (fandom host, series folder under series/)
WIKIS = {
    "marvel": ("https://marvel.fandom.com", "marvel"),
    "mcu": ("https://marvelcinematicuniverse.fandom.com", "mcu"),
}
UA = "ScriptEngine/0.1 (wiki knowledge indexer; https://github.com/nikhiljusthere/ScriptEngine)"
IMPERSONATE = "chrome136"

# Shared 429 back-off: one 429 pauses every worker, like the crawler does.
_throttle_until = 0.0
_throttle_lock = threading.Lock()


def await_throttle() -> None:
    global _throttle_until
    while True:
        with _throttle_lock:
            delay = _throttle_until - time.monotonic()
        if delay <= 0:
            return
        time.sleep(min(delay, 5.0))


def throttle(seconds: float) -> None:
    global _throttle_until
    seconds = min(float(seconds), 120.0)
    with _throttle_lock:
        resume = time.monotonic() + seconds
        if resume > _throttle_until:
            _throttle_until = resume
            print(f"rate limited; pausing all workers {seconds:.0f}s", flush=True)


def http_get(url: str, params: dict | None = None, retries: int = 4) -> bytes | None:
    """GET with 429 compliance and exponential backoff. Returns body or None."""
    params = dict(params or {})
    for attempt in range(1, retries + 1):
        await_throttle()
        if attempt > 1:
            time.sleep(1.5 * attempt)
        try:
            r = get(url, params=params, impersonate=IMPERSONATE, timeout=60,
                    headers={"User-Agent": UA})
        except Exception as error:
            print(f"  attempt {attempt}/{retries} failed: {error}", flush=True)
            continue
        if r.status_code == 429:
            throttle(int(r.headers.get("Retry-After", 30)))
            continue
        if r.status_code >= 400:
            print(f"  HTTP {r.status_code} for {url.split('?')[0]}", flush=True)
            return None
        return r.content
    return None


def sanitize(title: str) -> str:
    """Same filename rule as the crawler (crawler.py:sanitise_filename)."""
    for char in r'/\:*?"<>|':
        title = title.replace(char, "_")
    return title.strip()[:150] or "page"


def enumerate_titles(out: Path, api: str, limit: int = 0) -> list[str]:
    """Independent main-namespace enumeration, streamed to enumeration.jsonl.

    Resumable: each line is `{title, pageid}`; a final `{"done": true}` line
    marks a completed walk. Resuming continues from the last enumerated
    title (`apcontinue`), so a re-run never duplicates lines.
    """
    enum = out / "enumeration.jsonl"
    known: list[str] = []
    apcontinue: str | None = None
    complete = False
    if enum.exists():
        lines = enum.read_text(encoding="utf-8").strip().splitlines()
        for line in lines:
            row = json.loads(line)
            if "title" not in row:
                if row.get("done"):
                    complete = True
                break  # a sentinel line ends the walk; nothing after it
            known.append(row["title"])
            apcontinue = row["title"]
        if complete:
            print(f"enumeration already complete: {len(known)} titles", flush=True)
            return known[:limit] if limit else known
        print(f"resuming enumeration from {len(known)} titles (after {apcontinue!r})", flush=True)

    print("enumerating main namespace (independent source B list)...", flush=True)
    with enum.open("a", encoding="utf-8") as fh:
        while True:
            params = {
                "action": "query", "list": "allpages",
                "aplimit": "100", "apnamespace": "0", "apfilterredir": "nonredirects",
                "format": "json",
            }
            if apcontinue:
                params["apcontinue"] = apcontinue
            data = json.loads(http_get(api, params) or b"{}")
            pages = (data.get("query") or {}).get("allpages", [])
            if not pages:
                raise SystemExit(f"enumeration refused after {len(known)} titles "
                                 f"(rate limit? wait a few minutes and re-run)")
            for page in pages:
                known.append(page["title"])
                fh.write(json.dumps({"title": page["title"], "pageid": page["pageid"]}) + "\n")
            fh.flush()
            apcontinue = pages[-1]["title"]
            if limit and len(known) >= limit:
                break
            if "apcontinue" not in (data.get("continue") or {}):
                break
            time.sleep(0.3)
        fh.write(json.dumps({"done": "apcontinue" not in (data.get("continue") or {}) and not limit}) + "\n")
    print(f"enumerated {len(known)} titles", flush=True)
    return known[:limit] if limit else known


def export_url_for(base: str, title: str) -> str:
    """Per-title URL path form — the only Special:Export shape Fandom honours.

    `pages=` (batch) is silently ignored (verified 2026-09-25: GET/POST,
    wildcard and real csrf tokens all return the bare skeleton), so the
    export source is per-title. Percent-encoding the path handles titles
    with pipes, slashes and friends.
    """
    return f"{base}/wiki/Special:Export/{quote(title, safe='')}"


def fetch_title(base: str, title: str) -> dict | None:
    """One Special:Export/<title> request -> {title, pageid, revid, timestamp, wikitext}."""
    body = http_get(export_url_for(base, title))
    if body is None:
        return None
    try:
        root = ET.fromstring(body)
    except ET.ParseError as error:
        print(f"  export XML undecodable for {title!r}: {error}", flush=True)
        return None
    ns = root.tag[: root.tag.index("}") + 1] if "}" in root.tag else ""

    def pages_in(elem):
        # single-title responses wrap one <page>; tolerate the plural shape
        yield elem
        for child in elem:
            if child.tag.split("}", 1)[-1] == "page":
                yield child

    for page in pages_in(root):
        if page.tag.split("}", 1)[-1] != "page":
            continue
        title_el = page.find(f"{ns}title")
        pageid = (page.findtext(f"{ns}pageid") or "0")
        revision = page.find(f"{ns}revision")
        revid = revision.findtext(f"{ns}id") if revision is not None else ""
        timestamp = revision.findtext(f"{ns}timestamp") if revision is not None else ""
        text_elem = revision.find(f"{ns}text") if revision is not None else None
        wikitext = text_elem.text if text_elem is not None and text_elem.text else ""
        record = {"title": (title_el.text if title_el is not None else title),
                  "pageid": int(pageid), "revid": int(revid or 0),
                  "timestamp": timestamp, "wikitext": wikitext}
        if page.find(f"{ns}redirect") is not None:
            record["redirect"] = True
        return record
    return None


def save_page(out: Path, record: dict) -> None:
    record = {**record, "source": "special-export",
              "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (out / f"{sanitize(record['title'])}.json").write_text(
        json.dumps(record, ensure_ascii=False), encoding="utf-8")


def worker(queue: deque, out: Path, base: str, stats: dict, stats_lock: threading.Lock) -> None:
    while True:
        with stats_lock:
            if not queue:
                return
            title = queue.popleft()
        record = fetch_title(base, title)
        with stats_lock:
            if record is None:
                stats["failed_batches"] += 1
                stats["failed"].append(title)
            else:
                save_page(out, record)
                stats["written"] += 1
                if stats["written"] % 2000 == 0:
                    print(f"[{stats['written']} written, {len(queue)} titles queued]", flush=True)
        time.sleep(0.25)  # per-worker spacing on top of the shared 429 pause


def main() -> None:
    wiki_id = "marvel"
    limit = 0
    workers = 2
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--wiki" and i + 1 < len(args):
            wiki_id = args[i + 1]
        elif arg == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
        elif arg == "--workers" and i + 1 < len(args):
            workers = int(args[i + 1])
    if wiki_id not in WIKIS:
        raise SystemExit(f"unknown wiki {wiki_id!r}; choose from {sorted(WIKIS)}")
    base, series_folder = WIKIS[wiki_id]
    out = REPO / "series" / series_folder / "export"
    out.mkdir(parents=True, exist_ok=True)
    api = f"{base}/api.php"

    titles = enumerate_titles(out, api, limit)
    print(f"{len(titles)} titles to fetch via {base}/wiki/Special:Export/<title>", flush=True)

    existing = {p.stem for p in out.glob("*.json") if p.name != "RECEIPT.json"}
    todo = [t for t in titles if sanitize(t) not in existing]
    print(f"resuming: {len(titles) - len(todo)} of {len(titles)} on disk; "
          f"{len(todo)} to fetch", flush=True)

    queue = deque(todo)
    stats = {"written": 0, "failed_batches": 0, "failed": []}
    stats_lock = threading.Lock()
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(worker, queue, out, base, stats, stats_lock)
                   for _ in range(workers)]
        for f in futures:
            f.result()

    on_disk = len([p for p in out.glob("*.json") if p.name != "RECEIPT.json"])
    receipt = {
        "source": "special-export",
        "wiki": wiki_id,
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "enumerated": len(titles),
        "on_disk": on_disk,
        "failed_requests": stats["failed_batches"],
        "failed_titles": len(set(stats["failed"])),
        "complete": on_disk >= len(titles) and not stats["failed"],
    }
    (out / "RECEIPT.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
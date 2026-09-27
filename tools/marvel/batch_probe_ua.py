#!/usr/bin/env python3
"""One-shot: replicate the crawler's exact session (impersonation + its headers)
on the 50-title batch URL, to discriminate 'egress is dirty' from
'WAF treats the crawler's ScriptEngine UA + browser-TLS combo differently'."""
import asyncio
import json
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from curl_cffi.requests import AsyncSession

from scriptengine.ingest.crawler import select_impersonation

URL_FILE = "/tmp/uk_batch_probe.jsonl"
CRAWLER_UA = "ScriptEngine/0.1 (wiki knowledge indexer; https://github.com/nikhiljusthere/ScriptEngine)"
BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


async def probe(session: AsyncSession, label: str, url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}/api.php"
    params = dict(urllib.parse.parse_qsl(parsed.query))
    headers = {"User-Agent": label if False else CRAWLER_UA if label == "crawler" else BROWSER_UA,
               "Accept-Language": "en-US,en;q=0.9"}
    t0 = time.time()
    try:
        r = await session.get(base, params=params, headers=headers)
        dt = time.time() - t0
        d = r.json()
        pages = (d.get("query") or {}).get("pages", [])
        have = [p for p in pages if not p.get("missing") and p.get("revisions")]
        print(f"{label}-UA batch: HTTP {r.status_code} in {dt:.2f}s, {len(r.content)} bytes, pages {len(have)}/{len(pages)}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"{label}-UA batch EXC after {time.time() - t0:.1f}s: {type(e).__name__}: {str(e)[:200]}", flush=True)


async def main() -> None:
    url = Path(URL_FILE).read_text(encoding="utf-8").splitlines()[0].strip()
    imp = select_impersonation()
    print(f"impersonation: {imp}", flush=True)
    async with AsyncSession(impersonate=imp, max_clients=2, timeout=60) as s:
        await probe(s, "crawler", url)
        await probe(s, "browser", url)


if __name__ == "__main__":
    asyncio.run(main())
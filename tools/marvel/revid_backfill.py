#!/usr/bin/env python3
"""F1 revid backfill for the MARVEL 100% campaign (untracked campaign
tooling, public API only).

F1 (GATE A council, 2026-09-25): every stored page carries `revid: 0`
because the original crawl fetched `prop=revisions` with `rvprop=content`
alone, which filters the revid out of the revision object. The gated fix
(`rvprop=ids|content`, 664796b2) stamps revids natively on new crawls;
this tool stamps the EXISTING corpus with a one-way metadata update:

  * batches of 50 stored titles -> one `action=query` request
    (`prop=revisions`, `rvprop=ids`, `redirects=1` — the same convention as
    `revid_spotcheck.py`);
  * match by the stored `pageid` (a stored title may now redirect; the live
    revision belongs to the page, not the title spelling);
  * surgical in-place edit: only the `"revid": <n>` line is rewritten
    (byte-preserving for every other key), atomic .tmp + replace;
  * resumable: a file with a non-zero stored revid is already stamped and
    is skipped, so after an egress rotation the same command picks up where
    it stopped.

Throttle policy (plan §1a): on a 429 the run stops cleanly (exit 2) with
the resume state in the receipt; the operator rotates the egress IP
(nordvpn, exhausted-country pool) and re-runs. A stalled IP is never
blind-retried.

Usage (from the repo root):
  PYTHONPATH=$PWD scriptengine/.venv/bin/python tools/marvel/revid_backfill.py \
      --series marvel --limit 200            # smoke: 4 batches
  PYTHONPATH=$PWD scriptengine/.venv/bin/python tools/marvel/revid_backfill.py \
      --series marvel --egress-note "GB 194.88.x (nordvpn)"
  PYTHONPATH=$PWD scriptengine/.venv/bin/python tools/marvel/revid_backfill.py \
      --series marvel --probe "Elizabeth Tyne (Earth-33263)"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scriptengine.config import series_paths  # noqa: E402

WIKIS = {
    "marvel": "https://marvel.fandom.com",
    "mcu": "https://marvelcinematicuniverse.fandom.com",
}
# Campaign WAF-UA finding (2026-09-25): fetch-side campaign calls carry the
# chrome136 browser UA (see plan §1a + wall episode record).
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)
REVID_LINE = re.compile(r'(?m)^(\s*)"revid":\s*\d+([,\s]*)$')


def stamp_revid(path: Path, live_revid: int) -> bool:
    """Rewrite only the revid line; verify the JSON still parses to the
    same dict with the new value. Returns False on any anomaly."""
    text = path.read_text(encoding="utf-8")
    new_text, n = REVID_LINE.subn(
        lambda m: f'{m.group(1)}"revid": {live_revid}{m.group(2)}', text, count=1
    )
    if n != 1:
        print(f"[backfill] ANOMALY {path.name}: revid line not found/unique; skipped",
              flush=True)
        return False
    before = json.loads(text)
    after = json.loads(new_text)
    if {k: v for k, v in before.items() if k != "revid"} != {
        k: v for k, v in after.items() if k != "revid"
    } or after.get("revid") != live_revid:
        print(f"[backfill] ANOMALY {path.name}: round-trip check failed; skipped",
              flush=True)
        return False
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(path)
    return True


def probe(api: str, title: str) -> dict[str, Any]:
    from curl_cffi.requests import get

    params = {
        "action": "query", "titles": title, "format": "json",
        "prop": "revisions", "rvprop": "ids", "redirects": "1",
    }
    r = get(api, params=params, impersonate="chrome136", timeout=30,
            headers={"User-Agent": UA})
    data = r.json()
    pages = (data.get("query") or {}).get("pages") or {}
    page = next(iter(pages.values()), {})
    if page.get("missing") or not page.get("revisions"):
        return {"title": title, "live_revid": None,
                "status": "missing-live (title no longer resolves)"}
    return {"title": title, "live_revid": page["revisions"][0].get("revid"),
            "live_pageid": page.get("pageid"),
            "live_title": page.get("title"), "status": "ok"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", required=True, choices=sorted(WIKIS))
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--delay", type=float, default=0.8,
                    help="seconds between batch requests (default 0.8)")
    ap.add_argument("--workers", type=int, default=1,
                    help="parallel batch fetches (default 1 = sequential; "
                         "a 429/error still stops the whole run cleanly)")
    ap.add_argument("--limit", type=int, default=0,
                    help="stamp at most N unstamped files (smoke test); 0 = all")
    ap.add_argument("--probe", action="append", default=[],
                    metavar="TITLE",
                    help="probe one live title (missing/redirect check), "
                         "then exit")
    ap.add_argument("--egress-note", default="")
    a = ap.parse_args()

    api = f"{WIKIS[a.series]}/api.php"
    if a.probe:
        for title in a.probe:
            print(json.dumps(probe(api, title), ensure_ascii=False))
        return 0

    paths = series_paths(a.series)
    wdir = paths.wikitext
    files = sorted(p for p in wdir.glob("*.json") if p.name != "RECEIPT.json")
    pending: list[tuple[Path, str, int]] = []  # (file, title, stored_pageid)
    already_stamped = 0
    unreadable = 0
    for path in files:
        try:
            stored = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - recorded, not fatal
            unreadable += 1
            continue
        if stored.get("revid"):
            already_stamped += 1
            continue
        pending.append(
            (path, stored.get("title") or path.stem, stored.get("pageid", 0))
        )
    if a.limit:
        pending = pending[: a.limit]

    from curl_cffi.requests import get

    print(f"[backfill {a.series}] {len(files)} files | stamped-skipped "
          f"{already_stamped} | unstamped {len(pending)} | unreadable "
          f"{unreadable}", flush=True)
    if not pending:
        print("[backfill] nothing to do")
        return 0

    stamped = 0
    missing: list[str] = []
    failed_batches = 0
    batches_run = 0
    stop_reason = "complete"

    def stamp_chunk(chunk, data):
        """Stamp one fetched batch; return (stamped_n, missing_titles)."""
        pages = (data.get("query") or {}).get("pages") or {}
        by_pageid = {
            int(pid): page for pid, page in pages.items() if not page.get("missing")
        }
        n_stamped = 0
        m: list[str] = []
        for path, title, pageid in chunk:
            page = by_pageid.get(int(pageid))
            live = (
                page["revisions"][0].get("revid")
                if page and page.get("revisions") else None
            )
            if live is None:
                m.append(title)
                continue
            if stamp_revid(path, live):
                n_stamped += 1
        return n_stamped, m

    def fetch_chunk(chunk):
        """One API batch; return (chunk, kind, data). kind: ok | throttled-429
        | api-error: ... | error: ..."""
        params = {
            "action": "query", "titles": "|".join(t for _, t, _ in chunk),
            "format": "json", "prop": "revisions", "rvprop": "ids",
            "redirects": "1",
        }
        r = get(api, params=params, impersonate="chrome136", timeout=60,
                headers={"User-Agent": UA})
        if r.status_code == 429:
            return chunk, "throttled-429", None
        data = r.json()
        if "error" in data:
            return chunk, f"api-error: {data.get('error')}", None
        return chunk, "ok", data

    if a.workers <= 1:
        for start in range(0, len(pending), a.batch_size):
            chunk = pending[start : start + a.batch_size]
            try:
                _, kind, data = fetch_chunk(chunk)
            except Exception as error:  # noqa: BLE001 - network/parse, stop clean
                failed_batches += 1
                stop_reason = f"error: {error}"
                break
            if kind != "ok":
                failed_batches += 1
                stop_reason = kind
                break
            n_st, m = stamp_chunk(chunk, data)
            stamped += n_st
            missing.extend(m)
            batches_run += 1
            done = start + len(chunk)
            print(f"[backfill {a.series}] batch {batches_run}: {done}/{len(pending)} "
                  f"stamped={stamped} missing={len(missing)}", flush=True)
            if done < len(pending) and a.delay:
                time.sleep(a.delay)
    else:
        # Parallel batches: N in-flight API fetches; the first 429/error sets
        # the stop flag, queued batches are skipped, in-flight ones finish,
        # and the run exits cleanly (same receipt/exit-code contract).
        stop_event = threading.Event()

        def work(chunk):
            if stop_event.is_set():
                return chunk, "skipped", None
            try:
                chunk, kind, data = fetch_chunk(chunk)
            except Exception as error:  # noqa: BLE001 - stop clean, resume later
                stop_event.set()
                return chunk, f"error: {error}", None
            if kind != "ok":
                stop_event.set()
            if kind == "ok" and a.delay:
                time.sleep(a.delay)
            return chunk, kind, data

        with ThreadPoolExecutor(max_workers=a.workers) as pool:
            futures = [
                pool.submit(work, pending[i:i + a.batch_size])
                for i in range(0, len(pending), a.batch_size)
            ]
            files_done = 0
            for fut in as_completed(futures):
                chunk, kind, data = fut.result()
                if kind == "skipped":
                    continue
                if kind != "ok":
                    failed_batches += 1
                    stop_reason = kind
                    break
                n_st, m = stamp_chunk(chunk, data)
                stamped += n_st
                missing.extend(m)
                batches_run += 1
                files_done += len(chunk)
                print(f"[backfill {a.series}] batch {batches_run}: "
                      f"{files_done}/{len(pending)} stamped={stamped} "
                      f"missing={len(missing)} (workers={a.workers})",
                      flush=True)

    receipt = {
        "series": a.series,
        "wiki": WIKIS[a.series],
        "files_total": len(files),
        "already_stamped": already_stamped,
        "unstamped_at_start": len(pending),
        "stamped_this_run": stamped,
        "unreadable": unreadable,
        "missing_live": missing,
        "failed_batches": failed_batches,
        "batches_run": batches_run,
        "stop_reason": stop_reason,
        "resume": ("re-run the same command; stamped files are skipped"
                   if stop_reason != "complete" else None),
        "egress_note": a.egress_note,
        "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    out = REPO / "reports" / "marvel" / "receipts" / \
        f"revid_backfill_{a.series}_{stop_reason}_2026-09-26.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    print(f"receipt -> {out}")
    return 2 if stop_reason != "complete" else 0


if __name__ == "__main__":
    sys.exit(main())
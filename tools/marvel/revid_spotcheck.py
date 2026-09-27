#!/usr/bin/env python3
"""GATE A exit evidence (3): revid spot-check.

Plan MARVEL_100_PLAN.md, GATE A item (3): 10 random stored pages,
stored `revid` == live API `revid` (or an explicit diff = the wiki was
edited between crawl and check — recorded, not a failure).

Read-only on the corpus; 10 API requests per series (trivial egress).

Run:  scriptengine/.venv/bin/python tools/marvel/revid_spotcheck.py --series marvel
      scriptengine/.venv/bin/python tools/marvel/revid_spotcheck.py --series mcu
"""
import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKIS = {
    "marvel": "https://marvel.fandom.com",
    "mcu": "https://marvelcinematicuniverse.fandom.com",
}
# Campaign WAF-UA finding (2026-09-25): Cloudflare WAF challenges the
# ScriptEngine crawler UA on this egress; every fetch-side campaign call
# carries the chrome136 browser UA (see plan §1a + wall episode record).
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", choices=sorted(WIKIS), required=True)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    from curl_cffi.requests import get

    wdir = REPO / "series" / args.series / "wikitext"
    files = sorted(p for p in wdir.glob("*.json") if p.name != "RECEIPT.json")
    if not files:
        raise SystemExit(f"no stored pages under {wdir}")
    random.seed(args.seed)
    picks = random.sample(files, min(args.n, len(files)))

    api = f"{WIKIS[args.series]}/api.php"
    rows = []
    for path in picks:
        stored = json.loads(path.read_text(encoding="utf-8"))
        title = stored.get("title") or path.stem
        params = {
            "action": "query", "titles": title, "format": "json",
            "prop": "revisions", "rvprop": "ids",
        }
        try:
            r = get(api, params=params, impersonate="chrome136", timeout=30,
                    headers={"User-Agent": UA})
            data = r.json()
        except Exception as error:  # noqa: BLE001 - recorded, not fatal
            rows.append({"title": title, "stored_revid": stored.get("revid"),
                         "live_revid": None, "status": f"fetch-error: {error}"})
            continue
        pages = (data.get("query") or {}).get("pages") or {}
        page = next(iter(pages.values()), {})
        live = None
        if page.get("revisions"):
            live = page["revisions"][0].get("revid")
        status = ("match" if live == stored.get("revid")
                  else "WIKI-EDITED (diff recorded)" if live is not None
                  else "page-missing-live")
        rows.append({"title": title, "stored_revid": stored.get("revid"),
                     "live_revid": live, "status": status})

    report = {
        "series": args.series,
        "wiki": WIKIS[args.series],
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n": len(rows),
        "matches": sum(1 for r in rows if r["status"] == "match"),
        "rows": rows,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                  encoding="utf-8")
        print(f"receipt -> {args.out}")
    # A wiki edit between crawl and check is expected over a campaign; the
    # receipt records it. Only fetch errors / missing pages fail the check.
    bad = [r for r in rows if r["status"].startswith(("fetch-error", "page-missing"))]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
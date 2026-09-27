#!/usr/bin/env python3
"""S3 delta re-enum (owner PERMANENT RULE 2026-09-27 — plan §S3 addendum).

Instead of a FULL `allpages` re-enumeration, list only what changed since
the last archived enumeration via MediaWiki `recentchanges`, walking
backwards from now to `--rcend`. Edits are discarded client-side (they
don't change page existence or titles); `new`/`delete`/`move` rows are
the delta. The operator then reconstructs the gate-day accounting list
(base archived list + new − deleted + move destinations) and re-archives
it (old lists are kept, never overwritten).

Small egress: a handful of 500-row API pages (vs ~2,800 for a full
marvel re-enum; measured 2026-09-27: marvel 38 h window = 2 calls).
Same egress discipline as `revid_backfill.py`: chrome136 impersonation
+ campaign WAF-UA; a 429 or error STOPS CLEAN (receipt written, exit
42/1, NO blind retry) — rotate the egress per plan §1a and re-run (the
run is idempotent: same window, receipt overwritten on completion).

Fandom API specifics (probed 2026-09-27): rows are FLAT
(`type`/`title`/`timestamp`/`user`/`pageid`/`oldtitle`, no `rc*`
prefix), the `rctype` filter is IGNORED by their build (filter
client-side), and continuation uses the `rccontinue` key (a
`timestamp|rcid` pair).

Also: `--check-titles "A|B|C"` = direct liveness check of known
missing-live titles (one API call; reports live/missing/redirect +
pageid/revid) for the receipt.

Usage (venv python — system py3 lacks curl_cffi):
  scriptengine/.venv/bin/python tools/marvel/recentchanges_delta.py \
      --series marvel --rcend 2026-09-25T18:30:00Z
  scriptengine/.venv/bin/python tools/marvel/recentchanges_delta.py \
      --series mcu --rcend 2026-09-25T19:30:00Z \
      --check-titles "Elizabeth Tyne (Earth-33263)|Enok (Hyboria) (Earth-616)|Realm of Nothingness (Forbidden Dimension)" \
      --egress-note "FI #216 187.40.62.123"
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

WIKIS = {
    "marvel": "https://marvel.fandom.com",
    "mcu": "https://marvelcinematicuniverse.fandom.com",
}
# Campaign WAF-UA finding (2026-09-25): fetch-side campaign calls carry the
# chrome136 browser UA (see plan §1a + wall episode record). Duplicated from
# revid_backfill.py on purpose (verified-imported-by-nothing rule).
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)
# new/delete/move are the only recentchanges types that change the live
# title set (page existence / spelling); everything else is discarded.
INTERESTING = ("new", "delete", "move")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch_page(api: str, rcend: str, rcprop: str,
               rccontinue: str | None) -> tuple[str, dict | None]:
    """One recentchanges page (500 rows). Returns (kind, data): kind is
    'ok' | 'throttled-429' | 'api-error: ...' (data None on non-ok)."""
    from curl_cffi.requests import get

    p = {
        "action": "query", "list": "recentchanges", "rcnamespace": "0",
        "rcprop": rcprop, "rclimit": "500", "format": "json",
        "formatversion": "2", "rcend": rcend,
    }
    if rccontinue:
        p["rccontinue"] = rccontinue
    r = get(api, params=p, impersonate="chrome136", timeout=60,
            headers={"User-Agent": UA})
    if r.status_code == 429:
        return "throttled-429", None
    data = r.json()
    if "error" in data:
        return f"api-error: {json.dumps(data['error'])[:200]}", None
    return "ok", data


def walk_recentchanges(api: str, rcend: str, delay: float) -> dict:
    """Walk recentchanges (ns 0) from now back to rcend. Returns
    {'status', 'api_calls', 'type_counts', 'rows' (new/delete/move only),
    'window_first_ts', 'window_last_ts', 'rcprop_used', 'note'}.
    Stops clean on 429/error (no blind retry)."""
    rcprop = "title|timestamp|user|ids|oldtitle"
    rccontinue: str | None = None
    rows: list[dict] = []
    type_counts: dict[str, int] = {}
    api_calls = 0
    status = "complete"
    note = ""
    first_ts = last_ts = None
    while True:
        kind, data = fetch_page(api, rcend, rcprop, rccontinue)
        api_calls += 1
        if kind != "ok":
            if "Unrecognized value" in kind and "rcprop" in kind:
                rcprop = "title|timestamp|user"
                note = "rcprop fallback: ids/oldtitle not supported"
                continue  # retry the same page with the reduced rcprop
            status = "throttled-429" if kind == "throttled-429" else f"error: {kind}"
            note = kind
            break
        for rc in (data.get("query") or {}).get("recentchanges") or []:
            t = rc.get("type")
            type_counts[t] = type_counts.get(t, 0) + 1
            ts = rc.get("timestamp")
            if ts:
                first_ts = min(first_ts, ts) if first_ts else ts
                last_ts = max(last_ts, ts) if last_ts else ts
            if t in INTERESTING:
                rows.append({
                    "type": t, "title": rc.get("title"), "ts": ts,
                    "user": rc.get("user"), "pageid": rc.get("pageid"),
                    "oldtitle": rc.get("oldtitle"),
                })
        cont = data.get("continue") or {}
        # Fandom build: 'rccontinue' (ts|rcid); stock MediaWiki would use
        # 'query-continue' — honour whichever is present.
        nxt = cont.get("rccontinue") or cont.get("query-continue")
        if nxt:
            rccontinue = nxt
            if delay:
                time.sleep(delay)
            continue
        break
    return {
        "status": status, "api_calls": api_calls, "type_counts": type_counts,
        "rows": rows, "window_first_ts": last_ts, "window_last_ts": first_ts,
        "rcprop_used": rcprop, "note": note,
    }


def check_titles(api: str, titles: list[str]) -> dict:
    """Direct liveness check (one call): live / missing / redirect +
    pageid/revid. For the known missing-live receipt."""
    from curl_cffi.requests import get

    params = {
        "action": "query", "titles": "|".join(titles), "redirects": "1",
        "prop": "revisions", "rvprop": "ids", "format": "json",
        "formatversion": "2",
    }
    r = get(api, params=params, impersonate="chrome136", timeout=60,
            headers={"User-Agent": UA})
    if r.status_code == 429:
        return {"status": "throttled-429"}
    data = r.json()
    if "error" in data:
        return {"status": f"error: {json.dumps(data['error'])[:200]}"}
    pages = (data.get("query") or {}).get("pages") or {}
    # Fandom build quirk (probed 2026-09-27): query.pages arrives as a LIST
    # of page dicts, not the stock formatversion=2 {pageid: dict} mapping.
    page_list = list(pages.values()) if isinstance(pages, dict) else list(pages)
    out: dict[str, dict] = {}
    for t in titles:
        entry = next((p for p in page_list if p.get("title") == t), None)
        if entry is None:
            entry = next((p for p in page_list
                          if p.get("title", "").lower() == t.lower()), None)
        if entry is None:
            out[t] = {"status": "unknown"}
        elif entry.get("missing"):
            out[t] = {"status": "missing"}
        else:
            revid = (entry.get("revisions") or [{}])[0].get("revid")
            out[t] = {"status": "live", "pageid": entry.get("pageid"),
                      "revid": revid}
    return {"status": "complete", "pages": out}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", required=True, choices=sorted(WIKIS))
    ap.add_argument("--rcend", required=True,
                    help="oldest change to include (ISO UTC), i.e. the "
                         "timestamp of the last archived enumeration "
                         "(minus a safety margin)")
    ap.add_argument("--check-titles", default="",
                    help="pipe-separated titles for a direct liveness check")
    ap.add_argument("--egress-note", default="")
    ap.add_argument("--delay", type=float, default=0.8)
    ap.add_argument("--out", default="",
                    help="receipt JSON (default "
                         "reports/marvel/receipts/recentchanges_delta_<series>_<day>.json)")
    ap.add_argument("--new-titles-out", default="",
                    help="plain-lines file for fixlist_fetch (default "
                         "tools/marvel/recent_new_<series>_<day>.jsonl)")
    a = ap.parse_args()

    day = now_iso()[:10]
    out = Path(a.out) if a.out else (
        ROOT / "reports/marvel/receipts"
        / f"recentchanges_delta_{a.series}_{day}.json")
    new_out = Path(a.new_titles_out) if a.new_titles_out else (
        ROOT / f"tools/marvel/recent_new_{a.series}_{day}.jsonl")

    started = now_iso()
    api = f"{WIKIS[a.series]}/api.php"
    walk = walk_recentchanges(api, a.rcend, a.delay)

    # New pages: the fixlist for fixlist_fetch (deduped, sorted plain lines).
    new_titles = sorted({r["title"] for r in walk["rows"]
                         if r["type"] == "new" and r["title"]})
    new_out.parent.mkdir(parents=True, exist_ok=True)
    new_out.write_text("\n".join(new_titles) + ("\n" if new_titles else ""),
                       encoding="utf-8")

    check = None
    if a.check_titles:
        titles = [t for t in a.check_titles.split("|") if t.strip()]
        check = check_titles(api, titles)
        time.sleep(a.delay)

    receipt = {
        "tool": "tools/marvel/recentchanges_delta.py",
        "series": a.series, "wiki": WIKIS[a.series], "rcend": a.rcend,
        "started_utc": started, "finished_utc": now_iso(),
        "status": walk["status"] + (f"; titles-{check['status']}"
                                     if check else ""),
        "api_calls": walk["api_calls"] + (1 if a.check_titles else 0),
        "rcprop_used": walk.get("rcprop_used"),
        "note": walk.get("note", ""),
        "egress_note": a.egress_note,
        "type_counts": walk["type_counts"],
        "window_first_ts": walk["window_first_ts"],
        "window_last_ts": walk["window_last_ts"],
        "interesting_rows": walk["rows"],
        "new_titles_file": str(new_out.relative_to(ROOT)),
        "new_titles": new_titles,
        "check_titles": check,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    n_new = len([r for r in walk["rows"] if r["type"] == "new"])
    n_del = len([r for r in walk["rows"] if r["type"] == "delete"])
    n_mov = len([r for r in walk["rows"] if r["type"] == "move"])
    print(f"[recentchanges {a.series}] status={receipt['status']} "
          f"api_calls={receipt['api_calls']} new={n_new} delete={n_del} "
          f"move={n_mov} "
          f"window=[{walk['window_first_ts']} .. {walk['window_last_ts']}] "
          f"-> {out.relative_to(ROOT)}", flush=True)
    if walk["status"] != "complete":
        return 42 if "throttled" in walk["status"] else 1
    if check and check.get("status") != "complete":
        return 42 if "throttled" in check["status"] else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
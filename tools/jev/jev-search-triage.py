#!/usr/bin/env python3
"""Search-result triage: collapse N fetched results to the ones that matter, on the fast lane.

The slow part of a research pass is not the fetches — it is deciding which of the
50-200 fetched results matter before anything feeds the 27B. This does that
decision locally: decider-0.8b via the :8018 gateway fast lane, one plain
question per item. Measured separation on the decider: relevant >= 0.6,
noise <= 0.3, so the default keep threshold is 0.3.

Two modes:
  --query "..."           fetch + judge via the :8041 search-judge service
                          (5 keyless engines: duckduckgo/wikipedia/hackernews/
                          github/arxiv; start it with ~/tools/jev/bin/start-D-services.sh)
  --input results.jsonl   judge an existing result set (agent-reach output, or any
                          list / NDJSON of {title, snippet, url} objects), no fetching

Output: the ranked keep list on stdout (what the 27B reads); the full judged set
goes to --out (jsonl). Unjudged items (judge down) are kept and flagged.
Nothing here grades; it only sorts and filters.

    python jev-search-triage.py --query "chainsaw man falling devil abilities" --top 8
    agent-reach ... | python jev-search-triage.py --input - --query "..." --top 8
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

JEV_URL = os.environ.get("SCRIPTENGINE_JEV_URL", "http://127.0.0.1:8018/v1/systemone")
SEARCH_URL = os.environ.get("JEV_SEARCH_URL", "http://127.0.0.1:8041/api/ask")
QUESTION = "Is this search result relevant to the query?"


def _ask(state: dict) -> float:
    body = json.dumps({"model": "jev-latest", "state": state,
                       "questions": {"q": {"type": "noul", "instructions": QUESTION}}}).encode()
    req = urllib.request.Request(JEV_URL, data=body, headers={
        "Content-Type": "application/json", "Authorization": "Bearer local"})
    with urllib.request.urlopen(req, timeout=120) as r:
        p = json.loads(r.read())["answers"]["q"]["noul"]
    return p if isinstance(p, float) else 0.0


def _item_fields(d: dict) -> tuple[str, str, str]:
    title = str(d.get("title") or d.get("name") or "")
    snippet = str(d.get("snippet") or d.get("text") or d.get("summary") or "")
    url = str(d.get("url") or d.get("link") or d.get("href") or "")
    return title, snippet, url


def fetch_via_search_service(query: str, sources=None, window=None) -> list[dict]:
    """POST :8041 /api/ask (NDJSON stream); collect every judged item."""
    payload = {"q": query}
    if sources:
        payload["s"] = sources
    if window:
        payload["w"] = window
    req = urllib.request.Request(SEARCH_URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    items: list[dict] = []
    with urllib.request.urlopen(req, timeout=180) as r:
        for line in r:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "lane":
                for it in ev.get("items", []):
                    it["engine"] = ev.get("source")
                    items.append(it)
            elif ev.get("type") == "error":
                print(f"warning: {ev.get('error')}", file=sys.stderr)
    if not items:
        print("no results (engine down or bot-challenged on every engine)", file=sys.stderr)
    return items


def judge_set(items: list[dict], query: str, workers: int) -> list[dict]:
    """Judge items that lack a relevance score, one plain question each (fast lane)."""
    todo = [it for it in items if not (it.get("ranked") and isinstance(it.get("relevance"), (int, float)))]
    if not todo:
        return items

    def one(it: dict) -> dict:
        title, snippet, url = _item_fields(it)
        try:
            it["relevance"] = round(_ask({"query": query, "title": title,
                                          "snippet": snippet[:400], "url": url}), 4)
            it["ranked"] = True
        except Exception as e:  # judge down: keep the item, flag it (fail-open)
            it["relevance"] = 0.0
            it["ranked"] = False
            it["judge_error"] = str(e)[:120]
        return it

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for it in pool.map(one, todo):
            pass
    return items


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--query", help="the query results are judged against (required unless each input item carries one)")
    ap.add_argument("--input", help="results jsonl/json (or '-' for stdin); judged without fetching")
    ap.add_argument("--sources", help="comma-separated engines for --query mode (default: judge-picked)")
    ap.add_argument("--window", choices=["any", "24h", "7d", "30d"], help="time window for --query mode")
    ap.add_argument("--threshold", type=float, default=0.3)
    ap.add_argument("--top", type=int, default=10, help="how many keep-list entries to print")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", help="write the full judged set to this jsonl")
    args = ap.parse_args(argv)

    if args.input:
        raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
        raw = raw.strip()
        try:
            data = json.loads(raw)  # a JSON array
            items = data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            items = [json.loads(l) for l in raw.splitlines() if l.strip()]  # NDJSON
        query = args.query or next((str(d.get("query") or "") for d in items if d.get("query")), "")
        if not query:
            print("need --query (or a 'query' field on the input items)", file=sys.stderr)
            return 2
        items = judge_set(items, query, args.workers)
    else:
        if not args.query:
            print("need --query (fetch mode) or --input (judge-an-existing-set mode)", file=sys.stderr)
            return 2
        items = fetch_via_search_service(args.query,
                                         args.sources.split(",") if args.sources else None, args.window)
        # the :8041 service already judged via the fast lane; nothing to do

    for it in items:
        p = it.get("relevance")
        it["keep"] = (p is None) or p >= args.threshold  # unjudged -> keep (fail-open)
    items.sort(key=lambda it: (-(it.get("relevance") or 0), it.get("engine") or ""))
    kept = [it for it in items if it["keep"]]

    print(f"# query: {args.query or '(per-item)'}\n# judged {len(items)} results; "
          f"{len(kept)} keep (p >= {args.threshold} or unjudged); top {args.top} shown\n")
    for i, it in enumerate(kept[: args.top], 1):
        p = it.get("relevance")
        flag = " [UNJUDGED]" if not it.get("ranked") else ""
        print(f"{i}. (p={p if p is not None else 'n/a'}{flag}) {it.get('title') or ''}")
        print(f"   {it.get('url', '')}")
        snip = str(it.get("snippet") or "")[:160]
        if snip:
            print(f"   {snip}")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        print(f"\nfull judged set -> {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
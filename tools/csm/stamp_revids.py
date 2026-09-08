#!/usr/bin/env python3
"""Stamp the CSM seed bank with current wiki revision ids (plan §5.2, re-scoped).

CSM-1 of the CSM 100% campaign (council ruling: "pin the gold bank" means
stamp revid at authoring time — the bank is inventoried and stamped, zero new
questions). CSM-specific by the standing rule: it touches only
questions/csm.json + questions/_csm_relations.json, never JJK tooling.

What it does:
  - collect every distinct wiki source title across both files
  - fetch each page's current revid + timestamp from the Fandom API
  - write a top-level `revids` map into each file, plus per-question
    `source_revid` (the revid of the question's first wiki source) and
    `revid_fetched` date; non-wiki sources (e.g. cbr.com) are left
    unpinned and reported
  - re-running is idempotent: it refreshes the stamp and reports which
    pages moved since the last stamp (drift = a page's wiki content changed
    under the bank, so its questions need re-verification)

Run:  scriptengine/.venv/bin/python tools/csm/stamp_revids.py [--dry-run]
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
FILES = [
    REPO / "questions/csm.json",
    REPO / "questions/_csm_relations.json",
]
API = "https://chainsaw-man.fandom.com/api.php"
WIKI_HOST = "chainsaw-man.fandom.com"


def wiki_titles(sources):
    """Distinct wiki titles from a source-URL list (non-wiki URLs are dropped)."""
    out = []
    for url in sources or []:
        m = re.search(r"/wiki/([^?#]+)$", url)
        if m and WIKI_HOST in url:
            t = urllib.parse.unquote(m.group(1)).replace("_", " ")
            if t not in out:
                out.append(t)
    return out


def fetch_revids(titles):
    """Current revid + timestamp per title, batched 50/request. Returns
    {title: {revid, timestamp, redirects: [...]} or {error: msg}}."""
    result = {}
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "prop": "revisions",
            "rvprop": "ids|timestamp", "redirects": "1",
            "titles": "|".join(batch), "limit": str(len(batch)),
        })
        with urllib.request.urlopen(f"{API}?{q}", timeout=30) as r:
            data = json.load(r)
        pages = data.get("query", {}).get("pages", {})
        redir = {p["from"]: p["to"] for p in data.get("query", {}).get("normalized", []) or []}
        for p in pages.values():
            rev = (p.get("revisions") or [{}])[0]
            title = p["title"]
            if p.get("missing"):
                result[title] = {"error": "page does not exist"}
            else:
                result[title] = {"revid": rev.get("revid"),
                                 "timestamp": rev.get("timestamp"),
                                 "redirects": [redir[t] for t in redir if p.get("redirected") and t in redir]}
        # any title that was neither in pages nor normalized = not found
        seen = {p["title"] for p in pages.values()} | set(redir.values())
        for t in batch:
            key = t
            while key in redir:
                key = redir[key]
            if key not in seen and t not in result:
                result[t] = {"error": "no page found"}
    return result


def indent_of(path):
    text = path.read_text()
    m = re.match(r"^\{\n ?+", text)
    return len(m.group(0)) - 1 if m else 2


def stamp_file(path, fetched):
    data = json.loads(path.read_text())
    prev = data.get("revids") or {}
    all_titles = []
    for q in data.get("questions", []) + data.get("retired", []):
        for t in wiki_titles(q.get("sources")):
            if t not in all_titles:
                all_titles.append(t)
    unpinned = []
    for q in data.get("questions", []) + data.get("retired", []):
        for url in q.get("sources", []):
            if WIKI_HOST not in url:
                unpinned.append((q.get("id", q.get("question", "?")), url))
    return data, all_titles, prev, unpinned


def main():
    dry = "--dry-run" in sys.argv
    fetched = str(date.today())
    titles, prev_maps, unpinned = [], {}, []
    for f in FILES:
        data, t, prev, up = stamp_file(f, fetched)
        titles.extend(t)
        prev_maps[f] = (prev, data)
        unpinned.extend(up)
    titles = sorted(set(titles))
    print(f"{len(titles)} distinct wiki source pages across {len(FILES)} files")
    revids = fetch_revids(titles)
    for t in titles:
        info = revids.get(t, {"error": "fetch failed"})
        print(f"  {t:35s} -> {info.get('revid', info.get('error'))}"
              + (f" (moved from {prev_maps[FILES[0]][0].get(t, {}).get('revid')})"
                 if t in prev_maps[FILES[0]][0] and prev_maps[FILES[0]][0][t].get("revid") != info.get("revid") else ""))
    for f in FILES:
        data, prev = prev_maps[f]
        new_map = {}
        for t in titles:
            info = revids.get(t)
            if info and "revid" in info:
                new_map[t] = info
        for q in data.get("questions", []) + data.get("retired", []):
            wt = wiki_titles(q.get("sources"))
            first = new_map.get(wt[0]) if wt else None
            q["source_revid"] = first["revid"] if first else None
            q["revid_fetched"] = fetched
        data["revids"] = new_map
        data["revid_stamp"] = {"fetched": fetched, "api": API,
                               "note": "current revid of each source page at fetch time; "
                                       "a re-run reports pages that moved (drift = re-verify)"}
        if not dry:
            ind = indent_of(f)
            f.write_text(json.dumps(data, indent=ind, ensure_ascii=False) + "\n")
        print(f"{'would write' if dry else 'wrote'} {f.relative_to(REPO)}: "
              f"{len(new_map)} pinned, {len(titles) - len(new_map)} unpinnable, "
              f"{len(data.get('questions', [])) + len(data.get('retired', []))} questions stamped")
    if unpinned:
        print("non-wiki sources (no revid, left unpinned):")
        for qid, url in sorted(set(unpinned)):
            print(f"  {qid}: {url}")
    if dry:
        print("dry run — nothing written")


if __name__ == "__main__":
    main()
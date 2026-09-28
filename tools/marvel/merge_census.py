#!/usr/bin/env python
"""P2b merge census (architect 2026-09-28): what does the index-time alias
merge change in each series' graph?

Read-only: loads the corpus exactly the way `index` does (load_extracted
with the current overrides, the same dropped-work filter the build applies
before the graph phase) and replays the `_load_graph` resolver without
touching a store. Per series it reports:

- names_merged         bare names the resolver points at one page's node
                       (page titles excluded: they already have their node)
- edges_repointed      edges whose target is one of those names; the old
                       build forked a stub node on first occurrence, the
                       new build links the surviving page's node
- chunk_links_repointed  chunk entity occurrences with one of those names;
                       the old build linked the stub (or nothing), the new
                       build links the page's node
- old_stub_targets     distinct bare targets the old build would have
                       forked as stub nodes, for context
- stubs_absorbed       of those, how many the merge absorbs into a page node
- examples             the merged names with the most edges, and where they
                       resolve

Usage: scriptengine/.venv/bin/python tools/marvel/merge_census.py <series>...

Flags:
  --force-merge  pass `alias_merge: true` on top of the series' real
                 overrides, i.e. replay the pre-gate (ungated) heuristic
                 under the gated engine. Cross-checks the pre-gate numbers.
  --post-gate    (default) replay with the series' real overrides: inferred
                 merges only where `alias_merge` is declared; `alias_map`
                 pins always apply.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter

import os
import sys

# Repo-root bootstrap: running this file by path puts its own directory
# on sys.path, not the repo root, so `import scriptengine` would fail.
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scriptengine.config import load_overrides, series_paths
from scriptengine.index.build import (
    _build_alias_resolver,
    _harvest_link_aliases,
)
from scriptengine.index.chunker import (
    chunk_page,
    effective_boilerplate_sections,
)
from scriptengine.ingest.canon import discounted_works, page_is_discounted
from scriptengine.ingest.crawler import load_extracted


def census(series: str, force_merge: bool = False) -> dict:
    paths = series_paths(series)
    overrides = load_overrides(paths)
    pages, _ = load_extracted(paths, overrides)
    resolver_overrides = overrides
    if force_merge:
        resolver_overrides = {**overrides, "alias_merge": True}

    # The same dropped-work filter the build applies before the graph phase.
    works = discounted_works(overrides)
    if works:
        categories_by_title = {p.title.lower(): p.categories for p in pages}
        dropped = {
            p.title
            for p in pages
            if page_is_discounted(p, works, categories_by_title)
        }
        pages = [
            p for p in pages
            if p.title not in dropped and p.title.split("/", 1)[0] not in dropped
        ]
    else:
        dropped = set()

    node_ids = {p.title: i for i, p in enumerate(pages)}
    usage = _harvest_link_aliases(pages)
    resolver = _build_alias_resolver(pages, usage, resolver_overrides, node_ids)
    titles_lower = {t.lower() for t in node_ids}
    merged = {n: resolver[n] for n in resolver if n not in titles_lower}
    by_id = {i: t for t, i in node_ids.items()}

    edge_hits: Counter = Counter()
    old_stubs: set[str] = set()
    for p in pages:
        for e in p.edges:
            if e.target in dropped:
                continue
            if e.target not in node_ids:
                old_stubs.add(e.target)
            key = e.target.strip().lower()
            if key in merged:
                edge_hits[key] += 1

    chunk_hits: Counter = Counter()
    boilerplate = effective_boilerplate_sections(overrides)
    for p in pages:
        for chunk in chunk_page(p, boilerplate=boilerplate):
            for ent in chunk.entities:
                key = ent.strip().lower()
                if key in merged:
                    chunk_hits[key] += 1

    examples = [
        {
            "name": name,
            "resolves_to": by_id[merged[name]],
            "edges": edge_hits.get(name, 0),
            "chunk_links": chunk_hits.get(name, 0),
        }
        for name in sorted(merged, key=lambda n: (-edge_hits.get(n, 0), n))[:5]
    ]

    return {
        "series": series,
        "pages": len(pages),
        "dropped_pages": len(dropped),
        "names_merged": sorted(merged),
        "edges_repointed": sum(edge_hits.values()),
        "chunk_links_repointed": sum(chunk_hits.values()),
        "old_stub_targets": len(old_stubs),
        "stubs_absorbed": len(
            {t for t in old_stubs if t.strip().lower() in merged}
        ),
        "examples": examples,
    }


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--force-merge"]
    force_merge = "--force-merge" in sys.argv
    for series in args:
        t0 = time.time()
        result = census(series, force_merge=force_merge)
        result["seconds"] = round(time.time() - t0, 1)
        result["mode"] = "force-merge (pre-gate replay)" if force_merge else "post-gate (real overrides)"
        print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
"""Resolve the wiki's curated list templates into the stored corpus.

The crawler never fetches the Template: namespace, so a page whose entire
"list" section is a bare transclusion -- `{{Ten Shadows Shikigami}}` -- is
stored as 28 characters with no links. The wiki's canonical curated lists live
in exactly those transclusions, invisible to every downstream reader. This
module resolves a declared allowlist of list templates via the MediaWiki
`expandtemplates` action and splices the expanded wikitext into the page's
stored `wikitext`, so the next `index` parses the real list.

Idempotent by construction: once a page's transclusion has been replaced, the
bare `{{Name}}` is gone from its wikitext and a re-run finds nothing to do.
`refresh` after a re-crawl restores the raw wikitext, at which point the
transclusions are found again and re-resolved, against the cache where it has
an entry.

The allowlist lives in `series/<name>/overrides.yaml` under `template_lists:`,
the only place a series-specific decision may live.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings, load_overrides
from scriptengine.ingest.crawler import WikiCrawler, api_base, load_manifest
from scriptengine.ingest.wikitext import find_templates, parse_template

CACHE_NAME = "template_cache.json"


def declared_lists(overrides: dict[str, Any] | None) -> tuple[str, ...]:
    """Template names this wiki wants resolved, in declaration order."""
    raw = (overrides or {}).get("template_lists") or ()
    return tuple(str(name).strip() for name in raw if str(name).strip())


def find_unresolved(
    wikitext: str, declared: tuple[str, ...]
) -> list[tuple[str, int, int]]:
    """`(template_name, start, end)` for each declared top-level transclusion.

    `find_templates` yields only outermost `{{...}}`. A transclusion that has
    already been resolved is no longer a bare `{{Name}}` in the text, which is
    what makes a re-run skip it for free. The `Template:` namespace prefix is
    stripped so a `{{Template:X}}` call matches `X` like the bare call does.
    """
    wanted = {name.lower() for name in declared}
    found: list[tuple[str, int, int]] = []
    for start, end, body in find_templates(wikitext):
        name = parse_template(body)[0].split(":")[-1].strip()
        if name.lower() in wanted:
            found.append((name, start, end))
    return found


def splice(wikitext: str, expansions: dict[str, str]) -> str:
    """Replace every declared transclusion with its expansion.

    Expansions key on template name, matched case-insensitively, and the
    *lookup* is folded too. MediaWiki capitalises a template's first letter for
    you, so `{{ten shadows shikigami}}` and `{{Ten Shadows Shikigami}}` are one
    template and a wiki's editors write both. Matching case-insensitively while
    looking up case-sensitively raised `KeyError` on the first page that
    disagreed with the declaration's spelling.

    Spans are spliced last-to-first so earlier offsets stay valid as the text
    grows.
    """
    folded = {name.lower(): text for name, text in expansions.items()}
    spans: list[tuple[int, int, str]] = []
    for start, end, body in find_templates(wikitext):
        name = parse_template(body)[0].split(":")[-1].strip().lower()
        if name in folded:
            spans.append((start, end, name))
    out = wikitext
    for start, end, name in sorted(spans, key=lambda span: span[1], reverse=True):
        out = out[:start] + folded[name] + out[end:]
    return out


class TemplateCache:
    """The expanded wikitext for each template, keyed by template name."""

    def __init__(self, entries: dict[str, dict[str, str]] | None = None) -> None:
        self.entries = entries or {}

    @classmethod
    def load(cls, path: Path) -> "TemplateCache":
        if not path.exists():
            return cls()
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError, ValueError):
            return cls()
        return cls(loaded if isinstance(loaded, dict) else {})

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps(self.entries, ensure_ascii=False, indent=2), encoding="utf-8"
        )


async def _expansions(
    crawler: WikiCrawler,
    base: str,
    names: set[str],
    cache: TemplateCache,
    refresh: bool,
) -> tuple[dict[str, str], int]:
    """`{template_name: expanded_wikitext}` for the names that need fetching."""
    expansions: dict[str, str] = {}
    fetched = 0
    for name in sorted(names):
        if not refresh and name in cache.entries:
            expansions[name] = cache.entries[name]["wikitext"]
            continue
        expanded = await crawler.expand_templates(base, f"{{{{{name}}}}}")
        if not expanded:
            continue
        fetched += 1
        expansions[name] = expanded
        cache.entries[name] = {
            "wikitext": expanded,
            "resolved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    return expansions, fetched


async def resolve_series(
    paths: SeriesPaths,
    overrides: dict[str, Any] | None = None,
    settings: Settings | None = None,
    *,
    refresh: bool = False,
) -> dict[str, Any]:
    """Splice every declared transclusion's expansion into the stored wikitext.

    Returns a report rather than raising: a wiki with nothing declared, or a
    corpus with nothing unresolved, are both legitimate states of the world.
    """
    settings = settings or get_settings()
    overrides = overrides if overrides is not None else load_overrides(paths)
    declared = declared_lists(overrides)
    if not declared:
        return {"status": "no_template_lists", "templates": 0, "pages_updated": 0}

    manifest = load_manifest(paths)
    wiki_url = manifest.get("wiki", "")
    if not wiki_url:
        return {"status": "no_manifest", "templates": 0, "pages_updated": 0}
    base = api_base(wiki_url)

    cache = TemplateCache.load(paths.root / CACHE_NAME)
    pages_with_unresolved = 0
    pages_updated = 0
    templates_fetched = 0

    async with WikiCrawler(settings) as crawler:
        for page_path in sorted(paths.wikitext.glob("*.json")):
            try:
                data = json.loads(page_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            wikitext = data.get("wikitext", "")
            spans = find_unresolved(wikitext, declared)
            if not spans:
                continue
            pages_with_unresolved += 1

            names = {name for name, _, _ in spans}
            expansions, fetched = await _expansions(
                crawler, base, names, cache, refresh
            )
            templates_fetched += fetched
            if not expansions:
                continue

            data["wikitext"] = splice(wikitext, expansions)
            page_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            pages_updated += 1

    cache.save(paths.root / CACHE_NAME)
    return {
        "status": "ok",
        "templates_declared": len(declared),
        "templates_fetched": templates_fetched,
        "pages_with_unresolved": pages_with_unresolved,
        "pages_updated": pages_updated,
    }

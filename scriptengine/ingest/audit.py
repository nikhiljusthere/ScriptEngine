"""Auditing what extraction actually understood.

A broken extractor is silent. The previous pipeline's section detector never
matched a single heading — it looked for a bare ``appearance`` while the corpus
contained ``## Appearance`` — and reported no error at all. Every document
collapsed into one unnamed section, and the pipeline carried on to embedding.

This module exists so that failure mode cannot repeat unnoticed. Run it before
indexing; the numbers are cheap to produce and expensive to skip.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any

from scriptengine.config import SeriesPaths, load_overrides
from scriptengine.ingest.crawler import load_extracted, load_manifest
from scriptengine.ingest.documents import WikiPage

# Thresholds worth failing over. Documented in docs/EXTRACTION_AUDIT.md.
MIN_TYPED_RATIO = 0.90
MIN_SECTIONS_PER_PAGE = 1.5      # at or below 1, section splitting has failed
MIN_RESOLVED_EDGE_RATIO = 0.70


def audit_series(paths: SeriesPaths, sample: int = 0) -> dict[str, Any]:
    """Measure extraction quality for a crawled series."""
    # Re-extracted the same way `index` does. Auditing the extraction stored at
    # crawl time while indexing a freshly parsed one would make this a report on
    # history rather than on what is about to be indexed.
    pages, ontology = load_extracted(paths, load_overrides(paths))
    if sample:
        pages = pages[:sample]

    if not pages:
        return {"series": paths.name, "error": "no pages found; run `crawl` first"}

    manifest = load_manifest(paths)

    # Resolve wikilinks against every title on the wiki, not just the pages that
    # happen to be on disk. A capped crawl links heavily to articles it has not
    # reached yet; counting those as dangling measures the sample size rather
    # than the extraction, and buries the genuinely broken links.
    known_titles = set(manifest.get("all_titles") or ())
    partial = bool(known_titles) and len(known_titles) > len(pages)

    known_titles.update(page.title for page in pages)
    for page in pages:
        known_titles.update(page.redirects)
        known_titles.update(page.aliases)

    types = Counter(page.page_type for page in pages)
    typed = sum(count for kind, count in types.items() if kind != "unknown")

    with_infobox = sum(1 for page in pages if page.facts)
    total_sections = sum(len(page.sections) for page in pages)
    total_facts = sum(len(page.facts) for page in pages)
    total_citations = sum(
        len(page.citations) + sum(len(f.citations) for f in page.facts) for page in pages
    )

    edges = [edge for page in pages for edge in page.edges]
    resolved = sum(1 for edge in edges if edge.target in known_titles)

    empty_pages = [page.title for page in pages if not page.word_count]
    no_sections = [page.title for page in pages if not page.sections]

    warnings = [
        {"page": page.title, "issue": issue}
        for page in pages
        for issue in page.warnings
    ]

    report: dict[str, Any] = {
        "series": paths.name,
        "sampled": len(pages),
        "types": dict(types.most_common()),
        "coverage": {
            "typed": round(typed / len(pages), 3),
            "with_infobox": round(with_infobox / len(pages), 3),
            "mean_sections": round(total_sections / len(pages), 2),
            "mean_facts": round(total_facts / len(pages), 2),
            "mean_words": round(sum(p.word_count for p in pages) / len(pages)),
            "citations": total_citations,
        },
        "graph": {
            "edges": len(edges),
            "resolved": round(resolved / len(edges), 3) if edges else 0.0,
            "dangling": len(edges) - resolved,
            "resolved_against": "whole wiki" if partial else "crawled pages",
            "relations": dict(Counter(e.relation for e in edges).most_common(12)),
            "top_dangling": [
                {"target": target, "count": count}
                for target, count in Counter(
                    edge.target for edge in edges if edge.target not in known_titles
                ).most_common(10)
            ],
        },
        "problems": {
            "pages_without_prose": empty_pages[:25],
            "pages_without_sections": no_sections[:25],
        },
        "warnings": warnings[:50],
        "checks": [],
    }

    report["checks"] = _run_checks(report, capped=bool(manifest.get("enumeration_capped")))
    report["passed"] = all(check["passed"] for check in report["checks"])

    # What discovery saw, including what it rejected: a template with many
    # votes that did not become a type is the first place to look when pages
    # come back untyped.
    report["infobox_votes"] = dict(list(ontology.infobox_votes.items())[:15])
    report["vocabulary"] = sorted(ontology.types)

    if manifest:
        report["crawl"] = {
            "wiki": manifest.get("wiki"),
            "crawled_at": manifest.get("crawled_at"),
            "pages_written": manifest.get("pages_written"),
            "pages_skipped": manifest.get("pages_skipped"),
            "pages_failed": manifest.get("pages_failed"),
            "discovered_types": sorted(
                set((manifest.get("ontology") or {}).get("infobox_types", {}).values())
            ),
        }

    return report


def _run_checks(report: dict[str, Any], capped: bool = False) -> list[dict[str, Any]]:
    """Turn the raw numbers into pass/fail verdicts with an explanation."""
    coverage = report["coverage"]
    graph = report["graph"]

    checks = [
        {
            "name": "pages typed",
            "value": coverage["typed"],
            "threshold": MIN_TYPED_RATIO,
            "passed": coverage["typed"] >= MIN_TYPED_RATIO,
            "meaning": "the infobox vocabulary is missing templates this wiki uses",
        },
        {
            "name": "sections per page",
            "value": coverage["mean_sections"],
            "threshold": MIN_SECTIONS_PER_PAGE,
            "passed": coverage["mean_sections"] >= MIN_SECTIONS_PER_PAGE,
            "meaning": "section splitting has failed; nothing downstream is trustworthy",
        },
        {
            "name": "edges resolved",
            "value": graph["resolved"],
            "threshold": MIN_RESOLVED_EDGE_RATIO,
            "passed": graph["resolved"] >= MIN_RESOLVED_EDGE_RATIO,
            "meaning": "wikilink targets are not matching crawled titles; check redirects",
        },
    ]

    if capped:
        # On a --max-pages run most of the wiki was never enumerated, so links
        # into it are unresolvable by construction. Failing here would measure
        # the sample size and drown the checks that do mean something.
        for check in checks:
            if check["name"] == "edges resolved":
                check["passed"] = True
                check["skipped"] = True
                check["meaning"] = (
                    "not checked: the crawl was capped with --max-pages, so most "
                    "link targets were never enumerated"
                )

    return checks


def write_report(paths: SeriesPaths, report: dict[str, Any]) -> str:
    paths.audit.mkdir(parents=True, exist_ok=True)
    destination = paths.audit / "report.json"
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return str(destination)


def compare_page(page: WikiPage) -> dict[str, Any]:
    """A single page's extraction, for eyeballing one result in detail."""
    return {
        "title": page.title,
        "type": page.page_type,
        "infobox": page.infobox_template,
        "facts": {f.key: f.value for f in page.facts},
        "sections": [
            {"breadcrumb": s.breadcrumb, "level": s.level, "words": s.word_count}
            for s in page.sections
        ],
        "edges": len(page.edges),
        "citations": len(page.citations),
        "warnings": page.warnings,
    }

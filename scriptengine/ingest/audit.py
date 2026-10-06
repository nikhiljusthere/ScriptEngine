"""Auditing what extraction actually understood.

A broken extractor is silent. The previous pipeline's section detector never
matched a single heading. It looked for a bare ``appearance`` while the corpus
contained ``## Appearance``, and reported no error at all. Every document
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

# Share of prose sentences that must resolve to a chapter on a wiki that cites
# at all. Deliberately low: reference lists, episode tables and trivia sections
# carry no citations and never will. It exists to catch the failure this project
# has already had once: citations captured as structured objects and then
# dropped from every downstream text, so the scripts had nothing to cite.
MIN_SOURCED_SENTENCE_RATIO = 0.25

# Share of citation parameters the extractor must account for. Not 100%: wikis
# carry one-off parameters nobody can identify, and inventing a meaning for one
# is worse than ignoring it.
MIN_UNDERSTOOD_PARAM_RATIO = 0.99


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
    known_titles: set[str] = set(manifest.get("all_titles") or ())
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
    sourcing = _citation_coverage(pages, edges, load_overrides(paths))
    sourcing["unknown_qualifiers"] = _unknown_qualifiers(pages, ontology)
    sourcing["refs_with_locator"] = _refs_with_locator(pages, ontology)

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
        # What a script can actually cite. A citation that never reaches the
        # prose is a citation the writer cannot use.
        "sourcing": sourcing,
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


def _citation_coverage(pages: list[WikiPage], edges: list[Any], overrides: dict | None = None) -> dict[str, Any]:
    """How much of the prose a script could put a chapter and episode on.

    Measured the way the context builder measures it, through
    `retrieve/citations.py`: a reference covers the sentences before it, and a
    chapter resolves to its episode through the wiki's own adaptation edges. So
    this number is the one the writer will actually see, not a count of
    reference templates that may or may not have survived extraction.
    """
    from scriptengine.retrieve.citations import EpisodeIndex, coverage, declared_episode_map

    spec = (overrides or {}).get("episode_map")
    mapping: dict[str, str] = {}
    if spec:
        # the wiki's declared adaptation relations and number keys (see
        # citations.declared_episode_map); the default below is JJK's shape
        by_title = {page.title: page for page in pages}
        mapping = declared_episode_map(
            spec,
            ((e.source, e.relation, e.target) for e in edges),
            lambda name: {f.key: f.value for f in getattr(by_title.get(name), "facts", [])},
            lambda name: getattr(by_title.get(name), "page_type", ""),
        )
    for edge in edges if not spec else ():
        if edge.relation == "anime episode":
            chapter, episode = edge.source, edge.target
        elif edge.relation == "adapted from":
            chapter, episode = edge.target, edge.source
        else:
            continue
        chapter = _instalment(chapter, "Chapter")
        episode = _instalment(episode, "Episode")
        if chapter and episode:
            mapping.setdefault(chapter, episode)

    index = EpisodeIndex(mapping)
    totals = {"sentences": 0, "with_chapter": 0, "with_episode": 0, "cited_directly": 0}
    for page in pages:
        for section in page.sections:
            for key, value in coverage(section.text, index).items():
                totals[key] += value

    sentences = totals["sentences"] or 1
    return {
        "sentences": totals["sentences"],
        "chapter_episode_map": len(mapping),
        "with_chapter": round(totals["with_chapter"] / sentences, 3),
        "with_episode": round(totals["with_episode"] / sentences, 3),
        "cited_directly": round(totals["cited_directly"] / sentences, 3),
    }


def _unknown_qualifiers(pages: list[WikiPage], ontology: Any) -> dict[str, dict[str, int] | int]:
    """Reference parameters the extractor does not know what to do with.

    This is the audit that would have caught the Modulo bug on day one. The wiki
    wrote ``{{Ref|modulo=y|chap=16}}``; the extractor understood `chap`, ignored
    `modulo`, and rendered "(Chapter 16)", indistinguishable from the main
    series' Chapter 16, on 427 references. Nothing failed, and the wrong chapter
    number was available to every script.

    A parameter that is neither a locator, nor a page number, nor a configured
    work qualifier is a statement about the citation that is being dropped. It
    might be harmless. It might be renumbering the whole manga.
    """
    from scriptengine.ingest.wikitext import (
        EXTERNAL_PARAMS,
        LOCATOR_PARAMS,
        _normalise_param,
        is_page_param,
    )

    works = getattr(ontology, "citation_works", None)
    known = {
        _normalise_param(k)
        for k in LOCATOR_PARAMS | EXTERNAL_PARAMS | (works.known_params if works else set())
    }

    counts: Counter = Counter()
    total = 0
    for page in pages:
        citations = [
            *page.citations,
            *(citation for section in page.sections for citation in section.citations),
            *(citation for fact in page.facts for citation in fact.citations),
        ]
        for citation in citations:
            for key in citation.params:
                total += 1
                if (
                    key.startswith("_")
                    or _normalise_param(key) in known
                    or is_page_param(key)
                ):
                    continue
                counts[key] += 1
    return {"params": dict(counts.most_common(10)), "total": total}


def _refs_with_locator(pages: list[WikiPage], ontology: Any) -> int:
    """How many of this wiki's references name an instalment at all.

    The difference between a bug and a fact about the wiki. Berserk carries 36
    citations across 491 pages and almost every one of them points at cover art,
    a calendar or an interview, so 0% sourced prose there is the wiki's own
    habit, not a locator this project failed to read. Bleach and Hunterpedia cite
    a chapter on nearly every sentence, so 0% there would mean something broke.
    """
    from scriptengine.ingest.wikitext import _citation_marker

    grammar = getattr(ontology, "citation_works", None)
    found = 0
    for page in pages:
        for citation in page.citations:
            if _citation_marker(citation.params, grammar):
                found += 1
    return found


def _instalment(title: str, kind: str) -> str:
    prefix = f"{kind} "
    return title[len(prefix):].strip() if title.startswith(prefix) else ""


def _run_checks(report: dict[str, Any], capped: bool = False) -> list[dict[str, Any]]:
    """Turn the raw numbers into pass/fail verdicts with an explanation."""
    coverage = report["coverage"]
    graph = report["graph"]
    sourcing = report["sourcing"]

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
        {
            "name": "prose sentences sourced",
            "value": sourcing["with_chapter"],
            "threshold": MIN_SOURCED_SENTENCE_RATIO,
            "passed": sourcing["with_chapter"] >= MIN_SOURCED_SENTENCE_RATIO,
            "meaning": (
                "the wiki cites its prose but the locators are not reaching it, "
                "so scripts cannot tag a line with its chapter and episode"
            ),
        },
    ]

    # Measured as a share rather than a count. A parameter this wiki reaches for
    # constantly and the extractor ignores is the signal: `modulo` was 916 of
    # Jujutsu Kaisen's references, renumbering a whole sequel. Two stray uses of
    # something nobody can identify is not worth failing a corpus over, and
    # guessing what they mean is how a wrong chapter reaches a script.
    unknown = (sourcing.get("unknown_qualifiers") or {}).get("params") or {}
    total = max((sourcing.get("unknown_qualifiers") or {}).get("total", 0), 1)
    share = sum(unknown.values()) / total
    checks.append(
        {
            "name": "citation parameters understood",
            "value": round(1 - share, 3),
            "threshold": MIN_UNDERSTOOD_PARAM_RATIO,
            "passed": share <= 1 - MIN_UNDERSTOOD_PARAM_RATIO,
            "meaning": (
                "these reference parameters are dropped: "
                + ", ".join(f"{key} ({count})" for key, count in unknown.items())
                + ". If one names a sequel or a spin-off, its chapters are being "
                "cited as if they belonged to the main series. Map it in "
                "series/<name>/overrides.yaml under citation_params."
            ),
        }
    )

    if not coverage["citations"]:
        # A wiki that cites nothing cannot fail a citation check.
        for check in checks:
            if check["name"] in {"prose sentences sourced", "citation parameters understood"}:
                check["passed"] = True
                check["skipped"] = True
                check["meaning"] = "not checked: this wiki carries no citation templates"
    elif not (
        sourcing.get("refs_with_locator")
        or sourcing.get("with_chapter")
        or sourcing.get("with_episode")
    ):
        # It cites, but never with a chapter or an episode. Berserk cites cover
        # art and interviews. Failing here would report the wiki's habits as
        # this project's bug, and the number that matters is already visible.
        #
        # The measured coverage is part of the test on purpose: `<ref>` tags are
        # not template citations, so a wiki that sources everything through them
        # has `refs_with_locator == 0` and 84% of its prose sourced.
        for check in checks:
            if check["name"] == "prose sentences sourced":
                check["passed"] = True
                check["skipped"] = True
                check["meaning"] = (
                    "not checked: none of this wiki's references name a chapter "
                    "or an episode, so its scripts cannot carry instalment tags"
                )

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

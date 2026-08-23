"""page-gen: the deterministic structured half of a page-campaign batch."""
import json

import pytest

from scriptengine.config import SeriesPaths
from scriptengine.ingest.crawler import parse_page


def _crawl_json(title, wikitext, facts=(), sections=()):
    """A minimal crawl-JSON document, shaped like the crawler writes."""
    return {
        "title": title,
        "url": f"https://jujutsu-kaisen.fandom.com/wiki/{title.replace(' ', '_')}",
        "pageid": 1,
        "revid": 2,
        "page_type": "character",
        "infobox_template": "Character Infobox",
        "categories": [],
        "templates": ["Character Infobox"],
        "lead": "Lead prose.",
        "sections": [
            {"title": t, "level": lvl, "index": str(i), "path": [], "text": "",
             "wikitext": wt, "links": [], "citations": []}
            for i, (t, wt, lvl) in enumerate(sections)
        ],
        "facts": [
            {"key": k, "value": v, "label": "", "links": [], "citations": [], "raw": v}
            for k, v in facts
        ],
        "edges": [], "links": [], "citations": [],
        "redirects": [], "aliases": [], "wikitext": wikitext,
        "fetched_at": "2026-08-24T00:00:00+00:00",
    }


def _mini_series(tmp_path, title="Angel"):
    root = tmp_path / "series" / "jjk"
    (root / "wikitext").mkdir(parents=True)
    (root / "wikitext" / "Angel.json").write_text(
        json.dumps(_crawl_json(
            "Angel",
            "{{Character Infobox|name=Angel|status=Unknown|race=Human Incarnation|debut=Chapter 199}}\n\n"
            "== Appearance ==\nAppearance prose.\n\n== Synopsis ==\n=== History ===\nHistory prose.\n",
            facts=[("status", "Unknown"), ("race", "Human Incarnation"), ("debut", "Chapter 199")],
            sections=[("Appearance", "Appearance prose.", 2),
                      ("Synopsis", "", 2),
                      ("History", "History prose.", 3)])),
        encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps({
        "wiki": "https://jujutsu-kaisen.fandom.com",
        "ontology": {"wiki": "https://jujutsu-kaisen.fandom.com", "infobox_types": {}},
    }), encoding="utf-8")
    return SeriesPaths(name="jjk", root=root)


def test_parse_page_reextracts_the_stored_crawl(tmp_path):
    paths = _mini_series(tmp_path)
    page = parse_page(paths, "Angel")
    assert page.title == "Angel"
    facts = {f.key: f.value for f in page.facts}
    # `name` survives extraction too: only presentational keys are skipped.
    assert facts["name"] == "Angel"
    assert facts["status"] == "Unknown"
    assert facts["race"] == "Human Incarnation"
    assert facts["debut"] == "Chapter 199"
    # Sections come from the wikitext, re-leveled by the API levels the crawl
    # stored, so `History` lands under its `Synopsis` parent.
    assert [s.title for s in page.sections] == ["Appearance", "Synopsis", "History"]
    assert page.sections[2].breadcrumb == "Synopsis / History"


def test_parse_page_missing_page_raises(tmp_path):
    paths = _mini_series(tmp_path)
    with pytest.raises(FileNotFoundError, match="Angel2"):
        parse_page(paths, "Angel2")
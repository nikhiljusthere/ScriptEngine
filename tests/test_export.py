"""Tests for the Obsidian vault export."""

from __future__ import annotations

import json
import re

import pytest
import yaml

from scriptengine.config import SeriesPaths
from scriptengine.export import export_obsidian
from scriptengine.stores.facts import FactStore

_WIKILINK = re.compile(r"\[\[([^\[\]|]+)(?:\|[^\[\]]+)?\]\]")


def _page(title: str, url: str, *, lead: str, sections: list[dict], wikitext: str) -> dict:
    return {
        "title": title, "url": url, "pageid": 1, "revid": 1,
        "page_type": "character", "infobox_template": "Character Infobox",
        "categories": [], "templates": [], "lead": lead, "sections": sections,
        "facts": [], "edges": [], "links": [], "citations": [],
        "redirects": [], "aliases": [], "wikitext": wikitext,
        "fetched_at": "", "warnings": [],
    }


@pytest.fixture()
def series(tmp_path):
    """A tiny indexed series: two documents, one location, two colliding links."""
    store = FactStore(tmp_path / "facts.db")
    store.initialise()

    todo_doc = store.add_document(
        title="Aoi Todo", url="https://wiki.test/Aoi_Todo", page_type="character",
        infobox_template="Character Infobox", lead="", word_count=0, revid=1, fetched_at="",
    )
    yuji_doc = store.add_document(
        title="Yuji Itadori", url="https://wiki.test/Yuji_Itadori", page_type="character",
        infobox_template="Character Infobox", lead="", word_count=0, revid=1, fetched_at="",
    )

    todo = store.add_node("Aoi Todo", "character", todo_doc)
    store.add_node("Yuji Itadori", "character", yuji_doc)
    kyoto = store.add_node("Kyoto Metropolitan Curse Technical College", "location")
    store.add_node("fr:Aoi Todo")
    store.add_node("fr_Aoi Todo")

    store.add_aliases(todo, ["Aoi Todo", "Todo"])
    store.add_aliases(kyoto, ["Kyoto Metropolitan Curse Technical College", "Kyoto Jujutsu High"])

    store.add_edge(
        source_id=todo, relation="affiliation", target_id=kyoto,
        confidence=0.95, provenance="infobox", section="Affiliation",
    )
    store.add_edge(
        source_id=todo, relation="mentions", target_id=store.node_by_name("Yuji Itadori")["id"],
        confidence=0.6, provenance="prose", section="Synopsis",
    )
    for name in ("fr:Aoi Todo", "fr_Aoi Todo"):
        store.add_edge(
            source_id=kyoto, relation="mentions",
            target_id=store.node_by_name(name)["id"],
            confidence=0.6, provenance="prose", section="Navigation",
        )
    store.add_fact(node_id=todo, key="class", label="Grade", value="Grade 1", citation="Ref vol=5 page=26")
    store.add_fact(node_id=store.node_by_name("Yuji Itadori")["id"], key="species", label="Species", value="Human", citation="")
    store.commit()
    store.close()

    wikitext = tmp_path / "wikitext"
    wikitext.mkdir()

    todo_page = _page(
        "Aoi Todo", "https://wiki.test/Aoi_Todo",
        lead="Aoi Todo is a sorcerer who studies at Kyoto Jujutsu High.",
        wikitext=(
            "Aoi Todo is a sorcerer who studies at [[Kyoto Metropolitan Curse Technical College|Kyoto Jujutsu High]].\n"
            "==Synopsis==\nTodo fights [[Yuji Itadori|Yuji]] at the Goodwill Event (see [[Wikipedia:Todo|Wikipedia]]) and they become friends.\n"
            "==References==\n"
        ),
        sections=[
            {
                "title": "Synopsis", "level": 2, "index": "1", "anchor": "Synopsis", "path": [],
                "text": "Todo fights Yuji at the Goodwill Event (see Wikipedia) and they become friends.",
                "wikitext": "==Synopsis==\nTodo fights [[Yuji Itadori|Yuji]] at the Goodwill Event (see [[Wikipedia:Todo|Wikipedia]]) and they become friends.\n",
                "links": [
                    {"target": "Yuji Itadori", "display": "Yuji"},
                    {"target": "Wikipedia:Todo", "display": "Wikipedia"},
                ],
                "citations": [],
            },
            {
                "title": "References", "level": 2, "index": "2", "anchor": "References", "path": [],
                "text": "", "wikitext": "", "links": [], "citations": [],
            },
        ],
    )
    yuji_page = _page(
        "Yuji Itadori", "https://wiki.test/Yuji_Itadori",
        lead="Yuji Itadori is a sorcerer.",
        wikitext="Yuji Itadori is a sorcerer.\n",
        sections=[],
    )
    (wikitext / "Aoi Todo.json").write_text(json.dumps(todo_page, ensure_ascii=False), encoding="utf-8")
    (wikitext / "Yuji Itadori.json").write_text(json.dumps(yuji_page, ensure_ascii=False), encoding="utf-8")
    return SeriesPaths(name="test", root=tmp_path)


class TestExport:
    def test_node_and_document_files_exist(self, series):
        report = export_obsidian(series)
        assert (series.root / "obsidian" / "nodes" / "Aoi Todo.md").exists()
        assert (series.root / "obsidian" / "documents" / "Aoi Todo.md").exists()
        assert (series.root / "obsidian" / "documents" / "Yuji Itadori.md").exists()
        assert (series.root / "obsidian" / "README.md").exists()
        assert report["nodes"] == 5
        assert report["documents"] == 2

    def test_every_wikilink_resolves_to_a_file(self, series):
        export_obsidian(series)
        vault = series.root / "obsidian"
        for path in vault.rglob("*.md"):
            if path.name == "README.md":
                continue
            for target in _WIKILINK.findall(path.read_text(encoding="utf-8")):
                assert (vault / "nodes" / f"{target}.md").exists() or (
                    vault / "documents" / f"{target}.md"
                ).exists(), f"dangling link [[{target}]] in {path}"

    def test_frontmatter_carries_aliases_facts_and_citations(self, series):
        export_obsidian(series)
        text = (series.root / "obsidian" / "nodes" / "Aoi Todo.md").read_text(encoding="utf-8")
        frontmatter = yaml.safe_load(text.split("---", 2)[1])
        assert frontmatter["type"] == "character"
        assert frontmatter["resolved"] is True
        assert "todo" in frontmatter["aliases"]
        assert frontmatter["Grade"] == "Grade 1"
        assert frontmatter["_citations"]["Grade"] == "Ref vol=5 page=26"

    def test_document_file_relinks_prose_and_skips_boilerplate(self, series):
        export_obsidian(series)
        text = (series.root / "obsidian" / "documents" / "Aoi Todo.md").read_text(encoding="utf-8")
        assert "[[Kyoto Metropolitan Curse Technical College|Kyoto Jujutsu High]]" in text
        assert "[[Yuji Itadori|Yuji]]" in text
        assert "[[Wikipedia" not in text
        assert "## Synopsis" in text
        assert "## References" not in text

    def test_unresolved_nodes_become_stubs(self, series):
        export_obsidian(series)
        text = (series.root / "obsidian" / "nodes" / "Kyoto Metropolitan Curse Technical College.md").read_text(encoding="utf-8")
        assert yaml.safe_load(text.split("---", 2)[1])["resolved"] is False
        assert not (series.root / "obsidian" / "documents" / "Kyoto Metropolitan Curse Technical College.md").exists()

    def test_collided_filenames_are_rewritten(self, series):
        export_obsidian(series)
        # "fr:Aoi Todo" sanitises to "fr_Aoi Todo"; the node that really is
        # "fr_Aoi Todo" keeps the plain name and the namespaced one is suffixed.
        assert (series.root / "obsidian" / "nodes" / "fr_Aoi Todo.md").exists()
        assert (series.root / "obsidian" / "nodes" / "fr_Aoi Todo_2.md").exists()
        kyoto = (series.root / "obsidian" / "nodes" / "Kyoto Metropolitan Curse Technical College.md").read_text(encoding="utf-8")
        assert "[[fr_Aoi Todo]]" in kyoto
        assert "[[fr_Aoi Todo_2]]" in kyoto

    def test_min_confidence_drops_mentions_edges(self, series):
        export_obsidian(series, min_confidence=0.95)
        text = (series.root / "obsidian" / "nodes" / "Aoi Todo.md").read_text(encoding="utf-8")
        assert "[[Kyoto Metropolitan Curse Technical College|affiliation]]" in text
        assert "Yuji Itadori" not in text

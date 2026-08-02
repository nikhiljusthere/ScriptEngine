"""Tests for graph-driven ability lookup."""

from __future__ import annotations

import json

import pytest

from scriptengine.config import SeriesPaths
from scriptengine.retrieve.abilities import collect_abilities
from scriptengine.stores.facts import FactStore


@pytest.fixture()
def series(tmp_path):
    """A tiny series: Yuji uses Black Flash (debut Ch. 48) and Manji Kick."""
    store = FactStore(tmp_path / "facts.db")
    store.initialise()

    yuji_doc = store.add_document(
        title="Yuji Itadori", url="", page_type="character",
        infobox_template="Character Infobox", lead="", word_count=0,
        revid=1, fetched_at="",
    )
    yuji = store.add_node("Yuji Itadori", "character", yuji_doc)
    store.add_aliases(yuji, ["Itadori", "Yuji"])

    for title, debut in [("Black Flash", "Chapter 48"), ("Manji Kick", "Chapter 97")]:
        doc = store.add_document(
            title=title, url="", page_type="technique",
            infobox_template="Technique Infobox", lead="", word_count=0,
            revid=1, fetched_at="",
        )
        ability = store.add_node(title, "technique", doc)
        store.add_edge(
            source_id=ability, relation="user", target_id=yuji,
            confidence=0.95, provenance="infobox", section="Users",
        )
        store.add_edge(
            source_id=ability, relation="debut", target_id=store.add_node(debut),
            confidence=0.95, provenance="infobox", section="Debut",
        )
        store.add_edge(
            source_id=ability, relation="type",
            target_id=store.add_node("Hand-to-Hand Combat"),
            confidence=0.95, provenance="infobox", section="Type",
        )
        store.add_section(
            document_id=doc, title="Yuji Itadori", breadcrumb="Usage / Yuji Itadori",
            level=3, ordinal=0, word_count=3,
            text="Yuji lands Black Flash on a transfigured human, then keeps fighting.",
        )

    store.commit()
    store.close()

    (tmp_path / "wikitext").mkdir()
    (tmp_path / "wikitext" / "Black Flash.json").write_text(
        json.dumps(
            {
                "title": "Black Flash",
                "sections": [
                    {
                        "path": ["Usage"],
                        "title": "Yuji Itadori",
                        "citations": [
                            {"template": "Ref", "params": {"chap": "48"}, "raw": ""},
                            {"template": "Ref", "params": {"chap": "117"}, "raw": ""},
                            {"template": "Ref", "params": {"movie": "0"}, "raw": ""},
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return SeriesPaths(name="test", root=tmp_path)


def test_lists_abilities_with_debuts_and_usage(series):
    result = collect_abilities(series, "Yuji Itadori")

    assert result is not None
    assert result["entity"] == "Yuji Itadori"
    names = [a["name"] for a in result["abilities"]]
    assert names == ["Black Flash", "Manji Kick"]

    black_flash = next(a for a in result["abilities"] if a["name"] == "Black Flash")
    assert black_flash["debut"] == "Chapter 48"
    assert black_flash["type"] == "Hand-to-Hand Combat"
    assert black_flash["usage_chapters"] == [48, 117]  # Ref chap params only
    assert "Yuji lands Black Flash" in black_flash["usage"]


def test_resolves_through_alias(series):
    result = collect_abilities(series, "Itadori")
    assert result is not None
    assert result["entity"] == "Yuji Itadori"


def test_unknown_entity_returns_none(series):
    assert collect_abilities(series, "Sukuna") is None

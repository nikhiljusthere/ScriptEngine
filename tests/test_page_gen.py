"""page-gen: the deterministic structured half of a page-campaign batch."""
import json
import re

import pytest

from scriptengine.config import SeriesPaths
from scriptengine.ingest.crawler import parse_page
from scriptengine.stores.facts import FactStore


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


def _build_store(paths, title="Angel"):
    """The Angel page in `facts.db`, shaped like the campaign's fixture data.

    The document-level `infobox` chunk carries the identity values the
    campaign treats as on-page; the kanji/romaji cells are deliberately
    absent from it, which is what exercises the G3 unchunked-cell retires.
    """
    store = FactStore(paths.facts_db)
    store.initialise()
    doc = store.add_document(
        title=title,
        url="https://jujutsu-kaisen.fandom.com/wiki/Angel",
        page_type="character",
        infobox_template="Character Infobox",
        lead="Lead prose.",
        word_count=12,
        revid=2,
        fetched_at="2026-08-24T00:00:00+00:00",
    )
    sections = [
        ("Appearance", "Appearance", 2, "Angel looks young and delicate, with pale skin."),
        ("Personality", "Personality", 2, "Angel is calm and reserved."),
        ("Synopsis", "Synopsis", 2, ""),
        ("History", "Synopsis / History", 3, "Angel first appears in Chapter 199."),
        ("References", "References", 2, ""),
    ]
    for ordinal, (sect, crumb, level, text) in enumerate(sections, start=1):
        store.add_section(
            document_id=doc, title=sect, breadcrumb=crumb, level=level,
            ordinal=ordinal, text=text, word_count=len(text.split()),
        )
    node = store.add_node(title, label="character", document_id=doc)
    store.add_aliases(node, ["hana kurusu"])
    facts = [
        ("status", "Status", "Unknown"),
        ("race", "Species", "Human Incarnation"),
        ("age", "Age", "1000+"),
        ("gender", "Gender", "Female"),
        ("occupation", "Occupation", ""),
        ("debut", "Manga Debut", "Chapter 199"),
        ("kanji", "Japanese", "天使"),
        ("romaji", "Romaji", "Tenshi"),
        ("alias", "Alias", "Hana Kurusu"),
        ("affiliation", "Affiliation", "Jujutsu Sorcerers\nMaki Zenin Group"),
    ]
    for key, label, value in facts:
        store.add_fact(node_id=node, key=key, label=label, value=value, citation="")
    store.add_chunk(
        document_id=doc, section_id=None, parent_id=None, level=0, ordinal=0,
        doc_title=title, breadcrumb="infobox",
        text="Status: Unknown. Species: Human Incarnation. Age: 1000+."
             " Gender: Female. Debut: Chapter 199.",
    )
    store.commit()
    return store


@pytest.fixture
def series_with_store(tmp_path):
    paths = _mini_series(tmp_path)
    store = _build_store(paths)
    yield paths, store
    store.close()


def test_identity_catalog_one_question_per_field(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=None)
    by_note = {q["note"]: q for q in out.questions}
    assert by_note["page-gen:identity:status"]["question"] == "What is the status of Angel?"
    assert by_note["page-gen:identity:status"]["answer"] == [{"item": "Unknown", "aliases": []}]
    assert by_note["page-gen:identity:race"]["answer"] == [{"item": "Human Incarnation", "aliases": []}]
    assert by_note["page-gen:identity:debut"]["question"] == "In which manga chapter does Angel first appear?"
    assert by_note["page-gen:identity:age"]["answer"] == [{"item": "1000+", "aliases": []}]
    assert all(q["subject"] == "Angel" and q["tier"] == "wiki" for q in out.questions)
    assert all(q["note"].startswith("page-gen:") for q in out.questions)
    # Off-catalogue fields (capabilities and friends) are the prose pass's:
    assert not any(q["note"].startswith("page-gen:identity:capabilities") for q in out.questions)


def test_identity_empty_field_is_auto_retired(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=None)
    assert any("empty" in r["reason"] for r in out.retires)
    assert not any(q["note"] == "page-gen:identity:occupation" for q in out.questions)


def test_unchunked_kanji_is_retired_not_golded(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=None)
    unchecked = [q for q in out.questions
                 if q["note"] in ("page-gen:identity:kanji", "page-gen:identity:romaji")]
    assert unchecked == []
    assert any("unchunked" in r["reason"] for r in out.retires)


def test_alias_and_affiliation_become_rosters(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=None)
    by_name = {r["name"]: r for r in out.rosters}
    assert set(by_name["Angel's aliases"]["members"]) == {"Hana Kurusu"}
    assert set(by_name["Angel's affiliations"]["members"]) == {"Jujutsu Sorcerers", "Maki Zenin Group"}
    by_note = {q["note"]: q for q in out.questions}
    q = by_note["page-gen:affiliation"]
    assert q["kind"] == "set" and q["expect_mode"] == "roster"
    assert [a["item"] for a in q["answer"]] == ["Jujutsu Sorcerers", "Maki Zenin Group"]


def test_phrasing_traps_hold_on_generated_questions(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=None)
    for q in out.questions:
        lead = q["question"].split()
        assert lead[0][0].isupper()
        # House style fronts wh-questions with a preposition ("In which manga
        # chapter does..."), so the guard reads the first content word.
        content = lead[1] if lead[0].lower() in ("in", "on", "at", "by", "to") else lead[0]
        assert content.lower() in ("what", "which", "who", "where", "when", "how")
        assert "whom" not in q["question"].lower()
        assert "in order to" not in q["question"].lower()
        assert "how many" not in q["question"].lower()
    for r in out.rosters:
        for phrase in r["match"]:
            assert not re.search(r"\b(arc|saga)s?\b", phrase)
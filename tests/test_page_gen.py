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
        ("Culling Game Arc", "Synopsis / Culling Game Arc", 3,
         "During the Culling Game, Angel vs. Sukuna takes place on a rooftop."),
        ("Cursed Technique", "Abilities and Powers / Cursed Technique", 3,
         "Flight and Jacob's Ladder are Angel's techniques."),
        ("Trivia", "Trivia", 2, "Angel appears in fan polls."),
        ("References", "References", 2, ""),
        ("Navigation", "Navigation", 2, ""),
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
    _add_battles(store)
    store.ensure_abilities()
    store.save_abilities("Angel", [
        {"name": "Flight", "kind": "technique"},
        {"name": "Jacob's Ladder", "kind": "technique"},
    ], 2, "v1", "test")
    store.ensure_relations()
    store.save_relations("Angel", [
        {"other": "Sukuna", "relation": "rival"},
        {"other": "Higuruma", "relation": "ally"},
        {"other": "Ino", "relation": "ally"},
    ], 2, "v1", "test")
    store.commit()
    return store


def _add_battles(store):
    """Two battle documents: one names the title, one names the alias.

    Shaped like the JJK battle infobox (`side1`/`powers1`), the fixture's
    `_JJK_OVERRIDES` says as much; with `overrides=None` the builder's
    default pairs find nothing and no battle questions are generated.
    """
    specs = [
        {
            "title": "Angel vs. Sukuna",
            "facts": [
                ("side1", "Side 1", "Angel"),
                ("side2", "Side 2", "Sukuna"),
                ("outcome", "Outcome", "Angel wins."),
                ("place", "Place", "Shinjuku"),
                ("date", "Date", "December 24, 2018"),
                ("chapters", "Chapters", "Chapter 199 - 203"),
                ("powers1", "Powers 1", "Angel\nFlight\nJacob's Ladder"),
                ("powers2", "Powers 2", "Sukuna\nCursed Speech"),
            ],
            "text": "Angel vs. Sukuna took place in Shinjuku on December 24, 2018,"
                    " spanning Chapter 199 to 203. The outcome was that Angel wins."
                    " Angel used Flight and Jacob's Ladder against Sukuna's Cursed Speech.",
        },
        {
            "title": "Jujutsu Sorcerers vs. Sukuna",
            "facts": [
                ("side1", "Side 1", "Maki Zenin Hana Kurusu"),
                ("side2", "Side 2", "Sukuna"),
                ("outcome", "Outcome", "Inconclusive."),
                ("chapters", "Chapters", "Chapter 204"),
                ("powers1", "Powers 1", "Maki\nHand-to-Hand Combat\nHana Kurusu\nFlight"),
                ("powers2", "Powers 2", "Sukuna\nCursed Speech"),
            ],
            "text": "Jujutsu Sorcerers vs. Sukuna is recorded in Chapter 204."
                    " The outcome was Inconclusive. Hana Kurusu used Flight.",
        },
    ]
    for spec in specs:
        doc = store.add_document(
            title=spec["title"],
            url=f"https://jujutsu-kaisen.fandom.com/wiki/{spec['title'].replace(' ', '_')}",
            page_type="battle",
            infobox_template="Battle Infobox",
            lead="",
            word_count=len(spec["text"].split()),
            revid=2,
            fetched_at="2026-08-24T00:00:00+00:00",
        )
        section_id = store.add_section(
            document_id=doc, title="Synopsis", breadcrumb="Synopsis", level=2,
            ordinal=1, text=spec["text"], word_count=len(spec["text"].split()),
        )
        node = store.add_node(spec["title"], label="battle", document_id=doc)
        for key, label, value in spec["facts"]:
            store.add_fact(node_id=node, key=key, label=label, value=value, citation="")
        store.add_chunk(
            document_id=doc, section_id=section_id, parent_id=None, level=1,
            ordinal=1, doc_title=spec["title"], breadcrumb="Synopsis", text=spec["text"],
        )


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


# Mirrors `series/jjk/overrides.yaml` `battle_relations:` -- the catalog must
# take the vocabulary from the overrides, never hardcode it.
_JJK_OVERRIDES = {
    "battle_relations": [
        {"side": "side1", "abilities": "powers1"},
        {"side": "side2", "abilities": "powers2"},
    ]
}


def test_battle_block_questions(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    q = {x["note"]: x for x in out.questions}
    assert q["page-gen:battle:Angel vs. Sukuna:outcome"]["question"] == "What is the outcome of Angel vs. Sukuna?"
    assert q["page-gen:battle:Angel vs. Sukuna:outcome"]["answer"] == [{"item": "Angel wins.", "aliases": []}]
    assert q["page-gen:battle:Angel vs. Sukuna:chapters"]["question"] == "In which manga chapter does Angel vs. Sukuna begin?"
    assert q["page-gen:battle:Angel vs. Sukuna:chapters"]["answer"] == [{"item": "Chapter 199", "aliases": []}]
    assert q["page-gen:battle:Jujutsu Sorcerers vs. Sukuna:chapters"]["question"] == "Which manga chapters cover Jujutsu Sorcerers vs. Sukuna?"
    assert "page-gen:battle:Angel vs. Sukuna:episodes" not in q   # no episodes fact on the page
    # every battle fact names the character page and the battle page
    for note, q in q.items():
        if note.startswith("page-gen:battle:"):
            assert len(q["sources"]) == 2 and q["sources"][0].endswith("/wiki/Angel")


def test_battle_set_and_decl(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    setq = [q for q in out.questions if q["note"] == "page-gen:battles"]
    assert len(setq) == 1 and setq[0]["kind"] == "set" and setq[0]["expect_mode"] == "roster"
    items = [a["item"] for a in setq[0]["answer"]]
    assert "Angel vs. Sukuna" in items
    # alias discovery: the battle that names Hana Kurusu is in the set too
    assert len(items) >= 2 and "Jujutsu Sorcerers vs. Sukuna" in items
    decl = [r for r in out.rosters if r["name"] == "Every battle involving Angel"]
    assert decl and set(items) == set(decl[0]["members"])


def test_battle_aliases_override_drives_the_search(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    # Drop the alias row: without it, only the battle naming the title itself
    # is reachable, and the per-wiki bridge (`battle_aliases`) must supply it.
    node = store.node_by_name("Angel")
    store.connection.execute("DELETE FROM aliases WHERE node_id = ?", (node["id"],))
    store.commit()

    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    battles = [q["note"] for q in out.questions if q["note"].startswith("page-gen:battle:")]
    assert any("Angel vs. Sukuna" in n for n in battles)
    assert not any("Jujutsu Sorcerers" in n for n in battles)

    overrides = {**_JJK_OVERRIDES, "battle_aliases": {"Angel": ["Hana Kurusu"]}}
    out2 = generate_structured(paths, "Angel", overrides=overrides)
    setq = next(q for q in out2.questions if q["note"] == "page-gen:battles")
    assert set(a["item"] for a in setq["answer"]) == {
        "Angel vs. Sukuna", "Jujutsu Sorcerers vs. Sukuna"}


def test_battle_page_generates_its_own_facts_not_the_union(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel vs. Sukuna", overrides=_JJK_OVERRIDES)
    notes = [q["note"] for q in out.questions]
    # A battle page's subject is the fight itself: its own infobox facts, never
    # the union of every battle a fighter in it is in elsewhere (the old code
    # reduced the title to "sukuna" and pulled in both fixture battles).
    assert "page-gen:battle:Angel vs. Sukuna:outcome" in notes
    assert not any("Jujutsu Sorcerers vs. Sukuna" in n for n in notes)
    # The degenerate one-battle "every battle" set/roster is not declared.
    assert "page-gen:battles" not in notes
    assert not any(r["name"] == "Every battle involving Angel vs. Sukuna"
                   for r in out.rosters)
    outcome = next(q for q in out.questions
                   if q["note"] == "page-gen:battle:Angel vs. Sukuna:outcome")
    assert outcome["answer"] == [{"item": "Angel wins.", "aliases": []}]


def test_battle_technique_question_is_a_fact_not_a_roster(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    q = [x for x in out.questions if x["note"] == "page-gen:battle:Angel vs. Sukuna:techniques"]
    assert q and q[0]["kind"] == "fact" and q[0]["expect_mode"] == "qa"
    assert [a["item"] for a in q[0]["answer"]] == ["Flight, Jacob's Ladder"]
    # the alias-matched battle names the character by alias in its question,
    # and its technique span is read from under her marker in a side cell that
    # lists several fighters (the live JJK shape, `<br/>`-flattened to spaces)
    q2 = [x for x in out.questions if x["note"] == "page-gen:battle:Jujutsu Sorcerers vs. Sukuna:techniques"]
    assert q2 and "Hana Kurusu" in q2[0]["question"]
    assert [a["item"] for a in q2[0]["answer"]] == ["Flight"]


def test_technique_roster_and_set(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    decl = [r for r in out.rosters if r["name"] == "Every named technique of Angel"]
    assert decl and set(decl[0]["members"]) == {"Flight", "Jacob's Ladder"}
    q = [x for x in out.questions if x["note"] == "page-gen:techniques"]
    assert q and q[0]["kind"] == "set" and q[0]["expect_mode"] == "roster"
    assert [a["item"] for a in q[0]["answer"]] and set(a["item"] for a in q[0]["answer"]) == {
        "Flight", "Jacob's Ladder"}


def test_relation_rosters_group_by_relation(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    names = {r["name"] for r in out.rosters}
    assert "Every ally of Angel" in names
    # a one-line relation is prose, not a closed set (the Kento Nanami finding)
    assert "Every rival of Angel" not in names
    decl = [r for r in out.rosters if r["name"] == "Every ally of Angel"][0]
    assert set(decl["members"]) == {"Higuruma", "Ino"}
    q = [x for x in out.questions if x["note"] == "page-gen:relation:ally"]
    assert q and q[0]["kind"] == "set" and q[0]["expect_mode"] == "roster"


def test_coverage_marks_uncovered_and_retired(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    cov = out.coverage
    paths_covered = {s["path"] for s in cov["sections"] if s["covered_by"]}
    assert "Synopsis / Culling Game Arc" in paths_covered
    assert "Abilities and Powers / Cursed Technique" in paths_covered
    assert "Trivia" in cov["uncovered"]
    retired = {s["path"]: s["reason"] for s in cov["retired_sections"]}
    assert "References" in retired and "Navigation" in retired
    # the ledger is exhaustive: every section is covered, uncovered, or retired
    all_paths = {s["path"] for s in cov["sections"]}
    assert all_paths == paths_covered | set(cov["uncovered"]) | set(retired)


def test_virtual_infobox_section_is_covered_by_identity(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    by_path = {s["path"]: s for s in out.coverage["sections"]}
    assert by_path["infobox"]["covered_by"]
    assert by_path["lead"]["covered_by"]
    # battle questions land on the section that narrates the fight
    battle = [s for s in out.coverage["sections"]
              if s["path"] == "Synopsis / Culling Game Arc"][0]
    assert any(n.startswith("page-gen:battle:") for n in battle["covered_by"])


def test_verify_sheet_shape(series_with_store):
    from scriptengine.eval.page_gen import generate_structured

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    row = {v["question"]: v for v in out.verify}
    v = row["What is the status of Angel?"]
    assert v["source"] == "identity:status"
    assert v["page_span"] == "Unknown"
    assert v["section"] == "infobox"
    set_row = row["Every battle involving Angel"]
    assert set_row["kind"] == "set"
    assert "Angel vs. Sukuna" in set_row["answer"]
    assert set_row["section"] == "infobox"


def test_route_safe_flags_each_trap():
    from scriptengine.eval.page_gen import route_safe

    assert route_safe("What is Angel's status?") == []
    assert route_safe("In which manga chapter does Angel first appear?") == []
    assert route_safe("Every battle involving Angel", kind="set") == []
    assert "wh-word" in route_safe("According to the wiki, Angel...")
    assert "whom" in route_safe("Whom did Angel fight?")
    assert "in order to" in route_safe("What did Angel do in order to win?")
    assert "how many" in route_safe("How many battles did Angel have?")


def test_generator_raises_on_trap_question(series_with_store, monkeypatch):
    from scriptengine import eval as eval_pkg

    paths, store = series_with_store
    import scriptengine.eval.page_gen as pg

    real_builder = pg._identity_builder

    def trap_builder(store_, paths_, title, aliases, overrides, wiki, out, verified):
        real_builder(store_, paths_, title, aliases, overrides, wiki, out, verified)
        out.questions.append({
            "id": "", "kind": "fact", "question": "According to the wiki, Angel's status",
            "subject": title, "tier": "wiki", "expect_mode": "qa", "scope": "closed",
            "answer": [{"item": "Unknown", "aliases": []}], "sources": [],
            "verified": verified, "note": "page-gen:trap",
        })

    monkeypatch.setattr(pg, "_BUILDERS", (trap_builder,))
    import pytest
    with pytest.raises(pg.PageGenError, match="According to"):
        pg.generate_structured(paths, "Angel", overrides=None)


def test_write_batch_creates_and_validates(tmp_path, series_with_store):
    from scriptengine.eval import questions as Q
    from scriptengine.eval.page_gen import generate_structured, write_batch

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    batch = write_batch(tmp_path / "_jjk_page_angel.json", "jjk", "angel",
                        "https://jujutsu-kaisen.fandom.com", out)
    ids = [q["id"] for q in batch["questions"]]
    assert len(ids) == len(set(ids))
    assert ids and all(i.startswith("jjk-pg-angel-") for i in ids)
    assert batch["series"] == "jjk" and batch["wiki"].startswith("https://")
    Q.validate([Q.load_file(tmp_path / "_jjk_page_angel.json")])


def test_rerun_never_clobbers_hand_authored(tmp_path, series_with_store):
    from scriptengine.eval.page_gen import generate_structured, write_batch

    paths, store = series_with_store
    out1 = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    first = write_batch(tmp_path / "_jjk_page_angel.json", "jjk", "angel",
                        "https://jujutsu-kaisen.fandom.com", out1)
    hand = {"id": "jjk-pg-angel-900", "kind": "fact",
            "question": "How did Angel defeat Sukuna in the Culling Game?",
            "subject": "Angel", "tier": "wiki", "expect_mode": "qa", "scope": "closed",
            "answer": [{"item": "she did not"}],
            "sources": ["https://jujutsu-kaisen.fandom.com/wiki/Angel"],
            "verified": "2026-08-23", "note": "hand-authored S1"}
    existing = dict(first)
    existing["questions"] = list(first["questions"]) + [hand]
    out2 = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    second = write_batch(tmp_path / "_jjk_page_angel.json", "jjk", "angel",
                         "https://jujutsu-kaisen.fandom.com", out2, existing=existing)
    assert any(q["id"] == "jjk-pg-angel-900" for q in second["questions"])
    assert all(q["id"] == "jjk-pg-angel-900" or q["note"].startswith("page-gen:")
               for q in second["questions"])


def test_collision_supersedes_the_hand_authored(tmp_path, series_with_store):
    from scriptengine.eval.page_gen import generate_structured, write_batch

    paths, store = series_with_store
    out = generate_structured(paths, "Angel", overrides=_JJK_OVERRIDES)
    dup = {"id": "jjk-pg-angel-777", "kind": "fact",
           "question": "What is the status of Angel?",
           "subject": "Angel", "tier": "wiki", "expect_mode": "qa", "scope": "closed",
           "answer": [{"item": "Unknown"}],
           "sources": ["https://jujutsu-kaisen.fandom.com/wiki/Angel"],
           "verified": "2026-08-23", "note": "hand S4"}
    batch = write_batch(tmp_path / "_jjk_page_angel.json", "jjk", "angel",
                        "https://jujutsu-kaisen.fandom.com", out,
                        existing={"questions": [dup], "retired": []})
    assert all(q["id"] != "jjk-pg-angel-777" for q in batch["questions"])
    assert any("superseded" in r["reason"] for r in batch["retired"])


def _merge_fixture(tmp_path):
    overrides = tmp_path / "overrides.yaml"
    overrides.write_text(
        "rosters:\n"
        "  # a comment that must survive\n"
        "  - name: Existing Roster\n"
        "    match: [existing]\n"
        "    members: [One]\n"
        "battle_relations:\n"
        "  - side: side1\n"
        "    abilities: powers1\n", encoding="utf-8")
    decl = tmp_path / "decl.yaml"
    decl.write_text("rosters:\n"
                    "  - name: New Roster\n"
                    "    match: [new]\n"
                    "    subject: Angel\n"
                    '    members: ["A", "B: C"]\n', encoding="utf-8")
    return overrides, decl


def test_render_decl_quoting_and_style():
    from scriptengine.eval.page_gen import PageGenOutput, render_decl
    import yaml

    out = PageGenOutput()
    out.rosters.append({
        "name": "Every battle involving Angel",
        "match": ["every battle involving angel"],
        "subject": "Angel",
        "members": ["Angel vs. Sukuna", "Desshi Pacification Squad vs. Sukuna: Round 2"],
    })
    text = render_decl(out, "Angel", "2026-08-24")
    rosters = yaml.safe_load(text)
    assert list(rosters) == ["rosters"]
    assert rosters["rosters"][0]["members"] == [
        "Angel vs. Sukuna", "Desshi Pacification Squad vs. Sukuna: Round 2"]
    # a value containing ':' must be JSON-quoted in the source, not a plain scalar
    assert '"Desshi Pacification Squad vs. Sukuna: Round 2"' in text
    assert "2026-08-24" in text and "Angel" in text


def test_merge_decl_text_inserts_and_preserves_comments(tmp_path):
    from scriptengine.eval.page_gen import merge_decl
    import yaml

    overrides, decl = _merge_fixture(tmp_path)
    inserted = merge_decl(decl, overrides, "# ── page-gen: Angel (2026-08-24) ──")
    assert inserted == 1
    text = overrides.read_text(encoding="utf-8")
    assert "# a comment that must survive" in text
    assert "New Roster" in text
    rosters = yaml.safe_load(text)["rosters"]
    assert [r["name"] for r in rosters] == ["Existing Roster", "New Roster"]
    assert yaml.safe_load(text)["battle_relations"] == [
        {"side": "side1", "abilities": "powers1"}]


def test_merge_decl_skips_duplicate_names(tmp_path):
    from scriptengine.eval.page_gen import merge_decl

    overrides, decl = _merge_fixture(tmp_path)
    before = overrides.read_text(encoding="utf-8")
    dup = tmp_path / "dup_decl.yaml"
    dup.write_text("rosters:\n  - name: Existing Roster\n    match: [existing]\n",
                   encoding="utf-8")
    assert merge_decl(dup, overrides, "# header") == 0
    assert overrides.read_text(encoding="utf-8") == before


def test_merge_decl_appends_when_no_rosters_key(tmp_path):
    from scriptengine.eval.page_gen import merge_decl
    import yaml

    overrides = tmp_path / "overrides.yaml"
    overrides.write_text("battle_relations:\n  - side: side1\n    abilities: powers1\n",
                         encoding="utf-8")
    decl = tmp_path / "decl.yaml"
    decl.write_text("rosters:\n  - name: New Roster\n    match: [new]\n",
                    encoding="utf-8")
    assert merge_decl(decl, overrides, "# header") == 1
    rosters = yaml.safe_load(overrides.read_text(encoding="utf-8"))["rosters"]
    assert [r["name"] for r in rosters] == ["New Roster"]


def test_prose_extra_sections_groups_by_section_path():
    from scriptengine.eval.page_gen import prose_extra_sections

    batch = {"questions": [
        {"id": "1", "note": "prose:Trivia", "question": "q1"},
        {"id": "2", "note": "prose:Appearance", "question": "q2"},
        {"id": "3", "note": "prose:Trivia", "question": "q3"},
        {"id": "4", "note": "page-gen:identity:status", "question": "q4"},
        {"id": "5", "note": "S1: lead", "question": "q5"},
    ]}
    extra = prose_extra_sections(batch)
    assert set(extra) == {"Trivia", "Appearance"}
    assert [q["id"] for q in extra["Trivia"]] == ["1", "3"]
    assert [q["id"] for q in extra["Appearance"]] == ["2"]
    # A `prose:` note with no path, and an empty batch, contribute nothing.
    assert prose_extra_sections({"questions": [{"note": "prose:", "question": "q"}]}) == {}
    assert prose_extra_sections({}) == {}


def test_page_set_by_tier(series_with_store):
    from scriptengine.eval.page_gen import PageGenError, page_set

    paths, store = series_with_store
    assert page_set(store, "a") == ["Angel"]
    assert page_set(store, "b") == ["Angel vs. Sukuna", "Jujutsu Sorcerers vs. Sukuna"]
    # `include` reaches the pages the tier filter never would
    assert page_set(store, "a", include=["Angel vs. Sukuna"]) == [
        "Angel", "Angel vs. Sukuna"]
    with pytest.raises(PageGenError, match="unknown tier"):
        page_set(store, "z")


def test_run_page_gen_status(series_with_store, tmp_path):
    from scriptengine.eval.page_gen import run_page_gen

    paths, _ = series_with_store
    status = run_page_gen(
        paths, "Angel", _JJK_OVERRIDES,
        tmp_path / "b.json", tmp_path / "decl.yaml",
        tmp_path / "coverage.json", tmp_path / "verify.json")
    assert (tmp_path / "b.json").exists()
    assert (tmp_path / "decl.yaml").exists()
    assert (tmp_path / "coverage.json").exists()
    assert status["page"] == "Angel"
    assert status["structured"] > 0 and "identity" in status["by_class"]
    assert status["uncovered"]  # the fixture leaves prose sections uncovered


def test_roster_phrase_safe_bans_arc_saga_words():
    from scriptengine.eval.page_gen import _roster_phrase_safe

    assert _roster_phrase_safe("Sukuna")
    assert _roster_phrase_safe("Maki Zenin")
    # a word "arc"/"saga" in the title lands in the roster match phrase -> unsafe
    assert not _roster_phrase_safe("Fearsome Womb Arc")
    assert not _roster_phrase_safe("Gojo's Past Arc")
    assert not _roster_phrase_safe("Vs. Mahito Arc")
    assert not _roster_phrase_safe("The Final Saga")


def test_declared_battles_wins_over_discovery():
    from scriptengine.eval.page_gen import _declared_battles

    overrides = {"rosters": [
        {"name": "Angel's aliases", "match": ["angel's aliases"],
         "subject": "Angel", "members": ["Hana Kurusu"]},
        {"name": "Every battle involving Angel",
         "match": ["every battle involving angel"],
         "subject": "Angel", "members": ["Angel vs. Sukuna"]},
    ]}
    # the battles roster (name carries "battle") is picked, not the aliases one
    assert _declared_battles(overrides, "Angel") == ["Angel vs. Sukuna"]
    assert _declared_battles(overrides, "Nobody") is None
    # a character with no declared battles roster falls back to discovery
    assert _declared_battles({"rosters": overrides["rosters"][:1]}, "Angel") is None


def _cli(tmp_path, monkeypatch):
    """Point the CLI's settings at the fixture's series tree + a fresh questions root."""
    import scriptengine.cli as cli
    from scriptengine.config import Settings

    settings = Settings(series_root=tmp_path / "series",
                        questions_root=tmp_path / "questions")
    monkeypatch.setattr(cli, "get_settings", lambda: settings)
    return cli


def test_page_gen_command_writes_all_four_artifacts(tmp_path, series_with_store, monkeypatch):
    import json
    from typer.testing import CliRunner

    cli = _cli(tmp_path, monkeypatch)
    result = CliRunner().invoke(cli.app, ["page-gen", "--series", "jjk", "--page", "Angel"])
    assert result.exit_code == 0, result.output
    q = tmp_path / "questions" / "_jjk_page_angel.json"
    for name in ("_jjk_page_angel.decl.yaml", "_jjk_page_angel.coverage.json",
                 "_jjk_page_angel.verify.json"):
        assert (tmp_path / "questions" / name).exists()
    batch = json.loads(q.read_text(encoding="utf-8"))
    assert batch["questions"] and all(x["note"].startswith("page-gen:") for x in batch["questions"])


def test_page_merge_command_inserts_into_overrides(tmp_path, series_with_store, monkeypatch):
    from typer.testing import CliRunner
    import yaml

    cli = _cli(tmp_path, monkeypatch)
    paths, _ = series_with_store
    paths.overrides.write_text(
        "rosters:\n  - name: Existing\n    match: [existing]\n", encoding="utf-8")
    decl = tmp_path / "questions" / "_jjk_page_angel.decl.yaml"
    decl.parent.mkdir(parents=True, exist_ok=True)
    decl.write_text("rosters:\n"
                    "  - name: Every battle involving Angel\n"
                    "    match: [every battle involving angel]\n"
                    "    subject: Angel\n"
                    "    members: [Angel vs. Sukuna]\n", encoding="utf-8")

    result = CliRunner().invoke(cli.app, ["page-merge", "--series", "jjk", "--batch", "angel"])
    assert result.exit_code == 0, result.output
    rosters = yaml.safe_load(paths.overrides.read_text(encoding="utf-8"))["rosters"]
    assert [r["name"] for r in rosters] == ["Existing", "Every battle involving Angel"]


def test_page_gen_rerun_feeds_prose_questions_into_the_ledger(tmp_path, series_with_store, monkeypatch):
    import json
    from typer.testing import CliRunner

    cli = _cli(tmp_path, monkeypatch)
    result = CliRunner().invoke(cli.app, ["page-gen", "--series", "jjk", "--page", "Angel"])
    assert result.exit_code == 0, result.output
    batch_path = tmp_path / "questions" / "_jjk_page_angel.json"
    coverage_path = tmp_path / "questions" / "_jjk_page_angel.coverage.json"
    cov1 = json.loads(coverage_path.read_text(encoding="utf-8"))
    assert "Trivia" in cov1["uncovered"]

    # Phase 3 registered a prose question for Trivia, as the prose pass would.
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    batch["questions"].append({
        "id": "jjk-pg-angel-900",
        "kind": "fact",
        "question": "What fan-poll result is recorded for Angel?",
        "subject": "Angel",
        "tier": "wiki",
        "expect_mode": "qa",
        "scope": "open",
        "answer": [{"item": "Angel appears in fan polls.", "aliases": []}],
        "sources": ["https://jujutsu-kaisen.fandom.com/wiki/Angel"],
        "verified": "2026-08-24",
        "note": "prose:Trivia",
    })
    batch_path.write_text(json.dumps(batch, indent=2, ensure_ascii=False), encoding="utf-8")

    # The re-run's ledger must see the prose question and keep it in the batch.
    result = CliRunner().invoke(cli.app, ["page-gen", "--series", "jjk", "--page", "Angel"])
    assert result.exit_code == 0, result.output
    cov2 = json.loads(coverage_path.read_text(encoding="utf-8"))
    assert "Trivia" not in cov2["uncovered"]
    by_path = {s["path"]: s for s in cov2["sections"]}
    assert "prose:Trivia" in by_path["Trivia"]["covered_by"]
    batch2 = json.loads(batch_path.read_text(encoding="utf-8"))
    assert any(q.get("note") == "prose:Trivia" for q in batch2["questions"])


def test_page_sweep_command(tmp_path, series_with_store, monkeypatch):
    import json
    from typer.testing import CliRunner
    from scriptengine.eval.page_gen import slug_of

    cli = _cli(tmp_path, monkeypatch)
    result = CliRunner().invoke(cli.app, ["page-sweep", "--series", "jjk", "--tier", "b"])
    assert result.exit_code == 0, result.output
    report_path = tmp_path / "questions" / "_jjk_page_sweep_b.report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    swept = {p["page"] for p in report["pages"]}
    assert swept == {"Angel vs. Sukuna", "Jujutsu Sorcerers vs. Sukuna"}
    for page in swept:
        assert (tmp_path / "questions" / f"_jjk_page_{slug_of(page)}.json").exists()
    # resumable: a second run sweeps nothing new
    result = CliRunner().invoke(cli.app, ["page-sweep", "--series", "jjk", "--tier", "b"])
    assert "swept 0 page(s)" in result.output
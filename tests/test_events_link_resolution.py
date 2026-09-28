"""Link-aware participant resolution (architect 2026-09-28).

The wiki's own wikilinks are pre-resolved edges: a page's `chunk_nodes` set
is the wiki's answer to "which variant of this name does this page mean".
The rule: an ambiguous candidate set with exactly one linked member resolves
deterministically; zero or several linked members stay a counted ambiguity.

Four tests pin it:

* `pick_candidate` carries the link set: it breaks a tie the reality signal
  leaves, inside the reality-narrowed set when reality narrows;
* the wiki's shape rules (2026-09-28): an exact title match wins over the
  name's `(qualifier)` and `/subpage` variants, and a variant is a
  candidate only where the passage points at it -- a link from the page or
  the passage's own page; unpointed variants alone resolve to nothing;
* `re_resolve_participants` repairs stored rows in both directions -- a row
  in the explicit-ambiguous form (NULL node, the candidate list in the name)
  is re-pointed to its page's sole linked candidate, and a row that already
  carries a node is re-pointed when its name maps to a multi-candidate pool;
  a re-point that would duplicate a row the page already stores merges
  (the wiki's answer is recorded once, the store's own dedup rule);
* the receipt's numbers: the ambiguous tally drops by exactly the rescued
  rows, and `link_broken` counts what the link signal alone did -- a
  re-point the shape rule reaches on its own is the shape rule's, not the
  link's.

The wiki's declared non-participant prefixes (`events:
participant_excludes:`, the mcu's `Hub:` index pages, 2026-09-28) are
tested where they live: in the pool the shapes fold over,
`participant_candidates`.
"""

from __future__ import annotations

import pytest

from scriptengine.ingest.events import (
    participant_candidates,
    pick_candidate,
    re_resolve_participants,
)
from scriptengine.stores.facts import FactStore


def test_the_link_signal_breaks_a_set_that_reality_leaves():
    cands = [
        (11, "Wolverine (Earth-616)", None),
        (12, "Hellverine (Demon) (Earth-616)", None),
    ]
    # No signal at all: a counted ambiguity...
    assert pick_candidate(cands, None, None) == {"ambiguous": cands}
    # ...and exactly one linked member is the wiki's own answer.
    assert pick_candidate(cands, None, None, {11}) == (11, "Wolverine (Earth-616)", None)
    # Several linked members break nothing, and neither does none.
    assert pick_candidate(cands, None, None, {11, 12}) == {"ambiguous": cands}
    assert pick_candidate(cands, None, None, set()) == {"ambiguous": cands}
    # Where reality narrows the set, the link breaks the tie inside it.
    real = [
        (11, "A (Earth-616)", "earth-616"),
        (12, "B (Earth-616)", "earth-616"),
        (13, "C (Tierra-982)", "tierra-982"),
    ]
    assert pick_candidate(real, None, "earth-616") == {"ambiguous": real[:2]}
    assert pick_candidate(real, None, "earth-616", {12}) == (12, "B (Earth-616)", "earth-616")


def test_the_bare_name_never_names_a_variant_the_passage_does_not_point_at():
    # The pool a bare name folds over carries the wiki's variant forms of it
    # (the `/subpage` and `(qualifier)` shapes, 2026-09-28).
    pool = [
        (21, "Thanos", None),
        (22, "Thanos/Age of Ultron", None),
        (23, "Thanos/Earth-838", None),
    ]
    # The exact title match wins over every variant of the name, whatever
    # the casing the model wrote.
    assert pick_candidate(pool, "Thanos", None) == (21, "Thanos", None)
    assert pick_candidate(pool, "thanos", None) == (21, "Thanos", None)
    # Where the exact page is absent, a variant is a candidate only where
    # the passage points at it: a link from the page...
    spin = [(22, "Thanos/Age of Ultron", None), (23, "Thanos/Earth-838", None)]
    assert pick_candidate(spin, "Thanos") is None
    assert pick_candidate(spin, "Thanos", None, {22}) == (22, "Thanos/Age of Ultron", None)
    # ...or the passage's own page is that variant.
    avengers = [
        (31, "The Avengers", None),
        (32, "The Avengers (comic)", None),
        (33, "The Avengers/Home Video", None),
    ]
    assert pick_candidate(avengers, "The Avengers") == (31, "The Avengers", None)
    spin_av = [(32, "The Avengers (comic)", None), (33, "The Avengers/Home Video", None)]
    assert pick_candidate(spin_av, "The Avengers", None, {32}) == (32, "The Avengers (comic)", None)
    assert pick_candidate(
        spin_av, "The Avengers", None, set(), "The Avengers/Home Video"
    ) == (33, "The Avengers/Home Video", None)
    # A page that is the variant of another name points at nothing here.
    assert pick_candidate(spin_av, "The Avengers", None, set(), "Loki") is None
    # Several pointed variants break nothing: a counted ambiguity.
    assert isinstance(pick_candidate(spin, "Thanos", None, {22, 23}), dict)


def test_the_wikis_declared_non_participants_leave_their_pools(tmp_path):
    # The mcu declaration (2026-09-28): the wiki's `Hub:` index pages are
    # apparatus, never event participants.
    root = tmp_path / "hubwiki"
    root.mkdir()
    (root / "overrides.yaml").write_text(
        "events:\n  participant_excludes:\n    - 'Hub:'\n", encoding="utf-8"
    )
    store = FactStore(root / "facts.db")
    store.initialise()
    c = store.connection
    c.executemany(
        "INSERT INTO documents (id, title, page_type) VALUES (?, ?, ?)",
        [(1, "Thanos", "character"), (2, "Hub:Thanos", "character")],
    )
    c.executemany(
        "INSERT INTO nodes (id, name, document_id, is_resolved) VALUES (?, ?, ?, 1)",
        [(1, "Thanos", 1), (2, "Hub:Thanos", 2)],
    )
    c.execute("INSERT INTO aliases (alias, node_id) VALUES ('Thanos', 2)")
    c.commit()

    cands = participant_candidates(store)
    # The hub's own name and its alias both fold onto the declared prefix:
    # the pool the bare name reaches carries the character page, never the
    # hub, so the bare name resolves exactly.
    assert [c[1] for c in cands["thanos"]] == ["Thanos"]
    assert "hub:thanos" not in cands
    store.close()

    # A wiki that declares nothing is untouched: the hub stays a candidate.
    silent = tmp_path / "silent"
    silent.mkdir()
    s2 = FactStore(silent / "facts.db")
    s2.initialise()
    c2 = s2.connection
    c2.executemany(
        "INSERT INTO documents (id, title, page_type) VALUES (?, ?, ?)",
        [(1, "Thanos", "character"), (2, "Hub:Thanos", "character")],
    )
    c2.executemany(
        "INSERT INTO nodes (id, name, document_id, is_resolved) VALUES (?, ?, ?, 1)",
        [(1, "Thanos", 1), (2, "Hub:Thanos", 2)],
    )
    c2.execute("INSERT INTO aliases (alias, node_id) VALUES ('Thanos', 2)")
    c2.commit()
    assert [c[1] for c in participant_candidates(s2)["thanos"]] == [
        "Thanos",
        "Hub:Thanos",
    ]
    s2.close()


@pytest.fixture()
def store(tmp_path):
    """One store, four event pages, the one codename collision.

    The codename `Wolverine` is an alias of two variant nodes, so the name
    maps to a two-candidate pool -- the same-reality collision the link
    signal exists to break. Each event page states one row against Magneto:

    * X of Swords: the explicit-ambiguous form, and the page links to
      exactly one of the two variants -- the wiki answered;
    * Siege: the same filed name, but the page links to both -- the wiki
      did not answer;
    * Civil War: the same filed name, the page links to neither;
    * Secret Invasion: a row that already carries a node, under the bare
      codename, on a page that links to the *other* variant;
    * Avengers: the same event stored twice -- once resolved (the wiki's
      answer) and once in the ambiguous form. The page links to the
      resolved variant, so the rescue re-points the ambiguous row onto its
      duplicate and the pair merges.
    """
    root = tmp_path / "linkres"
    root.mkdir()
    store = FactStore(root / "facts.db")
    store.initialise()
    store.ensure_events()
    wolverine_doc = store.add_document(
        title="Wolverine", url="", page_type="character",
        infobox_template="Character Infobox",
        lead="Wolverine is a mutant with claws.",
        word_count=7, revid=1, fetched_at="",
    )
    hellverine_doc = store.add_document(
        title="Hellverine", url="", page_type="character",
        infobox_template="Character Infobox",
        lead="Hellverine is a demon wearing Wolverine's face.",
        word_count=8, revid=1, fetched_at="",
    )
    magneto_doc = store.add_document(
        title="Magneto", url="", page_type="character",
        infobox_template="Character Infobox",
        lead="Magneto is a mutant villain.",
        word_count=6, revid=1, fetched_at="",
    )
    wolverine = store.add_node("Wolverine (Earth-616)", "character", wolverine_doc)
    hellverine = store.add_node("Hellverine (Demon) (Earth-616)", "character", hellverine_doc)
    magneto = store.add_node("Magneto", "character", magneto_doc)
    store.add_aliases(wolverine, ["Wolverine"])
    store.add_aliases(hellverine, ["Wolverine"])

    def event_page(title: str, links: list[int]) -> int:
        doc = store.add_document(
            title=title, url="", page_type="event",
            infobox_template="Event Infobox",
            lead="The war comes to a head.",
            word_count=6, revid=1, fetched_at="",
        )
        section = store.add_section(
            document_id=doc, title="Plot", breadcrumb=f"{title}/Plot", level=2,
            ordinal=0,
            text=("The war comes to a head as Magneto and the X-Men clash"
                  " over the dark dimension."),
            word_count=15,
        )
        chunk = store.add_chunk(
            document_id=doc, section_id=section, parent_id=None, level=2,
            ordinal=0, doc_title=title, breadcrumb=f"{title}/Plot",
            text="The war comes to a head.",
        )
        if links:
            store.link_chunk_nodes(chunk, links)
        return section

    ambiguous_name = "Wolverine (Earth-616) | Hellverine (Demon) (Earth-616)"

    def row(section: int, subject_node, subject_name) -> dict:
        return {
            "subject_node": subject_node, "subject_name": subject_name,
            "object_node": magneto, "object_name": "Magneto",
            "verb": "fought", "section_id": section,
            "quote": "Wolverine fights Magneto",
            "temporal": True, "time_rank": 0.0,
        }

    store.save_events(
        "X of Swords",
        [row(event_page("X of Swords", [wolverine, magneto]), None, ambiguous_name)],
        revid=1, prompt_version="test", model="test",
    )
    store.save_events(
        "Siege",
        [row(event_page("Siege", [wolverine, hellverine, magneto]), None, ambiguous_name)],
        revid=1, prompt_version="test", model="test",
    )
    store.save_events(
        "Civil War",
        [row(event_page("Civil War", [magneto]), None, ambiguous_name)],
        revid=1, prompt_version="test", model="test",
    )
    store.save_events(
        "Secret Invasion",
        [row(event_page("Secret Invasion", [hellverine, magneto]), wolverine, "Wolverine")],
        revid=1, prompt_version="test", model="test",
    )
    # The same event, two ways of filing it: once resolved (the row the
    # page's link points at -- the wiki's answer) and once in the ambiguous
    # form. The rescue re-points the latter onto its duplicate, and the pair
    # must merge, not double-record the event.
    avengers_section = event_page("Avengers", [wolverine, magneto])
    store.save_events(
        "Avengers",
        [
            row(avengers_section, wolverine, "Wolverine (Earth-616)"),
            row(avengers_section, None, ambiguous_name),
        ],
        revid=1, prompt_version="test", model="test",
    )
    store.commit()
    store.close()
    return root, wolverine, hellverine, magneto


def test_the_pages_own_links_repair_the_filed_rows(store):
    root, wolverine, hellverine, magneto = store
    with FactStore(root / "facts.db") as s:
        s.ensure_events()
        report = re_resolve_participants(s)
        rows = {
            r["arc_key"]: (r["subject_node"], r["subject_name"])
            for r in s.connection.execute(
                "SELECT arc_key, subject_node, subject_name FROM events"
            )
        }
        row_count = s.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    # Two of the four filed ambiguities are the wiki's own answers.
    assert report["before"]["rows"] == 6
    assert report["before"]["ambiguous"] == 4
    assert report["after"]["rows"] == 5
    assert report["after"]["ambiguous"] == 2
    assert rows["X of Swords"] == (wolverine, "Wolverine (Earth-616)")
    # The page that linked both variants, and the one that linked neither,
    # keep their counted ambiguity, names untouched.
    assert rows["Siege"] == (None, "Wolverine (Earth-616) | Hellverine (Demon) (Earth-616)")
    assert rows["Civil War"] == (None, "Wolverine (Earth-616) | Hellverine (Demon) (Earth-616)")
    # The row that already carried a node is re-pointed by the page's link
    # to the variant the page actually means.
    assert rows["Secret Invasion"] == (hellverine, "Hellverine (Demon) (Earth-616)")
    # The re-pointed row that duplicates the page's stored answer merges:
    # the event is recorded once, and the merge is its own number.
    assert rows["Avengers"] == (wolverine, "Wolverine (Earth-616)")
    assert row_count == 5
    assert report["after"]["merged"] == 1
    # The link signal alone did two re-pointings: the rescued row and the
    # merged row. The 'Secret Invasion' re-point is the shape rule's -- the
    # unpointed variant falls out of the pool on its own, so the probe
    # without the page signals reaches the same node, and the tally keeps
    # the two signals apart.
    assert report["after"]["link_broken"] == 2
    assert report["after"]["moved"] == 7

def test_the_pages_own_entity_wins_for_its_own_names():
    """R12 fix 2: on Henry McCoy (Earth-616), "Beast" names the page's own
    subject; the page never links to itself, so without this rule the link
    signal picked the only linked namesake (the clone)."""
    from scriptengine.ingest.events import pick_candidate

    own = (1, "Henry McCoy (Earth-616)", "616")
    clone = (2, "Henry McCoy (Clone) (Earth-616)", "616")
    pick = pick_candidate([own, clone], "Beast", "616", {2},
                          "Henry McCoy (Earth-616)")
    assert pick == own
    # On another page the same pair stays the link signal's call.
    assert pick_candidate([own, clone], "Beast", "616", {2},
                          "Utopia (X-Men Base)") == clone


def test_stored_rows_re_resolve_from_the_raw_mention(tmp_path):
    """R12 follow-up: a row filed on the wrong namesake by an older resolver
    is repaired from the model's stored mention, with no re-extraction."""
    s = FactStore(tmp_path / "facts.db")
    s.initialise()
    s.ensure_events()
    docs = {}
    for title in ("Henry McCoy (Earth-616)", "Henry McCoy (Clone) (Earth-616)", "Magneto"):
        docs[title] = s.add_document(
            title=title, url="", page_type="character",
            infobox_template="Character Infobox", lead=f"{title} is a mutant.",
            word_count=5, revid=1, fetched_at="",
        )
    beast = s.add_node("Henry McCoy (Earth-616)", "character", docs["Henry McCoy (Earth-616)"])
    clone = s.add_node("Henry McCoy (Clone) (Earth-616)", "character",
                       docs["Henry McCoy (Clone) (Earth-616)"])
    magneto = s.add_node("Magneto", "character", docs["Magneto"])
    s.add_aliases(beast, ["Beast"])
    s.add_aliases(clone, ["Beast"])
    section = s.add_section(
        document_id=docs["Henry McCoy (Earth-616)"], title="History",
        breadcrumb="Henry McCoy (Earth-616)/History", level=2, ordinal=0,
        text="Beast fought Magneto on the island.", word_count=6,
    )
    chunk = s.add_chunk(
        document_id=docs["Henry McCoy (Earth-616)"], section_id=section,
        parent_id=None, level=2, ordinal=0, doc_title="Henry McCoy (Earth-616)",
        breadcrumb="Henry McCoy (Earth-616)/History", text="Beast fought Magneto.",
    )
    s.link_chunk_nodes(chunk, [clone, magneto])
    s.save_events("Henry McCoy (Earth-616)", [{
        "subject_node": clone, "subject_name": "Henry McCoy (Clone) (Earth-616)",
        "subject_mention": "Beast", "object_node": magneto,
        "object_name": "Magneto", "object_mention": "Magneto",
        "verb": "fought", "section_id": section,
        "quote": "Beast fought Magneto", "temporal": True, "time_rank": 0.0,
    }], revid=1, prompt_version="test", model="test")
    s.commit()
    re_resolve_participants(s)
    got = s.connection.execute(
        "SELECT subject_node, subject_name, subject_mention FROM events").fetchone()
    s.close()
    assert (got["subject_node"], got["subject_name"], got["subject_mention"]) == (
        beast, "Henry McCoy (Earth-616)", "Beast")


def test_a_subpage_never_outranks_its_base_page():
    from scriptengine.ingest.events import pick_candidate

    base = (1, "Quake", None)
    sub = (2, "Quake/Destroyed Earth", None)
    assert pick_candidate([base, sub], "Daisy Johnson") == base
    # A passage that links the subpage keeps it in play (and the link breaks it).
    assert pick_candidate([base, sub], "Daisy Johnson", None, {2}) == sub

"""Link-aware participant resolution (architect 2026-09-28).

The wiki's own wikilinks are pre-resolved edges: a page's `chunk_nodes` set
is the wiki's answer to "which variant of this name does this page mean".
The rule: an ambiguous candidate set with exactly one linked member resolves
deterministically; zero or several linked members stay a counted ambiguity.

Three tests pin it:

* `pick_candidate` carries the link set: it breaks a tie the reality signal
  leaves, inside the reality-narrowed set when reality narrows;
* `re_resolve_participants` repairs stored rows in both directions -- a row
  in the explicit-ambiguous form (NULL node, the candidate list in the name)
  is re-pointed to its page's sole linked candidate, and a row that already
  carries a node is re-pointed when its name maps to a multi-candidate pool;
* the receipt's numbers: the ambiguous tally drops by exactly the rescued
  rows, and `link_broken` counts what the link signal alone did.
"""

from __future__ import annotations

import pytest

from scriptengine.ingest.events import pick_candidate, re_resolve_participants
from scriptengine.stores.facts import FactStore


def test_the_link_signal_breaks_a_set_that_reality_leaves():
    cands = [
        (11, "Wolverine (Earth-616)", None),
        (12, "Hellverine (Demon) (Earth-616)", None),
    ]
    # No signal at all: a counted ambiguity...
    assert pick_candidate(cands, None) == {"ambiguous": cands}
    # ...and exactly one linked member is the wiki's own answer.
    assert pick_candidate(cands, None, {11}) == (11, "Wolverine (Earth-616)", None)
    # Several linked members break nothing, and neither does none.
    assert pick_candidate(cands, None, {11, 12}) == {"ambiguous": cands}
    assert pick_candidate(cands, None, set()) == {"ambiguous": cands}
    # Where reality narrows the set, the link breaks the tie inside it.
    real = [
        (11, "A (Earth-616)", "earth-616"),
        (12, "B (Earth-616)", "earth-616"),
        (13, "C (Tierra-982)", "tierra-982"),
    ]
    assert pick_candidate(real, "earth-616") == {"ambiguous": real[:2]}
    assert pick_candidate(real, "earth-616", {12}) == (12, "B (Earth-616)", "earth-616")


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
      codename, on a page that links to the *other* variant.
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

    # One of the three filed ambiguities is the wiki's own answer.
    assert report["before"]["ambiguous"] == 3
    assert report["after"]["ambiguous"] == 2
    assert rows["X of Swords"] == (wolverine, "Wolverine (Earth-616)")
    # The page that linked both variants, and the one that linked neither,
    # keep their counted ambiguity, names untouched.
    assert rows["Siege"] == (None, "Wolverine (Earth-616) | Hellverine (Demon) (Earth-616)")
    assert rows["Civil War"] == (None, "Wolverine (Earth-616) | Hellverine (Demon) (Earth-616)")
    # The row that already carried a node is re-pointed by the page's link
    # to the variant the page actually means.
    assert rows["Secret Invasion"] == (hellverine, "Hellverine (Demon) (Earth-616)")
    # The link signal alone did two re-pointings: the rescued row and the
    # re-pointed row. What it did is its own number, not the move total.
    assert report["after"]["link_broken"] == 2
    assert report["after"]["moved"] >= 2
"""Speed rewrites of store queries must return what the originals returned.

The D3 Marvel sweep ran at 8.9 s a probe because three store paths scanned
whole tables; each was rewritten to return the identical rows faster. These
pin the identity, not the speed: a rewrite that drifts from the original's
rows or order would silently change every served bundle.
"""

from __future__ import annotations

import random

import pytest

from scriptengine.eval import span_recall as sr
from scriptengine.stores.facts import FactStore


@pytest.fixture()
def graph(tmp_path):
    """A dense random graph: hubs whose second hop spans most of the nodes."""
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    rng = random.Random(5)
    ids = []
    for i in range(300):
        document = None
        if rng.random() < 0.5:
            document = store.add_document(
                title=f"Page {i}", url="", page_type="character",
                infobox_template="", lead="", word_count=0, revid=1,
                fetched_at="")
        ids.append(store.add_node(f"Node {i}", document_id=document))
    for _ in range(1500):
        a, b = rng.choice(ids[:20]), rng.choice(ids)  # hubs among the first 20
        if rng.random() < 0.5:
            a, b = b, a
        store.add_edge(source_id=a, relation="mentions", target_id=b,
                       confidence=rng.choice([0.4, 0.6, 1.0]),
                       provenance="prose", section="History")
    store.commit()
    yield store, ids
    store.close()


def test_limited_neighbours_are_the_head_of_the_full_walk(graph):
    store, ids = graph
    rng = random.Random(9)
    for _ in range(40):
        seeds = rng.sample(ids, rng.choice([1, 2, 5]))
        full = store.neighbours(seeds, depth=2, min_confidence=0.5)
        for limit in (3, 40, 10_000):  # fast path, and the fallback walk
            head = store.neighbours(seeds, depth=2, min_confidence=0.5,
                                    limit=limit)
            assert ([(r["id"], r["hops"]) for r in head]
                    == [(r["id"], r["hops"]) for r in full[:limit]])


def test_chunks_for_nodes_keeps_its_rows_and_order(graph):
    store, ids = graph
    documents = [row["id"] for row in store.connection.execute(
        "SELECT id FROM documents")]
    rng = random.Random(3)
    for n, document in enumerate(documents):
        chunk = store.add_chunk(
            document_id=document, section_id=None, parent_id=None,
            level=rng.choice([0, 2]), ordinal=n, breadcrumb="History",
            text=f"chunk {n}", doc_title=f"doc {n}")
        store.connection.executemany(
            "INSERT OR IGNORE INTO chunk_nodes (chunk_id, node_id) VALUES (?, ?)",
            [(chunk, node) for node in rng.sample(ids, 3)])
    store.commit()
    wanted = rng.sample(ids, 30)
    got = store.chunks_for_nodes(wanted, limit=500)
    placeholders = ",".join("?" * len(wanted))
    expected = store.connection.execute(
        f"SELECT DISTINCT c.* FROM chunks c NOT INDEXED"
        f" JOIN chunk_nodes cn ON cn.chunk_id = c.id"
        f" WHERE cn.node_id IN ({placeholders}) AND c.level = 2"
        f" ORDER BY c.document_id, c.ordinal", wanted).fetchall()
    assert [tuple(r) for r in got] == [tuple(r) for r in expected]
    assert got  # the fixture really exercised the join


def test_fact_keys_memo_sees_a_committed_write(tmp_path):
    store = FactStore(tmp_path / "facts.db")
    store.initialise()
    node = store.add_node("Aoi Todo")
    store.add_fact(node_id=node, key="grade", label="Grade", value="1",
                   citation="")
    store.commit()
    assert [r["key"] for r in store.fact_keys()] == ["grade"]
    other = store.add_node("Yuji Itadori")
    store.add_fact(node_id=other, key="age", label="Age", value="15",
                   citation="")
    # uncommitted: this connection sees the row, so the memo must not answer
    assert {r["key"] for r in store.fact_keys()} == {"grade", "age"}
    store.commit()
    reader = FactStore(tmp_path / "facts.db")
    assert {r["key"] for r in reader.fact_keys()} == {"grade", "age"}
    reader.close()
    store.close()


def test_parallel_sweep_writes_the_serial_rows(tmp_path, monkeypatch):
    """Only the fetch fans out: verdicts and ledger rows match workers=1."""
    import json

    panel = [(f"Page {i % 7}", "History",
              f"Probe sentence number {i} for the parallel test.")
             for i in range(60)]

    def answer(query, series_, timeout, base, door=None):
        n = int(query.split("number ")[1].split()[0])
        if n % 11 == 0:
            raise ConnectionError("server went away")
        title = f"Page {n % 7}" if n % 5 else "Elsewhere"
        text = query if n % 3 else "something else entirely"
        return {"mode": "qa", "truncated": n % 13 == 0,
                "beats": [{"doc_title": title, "text": text}]}

    monkeypatch.setattr(sr, "_ask", answer)
    ledgers = {}
    for workers in (1, 8):
        results = tmp_path / f"sweep_{workers}.jsonl"
        run = sr.recall("demo", panel=panel, results_path=results, door="qa",
                        workers=workers)
        ledgers[workers] = (run["counts"], [
            json.loads(line) for line in
            results.read_text(encoding="utf-8").splitlines() if line])
    assert ledgers[1] == ledgers[8]

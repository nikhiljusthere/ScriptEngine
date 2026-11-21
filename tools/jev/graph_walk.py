"""neo4jev's decision-driven graph walk, over ScriptEngine's SQLite graph instead of Neo4j.

neo4jev's navigator asks one `system_one` call per hop: a `choice` over the
current node's relationships plus a `noul` "is the goal reached?". It takes the
graph as an injected candidate fetcher, so this file supplies one that reads
`facts.db` (`edges` between `nodes`, plus the extracted `relations` table) and
reuses neo4jev's beam search unchanged. Node ids are node names.

Research/eval use only: it is not part of retrieval, which stays model-free.

Run in the neo4jev venv (it needs typesafe-sdk and neo4jev; not ScriptEngine's deps):

    TYPESAFE_BASE_URL=http://127.0.0.1:8018 TYPESAFE_API_KEY=local \\
      ~/tools/jev/venvs/neo4jev/bin/python tools/jev/graph_walk.py \\
      --series opm --start Saitama --goal "a technique Saitama uses" --max-calls 6
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from neo4jev.navigator import NavigatorConfig, NodeContext, run_navigate
from neo4jev.types import FreeTextGoal, NavCandidate, assign_edge_keys
from typesafe_sdk import AsyncTypeSafeClient

ROOT = Path(__file__).resolve().parents[2]
PER_NODE = 60  # well under the 255-option Choice limit; the fetcher owns the cap


def fetcher(db: sqlite3.Connection):
    def label_of(name: str) -> str:
        row = db.execute("SELECT label FROM nodes WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
        return row[0] if row else "unknown"

    def fetch(name: str) -> list[NavCandidate]:
        here = label_of(name)
        out: list[NavCandidate] = []
        for rid, rel, other, olabel, section in db.execute(
            "SELECT e.id, e.relation, t.name, t.label, e.section FROM edges e"
            " JOIN nodes s ON s.id = e.source_id JOIN nodes t ON t.id = e.target_id"
            " WHERE s.name = ? COLLATE NOCASE LIMIT ?", (name, PER_NODE // 2)):
            out.append(NavCandidate("", f"edge:{rid}", rel, {"section": section or ""}, other, olabel, {},
                                    name, here, "out"))
        for rid, rel, other, olabel, section in db.execute(
            "SELECT e.id, e.relation, s.name, s.label, e.section FROM edges e"
            " JOIN nodes s ON s.id = e.source_id JOIN nodes t ON t.id = e.target_id"
            " WHERE t.name = ? COLLATE NOCASE LIMIT ?", (name, PER_NODE // 4)):
            out.append(NavCandidate("", f"edge:{rid}", rel, {"section": section or ""}, name, here, {},
                                    other, olabel, "in"))
        try:
            rows = db.execute("SELECT rowid, relation, other, quote FROM relations"
                              " WHERE character = ? COLLATE NOCASE LIMIT ?", (name, PER_NODE // 4)).fetchall()
        except sqlite3.OperationalError:  # a store extracted before relations existed
            rows = []
        for rid, rel, other, quote in rows:
            out.append(NavCandidate("", f"rel:{rid}", rel, {"quote": (quote or "")[:200]}, other, label_of(other),
                                    {}, name, here, "out"))
        return assign_edge_keys(out[:PER_NODE])

    return fetch


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", required=True)
    ap.add_argument("--start", required=True, help="node name to start from")
    ap.add_argument("--goal", required=True, help="free-text goal")
    ap.add_argument("--max-calls", type=int, default=6)
    ap.add_argument("--max-depth", type=int, default=2)
    args = ap.parse_args(argv)

    db = sqlite3.connect(f"file:{ROOT / 'series' / args.series / 'facts.db'}?mode=ro", uri=True)
    fetch = fetcher(db)
    start = db.execute("SELECT name, label FROM nodes WHERE name = ? COLLATE NOCASE", (args.start,)).fetchone()
    if not start:
        raise SystemExit(f"no node named {args.start!r} in {args.series}")
    result = run_navigate(
        AsyncTypeSafeClient(timeout=180.0),  # TYPESAFE_BASE_URL / TYPESAFE_API_KEY from the environment; CPU lane is slow
        fetch,
        NodeContext(element_id=start[0], label=start[1]),
        FreeTextGoal(args.goal),
        config=NavigatorConfig(max_calls=args.max_calls, max_depth=args.max_depth, beam_width=2, top_k=2),
    )
    paths = [{
        "log_prob": round(p.cumulative_log_prob, 3),
        "terminated": str(p.terminated_reason),
        "hops": [{"from": s.node_id, "via": [f"{c.rel_type} -> {c.next_element_id}" for c in s.chosen],
                  "goal_noul": s.noul} for s in p.steps],
    } for p in result.paths]
    print(json.dumps({"start": start[0], "goal": args.goal, "paths": paths}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""The mechanical event gates (plan/JJK_100_PLAN.md §GATES), over a stored
events table. Offline, read-only, no model.

    python tools/events_gates.py --series jjk [--db PATH] [--json OUT]

G1 quote carried in ONE grid window of the passage the row claims (the
   windowing-100 council's window-level G1, 2026-09-30: a quote verbatim in
   the section but absent from every window a read carries must not be
   attributed to sentences that don't cover it)
G2 verb in eventive_verbs(store) for this wiki
G3 subject == object only for a self-directed verb, or a quote that says so
   ("himself", "herself", ...) -- never for arrived/departed
G4 arrived/departed: the object is a place or a group -- a node whose page
   type is one the wiki declares under `events: place_types:` in its
   overrides. A wiki that declares none reports G4 as undeclared, never a
   guessed pass.
G5 the quote is at least 20 characters. Soft: `quoted_in` already refuses
   under 12, and "Bayer takes on Gojo" is a real event at 19, so G5 is
   reported and never used as a drop.
G6 both participants resolved to one node (an ambiguous or unresolved end
   is a counted class, not a failure of the row)
G7 the row was written under the current PROMPT_VERSION (a stale row is a
   row the re-extraction did not replace: a failed or out-of-scope page)

CLEAN = passes G1-G4 and G7. A row fails a gate with a cause; nothing here
deletes anything.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scriptengine.ingest.events import (  # noqa: E402
    PROMPT_VERSION,
    _SELF_VERBS,
    _events_overrides,
    _row_passage_text,
    eventive_verbs,
)
from scriptengine.ingest.windows import quote_window  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402

# A quote that states the act was self-directed makes subject == object legal
# ("Toji kills himself"). The pronoun is the passage's own word, not a guess.
_REFLEXIVE = re.compile(
    r"\b(himself|herself|itself|themselves|themself|oneself|own life)\b", re.I
)
_MOVEMENT = {"arrived", "departed"}


def gate_rows(store: FactStore) -> tuple[list[dict], dict]:
    conn = store.connection
    verbs = eventive_verbs(store)
    declared = _events_overrides(store).get("place_types")
    place_types = {str(t) for t in declared} if declared else None
    page_type = {
        int(r[0]): r[1]
        for r in conn.execute(
            "SELECT n.id, d.page_type FROM nodes n"
            " JOIN documents d ON d.id = n.document_id"
        )
    }
    out = []
    for row in conn.execute("SELECT rowid AS rid, * FROM events"):
        fails = []
        text = _row_passage_text(store, row)
        # G1 at the window level (windowing-100 council 2026-09-30): the
        # quote must sit inside one grid window of the passage -- the span
        # a read actually carries -- not merely somewhere in it. The
        # builder's labels feed the window id only; containment depends on
        # the passage's own grid.
        if quote_window(
            row["doc_title"] or "", "", text, row["quote"] or ""
        ) is None:
            fails.append("G1")
        if row["verb"] not in verbs:
            fails.append("G2")
        s_end = row["subject_node"] if row["subject_node"] is not None else row["subject_name"]
        o_end = row["object_node"] if row["object_node"] is not None else row["object_name"]
        self_row = s_end == o_end
        # A movement's object is a place, so a self-movement is never legal,
        # reflexive or not ("Higuruma leaves and shuts the door behind himself").
        reflexive = row["verb"] not in _MOVEMENT and _REFLEXIVE.search(row["quote"] or "")
        if self_row and row["verb"] not in _SELF_VERBS and not reflexive:
            fails.append("G3")
        g4 = None
        if row["verb"] in _MOVEMENT:
            if place_types is None:
                g4 = "undeclared"
            else:
                obj_type = page_type.get(row["object_node"]) if row["object_node"] is not None else None
                g4 = "pass" if (not self_row and obj_type in place_types) else "fail"
                if g4 == "fail":
                    fails.append("G4")
        soft = []
        if len((row["quote"] or "").strip()) < 20:
            soft.append("G5")
        if row["subject_node"] is None or row["object_node"] is None:
            soft.append("G6")
        if row["prompt_version"] != PROMPT_VERSION:
            fails.append("G7")
        out.append({
            "rid": row["rid"], "doc": row["doc_title"], "verb": row["verb"],
            "subject": row["subject_name"], "object": row["object_name"],
            "quote": row["quote"], "fails": fails, "soft": soft, "g4": g4,
            "self": self_row, "verified": row["verified"],
            "prompt_version": row["prompt_version"],
        })
    tally: dict = {"rows": len(out), "place_types": sorted(place_types) if place_types else None}
    for gate in ("G1", "G2", "G3", "G4", "G7"):
        tally[gate] = sum(gate in r["fails"] for r in out)
    for gate in ("G5", "G6"):
        tally[gate + "_soft"] = sum(gate in r["soft"] for r in out)
    tally["G4_na"] = sum(r["g4"] is None for r in out)
    tally["G4_undeclared"] = sum(r["g4"] == "undeclared" for r in out)
    tally["clean"] = sum(not r["fails"] for r in out)
    tally["self_by_verb"] = dict(collections.Counter(r["verb"] for r in out if r["self"]))
    tally["verified"] = dict(collections.Counter(str(r["verified"]) for r in out))
    tally["prompt_versions"] = dict(collections.Counter(r["prompt_version"] for r in out))
    tally["verbs"] = dict(collections.Counter(r["verb"] for r in out))
    return out, tally


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", required=True)
    ap.add_argument("--db", help="a facts.db other than series/<name>/facts.db")
    ap.add_argument("--json", help="write per-row results here")
    args = ap.parse_args()
    db = Path(args.db) if args.db else ROOT / "series" / args.series / "facts.db"
    with FactStore(db) as store:
        rows, tally = gate_rows(store)
    print(json.dumps(tally, indent=1))
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=0), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

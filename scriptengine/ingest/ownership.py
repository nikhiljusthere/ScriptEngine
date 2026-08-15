"""Ownership a wiki states in a sentence rather than in a field.

`owned_by` walks `user`/`owner` infobox edges, which is how One Punch Man and
Dragon Ball record who has what. Bleach does not: its technique pages carry no
`user` field at all and say it in the first line instead.

    Some no mai, Tsukishiro   "is a technique of Rukia Kuchiki's Zanpakutō,
                               Sode no Shirayuki"
    Chain                     "is a Zanpakutō technique of Ichigo Kurosaki's
                               Zangetsu"
    Shūkei: Hakuteiken        "is a technique of Byakuya Kuchiki's Bankai,
                               Senbonzakura Kageyoshi"

Measured over the 488 technique pages on that wiki, 96 name a character this
way and every one of them was unreachable: no edge, no category tying it to the
person, and nothing in the character's own ability prose. `Every dance of
Rukia's Shikai Sode no Shirayuki` scored zero with all three dances sitting on
their own pages saying whose they are.

This reads that sentence and writes the edge the wiki did not. Deliberately not
a model: the sentence is formulaic, a regular expression can be held to it, and
a rule that fires 96 times is worth more when it is the same rule every time.

**The edge is written under its own relation.** `stated user` is not `user`, so
what the wiki declared and what was derived from prose stay distinguishable —
if this rule is ever wrong, the damage is visible and removable.

`index` rebuilds the graph, so this runs after it.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from scriptengine.config import SeriesPaths, load_overrides
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

# The relation these edges are written under. Kept apart from `user` so a
# derived claim is never mistaken for one the wiki made in a field.
STATED_USER = "stated user"

# "is a technique of X", "is a Zanpakutō technique of X", "is a technique used
# by X". The kind word is allowed to carry qualifiers -- `Zanpakutō`, `Shunpo`,
# `advanced` -- but the sentence must still say *of* or *used by* somebody, and
# the name must start where a name starts. Anything looser matched
# "is a technique of the Gotei 13" and similar.
_STATES_OWNER = re.compile(
    r"\bis an?\s+[\w'’\-À-ɏ]{0,20}(?:\s+[\w'’\-À-ɏ]{0,20}){0,2}?"
    r"\b(?:technique|ability|power|move|attack)s?\s+(?:of|used by)\s+"
    r"([A-Z][\w'’\-À-ɏ]*(?:\s+[A-Z][\w'’\-À-ɏ]*){0,3})",
)


# A second shape: the page describes an occasion instead of declaring an owner.
# "When used by Kenpachi Zaraki, this technique was sufficiently powerful to
# overpower ..." attributes it as surely as "is a technique of" does, and Bleach
# writes it both ways.
_USED_BY = re.compile(
    r"(?:[Ww]hen|[Aa]lso|[Ll]ater)\s+used by\s+"
    r"([A-Z][\w'’\-À-ɏ]*(?:\s+[A-Z][\w'’\-À-ɏ]*){0,3})",
)


def stated_owner(text: str) -> str:
    """The character a technique page's lead says it belongs to, or ``""``."""
    match = _STATES_OWNER.search(text or "") or _USED_BY.search(text or "")
    if not match:
        return ""
    # `Rukia Kuchiki's Zanpakutō` -- the owner is the person, not the sword,
    # and the capture runs on through the possessive because `Zanpakutō` is
    # capitalised too. Cut at the apostrophe.
    return re.split(r"['’]s", match.group(1))[0].strip()


def derive(paths: SeriesPaths, limit: int = 0) -> dict[str, Any]:
    """Write a `stated user` edge for every technique page naming its owner."""
    from scriptengine.retrieve import semantics as ontology

    overrides = load_overrides(paths)
    report = {"considered": 0, "stated": 0, "written": 0, "unknown_owner": 0}
    with FactStore(paths.facts_db) as store:
        pages = [
            row["title"]
            for row in store.connection.execute(
                "SELECT title, page_type FROM documents"
            )
            if ontology.type_from_page_type(row["page_type"], overrides)
            == ontology.TECHNIQUE
        ]
        if limit:
            pages = pages[:limit]
        report["considered"] = len(pages)

        for title in pages:
            lead = " ".join(
                row["text"]
                for row in store.connection.execute(
                    "SELECT c.text FROM chunks c JOIN documents d"
                    " ON c.document_id = d.id"
                    " WHERE d.title = ? COLLATE NOCASE ORDER BY c.ordinal LIMIT 2",
                    (title,),
                )
            )
            owner = stated_owner(lead)
            if not owner:
                continue
            report["stated"] += 1
            # The owner has to be somebody this wiki has, and a character --
            # `is a technique of the Quincy` names a race, not a person.
            node = store.node_by_name(owner)
            if node is None or ontology.semantic_type(
                store, node["name"], overrides
            ) != ontology.CHARACTER:
                report["unknown_owner"] += 1
                logger.info("no character named %r for %r", owner, title)
                continue
            source = store.node_by_name(title)
            if source is None:
                continue
            existing = store.connection.execute(
                "SELECT 1 FROM edges WHERE source_id = ? AND target_id = ?"
                "   AND relation = ? LIMIT 1",
                (source["id"], node["id"], STATED_USER),
            ).fetchone()
            if existing:
                continue
            store.connection.execute(
                "INSERT INTO edges (source_id, target_id, relation) VALUES (?, ?, ?)",
                (source["id"], node["id"], STATED_USER),
            )
            report["written"] += 1
        store.connection.commit()
    return report

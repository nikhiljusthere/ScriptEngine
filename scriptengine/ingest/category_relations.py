"""Relations a wiki states in a category, not in a field. (L5, plan §C2)

`member_of` and `created_by` have infobox fields, but the wiki also files
members under their group and works under their creators as *categories*:
`Hydra (Earth-616)/Members`, `Stan Lee/Creator`, `Secret Invasion casualties`,
`2009 Character Debuts`. A character in `Hydra (Earth-616)/Members` was a
Hydra member even when the infobox says nothing, and a comic in `Stan
Lee/Creator` has a creator the page's own prose may not name. The category is
the wiki's own statement of the relation; this pass reads the statement and
writes the edge it did not.

The grammar is declared per series in `overrides.yaml`, because the category
language is a wiki convention, not an engine fact. Marvel files by suffix
(`X/Members`, `X/Creator`), the MCU wiki embeds the target in the name
(`X Crew Members`), and most wikis do neither. What is generic is the
mechanism:

    category_relations:
      - {pattern: "^(.+)/Members$", relation: member_of,
         target: 1, contradicts: affiliation}
      - {pattern: "^(\\d{4}) Character Debuts$", relation: debuted_year,
         value: 1}

* `pattern`  -- a regular expression matched against the category name.
* `target`   -- capture group that names the *other* node. Resolved against
                the store's nodes, then its aliases. An exact node name is
                confidence 1.0, an alias hit 0.9; an unresolved capture is
                counted and skipped, never invented.
* `value`    -- capture group that is a property, not a node. Written to
                `facts` under `relation`, the category as citation.
* `kind`     -- a qualifier recorded in the provenance, e.g. `;kind=casualty`
                on `event_participant` edges.
* `contradicts` -- the infobox fact key this relation can contradict. The
                audit samples category edges against it: a category edge the
                page's own field denies is a finding, not a keep.

The edges are written under their provenance, `category:<name>`, so what the
wiki filed and what a field declared stay distinguishable, the way `stated
user` (ingest/ownership.py) keeps its prose-derived edges removable.

`index` rebuilds the graph, so this runs after it. It is idempotent: one edge
per (subject, relation, target) -- two categories stating the same relation
collapse to the stronger confidence -- and the fact existence check make a
second run a no-op that only counts.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from scriptengine.config import SeriesPaths, load_overrides
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

# Exact node names outrank aliases, and the two confidences are the only two
# the mechanism knows: the store said the name, or the store said the name's
# alias. Anything weaker (fuzzy, cross-wiki) is a different, unshipped rule.
_EXACT = 1.0
_ALIAS = 0.9


@dataclass(frozen=True)
class _Rule:
    pattern: str
    relation: str
    target: int | None
    value: int | None
    kind: str | None
    contradicts: str | None
    rx: re.Pattern

    @classmethod
    def parse(cls, entry: Any) -> "_Rule":
        if not isinstance(entry, dict) or "pattern" not in entry or "relation" not in entry:
            raise ValueError(
                f"a category_relations entry needs `pattern` and `relation`: {entry!r}"
            )
        target = entry.get("target")
        value = entry.get("value")
        if target is not None and not isinstance(target, int):
            raise ValueError(f"`target` names a capture group, got {target!r}")
        if value is not None and not isinstance(value, int):
            raise ValueError(f"`value` names a capture group, got {value!r}")
        return cls(
            pattern=str(entry["pattern"]),
            relation=str(entry["relation"]),
            target=target,
            value=value,
            kind=entry.get("kind"),
            contradicts=entry.get("contradicts"),
            rx=re.compile(str(entry["pattern"])),
        )


def _rules(overrides: dict[str, Any]) -> list[_Rule]:
    raw = overrides.get("category_relations") or []
    if not isinstance(raw, list):
        raise ValueError(f"`category_relations` must be a list, got {type(raw).__name__}")
    return [_Rule.parse(entry) for entry in raw]


def _resolve_map(store: FactStore) -> dict[str, tuple[int, float]]:
    """Name (casefolded) -> (node_id, confidence), aliases first, names on top."""
    resolve: dict[str, tuple[int, float]] = {}
    for alias, node_id in store.connection.execute("SELECT alias, node_id FROM aliases"):
        resolve[alias.casefold()] = (node_id, _ALIAS)
    for name, node_id in store.connection.execute(
        "SELECT name, id FROM nodes WHERE name IS NOT NULL"
    ):
        resolve[name.casefold()] = (node_id, _EXACT)
    return resolve


def derive(paths: SeriesPaths, limit: int = 0) -> dict[str, Any]:
    """Write the edges and facts the series' `category_relations:` declares."""
    rules = _rules(load_overrides(paths))
    report: dict[str, Any] = {
        "rules": len(rules),
        "considered": 0,
        "matched": 0,
        "edges_written": 0,
        "facts_written": 0,
        "already": 0,
        "unresolved": 0,
        "no_subject": 0,
    }
    if not rules:
        return report

    with FactStore(paths.facts_db) as store:
        resolve = _resolve_map(store)
        # The subject is the document's own node: its id alone, since the
        # confidence on the edge is about the *target* resolution.
        subject_ids = {name: node_id for name, (node_id, _c) in resolve.items()}
        doc_titles = {
            row[0]: row[1].casefold()
            for row in store.connection.execute("SELECT id, title FROM documents")
        }

        # A category's captures are a function of the category *name*, so the
        # regex runs once per distinct name (Marvel has 2.5M rows but 212k
        # names) and the document walk is a dict lookup.
        name_plans: dict[str, list[tuple[_Rule, str | None, str | None]]] = {}
        for category in [
            row[0]
            for row in store.connection.execute("SELECT DISTINCT category FROM categories")
        ]:
            plan = []
            for rule in rules:
                match = rule.rx.search(category)
                if not match:
                    continue
                captures = match.groups()
                if (
                    rule.target is not None
                    and (rule.target > len(captures) or captures[rule.target - 1] is None)
                ):
                    # The pattern matched but the target group did not: this
                    # name states the relation but names no one, so there is
                    # nothing to resolve.
                    continue
                if (
                    rule.value is not None
                    and (rule.value > len(captures) or captures[rule.value - 1] is None)
                ):
                    continue
                target = captures[rule.target - 1] if rule.target is not None else None
                value = captures[rule.value - 1] if rule.value is not None else None
                plan.append((rule, target, value))
            if plan:
                name_plans[category] = plan

        # Two categories can state the same relation with the same target
        # (`Hydra (Earth-616)/Members` and `Hydra/Members` both file doc 1
        # under Hydra). The graph keeps one edge per (subject, relation,
        # target), at the stronger confidence, so the pass stays idempotent
        # under the table's own `UNIQUE` shape as well as re-runs.
        pending: dict[tuple[int, str, int], tuple[float, str]] = {}
        rows = store.connection.execute(
            "SELECT c.document_id, c.category FROM categories c"
        )
        for document_id, category in rows:
            if limit and report["considered"] >= limit:
                break
            plan = name_plans.get(category)
            if plan is None:
                continue
            report["considered"] += 1
            subject = subject_ids.get(doc_titles.get(document_id, ""))
            if subject is None:
                report["no_subject"] += 1
                continue
            report["matched"] += 1
            for rule, target, value in plan:
                if target is not None:
                    hit = resolve.get(target.casefold())
                    if hit is None:
                        report["unresolved"] += 1
                        logger.info(
                            "no node named %r (category %r)", target, category
                        )
                        continue
                    target_id, confidence = hit
                    provenance = f"category:{category}"
                    if rule.kind is not None:
                        provenance += f";kind={rule.kind}"
                    key = (subject, rule.relation, target_id)
                    current = pending.get(key)
                    if current is None or confidence > current[0]:
                        pending[key] = (confidence, provenance)
                if value is not None:
                    citation = f"category:{category}"
                    cursor = store.connection.execute(
                        "INSERT INTO facts (node_id, key, value, citation)"
                        " SELECT ?, ?, ?, ? WHERE NOT EXISTS"
                        " (SELECT 1 FROM facts WHERE node_id = ? AND key = ? AND value = ?)",
                        (subject, rule.relation, value, citation,
                         subject, rule.relation, value),
                    )
                    if cursor.rowcount:
                        report["facts_written"] += 1
                    else:
                        report["already"] += 1
        for (subject, relation, target_id), (confidence, provenance) in pending.items():
            cursor = store.connection.execute(
                "INSERT INTO edges (source_id, target_id, relation, confidence, provenance)"
                " SELECT ?, ?, ?, ?, ? WHERE NOT EXISTS"
                " (SELECT 1 FROM edges"
                "  WHERE source_id = ? AND target_id = ? AND relation = ?)",
                (subject, target_id, relation, confidence, provenance,
                 subject, target_id, relation),
            )
            if cursor.rowcount:
                report["edges_written"] += 1
            else:
                report["already"] += 1
        store.connection.commit()
    return report


def audit(paths: SeriesPaths, sample: int = 200) -> dict[str, Any]:
    """Sample the category edges against the infobox field they can contradict.

    The plan's gate: an edge the page's own field denies is a finding, not a
    keep. Sampling keeps the check a receipt instead of a 100k-row rewrite,
    and the sample is deterministic (a stride over edge ids), so re-running
    the gate re-checks the same pages.
    """
    rules = _rules(load_overrides(paths))
    by_relation = {rule.relation: rule for rule in rules if rule.contradicts}
    report: dict[str, Any] = {
        "sampled": 0,
        "auditable": 0,
        "unauditable": 0,
        "consistent": 0,
        "contradictions": [],
    }
    if not by_relation:
        return report

    with FactStore(paths.facts_db) as store:
        total = store.connection.execute(
            "SELECT COUNT(*) FROM edges WHERE provenance LIKE 'category:%'"
        ).fetchone()[0]
        if total == 0:
            return report
        stride = max(total // sample, 1)
        edges = store.connection.execute(
            "SELECT e.id, e.source_id, e.relation, t.name, e.provenance"
            " FROM edges e JOIN nodes t ON t.id = e.target_id"
            " WHERE e.provenance LIKE 'category:%' AND e.id % ? = 0"
            " ORDER BY e.id LIMIT ?",
            (stride, sample),
        ).fetchall()

        for _edge_id, source_id, relation, target_name, provenance in edges:
            report["sampled"] += 1
            rule = by_relation.get(relation)
            if rule is None:
                report["unauditable"] += 1
                continue
            report["auditable"] += 1
            field = store.connection.execute(
                "SELECT value FROM facts WHERE node_id = ? AND key = ?",
                (source_id, rule.contradicts),
            ).fetchone()
            if field is None or not field[0].strip():
                # No counter-evidence: nothing on the page denies the category.
                report["consistent"] += 1
                continue
            parts = {
                _normalize(part)
                for part in re.split(r"[;]| and ", field[0], flags=re.I)
                if _normalize(part)
            }
            if _normalize(target_name) in parts:
                report["consistent"] += 1
            else:
                report["contradictions"].append(
                    {
                        "source_id": source_id,
                        "relation": relation,
                        "category": target_name,
                        "field": field[0],
                        "provenance": provenance,
                    }
                )
    return report


def _normalize(name: str) -> str:
    """Casefold and drop the Earth-suffix the wiki files by (`Hydra (Earth-616)`)."""
    return re.sub(r"\s*\(earth-\d+\)\s*$", "", name, flags=re.I).strip().casefold()
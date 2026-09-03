"""What is actually in the engine, generated from the engine.

Every series brings its own wiki, its own citation grammar, its own roster
registry and its own sourcing rate, and there was no single place that said so.
A hand-written table would be wrong within a week, so this one is rebuilt from the
stores on demand, so it is either current or obviously absent.

Nothing here recomputes anything expensive. The counts come out of SQLite, the
sourcing percentages out of the audit report each series already writes, and the
rosters out of the same `load_rosters` the retriever uses.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from scriptengine.config import Settings, get_settings, load_overrides, series_paths


def collect(settings: Settings | None = None) -> list[dict[str, Any]]:
    """One record per indexed series."""
    from scriptengine.retrieve.citations import EpisodeIndex, locator_from_title
    from scriptengine.retrieve.roster import _declared_members, load_rosters
    from scriptengine.stores.facts import FactStore
    from scriptengine.stores.vectors import VectorStore

    settings = settings or get_settings()
    root = settings.series_root
    records: list[dict[str, Any]] = []

    for path in sorted(root.iterdir()) if root.exists() else []:
        if not path.is_dir():
            continue
        paths = series_paths(path.name)
        if not paths.facts_db.exists():
            continue

        record: dict[str, Any] = {"series": path.name}
        record.update(_manifest(paths))
        record.update(_audit(paths))

        with FactStore(paths.facts_db) as store:
            stats = store.stats()
            record.update(
                {
                    "documents": stats["documents"],
                    "facts": stats["facts"],
                    "edges": stats["edges"],
                    "chunks": stats["chunks"],
                    "types": len(stats.get("types") or {}),
                    "episode_map": len(EpisodeIndex.from_store(store)),
                }
            )
            rosters = []
            for definition in load_rosters(load_overrides(paths)):
                if definition.groups:
                    size = sum(
                        len(store.documents_in_category(c, limit=400))
                        for c in definition.groups.values()
                    )
                    rosters.append(
                        {"name": definition.name, "members": size,
                         "groups": len(definition.groups)}
                    )
                else:
                    rosters.append(
                        {"name": definition.name,
                         "members": len(_declared_members(store, definition)),
                         "groups": 0}
                    )
            record["rosters"] = rosters
            # The other way a claim gets a locator. A wiki that never cites its
            # own prose can still be sourced when its story is written one page
            # per instalment, because the page title *is* the citation.
            record["instalments"] = sum(
                1
                for row in store.connection.execute("SELECT title FROM documents")
                if locator_from_title(row["title"])
            )

        record["vectors"] = 0
        if paths.vectors.exists():
            with VectorStore(paths.vectors) as vectors:
                record["vectors"] = vectors.count()

        records.append(record)

    return records


def _manifest(paths) -> dict[str, Any]:
    if not paths.manifest.exists():
        return {"wiki": "", "enumerated": 0, "skipped": 0}
    try:
        data = json.loads(paths.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"wiki": "", "enumerated": 0, "skipped": 0}
    return {
        "wiki": data.get("wiki", ""),
        "enumerated": data.get("pages_enumerated", 0),
        "skipped": data.get("pages_skipped", 0),
        "crawled_at": (data.get("crawled_at") or "")[:10],
    }


def _audit(paths) -> dict[str, Any]:
    """Sourcing and typing, from the report `cli audit` already wrote."""
    report = paths.audit / "report.json"
    if not report.exists():
        return {}
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    sourcing = data.get("sourcing") or {}
    return {
        "typed": (data.get("coverage") or {}).get("typed"),
        "with_chapter": sourcing.get("with_chapter"),
        "with_episode": sourcing.get("with_episode"),
        "cited_directly": sourcing.get("cited_directly"),
        "audited": bool(data),
    }


def render(records: list[dict[str, Any]]) -> str:
    """The catalogue as markdown."""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total_pages = sum(r["documents"] for r in records)
    total_rosters = sum(len(r["rosters"]) for r in records)

    lines = [
        "# Catalogue",
        "",
        f"What is in the engine, as of {stamp}. Generated by",
        "`python -m scriptengine.cli catalogue`. Do not edit by hand, it is",
        "rebuilt from the stores and any edit will be overwritten.",
        "",
        f"**{len(records)} series, {total_pages:,} pages, "
        f"{total_rosters} declared enumeration sets.**",
        "",
        "## Series",
        "",
        "| series | wiki | pages | typed | prose → chapter | → episode | "
        "instalment pages | rosters |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in sorted(records, key=lambda r: -r["documents"]):
        host = (r.get("wiki") or "").replace("https://", "").replace(".fandom.com", "")
        lines.append(
            f"| `{r['series']}` | {host} | {r['documents']:,} | "
            f"{_pct(r.get('typed'))} | {_pct(r.get('with_chapter'))} | "
            f"{_pct(r.get('with_episode'))} | {r.get('instalments', 0):,} | "
            f"{len(r['rosters'])} |"
        )

    lines += [
        "",
        "`prose → chapter` is the share of sentences carrying an inline reference.",
        "`instalment pages` is the other route: a wiki that never cites its own",
        "prose can still be sourced when its story is written one page per",
        "chapter or episode, because the page title is the citation. A series",
        "with a low percentage and a high instalment count is still sourceable;",
        "one with both at zero is not, and that is a fact about the wiki rather",
        "than about the pipeline. Wikis that title chapter pages by name rather",
        "than by number show zero here even though they have chapters.",
        "",
        "## Stores",
        "",
        "| series | facts | edges | chunks | vectors | chapter→episode map |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in sorted(records, key=lambda r: -r["documents"]):
        lines.append(
            f"| `{r['series']}` | {r['facts']:,} | {r['edges']:,} | "
            f"{r['chunks']:,} | {r['vectors']:,} | {r['episode_map']:,} |"
        )

    lines += ["", "## Declared enumeration sets", ""]
    for r in sorted(records, key=lambda r: r["series"]):
        if not r["rosters"]:
            continue
        lines.append(f"### `{r['series']}`")
        lines.append("")
        for roster in sorted(r["rosters"], key=lambda x: -x["members"]):
            shape = (
                f"{roster['members']:,} members across {roster['groups']} groups"
                if roster["groups"]
                else f"{roster['members']:,} members"
            )
            lines.append(f"- **{roster['name']}**: {shape}")
        lines.append("")

    return "\n".join(lines) + "\n"


def _pct(value: Any) -> str:
    """`n/a` means not measured. Zero means measured, and zero.

    Berserk really does source 0% of its prose, because its wiki cites cover art
    rather than instalments. Rendering that as "n/a" would hide a fact worth
    knowing behind something that looks like missing data.
    """
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.0f}%"

"""The HTTP service.

    python -m scriptengine.api.main

Bound to localhost by default. The Electron shell and ComfyUI are both local,
and a wiki index is not something to expose to a network by accident.

The previous project's UI called endpoints on this port that were never
written, so every button on its dashboard was dead.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from scriptengine.api.context import build_context, render_prompt
from scriptengine.config import get_settings, series_paths
from scriptengine.index.build import index_status
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ScriptEngine",
    description=(
        "A universal knowledge engine over Fandom wikis. Serves ordered, cited, "
        "structured context to whatever writes your scripts."
    ),
    version="0.1.0",
)


# ── requests ─────────────────────────────────────────────────────────────────


class ContextRequest(BaseModel):
    series: str
    query: str
    mode: Literal["qa", "narrative"] = "qa"
    token_budget: int = Field(default=6000, ge=200, le=100_000)
    as_prompt: bool = Field(
        default=False, description="Also return the bundle rendered as plain text."
    )


class SearchRequest(BaseModel):
    series: str
    query: str
    top_k: int = Field(default=8, ge=1, le=50)
    rerank: bool = True


# ── helpers ──────────────────────────────────────────────────────────────────


def _paths_or_404(series: str):
    try:
        paths = series_paths(series)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    if not paths.facts_db.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                f"Series {series!r} is not indexed. Run: "
                f"python -m scriptengine.cli index --series {series}"
            ),
        )
    return paths


# ── endpoints ────────────────────────────────────────────────────────────────


@app.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    root = settings.series_root
    series = (
        sorted(path.name for path in root.iterdir() if path.is_dir())
        if root.exists()
        else []
    )
    return {
        "status": "ok",
        "version": app.version,
        "device": settings.resolved_device(),
        "embed_model": settings.embed_model,
        "rerank_model": settings.rerank_model,
        "series": series,
    }


@app.get("/series")
def list_series() -> dict[str, Any]:
    settings = get_settings()
    root = settings.series_root
    if not root.exists():
        return {"series": []}

    entries = []
    for path in sorted(root.iterdir()):
        if path.is_dir():
            entries.append(index_status(series_paths(path.name)))
    return {"series": entries}


@app.post("/context")
def context(request: ContextRequest) -> dict[str, Any]:
    """The endpoint a script-writing model calls.

    Returns passages in the right order — narrative order when asked for it,
    not similarity order — with the facts behind them and a citation each.
    """
    paths = _paths_or_404(request.series)
    bundle = build_context(
        paths, request.query, mode=request.mode, token_budget=request.token_budget
    )
    if request.as_prompt:
        bundle["prompt"] = render_prompt(bundle)
    return bundle


@app.post("/search")
def search(request: SearchRequest) -> dict[str, Any]:
    from scriptengine.retrieve.hybrid import HybridRetriever

    paths = _paths_or_404(request.series)
    with HybridRetriever(paths) as retriever:
        result = retriever.search(
            request.query, top_k=request.top_k, rerank=request.rerank
        )
        retriever.release_models()
    return result.as_dict()


@app.get("/facts/{series}/{entity}")
def facts(series: str, entity: str) -> dict[str, Any]:
    """Exact structured facts for one entity.

    A lookup, not a search. Infobox parameters are stored as facts rather than
    flattened into prose, so a character's grade or debut chapter is answered
    exactly instead of retrieved and hoped about.
    """
    paths = _paths_or_404(series)
    with FactStore(paths.facts_db) as store:
        node = store.node_by_name(entity)
        if node is None:
            matches = store.link_entities(entity)
            if not matches:
                raise HTTPException(
                    status_code=404, detail=f"No entity matching {entity!r} in {series!r}."
                )
            node = matches[0]

        rows = store.facts_for(node["name"])
        relations = store.edges_for([int(node["id"])], min_confidence=0.9, limit=60)
        aliases = store.connection.execute(
            "SELECT alias FROM aliases WHERE node_id = ?", (int(node["id"]),)
        ).fetchall()

        return {
            "series": series,
            "entity": node["name"],
            "type": node["label"],
            "aliases": sorted(row["alias"] for row in aliases),
            "facts": [
                {
                    "key": row["key"],
                    "field": row["label"] or row["key"],
                    "value": row["value"],
                    "citation": row["citation"],
                }
                for row in rows
            ],
            "relations": [
                {
                    "source": row["source"],
                    "relation": row["relation"],
                    "target": row["target"],
                }
                for row in relations
            ],
        }


@app.get("/timeline/{series}/{subject}")
def timeline(series: str, subject: str, max_beats: int = 40) -> dict[str, Any]:
    """An event as ordered beats."""
    from scriptengine.retrieve.narrative import NarrativeRetriever

    paths = _paths_or_404(series)
    with NarrativeRetriever(paths) as retriever:
        narrative = retriever.timeline(subject, max_beats=max_beats)

    if not narrative.beats:
        raise HTTPException(
            status_code=404, detail=f"No narrative found for {subject!r} in {series!r}."
        )
    return narrative.as_dict()


def main() -> None:
    import uvicorn

    settings = get_settings()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, log_level="info")


if __name__ == "__main__":
    main()

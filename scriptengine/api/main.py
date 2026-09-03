"""The HTTP service.

    python -m scriptengine.api.main

Bound to localhost by default. The Electron shell and ComfyUI are both local,
and a wiki index is not something to expose to a network by accident.

The previous project's UI called endpoints on this port that were never
written, so every button on its dashboard was dead.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from scriptengine.api.context import build_context, render_prompt
from scriptengine.config import get_settings, series_paths
from scriptengine.index.build import index_status
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

# Import time is process start for this purpose: the module holding the code
# being measured is loaded exactly once, and reloading it is what a restart
# does. Reported by `/health` so a measurement can refuse a stale server.
_STARTED = datetime.now(timezone.utc).isoformat(timespec="seconds")

app = FastAPI(
    title="ScriptEngine",
    description=(
        "A universal knowledge engine over Fandom wikis. Serves ordered, cited, "
        "structured context to whatever writes your scripts."
    ),
    version="0.1.0",
)


@app.on_event("startup")
def _sweep_idle_models() -> None:
    """Return the GPU to ComfyUI once the models have gone idle.

    The models now stay resident between requests, which is what makes a second
    query fast. Something still has to free them when the server goes quiet, and
    it cannot be the request path -- an idle server serves no requests. A daemon
    thread checks every 30s and unloads whatever has passed
    `model_idle_unload_seconds`.
    """
    import threading
    import time

    from scriptengine.index.embedder import sweep_idle

    settings = get_settings()
    if not settings.model_idle_unload_seconds:
        return

    def loop() -> None:
        while True:
            time.sleep(30)
            try:
                sweep_idle()
            except Exception:  # noqa: BLE001 - a sweep must never kill the server
                logger.exception("idle model sweep failed")

    threading.Thread(target=loop, name="model-idle-sweep", daemon=True).start()


# ── requests ─────────────────────────────────────────────────────────────────


class ContextRequest(BaseModel):
    series: str
    query: str
    mode: Literal["qa", "narrative", "roster", "auto"] = "qa"
    # The page the question is authored against, when the query's own words do
    # not name it: "What kind of motif does the King of Curses have, per the
    # page's Trivia?" asks about Angel's page but names only Sukuna's title, so
    # the search would focus Sukuna and never surface the one passage that
    # carries the answer. It widens the qa vector focus to the named page, and
    # (release R1-b) takes precedence over the query's own subject for the mode
    # decision whenever the page is a thing rather than a story; a story-typed
    # page keeps the narrative read, and the wide search keeps the focus either
    # way.
    subject: str | None = None
    token_budget: int = Field(default=6000, ge=200, le=100_000)
    top_k: int | None = Field(
        default=None,
        ge=1,
        le=50,
        description=(
            "Passages to retrieve before budgeting. Defaults to the engine's "
            "tuned value; raise for multi-entity questions that need recall. In "
            "narrative mode it sets how many beats are gathered."
        ),
    )
    as_prompt: bool = Field(
        default=False, description="Also return the bundle rendered as plain text."
    )
    # The two choices the user makes before a script is written. They belong on
    # the request because the rendered prompt states them: the writing rules are
    # served with the context, not left in a document the client may not read.
    words: int = Field(
        default=0, ge=0, le=20_000, description="Target script length, in words."
    )
    intro: bool = Field(
        default=True, description="Whether the script opens with a hook paragraph."
    )
    rules: bool = Field(
        default=True,
        description="Append the house style, voice and annotation rules to the prompt.",
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
        # When this process started, so a caller can tell whether it predates
        # the code it is about to measure. One run of the canon suite was
        # taken against a stale server and reported no change from a fix that
        # had in fact worked -- the replacement had exited on a bound port
        # while the old process kept answering. `cli canon-run` compares this
        # against the newest mtime under `scriptengine/` and refuses to start.
        "started": _STARTED,
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

    Returns passages in the right order (narrative order when asked for it,
    not similarity order) with the facts behind them and a citation each.

    `mode="auto"` reads the topic: "Every Rank of Curse" is a set and comes back
    as a roster, anything else comes back as a narrative. Most script topics are
    one or the other, and asking the caller to classify its own topic is asking
    it to know which mode exists.
    """
    from scriptengine.retrieve.router import route

    paths = _paths_or_404(request.series)
    mode = request.mode
    routed = None
    if mode == "auto":
        routed = route(paths, request.query, subject=request.subject)
        mode = routed.mode

    bundle = build_context(
        paths,
        request.query,
        mode=mode,
        token_budget=request.token_budget,
        top_k=request.top_k,
        subject=request.subject,
    )
    # A roster with nothing in it is not an answer. Falling back keeps a topic
    # phrased as a list ("Every fight in Shibuya") from returning an empty
    # bundle when the wiki has no such set.
    if mode == "roster" and not bundle.get("members") and request.mode == "auto":
        bundle = build_context(
            paths,
            request.query,
            mode="narrative",
            token_budget=request.token_budget,
            top_k=request.top_k,
            subject=request.subject,
        )

    # Why this mode was chosen, so a misroute is visible to the caller rather
    # than only in a trace.
    if routed is not None:
        bundle["routed"] = routed.as_dict()

    if request.as_prompt:
        bundle["prompt"] = render_prompt(
            bundle, intro=request.intro, words=request.words, rules=request.rules
        )
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


@app.get("/abilities/{series}/{entity}")
def abilities(series: str, entity: str) -> dict[str, Any]:
    """Every ability a character uses, straight from the knowledge graph.

    Walks the `user` edges backwards from the character to its ability pages
    (the retriever cannot do this: prose ranking misses abilities when the
    character's own page is not indexed). Each ability comes with its debut
    chapter, its `Usage / <character>` section, and the chapter refs inside
    that section, where the character actually used it, not just where it is
    mentioned.
    """
    from scriptengine.retrieve.abilities import collect_abilities

    paths = _paths_or_404(series)
    result = collect_abilities(paths, entity)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No entity matching {entity!r} in {series!r}.",
        )
    return result


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

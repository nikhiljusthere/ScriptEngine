"""Assembling the context bundle a script-writing model consumes.

This is the shape of the whole product. Everything upstream exists so that this
function can return passages in the right order, the facts behind them, and a
citation for each — inside a token budget the caller has to live within.

Two decisions matter here.

**Ordering is preserved, not re-sorted by relevance.** In narrative mode the
beats come back in the order they happened. A script written from
relevance-ordered fragments reads like a wiki summary; one written from ordered
beats reads like a story.

**Truncation happens at beat boundaries.** A smaller budget costs you later
beats, never a mangled one. Half a beat is worse than no beat: the model will
write confidently from a sentence that stops mid-clause.
"""

from __future__ import annotations

from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings

# Rough conversion from characters to tokens for English prose. Deliberately
# pessimistic — overshooting a context window costs a failed generation, while
# undershooting costs a little unused room.
CHARS_PER_TOKEN = 3.6

# Everything rendered into the prompt has to be paid for out of the budget,
# including the cast list.
MAX_PARTICIPANTS = 20


def estimate_tokens(text: str) -> int:
    return int(len(text) / CHARS_PER_TOKEN) + 1


def build_context(
    paths: SeriesPaths,
    query: str,
    mode: str = "qa",
    token_budget: int = 6000,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Return an ordered, cited, budgeted bundle for a downstream model."""
    settings = settings or get_settings()
    if mode not in {"qa", "narrative"}:
        raise ValueError(f"Unknown mode {mode!r}; expected 'qa' or 'narrative'.")

    if mode == "narrative":
        return _narrative_context(paths, query, token_budget, settings)
    return _qa_context(paths, query, token_budget, settings)


def _narrative_context(
    paths: SeriesPaths, query: str, token_budget: int, settings: Settings
) -> dict[str, Any]:
    from scriptengine.retrieve.narrative import NarrativeRetriever

    with NarrativeRetriever(paths, settings) as retriever:
        narrative = retriever.timeline(query, max_beats=60)

    # The Shibuya Incident lists 42 participants. Rendering all of them spends
    # a chunk of the budget on a cast list before a single event is described,
    # and the ones that matter are the ones the beats actually name.
    participants = narrative.participants[:MAX_PARTICIPANTS]

    beats: list[dict[str, Any]] = []
    used = estimate_tokens(", ".join(participants))

    for beat in narrative.beats:
        payload = beat.as_dict()
        cost = estimate_tokens(payload["text"]) + 40  # heading and metadata
        if used + cost > token_budget and beats:
            break
        beats.append(payload)
        used += cost

    return {
        "series": paths.name,
        "mode": "narrative",
        "subject": narrative.subject,
        "beats": beats,
        "participants": participants,
        "facts": [],
        "truncated": len(beats) < len(narrative.beats),
        "beats_available": len(narrative.beats),
        "tokens_used": used,
    }


def _qa_context(
    paths: SeriesPaths, query: str, token_budget: int, settings: Settings
) -> dict[str, Any]:
    from scriptengine.retrieve.hybrid import HybridRetriever

    with HybridRetriever(paths, settings) as retriever:
        result = retriever.search(query, top_k=settings.final_top_k)
        retriever.release_models()

    # Facts are cheap and exact, so they are paid for first: a character's grade
    # is a dozen tokens and is the kind of detail a script gets wrong.
    facts = [
        {
            "entity": fact["entity"],
            "field": fact["label"],
            "value": fact["value"],
            "citation": fact["citation"],
        }
        for fact in result.facts[:30]
    ]
    entities = result.entities[:MAX_PARTICIPANTS]
    used = sum(estimate_tokens(f"{f['field']}: {f['value']}") for f in facts)
    used += estimate_tokens(", ".join(entities))

    beats: list[dict[str, Any]] = []
    for order, passage in enumerate(result.passages, start=1):
        cost = estimate_tokens(passage.text) + 30
        if used + cost > token_budget and beats:
            break
        beats.append(
            {
                "order": order,
                "title": passage.breadcrumb or passage.doc_title,
                "doc_title": passage.doc_title,
                "breadcrumb": passage.breadcrumb,
                "text": passage.text,
                "score": round(passage.score, 4),
            }
        )
        used += cost

    return {
        "series": paths.name,
        "mode": "qa",
        "subject": query,
        "beats": beats,
        "participants": entities,
        "facts": facts,
        "relations": result.relations[:20],
        "truncated": len(beats) < len(result.passages),
        "beats_available": len(result.passages),
        "tokens_used": used,
    }


def render_prompt(bundle: dict[str, Any]) -> str:
    """Flatten a bundle into plain text, for callers that just want a string.

    Offered because the alternative is every consumer inventing its own
    formatting, and formatting is where citations get quietly dropped.
    """
    lines: list[str] = [f"# {bundle['subject']}", ""]

    if bundle.get("facts"):
        lines.append("## Established facts")
        for fact in bundle["facts"]:
            citation = f"  [{fact['citation']}]" if fact.get("citation") else ""
            lines.append(f"- {fact['entity']} — {fact['field']}: {fact['value']}{citation}")
        lines.append("")

    if bundle.get("participants"):
        lines.append("## Involved")
        lines.append(", ".join(bundle["participants"]))
        lines.append("")

    heading = "## Events in order" if bundle["mode"] == "narrative" else "## Sources"
    lines.append(heading)
    for beat in bundle["beats"]:
        marker = f"[{beat['order']}]"
        time = f" ({beat['time']})" if beat.get("time") else ""
        lines.append(f"\n{marker} {beat['title']}{time}")
        lines.append(f"    source: {beat.get('doc_title', '')}")
        lines.append(beat["text"])

    if bundle.get("truncated"):
        lines.append(
            f"\n[truncated: {len(bundle['beats'])} of "
            f"{bundle['beats_available']} sections included]"
        )

    return "\n".join(lines)

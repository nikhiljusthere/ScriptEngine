"""Assembling the context bundle a script-writing model consumes.

This is the shape of the whole product. Everything upstream exists so that this
function can return passages in the right order, the facts behind them, and a
citation for each — inside a token budget the caller has to live within.

Three decisions matter here.

**Ordering is story order, with the strongest matches leading.** In narrative
mode the beats of an event come back in the order they happened. When the query
names specific content ("sealed and freed"), the events that match it most
strongly lead — instalment order within each score band — so the budget reaches
the end of the story instead of running out inside the first event page. A
script written from relevance-ordered fragments reads like a wiki summary; one
written from ordered beats reads like a story.

**Truncation happens at beat boundaries.** A smaller budget costs you later
beats, never a mangled one. Half a beat is worse than no beat: the model will
write confidently from a sentence that stops mid-clause. Beats longer than
2800 characters are split at sentence ends, and each part is re-attributed, so
one giant section cannot starve every beat after it and no part loses the
citation that covers it.

**Every beat states where it came from.** A script has to end each block with
its chapter and episode, and the wiki cites once per paragraph, not once per
sentence — 12.8% of the sentences in a fetched Shibuya Incident bundle carried
a locator, and 60 of its 128 beats carried none at all. `retrieve/citations.py`
resolves that: the beat header carries the span its prose is sourced to, so the
writer never has to guess and never has to leave a block untagged.
"""

from __future__ import annotations

from typing import Any

from scriptengine.api.rules import writing_rules
from scriptengine.config import SeriesPaths, Settings, get_settings
from scriptengine.retrieve import citations as cite

# Rough conversion from characters to tokens for English prose. Deliberately
# pessimistic — overshooting a context window costs a failed generation, while
# undershooting costs a little unused room.
CHARS_PER_TOKEN = 3.6

# Everything rendered into the prompt has to be paid for out of the budget,
# including the cast list.
MAX_PARTICIPANTS = 20

# One beat can dwarf the budget: a Shibuya section runs over 16,000 characters.
# Beats are capped at sentence boundaries, so a long section contributes its
# opening as a digest instead of starving every beat after it.
MAX_BEAT_CHARS = 2800

# No roster member needs more than this, however small the list: past it the
# entry stops being a section and starts being the whole page.
MAX_MEMBER_CHARS = 4000

MODES = {"qa", "narrative", "roster"}


def estimate_tokens(text: str) -> int:
    return int(len(text) / CHARS_PER_TOKEN) + 1


def _split_oversized_beat(
    beat: dict[str, Any], episodes: cite.EpisodeIndex | None = None
) -> list[dict[str, Any]]:
    """Split a beat longer than MAX_BEAT_CHARS, keeping each part sourced.

    Splitting used to slice the raw text at paragraph ends, which is why most
    beats came back with no citation at all: a section cites itself once, in its
    last paragraph, and every earlier slice lost that reference. Parts are built
    out of attributed sentences instead, so each one reports the chapters and
    episodes its own prose is sourced to.
    """
    text = beat["text"]
    if len(text) <= MAX_BEAT_CHARS:
        return [dict(beat, **_sourcing(text, episodes))]

    sentences = cite.attribute(text, episodes)
    parts: list[list[cite.SentenceCitation]] = [[]]
    length = 0

    for sentence in sentences:
        cost = len(sentence.text) + 1
        if length + cost > MAX_BEAT_CHARS and parts[-1]:
            parts.append([])
            length = 0
        parts[-1].append(sentence)
        length += cost

    built: list[dict[str, Any]] = []
    for part in parts:
        if not part:
            continue
        found = cite.locators(part)
        built.append(
            dict(
                beat,
                order=0,
                text=" ".join(sentence.text for sentence in part),
                citations=[locator.render() for locator in found],
                source_span=cite.span(found),
            )
        )
    return built


def _sourcing(text: str, episodes: cite.EpisodeIndex | None) -> dict[str, Any]:
    found = cite.locators(cite.attribute(text, episodes))
    return {
        "citations": [locator.render() for locator in found],
        "source_span": cite.span(found),
    }


def _capped_beats(
    beats: list[dict[str, Any]], episodes: cite.EpisodeIndex | None = None
) -> list[dict[str, Any]]:
    """Expand oversized beats into sourced, sentence-aligned parts."""
    expanded: list[dict[str, Any]] = []
    for beat in beats:
        expanded.extend(_split_oversized_beat(beat, episodes))
    for order, beat in enumerate(expanded, start=1):
        beat["order"] = order
    return expanded


def build_context(
    paths: SeriesPaths,
    query: str,
    mode: str = "qa",
    token_budget: int = 6000,
    top_k: int | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Return an ordered, cited, budgeted bundle for a downstream model."""
    settings = settings or get_settings()
    if mode not in MODES:
        raise ValueError(f"Unknown mode {mode!r}; expected one of {sorted(MODES)}.")

    if mode == "narrative":
        return _narrative_context(paths, query, token_budget, top_k, settings)
    if mode == "roster":
        return _roster_context(paths, query, token_budget, settings)
    return _qa_context(paths, query, token_budget, top_k, settings)


def _narrative_context(
    paths: SeriesPaths,
    query: str,
    token_budget: int,
    top_k: int | None,
    settings: Settings,
) -> dict[str, Any]:
    from scriptengine.retrieve.narrative import NarrativeRetriever

    # `top_k` is the caller's request for breadth. In narrative mode that is a
    # number of beats, not of passages; it used to be accepted by the API and
    # then ignored, so `script_writer.ps1` sent one on every fetch for nothing.
    max_beats = max(top_k * 5, 60) if top_k else 60

    with NarrativeRetriever(paths, settings) as retriever:
        narrative = retriever.timeline(query, max_beats=max_beats)
        episodes = retriever.episodes
        # Facts are cheap and exact. A narrative bundle used to return none at
        # all, so a script written from it had the story and not one grade,
        # birthday or debut chapter to anchor it.
        facts = _subject_facts(retriever.store, narrative)

    # The Shibuya Incident lists 42 participants. Rendering all of them spends
    # a chunk of the budget on a cast list before a single event is described,
    # and the ones that matter are the ones the beats actually name.
    participants = narrative.participants[:MAX_PARTICIPANTS]

    beats = _capped_beats([beat.as_dict() for beat in narrative.beats], episodes)
    used = estimate_tokens(", ".join(participants))
    used += sum(estimate_tokens(f"{f['field']}: {f['value']}") for f in facts)

    included: list[dict[str, Any]] = []
    for payload in beats:
        cost = estimate_tokens(payload["text"]) + 40  # heading and metadata
        if used + cost > token_budget and included:
            break
        included.append(payload)
        used += cost

    return {
        "series": paths.name,
        "mode": "narrative",
        "subject": narrative.subject,
        "beats": included,
        "participants": participants,
        "facts": facts,
        "truncated": len(included) < len(beats),
        "beats_available": len(beats),
        "tokens_used": used,
    }


def _subject_facts(store: Any, narrative: Any, limit: int = 24) -> list[dict[str, Any]]:
    """The subject's own infobox facts, rendered for the prompt."""
    from scriptengine.stores.facts import NOISE_FACT_KEYS

    facts: list[dict[str, Any]] = []
    for row in store.facts_for(narrative.subject):
        if not row["value"] or row["key"] in NOISE_FACT_KEYS:
            continue
        facts.append(
            {
                "entity": narrative.subject,
                "field": row["label"] or row["key"],
                "value": row["value"],
                "citation": row["citation"],
            }
        )
        if len(facts) >= limit:
            break
    return facts


def _roster_context(
    paths: SeriesPaths, query: str, token_budget: int, settings: Settings
) -> dict[str, Any]:
    """Every member of the set the query names, as its own budgeted section.

    Rosters are what most of the sample scripts are: one section per member, in
    a deliberate order. Members are paid for one at a time so a long entry near
    the top cannot swallow the tail of the list.
    """
    from scriptengine.retrieve.roster import build_roster

    roster = build_roster(paths, query, settings)

    # Every member gets an equal share of the budget. A roster is a list of
    # equals — the twentieth entry deserves the same treatment as the first —
    # and paying for them in order would let three long biographies at the top
    # spend everything the tail needed.
    share = int(token_budget * CHARS_PER_TOKEN / max(len(roster.members), 1) * 0.85)
    member_chars = max(600, min(share, MAX_MEMBER_CHARS))

    used = 0
    members: list[dict[str, Any]] = []
    for member in roster.members:
        payload = member.as_dict()
        payload["text"] = _trim(payload.get("text", ""), member_chars)
        cost = estimate_tokens(payload["text"]) + 60
        if used + cost > token_budget and members:
            break
        members.append(payload)
        used += cost

    return {
        "series": paths.name,
        "mode": "roster",
        "subject": roster.subject,
        "basis": roster.basis,
        "kind": roster.kind,
        "groups": roster.groups,
        "members": members,
        "beats": [],
        "participants": [],
        "facts": [],
        "truncated": len(members) < len(roster.members),
        "members_available": len(roster.members),
        "tokens_used": used,
    }


def _qa_context(
    paths: SeriesPaths,
    query: str,
    token_budget: int,
    top_k: int | None,
    settings: Settings,
) -> dict[str, Any]:
    from scriptengine.retrieve.hybrid import HybridRetriever
    from scriptengine.stores.facts import FactStore

    with HybridRetriever(paths, settings) as retriever:
        result = retriever.search(query, top_k=top_k, rerank=True)
        retriever.release_models()

    with FactStore(paths.facts_db) as store:
        episodes = cite.EpisodeIndex.from_store(store)

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
        text = cite.upgrade_markers(passage.text, episodes)
        beats.append(
            {
                "order": order,
                "title": passage.breadcrumb or passage.doc_title,
                "doc_title": passage.doc_title,
                "breadcrumb": passage.breadcrumb,
                "text": text,
                "score": round(passage.score, 4),
                **_sourcing(text, episodes),
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


def render_prompt(
    bundle: dict[str, Any], intro: bool = True, words: int = 0, rules: bool = True
) -> str:
    """Flatten a bundle into plain text, for callers that just want a string.

    Offered because the alternative is every consumer inventing its own
    formatting, and formatting is where citations get quietly dropped.

    Two things are deliberately absent. There are no `[n]` order markers: the
    house rules forbid them in a script, the retired ComfyUI node stripped them
    before the model saw them, and leaving them in the served prompt only gave
    the writer something to copy. And a page's name is printed when it changes
    rather than under every beat — the last Shibuya bundle repeated
    `source: Shibuya Incident` 128 times.
    """
    lines: list[str] = [f"# {bundle['subject']}", ""]

    if bundle.get("basis"):
        lines.append(f"Set: {bundle['basis']}")
        if bundle.get("groups"):
            lines.append("Groups: " + ", ".join(bundle["groups"]))
        lines.append("")

    if bundle.get("facts"):
        lines.append("## Established facts")
        for fact in bundle["facts"]:
            citation = f"  [{fact['citation']}]" if fact.get("citation") else ""
            value = _one_line(fact["value"])
            lines.append(f"- {fact['entity']} — {fact['field']}: {value}{citation}")
        lines.append("")

    if bundle.get("participants"):
        lines.append("## Involved")
        lines.append(", ".join(bundle["participants"]))
        lines.append("")

    if bundle.get("relations"):
        lines.append("## Relationships")
        for relation in bundle["relations"]:
            lines.append(
                f"- {relation['source']} — {relation['relation']} — {relation['target']}"
            )
        lines.append("")

    if bundle.get("members"):
        lines.extend(_render_members(bundle["members"]))
    if bundle.get("beats"):
        lines.extend(_render_beats(bundle))

    if bundle.get("truncated"):
        remaining = bundle.get("beats_available") or bundle.get("members_available", 0)
        included = len(bundle.get("beats") or bundle.get("members", []))
        lines.append(f"\n[truncated: {included} of {remaining} sections included]")

    if rules:
        lines.append("")
        lines.append(writing_rules(intro=intro, words=words))

    return "\n".join(lines)


def _trim(text: str, limit: int) -> str:
    """Cut at a sentence end, never mid-clause.

    Half a sentence is worse than no sentence: the model will finish it, and it
    will finish it with something the wiki never said.
    """
    if len(text) <= limit:
        return text
    cut = text.rfind(". ", 0, limit + 1)
    return text[: cut + 1] if cut > limit // 2 else text[:limit].rstrip()


def _one_line(value: str, limit: int = 160) -> str:
    """Fact values render as one line.

    An infobox list arrives with newlines in it — Naoya Zenin's `relatives` is
    twelve names on twelve lines — and a labelled line that runs to twelve of
    them stops looking like a fact and starts looking like prose the script
    might quote.
    """
    flat = " / ".join(part.strip() for part in (value or "").splitlines() if part.strip())
    return flat if len(flat) <= limit else flat[: limit - 1].rstrip() + "…"


def _render_beats(bundle: dict[str, Any]) -> list[str]:
    heading = "## Events in order" if bundle["mode"] == "narrative" else "## Sources"
    lines = [heading]
    current_source = ""

    for beat in bundle["beats"]:
        source = beat.get("doc_title", "")
        if source and source != current_source:
            lines.append(f"\n### {source}")
            current_source = source

        time = f" ({beat['time']})" if beat.get("time") else ""
        lines.append(f"\n{beat['title']}{time}")
        if beat.get("source_span"):
            lines.append(f"    sourced: {beat['source_span']}")
        lines.append(beat["text"])

    return lines


def _render_members(members: list[dict[str, Any]]) -> list[str]:
    lines = ["## Members"]
    current_group = ""

    for member in members:
        group = member.get("group", "")
        if group and group != current_group:
            lines.append(f"\n### {group}")
            current_group = group

        lines.append(f"\n{member['name']}")
        if member.get("debut"):
            lines.append(f"    debut: {member['debut']}")
        if member.get("source_span"):
            lines.append(f"    sourced: {member['source_span']}")
        for fact in member.get("facts", [])[:10]:
            lines.append(f"    {fact['field']}: {_one_line(fact['value'])}")
        if member.get("text"):
            lines.append(member["text"])

    return lines

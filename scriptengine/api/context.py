"""Assembling the context bundle a script-writing model consumes.

This is the shape of the whole product. Everything upstream exists so that this
function can return passages in the right order, the facts behind them, and a
citation for each, inside a token budget the caller has to live within.

Three decisions matter here.

**Ordering is story order, with the strongest matches leading.** In narrative
mode the beats of an event come back in the order they happened. When the query
names specific content ("sealed and freed"), the events that match it most
strongly lead (instalment order within each score band) so the budget reaches
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
sentence. 12.8% of the sentences in a fetched Shibuya Incident bundle carried
a locator, and 60 of its 128 beats carried none at all. `retrieve/citations.py`
resolves that: the beat header carries the span its prose is sourced to, so the
writer never has to guess and never has to leave a block untagged.
"""

from __future__ import annotations

import os
import re
import sqlite3
from typing import Any

from scriptengine.api.rules import writing_rules
from scriptengine.config import SeriesPaths, Settings, get_settings, load_overrides
from scriptengine.retrieve import citations as cite
from scriptengine.retrieve import roster

# Rough conversion from characters to tokens for English prose. Deliberately
# pessimistic, because overshooting a context window costs a failed generation, while
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

MODES = {"qa", "narrative", "roster", "relations"}


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
    subject: str | None = None,
) -> dict[str, Any]:
    """Return an ordered, cited, budgeted bundle for a downstream model.

    `subject` names the page the question is about when its words do not. qa
    widens its vector focus with it, and narrative leads the walk with the
    page's own sections (the R6 floor), because both are paths that would
    otherwise read a page the query's own words never resolved.
    """
    settings = settings or get_settings()
    if mode not in MODES:
        raise ValueError(f"Unknown mode {mode!r}; expected one of {sorted(MODES)}.")

    if mode == "narrative":
        return _narrative_context(paths, query, token_budget, top_k, settings, subject)
    if mode == "roster":
        return _roster_context(paths, query, token_budget, settings)
    if mode == "relations":
        return _relations_context(paths, query, token_budget, top_k, settings, subject)
    return _qa_context(paths, query, token_budget, top_k, settings, subject)


def _narrative_context(
    paths: SeriesPaths,
    query: str,
    token_budget: int,
    top_k: int | None,
    settings: Settings,
    subject: str | None = None,
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
        # The authored page's own sections, the recall floor the qa path has
        # (R6): a battle question routed here must be able to read the battle
        # it is about, even when the query's own words resolve a character the
        # fight merely names.
        floor = retriever.authored_floor(subject, max_beats) if subject else []

    # The Shibuya Incident lists 42 participants. Rendering all of them spends
    # a chunk of the budget on a cast list before a single event is described,
    # and the ones that matter are the ones the beats actually name.
    participants = narrative.participants[:MAX_PARTICIPANTS]

    # The floor leads, in the wiki's section order; the query-driven timeline
    # follows with the sections the floor already reached removed by identity,
    # so a section the timeline also walked is not paid for twice.
    seen = {(beat.doc_title, beat.breadcrumb) for beat in floor}
    ordered = [
        *floor,
        *(beat for beat in narrative.beats
          if (beat.doc_title, beat.breadcrumb) not in seen),
    ]
    beats = _capped_beats([beat.as_dict() for beat in ordered], episodes)
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

    # A roster can carry the wiki's own words about the set -- the `Result`
    # cells of a fighter's battle table -- and they are paid for first, the
    # way qa pays for facts: they are the answer, not decoration.
    facts = roster.facts
    used = sum(estimate_tokens(f"{f['entity']}, {f['field']}: {f['value']}")
               for f in facts)

    # Every member gets an equal share of the budget. A roster is a list of
    # equals, since the twentieth entry deserves the same treatment as the first,
    # and paying for them in order would let three long biographies at the top
    # spend everything the tail needed.
    share = int(token_budget * CHARS_PER_TOKEN / max(len(roster.members), 1) * 0.85)
    member_chars = max(600, min(share, MAX_MEMBER_CHARS))

    members: list[dict[str, Any]] = []
    for member in roster.members:
        payload = member.as_dict()
        payload["text"] = _trim(payload.get("text", ""), member_chars)
        cost = estimate_tokens(payload["text"]) + 60
        if used + cost > token_budget and members:
            break
        members.append(payload)
        used += cost

    # G7: a count question ("How many X...?") routed to a roster still needs the
    # prose that states the number ("summon up to ten..."). A member list never
    # says the count, so for count queries carry the subject's own passages --
    # the same text a qa bundle would return -- paid after the members within the
    # same budget, so the number is present in the bundle a scorer reads.
    passages: list[dict[str, Any]] = []
    from scriptengine.retrieve.router import _COUNT
    if _COUNT.search(query or ""):
        from scriptengine.retrieve.hybrid import HybridRetriever
        with HybridRetriever(paths, settings) as retriever:
            found = retriever.search(query, top_k=8, rerank=True)
            retriever.release_models()
        for order, passage in enumerate(found.passages, start=1):
            cost = estimate_tokens(passage.text) + 30
            if used + cost > token_budget and (members or passages):
                break
            passages.append({
                "order": order,
                "title": passage.breadcrumb or passage.doc_title,
                "doc_title": passage.doc_title,
                "text": passage.text,
                "score": round(passage.score, 4),
            })
            used += cost

    return {
        "series": paths.name,
        "mode": "roster",
        "subject": roster.subject,
        "basis": roster.basis,
        "kind": roster.kind,
        "groups": roster.groups,
        "members": members,
        "passages": passages,
        "beats": [],
        "participants": [],
        "facts": facts,
        "truncated": len(members) < len(roster.members),
        "members_available": len(roster.members),
        # How well the set the wiki gave back matches the set that was asked
        # for. A caller writing a script off this bundle needs to know when the
        # answer is `Straw Hat Pirates' Creations` for "Every Straw Hat Pirate".
        "confidence": roster.confidence,
        "unmatched": roster.unmatched,
        "warning": roster.warning,
        # Membership validation. `candidates` is what the wiki's set held before
        # the topic's own constraints were applied, and `rejected` says which
        # ones did not survive and why, so a list dropping from 160 to 75 is
        # inspectable rather than mysterious.
        "candidates": roster.candidates,
        "rejected": roster.rejected,
        "scope": roster.scope,
        "capped": roster.capped,
        "tokens_used": used,
    }


def _relations_context(
    paths: SeriesPaths,
    query: str,
    token_budget: int,
    top_k: int | None,
    settings: Settings,
    subject: str | None = None,
) -> dict[str, Any]:
    """The character's relationships, as the primary answer.

    R-5 (G-CSM-4): "Every documented relationship of X" and its interrogative
    twins route here instead of to a roster set (the "Every" makes it
    set-shaped, so the enumeration rule grabs it) or the qa passage search
    (rule 3, which the relation rows never reach), because the wiki records
    relationships as relation rows -- the extracted `relations` table and the
    graph `edges` -- that neither path serves. The rows lead the bundle; the
    ranked order (the edge the question names first) is paid in order and cut
    at the budget, so a busy character's one relevant row is not buried behind
    forty unrelated ones.
    """
    from scriptengine.stores.facts import FactStore
    from scriptengine.retrieve.roster import rank_relations

    with FactStore(paths.facts_db) as store:
        # The character: the authored subject when the caller named it, else the
        # query's own linked entity ("...relationship of Denji" -> Denji).
        probe = subject or query
        linked = store.link_entities(probe)
        ids = [int(row["id"]) for row in linked[:3]]
        if subject:
            names = [subject]
        elif linked:
            names = [row["name"] for row in linked]
        else:
            # Fallback: the "relationship of X" object, when the query's words
            # linked no known entity. The LLM `relations` table is a keyed
            # lookup, so it still answers even with no node id to walk edges.
            m = re.search(
                r"relationship(?:s)?\s+(?:of|with)\s+([\w ]+)$",
                query or "", re.IGNORECASE,
            )
            names = [m.group(1).strip()[:60]] if m else []
        names = names[:3]
        # Both ways a relationship is recorded: the LLM-extracted rows (verbatim
        # quote + era, the wiki's own words) and the graph edges (resolved
        # infobox links). The qa path already unions the two (hybrid, 3b/3c);
        # here the union IS the answer, so it leads the bundle.
        relations: list[dict[str, Any]] = []
        for row in store.edges_for(ids, min_confidence=0.9, limit=40):
            relations.append({
                "source": row["source"], "relation": row["relation"],
                "target": row["target"], "confidence": row["confidence"],
                "quote": "", "era": "",
            })
        seen = {(r["source"], r["relation"], r["target"], r["quote"])
                for r in relations}
        for name in names:
            for row in store.relations_of(name, both_ways=True):
                key = (row["character"], row["relation"], row["other"],
                       row["quote"] or "")
                if key in seen:
                    continue
                seen.add(key)
                relations.append({
                    "source": row["character"], "relation": row["relation"],
                    "target": row["other"], "confidence": 1.0,
                    "quote": row["quote"] or "", "era": row["era"] or "",
                })
        ranked = rank_relations(relations, query)

    if top_k:
        ranked = ranked[:top_k]

    # The rows are cheap; pay for them in rank order and cut at the budget, so a
    # long character's tail is what drops, never the edge that answers the
    # question. The first row is never dropped, the way a roster's first member
    # is not. The cost is in tokens (estimate_tokens), so the guard compares
    # against token_budget like every other mode - charging tokens against a
    # char budget made the effective cap 3.6x the requested budget (council_r5
    # amendment A2, caught by rev_2).
    used = 0
    included: list[dict[str, Any]] = []
    for order, relation in enumerate(ranked, start=1):
        line = f"{relation['source']} / {relation['relation']} / {relation['target']}"
        if relation.get("era"):
            line += f" ({relation['era']})"
        if relation.get("quote"):
            line += f": {relation['quote']}"
        cost = estimate_tokens(line) + 5
        if included and used + cost > token_budget:
            break
        relation = dict(relation, order=order)
        included.append(relation)
        used += cost

    return {
        "series": paths.name,
        "mode": "relations",
        "subject": names[0] if names else query,
        "relations": included,
        "participants": names,
        "facts": [],
        "beats": [],
        "truncated": len(included) < len(ranked),
        "relations_available": len(ranked),
        "tokens_used": used,
    }


_STORY_PAGE_RE = re.compile(
    r"\b([\w'’\-]+(?:\s+[\w'’\-]+){0,6}?)\s+(arc|chapter|episode|volume)\b",
    re.IGNORECASE,
)
_STORY_PAGE_LEAD_RE = re.compile(
    r"\b(arc|chapter|episode|volume)\s+([A-Za-z0-9'’\-]+(?:\s+[A-Za-z0-9'’\-]+){0,3})",
    re.IGNORECASE,
)

_STRIP_PUNCT = " \t\n\r\f\v.,;:!?()[]{}\"'“”‘’—-"
_APOSTROPHES = ("'", "’", "‘", "ʼ")
_POSSESSIVE_RE = re.compile(
    r"\b((?:[\w'’\-]+\s+){0,1}[\w'’\-]+)\s*['’]s\b\s+([A-Za-z0-9'’\-]+)",
    re.IGNORECASE,
)
_OWNER_LEAD_STOPWORDS = frozenset({
    "the", "a", "an", "to", "of", "in", "on", "for", "with", "is", "are",
    "was", "were", "be", "and", "or", "at", "by", "from", "that", "what",
    "who", "do", "does", "did",
})


def _owner_attribute_hit(store, query: str) -> bool:
    """Whether the query names an owner's declared ability/contract.

    "Mysterious Man's Typhoon Devil Contract" is answered on the
    owner's page (the router's possessive-owner rule reads it
    correctly); the abilities table declares the (character,
    ability-prefix) pair, so verbatim defers instead of hijacking the
    subject to the ability's namesake page. Generic mechanism (store
    lookup, no names); per-row evidence decides each pair.
    """
    for match in _POSSESSIVE_RE.finditer(query or ""):
        owner = match.group(1).strip(_STRIP_PUNCT)
        head = match.group(2).strip(_STRIP_PUNCT)
        if not owner or not head:
            continue
        parts = [w for w in owner.split() if w.lower() not in _OWNER_LEAD_STOPWORDS]
        if not parts:
            continue
        owner = " ".join(parts)
        try:
            hit = store.connection.execute(
                "SELECT 1 FROM abilities WHERE character = ? COLLATE NOCASE"
                " AND name LIKE ? ESCAPE '\\' LIMIT 1",
                (owner, head.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"),
            ).fetchone()
        except sqlite3.OperationalError:
            # A store built before ability extraction has no abilities table
            # at all; then no (character, ability) pair is declared and the
            # check is trivially negative (the same contract as
            # FactStore.abilities_of: absence is a complete answer).
            return False
        if hit is not None:
            return True
    return False


def _verbatim_title_subject(paths: SeriesPaths, query: str) -> str | None:
    """The longest exact document title occurring in the query, if resolved.

    DERIV leg v3 (general rule): possessive spans ("Denji's") are
    modifiers, never referents; trailing punctuation ("arc?",
    "Thugs,") is orthography (internal punctuation belongs to the
    title and is kept). Longest match wins, then leftmost — so
    "Tokyo Special Division 5" beats "Control Devil arc" with no
    temporal special-casing, and "Yakuza" beats possessive "Denji's".
    Possessive-owner-with-declared-ability queries defer entirely
    (see _owner_attribute_hit). Resolution via subject_node_name;
    anything unresolvable returns None and the next tier runs
    unchanged. Generic vocabulary only.
    """
    from scriptengine.stores.facts import FactStore

    if not query:
        return None
    words = query.split()
    if not words:
        return None
    with FactStore(paths.facts_db) as store:
        if _owner_attribute_hit(store, query):
            return None
        for width in range(min(6, len(words)), 0, -1):
            for i in range(len(words) - width + 1):
                span = words[i:i + width]
                if any(q in w for w in span for q in _APOSTROPHES):
                    continue
                candidate = " ".join(span).strip(_STRIP_PUNCT)
                if not candidate:
                    continue
                if store.subject_node_name(candidate) is not None:
                    return candidate
    return None


def _story_page_subject(paths: SeriesPaths, query: str) -> str | None:
    """A story page (arc/chapter/episode/volume) the query names, if it resolves.

    D7 spike: the no-hint qa path scopes retrieval to linked entities, so a
    question about a story page ("What happens in the Katana Man arc?")
    reads the character the page is named after and never reaches the page's
    own chunks (probe 1: gold absent top-50+dropped; probes 2/3: naming the
    page flips the verdict). When the query names such a page and it resolves
    to a node, return it so the R6 floor + focus include it. Resolution is by
    node/alias lookup (subject_node_name, case-insensitive); anything
    unresolvable returns None and the ranked behaviour stands unchanged.
    Generic page-type patterns only — no series names.
    """
    from scriptengine.stores.facts import FactStore

    candidates: list[str] = []
    for match in _STORY_PAGE_RE.finditer(query or ""):
        words = match.group(1).split()
        keyword = match.group(2)
        for i in range(len(words)):
            candidates.append(" ".join(words[i:]) + " " + keyword)
    for match in _STORY_PAGE_LEAD_RE.finditer(query or ""):
        # Keyword-first titles ("Chapter 1", "Episode 12", "Volume 13"):
        # the number follows the keyword, so the trailing pattern above
        # never sees them.
        words = (match.group(1) + " " + match.group(2)).split()
        for i in range(len(words)):
            candidates.append(" ".join(words[i:]))
    if not candidates:
        return None
    with FactStore(paths.facts_db) as store:
        for candidate in candidates:
            if store.subject_node_name(candidate) is not None:
                return candidate
    return None


def _tiered_enabled() -> bool:
    """Whether tier-2 recall appends ranks 9-30 within leftover budget.

    TIERED leg (flagged experiment, kill = unset, no revert commit).
    Mirrors the events_order_enabled pattern: read on every call.
    """
    return os.environ.get("SCRIPTENGINE_TIERED_RECALL", "0") == "1"


def _abilwidth_enabled() -> bool:
    """ABILWIDTH leg gate (kill = unset, no revert commit): widen beam
    top_k to 30 for possessive-owner ability queries. Mirrors
    _tiered_enabled: read on every call; OFF = committed-tree behavior.
    """
    return os.environ.get("SCRIPTENGINE_ABILWIDTH_RECALL", "0") == "1"


def _qa_context(
    paths: SeriesPaths,
    query: str,
    token_budget: int,
    top_k: int | None,
    settings: Settings,
    subject: str | None = None,
) -> dict[str, Any]:
    from scriptengine.retrieve.hybrid import HybridRetriever, Passage
    from scriptengine.stores.facts import FactStore

    # D7 spike: derive a story-page subject when the caller names none, so
    # arc/chapter/episode/volume questions read the page they are about
    # instead of the entity the page is named after. Tier 2 falls back to
    # the router's subject read (the auto path's 2-prep forward) for
    # character/organization subjects the story patterns never name. None
    # when nothing resolves: behaviour unchanged.
    # DERIV leg (v3 general rule): verbatim-title containment FIRST —
    # the longest exact document title occurring in the query (trailing
    # punctuation stripped, possessive spans skipped, must resolve).
    # Outranks story/router by construction: longer beats shorter, then
    # leftmost. Router stays last so every currently-served row keeps
    # its subject unless verbatim finds better (measured per row).
    if subject is None:
        subject = _verbatim_title_subject(paths, query)
    if subject is None:
        subject = _story_page_subject(paths, query)
    if subject is None:
        try:
            from scriptengine.retrieve.router import route as _route_qa

            _routed = _route_qa(paths, query, subject=None)
            subject = (_routed.signals or {}).get("subject") or None
        except Exception:
            subject = None

    # ABILWIDTH leg: possessive-owner-with-declared-ability queries
    # ("Mysterious Man's Typhoon Devil Contract", "Falling Devil's Body
    # Control") get beam top_k=30 — their gold ranks 12-47, cut at 8,
    # and tiered appends can't reach them (saturated bundles, no
    # leftover). Reuses the _owner_attribute_hit predicate (derivation
    # deferral): only declared (character, ability-prefix) pairs trigger.
    # Caller-passed top_k always wins; no-apostrophe queries skip the
    # store open entirely.
    if top_k is None and _abilwidth_enabled() and any(q in query for q in _APOSTROPHES):
        from scriptengine.stores.facts import FactStore

        with FactStore(paths.facts_db) as _store:
            if _owner_attribute_hit(_store, query):
                top_k = 30

    with HybridRetriever(paths, settings) as retriever:
        result = retriever.search(query, top_k=top_k, rerank=True, focus=subject)
        # TIERED leg: second identical search at top_k=30; tier-1 above
        # untouched (same shortlist, same rerank, same order). Tier-2 =
        # passages tier-1 lacks; the budget walk below only renders them
        # from genuinely unused budget (walk breaks at cap), so a full
        # budget yields byte-identical bundles with the flag on or off.
        tier2: list = []
        if _tiered_enabled():
            _r2 = retriever.search(query, top_k=30, rerank=True, focus=subject)
            _seen = {p.chunk_id for p in result.passages}
            tier2 = [p for p in _r2.passages if p.chunk_id not in _seen]
        retriever.release_models()

    with FactStore(paths.facts_db) as store:
        episodes = cite.EpisodeIndex.from_store(store)
        # Entity-anchored recall floor (R6; closes the G5/G11/G13/G14 family on
        # the qa path): the page a question is authored against is fetched
        # straight from the store and leads the budget walk, so its text is
        # served whether or not any one of its passages outranks the rest of
        # the corpus. The ranked beam used to be the only route to the
        # subject's page, and a phrasing whose keywords missed the answer's
        # words left the answer on the page and out of the bundle at once
        # (Kechizu 036, Tsumiki's kanji meanings, Toge 051). Size-aware by
        # construction: the loop below walks these first, in the wiki's own
        # section order, and cuts at passage boundaries exactly as it cuts the
        # beam (the first passage is never dropped, even if it alone exceeds
        # the budget). A subject that resolves to no document yields an empty
        # floor and the ranked behaviour stands unchanged.
        def _to_passage(row: Any) -> "Passage":
            return Passage(
                chunk_id=row["id"],
                text=row["text"],
                doc_title=row["doc_title"],
                breadcrumb=row["breadcrumb"],
                ordinal=row["ordinal"],
                score=0.0,
                parent_text=row["parent_text"] or "",
            )

        def _section(breadcrumb: str | None) -> str:
            # The de-dup below keys on the section a beat actually sits in --
            # the breadcrumb's last component -- not its whole path
            # ("Abilities and Powers / Cursed Technique" is Cursed Technique).
            return (breadcrumb or "").split(" / ")[-1].strip()

        # F2b (council 14): the floor used to serve EVERY sub-chunk of EVERY
        # section -- a long section fragments into many chunks (Yuji's Personality
        # is 8, his /Synopsis Culling Game arc 63; a main character's whole floor
        # is ~220 passages) -- so the 6000-token walk exhausted on the front-of-page
        # sections and never reached the one a question needs (the subpage History
        # sat ~15th in the floor and past the budget at once). The recall contract
        # is that each SECTION of the subject's page is present, not every fragment:
        # keep the leading chunk of each section (the store returns ordinal order,
        # so the first is the section's head), bounding the footprint to the number
        # of sections. Query-independent and beam-untouched (B1 holds).
        def _cap_sections(passages, cap: int = 1):
            # cap 1 is the F2b recall contract (the section's head, one chunk).
            # A wiki whose answer prose sits mid-section (CSM's box/episode
            # pages: "What happens in Chapter 97?" reads Summary chunks 4-5,
            # never chunk 2) raises `floor_section_cap` in its overrides.yaml;
            # the walk still pays in the wiki's section order, so a bigger cap
            # only widens the floor, never reorders the beam.
            kept: list = []
            counts: dict[str, int] = {}
            for p in passages:
                key = p.breadcrumb or p.doc_title
                if counts.get(key, 0) >= cap:
                    continue
                counts[key] = counts.get(key, 0) + 1
                kept.append(p)
            return kept

        floor_cap = int(load_overrides(paths).get("floor_section_cap") or 1)
        floor = _cap_sections(
            [_to_passage(row) for row in (store.passages_for_subject(subject) if subject else [])],
            floor_cap,
        )
        # F2: a character whose story beats the wiki filed off the main page (its
        # /Synopsis subpage) -- e.g. a "history of X" question authored on a
        # character whose main page has no History section. The subpage's
        # sections join the floor, but only those the main page does not already
        # carry, so a main-cast character with a History on the main page is not
        # double-served.
        if subject:
            sub = _cap_sections(
                [_to_passage(row) for row in store.synopsis_subpage_passages(subject)],
                floor_cap,
            )
            if sub:
                have = {_section(p.breadcrumb) for p in floor}
                floor += [p for p in sub if _section(p.breadcrumb) not in have]
        # 2-prep: the subject's own facts lead the slice below. A busy character's
        # facts sit behind a dozen lesser-linked entities in the entity-link
        # order, so the flat top-30 cut dropped the subject's own grade (B4: the
        # bundle carried twelve Hana Kurusu rows and five of Gojo's, and Gojo's
        # `Special Grade` sat past the cut) while serving a random participant's.
        # Resolve the subject to its node's canonical name (its own name, then an
        # editor-maintained alias) and fetch that block.
        subject_name: str | None = None
        subject_fact_rows: list[dict[str, Any]] = []
        if subject:
            subject_name = store.subject_node_name(subject)
            if subject_name:
                subject_fact_rows = [
                    {
                        "entity": subject_name,
                        "key": fact["key"],
                        "label": fact["label"] or fact["key"],
                        "value": fact["value"],
                        "citation": fact["citation"],
                    }
                    for fact in store.facts_for(subject_name)[:24]
                ]

    # Facts are cheap and exact, so they are paid for first: a character's grade
    # is a dozen tokens and is the kind of detail a script gets wrong. The
    # subject's block leads (capped at twenty-four), the remainder fills from the
    # ranked slice excluding the subject's own rows so a fact is not paid for
    # twice; without a subject that resolves to a node, the flat slice stands.
    if subject_fact_rows:
        fill = [fact for fact in result.facts if fact["entity"] != subject_name]
        raw_facts = (subject_fact_rows + fill)[:30]
    else:
        raw_facts = result.facts[:30]
    facts = [
        {
            "entity": fact["entity"],
            "field": fact["label"],
            "value": fact["value"],
            "citation": fact["citation"],
        }
        for fact in raw_facts
    ]
    entities = result.entities[:MAX_PARTICIPANTS]
    used = sum(estimate_tokens(f"{f['field']}: {f['value']}") for f in facts)
    used += estimate_tokens(", ".join(entities))

    ranked = roster.rank_relations(result.relations, query)
    named = {name.lower() for name in entities}

    def connects_named(row: dict[str, Any]) -> bool:
        source = (row.get("source") or "").lower()
        target = (row.get("target") or "").lower()
        return source in named and target in named and source != target

    # "Who is X to Y" names both ends of the answer row, and the wiki files a
    # relationship under whichever character's page it feels like. On a busy
    # character (Saitama owns dozens of relations) the row filed under the
    # other end sits past the slice, so the rows connecting two named
    # characters keep the front of the bundle and the rest follow in rank order.
    relations = [row for row in ranked if connects_named(row)]
    relations += [row for row in ranked if not connects_named(row)]

    beats: list[dict[str, Any]] = []
    # The ranked beam is walked first so a cross-page beat (B1, the `Angel` page)
    # or a non-leading section the beam reaches (Equipment, Quotes, the arc
    # timeline) is paid before the subject's own floor can evict it; the floor
    # then fills leftover budget in the wiki's section order, still guaranteeing
    # the subject's page on a keyword-miss (Kechizu 036, Tsumiki's kanji, Toge
    # 051). The old floor-first walk with a half-budget reservation capped the
    # floor without protecting the beam: B1's cross-page beat was evicted even at
    # 50%, and the Appearance-first floor burned budget before reaching the
    # sections F1/F2/C2/C3 actually need.
    beam_ids = {p.chunk_id for p in result.passages}
    floor_fill = [p for p in floor if p.chunk_id not in beam_ids]
    # F2b stage 2 (council 14): now that the floor is bounded to one chunk per
    # section, order it so the section a question actually asks about is paid
    # first -- a "history of X" question ranks the History section ahead of the
    # Appearance/Personality sections that used to burn the whole budget. The
    # score is the overlap of the query's content-terms with the section title;
    # the subject's own name is excluded (it is in every beat of its own page and
    # discriminates nothing), so a neutral query scores 0 everywhere and the wiki
    # section order is preserved exactly where it already worked. A fixed rule,
    # not a per-question knob: a section titled "Tragedy" instead of "History" is
    # handled by widening the matched terms, never by re-tuning this sort.
    _STOP = {
        "the", "of", "a", "an", "is", "are", "was", "were", "what", "who",
        "which", "how", "when", "where", "why", "to", "in", "on", "for", "and",
        "or", "its", "his", "her", "their", "with", "as", "by", "at", "does",
        "did", "do", "be", "can", "could", "would", "should", "that", "this",
    }

    def _content_tokens(s: str | None) -> set[str]:
        return {
            t for t in re.findall(r"[a-z0-9]+", (s or "").lower())
            if len(t) >= 3 and t not in _STOP
        }

    qterms = _content_tokens(query) - (_content_tokens(subject) if subject else set())

    def _qrank(p) -> tuple[int, int]:
        return (-len(qterms & _content_tokens(p.breadcrumb)), p.ordinal)

    floor_fill.sort(key=_qrank)
    # Guarded floor-lead (Kenjaku/Trivia census fault): when the query points at
    # exactly one of the subject's sections with a distinctive term ("trivia" ->
    # Trivia, "cursed technique" -> Cursed Techniques), pay that section's
    # leading chunk BEFORE the ranked beam, or a busy character's big
    # Personality/Abilities sections fill the 6000-token budget and the targeted
    # section never appears (the beam is walked to exhaustion before the floor).
    # The guard -- the top floor section must strictly beat every other on
    # query-term overlap with its title -- keeps the beam-first walk for neutral
    # and cross-page questions, which is what protects B1 (a cross-page question
    # names no single section of the subject's page, so no lead fires).
    lead = None
    if floor_fill:
        best = floor_fill[0]
        best_score = -_qrank(best)[0]
        if best_score >= 1 and all(
            -_qrank(p)[0] < best_score for p in floor_fill[1:]
        ):
            lead = best
    # TIERED leg: tier-2 appends after beam+floor, deduped by chunk,
    # so the budget walk (breaks at cap below) renders it only from
    # leftover budget. Identical tier-1 + floor order when flag off.
    _have_ids = {p.chunk_id for p in [*result.passages, *floor_fill]}
    tier2_novel = [p for p in tier2 if p.chunk_id not in _have_ids]
    if lead is not None:
        ordered = [lead, *[p for p in [*result.passages, *floor_fill] if p is not lead], *tier2_novel]
    else:
        ordered = [*result.passages, *floor_fill, *tier2_novel]
    for order, passage in enumerate(ordered, start=1):
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
        # Ranked before the slice, with the rows connecting two named characters
        # hoisted to the front (see above): `edges_for` returns strongest-
        # confidence first and stops at its own limit, so on a character with
        # thirty-two edges the one that answers "Who is X's student?" fell
        # outside the twenty without ever being ranked.
        "relations": relations[:20],
        "truncated": len(beats) < len(ordered),
        "beats_available": len(ordered),
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
    rather than under every beat. The last Shibuya bundle repeated
    `source: Shibuya Incident` 128 times.
    """
    lines: list[str] = [f"# {bundle['subject']}", ""]

    if bundle.get("basis"):
        lines.append(f"Set: {bundle['basis']}")
        if bundle.get("groups"):
            lines.append("Groups: " + ", ".join(bundle["groups"]))
        # A roster knows its own size and was not saying it. "How many members
        # are in the Phantom Troupe?" is answered by one number, and the bundle
        # listed all thirteen without ever stating that there were thirteen, so
        # the writer had to count the list themselves. Nine such questions
        # measured as "the answer was not present in what was served" while the
        # members sat right underneath.
        #
        # The count is reported with the confidence, because a set that is
        # `partial` or `weak` is the wrong set and its size is then a
        # confidently wrong number -- exactly the failure this engine tries not
        # to hand a writer. `Grand Line Islands` returns four and reports
        # `exact` while the wiki keeps hundreds, so the number is evidence about
        # what was retrieved, never a claim about the series.
        members = bundle.get("members") or []
        if members:
            confidence = bundle.get("confidence")
            suffix = f" ({confidence})" if confidence else ""
            lines.append(f"Size: {len(members)} members{suffix}")
        lines.append("")

    if bundle.get("facts"):
        lines.append("## Established facts")
        for fact in bundle["facts"]:
            citation = f"  [{fact['citation']}]" if fact.get("citation") else ""
            value = _one_line(fact["value"])
            lines.append(f"- {fact['entity']}, {fact['field']}: {value}{citation}")
        lines.append("")

    if bundle.get("participants"):
        lines.append("## Involved")
        lines.append(", ".join(bundle["participants"]))
        lines.append("")

    if bundle.get("relations"):
        lines.append("## Relationships")
        for relation in bundle["relations"]:
            line = (f"- {relation['source']} / {relation['relation']} / "
                    f"{relation['target']}")
            # The extracted rows carry the wiki's own words about the
            # relationship; they are the answer, not decoration, and the
            # era scopes which stretch of the story they describe.
            if relation.get("era"):
                line += f" ({relation['era']})"
            if relation.get("quote"):
                line += f": {relation['quote']}"
            lines.append(line)
        lines.append("")

    if bundle.get("members"):
        lines.extend(_render_members(bundle["members"]))
    if bundle.get("passages"):
        lines.extend(_render_passages(bundle["passages"]))
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

    An infobox list arrives with newlines in it. Naoya Zenin's `relatives` is
    twelve names on twelve lines, and a labelled line that runs to twelve of
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


def _render_passages(passages: list[dict[str, Any]]) -> list[str]:
    """The prose a count roster carries (G7), so the number the list implies
    is actually stated in the writer's prompt, not left to be counted off.
    """
    lines = ["## Sources"]
    for passage in passages:
        source = passage.get("doc_title", "")
        if source:
            lines.append(f"\n### {source}")
        text = passage.get("text", "")
        if text:
            lines.append(text)
    return lines

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

import re
from typing import Any

from scriptengine.api.rules import writing_rules
from scriptengine.config import SeriesPaths, Settings, get_settings
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

    with HybridRetriever(paths, settings) as retriever:
        result = retriever.search(query, top_k=top_k, rerank=True, focus=subject)
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
        floor = [
            Passage(
                chunk_id=row["id"],
                text=row["text"],
                doc_title=row["doc_title"],
                breadcrumb=row["breadcrumb"],
                ordinal=row["ordinal"],
                score=0.0,
                parent_text=row["parent_text"] or "",
            )
            for row in (store.passages_for_subject(subject) if subject else [])
        ]
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
    # The subject's own passages lead the walk, in the wiki's section order; the
    # ranked beam follows with the subject's own passages removed by id, since
    # their section-ordered copies are the ones that get paid for. An uncapped
    # floor starves the beam: Gojo's page is forty-two passages (~8.5k tokens)
    # against the 6k default budget, and the walk would spend it all on the
    # floor and serve the beam nothing, evicting the cross-page beat (B1, the
    # `Angel` page) that only the ranked beam reaches. Reserve half the budget
    # for the beam and cap the floor at the other half; the first floor passage
    # is still never dropped, since the floor is the subject's own page.
    beam_reserves = token_budget // 2 if floor else 0
    floor_ids = {passage.chunk_id for passage in floor}
    ordered = [*floor, *(p for p in result.passages if p.chunk_id not in floor_ids)]
    for order, passage in enumerate(ordered, start=1):
        cost = estimate_tokens(passage.text) + 30
        limit = (
            token_budget - beam_reserves
            if passage.chunk_id in floor_ids
            else token_budget
        )
        if used + cost > limit and beats:
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

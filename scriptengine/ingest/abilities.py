"""Index-time extraction of the abilities a wiki only writes as prose.

Half of what a character-scoped question asks for is not an entity anywhere.
Measured across seventeen questions and their online canon, 47 of 113 items
exist as pages and 20 more as section headings — the other 57 exist only inside
a paragraph:

    Killua Zoldyck   §Abilities & Powers / Nen
        "…Godspeed… Whirlwind… Speed of Lightning…"

Hunterpedia gives none of those a page, files them under no category, and
records no `users` field pointing at Killua. Neither the ownership path nor the
heading path can reach them, and no structural rule ever will: the chunk text
carries no markup at all, so there is nothing to key on but the sentence.

So a local model reads the ability sections of a character's page, once, at
index time. This mirrors `ingest/classify.py` deliberately rather than
inventing a second mechanism, and inherits the three rules that make that one
safe to trust:

* **It never runs during a query.** Retrieval reads the `abilities` table. The
  same question answers the same way twice and the eval sets stay meaningful.
* **It is asked only where the prose is the only source** — the character pages
  a series declares `ability_sections` for, a few hundred per wiki at most.
* **It may only name what the section names.** The prompt forbids recall from
  the model's own knowledge of the series, because a model that has read the
  manga will happily supply abilities this wiki never mentions, and those are
  indistinguishable from retrieved ones once stored.

Every row keeps the section it came from and a one-line reason, so an
extraction that looks wrong can be argued with rather than guessed at.
"""

from __future__ import annotations

import json
import logging
import os
import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings, load_overrides
from scriptengine.llm.client import LLMClient, LLMUnavailable
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

# Bump to invalidate every stored extraction. Anything that changes what the
# model is asked changes this — including what it is asked *about*: reading the
# page lead (`_is_lead`) widened the passages without touching the prompt, and
# the seven already-extracted series would have kept their cached answers
# through it. The `-opencode` suffix is dropped because extraction runs against
# LM Studio now; the model each row was produced by is stored on the row.
#
# 2026-08-15.1 adds the colon rule. The bank counts the wiki's graded stat lines
# as abilities -- `Immense Speed & Reflexes`, `Great Tactical Intellect`,
# `Cursed Energy Capacity` -- and 64 canon items were missing because the "a
# name, not a description" rule read straight past them. They are named: the
# wiki writes `Name: description` at the head of a paragraph, and that colon is
# visible in the passage even after the bold markers are stripped.
PROMPT_VERSION = "2026-08-15.1"

# What an extracted ability may be called, in the vocabulary `semantics` speaks
# so the retrieval side can filter on the same words it filters pages by.
KINDS = ("technique", "transformation", "item")

SYSTEM = (
    "You extract named abilities from fiction-wiki prose. You answer with JSON "
    "only — no prose, no code fences. You never name anything the passage does "
    "not name, however well you know the series."
)

_TEMPLATE = """List the named abilities this passage attributes to {character}.

Series: {series}
Character: {character}
Section: {section}

Passage:
{passage}

Answer with JSON exactly in this shape:
{{"abilities": [{{"name": "...", "kind": "...", "reason": "one short clause"}}]}}

`kind` must be one of: {kinds}.

Rules:
- Only names that appear in the passage. If the passage names none, answer
  {{"abilities": []}} — an empty answer is correct and useful.
- Only what belongs to {character}. A passage comparing them to someone else
  still names the other person's abilities; those are not theirs.
- A proper name for a specific ability, not a description of it. "Godspeed" is
  an ability; "extremely fast" is not, and neither is "his electric powers".
- A line that opens with a name and a colon is the wiki naming an ability, and
  counts even when the name reads like a trait. "Immense Speed & Reflexes:
  Satoru is an extremely fast fighter" names `Immense Speed & Reflexes`;
  "Great Tactical Intellect: Sukuna is an extremely intelligent individual"
  names `Great Tactical Intellect`. The test is whether the passage gives it a
  name of its own, not whether the name sounds generic. The same capability
  mentioned only inside a sentence is still a description and stays out.
- Not the general system the ability belongs to. On a wiki with Nen, Haki or
  Cursed Energy, the system itself is not one of the character's abilities.
- Give the name as the passage writes it, without honorifics or the character's
  name attached."""


@dataclass(frozen=True)
class Extraction:
    character: str
    section: str
    abilities: list[dict[str, str]]


def needs_extracting(store: FactStore, overrides: dict | None = None) -> list[str]:
    """The character pages whose abilities live in prose on this wiki.

    Driven by the same `ability_sections:` declaration retrieval uses, so a
    series that declares none is skipped entirely — Dragon Ball records
    ownership as edges and needs no inference at all.
    """
    declared = (overrides or {}).get("ability_sections") or {}
    wanted = {
        str(section).strip().lower()
        for sections in declared.values()
        for section in sections
        if str(section).strip()
    }
    if not wanted:
        return []

    # One query rather than a `sections_of` call per page: these wikis hold
    # tens of thousands of pages, and asking each in turn is minutes of SQLite
    # before a single token is generated.
    clauses = " OR ".join(
        ["c.breadcrumb LIKE ? COLLATE NOCASE"] * len(wanted)
        + ["d.title LIKE ? COLLATE NOCASE"] * len(wanted)
    )
    values = [f"{section}%" for section in wanted] + [f"%{section}%" for section in wanted]
    # Ordered by how much ability prose there is, because that is what makes a
    # character worth the inference: a wiki has hundreds of pages carrying an
    # `Abilities & Powers` heading and a sentence under it, and the ones a
    # question is ever going to ask about are the ones with paragraphs. This is
    # what makes `--limit` mean "the characters that matter" rather than "the
    # first few alphabetically" — which is otherwise 288th Hunter Exam's 1st
    # Phase Examiner, Abaki, Abengane.
    rows = store.connection.execute(
        "SELECT CASE WHEN instr(d.title, '/') > 0"
        "            THEN substr(d.title, 1, instr(d.title, '/') - 1)"
        "            ELSE d.title END AS root,"
        "       SUM(LENGTH(c.text)) AS weight"
        " FROM documents d JOIN chunks c ON c.document_id = d.id"
        f" WHERE {clauses}"
        " GROUP BY root ORDER BY weight DESC",
        values,
    ).fetchall()
    return [row["root"] for row in rows if row["root"]]


def _matches(section: str, breadcrumb: str, title: str) -> bool:
    """Whether a section path is one the series declared as holding abilities."""
    head = breadcrumb.split("/", 1)[0].strip().lower()
    return section in head or section in title.lower()


def _is_lead(breadcrumb: str, title: str) -> bool:
    """Whether this is the page's own opening section.

    A wiki lead summarises the character, and on Hunterpedia that summary is
    where three of Kurapika's four chains are named — `Holy Chain`,
    `Steal Chain` and `Emperor Time` appear there and nowhere else on any page
    of his. The lead is about the character by definition, which is what
    separates it from the plot and synopsis sections deliberately left out:
    those recap episodes, and an ability named in a fight recap is being
    described rather than defined.
    """
    crumb = (breadcrumb or "").strip().lower()
    return bool(crumb) and crumb == (title or "").strip().lower()


def passages(store: FactStore, character: str, overrides: dict) -> list[tuple[str, str]]:
    """The ability prose for one character, one entry per section.

    Sections are read whole rather than chunk by chunk: the abilities are named
    across a paragraph, and splitting it costs the model the sentence that says
    whose they are.
    """
    declared = (overrides or {}).get("ability_sections") or {}
    wanted = {
        str(section).strip().lower()
        for sections in declared.values()
        for section in sections
        if str(section).strip()
    }
    out: list[tuple[str, str]] = []
    for row in store.sections_of(character):
        breadcrumb = row["breadcrumb"] or ""
        title = row["title"] or ""
        if not (any(_matches(section, breadcrumb, title) for section in wanted)
                or _is_lead(breadcrumb, title)):
            continue
        text = (row["text"] or "").strip()
        if len(text) < 120:
            # A heading with nothing under it names nothing.
            continue
        out.append((breadcrumb or title, text))
    return out


_JSON = re.compile(r"\{.*\}", re.S)


def parse_response(text: str) -> list[dict[str, str]]:
    """Read the model's JSON, tolerating the fences it was told not to use."""
    match = _JSON.search(text or "")
    if not match:
        return []
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, dict):
        return []

    found: list[dict[str, str]] = []
    for entry in payload.get("abilities") or []:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name") or "").strip()
        if not name or len(name) > 80:
            continue
        # A named ability is a proper noun. Told not to return descriptions,
        # the model returned "master swordsmanship", "combat pragmatism" and
        # "uses children to bait and distract enemies" for Guts, and "electric
        # aura" for Killua — all lower case, while every real one it found is
        # not: Godspeed, Chain Jail, Whirlwind, Speed of Lightning, Rhythm
        # Echo. Wikis capitalise the things they have named, so the shape of
        # the string carries the distinction the instruction could not.
        if not name[0].isupper():
            continue
        # A sentence also starts with a capital. "Sleeping with a larger part of
        # his brain awake" and "Holding his breath for some minutes even if
        # fatigued" both cleared the rule above; the longest ability name
        # measured is four words.
        if len(name.split()) > 5:
            continue
        kind = str(entry.get("kind") or "").strip().lower()
        found.append({
            "name": name,
            "kind": kind if kind in KINDS else "technique",
            "reason": str(entry.get("reason") or "").strip()[:200],
        })
    return found


def extract_character(
    client: LLMClient, store: FactStore, series: str, character: str, overrides: dict
) -> list[dict[str, str]]:
    """Every named ability the wiki's prose gives this character."""
    from scriptengine.retrieve.roster import ability_stopwords

    # The power system a series runs on is not one character's ability. The
    # prompt says so and the model mostly obeys, but "mostly" left 129 of 345
    # Hunter x Hunter rows reading Ten, Ren, Zetsu, Gyo.
    stopwords = ability_stopwords(overrides)
    found: list[dict[str, str]] = []
    seen: set[str] = set()
    for section, text in passages(store, character, overrides):
        for window in _windows(text):
            prompt = _TEMPLATE.format(
                series=series,
                character=character,
                section=section,
                passage=window,
                kinds=", ".join(KINDS),
            )
            # Generous, because the local models are thinking models. Gemma 4
            # spends about 4,000 tokens reasoning over a 4,000-character
            # passage before it writes a word of the answer; at 4,000 it hits
            # the ceiling mid-thought and returns nothing, which looks exactly
            # like "this passage names nothing".
            answer = client.complete(
                prompt, system=SYSTEM, temperature=0.0, max_tokens=_answer_budget()
            )
            for entry in parse_response(answer):
                key = entry["name"].strip().lower()
                # The character's own name is not one of their abilities, and a
                # section heading repeated back is not one either.
                if key in seen or key == character.lower() or key in section.lower():
                    continue
                if key in stopwords:
                    continue
                # It has to be in the passage. Measured over 2,841 stored rows,
                # the local model produced 91 names that appear nowhere in the
                # text it was shown — `Fireball shooting`, `Sword fighting`,
                # `Cero Barrage`, `Ghostly Wolf Summoning`. Several describe
                # something the character really does; none is what the wiki
                # calls it, and a name the source never uses cannot be cited.
                if not _grounded_in(entry["name"], window, section):
                    logger.info("ungrounded %r for %s", entry["name"], character)
                    continue
                seen.add(key)
                entry["section"] = section
                found.append(entry)
    return found


def _answer_budget() -> int:
    """Room for a thinking model to think *and* answer.

    Gemma 4 spends about 4,000 tokens reasoning over a 4,000-character passage
    and more on a dense one; at 4,000 it stopped mid-thought and returned
    nothing, which is indistinguishable from "this passage names nothing".
    Configurable because how much a model thinks is a property of the model.
    """
    return int(os.environ.get("SCRIPTENGINE_ANSWER_TOKENS", "32000"))


def _grounded_in(name: str, passage: str, section: str) -> bool:
    """Whether the passage actually calls it that.

    The heading counts as much as the prose: `Equipment / Cannon Arm` names the
    thing the paragraph under it describes, and reading only the body marked
    every one of those as invented.

    This is a citation test rather than a truth test. Coyote Starrk really does
    summon wolves; the wiki simply never writes "Ghostly Wolf Summoning", so a
    script quoting that phrase would be quoting the model rather than the
    source.
    """
    return _fold(name) in _fold(f"{section} {passage}")


def _fold(text: str) -> str:
    """Compare on letters and digits, ignoring case, accents and punctuation.

    Whitespace is collapsed rather than merely substituted. Stripping the
    Japanese out of `Bang! (バン！)` leaves five spaces where it was, and a
    padded string matches nothing — Makima's real named ability would have been
    dropped as invented.
    """
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def _windows(text: str, size: int = 4000, overlap: int = 300) -> list[str]:
    """Split a section so none of it goes unread.

    Killua's `Abilities & Powers` runs to 17,672 characters. Sending the first
    4,000 returned Whirlwind and Speed of Lightning and missed Godspeed,
    Lightning Palm and Thunderbolt — not because the model could not find them
    but because it was never shown them. The overlap keeps an ability named
    across a window boundary from falling between two requests.
    """
    if len(text) <= size:
        return [text]
    out: list[str] = []
    start = 0
    while start < len(text):
        out.append(text[start:start + size])
        start += size - overlap
    return out


def _revid(store: FactStore, title: str) -> str:
    row = store.connection.execute(
        "SELECT revid FROM documents WHERE title = ? COLLATE NOCASE", (title,)
    ).fetchone()
    return str(row["revid"] if row else "") or ""


def extract_series(
    paths: SeriesPaths,
    settings: Settings | None = None,
    limit: int | None = None,
    refresh: bool = False,
    progress: Any = None,
) -> dict[str, Any]:
    """Extract this series' prose-only abilities, skipping what is current.

    Cached on `revid` and `PROMPT_VERSION` exactly as classification is, so a
    second run costs nothing and a re-crawl pays only for what changed.
    """
    settings = settings or get_settings()
    overrides = load_overrides(paths)
    client = LLMClient(settings)
    if not client.available():
        raise LLMUnavailable(
            f"No model at {client.base_url}. Start Ollama, or set "
            "SCRIPTENGINE_LLM_BASE_URL."
        )

    report = {"considered": 0, "extracted": 0, "cached": 0, "failed": 0, "abilities": 0}
    with FactStore(paths.facts_db) as store:
        store.ensure_abilities()
        characters = needs_extracting(store, overrides)
        report["considered"] = len(characters)

        for character in (characters[:limit] if limit else characters):
            revid = _revid(store, character)
            state = store.extraction_state(character)
            current = (
                state
                and not refresh
                and state["prompt_version"] == PROMPT_VERSION
                and str(state["revid"] or "") == revid
            )
            if current:
                report["cached"] += 1
                continue

            try:
                found = extract_character(
                    client, store, paths.name, character, overrides
                )
            except LLMUnavailable:
                raise
            except Exception as error:  # noqa: BLE001 - one page must not stop the run
                logger.warning("Extracting %r failed: %s", character, error)
                report["failed"] += 1
                continue

            store.save_abilities(
                character=character,
                found=found,
                revid=int(revid) if revid.isdigit() else None,
                prompt_version=PROMPT_VERSION,
                model=settings.llm_model,
            )
            report["extracted"] += 1
            report["abilities"] += len(found)
            if progress is not None:
                progress(character, len(found))
    return report

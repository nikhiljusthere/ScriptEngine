"""Index-time extraction of the abilities a wiki only writes as prose.

Half of what a character-scoped question asks for is not an entity anywhere.
Measured across seventeen questions and their online canon, 47 of 113 items
exist as pages and 20 more as section headings; the other 57 exist only inside
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
* **It is asked only where the prose is the only source.** The character pages
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
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings, load_overrides
from scriptengine.llm.client import LLMClient, LLMRateLimited, LLMUnavailable
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

# Bump to invalidate every stored extraction. Anything that changes what the
# model is asked changes this, including what it is asked *about*: reading the
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
PROMPT_VERSION = "2026-08-15.3"

# What an extracted ability may be called, in the vocabulary `semantics` speaks
# so the retrieval side can filter on the same words it filters pages by.
KINDS = ("technique", "transformation", "trait", "item")

# How a character came by an ability. `innate` is the default and the common
# case; the rest exist because the wiki says so and a script needs the
# difference. Yuta Okkotsu's technique *is* copying, so `Limitless` and
# `Unlimited Void` are genuinely his to use and genuinely not his own -- stored
# flat they answered "Every cursed technique of Yuta Okkotsu" with Gojo's kit.
#
# Recorded beside the name rather than folded into it. `Limitless` has its own
# page, which is what the citation resolves against, and the extraction gate
# requires the name to appear in the passage verbatim -- so a row called
# `Copied Limitless` would be thrown away by the guard that keeps this store
# honest, and lose its page link on the way.
ACQUIRED = ("innate", "copied", "inherited", "granted")

SYSTEM = (
    "You extract named abilities from fiction-wiki prose. You answer with JSON "
    "only: no prose, no code fences. You never name anything the passage does "
    "not name, however well you know the series."
)

_TEMPLATE = """List the named abilities this passage attributes to {character}.

Series: {series}
Character: {character}
Section: {section}

Passage:
{passage}

Answer with JSON exactly in this shape:
{{"abilities": [{{"name": "...", "kind": "...", "acquired": "...", "reason": "one short clause"}}]}}

`kind` must be one of: {kinds}.
`acquired` must be one of: {acquired}. Use `innate` unless the passage says
otherwise.

Rules:
- Only names that appear in the passage. If the passage names none, answer
  {{"abilities": []}}. An empty answer is correct and useful.
- Only what belongs to {character}. A passage comparing them to someone else
  still names the other person's abilities; those are not theirs.
- A proper name for a specific ability, not a description of it. "Godspeed" is
  an ability; "extremely fast" is not, and neither is "his electric powers".
- `trait` is for a graded capability the wiki names but does not treat as a
  technique: `Immense Strength`, `Great Tactical Intellect`, `Cursed Energy
  Capacity`, `Master Swordsman`. `technique` is for a named move or power with
  its own identity: `Godspeed`, `Black Flash`, `Limitless`. If the name grades
  something the character simply has, it is a `trait`.
- `acquired` is `copied` when the passage says this character copied the ability
  from someone else, `inherited` when it came down a family or clan, `granted`
  when someone gave it to them, and `innate` otherwise. Yuta Okkotsu's page says
  his technique "allows him to copy the innate techniques of people who had
  their body parts consumed by Rika" -- everything he copies is `copied`, and
  the copying itself is `innate`.
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
    series that declares none is skipped entirely; Dragon Ball records
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
    # first few alphabetically", which is otherwise 288th Hunter Exam's 1st
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
    where three of Kurapika's four chains are named: `Holy Chain`,
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
    return out + owned_passages(store, character, overrides)


def owned_passages(
    store: FactStore, character: str, overrides: dict
) -> list[tuple[str, str]]:
    """Ability prose on the pages a character *owns*, not on their own page.

    One Piece nests one level deeper than the other wikis. The character page
    names the fighting *styles*, each style has its own page, and the named
    techniques are prose inside that page:

        Roronoa Zoro        ->  Three Sword Style, Two Sword Style, ...
        Three Sword Style   ->  Oni Giri, Shishi Sonson, Tatsumaki, Ashura, ...

    Reading only character pages therefore returns the styles and stops.
    Measured on `Every technique of Zoro`: 10 canon items and 1 found, while
    `Three Sword Style` held most of the rest and had never been read by
    anything -- it is a technique page, and extraction only ever asked about
    characters.

    The link is one the wiki already recorded, `Three Sword Style -user->
    Roronoa Zoro`, so this walks that edge backwards and reads the declared
    sections of what comes back. Nothing is inferred: a page is read only
    because the wiki named this character in one of the declared fields.

    Off unless a series declares it, since most wikis keep the techniques on the
    character and this would only add noise there:

        ability_owner_sections:
          relations: [user, users]
          sections: [Techniques]
    """
    declared = (overrides or {}).get("ability_owner_sections") or {}
    sections = [
        str(section).strip().lower()
        for section in (declared.get("sections") or [])
        if str(section).strip()
    ]
    if not sections:
        return []
    relations = [
        str(relation).strip()
        for relation in (declared.get("relations") or ["user", "users"])
        if str(relation).strip()
    ]

    out: list[tuple[str, str]] = []
    for page in store.owned_by(character, relations):
        # The character's own pages are already covered by the caller.
        if page.split("/")[0].strip().lower() == (character or "").strip().lower():
            continue
        for row in store.sections_of(page):
            breadcrumb = row["breadcrumb"] or ""
            title = row["title"] or ""
            if not any(_matches(section, breadcrumb, title) for section in sections):
                continue
            text = (row["text"] or "").strip()
            if len(text) < 120:
                continue
            # The page goes in the section label, so a stored row still says
            # where it was read from. That is what `abilities.section` is for,
            # and it keeps these rows tellable from ones read off the character.
            out.append((f"{page} / {breadcrumb or title}", text))
    return out


_JSON = re.compile(r"\{.*\}", re.S)


def parse_response(text: str, keep: tuple[str, ...] = ()) -> list[dict[str, str]]:
    """Read the model's JSON, tolerating the fences it was told not to use.

    `keep` names extra fields to carry through. The rows this builds are fresh
    dicts rather than the model's, so a caller asking for a field this function
    does not know about got an empty string and no error. `narrative_abilities`
    asks for `owner`, and without it every one of its rows failed the
    `if not name or not owner` guard: 927 windows, 0 rows, 0 failures, on a
    pass that could never have stored anything on any wiki.
    """
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
        # aura" for Killua, all lower case, while every real one it found is
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
        row = {
            "name": name,
            "kind": kind if kind in KINDS else "technique",
            "reason": str(entry.get("reason") or "").strip()[:200],
        }
        for field in keep:
            row[field] = str(entry.get(field) or "").strip()
        found.append(row)
    return found


def extract_character(
    client: LLMClient, store: FactStore, series: str, character: str, overrides: dict
) -> list[dict[str, str]]:
    """Every named ability the wiki's prose gives this character."""
    return extract_from_passages(
        client, series, character, passages(store, character, overrides), overrides
    )


def extract_from_passages(
    client: LLMClient,
    series: str,
    character: str,
    found_passages: list[tuple[str, str]],
    overrides: dict,
) -> list[dict[str, str]]:
    """The same extraction, over passages already read.

    Split out from `extract_character` so the expensive part can run on a worker
    thread. Everything here is prompt-building, network and string work; the
    store is touched only to *fetch* the passages, which stays on the thread
    that owns the connection, because a `sqlite3` connection belongs to one
    thread and the run writes to the same file it is reading.
    """
    from scriptengine.retrieve.roster import ability_stopwords

    # The power system a series runs on is not one character's ability. The
    # prompt says so and the model mostly obeys, but "mostly" left 129 of 345
    # Hunter x Hunter rows reading Ten, Ren, Zetsu, Gyo.
    stopwords = ability_stopwords(overrides)
    found: list[dict[str, str]] = []
    seen: set[str] = set()
    for section, text in found_passages:
        for window in _windows(text):
            prompt = _TEMPLATE.format(
                series=series,
                character=character,
                section=section,
                passage=window,
                kinds=", ".join(KINDS),
                acquired=", ".join(ACQUIRED),
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
                # text it was shown: `Fireball shooting`, `Sword fighting`,
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
    padded string matches nothing; Makima's real named ability would have been
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
    Lightning Palm and Thunderbolt, not because the model could not find them
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
    workers: int = 1,
    only: set[str] | None = None,
) -> dict[str, Any]:
    """Extract this series' prose-only abilities, skipping what is current.

    Cached on `revid` and `PROMPT_VERSION` exactly as classification is, so a
    second run costs nothing and a re-crawl pays only for what changed.

    `workers` runs that many extractions at once. It is worth setting only for
    the `opencode` backend, where a call is a subprocess waiting on somebody
    else's API: measured at 89s per character against a local model's 25s, but
    3,365 characters is 83 hours in one line and the wait is not this machine's
    to spend. A local backend should stay at 1: it is one GPU, and asking it
    for eight answers at once does not make it finish sooner.
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

        # Reading every character is mostly waste. One Piece alone has 1,640
        # candidates at 12.5 windows each -- about 20,500 of the corpus's
        # ~30,000 calls -- and the bank asks about a few dozen of them. The
        # bank is what the engine is measured against, so a character no
        # question reaches cannot change the number either way.
        #
        # Not the default: the store is also read by hand and by narrative
        # retrieval, where a character outside the bank is still worth having.
        if only:
            wanted_names = {name.strip().lower() for name in only}
            characters = [
                name for name in characters if name.strip().lower() in wanted_names
            ]
        report["considered"] = len(characters)

        wanted = characters[:limit] if limit else characters

        # What is still owed, after the cache. Settled up front so the pool is
        # never handed work that a cache hit would have skipped.
        todo: list[tuple[str, str]] = []
        for character in wanted:
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
            todo.append((character, revid))

        def store_result(character: str, revid: str, found: list[dict[str, str]]):
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

        if workers <= 1:
            for character, revid in todo:
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
                store_result(character, revid, found)
            return report

        # A chunk at a time rather than one big submit: passages are read on
        # this thread, and holding all of them for a wiki the size of One Piece
        # (1,640 characters) would be pointless when the pool can only be
        # working on `workers` of them. Saving per chunk also means an
        # interrupted run keeps everything it already paid for.
        #
        # Timeouts are retried once at the end, at a quarter of the width. They
        # are a transient of asking a shared API for too much at once, not a
        # property of the character: a first jjk pass at 16 workers lost 33 of
        # 63 characters to `opencode timed out after 300s`, and losing a page
        # for the run costs more than paying for it twice.
        retry: list[tuple[str, str]] = []
        for start in range(0, len(todo), workers * 4):
            chunk = todo[start : start + workers * 4]
            work = [
                (character, revid, passages(store, character, overrides))
                for character, revid in chunk
            ]

            def run(job):
                character, _, found_passages = job
                return extract_from_passages(
                    client, paths.name, character, found_passages, overrides
                )

            with ThreadPoolExecutor(max_workers=workers) as pool:
                for (character, revid, _), outcome in zip(
                    work, pool.map(_guarded(run), work)
                ):
                    if isinstance(outcome, BaseException):
                        # Throttling means every later call fails too, so it
                        # stops the run rather than filling the store with the
                        # empty results of a provider saying no.
                        if isinstance(outcome, LLMRateLimited):
                            raise outcome
                        logger.warning(
                            "Extracting %r failed: %s", character, outcome
                        )
                        retry.append((character, revid))
                        continue
                    store_result(character, revid, outcome)

        if retry:
            logger.warning("Retrying %d character(s) that failed", len(retry))
            narrow = max(1, workers // 4)
            for start in range(0, len(retry), narrow * 4):
                chunk = retry[start : start + narrow * 4]
                work = [
                    (character, revid, passages(store, character, overrides))
                    for character, revid in chunk
                ]

                def run_again(job):
                    character, _, found_passages = job
                    return extract_from_passages(
                        client, paths.name, character, found_passages, overrides
                    )

                with ThreadPoolExecutor(max_workers=narrow) as pool:
                    for (character, revid, _), outcome in zip(
                        work, pool.map(_guarded(run_again), work)
                    ):
                        if isinstance(outcome, BaseException):
                            if isinstance(outcome, LLMRateLimited):
                                raise outcome
                            logger.warning(
                                "Extracting %r failed twice: %s", character, outcome
                            )
                            report["failed"] += 1
                            continue
                        store_result(character, revid, outcome)
    return report


def _guarded(run):
    """Run a job, returning the exception instead of raising it.

    `ThreadPoolExecutor.map` re-raises on first failure and abandons the rest of
    the batch. One character's page failing must cost that character only; the
    same rule the serial path has always followed.
    """

    def attempt(job):
        try:
            return run(job)
        except BaseException as error:  # noqa: BLE001 - handed back to the caller
            return error

    return attempt

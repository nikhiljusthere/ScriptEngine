"""Abilities a wiki only ever shows happening, in a chapter or episode summary.

`ingest/abilities.py` reads a character's own ability sections. That is where a
wiki lists what someone *has*, and it misses everything the wiki only records as
something that *happened*:

    Chapter 216 / Trivia   "Makima's contract with the Prime Minister of Japan,
                            i.e. redirecting any lethal injuries or damage done
                            on them towards ..."
    Chapter 90  / Summary  "blood weapons suddenly pushing out from within the
                            bodies of her and the Public Safety members"

Neither is on Makima's or Power's page in any form. Both were scored as items
the corpus did not contain, and the corpus contained them the whole time.

**This pass reads pages, not characters.** Reading per character would re-read
the same chapter once for everyone it mentions: on Chainsaw Man, Denji alone
appears in 664 chapter chunks totalling 963,433 characters, and the series has
175 characters over 1,029 such chunks. Read once per page and attributed by the
model, the whole series is about 290 windows.

So the model is asked a different question from the one `abilities.py` asks. It
is given a passage with no subject and must name both the ability *and* whose it
is, which is the same shape `ingest/relations.py` uses, and it is guarded the
same way:

* the ability name must appear in the passage verbatim;
* the owner must resolve to a page this wiki types as a character;
* the owner must be named in the passage, so "everyone knows whose that is"
  cannot get through.

Rows are added rather than replacing, and never overwrite a row read from a
character's own page. A chapter summary is the weaker of the two sources: it
shows an ability being used without necessarily naming it the way the wiki's own
ability list does.

Off unless a series declares which page types to read:

    ability_narrative_types: [chapter_box, episode]
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

from scriptengine.config import SeriesPaths, Settings, get_settings, load_overrides
from scriptengine.ingest.abilities import (
    KINDS,
    _grounded_in,
    _windows,
    parse_response,
)
from scriptengine.llm.client import LLMClient, LLMRateLimited, LLMUnavailable
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

# Separate from `abilities.PROMPT_VERSION`: this is a different question over
# different text, and bumping one must not invalidate the other.
PROMPT_VERSION = "2026-08-16.1"

SYSTEM = (
    "You extract named abilities, and whose they are, from fiction-wiki story "
    "summaries. You answer with JSON only: no prose, no code fences. You never "
    "name anything the passage does not name, however well you know the series."
)

_TEMPLATE = """List the named abilities this passage shows being used, and who used each one.

Series: {series}
Page: {page}
Section: {section}

Passage:
{passage}

Answer with JSON exactly in this shape:
{{"abilities": [{{"name": "...", "owner": "...", "kind": "...", "reason": "one short clause"}}]}}

`kind` must be one of: {kinds}.

Rules:
- Only names that appear in the passage. If it names none, answer
  {{"abilities": []}}. An empty answer is correct and useful.
- `owner` must be a character named in this passage. If the passage does not say
  whose the ability is, leave it out entirely rather than guessing.
- A proper name for a specific ability, not a description of it. "Blood weapons"
  is an ability; "she was very strong" is not.
- This is a story summary, so most of it is events rather than abilities. Naming
  nothing is the common and correct answer.
"""


def passages(store: FactStore, overrides: dict) -> list[tuple[str, str, str]]:
    """`(page, section, text)` for the page types this series declares."""
    declared = [
        str(t).strip()
        for t in ((overrides or {}).get("ability_narrative_types") or [])
        if str(t).strip()
    ]
    if not declared:
        return []
    marks = ",".join("?" * len(declared))
    rows = store.connection.execute(
        "SELECT DISTINCT d.title AS title, c.breadcrumb AS breadcrumb,"
        "       c.text AS text"
        f" FROM chunks c JOIN documents d ON c.document_id = d.id"
        f" WHERE d.page_type IN ({marks})"
        " ORDER BY d.title, c.ordinal",
        declared,
    ).fetchall()
    out: list[tuple[str, str, str]] = []
    for row in rows:
        text = (row["text"] or "").strip()
        if len(text) < 200:
            continue
        out.append((row["title"], row["breadcrumb"] or row["title"], text))
    return out


def extract_from_passage(
    client: LLMClient,
    series: str,
    page: str,
    section: str,
    text: str,
    characters: dict[str, str],
    stopwords: set[str],
) -> list[tuple[str, dict[str, str]]]:
    """`(owner, row)` for one passage. Thread-safe: touches no store."""
    from scriptengine.ingest.abilities import _answer_budget

    found: list[tuple[str, dict[str, str]]] = []
    for window in _windows(text):
        prompt = _TEMPLATE.format(
            series=series, page=page, section=section,
            passage=window, kinds=", ".join(KINDS),
        )
        answer = client.complete(
            prompt, system=SYSTEM, temperature=0.0, max_tokens=_answer_budget()
        )
        for entry in parse_response(answer, keep=("owner",)):
            name = str(entry.get("name") or "").strip()
            owner = str(entry.get("owner") or "").strip()
            if not name or not owner:
                continue
            if name.strip().lower() in stopwords:
                continue
            # The owner has to be somebody this wiki types as a character, and
            # the model has to have read the name here rather than recalled it.
            canonical = characters.get(owner.lower())
            if not canonical:
                logger.info("no character %r on %s", owner, page)
                continue
            if owner.lower() not in window.lower():
                logger.info("owner %r not in the passage on %s", owner, page)
                continue
            if not _grounded_in(name, window, section):
                logger.info("ungrounded %r on %s", name, page)
                continue
            found.append((canonical, {
                "name": name,
                "kind": str(entry.get("kind") or "technique").strip().lower(),
                "reason": str(entry.get("reason") or "").strip(),
                # Provenance: a reader of the store can tell this row came from
                # a story summary rather than from an ability list.
                "section": f"{page} / {section}",
            }))
    return found


def known_characters(store: FactStore, overrides: dict) -> dict[str, str]:
    """`folded name -> canonical`, built on the connection-owning thread."""
    from scriptengine.retrieve import semantics as ont

    out: dict[str, str] = {}
    for row in store.connection.execute("SELECT name FROM nodes"):
        name = row["name"]
        if not name:
            continue
        if ont.semantic_type(store, name, overrides) == ont.CHARACTER:
            out[name.lower()] = name
    return out


def extract_series(
    paths: SeriesPaths,
    settings: Settings | None = None,
    limit: int = 0,
    workers: int = 1,
) -> dict[str, int]:
    """Read this series' declared narrative pages and store what they show."""
    from scriptengine.retrieve.roster import ability_stopwords

    settings = settings or get_settings()
    overrides = load_overrides(paths)
    client = LLMClient(settings)
    report = {"passages": 0, "windows": 0, "added": 0, "failed": 0}

    with FactStore(paths.facts_db) as store:
        store.ensure_abilities()
        found_passages = passages(store, overrides)
        if limit:
            found_passages = found_passages[:limit]
        report["passages"] = len(found_passages)
        if not found_passages:
            return report
        characters = known_characters(store, overrides)
        stopwords = ability_stopwords(overrides)
        report["windows"] = sum(len(_windows(t)) for _p, _s, t in found_passages)

        def run(job):
            page, section, text = job
            return extract_from_passage(
                client, paths.name, page, section, text, characters, stopwords
            )

        rows: list[tuple[str, dict[str, str]]] = []
        for start in range(0, len(found_passages), workers * 4):
            chunk = found_passages[start : start + workers * 4]
            with ThreadPoolExecutor(max_workers=workers) as pool:
                for outcome in pool.map(_guarded(run), chunk):
                    if isinstance(outcome, BaseException):
                        if isinstance(outcome, LLMRateLimited):
                            raise outcome
                        logger.warning("narrative page failed: %s", outcome)
                        report["failed"] += 1
                        continue
                    rows.extend(outcome)
            if rows:
                report["added"] += store.add_abilities(
                    rows, PROMPT_VERSION, settings.llm_model
                )
                rows = []
    return report


def _guarded(run):
    """Return the exception instead of raising, so one page cannot stop a run."""
    def inner(job):
        try:
            return run(job)
        except LLMRateLimited:
            raise
        except Exception as error:  # noqa: BLE001 - reported per page
            return error
    return inner

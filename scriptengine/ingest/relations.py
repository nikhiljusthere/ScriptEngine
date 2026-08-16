"""Index-time extraction of the relationships a wiki only writes as prose.

The infobox gives family and faction. `relatives`, `affiliation`, `occupation`,
`partner`: 239, 92, 104 and 15 edges on the Jujutsu Kaisen wiki. What it does
not give is the thing a script is actually built out of:

    Suguru Geto   §Relationships / Satoru Gojo
        "…the two were the strongest duo, until Geto defected…"

Nothing in the categories reaches that, no `users` field encodes it, and no
structural rule ever will, because it is a sentence. This is the same gap
`ingest/abilities.py` exists for, so this mirrors that module deliberately
rather than inventing a second mechanism, and inherits the rules that make it
safe to trust:

* **It never runs during a query.** Retrieval reads the `relations` table.
* **It is asked only where the prose is the only source.** The relationship
  and history sections of character pages.
* **It may only say what the passage says.** A model that has read the manga
  will happily supply a rivalry this wiki never mentions, and once stored that
  is indistinguishable from a retrieved one.

Three guards, all applied *after* the model answers, so a weaker model costs
recall rather than truth:

* the other end must resolve to an entity this wiki actually has, which is what
  stops a plausible-sounding invented character becoming a relationship;
* the evidence quote must appear in the passage verbatim, which is what stops
  a real pair of characters being given a relationship the page never states;
* the relation must be one of `RELATIONS`. Left open, a model writes "friend",
  "best friend", "former friend" and "close ally" for one relationship and the
  table stops being groupable. The quote is kept alongside so the nuance the
  vocabulary flattens is still there to read.

Relationships change. Gojo and Geto are classmates and then enemies, and a flat
triple would state something false for most of the story, so `era` carries the
arc or period when the passage names one, and the quote carries the rest.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from scriptengine.config import SeriesPaths, Settings, get_settings, load_overrides
from scriptengine.ingest.abilities import _fold, _windows
from scriptengine.llm.client import LLMClient, LLMRateLimited, LLMUnavailable
from scriptengine.stores.facts import FactStore

logger = logging.getLogger(__name__)

# Bump to invalidate every stored relation, exactly as `abilities` does.
PROMPT_VERSION = "2026-08-15.3"

# Directional, read from the subject: `(Gojo, Yuji, mentor)` is Gojo mentoring
# Yuji. Closed on purpose -- see the module docstring.
RELATIONS = (
    "family", "friend", "ally", "rival", "enemy", "mentor", "student",
    "superior", "subordinate", "romantic", "creator", "creation",
)

# Where a wiki writes relationships out. Overridable per series because the
# heading names differ; these are the ones measured across these eight wikis.
DEFAULT_SECTIONS = ("Relationships", "History")

SYSTEM = (
    "You extract stated relationships between characters from fiction-wiki "
    "prose. You answer with JSON only: no prose, no code fences. You never "
    "state a relationship the passage does not state, however well you know "
    "the series."
)

_TEMPLATE = """List the relationships this passage states between {character} and other characters.

Series: {series}
Character: {character}
Section: {section}

Passage:
{passage}

Answer with JSON exactly in this shape:
{{"relations": [{{"other": "...", "relation": "...", "era": "", "quote": "..."}}]}}

`relation` must be one of: {relations}.

Rules:
- Read every relation from {character}'s side, and mind the direction. If the
  passage says {character} taught someone, that is `mentor`; if someone taught
  {character}, that is `student`. This holds however the sentence is worded:
  "his top student being Garou" on Bang's page means Bang is the `mentor` of
  Garou, not the student; the person named after "student" is the student, and
  here that is Garou, not Bang. The same for `superior`/`subordinate` and
  `creator`/`creation`.
- `other` must be a character the passage names. Give the name as the passage
  writes it, without honorifics.
- `quote` must be copied from the passage word for word: the clause that
  states the relationship. Do not paraphrase it, shorten it or tidy it.
- If the passage states no relationship, answer {{"relations": []}}. An empty
  answer is correct and useful.
- Only relationships the passage actually states. Two characters appearing in
  the same sentence are not thereby allies, and fighting once is not `enemy`
  unless the passage frames it that way.
- `era` only when the passage names the period or arc the relationship belongs
  to: "during their student years", "after the Shibuya Incident". Leave it
  empty otherwise rather than guessing.
- A relationship that changed is two entries, each with the quote that supports
  it, not one averaged guess."""


def relation_sections(overrides: dict | None) -> tuple[str, ...]:
    declared = (overrides or {}).get("relation_sections") or []
    names = tuple(str(s).strip() for s in declared if str(s).strip())
    return names or DEFAULT_SECTIONS


def needs_relations(store: FactStore, overrides: dict | None = None) -> list[str]:
    """The character pages whose relationships live in prose on this wiki.

    Ordered by how much relationship prose there is, so `--limit` means "the
    characters that matter" rather than "the first few alphabetically": the
    same reason `abilities.needs_extracting` orders by weight.

    Restricted to pages that classify as characters. `History` is a heading on
    places and organisations too. `Shibuya`, `Jujutsu Headquarters`,
    `Ninja Village`, `Heroes` all reached this list on section name alone, and
    a relationship whose subject is a location is not a thing this table should
    hold. Abilities needs no such filter because only characters carry an
    `Abilities and Powers` section in the first place.
    """
    # Imported here rather than at module scope: `retrieve` imports the stores,
    # and the ingest side is loaded during indexing when that is still settling.
    from scriptengine.retrieve import semantics as ontology

    wanted = [s.lower() for s in relation_sections(overrides)]
    # The title clause matters as much as the breadcrumb one: a wiki that moves
    # relationships onto `<Character>/Relationships` writes the other people's
    # names as its headings, so nothing in the breadcrumb says "Relationships".
    clauses = " OR ".join(
        ["c.breadcrumb LIKE ? COLLATE NOCASE"] * len(wanted)
        + ["d.title LIKE ? COLLATE NOCASE"] * len(wanted)
    )
    values = [f"{section}%" for section in wanted] + [
        f"%/{section}" for section in wanted
    ]
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
    return [
        row["root"] for row in rows
        if row["root"]
        and ontology.semantic_type(store, row["root"], overrides) == "character"
    ]


def passages(store: FactStore, character: str, overrides: dict) -> list[tuple[str, str]]:
    """The relationship prose on this character's page and its subpages.

    A section counts when the breadcrumb starts with a declared name *or* when
    the wiki moved the whole thing onto a subpage of its own. One Punch Man does
    the latter: `Saitama/Relationships` holds 51 chunks and its breadcrumbs read
    `Hero Association / Genos`, `Hero Association / Bang`, `Hero Association /
    King` -- the headings are the other people, not the word "Relationships".

    Reading only the breadcrumb missed all of it, and with it the most important
    relationship in the series: Saitama and Genos came back with nothing at all.
    """
    wanted = [s.lower() for s in relation_sections(overrides)]
    found: list[tuple[str, str]] = []
    for row in store.connection.execute(
        "SELECT d.title, c.breadcrumb, c.text FROM chunks c"
        " JOIN documents d ON c.document_id = d.id"
        " WHERE (d.title = ? COLLATE NOCASE OR d.title LIKE ? COLLATE NOCASE)",
        (character, f"{character}/%"),
    ):
        breadcrumb = (row["breadcrumb"] or "").strip()
        head = breadcrumb.split("/", 1)[0].strip().lower()
        leaf = (row["title"] or "").split("/")[-1].strip().lower()
        if (head in wanted or leaf in wanted) and (row["text"] or "").strip():
            found.append((breadcrumb, row["text"]))
    return found


def parse_response(text: str) -> list[dict[str, str]]:
    """The model's JSON, or nothing. Never raises on a bad answer."""
    body = (text or "").strip()
    if body.startswith("```"):
        body = re.sub(r"^```[a-z]*\n?|\n?```$", "", body).strip()
    start, end = body.find("{"), body.rfind("}")
    if start < 0 or end <= start:
        return []
    try:
        data = json.loads(body[start : end + 1])
    except ValueError:
        return []
    rows = data.get("relations") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _quoted_in(quote: str, passage: str) -> bool:
    """Whether the passage really contains the clause the model quoted.

    Whitespace is normalised and diacritics folded, because a model reflows a
    line it copied correctly. Nothing else is relaxed: this is the check that
    stops a real pair of characters being handed a relationship the page never
    states, which is the failure that would be invisible in the stored row.
    """
    if not quote or len(quote.strip()) < 12:
        return False
    tidy = lambda s: re.sub(r"\s+", " ", _fold(s).lower()).strip()
    return tidy(quote) in tidy(passage)


def known_arcs(store: FactStore) -> dict[str, str]:
    """This wiki's arc names, folded, for putting an era in story order.

    A relationship is often true for part of a story and false for the rest.
    Frieza is an enemy for the whole of Dragon Ball Z and an ally during the
    Tournament of Power; a sorcerer is Grade 1 until they are promoted. Stored
    without a period, both readings are equally true and a script cannot tell
    which came first.

    Measured over the first run, 20 Jujutsu Kaisen pairs and 64 One Punch Man
    pairs already hold more than one relation -- `Choso <-> Noritoshi Kamo` is
    both `family` and `enemy` -- so the readings are being captured. What was
    missing is *when*.

    Folded because the model writes the arc as the prose does. jjk matched 19 of
    28 eras to an arc exactly and opm matched 0 of 21, while writing
    `Monster Association arc` for `Monster Association Arc` -- a difference of
    one capital letter.
    """
    from scriptengine.retrieve import chronology

    return {arc.strip().lower(): arc for arc in chronology.arc_pages(store) if arc}


def _era_for(said: str, section: str, arcs: dict[str, str]) -> str:
    """The period a relation belongs to: what the model said, or where it sat.

    An arc name is preferred over free text because it can be ordered against
    the wiki's own `previous`/`next` chain. `during their student years` cannot.

    Falling back to the section is not a guess: a relationship extracted from
    the prose under `History / Gojo's Past Arc` belongs to that arc by
    construction. 63 of 109 Jujutsu Kaisen rows sit under an arc-named section
    while only 28 carried an era of their own.
    """
    said = (said or "").strip()
    if said:
        hit = arcs.get(said.lower())
        if hit:
            return hit
        # `Monster Association arc` for `Monster Association Arc`.
        loose = arcs.get(re.sub(r"\s+arc$", " arc", said.lower()))
        if loose:
            return loose
    for part in (part.strip() for part in (section or "").split("/")):
        if part.lower() in arcs:
            return arcs[part.lower()]
    return said


def known_names(store: FactStore, overrides: dict | None = None) -> dict[str, str]:
    """Every name this wiki has an entity for, folded, to its canonical title.

    A map rather than a set so the stored row can say who the wiki calls this.
    The prose writes `Geto` and `Suguru Geto` in the same paragraph, and stored
    verbatim they become two people: the table stops joining, and a script
    asking who Gojo fell out with gets the answer twice under different names.

    Read once on the thread that owns the connection and handed to the workers
    as a plain set. The first cut of this passed the `FactStore` itself so the
    guard could call `node_by_name`, and every threaded extraction died with
    `SQLite objects created in a thread can only be used in that same thread` --
    25 characters considered, 22 failed, nothing stored. A connection belongs to
    one thread, which is the same reason `passages()` is read by the caller.

    Aliases are included: the prose says `Gojo` where the page is titled
    `Satoru Gojo`, and a relationship naming the short form is not an invention.
    """
    from scriptengine.retrieve import semantics as ontology

    canon: dict[str, str] = {}
    for row in store.connection.execute("SELECT name FROM nodes"):
        name = (row["name"] or "").strip()
        # Characters only. Every fight has a page and therefore a node, so
        # without this the other end of a relationship comes back as
        # `Maki Zenin, Hagane Daido & Rokujushi Miyo vs. Naoya Zenin` -- a real
        # entity on this wiki, and not a person anyone has a relationship with.
        if name and ontology.semantic_type(store, name, overrides) == "character":
            canon[name.lower()] = name
    for row in store.connection.execute(
        "SELECT a.alias, n.name FROM aliases a JOIN nodes n ON n.id = a.node_id"
    ):
        alias = (row["alias"] or "").strip().lower()
        target = (row["name"] or "").strip()
        # A page title always wins over an alias pointing elsewhere.
        if alias and target and alias not in canon and target.lower() in canon:
            canon[alias] = target
    return canon


def extract_from_passages(
    client: LLMClient,
    series: str,
    character: str,
    found_passages: list[tuple[str, str]],
    overrides: dict,
    known: dict[str, str],
    arcs: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    """Relationships stated for this character, over passages already read.

    `known` is the set of names this wiki has an entity for, resolved by the
    caller. Everything here is prompt-building, network and string work, so it
    is safe on a worker thread.
    """
    found: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for section, text in found_passages:
        for window in _windows(text):
            prompt = _TEMPLATE.format(
                series=series, character=character, section=section,
                passage=window, relations=", ".join(RELATIONS),
            )
            answer = client.complete(
                prompt, system=SYSTEM, temperature=0.0, max_tokens=_answer_budget()
            )
            for entry in parse_response(answer):
                other = str(entry.get("other") or "").strip()
                relation = str(entry.get("relation") or "").strip().lower()
                quote = str(entry.get("quote") or "").strip()
                if not other or relation not in RELATIONS:
                    continue
                # The other end has to be somebody this wiki has a page or an
                # alias for. Without it a model supplies a plausible name from
                # the series it has read and nothing in the row shows it.
                #
                # Resolved to the canonical title *before* the duplicate check,
                # or `Geto` and `Suguru Geto` are two people: both survive, the
                # table stops joining, and a script asking who Gojo fell out
                # with is told twice under different names.
                canonical = known.get(other.strip().lower())
                if not canonical:
                    logger.info("unknown other %r for %s", other, character)
                    continue
                other, entry["other"] = canonical, canonical
                if other.lower() == character.lower():
                    continue
                key = (other.lower(), relation)
                if key in seen:
                    continue
                if not _quoted_in(quote, window):
                    logger.info("unquoted %r->%r for %s", relation, other, character)
                    continue
                seen.add(key)
                entry["section"] = section
                entry["era"] = _era_for(entry.get("era", ""), section, arcs or {})
                found.append(entry)
    return found


def _answer_budget() -> int:
    import os

    return int(os.environ.get("SCRIPTENGINE_ANSWER_TOKENS", "2048"))


def _revid(store: FactStore, title: str) -> str:
    row = store.connection.execute(
        "SELECT revid FROM documents WHERE title = ? COLLATE NOCASE", (title,)
    ).fetchone()
    return str(row["revid"] or "") if row else ""


def extract_series(
    paths: SeriesPaths,
    settings: Settings | None = None,
    limit: int | None = None,
    refresh: bool = False,
    progress: Any = None,
    workers: int = 1,
) -> dict[str, Any]:
    """Extract this series' prose-only relationships, skipping what is current.

    Chunked and threaded exactly as `abilities.extract_series` is, and for the
    same reason: the store belongs to this thread, the network wait does not.
    """
    from concurrent.futures import ThreadPoolExecutor

    from scriptengine.ingest.abilities import _guarded

    settings = settings or get_settings()
    overrides = load_overrides(paths)
    client = LLMClient(settings)
    if not client.available():
        raise LLMUnavailable(f"No model at {client.base_url}.")

    report = {"considered": 0, "extracted": 0, "cached": 0, "failed": 0, "relations": 0}
    with FactStore(paths.facts_db) as store:
        store.ensure_relations()
        # Resolved here, on the thread that owns the connection.
        known = known_names(store, overrides)
        arcs = known_arcs(store)
        characters = needs_relations(store, overrides)
        report["considered"] = len(characters)
        wanted = characters[:limit] if limit else characters

        todo: list[tuple[str, str]] = []
        for character in wanted:
            revid = _revid(store, character)
            state = store.relation_state(character)
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
            store.save_relations(
                character=character, found=found,
                revid=int(revid) if revid.isdigit() else None,
                prompt_version=PROMPT_VERSION, model=settings.llm_model,
            )
            report["extracted"] += 1
            report["relations"] += len(found)
            if progress is not None:
                progress(character, len(found))

        if workers <= 1:
            for character, revid in todo:
                try:
                    found = extract_from_passages(
                        client, paths.name, character,
                        passages(store, character, overrides), overrides, known, arcs,
                    )
                except LLMUnavailable:
                    raise
                except Exception as error:  # noqa: BLE001 - one page must not stop the run
                    logger.warning("Relations for %r failed: %s", character, error)
                    report["failed"] += 1
                    continue
                store_result(character, revid, found)
            return report

        for start in range(0, len(todo), workers * 4):
            chunk = todo[start : start + workers * 4]
            work = [
                (character, revid, passages(store, character, overrides))
                for character, revid in chunk
            ]

            def run(job):
                character, _, found_passages = job
                return extract_from_passages(
                    client, paths.name, character, found_passages, overrides, known,
                    arcs,
                )

            with ThreadPoolExecutor(max_workers=workers) as pool:
                for (character, revid, _), outcome in zip(
                    work, pool.map(_guarded(run), work)
                ):
                    if isinstance(outcome, BaseException):
                        if isinstance(outcome, LLMRateLimited):
                            raise outcome
                        logger.warning(
                            "Relations for %r failed: %s", character, outcome
                        )
                        report["failed"] += 1
                        continue
                    store_result(character, revid, outcome)
    return report

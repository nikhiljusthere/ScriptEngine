"""page-gen: the deterministic structured half of a page-campaign batch.

The campaign's regular questions -- infobox identity, the per-battle
outcome/location/chapter/technique block, roster sets -- are a pure function
of `facts.db`: the fields are identical in shape across every page. This
module generates them with a provenance marker (`page-gen:<class>:<key>` in
`note`), emits the roster declarations, the section-coverage ledger and the
verify sheet, and merges its output into the one campaign batch without ever
touching a hand-authored question. Only the prose beats (battle "how",
synopsis, relationships, trivia) are left to a reader.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date

from scriptengine.config import SeriesPaths
from scriptengine.ingest.crawler import load_manifest, sanitise_filename
from scriptengine.stores.facts import FactStore

PROV = "page-gen:"

class PageGenError(Exception):
    """A page that cannot be generated: not crawled, not in the store, or a
    batch that would clobber a hand-authored question."""

@dataclass
class PageGenOutput:
    questions: list[dict] = field(default_factory=list)
    retires: list[dict] = field(default_factory=list)
    rosters: list[dict] = field(default_factory=list)
    coverage: dict = field(default_factory=dict)
    verify: list[dict] = field(default_factory=list)

# Field -> question. Keyed to the wiki's own infobox vocabulary (the fact
# keys), never to a series name: a wiki whose infobox calls a field `class`
# gets a "grade" question without the engine knowing which wiki it is.
IDENTITY_FIELDS: dict[str, str] = {
    "status": "What is the status of {name}?",
    "race": "What is {name}'s race?",
    "age": "How old is {name}?",
    "gender": "What is {name}'s gender?",
    "occupation": "What is {name}'s occupation?",
    "class": "What is {name}'s grade?",
    "debut": "In which manga chapter does {name} first appear?",
    "anime debut": "In which anime episode is {name} first depicted?",
    "debutanime": "In which anime episode is {name} first depicted?",
    "voice": "Who is {name}'s Japanese voice actor?",
    "eng voice": "Who is {name}'s English voice actor?",
    "creator": "Who created {name}?",
    "birthday": "What is {name}'s birthday?",
    "bloodtype": "What is {name}'s blood type?",
    "height": "What is {name}'s height?",
    "weight": "What is {name}'s weight?",
}

# Nihongo/Ruby shapes: the cell holds a script form the prose never repeats,
# so the value is not in any chunk and a gold would route to nothing. Golded
# only when chunked, else auto-retired (spec §8).
UNCHECKED_KEYS = frozenset({"kanji", "romaji", "japanese"})
UNCHECKED_QUESTIONS = {
    "kanji": "What are the kanji for {name}'s name?",
    "romaji": "What is the romaji of {name}'s name?",
    "japanese": "What is the Japanese spelling of {name}'s name?",
}

# `alias`/`affiliation` cells are lists. Split on newlines and the <br> the
# wiki writes between members; what is left is a closed set and a roster.
_LIST_SPLIT = re.compile(r"\n|<br\s*/?>", re.IGNORECASE)
LIST_FIELDS = {
    "alias": ("aliases", "alias"),
    "affiliation": ("affiliations", "affiliation"),
}

def slug_of(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")

def chunked(store: FactStore, value: str) -> bool:
    """True iff some chunk carries `value` -- the campaign's G3 check."""
    if not value:
        return False
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    row = store.connection.execute(
        "SELECT 1 FROM chunks WHERE text LIKE ? ESCAPE '\\' COLLATE NOCASE LIMIT 1",
        (f"%{escaped}%",),
    ).fetchone()
    return row is not None

def _question(
    question: str,
    kind: str,
    subject: str,
    golds: list[str],
    wiki: str,
    title: str,
    note: str,
    verified: str,
    expect_mode: str = "qa",
    extra_sources: tuple[str, ...] = (),
) -> dict:
    url = f"{wiki}/wiki/{title.replace(' ', '_')}"
    return {
        "id": "",
        "kind": kind,
        "question": question,
        "subject": subject,
        "tier": "wiki",
        "expect_mode": expect_mode,
        "scope": "closed",
        "answer": [{"item": g, "aliases": []} for g in golds],
        "sources": [url, *extra_sources],
        "verified": verified,
        "note": note,
    }

def _retire(out: PageGenOutput, question: str, value: str, reason: str, note: str) -> None:
    # Rows mirror the campaign's retired shape (id is numbered by write_batch);
    # the note is what `write_batch` uses to tell generated rows from hand rows.
    out.retires.append({
        "id": "",
        "item": value,
        "question": question,
        "reason": reason,
        "note": note,
        "retired": True,
    })

def _identity_builder(store, paths, title, aliases, overrides, wiki, out, verified):
    facts: dict[str, dict] = {}
    for row in store.facts_for(title):
        key = (row["key"] or "").lower()
        if key and key not in facts:
            facts[key] = row
    for key, row in facts.items():
        value = (row["value"] or "").strip()
        if key == "name":
            continue  # the name is the subject, not a question about it
        if key in UNCHECKED_KEYS:
            question = UNCHECKED_QUESTIONS[key].format(name=title)
            if not value:
                _retire(out, question, "", "field is empty on the page", f"{PROV}identity:{key}")
            elif not chunked(store, value):
                _retire(out, question, value,
                        "unchunked infobox cell (G3 Nihongo/Ruby shape)",
                        f"{PROV}identity:{key}")
            else:
                out.questions.append(_question(
                    question, "fact", title, [value], wiki, title,
                    f"{PROV}identity:{key}", verified))
            continue
        if key in IDENTITY_FIELDS:
            question = IDENTITY_FIELDS[key].format(name=title)
            if not value:
                _retire(out, question, "", "field is empty on the page", f"{PROV}identity:{key}")
            else:
                out.questions.append(_question(
                    question, "fact", title, [value], wiki, title,
                    f"{PROV}identity:{key}", verified))
            continue
        if key in LIST_FIELDS:
            plural, _ = LIST_FIELDS[key]
            members = [m.strip() for m in _LIST_SPLIT.split(value) if m.strip()] if value else []
            note = f"{PROV}{key}"
            if not members:
                _retire(out, f"What are all the {plural} of {title}?", "",
                        "field is empty on the page", note)
                continue
            s = title.lower()
            out.rosters.append({
                "name": f"{title}'s {plural}",
                "match": [f"all the {plural} of {s}", f"{plural} of {s}", f"{s}'s {plural}"],
                "subject": title,
                "members": members,
            })
            out.questions.append(_question(
                f"What are all the {plural} of {title}?", "set", title, members,
                wiki, title, note, verified, expect_mode="roster"))
            continue
        # Everything else (capabilities, hair, eye, ...) is prose: the ledger
        # leaves its section uncovered for the reader.

_BUILDERS = (_identity_builder,)

def _aliases_of(store: FactStore, paths: SeriesPaths, title: str) -> list[str]:
    """The page's alias rows plus the crawl's, best-effort.

    `battles_in` matches on a fighter's last content word, and a character's
    battle pages name her by the alias the page's own infobox carries, so the
    battle union has to be driven over every name, not just the title.
    """
    names: set[str] = set()
    node = store.node_by_name(title)
    if node is not None:
        for row in store.connection.execute(
            "SELECT alias FROM aliases WHERE node_id = ?", (node["id"],)
        ):
            names.add(row["alias"])
    crawl = paths.wikitext / f"{sanitise_filename(title)}.json"
    if crawl.exists():
        try:
            payload = json.loads(crawl.read_text(encoding="utf-8"))
            names.update(a for a in (payload.get("aliases") or []) if a)
        except (json.JSONDecodeError, OSError):
            pass  # best-effort: the store's alias rows stand alone
    return sorted(names)

def generate_structured(
    paths: SeriesPaths,
    title: str,
    overrides: dict | None = None,
    settings=None,
    extra_sections: dict | None = None,
) -> PageGenOutput:
    """The structured half of `title`'s campaign batch, straight from the store."""
    if not paths.facts_db.exists():
        raise PageGenError(f"no facts store for {paths.name!r} at {paths.facts_db}")
    store = FactStore(paths.facts_db)
    try:
        row = store.connection.execute(
            "SELECT 1 FROM documents WHERE title = ? COLLATE NOCASE", (title,)
        ).fetchone()
        if row is None:
            raise PageGenError(f"{title!r} is not in {paths.facts_db.name}: index the series first")

        manifest = load_manifest(paths)
        wiki = (manifest.get("wiki") or "").rstrip("/")
        if not wiki:
            crawl = paths.wikitext / f"{sanitise_filename(title)}.json"
            if crawl.exists():
                url = json.loads(crawl.read_text(encoding="utf-8")).get("url", "")
                wiki = url.split("/wiki/")[0] if "/wiki/" in url else ""
        if not wiki:
            raise PageGenError(f"no wiki base for {paths.name!r}: the manifest carries none")

        out = PageGenOutput()
        verified = date.today().isoformat()
        aliases = _aliases_of(store, paths, title)
        for builder in _BUILDERS:
            builder(store, paths, title, aliases, overrides, wiki, out, verified)
        return out
    finally:
        store.close()
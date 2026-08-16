"""The shapes that flow through ingestion.

One rule governs this module: **structure extracted is structure kept**. An
infobox parameter becomes a `Fact` and, where it links somewhere, an `Edge`,
never a sentence of prose that a later stage has to parse back into a fact.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Citation:
    """A reference to a source work.

    Fandom wikis cite through templates such as ``{{Ref|vol=5|page=26}}``, so
    the volume, chapter and page arrive as named parameters rather than as text
    to be parsed. Keeping them separate is what lets a generated script trace a
    claim back to a specific page of a specific volume.
    """

    template: str                       # the citing template, e.g. "Ref"
    params: dict[str, str] = field(default_factory=dict)
    raw: str = ""                       # original wikitext, for debugging

    def describe(self) -> str:
        """A short human-readable form, e.g. ``Ref vol=5 page=26``."""
        parts = " ".join(f"{k}={v}" for k, v in self.params.items() if v)
        return f"{self.template} {parts}".strip()


@dataclass(slots=True)
class Link:
    """A wikilink: ``[[Target|Display]]``.

    The target is already canonical, since MediaWiki resolved it when the page was
    written. This is why the factual backbone of the graph needs no NER and no
    per-series alias table.
    """

    target: str
    display: str = ""

    def __post_init__(self) -> None:
        if not self.display:
            self.display = self.target


@dataclass(slots=True)
class Fact:
    """One infobox parameter, with everything it carried.

    ``key`` is the wikitext parameter name (``class``, ``race``, ``debut``) and
    ``label`` is the wiki's own human rendering of it ("Grade", "Species",
    "Manga Debut"), taken from the Portable Infobox schema. Both are kept: the
    key is stable for lookups, the label is what a reader understands.
    """

    key: str
    value: str                                      # markup stripped
    label: str = ""                                 # human label, if the wiki gave one
    links: list[Link] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    raw: str = ""                                   # original parameter value


@dataclass(slots=True)
class Edge:
    """A typed relationship between two pages.

    ``confidence`` distinguishes how the edge was found. Infobox parameters are
    explicit statements by an editor and score high; a link merely appearing in
    prose is weaker evidence, and downstream ranking should be able to tell the
    difference.
    """

    source: str                                     # page title
    relation: str                                   # e.g. "affiliation", "mentions"
    target: str                                     # page title, canonical
    confidence: float = 1.0
    provenance: str = ""                            # where in the page it came from
    section: str = ""


@dataclass(slots=True)
class Section:
    """A section of a page, positioned in the heading tree.

    Levels come from the MediaWiki API, not from guessing at markup. The
    previous pipeline inferred headings with a regex that never matched, so
    every document collapsed into one unnamed section and nothing downstream
    could tell where anything belonged.
    """

    title: str
    level: int                                      # 2 for ==H2==, 3 for ===H3===
    index: str                                      # API section index
    anchor: str = ""
    path: list[str] = field(default_factory=list)   # breadcrumb of ancestor titles
    text: str = ""                                  # prose, markup stripped
    wikitext: str = ""                              # original, for re-parsing
    links: list[Link] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    # True when the heading came from an item marker (`;Kaio-ken`) rather than
    # from `==`. The chunker keeps these however short they are: the name is
    # the point, and an ability described in one sentence is still an ability.
    is_item: bool = False

    @property
    def breadcrumb(self) -> str:
        """``Abilities and Powers / Cursed Technique``."""
        return " / ".join([*self.path, self.title])

    @property
    def word_count(self) -> int:
        return len(self.text.split())


@dataclass(slots=True)
class WikiPage:
    """Everything one wiki page yielded.

    This is what the crawler writes to disk and every later stage reads. It is
    deliberately serialisable: re-running extraction should never require
    re-crawling, since a fetched page is expensive and parsing it is cheap.
    """

    title: str
    url: str
    pageid: int = 0
    revid: int = 0

    # Type, as discovered from the wiki rather than assumed.
    page_type: str = "unknown"
    infobox_template: str = ""

    categories: list[str] = field(default_factory=list)
    templates: list[str] = field(default_factory=list)

    lead: str = ""                                  # prose before the first heading
    sections: list[Section] = field(default_factory=list)
    facts: list[Fact] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)

    redirects: list[str] = field(default_factory=list)   # titles that land here
    aliases: list[str] = field(default_factory=list)     # names this page is known by

    wikitext: str = ""
    fetched_at: str = ""

    # Populated only when extraction had something to complain about.
    warnings: list[str] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return len(self.lead.split()) + sum(s.word_count for s in self.sections)

    def fact(self, key: str) -> Fact | None:
        """Look up a single infobox parameter by its wikitext key."""
        for candidate in self.facts:
            if candidate.key == key:
                return candidate
        return None

    def to_json(self, *, include_wikitext: bool = True) -> str:
        payload: dict[str, Any] = asdict(self)
        if not include_wikitext:
            payload.pop("wikitext", None)
            for section in payload["sections"]:
                section.pop("wikitext", None)
        return json.dumps(payload, ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WikiPage":
        """Rebuild from a JSON payload, restoring the nested dataclasses."""
        data = dict(payload)

        def citations(items: list[dict[str, Any]]) -> list[Citation]:
            return [Citation(**item) for item in items or []]

        def links(items: list[dict[str, Any]]) -> list[Link]:
            return [Link(**item) for item in items or []]

        data["citations"] = citations(data.get("citations", []))
        data["links"] = links(data.get("links", []))
        data["edges"] = [Edge(**item) for item in data.get("edges", [])]
        data["facts"] = [
            Fact(
                **{
                    **item,
                    "links": links(item.get("links", [])),
                    "citations": citations(item.get("citations", [])),
                }
            )
            for item in data.get("facts", [])
        ]
        data["sections"] = [
            Section(
                **{
                    **item,
                    "links": links(item.get("links", [])),
                    "citations": citations(item.get("citations", [])),
                }
            )
            for item in data.get("sections", [])
        ]
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})

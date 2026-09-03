"""Discovering a wiki's own type system.

The previous pipeline decided in Python what a Jujutsu Kaisen page could be:
`Character`, `Arc`, `Battle`, `Technique`, `Location`, `Organization`, `Object`,
`Volume`, backed by hand-written alias tables. Pointing that at the Marvel wiki
produces nothing, because Marvel's concepts are not JJK's concepts.

Every Fandom wiki already declares its own vocabulary. The `Template:` namespace
holds one infobox per kind of thing the wiki tracks, and each article says which
one it uses. Jujutsu Kaisen defines 20: `Character Infobox`, `Battle Infobox`,
`Episode Infobox`, `Technique Infobox`, `Story Arcs Infobox`, and so on. Reading
that list is how a series gets its types, and it is why adding a series requires
no code.

Nothing in this module names a series.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Iterable

from scriptengine.ingest.wikitext import CitationGrammar

# Trailing words to drop when turning a template name into a type:
# "Character Infobox" -> "character", "Infobox Person" -> "person".
_INFOBOX_WORD = re.compile(r"\b(infobox|info box|template)\b", re.IGNORECASE)
_NON_WORD = re.compile(r"[^a-z0-9]+")

# Infobox templates that describe presentation rather than a kind of subject.
_STRUCTURAL_INFOBOXES = {"infobox scroll box", "infobox", "scroll box"}

# The fewest named parameters a template must reach, on its best page, to be
# believed to describe a subject rather than a layout. Sparse infoboxes exist,
# so this is deliberately low; it only needs to exclude wrappers like `Tabs`.
MIN_INFOBOX_FIELDS = 5

# Categories that mark a page as maintenance or media rather than content.
# These are MediaWiki-wide conventions, not per-wiki choices.
#
# "articles needing" is deliberately absent. Maintenance banners like
# "Articles needing cleanup" sit on real pages: on Jujutsu Kaisen the three
# main character pages (Yuji Itadori, Satoru Gojo, Sukuna) all carry it, and
# skipping on a maintenance banner throws away the wiki's most-linked content.
_SKIP_CATEGORY_PATTERNS = (
    "images", "gallery", "galleries", "candidates for deletion",
    "stubs", "disambiguation", "blog posts",
    "browse", "site maintenance", "templates", "wiki",
)


def slugify_type(name: str) -> str:
    """Reduce a template name to a stable type id.

    ``Character Infobox`` and ``Infobox_Character`` both become ``character``,
    so a wiki's naming style does not leak into the data model.
    """
    cleaned = _INFOBOX_WORD.sub(" ", name.replace("_", " "))
    cleaned = _NON_WORD.sub("_", cleaned.strip().lower()).strip("_")
    return cleaned or "unknown"


def item_section_names(overrides: dict[str, Any] | None) -> set[str]:
    """The sections whose `;term` and `'''term'''` markers name real things.

    Read from the same `ability_sections:` declaration retrieval and extraction
    already use, so a series states this once. Nothing here names a series.
    """
    declared = (overrides or {}).get("ability_sections") or {}
    return {
        str(section).strip().lower()
        for sections in declared.values()
        for section in sections
        if str(section).strip()
    }


@dataclass
class Ontology:
    """What a wiki says it contains.

    Built once per crawl from the wiki's own metadata, then consulted for every
    page. Serialised into the series manifest so a re-index does not need to
    re-discover it.
    """

    wiki: str = ""
    # Normalised infobox template name -> type id, e.g. "character infobox" -> "character"
    infobox_types: dict[str, str] = field(default_factory=dict)
    # Type id -> {wikitext param -> human label}, from the Portable Infobox schema
    field_labels: dict[str, dict[str, str]] = field(default_factory=dict)
    # Categories seen, with page counts, for auditing
    categories: dict[str, int] = field(default_factory=dict)
    skip_categories: set[str] = field(default_factory=set)
    # Title -> type, filled in as pages are typed, so a subpage can inherit from
    # its parent regardless of which order the two were crawled in.
    page_types: dict[str, str] = field(default_factory=dict)
    # How many pages nominated each template as their infobox. Kept for the
    # audit: it shows what discovery saw, including what it rejected.
    infobox_votes: dict[str, int] = field(default_factory=dict)
    # Which works this wiki's citations distinguish between: a sequel restarts
    # its chapter numbering, so `{{Ref|modulo=y|chap=16}}` is not Chapter 16.
    # The names are per-wiki, so they come from overrides; see
    # `wikitext.CitationGrammar`.
    citation_works: CitationGrammar = field(default_factory=CitationGrammar)
    # The sections whose item markers are worth reading as headings. A wiki
    # writes each of a character's forms as `;Super Saiyan 4` or `'''Godspeed'''`
    # rather than as a real `==` heading, and the marker is the only thing
    # saying where one ends and the next begins.
    #
    # Scoped to the declared ability sections rather than applied everywhere,
    # because the same markers carry unrelated content elsewhere: One Piece
    # writes 7,491 of them, and its heaviest pages are `Chapter 1161` and
    # `Chapters and Volumes`, which are listings and not abilities.
    item_sections: set[str] = field(default_factory=set)

    @property
    def types(self) -> list[str]:
        return sorted(set(self.infobox_types.values()))

    def type_for_templates(self, templates: Iterable[str]) -> tuple[str, str]:
        """Return ``(type_id, matched_template)`` for a page's transclusions.

        A page transcludes many templates; only one is its infobox. Known
        infoboxes win over name-matching so that a wiki whose infobox is called
        something unusual still resolves correctly.
        """
        candidates = []
        for template in templates:
            normalised = _normalise_template(template)
            if normalised in _STRUCTURAL_INFOBOXES:
                continue
            if normalised in self.infobox_types:
                candidates.append((normalised, self.infobox_types[normalised]))

        if candidates:
            # Prefer the most specific name when a page nests infoboxes.
            normalised, type_id = max(candidates, key=lambda pair: len(pair[0]))
            return type_id, normalised

        for template in templates:
            # Lua modules implement infoboxes on older wikis, but their names are
            # implementation detail: Marvel transcludes `Module:CharacterInfobox‐
            # Origins`, which is not a page type. Only real templates may name one.
            if _is_module(template):
                continue
            normalised = _normalise_template(template)
            if "infobox" in normalised and normalised not in _STRUCTURAL_INFOBOXES:
                return slugify_type(normalised), normalised

        return "unknown", ""

    def labels_for(self, type_id: str) -> dict[str, str]:
        return self.field_labels.get(type_id, {})

    def is_skippable(self, categories: Iterable[str]) -> str:
        """Return a reason to skip the page, or an empty string to keep it."""
        for category in categories:
            lowered = category.lower()
            if lowered in self.skip_categories:
                return f"category: {category}"
            for pattern in _SKIP_CATEGORY_PATTERNS:
                if pattern in lowered:
                    return f"category: {category}"
        return ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "wiki": self.wiki,
            "infobox_types": self.infobox_types,
            "field_labels": self.field_labels,
            "categories": self.categories,
            "skip_categories": sorted(self.skip_categories),
            "infobox_votes": self.infobox_votes,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Ontology":
        return cls(
            wiki=payload.get("wiki", ""),
            infobox_types=payload.get("infobox_types", {}),
            field_labels=payload.get("field_labels", {}),
            categories=payload.get("categories", {}),
            skip_categories=set(payload.get("skip_categories", [])),
            infobox_votes=payload.get("infobox_votes", {}),
        )


def _is_module(name: str) -> bool:
    """True for Lua modules, which implement behaviour rather than name a type."""
    return name.strip().lstrip(":").lower().startswith(("module:", "модуль:"))


def _normalise_template(name: str) -> str:
    """``Template:Character_Infobox`` -> ``character infobox``."""
    cleaned = name.strip().lstrip(":")
    if ":" in cleaned:
        prefix, _, rest = cleaned.partition(":")
        if prefix.strip().lower() in {"template", "модуль", "modul"}:
            cleaned = rest
    return cleaned.replace("_", " ").strip().lower()


def build_ontology(
    wiki: str,
    template_titles: Iterable[str],
    overrides: dict[str, Any] | None = None,
) -> Ontology:
    """Derive the type vocabulary from the wiki's ``Template:`` namespace.

    ``overrides`` comes from `series/<name>/overrides.yaml` and is the only
    place a wiki-specific decision is allowed to live.
    """
    overrides = overrides or {}
    ontology = Ontology(wiki=wiki)

    for title in template_titles:
        normalised = _normalise_template(title)
        if "infobox" not in normalised or normalised in _STRUCTURAL_INFOBOXES:
            continue
        ontology.infobox_types[normalised] = slugify_type(normalised)

    for template, type_id in (overrides.get("type_aliases") or {}).items():
        ontology.infobox_types[_normalise_template(template)] = slugify_type(type_id)

    ontology.skip_categories = {
        str(c).lower() for c in (overrides.get("skip_categories") or [])
    }
    ontology.citation_works = CitationGrammar.from_overrides(overrides)
    ontology.item_sections = item_section_names(overrides)
    return ontology


def build_ontology_from_transclusions(
    wiki: str,
    pages_templates: Iterable[Iterable[str]],
    overrides: dict[str, Any] | None = None,
) -> Ontology:
    """Derive the vocabulary from what pages actually transclude.

    A fallback for when the `Template:` namespace cannot be enumerated: the
    wiki is rate-limiting, or the crawl predates the manifest. Every infobox in
    use is by definition transcluded by the pages using it, so the result is the
    same vocabulary reached from the other direction.
    """
    seen: set[str] = set()
    for templates in pages_templates:
        for template in templates:
            if _is_module(template):
                continue
            normalised = _normalise_template(template)
            if "infobox" in normalised and normalised not in _STRUCTURAL_INFOBOXES:
                seen.add(template)
    return build_ontology(wiki, sorted(seen), overrides)


def discover_infoboxes(
    wiki: str,
    pages: Iterable[tuple[str, str]],
    overrides: dict[str, Any] | None = None,
    min_pages: int = 2,
) -> Ontology:
    """Derive the vocabulary from the *shape* of each page's wikitext.

    This is what makes the engine universal. Searching template names for the
    word "infobox" finds Jujutsu Kaisen's twenty types and nothing at all on
    Chainsaw Man, whose infobox is called `Character`, or on Marvel, which uses
    Lua modules and `Marvel Database:Character Template`.

    Instead each page votes for its richest pre-heading template (see
    `wikitext.infobox_candidates`) and any template winning on at least
    `min_pages` pages becomes a type. Requiring more than one page keeps one-off
    layout wrappers out of the vocabulary.

    `pages` is an iterable of `(title, wikitext)`.
    """
    from scriptengine.ingest.wikitext import infobox_candidates

    votes: Counter = Counter()
    richest: dict[str, int] = {}
    for _, wikitext in pages:
        candidates = infobox_candidates(wikitext)
        if candidates:
            name, params = candidates[0]
            votes[name] += 1
            richest[name] = max(richest.get(name, 0), params)

    overrides = overrides or {}
    ontology = Ontology(wiki=wiki)

    # Deliberately not routed through `build_ontology`: that filters on the word
    # "infobox", which is the very assumption this function exists to replace.
    # A template elected by the pages themselves is an infobox whatever it is
    # called.
    for name, count in votes.items():
        normalised = _normalise_template(name)
        if count < min_pages or normalised in _STRUCTURAL_INFOBOXES:
            continue
        # A template that never describes more than a handful of fields on any
        # page is layout, not a subject. `Tabs` peaks at three parameters
        # (tab1/tab2/tab3); a real infobox reaches twenty. Electing layout
        # wrappers pollutes the vocabulary and, worse, lets them shadow the
        # actual infobox during extraction.
        if richest.get(name, 0) < MIN_INFOBOX_FIELDS:
            continue
        ontology.infobox_types[normalised] = slugify_type(normalised)

    for template, type_id in (overrides.get("type_aliases") or {}).items():
        ontology.infobox_types[_normalise_template(template)] = slugify_type(type_id)

    ontology.skip_categories = {
        str(c).lower() for c in (overrides.get("skip_categories") or [])
    }
    ontology.citation_works = CitationGrammar.from_overrides(overrides)
    ontology.item_sections = item_section_names(overrides)
    ontology.infobox_votes = dict(votes.most_common(40))
    return ontology


def learn_field_labels(
    ontology: Ontology, type_id: str, properties: dict[str, Any] | str | None
) -> None:
    """Record the wiki's human labels for a type's infobox parameters.

    Fandom's Portable Infobox extension publishes its schema in the page's
    ``properties.infoboxes`` blob: which parameter feeds which labelled row. That
    turns ``class`` into "Grade" and ``race`` into "Species", and the difference
    between a field a reader understands and one they have to guess at.

    Failures here are silent by design: labels are an enrichment, and a wiki that
    does not use Portable Infoboxes should still index perfectly well.
    """
    if not properties or type_id in ontology.field_labels:
        return

    blob = properties.get("infoboxes") if isinstance(properties, dict) else properties
    if not blob:
        return

    try:
        parsed = json.loads(blob) if isinstance(blob, str) else blob
    except (json.JSONDecodeError, TypeError):
        return

    labels: dict[str, str] = {}

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            sources = node.get("sources")
            if isinstance(sources, dict):
                for source, meta in sources.items():
                    label = (meta or {}).get("label") if isinstance(meta, dict) else None
                    if source and label:
                        labels.setdefault(str(source).lower(), str(label))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(parsed)
    if labels:
        ontology.field_labels[type_id] = labels

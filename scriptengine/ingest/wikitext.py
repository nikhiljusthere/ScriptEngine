"""Wikitext parsing.

Wikitext cannot be parsed with regular expressions. Templates nest inside
template parameters, links nest inside templates, and templates nest inside
links:

    |age = 18{{Ref|fan=Fanbook|page=36-37}}<br>86{{Ref|chap=21}} {{Sub|([[Jujutsu Kaisen Modulo|Modulo]])}}

A regex for ``\\{\\{(.+?)\\}\\}`` stops at the first ``}}`` and returns garbage.
So the scanners here track brace and bracket depth explicitly. Everything else
in this module is built on those two scanners.

Nothing here knows what series it is reading.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from scriptengine.ingest.documents import Citation, Fact, Link, Section

# Templates that cite a source rather than render content. Matched on a prefix
# so `Ref`, `Ref/contents` and `Reflist` are all recognised. This list is about
# MediaWiki convention, not about any particular wiki.
CITATION_TEMPLATES = ("ref", "cite", "sfn")

# Citation parameters that locate a claim rather than qualify it. Everything
# else a reference carries is either a page number, a name, or a statement about
# which work the instalment belongs to — and the audit flags the last kind when
# this module does not recognise it.
LOCATOR_PARAMS = frozenset({"chap", "chap2", "ep", "ep2", "vol", "fan"})
PAGE_PARAMS = frozenset({"page", "pages", "name"})

# `{{cite web}}` and its relatives describe a source outside the work — an
# interview, a shop listing, a cover image. A script cannot tag a line with a
# URL, so these are dropped on purpose and must not read as a dropped locator.
# The parameter names are the MediaWiki citation convention, not one wiki's.
EXTERNAL_PARAMS = frozenset({
    "url", "title", "publisher", "author", "date", "accessdate",
    "lastaccess", "archiveurl", "archivedate", "language",
    "website", "work", "quote", "isbn", "id", "transtitle", "format", "via",
    # `{{References|note|box=yes}}` renders the footnote list. It is furniture,
    # not a citation, even though its template name starts with "ref".
    "box", "group", "colwidth", "liststyle", "refs", "note",
})


def _normalise_param(key: str) -> str:
    """``access-date``, ``access date`` and ``accessdate`` are one parameter."""
    return re.sub(r"[\s_-]+", "", key.strip().lower())


def is_page_param(key: str) -> bool:
    """True for a page-number parameter, including the wiki's misspellings.

    `pagse` and `pagess` both appear on the Jujutsu Kaisen wiki. Page numbers
    are never rendered into prose, so a typo in one is not a dropped fact — and
    the audit that flags dropped parameters should not spend its signal on them.
    """
    lowered = _normalise_param(key)
    return lowered in PAGE_PARAMS or lowered.startswith("pag")

# Values a flag-style qualifier uses to mean "yes, this one".
_TRUE_VALUES = frozenset({"y", "yes", "true", "1"})


# The roles a citation can locate a claim by. `page` is recognised so it can be
# ignored on purpose: a page number is retrieval noise inside prose.
ROLES = frozenset({"chapter", "episode", "volume", "page"})

# How each role is spoken in a finished script.
_ROLE_LABEL = {"chapter": "Chapter", "episode": "Episode", "volume": "Volume"}


@dataclass(frozen=True)
class RefRole:
    """What a citation parameter or pattern locates, and in which work."""

    role: str = "chapter"
    work: str = ""

    @classmethod
    def parse(cls, spec: object, default_role: str = "chapter") -> "RefRole":
        if isinstance(spec, str):
            return cls(role=spec.strip().lower() or default_role)
        if isinstance(spec, dict):
            role = str(spec.get("as") or spec.get("role") or default_role).lower()
            return cls(role=role, work=str(spec.get("work") or ""))
        return cls(role=default_role)


@dataclass(frozen=True)
class CitationGrammar:
    """How one wiki writes a citation.

    Every wiki invents its own, and the differences are not cosmetic — they
    decide whether a script can put a chapter on a line at all. Five wikis, five
    grammars:

    * **flags** — ``{{Ref|modulo=y|chap=16}}`` on Jujutsu Kaisen. The parameter
      says the chapter belongs to the sequel, whose numbering restarts at 1, so
      the label prefixes the instalment: ``(Modulo Chapter 16)``.
    * **instalments** — ``{{Ref|movie=0}}``. The parameter *is* the instalment.
    * **params** — ``{{ref|ch = 20}}`` on One-Punch Man, whose ``wch`` means a
      chapter of the webcomic rather than the manga. A map from this wiki's
      parameter names to what they locate.
    * **positional** — ``{{Ref|m|216|3-4}}`` on Chainsaw Man. No named
      parameters at all: the first argument picks the medium, the second is the
      number. 2,946 references, every one of them rendering nothing before this.
    * **ref_tags** — ``<ref>''Bleach'' manga; Chapter 686, page 4</ref>`` on
      Bleach, Hunterpedia and Berserk. The locator is prose inside an HTML tag,
      and until it is read and replaced, that prose lands in the middle of the
      sentence it was citing.

    Empty by default, which is the previous behaviour. The vocabulary is per-wiki
    and lives in `series/<name>/overrides.yaml`; only the mechanism is here.
    """

    flags: dict[str, str] = field(default_factory=dict)
    instalments: dict[str, str] = field(default_factory=dict)
    params: dict[str, RefRole] = field(default_factory=dict)
    positional: dict[str, object] = field(default_factory=dict)
    ref_tags: tuple = ()

    @classmethod
    def from_overrides(cls, overrides: dict | None) -> "CitationGrammar":
        overrides = overrides or {}

        positional = dict(overrides.get("citation_positional") or {})
        if positional:
            positional["mediums"] = {
                str(k): RefRole.parse(v)
                for k, v in (positional.get("mediums") or {}).items()
            }

        ref_tags = tuple(
            (re.compile(str(rule["match"]), re.IGNORECASE), RefRole.parse(rule))
            for rule in (overrides.get("citation_ref_tags") or [])
            if rule.get("match")
        )

        return cls(
            flags={
                str(k).lower(): str(v)
                for k, v in (overrides.get("citation_works") or {}).items()
            },
            instalments={
                str(k).lower(): str(v)
                for k, v in (overrides.get("citation_instalments") or {}).items()
            },
            params={
                str(k).lower(): RefRole.parse(v)
                for k, v in (overrides.get("citation_params") or {}).items()
            },
            positional=positional,
            ref_tags=ref_tags,
        )

    @property
    def known_params(self) -> set[str]:
        return set(self.flags) | set(self.instalments) | set(self.params)

    def prefix_for(self, named: dict[str, str]) -> str:
        """``"Modulo "`` when this citation flags a different work, else ``""``."""
        for key, label in self.flags.items():
            if (named.get(key) or "").strip().lower() in _TRUE_VALUES:
                return f"{label} "
        return ""

    def from_positional(self, named: dict[str, str]) -> list[tuple[RefRole, str]]:
        """Read ``{{Ref|m|216|3-4}}`` through this wiki's positional schema."""
        mediums = self.positional.get("mediums") or {}
        if not mediums:
            return []
        select = int(self.positional.get("select", 0))
        number = int(self.positional.get("number", 1))
        role = mediums.get((named.get(f"_{select}") or "").strip())
        value = (named.get(f"_{number}") or "").strip()
        if role is None or not value:
            return []
        return [(role, value)]

    def from_prose(self, body: str) -> list[tuple[RefRole, str]]:
        """Read the locator out of a ``<ref>`` body, first rule that matches."""
        for pattern, role in self.ref_tags:
            match = pattern.search(body or "")
            if match:
                return [(role, match.group(1))]
        return []

# Templates that wrap or annotate text: the template disappears but its contents
# are prose worth keeping. The value says which positional argument holds that
# prose, because the convention differs and guessing gets it wrong:
#
#   {{Nihongo|Revealing One's Hand|情報の開示|Jōhō no Kaiji}}  -> first (English)
#   {{Ruby|情|じょう}}                                          -> first (the kanji)
#   {{Color|White|'''Binding Vows'''}}                          -> last (arg 1 is a colour)
#
# Picking the longest argument, which looks reasonable, yields the Japanese
# script for Nihongo and the furigana for Ruby.
TRANSPARENT_TEMPLATES: dict[str, str] = {
    "nihongo": "first",
    "ruby": "first",
    "sub": "first",
    "sup": "first",
    "small": "first",
    "big": "first",
    "nowrap": "first",
    "italic": "first",
    "bold": "first",
    "quote": "first",
    "color": "last",
    "font": "last",
    "scroll": "all",
    "scroll box": "all",
}

# Markup that carries no meaning once the text is extracted.
_HTML_TAG = re.compile(r"<[^>]+>")
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)

# Blocks whose *contents* are markup, not prose. Stripping only the surrounding
# tags leaves the payload behind — a <gallery> body is a list of image files,
# and it surfaced inside a Shibuya Incident timeline beat as
# "NanamiP.png|Kento Nanami|link=Kento Nanami".
_MEDIA_BLOCK = re.compile(
    r"<(gallery|imagemap|timeline|graph|poem|score)\b[^>]*>.*?</\1\s*>",
    re.DOTALL | re.IGNORECASE,
)
_HEADING = re.compile(r"^(={2,6})\s*(.+?)\s*\1\s*$", re.MULTILINE)

# Wikitable cell attributes precede the content after a single `|`, e.g.
# `| colspan="2" style="..." |Binding Vows`. Only the content is wanted.
_CELL_ATTRS = re.compile(r'^[^|\[{]*?(?:=|colspan|rowspan|style|align|width)[^|]*\|(?!\|)')
_QUOTES = re.compile(r"'{2,5}")
_LIST_PREFIX = re.compile(r"^[*#:;]+\s*", re.MULTILINE)
_WHITESPACE = re.compile(r"[ \t]+")
_BLANK_LINES = re.compile(r"\n{3,}")


# ─────────────────────────────────────────────────────────────────────────────
# Balanced scanners
# ─────────────────────────────────────────────────────────────────────────────


def _scan_balanced(text: str, start: int, open_tok: str, close_tok: str) -> int:
    """Return the index just past the delimiter that closes the one at `start`.

    Returns -1 if the construct is never closed, which happens on malformed
    pages and must not raise — a single bad page should not stop a crawl.
    """
    depth = 0
    i = start
    n = len(text)
    span = len(open_tok)

    while i < n:
        if text.startswith(open_tok, i):
            depth += 1
            i += span
        elif text.startswith(close_tok, i):
            depth -= 1
            i += span
            if depth == 0:
                return i
        else:
            i += 1
    return -1


def find_templates(text: str) -> list[tuple[int, int, str]]:
    """Locate every top-level ``{{...}}`` as ``(start, end, body)``.

    Only outermost templates are returned; nested ones stay inside the body and
    are found by recursing, which keeps a citation attached to the parameter it
    annotates rather than floating loose on the page.
    """
    found: list[tuple[int, int, str]] = []
    i = 0
    while i < len(text):
        start = text.find("{{", i)
        if start == -1:
            break
        end = _scan_balanced(text, start, "{{", "}}")
        if end == -1:
            break
        found.append((start, end, text[start + 2 : end - 2]))
        i = end
    return found


def split_params(body: str) -> list[str]:
    """Split a template body on ``|``, ignoring pipes inside nested constructs.

    A naive ``body.split("|")`` shatters ``|affiliation = [[A|B]]`` into two
    broken halves. Depth tracking keeps the link intact.
    """
    parts: list[str] = []
    current: list[str] = []
    brace = bracket = 0
    i = 0

    while i < len(body):
        if body.startswith("{{", i):
            brace += 1
            current.append("{{")
            i += 2
        elif body.startswith("}}", i):
            brace -= 1
            current.append("}}")
            i += 2
        elif body.startswith("[[", i):
            bracket += 1
            current.append("[[")
            i += 2
        elif body.startswith("]]", i):
            bracket -= 1
            current.append("]]")
            i += 2
        elif body[i] == "|" and brace == 0 and bracket == 0:
            parts.append("".join(current))
            current = []
            i += 1
        else:
            current.append(body[i])
            i += 1

    parts.append("".join(current))
    return parts


def parse_template(body: str) -> tuple[str, dict[str, str], list[str]]:
    """Split a template body into ``(name, named_params, positional_params)``."""
    parts = split_params(body)
    name = parts[0].strip() if parts else ""

    named: dict[str, str] = {}
    positional: list[str] = []

    for part in parts[1:]:
        if "=" in part:
            key, _, value = part.partition("=")
            key = key.strip()
            # A leading '=' or a key containing markup means this is not really
            # a named parameter, just prose that happens to contain '='.
            if key and "[[" not in key and "{{" not in key and "\n" not in key:
                named[key.lower()] = value.strip()
                continue
        positional.append(part.strip())

    return name, named, positional


def extract_links(text: str) -> list[Link]:
    """Collect every ``[[Target|Display]]`` in order of appearance.

    Category, File and Image links are skipped: they describe the page's
    presentation and membership, not its relationships. Section anchors are
    dropped from the target so ``[[Grade#Ranks|grade 1]]`` resolves to ``Grade``.
    """
    links: list[Link] = []
    i = 0

    while i < len(text):
        start = text.find("[[", i)
        if start == -1:
            break
        end = _scan_balanced(text, start, "[[", "]]")
        if end == -1:
            break

        body = text[start + 2 : end - 2]
        i = end

        target, _, display = body.partition("|")
        target = target.strip()
        # A leading colon escapes the namespace on the page — `[[:Category:X]]`
        # renders as plain text — but the target is still a Category page, not
        # an article. Strip it so the namespace check below does its job.
        target = target.lstrip(":")
        if not target or ":" in target.split("#")[0][:20] and _is_namespaced(target):
            continue

        target = normalise_title(target.split("#")[0])
        if not target:
            continue

        links.append(Link(target=target, display=strip_markup(display or target)))

    return links


def normalise_title(title: str) -> str:
    """Apply MediaWiki's own title rules so one page yields one node.

    MediaWiki capitalises the first letter of every title and treats
    underscores as spaces, so ``[[grade]]`` and ``[[Grade]]`` are the same page.
    Without this the graph grows a duplicate node for every casing a link
    happens to use — the real corpus produced both `Grade` and `grade`.
    """
    cleaned = title.replace("_", " ").strip()
    return cleaned[:1].upper() + cleaned[1:] if cleaned else ""


# Links that render no text at all: on the page they become an image, or
# nothing. Dropping them entirely is correct.
_SILENT_NAMESPACES = frozenset({
    "category", "file", "image", "media", "template", "module",
    "special", "mediawiki",
})

# Links that render as ordinary text but point outside this wiki. They are not
# relationships between pages here, yet their display text is real prose —
# `[[Wikipedia:Subaru Kimura|Subaru Kimura]]` is how the voice actor's name
# appears, and discarding it lost the answer to "who voices Aoi Todo".
_TEXTUAL_NAMESPACES = frozenset({
    "wikipedia", "w", "wikt", "wiktionary", "commons", "help",
    "talk", "user", "project", "imdb", "mal",
})


def _is_namespaced(target: str) -> bool:
    """True for links that are not a relationship to another article here."""
    prefix = target.split(":", 1)[0].strip().lower()
    return prefix in _SILENT_NAMESPACES or prefix in _TEXTUAL_NAMESPACES


def _renders_text(target: str) -> bool:
    """True when a link contributes words to the prose."""
    prefix = target.split(":", 1)[0].strip().lower()
    return prefix not in _SILENT_NAMESPACES


# `<ref>Bleach manga; Chapter 686, page 4</ref>` and its name-only reuse
# `<ref name="c686"/>`. Three of the five wikis crawled cite this way, and until
# these are read and replaced, `_HTML_TAG` deletes the tags and leaves the
# bibliography sitting in the middle of the sentence it was citing:
# "Ichigo fights. Bleach anime, Episode 179 He wins."
_REF_TAG = re.compile(r"<ref([^>/]*?)(?:/\s*>|>(.*?)</ref\s*>)", re.S | re.IGNORECASE)
_REF_NAME = re.compile(r"""name\s*=\s*["']?([^"'>\s]+)""", re.IGNORECASE)


def collect_ref_tag_definitions(text: str) -> dict[str, str]:
    """Named ``<ref>`` bodies, keyed by name.

    Same convention as the template form: the source is written out once and
    reused by name. Hunterpedia reuses 243 times across 19 sampled pages, so
    reading only the definition site would leave most cited lines unsourced.
    """
    definitions: dict[str, str] = {}
    for match in _REF_TAG.finditer(text or ""):
        name = _REF_NAME.search(match.group(1) or "")
        body = (match.group(2) or "").strip()
        if name and body:
            definitions.setdefault(name.group(1).strip().lower(), body)
    return definitions


def _strip_ref_tags(
    text: str,
    grammar: "CitationGrammar | None",
    definitions: dict[str, str] | None,
    inline_citations: bool = True,
) -> str:
    """Replace every ``<ref>`` with its locator, or with nothing.

    Nothing is the right answer for the many references that cite an interview,
    a cover image or a shop listing. Those carry no chapter, and leaving their
    text in the prose is how a page's bibliography ends up embedded as content.
    """
    definitions = definitions or {}

    def render(match: re.Match[str]) -> str:
        body = (match.group(2) or "").strip()
        if not body:
            name = _REF_NAME.search(match.group(1) or "")
            if name:
                body = definitions.get(name.group(1).strip().lower(), "")
        if not (body and inline_citations and grammar):
            return ""
        located = grammar.from_prose(body)
        if not located:
            return ""
        role, value = located[0]
        label = _ROLE_LABEL.get(role.role)
        if not label:
            return ""
        work = f"{role.work} " if role.work else ""
        return f"({work}{label} {value})"

    return _REF_TAG.sub(render, text or "")


def collect_ref_definitions(text: str) -> dict[str, dict[str, str]]:
    """Named references that carry a locator, keyed by their name.

    MediaWiki cites a source once and reuses it by name: ``{{Ref|name=c145p18|
    chap=145|ep=50}}`` is the definition and every later ``{{Ref|name=c145p18}}``
    means the same thing. Reading only the reuse loses the chapter — 538 of the
    Jujutsu Kaisen corpus's references are name-only, and every one of them
    rendered as nothing at all, leaving the line it cited unsourced.

    Definitions are collected across the whole page, because the definition and
    its reuses routinely sit in different sections.
    """
    definitions: dict[str, dict[str, str]] = {}

    for _, _, body in find_templates(text):
        name, named, _ = parse_template(body)
        if name.strip().lower().startswith(CITATION_TEMPLATES):
            key = (named.get("name") or "").strip().lower()
            if key and key not in definitions and _has_locator(named):
                definitions[key] = named
        else:
            # A citation is usually nested inside the parameter it annotates.
            for key, value in collect_ref_definitions(body).items():
                definitions.setdefault(key, value)

    return definitions


def _with_positional(named: dict[str, str], positional: list[str]) -> dict[str, str]:
    """Fold a template's positional arguments in as ``_0``, ``_1``, ``_2``.

    Chainsaw Man writes every reference positionally — ``{{Ref|m|216|3-4}}`` —
    so a renderer that only reads named parameters sees an empty citation. All
    2,946 of them rendered nothing.
    """
    merged = dict(named)
    for index, value in enumerate(positional):
        if value:
            merged.setdefault(f"_{index}", value)
    return merged


def _has_locator(named: dict[str, str]) -> bool:
    return any(named.get(key) for key in ("chap", "ep", "vol", "fan"))


def _resolve_ref(
    named: dict[str, str], ref_names: dict[str, dict[str, str]] | None
) -> dict[str, str]:
    """A reference's own parameters, or those of the definition it reuses."""
    if not ref_names or _has_locator(named):
        return named
    definition = ref_names.get((named.get("name") or "").strip().lower())
    return definition if definition else named


def extract_citations(
    text: str, ref_names: dict[str, dict[str, str]] | None = None
) -> list[Citation]:
    """Collect citation templates, recursing so nested ones are not missed.

    ``ref_names`` resolves name-only reuses back to the definition's locator, so
    a `Citation` carries the chapter whether it was written out here or once at
    the top of the page.
    """
    citations: list[Citation] = []

    for start, end, body in find_templates(text):
        name, named, positional = parse_template(body)
        lowered = name.strip().lower()

        if lowered.startswith(CITATION_TEMPLATES):
            params = dict(_resolve_ref(named, ref_names))
            for index, value in enumerate(positional):
                if value:
                    params.setdefault(f"_{index}", value)
            citations.append(
                Citation(template=name.strip(), params=params, raw=text[start:end])
            )
        else:
            # A citation is usually nested inside the parameter it annotates.
            citations.extend(extract_citations(body, ref_names))

    return citations


# ─────────────────────────────────────────────────────────────────────────────
# Markup stripping
# ─────────────────────────────────────────────────────────────────────────────


def strip_markup(
    text: str,
    inline_citations: bool = True,
    ref_names: dict[str, dict[str, str]] | None = None,
    works: CitationGrammar | None = None,
    ref_tags: dict[str, str] | None = None,
) -> str:
    """Reduce wikitext to readable prose.

    Citations are flattened to a short locator — ``(Chapter 143)`` — rather
    than dropped or expanded in full. The previous pipeline expanded them into
    the text — 40 to 130 per page of ``[Jujutsu Kaisen Manga: Vol. 5 (p. 26)]``
    — and then embedded that, so a large share of every vector encoded
    bibliography instead of content. Here they are captured as structured
    `Citation` objects for exact lookups and kept in prose only as the brief
    locator that the script's chapter annotations need. Infobox fact values
    pass ``inline_citations=False``: a fact is key-value data, and the citation
    already sits on the fact itself.
    """
    if not text:
        return ""

    text = _HTML_COMMENT.sub("", text)
    text = _MEDIA_BLOCK.sub(" ", text)
    # Before `_HTML_TAG` gets to them, or their bodies become prose.
    text = _strip_ref_tags(text, works, ref_tags, inline_citations)
    text = flatten_tables(text)
    text = _strip_templates(
        text, inline_citations=inline_citations, ref_names=ref_names, works=works
    )
    text = _flatten_links(text)
    text = _HTML_TAG.sub(" ", text)
    text = _QUOTES.sub("", text)
    text = _LIST_PREFIX.sub("", text)

    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')

    text = _WHITESPACE.sub(" ", text)
    text = _BLANK_LINES.sub("\n\n", text)
    return "\n".join(line.strip() for line in text.splitlines()).strip()


def flatten_tables(text: str) -> str:
    """Turn wikitables into readable lines instead of deleting them.

    On a Fandom wiki a table is not decoration. Technique lists, binding vows,
    battle records and episode listings are all tables, and discarding them —
    as the previous cleaner did, and as the obvious ``\\{\\|.*?\\|\\}`` regex
    does — silently removes some of the most factual content on the page.

    Nested tables are common (a technique table inside a layout table), so the
    scan is depth-aware and inner tables are flattened first.
    """
    out: list[str] = []
    i = 0

    while i < len(text):
        start = text.find("{|", i)
        if start == -1:
            out.append(text[i:])
            break

        out.append(text[i:start])
        end = _scan_balanced(text, start, "{|", "|}")
        if end == -1:
            # Unclosed table: keep the remainder rather than losing the page.
            out.append(text[start + 2 :])
            break

        out.append(_flatten_one_table(text[start + 2 : end - 2]))
        i = end

    return "".join(out)


def _is_media_only(cell: str) -> bool:
    """True when a cell contains nothing but file or image links."""
    remainder = cell
    for start, end, _ in reversed(
        [(m.start(), m.end(), "") for m in re.finditer(r"\[\[[^\]]*\]\]", cell)]
    ):
        target = cell[start + 2 : end - 2].split("|", 1)[0]
        if _is_namespaced(target):
            remainder = remainder[:start] + remainder[end:]
    return not remainder.strip(" |'\"")


def _flatten_one_table(body: str) -> str:
    """Render a single table body as one line per row."""
    body = flatten_tables(body)  # inner tables first
    rows: list[list[str]] = []
    current: list[str] = []

    for line in body.splitlines():
        stripped = line.strip()

        if stripped.startswith("|-"):            # row separator
            if current:
                rows.append(current)
                current = []
            continue
        if stripped.startswith("|+"):            # caption
            current.append(stripped[2:].strip())
            continue
        if not stripped.startswith(("|", "!")):
            # A continuation line of the previous cell.
            if current and stripped:
                current[-1] = f"{current[-1]} {stripped}".strip()
            continue

        # `!!` and `||` separate several cells on one line.
        marker = stripped[0]
        separator = "!!" if marker == "!" else "||"
        for cell in stripped[1:].split(separator):
            cell = _CELL_ATTRS.sub("", cell.strip()).strip().lstrip("|").strip()
            # A cell holding only an image renders no text, so keeping it would
            # leave an empty column and a stray " — " in the joined row.
            if cell and not _is_media_only(cell):
                current.append(cell)

    if current:
        rows.append(current)

    lines = [" — ".join(cell for cell in row if cell) for row in rows]
    return "\n" + "\n".join(line for line in lines if line.strip()) + "\n"


def _citation_marker(named: dict[str, str], works: "CitationGrammar | None" = None) -> str:
    """A compact locator for a citation, e.g. ``(Chapter 143, Episode 30)``.

    Page numbers are deliberately left to the structured Citation objects —
    this string travels inside prose that gets embedded, and a page number is
    retrieval noise there. Named refs without a locator (``{{Ref|name=fan2}}``)
    render nothing: their target already carries the marker.

    A sequel or a spin-off numbers its chapters from 1 again, so a citation says
    which work it means. On this wiki that is ``{{Ref|modulo=y|chap=16}}``, and
    dropping the qualifier rendered it ``(Chapter 16)`` — the same string as the
    main series' Chapter 16, and 427 references corpus-wide were affected. A
    script written from that would state the wrong chapter with full confidence.
    The qualifier vocabulary is per-wiki and comes from
    `series/<name>/overrides.yaml`; only the mechanism lives here.
    """
    works = works or CitationGrammar()
    parts: list[str] = []

    prefix = works.prefix_for(named)
    located: list[tuple[RefRole, str]] = []

    # The parameter names this project has always understood, plus whatever this
    # wiki calls them. A wiki-specific name wins, since it is the more precise
    # statement: One-Punch Man's `wch` is a chapter of the webcomic, not the manga.
    for key, role in (
        ("chap", RefRole("chapter")), ("chap2", RefRole("chapter")),
        ("ep", RefRole("episode")), ("ep2", RefRole("episode")),
        ("vol", RefRole("volume")),
    ):
        if named.get(key):
            located.append((role, named[key]))
    for key, role in works.params.items():
        if named.get(key) and role.role != "page":
            located.append((role, named[key]))
    if not located:
        located = works.from_positional(named)

    for role, value in located:
        label = _ROLE_LABEL.get(role.role)
        if not label:
            continue
        work = f"{role.work} " if role.work else prefix
        parts.append(f"{work}{label} {value}".strip())

    # A qualifier can also *be* the instalment rather than qualify one:
    # `{{Ref|movie=0}}` cites the film, which has no chapter at all.
    for key, label in works.instalments.items():
        value = named.get(key)
        if value:
            parts.append(f"{label} {value}".strip())

    if named.get("fan"):
        parts.append(named["fan"].strip())
    if not parts:
        return ""
    return "(" + ", ".join(parts) + ")"


def _strip_templates(
    text: str,
    inline_citations: bool = True,
    ref_names: dict[str, dict[str, str]] | None = None,
    works: CitationGrammar | None = None,
) -> str:
    """Remove templates, keeping the prose from the transparent ones."""
    out: list[str] = []
    i = 0

    while i < len(text):
        start = text.find("{{", i)
        if start == -1:
            out.append(text[i:])
            break

        out.append(text[i:start])
        end = _scan_balanced(text, start, "{{", "}}")
        if end == -1:
            out.append(text[start:])
            break

        name, named, positional = parse_template(text[start + 2 : end - 2])
        lowered = name.strip().lower()

        if lowered.startswith(CITATION_TEMPLATES):
            if inline_citations:
                marker = _citation_marker(
                    _resolve_ref(_with_positional(named, positional), ref_names), works
                )
                if marker:
                    out.append(marker)
        elif lowered in TRANSPARENT_TEMPLATES:
            candidates = [p for p in positional if p and not p.startswith("[[Category")]
            if candidates:
                strategy = TRANSPARENT_TEMPLATES[lowered]
                if strategy == "first":
                    kept = candidates[0]
                elif strategy == "last":
                    kept = candidates[-1]
                else:
                    kept = " ".join(candidates)
                out.append(
                    _strip_templates(
                        kept,
                        inline_citations=inline_citations,
                        ref_names=ref_names,
                        works=works,
                    )
                )
        # Everything else — navboxes, infoboxes, tabs — contributes no prose.

        i = end

    return "".join(out)


def _flatten_links(text: str) -> str:
    """Replace ``[[Target|Display]]`` with its display text."""
    out: list[str] = []
    i = 0

    while i < len(text):
        start = text.find("[[", i)
        if start == -1:
            out.append(text[i:])
            break

        out.append(text[i:start])
        end = _scan_balanced(text, start, "[[", "]]")
        if end == -1:
            out.append(text[start:])
            break

        body = text[start + 2 : end - 2]
        target, _, display = body.partition("|")
        if _renders_text(target.strip()):
            # An interwiki link still shows its label; only its target is
            # elsewhere. Strip the prefix when no label was given.
            shown = (display or target.split(":", 1)[-1]).strip()
            out.append(shown)

        i = end

    result = "".join(out)
    # External links: [https://example.com Label] keeps only the label.
    return re.sub(r"\[(?:https?|//)\S+\s+([^\]]+)\]", r"\1", result)


# ─────────────────────────────────────────────────────────────────────────────
# Infobox
# ─────────────────────────────────────────────────────────────────────────────


def infobox_candidates(text: str, min_params: int = 3) -> list[tuple[str, int]]:
    """Templates on this page that look structurally like an infobox.

    Name matching is not enough. Jujutsu Kaisen calls its infoboxes
    "Character Infobox", but Chainsaw Man calls the same thing "Character" and
    Marvel uses "Marvel Database:Character Template" — searching for the word
    "infobox" finds the first wiki's vocabulary and none of the others'.

    What holds across wikis is the shape. An infobox is transcluded before the
    first heading, carries several named parameters, and appears once. Layout
    templates (tabs, navboxes, scroll boxes) fail at least one of those, and
    inline templates like citations fail the position test.

    Returns `(name, parameter_count)` richest first. The count is the tiebreak
    that separates a real infobox from the layout wrapper beside it: `Tabs`
    declares three parameters, `Character Infobox` declares twenty-one.
    """
    lead = text.split("\n==", 1)[0]

    counts: dict[str, int] = {}
    params: dict[str, int] = {}

    for _, _, body in find_templates(lead):
        name, named, _ = parse_template(body)
        clean = normalise_title(name.strip().lstrip(":"))
        if not clean:
            continue
        counts[clean] = counts.get(clean, 0) + 1
        params[clean] = max(params.get(clean, 0), len(named))

    candidates = [
        (name, params[name])
        for name, count in counts.items()
        if count == 1 and params[name] >= min_params
    ]
    return sorted(candidates, key=lambda pair: pair[1], reverse=True)


def find_infobox(
    text: str, known_templates: set[str] | None = None
) -> tuple[str, dict[str, str]] | None:
    """Return the page's infobox as ``(template_name, raw_params)``.

    ``known_templates`` is the infobox vocabulary discovered from this wiki's
    ``Template:`` namespace. When supplied it is authoritative; otherwise the
    name is matched on the word "infobox", which is the Fandom convention.
    """
    normalised = {t.lower().replace("_", " ") for t in (known_templates or set())}
    matches: list[tuple[int, str, dict[str, str]]] = []

    for _, _, body in find_templates(text):
        name, named, _ = parse_template(body)
        clean = name.strip().lstrip(":").replace("_", " ")
        lowered = clean.lower()

        if lowered.startswith("template:"):
            lowered = lowered.split(":", 1)[1].strip()
            clean = clean.split(":", 1)[1].strip()

        if (normalised and lowered in normalised) or "infobox" in lowered:
            matches.append((len(named), clean, named))

    if not matches:
        return None

    # The richest match wins, not the first. A page commonly opens with a layout
    # wrapper before its real infobox — Jujutsu Kaisen character pages start
    # `{{Tabs|tab1=Profile|tab2=Synopsis|tab3=Image Gallery}}` and only then
    # `{{Character_Infobox|...}}`. Once `Tabs` entered the discovered vocabulary,
    # taking the first match returned three parameters instead of twenty-one,
    # and every character on the wiki lost its facts.
    matches.sort(key=lambda match: match[0], reverse=True)
    return matches[0][1], matches[0][2]


def facts_from_infobox(
    params: dict[str, str],
    labels: dict[str, str] | None = None,
    ref_names: dict[str, dict[str, str]] | None = None,
) -> list[Fact]:
    """Turn infobox parameters into facts, keeping links and citations attached.

    ``labels`` maps parameter names to the wiki's own human labels — ``class`` to
    "Grade", ``race`` to "Species" — as published in the Portable Infobox
    schema. Without it the keys still work; with it they are readable.
    """
    labels = labels or {}
    facts: list[Fact] = []

    for key, raw in params.items():
        if not raw or not raw.strip():
            continue
        # Presentational parameters describe how the box looks, not the subject.
        if key in {"image", "image gallery", "imagesize", "caption", "bgcolor", "color"}:
            continue

        value = strip_markup(raw, inline_citations=False)
        if not value:
            continue

        facts.append(
            Fact(
                key=key,
                value=value,
                label=labels.get(key, ""),
                links=extract_links(raw),
                citations=extract_citations(raw, ref_names),
                raw=raw,
            )
        )

    return facts


# ─────────────────────────────────────────────────────────────────────────────
# Sections
# ─────────────────────────────────────────────────────────────────────────────


def split_sections(
    text: str,
    api_sections: list[dict] | None = None,
    works: CitationGrammar | None = None,
) -> tuple[str, list[Section]]:
    """Split a page into its lead and its sections.

    ``api_sections`` is the section tree from ``prop=sections``, which carries
    authoritative levels. Headings are still located in the wikitext itself
    because byte offsets shift once templates are expanded; the API supplies the
    hierarchy, the wikitext supplies the content.
    """
    levels: dict[str, int] = {}
    if api_sections:
        for entry in api_sections:
            line = entry.get("line", "").strip()
            if line:
                try:
                    levels[line] = int(entry.get("level", 2))
                except (TypeError, ValueError):
                    levels[line] = 2

    # Collected once for the whole page: a `{{Ref|name=x}}` reuse and the
    # definition that gives it a chapter are routinely in different sections.
    ref_names = collect_ref_definitions(text)
    ref_tags = collect_ref_tag_definitions(text)

    matches = list(_HEADING.finditer(text))
    lead = strip_markup(
        text[: matches[0].start()] if matches else text,
        ref_names=ref_names,
        works=works,
        ref_tags=ref_tags,
    )

    sections: list[Section] = []
    ancestors: list[tuple[int, str]] = []

    for index, match in enumerate(matches):
        title = strip_markup(match.group(2)).strip()
        if not title:
            continue

        level = levels.get(title, len(match.group(1)))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end() : end]

        while ancestors and ancestors[-1][0] >= level:
            ancestors.pop()

        section = Section(
            title=title,
            level=level,
            index=str(index + 1),
            anchor=title.replace(" ", "_"),
            path=[name for _, name in ancestors],
            text=strip_markup(
                body, ref_names=ref_names, works=works, ref_tags=ref_tags
            ),
            wikitext=body,
            links=extract_links(body),
            citations=extract_citations(body, ref_names),
        )
        sections.append(section)
        ancestors.append((level, title))

    return lead, sections

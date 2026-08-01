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

from scriptengine.ingest.documents import Citation, Fact, Link, Section

# Templates that cite a source rather than render content. Matched on a prefix
# so `Ref`, `Ref/contents` and `Reflist` are all recognised. This list is about
# MediaWiki convention, not about any particular wiki.
CITATION_TEMPLATES = ("ref", "cite", "sfn")

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


def _is_namespaced(target: str) -> bool:
    """True for links into non-article namespaces, which are not relationships."""
    prefix = target.split(":", 1)[0].strip().lower()
    return prefix in {
        "category", "file", "image", "media", "template", "help", "module",
        "special", "talk", "user", "project", "mediawiki", "w", "wikipedia",
    }


def extract_citations(text: str) -> list[Citation]:
    """Collect citation templates, recursing so nested ones are not missed."""
    citations: list[Citation] = []

    for start, end, body in find_templates(text):
        name, named, positional = parse_template(body)
        lowered = name.strip().lower()

        if lowered.startswith(CITATION_TEMPLATES):
            params = dict(named)
            for index, value in enumerate(positional):
                if value:
                    params.setdefault(f"_{index}", value)
            citations.append(
                Citation(template=name.strip(), params=params, raw=text[start:end])
            )
        else:
            # A citation is usually nested inside the parameter it annotates.
            citations.extend(extract_citations(body))

    return citations


# ─────────────────────────────────────────────────────────────────────────────
# Markup stripping
# ─────────────────────────────────────────────────────────────────────────────


def strip_markup(text: str) -> str:
    """Reduce wikitext to readable prose.

    Citations are removed rather than flattened. The previous pipeline expanded
    them into the text — 40 to 130 per page of ``[Jujutsu Kaisen Manga: Vol. 5
    (p. 26)]`` — and then embedded that, so a large share of every vector
    encoded bibliography instead of content. Here they are captured as
    structured `Citation` objects and stripped from the prose.
    """
    if not text:
        return ""

    text = _HTML_COMMENT.sub("", text)
    text = flatten_tables(text)
    text = _strip_templates(text)
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


def _strip_templates(text: str) -> str:
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

        name, _, positional = parse_template(text[start + 2 : end - 2])
        lowered = name.strip().lower()

        if lowered.startswith(CITATION_TEMPLATES):
            pass  # captured separately; never inlined
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
                out.append(_strip_templates(kept))
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
        if _is_namespaced(target.strip()):
            pass  # category and file links render nothing inline
        else:
            out.append((display or target).strip())

        i = end

    result = "".join(out)
    # External links: [https://example.com Label] keeps only the label.
    return re.sub(r"\[(?:https?|//)\S+\s+([^\]]+)\]", r"\1", result)


# ─────────────────────────────────────────────────────────────────────────────
# Infobox
# ─────────────────────────────────────────────────────────────────────────────


def find_infobox(
    text: str, known_templates: set[str] | None = None
) -> tuple[str, dict[str, str]] | None:
    """Return the page's infobox as ``(template_name, raw_params)``.

    ``known_templates`` is the infobox vocabulary discovered from this wiki's
    ``Template:`` namespace. When supplied it is authoritative; otherwise the
    name is matched on the word "infobox", which is the Fandom convention.
    """
    normalised = {t.lower().replace("_", " ") for t in (known_templates or set())}

    for _, _, body in find_templates(text):
        name, named, _ = parse_template(body)
        clean = name.strip().lstrip(":").replace("_", " ")
        lowered = clean.lower()

        if lowered.startswith("template:"):
            lowered = lowered.split(":", 1)[1].strip()
            clean = clean.split(":", 1)[1].strip()

        if (normalised and lowered in normalised) or "infobox" in lowered:
            return clean, named

    return None


def facts_from_infobox(
    params: dict[str, str], labels: dict[str, str] | None = None
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

        value = strip_markup(raw)
        if not value:
            continue

        facts.append(
            Fact(
                key=key,
                value=value,
                label=labels.get(key, ""),
                links=extract_links(raw),
                citations=extract_citations(raw),
                raw=raw,
            )
        )

    return facts


# ─────────────────────────────────────────────────────────────────────────────
# Sections
# ─────────────────────────────────────────────────────────────────────────────


def split_sections(text: str, api_sections: list[dict] | None = None) -> tuple[str, list[Section]]:
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

    matches = list(_HEADING.finditer(text))
    lead = strip_markup(text[: matches[0].start()] if matches else text)

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
            text=strip_markup(body),
            wikitext=body,
            links=extract_links(body),
            citations=extract_citations(body),
        )
        sections.append(section)
        ancestors.append((level, title))

    return lead, sections

"""Reading an article's data from the page it is transcluded from.

Every wiki crawled before this one writes an article's infobox into the article:
`{{Character Infobox|name=...}}` sits at the top of the page and the parser reads
it there. Some wikis do not. They keep each article's infobox on a page of its
own, in a namespace of its own, and the article says only::

    {{Infobox}}

which the wiki's `Template:Infobox` expands to `{{Infobox:<article title>}}`. The
crawler fetches the main namespace, so the article arrives as that ten-character
call and nothing else: no facts, no type unless the transclusion list happens to
survive, and none of the named references the infobox defines and the prose
reuses. Measured on the first wiki that works this way, 1,453 of 7,794 articles
(every character page) stored zero facts.

The fix is to do what MediaWiki does. The series declares which bare call stands
for which page, the crawler fetches that page alongside the article, and the
call is replaced by the page's wikitext before anything is parsed. From there on
the article looks like every other wiki's, so nothing downstream changes.

The declaration lives in `series/<name>/overrides.yaml`::

    transcluded_pages:
      - template: Infobox           # the bare call an article makes
        page: "Infobox:{title}"     # the page it stands for

Off unless declared. Nothing here names a series, and nothing here touches the
network: which pages to fetch is this module's business, fetching them is the
crawler's.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from scriptengine.ingest.wikitext import find_templates, parse_template

# The placeholder a declared page name carries for the article's own title.
# Replaced literally rather than with `str.format`, because a wiki title may
# itself contain braces.
TITLE_SLOT = "{title}"

_ONLYINCLUDE = re.compile(r"<onlyinclude>(.*?)</onlyinclude>", re.S | re.IGNORECASE)
# An unclosed `<noinclude>` runs to the end of the page, as it does on the wiki.
_NOINCLUDE = re.compile(r"<noinclude>.*?(?:</noinclude>|\Z)", re.S | re.IGNORECASE)
_INCLUDEONLY_TAG = re.compile(r"</?includeonly>", re.IGNORECASE)


@dataclass(frozen=True)
class PageTransclusion:
    """One declared rule: this bare call stands for that page."""

    template: str   # normalised name of the call, e.g. "infobox"
    page: str       # page name with `{title}` for the article, e.g. "Infobox:{title}"

    def target(self, title: str) -> str:
        """The page an article titled ``title`` transcludes."""
        return self.page.replace(TITLE_SLOT, title)


def _normalise(name: str) -> str:
    """``Template:Infobox`` and ``infobox`` are one template.

    Only the `Template:` prefix is dropped. Splitting on the last colon, as the
    list resolver does, would turn a direct `{{Infobox:Some Page}}` into
    `Some Page` and match it against a rule it has nothing to do with.
    """
    cleaned = name.strip().lstrip(":").replace("_", " ")
    if cleaned.lower().startswith("template:"):
        cleaned = cleaned[len("template:"):]
    return cleaned.strip().lower()


def declared_transclusions(overrides: dict[str, Any] | None) -> tuple[PageTransclusion, ...]:
    """The series' `transcluded_pages:` rules, in declaration order.

    A rule missing either half, or whose page does not mention the article, is
    dropped: a page name without `{title}` would splice one page into every
    article that makes the call, which is a list template's job
    (`template_lists:`), not this one's.
    """
    rules: list[PageTransclusion] = []
    for entry in (overrides or {}).get("transcluded_pages") or ():
        if not isinstance(entry, dict):
            continue
        template = _normalise(str(entry.get("template") or ""))
        page = str(entry.get("page") or "").strip()
        if template and page and TITLE_SLOT in page:
            rules.append(PageTransclusion(template=template, page=page))
    return tuple(rules)


def bare_calls(
    wikitext: str, rules: tuple[PageTransclusion, ...]
) -> list[tuple[int, int, PageTransclusion]]:
    """``(start, end, rule)`` for each declared call that carries no arguments.

    Bare is the test because bare is the shape: the call has nothing to say
    because everything it means is on the other page. A call with parameters is
    an infobox written in place, on this wiki or any other, and must be left for
    the parser to read as it stands.

    Only outermost calls are considered, which is also what makes a second pass
    a no-op: once replaced, the call is gone from the text.
    """
    if not rules or not wikitext:
        return []
    by_name = {rule.template: rule for rule in rules}
    found: list[tuple[int, int, PageTransclusion]] = []
    for start, end, body in find_templates(wikitext):
        name, named, positional = parse_template(body)
        rule = by_name.get(_normalise(name))
        if rule is not None and not named and not positional:
            found.append((start, end, rule))
    return found


def targets(title: str, wikitext: str, rules: tuple[PageTransclusion, ...]) -> list[str]:
    """The pages this article needs fetched, without repeats."""
    seen: dict[str, None] = {}
    for _, _, rule in bare_calls(wikitext, rules):
        seen.setdefault(rule.target(title))
    return list(seen)


def as_transcluded(wikitext: str) -> str:
    """The part of a page MediaWiki includes when the page is transcluded.

    `<onlyinclude>` wins when present; otherwise `<noinclude>` blocks are left
    behind and `<includeonly>` is unwrapped. Without this a data page's own
    documentation and categories would be spliced into every article using it.
    """
    text = wikitext or ""
    only = _ONLYINCLUDE.findall(text)
    if only:
        text = "".join(only)
    text = _NOINCLUDE.sub("", text)
    return _INCLUDEONLY_TAG.sub("", text).strip()


def inline(
    title: str,
    wikitext: str,
    rules: tuple[PageTransclusion, ...],
    sources: dict[str, str],
) -> tuple[str, list[str]]:
    """Replace each declared bare call with the page it stands for.

    ``sources`` maps a page name to its wikitext. Returns the new wikitext and
    the pages that were wanted and not supplied; their calls are left exactly as
    the article wrote them, so a missing page is visible in the stored text
    rather than silently erased.

    Spans are replaced last-to-first so earlier offsets stay valid as the text
    grows.
    """
    missing: list[str] = []
    out = wikitext
    for start, end, rule in sorted(
        bare_calls(wikitext, rules), key=lambda span: span[0], reverse=True
    ):
        target = rule.target(title)
        source = sources.get(target)
        if source is None:
            missing.append(target)
            continue
        out = out[:start] + as_transcluded(source) + out[end:]
    return out, sorted(set(missing))


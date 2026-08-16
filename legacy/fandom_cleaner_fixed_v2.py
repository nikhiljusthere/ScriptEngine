#!/usr/bin/env python3
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

REMOVE_ALWAYS_TAGS = {"script", "style", "iframe"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
BLOCK_CHILD_TAGS = {"ul", "ol", "table", "p", "div", "blockquote", "section", "article", "aside"}


# Additional corpus-level filtering for graph quality
SKIP_PAGE_PATTERNS = [
    re.compile(r"^Modulo ", re.I),
    re.compile(r"^Jujutsu Kaisen Modulo$", re.I),
    re.compile(r"^Blu-ray & DVD ", re.I),
]

NOISE_ENTITY_TERMS = {
    "Kanji", "Rōmaji", "Romaji", "Kana",
    "Japanese", "English", "Alias"
}

NOISE_CLASSES = re.compile(
    r"(ambox|notice|warning|metadata|mw-editsection|bottom|pi-navigation|pi-image-collection|wds-tabs|wds-tab__content|"
    r"wikia-gallery|gallery|thumbcaption|lightbox-caption|gallery-image-wrapper|thumb|caption|info-icon|navbox|navibox|"
    r"catlinks|categories|toc|mw-empty-elt|latest)"
)


def should_skip_page(stem: str) -> bool:
    return any(p.search(stem) for p in SKIP_PAGE_PATTERNS)

def post_clean_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.strip() in NOISE_ENTITY_TERMS:
            continue
        line = re.sub(r"[’']s\b", "", line)
        lines.append(line)
    return "\n".join(lines)


def normalize_ws(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def compact_spaces(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+\.", ".", text)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r"\s+;", ";", text)
    text = re.sub(r"\s+:", ":", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\[\s+", "[", text)
    text = re.sub(r"\s+\]", "]", text)
    text = re.sub(r"\s+'s\b", "'s", text)
    text = re.sub(r"(\])([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"([a-zA-Z0-9])\s+\(", r"\1 (", text)
    return text

def clean_text(text: str) -> str:
    return normalize_ws(compact_spaces(text))

def is_label_like(text: str) -> bool:
    t = normalize_ws(text).rstrip(":")
    if not t or re.search(r"[.!?]$", t):
        return False
    if t.startswith("As "):
        return True
    return len(t.split()) <= 5

def build_citation_map(soup: BeautifulSoup) -> dict[str, str]:
    cmap: dict[str, str] = {}
    for li in soup.find_all("li", id=re.compile(r"^cite_note")):
        ref_span = li.find("span", class_="reference-text")
        if not ref_span:
            continue
        txt = clean_text(ref_span.get_text(" ", strip=True)).replace("↑", "").strip().rstrip(" .")
        if txt:
            cmap[li["id"]] = txt
    return cmap

def replace_citations(soup: BeautifulSoup, cmap: dict[str, str]) -> None:
    for sup in list(soup.find_all("sup", class_="reference")):
        a = sup.find("a", href=True)
        if not a:
            sup.decompose()
            continue
        href = a["href"].lstrip("#")
        if href in cmap:
            sup.replace_with(f"[{cmap[href]}]")
        else:
            sup.decompose()

def remove_japanese_annotations(soup: BeautifulSoup) -> None:
    for span in list(soup.find_all("span")):
        attrs = getattr(span, "attrs", {}) or {}
        classes = attrs.get("class") or []
        if any("t_nihongo" in c for c in classes):
            span.decompose()
            continue
        style = (attrs.get("style") or "").replace(" ", "")
        if ("font-weight:normal" in style or "font-weight:bold" in style) and span.find(class_=re.compile(r"t_nihongo")):
            span.decompose()
    for tag in list(soup.find_all(["ruby", "rb", "rt", "rp"])):
        tag.decompose()
    for a in list(soup.find_all("a", href=re.compile(r"Installing_Japanese"))):
        parent = a.parent
        a.decompose()
        if parent and getattr(parent, "name", None) == "sup" and not parent.get_text(strip=True):
            parent.decompose()

def remove_noise(soup: BeautifulSoup) -> None:
    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()

    for tag in list(soup.find_all(list(REMOVE_ALWAYS_TAGS))):
        tag.decompose()

    for el in list(soup.find_all(class_=NOISE_CLASSES)):
        if getattr(el, "name", None) in {"div", "table", "span", "section", "nav", "aside", "figure", "p", "li"}:
            if "mw-collapsible" in (el.get("class") or []):
                continue
            el.decompose()

    for el in list(soup.find_all(id="toc")):
        el.decompose()

    for fig in list(soup.find_all("figure")):
        fig.decompose()
    for el in list(soup.find_all(["img", "svg", "noscript"])):
        el.decompose()

    for el in list(soup.find_all("div", class_="mw-collapsible")):
        el.unwrap()
    for el in list(soup.find_all(["blockquote", "cite", "small", "sub", "dl", "dd"])):
        if el.parent is not None:
            el.unwrap()

    for p in list(soup.find_all("p", class_="mw-empty-elt")):
        p.decompose()

    for a in list(soup.find_all("a", href=True)):
        a.unwrap()

def _sanitize_clone(tag: Tag) -> Tag:
    clone = copy.deepcopy(tag)
    for el in list(clone.find_all(list(REMOVE_ALWAYS_TAGS))):
        el.decompose()
    for el in list(clone.find_all(["figure", "img", "svg", "noscript"])):
        el.decompose()
    for el in list(clone.find_all(class_=re.compile(r"(bottom|pi-navigation|pi-image|pi-image-collection|wds-tabs|wds-tab__content|gallery|thumb|lightbox-caption|thumbcaption|info-icon|caption|ambox|notice|warning)"))):
        if getattr(el, "name", None) in {"div", "table", "span", "figure", "nav", "p", "li", "section"}:
            el.decompose()
    for br in list(clone.find_all(["br", "hr"])):
        br.replace_with("<<<BR>>>")
    for el in list(clone.find_all(["small", "sub", "sup", "b", "i", "em", "strong", "span", "a"])):
        if el.parent is not None:
            el.unwrap()
    return clone

def _render_inline(node) -> str:
    if isinstance(node, NavigableString):
        return normalize_ws(str(node))
    if not isinstance(node, Tag):
        return ""
    if node.name in REMOVE_ALWAYS_TAGS or node.name in {"figure", "img", "svg", "noscript"}:
        return ""
    clone = _sanitize_clone(node)
    txt = clone.get_text(separator=" ", strip=True).replace("<<<BR>>>", "\n")
    return clean_text(txt)

def _split_lines(text: str) -> list[str]:
    return [normalize_ws(x) for x in text.replace("<<<BR>>>", "\n").split("\n") if normalize_ws(x)]


def _render_value_lines(node, indent: int = 1) -> list[str]:
    lines: list[str] = []
    buf: list[str] = []

    def flush():
        nonlocal buf
        if not buf:
            return
        txt = clean_text(" ".join(buf))
        buf = []
        if txt:
            lines.append(f"{'  '*indent}{txt}")

    for child in getattr(node, "children", []):
        if isinstance(child, NavigableString):
            txt = normalize_ws(str(child))
            if txt:
                if "<<<BR>>>" in txt:
                    parts = txt.split("<<<BR>>>")
                    for idx, part in enumerate(parts):
                        part = normalize_ws(part)
                        if part:
                            buf.append(part)
                        if idx != len(parts) - 1:
                            flush()
                else:
                    buf.append(txt)
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()
        if name in {"br", "hr"}:
            flush()
            continue
        if name in {"ul", "ol"}:
            flush()
            items = []
            for li in child.find_all("li", recursive=False):
                item = _render_inline(li)
                if item:
                    items.append(item)
            for item in items:
                lines.append(f"{'  '*indent}- {item}")
            continue
        if name in {"p", "div", "blockquote"}:
            txt = _render_inline(child)
            if txt:
                flush()
                for part in _split_lines(txt):
                    lines.append(f"{'  '*indent}{part}")
            continue
        txt = _render_inline(child)
        if txt:
            buf.append(txt)

    flush()

    out: list[str] = []
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        if re.fullmatch(r"[\(\)\[\]\s\-:]+", line.strip()):
            continue
        out.append(line)
    return out


def extract_infobox(soup: BeautifulSoup) -> str:
    aside = soup.find("aside", role="region")
    if not aside:
        return ""
    lines: list[str] = []

    title = aside.find(class_="pi-title")
    if title:
        t = clean_text(title.get_text(" ", strip=True))
        if t and t != "#":
            lines.append(f"### {t}")

    for hdr in aside.find_all(class_="pi-header"):
        if hdr.find_parent("section") is not None:
            continue
        txt = clean_text(hdr.get_text(" ", strip=True))
        if txt and txt not in {"#", "Contents"}:
            lines.append(f"\n**{txt}**")

    for section in aside.find_all("section", class_="pi-group"):
        header = section.find(class_="pi-header")
        if header:
            htxt = clean_text(header.get_text(" ", strip=True))
            if htxt and htxt not in {"#", "Contents"}:
                lines.append(f"\n**{htxt}**")

        for table in section.find_all("table", class_="pi-horizontal-group"):
            cap = table.find("caption")
            if cap:
                cap_txt = clean_text(cap.get_text(" ", strip=True))
                if cap_txt:
                    lines.append(f"\n**{cap_txt}**")
            header_cells = [clean_text(th.get_text(" ", strip=True)) for th in table.find_all("th")]
            for row in table.find_all("tr"):
                cells = row.find_all("td", recursive=False)
                if not cells:
                    continue
                for idx, td in enumerate(cells):
                    val = clean_text(_render_inline(td).replace("←", "").replace("→", ""))
                    if not val:
                        continue
                    lbl = header_cells[idx] if idx < len(header_cells) else ""
                    if lbl:
                        lines.append(f"  {lbl}: {val}")
                    else:
                        lines.append(f"  {val}")
            continue

        for item in section.find_all("div", class_="pi-data"):
            label_tag = item.find(class_="pi-data-label")
            value_tag = item.find(class_="pi-data-value")
            if not label_tag or not value_tag:
                continue
            label = clean_text(label_tag.get_text(" ", strip=True))
            if not label:
                continue
            vals = _render_value_lines(value_tag, indent=2)
            if not vals:
                raw = clean_text(value_tag.get_text(" ", strip=True))
                if raw:
                    lines.append(f"  {label}: {raw}")
                continue
            if len(vals) == 1 and not vals[0].lstrip().startswith("-"):
                lines.append(f"  {label}: {vals[0].strip()}")
            else:
                lines.append(f"  {label}:")
                for ln in vals:
                    txt = ln.strip()
                    if txt.startswith("- "):
                        lines.append(f"    {txt}")
                    else:
                        lines.append(f"    - {txt}")
    aside.decompose()
    return "## Infobox\n" + "\n".join(lines).strip() + "\n" if lines else ""

def render_block(node) -> str:
    if isinstance(node, NavigableString):
        return normalize_ws(str(node))
    if not isinstance(node, Tag):
        return ""
    if node.name in REMOVE_ALWAYS_TAGS or node.name in {"figure", "img", "svg", "noscript"}:
        return ""
    if node.name in HEADING_TAGS:
        headline = node.find(class_="mw-headline")
        text = headline.get_text(" ", strip=True) if headline else node.get_text(" ", strip=True)
        text = clean_text(text)
        if not text or text.lower() in {"contents", "references", "navigation"} or re.fullmatch(r"[#\s]+", text):
            return ""
        return f"{'#' * int(node.name[1])} {text}"
    if node.name in {"p", "blockquote"}:
        return _render_inline(node)
    if node.name == "div":
        has_block = any(isinstance(c, Tag) and c.name in BLOCK_CHILD_TAGS for c in node.children)
        if has_block:
            parts = [render_block(c) for c in node.children]
            parts = [p for p in parts if p]
            return "\n\n".join(parts)
        return _render_inline(node)
    if node.name in {"section", "article", "aside"}:
        parts = [render_block(c) for c in node.children]
        parts = [p for p in parts if p]
        return "\n\n".join(parts)
    if node.name == "ul":
        items = []
        for li in node.find_all("li", recursive=False):
            txt = _render_inline(li)
            if txt:
                items.append(f"- {txt}")
        return "\n".join(items)
    if node.name == "ol":
        items = []
        for i, li in enumerate(node.find_all("li", recursive=False), start=1):
            txt = _render_inline(li)
            if txt:
                items.append(f"{i}. {txt}")
        return "\n".join(items)
    if node.name == "table":
        rows = []
        for tr in node.find_all("tr"):
            cells = tr.find_all(["td", "th"], recursive=False)
            texts = [clean_text(_render_inline(c)) for c in cells if clean_text(_render_inline(c))]
            if texts:
                rows.append(" | ".join(texts))
        return "\n".join(rows)
    return _render_inline(node)

def extract_body_text(soup: BeautifulSoup) -> str:
    content = soup.find("div", class_="mw-parser-output") or soup.find("div", class_="mw-content-ltr") or soup
    blocks: list[str] = []
    for child in content.children:
        if isinstance(child, Tag) and child.name in HEADING_TAGS:
            headline = child.find(class_="mw-headline")
            heading_txt = headline.get_text(" ", strip=True) if headline else child.get_text(" ", strip=True)
            if clean_text(heading_txt).lower() in {"references", "navigation"}:
                break
        rendered = render_block(child)
        if rendered:
            blocks.append(rendered)
    text = "\n\n".join(blocks)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\]\s*\[", "; ", text)
    text = re.sub(r"(\])([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"\s+\.", ".", text)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r"\s+;", ";", text)
    text = re.sub(r"\s+:", ":", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\[\s+", "[", text)
    text = re.sub(r"\s+\]", "]", text)
    text = re.sub(r"\s+'s\b", "'s", text)
    text = re.sub(r"\s+([?!])", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = []
    for line in text.splitlines():
        line = normalize_ws(line)
        if not line:
            lines.append("")
            continue
        if re.fullmatch(r"[↑→←•·\-–—\/\\\d\s\.]*", line):
            continue
        lines.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()

def detect_page_type(stem: str, soup: BeautifulSoup) -> str:
    s = stem.lower().replace("_", " ")
    if s.startswith("list of battles"):
        return "list_battles"
    if s.startswith("list of episodes"):
        return "list_episodes"
    if s.startswith("list of characters"):
        return "list_characters"
    if s.startswith("chapter "):
        return "chapter"
    if s.startswith("episode "):
        return "episode"
    if s.startswith("volume "):
        return "volume"
    if re.search(r"\bvs\.?\b", s):
        return "battle"
    if s.endswith(" technique") or " technique" in s:
        return "technique"
    if s.endswith(" arc"):
        return "arc"
    if s.startswith("list of "):
        return "list"
    aside = soup.find("aside", role="region")
    if aside:
        sources = {d.get("data-source", "") for d in aside.find_all(attrs={"data-source": True})}
        if {"season number", "jp air date"} & sources:
            return "episode"
        if {"jp release", "eng release", "pages"} & sources:
            return "volume"
        if {"cover", "pages"} <= sources or {"pages", "date"} <= sources:
            return "chapter"
        if {"outcome", "side1", "side2"} & sources:
            return "battle"
        if {"race", "type", "user"} & sources:
            return "technique"
        if {"race", "age", "gender"} & sources:
            return "character"
    return "concept"

def extract_list_battles(soup: BeautifulSoup) -> str:
    content = soup.find("div", class_="mw-parser-output") or soup
    lines = []
    for child in content.children:
        if isinstance(child, Tag) and child.name == "p":
            txt = _render_inline(child)
            if txt:
                lines.append(txt)
            break
    for div in content.find_all("div", recursive=False):
        if div.get("id") == "toc":
            continue
        h1 = div.find("h1", recursive=False)
        table = div.find("table", recursive=False)
        if not h1 or not table:
            continue
        arc = _render_inline(h1)
        if arc:
            lines.append(f"\n## {arc}")
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"], recursive=False)
            if not cells or all(c.name == "th" for c in cells):
                continue
            if len(cells) >= 3:
                battle_td, outcome_td = cells[1], cells[2]
            elif len(cells) == 2:
                battle_td, outcome_td = cells[0], cells[1]
            else:
                battle_td, outcome_td = cells[0], None
            battle = _render_inline(battle_td)
            if not battle or battle.lower() in {"image", "battle / event", "battle/event", "outcome"}:
                continue
            line = f"- {battle}"
            if outcome_td:
                outcome = _render_inline(outcome_td)
                if outcome and outcome.lower() not in {"image", "battle / event", "battle/event", "outcome"}:
                    line += f": {outcome}"
            lines.append(line)
    return "\n".join(lines).strip()

def extract_list_episodes(soup: BeautifulSoup) -> str:
    content = soup.find("div", class_="mw-parser-output") or soup
    lines = []
    for block in content.find_all("div", recursive=False):
        h1 = block.find("h1", recursive=False)
        table = block.find("table", recursive=False)
        if not h1 or not table:
            continue
        season = _render_inline(h1)
        if season:
            lines.append(f"## {season}")
        for row in table.find_all("tr"):
            cells = row.find_all("td", recursive=False)
            if not cells:
                continue
            num = _render_inline(cells[0]) if len(cells) > 0 else ""
            title = _render_inline(cells[2]) if len(cells) > 2 else ""
            air = _render_inline(cells[3]) if len(cells) > 3 else ""
            title = re.sub(r"\s*\(.*\)$", "", title).strip()
            if num and title:
                item = f"- Episode {num}: {title}"
                if air:
                    item += f", {air}"
                lines.append(item)
    return "\n".join(lines).strip() if lines else extract_body_text(soup)

def extract_list_characters(soup: BeautifulSoup) -> str:
    content = soup.find("div", class_="mw-parser-output") or soup
    lines = []
    intro = None
    for child in content.children:
        if isinstance(child, Tag) and child.name == "p":
            txt = _render_inline(child)
            if txt:
                intro = txt
            break
    if intro:
        lines.append(intro)
    for h2 in content.find_all("h2", recursive=False):
        title = _render_inline(h2)
        if not title or title.lower() in {"contents", "navigation"}:
            continue
        lines.append(f"\n## {title}")
        bucket, seen, sub_seen = [], set(), set()
        sib = h2.next_sibling
        while sib and not (isinstance(sib, Tag) and sib.name == "h2"):
            if isinstance(sib, Tag):
                for sh in sib.find_all(class_=re.compile(r"head0|head1|head2|head3")):
                    sub = _render_inline(sh)
                    if sub and sub not in {"2018", "2007", "2086"} and sub not in sub_seen:
                        sub_seen.add(sub)
                        lines.append(f"### {sub}")
                for a in sib.find_all("a", href=True):
                    txt = _render_inline(a)
                    if not txt or txt in {"Contents", "Navigation", title} or txt.isdigit() or len(txt) > 45:
                        continue
                    if txt not in seen:
                        seen.add(txt)
                        bucket.append(txt)
            sib = sib.next_sibling
        for name in bucket:
            lines.append(f"- {name}")
    return "\n".join(lines).strip() if lines else (intro or "")

def convert_file(html_path: Path, out_dir: Path) -> Path:
    if should_skip_page(html_path.stem):
        return Path()
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    page_type = detect_page_type(html_path.stem, soup)

    cmap = build_citation_map(soup)
    replace_citations(soup, cmap)
    remove_japanese_annotations(soup)
    infobox_block = extract_infobox(soup)
    remove_noise(soup)

    parts = []
    if infobox_block:
        parts.append(infobox_block.strip())

    if page_type == "list_battles":
        parts.append(extract_list_battles(soup))
    elif page_type == "list_episodes":
        parts.append(extract_list_episodes(soup))
    elif page_type == "list_characters":
        parts.append(extract_list_characters(soup))
    else:
        parts.append(extract_body_text(soup))

    final = "\n\n".join(p.strip() for p in parts if p and p.strip())
    final = final.replace("\xa0", " ")
    final = post_clean_text(re.sub(r"\n{3,}", "\n\n", final).strip()) + "\n"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (html_path.stem + ".txt")
    out_path.write_text(final, encoding="utf-8")
    return out_path

def main() -> None:
    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("./cleaned_output")
    html_files = sorted(input_dir.rglob("*.html"))
    if not html_files:
        print(f"No .html files found in {input_dir}")
        sys.exit(1)
    print(f"Found {len(html_files)} HTML file(s) under {input_dir}")
    print(f"Writing cleaned text to: {output_dir}\n")
    errors = []
    for html_path in html_files:
        try:
            out_path = convert_file(html_path, output_dir)
            size_in = html_path.stat().st_size
            size_out = out_path.stat().st_size
            ratio = (1 - (size_out / size_in)) * 100 if size_in else 0
            print(f"  {html_path.name:48s} → {out_path.name:30s}  ({size_in // 1024:>4} KB → {size_out // 1024:>3} KB, {ratio:.0f}% noise removed)")
        except Exception as e:
            errors.append((html_path.name, str(e)))
            print(f"  ERROR {html_path.name}: {e}")
    print(f"\nDone. {len(html_files) - len(errors)} OK, {len(errors)} errors.")
    if errors:
        for name, err in errors:
            print(f"  FAILED: {name}: {err}")

if __name__ == "__main__":
    main()

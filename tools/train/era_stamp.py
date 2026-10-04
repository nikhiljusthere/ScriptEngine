#!/usr/bin/env python3
"""Era stamp for the Marvel franchise stores (U-WP2..U-WP2d, 2026-10-04).

Stamps every page of the store with the era it belongs to, from release
facts, the wiki's category links and the store's own wikilinks -- never
from free text:
  tier 1: the page's own release fact, in the per-store key order
          (marvel: `year`, then `releasedate` / `release date`;
           mcu: `release`, `released`, `first aired`, `release1`);
          a value parses to a year by 4-digit regex, a range yields its
          first year, and a year outside 1930-2030 is rejected;
  tier 1b (mcu, U-WP2d): a media page (movie/tv_series/episode/
          one_shot/game/book) with NO tier-1 year is dated from the
          `release` / `released` / `first aired` / `premiere` parameter
          of the FIRST infobox template of its raw wikitext (template
          parameter parse, never free text -- the infobox parser loses
          the params after a `<ref>` whose link text ends in `]`, an
          engine defect noted in the U-WP2d receipt, not fixed here),
          source `wikitext:<param>`;
  tier 2 (marvel): the page's `first` fact, resolved to the issue
          page's own tier-1 year by case-insensitive title match (one
          hop; unresolvable values are counted, never guessed);
  tier 2 (mcu): U-WP2c series-dating + categories -- a media document
          with NO tier-1 fact is dated by the earliest tier-1 year
          among the pages filed under `<media> Episodes` (source
          `episodes:<media>`) or its own `first` fact resolved to an
          episode/issue page with a tier-1 year (source
          `series_first:<media>`); the page's era then comes from the
          `categories` table -- `<Media> <role>`: strip the role word,
          resolve the media title (case-insensitive exact title) to a
          dated document (own tier-1 or series-dated), the EARLIEST
          such year wins (source `category:<media>`). Media pages keep
          their own release fact (tier 1 beats everything).
  tier 3 (mcu, U-WP2c, last-but-one): a page still undated is dated
          by the EARLIEST dated media document (film/tv series/
          episode/one-shot) it links to through the store's
          pre-resolved wikilinks (chunks -> chunk_nodes -> node ->
          document), restricted to links in the page's LEAD or FIRST
          section; source `link:<media>`.
  tier 4 (mcu, U-WP2d, last): a page still undated after EVERY other
          tier is dated by the EARLIEST dated media page (movie/tv
          series/episode/one-shot) whose own sections link TO it
          through the store's pre-resolved wikilinks (the media
          page's chunks' chunk_nodes pointing at the page's node);
          source `inlink:<media>`.
  else:   undated.
Eras: old < 2010, mid 2010-2020, new >= 2021.

U-WP2b: the mcu `date` fact is an IN-UNIVERSE date (the 1943 "Attack
at Azzano" is from the 2011 film), never a release signal: it is
reported in a `story_year` field, not used for the era.

U-WP2c section eras: a page's record carries a `sections` map
{section_title: year} for a section title that resolves to a dated
document -- and only when the match is not a generic-heading accident:
  mcu:   the section's media is ALSO one of the page's own category
          media (its `<media> <role>` rows);
  marvel: the section title is a comic issue/volume page title
          (page_type `comic` or `volume`).
A page whose sections never survive carries `"sections": {}`. The pool
emitter prefers the section era over the page era for a window.

Writes series/<s>/training/era.json (older outputs are renamed
*.pre-wp2b*, supersede-don't-delete):
    {page: {"year": int|null, "era": "old"|"mid"|"new"|"undated",
            "source": "<fact key, category:/episodes:/series_first:/
                       link:<media>, or rule>",
            "story_year": int|null (mcu only, the `date` fact),
            "sections": {section_title: year}}}
and reports era counts x top-8 page_type, % undated, the source-key
histogram, 10 random (title, year, source, page_type) rows per era
(seed 42; mcu rows include at least 3 character pages), and for mcu:
zero-category pages, media that resolve to no dated document (top 20
by page count), how many section eras survive the U-WP2c filter +
10 random survivors, the link-tier coverage on conflict/event
pages + 10 random conflict rows, and for U-WP2d: how many media
pages the tier-1b wikitext param dated (+10 random title/year rows)
and the inlink-tier coverage on conflict/event (+10 random rows).

    python tools/train/era_stamp.py --series marvel
    python tools/train/era_stamp.py --series mcu
"""
import argparse
import json
import random
import re
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# The tier-1b wikitext param scan reuses the engine's balanced template
# scanner (find_templates/parse_template): "template parameter parse, not
# free text" must mean the same scan the engine uses, so the two never
# diverge.
sys.path.insert(0, str(ROOT))
from scriptengine.ingest.wikitext import find_templates, parse_template

# The page's own release facts, per store, in priority order: the first
# tier that yields a parseable year stamps the page; a later tier is
# read only when every earlier tier yielded none. The stores carry the
# keys lowercase (verified 2026-10-04) and `facts.key` is indexed, so
# this is a key-indexed read, not a scan.
OWN_DATE_TIERS = {
    "marvel": (["year"], ["releasedate", "release date"]),
    "mcu": (["release"], ["released"], ["first aired"], ["release1"]),
}
# U-WP2b: the mcu `date` fact is an IN-UNIVERSE date (the 1943 "Attack
# at Azzano" is from the 2011 film), never a release signal: it is
# reported as `story_year`, not used for the era.
STORY_KEY = "date"
# The marvel tier-2 rule (U-WP2): the page's first-appearance fact, an
# issue title, resolved to that page's own tier-1 year.
FALLBACK_KEY = "first"
# U-WP2c: the media page types the link tier may date a page from
# (film, tv series, episode, one-shot) and the target types the mcu
# series-dating `first` fact must resolve to (episode / issue).
MCU_MEDIA_TYPES = ("movie", "tv_series", "episode", "one_shot")
MCU_FIRST_TARGET_TYPES = ("episode", "comic")
# U-WP2c: marvel section eras only accept a section title that is a
# comic issue/volume page title (generic headings like "Civil War" that
# match an event/arc page are false matches).
MARVEL_SECTION_TARGET_TYPES = ("comic", "volume")
# U-WP2d fix A: the media page types tier 1b covers (movie/tv series/
# episode-like one-shots/video games/books), and the release-param
# names read in priority order from the FIRST infobox template of the
# raw wikitext (normalised: lowercased, spaces/underscores/dashes
# folded, so `first aired`, `first_aired` and `First Aired` are one).
MCU_MEDIA_WIKI_TYPES = ("movie", "tv_series", "episode", "one_shot",
                       "game", "book")
WIKI_RELEASE_PARAMS = ("release", "released", "firstaired", "premiere")
# U-WP2d fix B: the media page types whose own sections may date a page
# through the INBOUND tier (the media side of an `inlink:` pair). Games
# and books are deliberately out: the spec's inbound sources are film/
# tv media.
MCU_INLINK_MEDIA_TYPES = ("movie", "tv_series", "episode", "one_shot")
# A 4-digit number inside a date-fact value, not embedded in a longer
# run of digits ("242" alone is not a year; "1994-2009" yields the
# first year).
YEAR_RE = re.compile(r"(?<!\d)(\d{4})(?!\d)")
YEAR_MIN, YEAR_MAX = 1930, 2030
ERAS = ("old", "mid", "new", "undated")


def era_of(year):
    if year is None:
        return "undated"
    if year < 2010:
        return "old"
    if year < 2021:
        return "mid"
    return "new"


def parse_year(value):
    """The value's first in-range 4-digit year, or None.

    A range yields its first year ("1994-2009" -> 1994, "Early 1960s" ->
    1960). A year outside 1930-2030 is rejected rather than guessed: a
    `releasedate` of "May 2026" is a stamp; a value with no in-range
    year in it is not one.
    """
    for match in YEAR_RE.finditer(str(value or "")):
        year = int(match.group(1))
        if YEAR_MIN <= year <= YEAR_MAX:
            return year
    return None


def norm_template_name(name):
    """Compare the store's `infobox_template` spelling against the
    wikitext template name: fold the colons (the engine's
    fold_template_colons), then spaces/underscores/dashes, casefold.

    The store spells the one-shot infobox `one-shot` and the hub
    `hub main`; the wikitext spells them however the wiki wrote the
    transclusion. Folding both sides keeps the two comparable.
    """
    return re.sub(r"[\s_\-]+", " ",
                  re.sub(r"\s*:\s*", ":", (name or "").strip().lstrip(":"))
                  ).casefold().strip()


def scan_template_params(body):
    """The top-level named params of a template body, HTML-safe.

    The engine's `split_params` tracks only `{{}}` and `[[ ]]` depth: a
    `<ref>` body whose external-link text ends in a `]` (e.g.
    `[UPDATE]]`) corrupts the bracket count, and every later
    top-level `|` stops splitting -- the params after it (on `Iron Man
    (film)`, `release` among them) are swallowed into the last param
    (U-WP2d engine defect, noted in the receipt, not fixed on purpose).
    This scanner treats every `<...>` span as atomic: a
    `<ref ...>...</ref>` pair skips to its closing tag, a self-closing
    `<ref name="x"/>` or plain tag skips to its `>`, so a stray `]`
    inside a citation can never touch the depth.
    """
    parts: list[str] = []
    cur: list[str] = []
    i, n, brace, bracket = 0, len(body), 0, 0
    while i < n:
        if body.startswith("{{", i):
            brace += 1; cur.append("{{"); i += 2
        elif body.startswith("}}", i):
            brace -= 1; cur.append("}}"); i += 2
        elif body.startswith("[[", i):
            bracket += 1; cur.append("[["); i += 2
        elif body.startswith("]]", i):
            bracket -= 1; cur.append("]]"); i += 2
        elif body[i] == "<":
            if body.startswith("<ref", i):
                gt = body.find(">", i)
                if gt == -1:
                    i = n
                elif gt > i and body[gt - 1] == "/":
                    i = gt + 1            # self-closing <ref name="x"/>
                else:
                    close = body.find("</ref", gt)
                    gt2 = body.find(">", close) if close != -1 else -1
                    i = (gt2 + 1) if gt2 != -1 else n
            else:
                gt = body.find(">", i)
                i = (gt + 1) if gt != -1 else n
            continue
        elif body[i] == "|" and brace == 0 and bracket == 0:
            parts.append("".join(cur))
            cur = []
            i += 1
        else:
            cur.append(body[i])
            i += 1
    parts.append("".join(cur))
    named: dict[str, str] = {}
    for part in parts[1:]:
        if "=" not in part:
            continue
        key, _sep, value = part.partition("=")
        # the same key normalisation as the engine's _normalise_param
        key = re.sub(r"[\s_-]+", "", key.strip().lower())
        if key:
            named.setdefault(key, value.strip())
    return named


def wikitext_release_year(path, template_name):
    """`(year, param)` for the page's raw wikitext, never free text.

    Reads the FIRST `template_name` infobox (the store's own
    `infobox_template` classification, matched on the top-level
    templates) and returns the first WIKI_RELEASE_PARAMS key present
    there, parsed through the same 4-digit rule as tier 1. The
    returned `param` is `None` when none of the four keys is present,
    in which case `year` is `None` too; a present key with no
    in-range year also yields `year=None`. `path=None` (the page has
    no stored wikitext) yields `(None, None)`.
    """
    if path is None:
        return (None, None)
    data = json.loads(path.read_text(encoding="utf-8"))
    wikitext = data.get("wikitext") or ""
    want = norm_template_name(template_name)
    for _start, _end, body in find_templates(wikitext):
        name, _named, _pos = parse_template(body)
        if norm_template_name(name) != want:
            continue
        named = scan_template_params(body)
        for param in WIKI_RELEASE_PARAMS:
            value = named.get(param)
            if not value:
                continue
            return (parse_year(value), param)
        return (None, None)
    return (None, None)


def random_rows(out, page_type, era, rng, min_characters=0):
    """10 (title, year, source, page_type) rows of one era,
    seed-deterministic; for mcu at least `min_characters` of them are
    character pages (the era the pool samples from, so the spot-check
    sees character pages)."""
    pool = sorted(t for t in out if out[t]["era"] == era)
    chars = [t for t in pool if page_type[t] == "character"]
    picked = rng.sample(chars, min(min_characters, len(chars)))
    rest = [t for t in pool if t not in set(picked)]
    picked += rng.sample(rest, min(10 - len(picked), len(rest)))
    print(f"random 10 ({era}, n={len(pool)}):")
    for t in picked:
        rec = out[t]
        year = "null" if rec["year"] is None else str(rec["year"])
        print(f"  {t} | {year} | {rec['source']} | {page_type[t]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", required=True, choices=sorted(OWN_DATE_TIERS))
    a = ap.parse_args()
    series = a.series
    sroot = ROOT / "series" / series
    db = sroot / "facts.db"
    if not db.exists():
        sys.exit(f"{series} is not indexed (no {db})")

    t0 = time.monotonic()
    con = sqlite3.connect(db)
    titles = [r[0] for r in con.execute("SELECT title FROM documents")]
    page_type = dict(con.execute("SELECT title, page_type FROM documents"))
    tiers = OWN_DATE_TIERS[series]
    keys = [k for tier in tiers for k in tier]
    if series == "marvel":
        keys.append(FALLBACK_KEY)
    else:
        keys += [STORY_KEY, FALLBACK_KEY]
    marks = ",".join("?" * len(keys))
    rows = con.execute(
        f"SELECT d.title, f.key, f.value"
        f" FROM facts f"
        f" JOIN nodes n ON n.id = f.node_id"
        f" JOIN documents d ON d.id = n.document_id"
        f" WHERE f.key IN ({marks})", keys).fetchall()
    cat_rows = con.execute(
        "SELECT d.title, c.category FROM categories c"
        " JOIN documents d ON d.id = c.document_id").fetchall()
    sec_rows = con.execute(
        "SELECT s.id, s.document_id, s.ordinal, s.title FROM sections s"
        " WHERE s.title IS NOT NULL AND s.title != ''").fetchall()
    doc_title = dict(con.execute("SELECT id, title FROM documents"))
    if series == "mcu":
        zero_cat = [r[0] for r in con.execute(
            "SELECT d.title FROM documents d"
            " WHERE d.id NOT IN (SELECT DISTINCT document_id FROM categories)")]
        # U-WP2c link tier: the store's pre-resolved wikilinks from each
        # page's LEAD chunk (section_id NULL) or FIRST section (min
        # ordinal) to media documents -- link structure only, never
        # free text.
        first_section = {}
        for sec_id, doc_id, ordinal, _title in sec_rows:
            cur = first_section.get(doc_id)
            if cur is None or ordinal < cur[1]:
                first_section[doc_id] = (sec_id, ordinal)
        # Every document gets an lf row: the 1,783 mcu pages that have a
        # lead chunk but no titled section would otherwise be dropped by
        # the inner join and lose their lead-section links (U-WP2c spec:
        # lead OR first section). -1 never matches a section_id.
        con.execute("CREATE TEMP TABLE lf (document_id INTEGER,"
                    " first_section_id INTEGER)")
        con.executemany(
            "INSERT INTO lf VALUES (?,?)",
            [(d, first_section[d][0] if d in first_section else -1)
             for d in doc_title])
        # (No explicit chunk_nodes(chunk_id) index: this sqlite build
        # rejects CREATE TEMP INDEX, and the planner's plan without one
        # is a scan of chunk_nodes + PK lookups + a bloom filter on lf,
        # ~2s on mcu -- measured 2026-10-04.)
        media_types_marks = ",".join("?" * len(MCU_MEDIA_TYPES))
        link_rows = con.execute(
            f"SELECT c.document_id, d.title, d.page_type"
            f" FROM chunk_nodes cn"
            f" JOIN chunks c ON c.id = cn.chunk_id"
            f" JOIN nodes n ON n.id = cn.node_id AND n.document_id IS NOT NULL"
            f" JOIN documents d ON d.id = n.document_id"
            f" JOIN lf ON lf.document_id = c.document_id"
            f"  AND (c.section_id IS NULL OR c.section_id = lf.first_section_id)"
            f" WHERE d.page_type IN ({media_types_marks})",
            MCU_MEDIA_TYPES).fetchall()
        # U-WP2d fix B: the INBOUND pairs -- every (media document,
        # other document) whose media page's chunks carry a
        # chunk_nodes row pointing at the other document's node,
        # through the store's pre-resolved links. No lead/first
        # restriction: the spec reads the media page's sections
        # wholesale. Self-links are out (a page's own chunks do not
        # date the page).
        inlink_marks = ",".join("?" * len(MCU_INLINK_MEDIA_TYPES))
        inlink_rows = con.execute(
            f"SELECT c.document_id, dt.id"
            f" FROM chunk_nodes cn"
            f" JOIN chunks c ON c.id = cn.chunk_id"
            f" JOIN nodes n ON n.id = cn.node_id AND n.document_id IS NOT NULL"
            f" JOIN documents dm ON dm.id = c.document_id"
            f" JOIN documents dt ON dt.id = n.document_id"
            f" WHERE dm.page_type IN ({inlink_marks})"
            f" AND c.document_id != n.document_id",
            MCU_INLINK_MEDIA_TYPES).fetchall()
        # U-WP2d fix A: the store's own infobox classification per page,
        # the template name tier 1b looks for in the raw wikitext.
        infobox_map = dict(con.execute(
            "SELECT title, infobox_template FROM documents"))
    con.close()

    # title -> key -> [values]; a title's several variant nodes merge.
    per_title: dict[str, dict[str, list[str]]] = {}
    for title, key, value in rows:
        per_title.setdefault(title, {}).setdefault(key, []).append(value)

    # Tier 1: the page's own release fact -- the earliest tier that
    # parses, its earliest in-range year (a title's several variant
    # facts of one key take the minimum, the first-appearance reading).
    own: dict[str, tuple[int, str]] = {}
    for title, by_key in per_title.items():
        for tier in tiers:
            for key in tier:
                years = [y for y in
                         (parse_year(v) for v in by_key.get(key, []))
                         if y is not None]
                if years:
                    own[title] = (min(years), key)
                    break
            if title in own:
                break

    # Casefold maps. First-wins on a collision (the store carries two
    # pages that differ only in case, e.g. marvel's `DOOM Vol 1 1` /
    # `Doom Vol 1 1`): document order is the tie-break, as in U-WP2,
    # so a re-run is byte-stable.
    ci_title: dict[str, str] = {}
    ci_group: dict[str, list[str]] = {}
    for t in titles:
        ci_group.setdefault(t.casefold(), []).append(t)
        ci_title.setdefault(t.casefold(), t)
    own_ci = {t.casefold(): (y, k) for t, (y, k) in own.items()}

    # ── tier 1b: the first infobox template of the raw wikitext (U-WP2d fix A) ─
    # A media page whose stored tier-1 facts give no year (the infobox
    # parser loses the params after a <ref> -- the engine defect noted
    # in the U-WP2d receipt, not fixed here) is dated from the
    # release/released/first aired/premiere parameter of the FIRST
    # infobox template of its raw wikitext (template parameter parse,
    # never free text). The merged years feed the series-dating, the
    # category tier and the record loop below, so a page filed under
    # the media (Robert Downey Jr. under `Iron Man (film) Actors`)
    # picks up the media's own year.
    wiki_hit: dict[str, tuple[int, str]] = {}
    wiki_no_file = wiki_no_param = wiki_no_year = 0
    if series == "mcu":
        for title in titles:
            if title in own or page_type.get(title) not in MCU_MEDIA_WIKI_TYPES:
                continue
            path = None
            # the crawler writes `:` and `/` as `_` in the file name
            for cand in (title, title.replace(":", "_").replace("/", "_")):
                p = sroot / "wikitext" / f"{cand}.json"
                if p.exists():
                    path = p
                    break
            if path is None:
                wiki_no_file += 1
                continue
            year, param = wikitext_release_year(
                path, infobox_map.get(title, ""))
            if year is None:
                if param is None:
                    wiki_no_param += 1
                else:
                    wiki_no_year += 1
                continue
            wiki_hit[title] = (year, f"wikitext:{param}")
            own[title] = wiki_hit[title]

    # ── category structure (mcu tier 2, U-WP2c) ────────────────────────
    # `<Media> <role>` rows: the role word is the last word, the media
    # title the rest. A page's own category media (ci) gate the section
    # era: a section title that names a media only counts when the page
    # is itself filed under that media (U-WP2c fix 1).
    cats: dict[str, list[str]] = {}
    cat_media: dict[str, set] = {}
    for title, category in cat_rows:
        cats.setdefault(title, []).append(category)
        parts = category.rsplit(" ", 1)
        if len(parts) == 2:
            cat_media.setdefault(title, set()).add(parts[0].casefold())
    # series-dating (U-WP2c fix 2): a media with no tier-1 fact is
    # dated by the EARLIEST tier-1 year of the pages filed under
    # `<media> Episodes` (source `episodes:<media>`), else by its own
    # `first` fact resolved to an episode/issue page with a tier-1 year
    # (source `series_first:<media>`). The casefold key carries the
    # media's spelling as the store's category values spell it.
    ep_pages: dict[str, list[str]] = {}
    for title, category in cat_rows:
        parts = category.rsplit(" ", 1)
        if len(parts) == 2 and parts[1].casefold() == "episodes":
            ep_pages.setdefault(parts[0].casefold(), []).append(title)
    first_targets: dict[str, tuple] = {}
    doc_type_ci = {t.casefold(): page_type[t] for t in titles}
    for title, by_key in per_title.items():
        for value in by_key.get(FALLBACK_KEY, []):
            value = str(value).strip()
            if not value:
                continue
            target = ci_title.get(value.casefold())
            if (target is not None and target in own
                    and doc_type_ci.get(target.casefold())
                    in MCU_FIRST_TARGET_TYPES):
                first_targets.setdefault(title.casefold(), (own[target][0], target))
    # The media's original spelling, first-wins as the category values
    # spell it (for source labels); a media with no document of its own
    # keeps its category spelling.
    media_spelling: dict[str, str] = {}
    for _title, category in cat_rows:
        parts = category.rsplit(" ", 1)
        if len(parts) == 2:
            media_spelling.setdefault(parts[0].casefold(), parts[0])
    series_dated: dict[str, tuple[int, str]] = {}
    for media_ci in sorted(set(ep_pages) | set(first_targets)):
        cands = []
        if media_ci in ep_pages:
            years = [own[t][0] for t in ep_pages[media_ci] if t in own]
            if years:
                cands.append(
                    (min(years),
                     f"episodes:{media_spelling.get(media_ci, ci_title.get(media_ci, media_ci.title()))}"))
        if media_ci in first_targets:
            year, _target_title = first_targets[media_ci]
            cands.append(
                (year,
                 f"series_first:{media_spelling.get(media_ci, ci_title.get(media_ci, media_ci.title()))}"))
        if cands:
            cands.sort()  # earliest year; ties to the `episodes:` rule
            series_dated[media_ci] = cands[0]
    # The dated set both tier-2 rules read from: own tier-1 years plus
    # the series-dated media (the earliest of the two candidate rules,
    # ties to `episodes:`).
    dated_ci: dict[str, int] = {}
    for t, (y, _k) in own.items():
        dated_ci.setdefault(t.casefold(), y)
    for media_ci, (y, _s) in series_dated.items():
        dated_ci.setdefault(media_ci, y)

    # ── section eras (U-WP2c fix 1) ────────────────────────────────────
    # mcu: the section's media must be one of the page's own category
    # media (generic headings that merely match a same-titled media,
    # like "Aftermath" on a conflict page, are dropped). marvel: the
    # section title must be a comic issue/volume page title.
    section_era: dict[str, dict[str, int]] = {}
    n_sec_pairs = 0
    for sec_id, doc_id, _ordinal, sec_title in sec_rows:
        year = dated_ci.get(sec_title.casefold())
        if year is None:
            continue
        page = doc_title[doc_id]
        if series == "mcu":
            if sec_title.casefold() not in cat_media.get(page, set()):
                continue
        else:
            target = ci_title.get(sec_title.casefold())
            if (target is None
                    or page_type.get(target) not in MARVEL_SECTION_TARGET_TYPES):
                continue
        section_era.setdefault(page, {})[sec_title] = year
        n_sec_pairs += 1
    n_sec_pages = len(section_era)

    # ── records ────────────────────────────────────────────────────────
    out: dict[str, dict] = {}
    for title in titles:
        if title in own:
            year, source = own[title]
        elif series == "mcu" and title.casefold() in series_dated:
            year, source = series_dated[title.casefold()]
        else:
            year, source = None, "undated"
        rec = {"year": year, "era": era_of(year), "source": source}
        if series == "mcu":
            # U-WP2b: the in-universe `date` fact, reported, never era.
            story_years = [y for y in
                           (parse_year(v) for v in
                            per_title.get(title, {}).get(STORY_KEY, []))
                           if y is not None]
            rec["story_year"] = min(story_years) if story_years else None
        rec["sections"] = section_era.get(title, {})
        out[title] = rec

    # ── tier 2: the `first` fallback (marvel) / categories (mcu) ──────
    fb_note = ""
    if series == "marvel":
        # The U-WP2 rule, unchanged: the `first` fact, resolved to the
        # issue page's own tier-1 year (one hop; unresolvable values
        # counted, never guessed).
        via_first: dict[str, tuple[int, str]] = {}
        unresolved_pages = 0
        unmatched_values = 0   # `first` value names no document
        no_year_targets = 0    # the matched document has no tier-1 year
        for title, by_key in per_title.items():
            if title in own or FALLBACK_KEY not in by_key:
                continue
            resolved = False
            for value in sorted(str(v).strip() for v in by_key[FALLBACK_KEY]):
                if not value:
                    continue
                target = ci_title.get(value.casefold())
                if target is None:
                    unmatched_values += 1
                elif target not in own:
                    no_year_targets += 1
                else:
                    via_first[title] = (own[target][0], FALLBACK_KEY)
                    resolved = True
                    break
            if not resolved:
                unresolved_pages += 1
        for title, (year, _src) in via_first.items():
            out[title] = {"year": year, "era": era_of(year),
                          "source": FALLBACK_KEY,
                          "sections": section_era.get(title, {})}
        fb_note = (f"first-fallback: resolved {len(via_first)} page(s) via `{FALLBACK_KEY}`; "
                   f"unresolved {unresolved_pages} page(s) "
                   f"({unmatched_values} value(s) matching no document, "
                   f"{no_year_targets} matching a document without a tier-1 year)")
    else:
        # U-WP2c: the category tier reads the DATED set (own tier-1 +
        # series-dated), so pages under a series like Agents of
        # S.H.I.E.L.D. now date from its earliest episode's first-air
        # year; a media page keeps its own release fact (tier 1).
        undated_media: Counter = Counter()  # media -> pages (no dated doc)
        generic_values = 0                  # category value names no doc
        stamped = 0
        title_cis = set(doc_type_ci)        # all document-title casefolds
        for title in sorted(cats):
            if title in own or title.casefold() in series_dated:
                continue  # tier 1 / series-dated media keep their own year
            best = None
            for m in cat_media.get(title, ()):
                year = dated_ci.get(m)
                if year is None:
                    if m in title_cis:
                        undated_media[ci_title[m]] += 1
                    else:
                        generic_values += 1
                    continue
                if best is None or (year, m) < best:
                    best = (year, m)
            if best is not None:
                out[title] = {"year": best[0], "era": era_of(best[0]),
                              "source": f"category:{ci_title[best[1]]}",
                              "story_year": out[title]["story_year"],
                              "sections": out[title]["sections"]}
                stamped += 1
        # U-WP2c fix 3: the last tier -- the earliest dated media the
        # page links to through the store's pre-resolved wikilinks in
        # its LEAD or FIRST section (link structure only, never free
        # text).
        link_cand: dict[int, list] = {}
        for doc_id, target_title, _ptype in link_rows:
            year = dated_ci.get(target_title.casefold())
            if year is not None:
                link_cand.setdefault(doc_id, []).append(
                    (year, target_title.casefold(), target_title))
        n_link = 0
        for doc_id in sorted(link_cand):
            page = doc_title[doc_id]
            if out[page]["era"] != "undated":
                continue
            year, _ci, media = min(link_cand[doc_id])
            out[page] = {"year": year, "era": era_of(year),
                         "source": f"link:{media}",
                         "story_year": out[page]["story_year"],
                         "sections": out[page]["sections"]}
            n_link += 1
        # U-WP2d fix B: the INBOUND tier, the last of all -- a page
        # still undated after every other tier is dated by the
        # EARLIEST dated media page (movie/tv series/episode/one-shot)
        # whose own sections link TO it through the store's
        # pre-resolved wikilinks (the media page's chunks'
        # chunk_nodes pointing at the page's node). The media's year
        # is its final one: every other tier has already run, so an
        # inlink never fights a tier that could have dated the media
        # itself.
        ce_before = Counter(
            page_type[t] for t in out
            if out[t]["era"] == "undated" and page_type[t] in ("conflict", "event"))
        media_docs = {mdoc for mdoc, _tdoc in inlink_rows}
        media_year = {d: out[doc_title[d]]["year"] for d in media_docs}
        inlink_cand: dict[int, list] = {}
        for mdoc, tdoc in set(inlink_rows):
            year = media_year.get(mdoc)
            if year is not None:
                inlink_cand.setdefault(tdoc, []).append(
                    (year, doc_title[mdoc].casefold(), doc_title[mdoc]))
        n_inlink = 0
        inlink_pt: Counter = Counter()
        for tdoc in sorted(inlink_cand):
            page = doc_title[tdoc]
            if out[page]["era"] != "undated":
                continue
            year, _ci, media = min(inlink_cand[tdoc])
            out[page] = {"year": year, "era": era_of(year),
                         "source": f"inlink:{media}",
                         "story_year": out[page]["story_year"],
                         "sections": out[page]["sections"]}
            n_inlink += 1
            inlink_pt[page_type[page]] += 1
        fb_note = (f"category tier: {stamped} page(s) via a dated media; "
                   f"series-dated media {len(series_dated)} "
                   f"({sum(1 for _s in series_dated.values() if _s[1].startswith('episodes:'))} by "
                   f"`<media> Episodes`, "
                   f"{sum(1 for _s in series_dated.values() if _s[1].startswith('series_first:'))} by "
                   f"`first`); "
                   f"link tier (lead/first-section wikilinks): {n_link} page(s); "
                   f"inlink tier (inbound media links, last): {n_inlink} page(s); "
                   f"undated media {sum(undated_media.values())} page(s) under "
                   f"{len(undated_media)} media; {generic_values} non-media value(s)")

    era_path = sroot / "training" / "era.json"
    era_path.parent.mkdir(parents=True, exist_ok=True)
    if era_path.exists():
        # Supersede, don't delete -- and never clobber an older archive:
        # a re-run archives beside the existing .pre-wp2b with a
        # timestamp.
        archive = era_path.with_name(era_path.name + ".pre-wp2b")
        if archive.exists():
            archive = era_path.with_name(
                f"era.json.pre-wp2b-{time.strftime('%Y%m%dT%H%M%S')}")
        era_path.rename(archive)
    era_path.write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    # ── report ─────────────────────────────────────────────────────────
    n = len(titles)
    era_totals = Counter(rec["era"] for rec in out.values())
    type_counts = Counter(page_type.values())
    top8 = [t for t, _ in type_counts.most_common(8)]
    matrix = {t: Counter() for t in top8}
    rest = Counter()
    for title, rec in out.items():
        pt = page_type[title]
        (matrix[pt] if pt in matrix else rest)[rec["era"]] += 1
    # Source histogram by rule: `category:/episodes:/series_first:/
    # link:<media>/inlink:<media>/wikitext:<param>` fold to their rule
    # prefix (per-media splits are reported under the histogram).
    def rule_of(source):
        if source.startswith(("category:", "episodes:", "series_first:",
                              "link:", "inlink:", "wikitext:")):
            return source.split(":", 1)[0]
        return source
    sources = Counter(rule_of(rec["source"]) for rec in out.values())
    media_counts = Counter(
        rec["source"].split(":", 1)[1] for rec in out.values()
        if rec["source"].startswith(("category:", "episodes:",
                                     "series_first:", "link:", "inlink:")))

    print(f"== {series}: {n} pages -> {era_path}")
    print("era x page_type (top 8 types):")
    header = "page_type".ljust(18) + "".join(e.ljust(9) for e in ERAS) + "total"
    print(header)
    for t in top8:
        row = matrix[t]
        print(t.ljust(18)
              + "".join(str(row.get(e, 0)).ljust(9) for e in ERAS)
              + str(sum(row.values())))
    print("rest (other types)".ljust(18)
          + "".join(str(rest.get(e, 0)).ljust(9) for e in ERAS)
          + str(sum(rest.values())))
    print("era totals (all types)"
          + "".join(f" {e}={era_totals.get(e, 0)}" for e in ERAS))
    undated = era_totals.get("undated", 0)
    print(f"undated: {undated}/{n} = {100.0 * undated / n:.2f}%")
    print("source histogram (by rule):")
    for key, count in sources.most_common():
        print(f"  {key}: {count}")
    for prefix in ("category", "episodes", "series_first", "link", "inlink"):
        top_media = [(m, c) for m, c in media_counts.most_common(40)
                     if m.startswith(f"{prefix}:")]
        if top_media:
            print(f"top-10 media ({prefix}):")
            for media, count in top_media[:10]:
                print(f"  {media}: {count}")
    if series == "mcu":
        story_n = sum(1 for rec in out.values() if rec["story_year"] is not None)
        print(f"story_year (the in-universe `date` fact, never the era): "
              f"{story_n} page(s)")
        print(f"zero-category pages: {len(zero_cat)}: {sorted(zero_cat)}")
        print("top-20 media resolving to NO dated document (by page count):")
        for media, count in undated_media.most_common(20):
            print(f"  {count:5d}  {media!r}")
    print(fb_note)
    print(f"section eras (U-WP2c-filtered): {n_sec_pairs} (doc, section) "
          f"pairs on {n_sec_pages} page(s)")
    sec_pairs = [(page, st, y) for page, sec in section_era.items()
                 for st, y in sec.items()]
    if sec_pairs:
        rng2 = random.Random(42)
        sample = rng2.sample(sorted(sec_pairs), min(10, len(sec_pairs)))
        print("random 10 surviving section eras (page | section | year):")
        for page, st, y in sample:
            print(f"  {page} | {st} | {y}")
    if series == "mcu":
        # U-WP2c fix 3 receipt: link-tier coverage on the event-rich
        # conflict/event pages + 10 random conflict rows for the check.
        link_rows_by_pt = Counter(
            page_type[t] for t in out
            if out[t]["source"].startswith("link:")
            and page_type[t] in ("conflict", "event"))
        print(f"link-tier coverage on conflicts/events: "
              f"conflict {link_rows_by_pt.get('conflict', 0)}, "
              f"event {link_rows_by_pt.get('event', 0)}")
        conflict_link = sorted(
            t for t in out
            if out[t]["source"].startswith("link:") and page_type[t] == "conflict")
        if conflict_link:
            rng3 = random.Random(42)
            print("random 10 conflict rows dated by the link tier:")
            for t in rng3.sample(conflict_link, min(10, len(conflict_link))):
                rec = out[t]
                print(f"  {t} | {rec['year']} | {rec['source']}")
        # U-WP2d fix A receipt: how many media pages the wikitext
        # release-param tier dated, + 10 random (title, year) rows.
        wiki_pt = Counter(page_type[t] for t in wiki_hit)
        print(f"tier 1b (wikitext infobox release param, media pages): "
              f"{len(wiki_hit)} page(s) dated "
              f"({', '.join(f'{k} {v}' for k, v in wiki_pt.most_common())}); "
              f"{wiki_no_file} without a wikitext file, "
              f"{wiki_no_param} without a release parameter, "
              f"{wiki_no_year} with no in-range year")
        if wiki_hit:
            rngw = random.Random(42)
            pick = sorted(rngw.sample(sorted(wiki_hit),
                                      min(10, len(wiki_hit))))
            print("random 10 (title | year | source) dated by tier 1b:")
            for t in pick:
                year, src = wiki_hit[t]
                print(f"  {t} | {year} | {src}")
        # U-WP2d fix B receipt: inlink-tier coverage on the
        # conflict/event pages (of the ones still undated after every
        # other tier) + 10 random rows (title, year, media).
        print(f"inlink-tier coverage on conflicts/events (undated after "
              f"every other tier): "
              f"conflict {inlink_pt.get('conflict', 0)}/"
              f"{ce_before.get('conflict', 0)}, "
              f"event {inlink_pt.get('event', 0)}/{ce_before.get('event', 0)}; "
              f"inlink-dated pages by type: "
              f"{dict(inlink_pt.most_common())}")
        inlink_ce = sorted(
            t for t in out
            if out[t]["source"].startswith("inlink:")
            and page_type[t] in ("conflict", "event"))
        if inlink_ce:
            rng4 = random.Random(42)
            print("random 10 conflict/event rows dated by the inlink tier "
                  "(title | year | media):")
            for t in rng4.sample(inlink_ce, min(10, len(inlink_ce))):
                rec = out[t]
                print(f"  {t} | {rec['year']} | {rec['source']}")
    rng = random.Random(42)
    for era in ERAS:
        random_rows(out, page_type, era, rng,
                    min_characters=3 if series == "mcu" else 0)
    print(f"elapsed {time.monotonic() - t0:.1f}s")


if __name__ == "__main__":
    sys.exit(main())
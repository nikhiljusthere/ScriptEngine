#!/usr/bin/env python3
"""B0 — CC/SDH catalog builder (zero-egress, no model).

Builds `reports/marvel/cc_catalog.jsonl` from the wikis themselves
(plan §B0: "structure is the source of truth"):

  * MCU wiki (`series/mcu/wikitext/`) — quiescent at B0 time (its F1
    backfill is queued after the marvel stage):
      - movie rows  <- own category in {Released Movies, Phase N Movies,
                        The * Saga Movies, Upcoming Movies}
      - series rows <- own category `TV Series`
      - episode rows <- pages whose category is `<Series> Episodes`
        (episode_count per series = local count of those pages)
  * Marvel DB (`series/marvel/wikitext/`) — read-safe while its F1
    backfill runs: stamp_revid is tmp-write + atomic rename, so a reader
    always sees a complete JSON (old or new):
      - series rows <- pages with a `Series Template` infobox
        (class: animated when the `seriestype` fact says Animated)
      - episode rows <- pages with an `Episode Template` infobox

Row shape (plan §B0 + campaign notes):
  {title, class: movie|series|episode|animated, wiki, year,
   episode_count (series rows), parent (episode rows),
   source_tier, audio_source, cc_source, status}

Owner decision 2026-09-27: B1 tier order starts at the S6 subtitle
databases (websites) — T-YT (YouTube) dropped (no speaker labels).
Hence `audio_source` is left null (no YouTube inventory step);
`cc_source` is the S6 tier that serves the title at B1 time.

Output receipt: reports/marvel/receipts/b0/cc_catalog_b0_<date>.json
"""
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MCU = REPO / "series/mcu/wikitext"
MARVEL = REPO / "series/marvel/wikitext"
OUT = REPO / "reports/marvel/cc_catalog.jsonl"
REC_DIR = REPO / "reports/marvel/receipts/b0"

MOVIE_CATS = re.compile(
    r"^(Released Movies|Phase [A-Za-z0-9]+ Movies|"
    r"The (Infinity|Multiverse) Saga Movies|Upcoming Movies)$"
)
MOVIE_REL_CATS = re.compile(
    r"^(Released Movies|Phase [A-Za-z0-9]+ Movies|"
    r"The (Infinity|Multiverse) Saga Movies)$"
)
EP_CAT = re.compile(r"^(?P<s>.+?) Episodes$")


def norm(title: str) -> str:
    t = title.lower()
    t = re.sub(r"^(marvel's|marvel )", "", t)
    t = re.sub(r"\((tv|animated) series\)$", "", t)
    t = t.strip(" .!")
    return re.sub(r"\s+", " ", t)


def fact_val(facts, key):
    for f in facts or []:
        if f.get("key") == key:
            return f.get("value")
    return None


def year_from(wikitext, facts):
    m = re.search(
        r"\|\s*release(?:[_ ]?(?:date|d))?\s*=\s*([^\n|]+)", wikitext or "", re.I
    )
    if m:
        y = re.search(r"(19|20)\d{2}", m.group(1))
        if y:
            return int(y.group(0))
    for k in ("dates", "first", "first aired", "first_aired", "premiered", "year"):
        v = fact_val(facts, k)
        if v:
            y = re.search(r"(19|20)\d{2}", str(v))
            if y:
                return int(y.group(0))
    m = re.search(
        r"\|\s*(?:first|first_aired|premiered|started)\s*=\s*([^\n|]+)",
        wikitext or "",
        re.I,
    )
    if m:
        y = re.search(r"(19|20)\d{2}", m.group(1))
        if y:
            return int(y.group(0))
    return None


def iter_json(dirpath):
    bad = 0
    for p in sorted(dirpath.glob("*.json")):
        try:
            yield json.loads(p.read_text(encoding="utf-8")), p
        except Exception:
            bad += 1
    if bad:
        print(f"[b0] WARN {dirpath.name}: {bad} files failed to parse", file=sys.stderr)


def main():
    rows = []
    diag = {}

    # ---------- MCU wiki ----------
    mcu_pages = []  # (title, cats, facts, wikitext, pageid)
    for d, _ in iter_json(MCU):
        mcu_pages.append(
            (
                d.get("title") or d.get("url", "").rsplit("/", 1)[-1],
                d.get("categories") or [],
                d.get("facts") or [],
                d.get("wikitext") or "",
                d.get("pageid"),
            )
        )
    n_mcu_files = len(mcu_pages)

    movie_rows, series_rows, ep_rows = [], [], []
    ep_by_series = Counter()
    for title, cats, facts, wikitext, pageid in mcu_pages:
        epm = None
        for c in cats:
            m = EP_CAT.match(c)
            if m:
                epm = m.group("s")
                break
        if epm:
            ep_by_series[epm] += 1
            continue  # episode pages counted under their series below
        mov = [c for c in cats if MOVIE_CATS.match(c)]
        if mov:
            released = bool([c for c in cats if MOVIE_REL_CATS.match(c)])
            movie_rows.append(
                {
                    "title": title,
                    "class": "movie",
                    "wiki": "mcu",
                    "year": year_from(wikitext, facts),
                    "episode_count": None,
                    "parent": None,
                    "source_tier": "S6",
                    "audio_source": None,
                    "cc_source": None,
                    "status": "released" if released else "upcoming",
                    "mcu_categories": sorted(set(cats) & {
                        "Released Movies", "Upcoming Movies",
                        "The Infinity Saga Movies", "The Multiverse Saga Movies",
                        "Phase One Movies", "Phase Two Movies", "Phase Three Movies",
                        "Phase Four Movies", "Phase Five Movies", "Phase Six Movies"}),
                    "pageid": pageid,
                }
            )
        elif "TV Series" in cats:
            series_rows.append(
                {
                    "title": title,
                    "class": "series",
                    "wiki": "mcu",
                    "year": year_from(wikitext, facts),
                    "episode_count": None,  # filled after the episode pass
                    "parent": None,
                    "source_tier": "S6",
                    "audio_source": None,
                    "cc_source": None,
                    "status": "cataloged-b0",
                    "mcu_categories": sorted(set(cats) & {
                        "TV Series", "Disney+ Series",
                        "The Infinity Saga TV Series", "The Multiverse Saga TV Series"}),
                    "pageid": pageid,
                }
            )

    # episode_count per MCU series: match `<series> Episodes` cat holder
    # against the series title (normalized)
    norm_series = {norm(s["title"]): s for s in series_rows}
    matched, unmatched = Counter(), Counter()
    for series_name, count in ep_by_series.items():
        key = norm(series_name)
        if key in norm_series:
            norm_series[key]["episode_count"] = count
            matched[series_name] = count
        else:
            # series page missing from the wiki (or named differently):
            # emit an episode-carrying stub row so no episode is lost
            unmatched[series_name] = count
            series_rows.append(
                {
                    "title": series_name,
                    "class": "series",
                    "wiki": "mcu",
                    "year": None,
                    "episode_count": count,
                    "parent": None,
                    "source_tier": "S6",
                    "audio_source": None,
                    "cc_source": None,
                    "status": "episode-stub (no series page)",
                    "pageid": None,
                }
            )

    # MCU episode rows
    for title, cats, facts, wikitext, pageid in mcu_pages:
        parent = next((c for c in cats if EP_CAT.match(c)), None)
        if parent:
            ep_rows.append(
                {
                    "title": title,
                    "class": "episode",
                    "wiki": "mcu",
                    "year": None,
                    "episode_count": None,
                    "parent": EP_CAT.match(parent).group("s"),
                    "source_tier": "S6",
                    "audio_source": None,
                    "cc_source": None,
                    "status": "cataloged-b0",
                    "pageid": pageid,
                }
            )

    # ---------- Marvel DB (animated + live-action series) ----------
    m_series, m_eps = [], []
    ep_tmpl_titles = []
    for d, _ in iter_json(MARVEL):
        tpls = [t.lower() for t in d.get("templates") or []]
        facts = d.get("facts") or []
        title = d.get("title")
        pageid = d.get("pageid")
        if any("series template" in t for t in tpls):
            seriestype = str(fact_val(facts, "seriestype") or "")
            animated = "animated" in seriestype.lower()
            m_series.append(
                {
                    "title": title,
                    "class": "animated" if animated else "series",
                    "wiki": "marvel",
                    "year": year_from(d.get("wikitext") or "", facts),
                    "episode_count": _to_int(fact_val(facts, "number of episodes")),
                    "parent": None,
                    "source_tier": "S6",
                    "audio_source": None,
                    "cc_source": None,
                    "status": "cataloged-b0",
                    "seriestype": seriestype or None,
                    "pageid": pageid,
                }
            )
        elif any("episode template" in t for t in tpls):
            ep_tmpl_titles.append(title)
            m_eps.append(
                {
                    "title": title,
                    "class": "episode",
                    "wiki": "marvel",
                    "year": _to_int(fact_val(facts, "year")),
                    "episode_count": None,
                    "parent": _parent_from_ep_title(title),
                    "source_tier": "S6",
                    "audio_source": None,
                    "cc_source": None,
                    "status": "cataloged-b0",
                    "pageid": pageid,
                }
            )

    # dedup: marvel series rows that collide with an mcu series row
    dupes = []
    kept_m_series = []
    for s in m_series:
        if norm(s["title"]) in norm_series or any(
            norm(s["title"]) == norm(x["title"]) for x in series_rows
        ):
            s["status"] = "dup-of-mcu"
            dupes.append(s["title"])
        kept_m_series.append(s)

    rows = movie_rows + series_rows + ep_rows + kept_m_series + m_eps
    rows.sort(key=lambda r: (r["class"], r["wiki"], r["title"] or ""))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    diag = {
        "date": str(date.today()),
        "mcu_files": n_mcu_files,
        "year_null": {
            "movies": sum(1 for r in movie_rows if r["year"] is None),
            "series": sum(1 for r in series_rows if r["year"] is None),
        },
        "counts": dict(Counter((r["class"] + ":" + r["wiki"]) for r in rows)),
        "mcu_series_episodes_matched": dict(matched),
        "mcu_series_unmatched_stubs": dict(unmatched),
        "marvel_dup_of_mcu": dupes,
        "rows_written": len(rows),
        "output": str(OUT),
        "notes": [
            "Owner decision 2026-09-27: B1 tier order starts at S6 "
            "subtitle databases (websites); T-YT dropped (no speaker labels). "
            "audio_source left null by design.",
            "animated-movie class (est. ~45) has no S1/S2 source page yet "
            "(e.g. Spider-Verse films are in neither corpus) — recorded gap, "
            "next B0 iteration or S6-direct title search.",
            "Marvel DB read is safe during the F1 marvel backfill: "
            "stamp_revid is tmp-write + atomic rename (complete JSON only).",
        ],
    }
    REC_DIR.mkdir(parents=True, exist_ok=True)
    rec = REC_DIR / f"cc_catalog_b0_{date.today()}.json"
    rec.write_text(json.dumps(diag, indent=1), encoding="utf-8")
    print(f"[b0] wrote {len(rows)} rows -> {OUT}")
    print(f"[b0] receipt -> {rec}")
    for k, v in diag["counts"].items():
        print(f"     {k:28s} {v}")


def _to_int(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def _parent_from_ep_title(title):
    # "<Series> Season N M" -> <Series>
    m = re.match(r"^(.*?)\s+Season\s+\d+\s+\d+$", title)
    return m.group(1) if m else None


if __name__ == "__main__":
    main()